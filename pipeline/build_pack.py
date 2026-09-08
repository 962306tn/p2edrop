#!/usr/bin/env python3
"""plan.json -> prompt pack + render manifest.

The creative work (hooks, scripts, scene beats) is written by the agent into
plan.json. This script does only the deterministic part: validate it, fan every
variant out into per-scene provider prompts, and emit the manifest the renderer
consumes. Keeping the split here is what makes a run reproducible - re-running
build_pack.py on the same plan always produces the same jobs and job ids.

Usage:
  python3 pipeline/build_pack.py plan.json [--out out/<slug>] [--config providers.json]
"""

import json
import re
from pathlib import Path

from common import PipelineError, die, load_config, log, run_cli

REQUIRED_PLAN_KEYS = ("brand", "language", "variants")
REQUIRED_VARIANT_KEYS = ("id", "format", "hook", "scenes")
REQUIRED_SCENE_KEYS = ("visual",)


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-") or "pack"


def validate(plan):
    missing = [k for k in REQUIRED_PLAN_KEYS if not plan.get(k)]
    if missing:
        die(f"plan is missing top-level keys: {', '.join(missing)}")
    if not isinstance(plan["variants"], list) or not plan["variants"]:
        die("plan.variants must be a non-empty list")

    seen = set()
    for index, variant in enumerate(plan["variants"], 1):
        where = f"variants[{index}]"
        missing = [k for k in REQUIRED_VARIANT_KEYS if not variant.get(k)]
        if missing:
            die(f"{where} is missing: {', '.join(missing)}")
        vid = slugify(variant["id"])
        if vid in seen:
            die(f"{where} repeats variant id '{vid}' - ids must be unique")
        seen.add(vid)
        if not isinstance(variant["scenes"], list) or not variant["scenes"]:
            die(f"{where}.scenes must be a non-empty list")
        for scene_index, scene in enumerate(variant["scenes"], 1):
            scene_missing = [k for k in REQUIRED_SCENE_KEYS if not scene.get(k)]
            if scene_missing:
                die(f"{where}.scenes[{scene_index}] is missing: {', '.join(scene_missing)}")


def scene_prompt(plan, variant, scene, scene_no):
    """One flat prompt string - what a text-to-video model actually reads.

    Also what you paste by hand into the Topview UI when you would rather click
    than call the API, so it has to stand alone without the rest of the pack.
    """
    parts = [scene["visual"].strip()]
    for label, key in (
        ("Camera", "camera"),
        ("Lighting", "lighting"),
        ("Motion", "motion"),
        ("Audio", "audio"),
    ):
        if scene.get(key):
            parts.append(f"{label}: {scene[key].strip()}")

    style = variant.get("style") or plan.get("style")
    if style:
        parts.append(f"Style: {style.strip()}")
    if plan.get("negative_prompt"):
        parts.append(f"Avoid: {plan['negative_prompt'].strip()}")

    on_screen = scene.get("overlay")
    if on_screen:
        # Burned-in text is the #1 source of garbled model output; keep it explicit.
        parts.append(f'On-screen text (render exactly, sans-serif, legible): "{on_screen.strip()}"')
    elif plan.get("no_text_in_video", True):
        parts.append("No on-screen text, captions, watermarks or logos.")

    header = f"[{variant['format']} / scene {scene_no} of {len(variant['scenes'])}]"
    return f"{header} " + " ".join(p.rstrip(".") + "." for p in parts if p)


def build_payload(plan, variant, scene, prompt, module_cfg):
    """Provider request body, with field names taken from providers.json so a
    renamed API field is a config edit, not a code change."""
    keys = module_cfg.get("payload_keys", {})
    defaults = {**(plan.get("defaults") or {}), **(variant.get("defaults") or {}), **(scene.get("defaults") or {})}

    values = {
        "prompt": prompt,
        "model": defaults.get("model"),
        "aspect_ratio": defaults.get("aspect_ratio") or plan.get("aspect_ratio"),
        "duration": scene.get("duration") or defaults.get("duration"),
        "resolution": defaults.get("resolution"),
        "seed": scene.get("seed") or defaults.get("seed"),
        "image_url": scene.get("image_url") or variant.get("image_url"),
    }

    payload = {}
    for logical, value in values.items():
        if value in (None, ""):
            continue
        payload[keys.get(logical, logical)] = value
    # Anything the provider needs that this pipeline does not model yet.
    payload.update(defaults.get("extra_payload") or {})
    payload.update(scene.get("extra_payload") or {})
    return payload


def script_markdown(plan, variant):
    lines = [
        f"# {variant['id']} - {variant['format']}",
        "",
        f"- Brand: {plan['brand']}",
        f"- Angle: {variant.get('angle', '-')}",
        f"- Language: {plan['language']}",
        f"- Aspect: {variant.get('defaults', {}).get('aspect_ratio') or plan.get('aspect_ratio', '-')}",
        "",
        "## Hook",
        variant["hook"],
    ]
    if variant.get("backup_hook"):
        lines += ["", "## Backup hook", variant["backup_hook"]]
    if variant.get("voiceover"):
        lines += ["", "## Voiceover", variant["voiceover"]]
    lines += ["", "## Scenes", ""]
    for i, scene in enumerate(variant["scenes"], 1):
        lines.append(f"**{i}. ({scene.get('duration', '?')}s)** {scene['visual']}")
        if scene.get("vo"):
            lines.append(f"  - VO: {scene['vo']}")
        if scene.get("overlay"):
            lines.append(f"  - Overlay: {scene['overlay']}")
        lines.append("")
    if variant.get("caption"):
        lines += ["## Caption", variant["caption"], ""]
    if variant.get("cta"):
        lines += ["## CTA", variant["cta"], ""]
    return "\n".join(lines)


def build(plan_path, out_dir=None, config_path=None):
    plan_path = Path(plan_path)
    if not plan_path.exists():
        die(f"plan not found: {plan_path}")
    try:
        plan = json.loads(plan_path.read_text())
    except ValueError as exc:
        die(f"{plan_path} is not valid JSON: {exc}")
    validate(plan)

    config = load_config(config_path)
    topview = config["topview"]
    module_name = (plan.get("defaults") or {}).get("module", "video_gen")
    module_cfg = topview["modules"].get(module_name)
    if not module_cfg:
        die(f"unknown topview module '{module_name}' - known: {', '.join(topview['modules'])}")

    slug = slugify(plan.get("slug") or f"{plan['brand']}-{plan.get('funnel', 'pack')}")
    out = Path(out_dir) if out_dir else Path("out") / slug
    prompts_dir = out / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    jobs = []
    index_rows = []
    for variant in plan["variants"]:
        vid = slugify(variant["id"])
        vdir = prompts_dir / vid
        vdir.mkdir(parents=True, exist_ok=True)

        topview_payloads = []
        flat_prompts = []
        for scene_no, scene in enumerate(variant["scenes"], 1):
            prompt = scene_prompt(plan, variant, scene, scene_no)
            payload = build_payload(plan, variant, scene, prompt, module_cfg)
            topview_payloads.append(payload)
            flat_prompts.append(f"--- scene {scene_no:02d} ---\n{prompt}\n")
            jobs.append(
                {
                    "job_id": f"{vid}/scene-{scene_no:02d}",
                    "variant": vid,
                    "scene": scene_no,
                    "provider": "topview",
                    "module": module_name,
                    "payload": payload,
                    "output": f"renders/{vid}/scene-{scene_no:02d}.mp4",
                }
            )

        (vdir / "topview.json").write_text(json.dumps(topview_payloads, indent=2, ensure_ascii=False))
        (vdir / "seedance.txt").write_text("\n".join(flat_prompts))
        (vdir / "script.md").write_text(script_markdown(plan, variant))
        # Hand-off for the post-production pass. Superscale reads it via its API
        # when configured, or you drag the rendered clips in and follow this.
        (vdir / "superscale.json").write_text(
            json.dumps(
                {
                    "variant": vid,
                    "format": variant["format"],
                    "brand": plan["brand"],
                    "aspect_ratio": variant.get("defaults", {}).get("aspect_ratio") or plan.get("aspect_ratio"),
                    "language": plan["language"],
                    "hook": variant["hook"],
                    "caption": variant.get("caption", ""),
                    "cta": variant.get("cta", ""),
                    "captions_burned_in": bool(plan.get("burn_captions", True)),
                    "music": variant.get("music") or plan.get("music", ""),
                    "clips": [f"renders/{vid}/scene-{n:02d}.mp4" for n in range(1, len(variant["scenes"]) + 1)],
                    "overlays": [s.get("overlay", "") for s in variant["scenes"]],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        index_rows.append(f"| {vid} | {variant['format']} | {variant.get('angle', '-')} | {len(variant['scenes'])} | {variant['hook'][:60]} |")

    manifest = {
        "slug": slug,
        "brand": plan["brand"],
        "plan": str(plan_path),
        "module": module_name,
        "jobs": jobs,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    (out / "INDEX.md").write_text(
        "\n".join(
            [
                f"# {plan['brand']} - {slug}",
                "",
                f"{len(plan['variants'])} variants, {len(jobs)} clips to render.",
                "",
                "| variant | format | angle | scenes | hook |",
                "| --- | --- | --- | --- | --- |",
                *index_rows,
                "",
                "## Render",
                "",
                "```bash",
                f"python3 pipeline/topview.py render {out}/manifest.json",
                f"python3 pipeline/superscale.py push {out}/manifest.json   # optional post-production",
                "```",
                "",
            ]
        )
    )

    log(f"built {len(jobs)} jobs across {len(plan['variants'])} variants -> {out}")
    log(f"  prompts:  {prompts_dir}")
    log(f"  manifest: {out / 'manifest.json'}")
    log(f"  next:     python3 pipeline/topview.py render {out / 'manifest.json'}")
    return 0


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    plan_path, out_dir, config_path = argv[0], None, None
    rest = argv[1:]
    while rest:
        flag = rest.pop(0)
        if flag == "--out":
            out_dir = rest.pop(0) if rest else die("--out needs a path")
        elif flag == "--config":
            config_path = rest.pop(0) if rest else die("--config needs a path")
        else:
            raise PipelineError(f"unknown flag: {flag}")
    return build(plan_path, out_dir, config_path)


if __name__ == "__main__":
    run_cli(main)

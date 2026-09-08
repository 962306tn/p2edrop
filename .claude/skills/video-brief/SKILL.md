---
name: video-brief
description: Turn a marketing brief into ready-to-render video prompts and render them on Topview (Seedance, Veo, Kling) and Superscale. Use when the user drops a brief, product description, or angle list and wants ad videos, UGC clips, TOF/MOF/BOF creatives, or a batch of variants - in any language.
---

# Brief -> prompt pack -> rendered videos

The split that makes this work: **you write the creative, the scripts do the plumbing.**
Never hand-write task ids, poll loops, or per-scene JSON - `pipeline/` already does that,
and it is what keeps a re-run from paying twice for the same clip.

## Steps

### 1. Read the brief, fill the gaps

Needed before writing anything: brand + product, market, language, funnel stage,
formats and how many angles each, duration, aspect ratio, tone. Anything the brief
does not say, choose a sane default and state the choice in one line - do not
interrogate the user. Only ask when a wrong guess would waste render credits
(for example: language, or vertical vs square).

### 2. Write `plan.json`

Copy the shape of `pipeline/briefs/example-plan.json`. Rules that matter:

- One entry in `variants` per format x angle. `id` is `NN-short-slug`, unique.
- `hook` must land in the first 2 seconds and be a sentence a human would actually
  say. `backup_hook` is a genuinely different opening, not a paraphrase.
- 3-6 `scenes` per variant. Each scene: `visual` (what the camera sees - subject,
  place, time of day, action), plus `camera`, `duration`, `vo`, and `overlay` when
  there is burned-in text. Write visuals as shots, not as summaries of the message.
- Keep the brand promise out of the model prompt: no claims, no logos, no packaging
  text. Those belong in `caption`, `cta` and the captions burned in later.
- `style` and `negative_prompt` at plan level keep 10 variants looking like one campaign.
- Language: write `hook`, `vo`, `caption`, `cta` in the brief's target language;
  keep `visual`/`camera` in English - the video models are trained on English prompts.

Validate as you go: `python3 pipeline/build_pack.py plan.json` fails loudly on a
malformed plan.

### 3. Build the pack

```bash
python3 pipeline/build_pack.py plan.json --out out/<slug>
```

Produces per variant: `script.md` (human review), `seedance.txt` (paste-into-UI
prompts), `topview.json` (API bodies), `superscale.json` (post-production hand-off),
plus `manifest.json` and `INDEX.md` for the whole pack.

### 4. Show before you spend

```bash
python3 pipeline/topview.py render out/<slug>/manifest.json --dry-run --limit 2
```

Show the user `INDEX.md` and one full variant `script.md`. Rendering costs credits,
so **get an explicit go-ahead before the first real render**, and suggest
`--only <variant>` for a single-variant test first.

### 5. Render

```bash
python3 pipeline/topview.py render out/<slug>/manifest.json --only 01-...   # test one
python3 pipeline/topview.py render out/<slug>/manifest.json                 # the rest
python3 pipeline/superscale.py push out/<slug>/manifest.json                # stitch
```

Resumable: task ids live in `out/<slug>/.state.json`. If a run times out or the
laptop sleeps, re-run the same command - it picks the tasks back up instead of
re-submitting. Failed clips stay failed until `--retry-failed`.

## When the API is not available

Topview's Ultra and Team plans include MCP but not the REST API. If
`topview.py doctor` returns 403, do not keep retrying - switch to the Topview MCP
server (`/mcp` in Claude Code, see `docs/topview-superscale.md`) and drive rendering
through its tools, feeding it the prompts from `seedance.txt` one variant at a time.
The pack, the review step and the credit-consent rule stay exactly the same.

## Do not

- Do not invent Topview endpoint paths in code. They live in `pipeline/providers.json`;
  if one is wrong, run `topview.py doctor` and fix the config.
- Do not render every variant before the user has seen a single one.
- Do not put subtitles in the model prompt unless `overlay` asks for it - burned-in
  text is added in post, where it is legible and correct.

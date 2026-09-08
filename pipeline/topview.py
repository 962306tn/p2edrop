#!/usr/bin/env python3
"""Render a manifest on Topview (Seedance, Veo, Kling, Wan, Vidu, Hailuo...).

  python3 pipeline/topview.py doctor                       # credentials + credit balance
  python3 pipeline/topview.py estimate out/<slug>/manifest.json
  python3 pipeline/topview.py render   out/<slug>/manifest.json [flags]
  python3 pipeline/topview.py query <taskId> --module t2v

render flags:
  --dry-run          print the payloads, submit nothing, spend nothing
  --only <variant>   render one variant (repeatable)
  --limit N          submit at most N clips this run
  --retry-failed     re-submit clips that previously failed
  --yes              skip the cost confirmation
  --config <path>    alternative providers.json

Submitted task ids are written to <out>/.state.json, so re-running resumes and
never pays twice for a clip that already has a task id.
"""

import json
import time
from pathlib import Path

from common import (
    PipelineError,
    State,
    Topview,
    die,
    download,
    estimate_credits,
    load_config,
    load_env_file,
    load_models,
    log,
    run_cli,
    task_state,
)


def load_manifest(path):
    path = Path(path)
    if not path.exists():
        die(f"manifest not found: {path}")
    return json.loads(path.read_text()), path.parent


def select(jobs, only, limit=None):
    picked = [j for j in jobs if not only or j["variant"] in only]
    if not picked:
        die("no jobs matched")
    return picked[:limit] if limit else picked


def cost_of(models, job):
    body = job["payload"]
    return estimate_credits(
        models,
        body.get("model", ""),
        body.get("resolution"),
        body.get("duration"),
        sound=str(body.get("sound", "off")).lower() == "on",
        count=body.get("generatingCount", 1),
    )


def summarise_cost(models, jobs):
    """(total, unpriced) - unpriced clips are models missing from the rate table."""
    total, unpriced = 0.0, 0
    for job in jobs:
        credits = cost_of(models, job)
        if credits is None:
            unpriced += 1
        else:
            total += credits
    return round(total, 2), unpriced


def cmd_doctor(cfg, argv):
    client = Topview(cfg)
    log(f"base_url: {client.base}")
    log("credentials: present")
    credit = client.credit()
    log(f"credit balance: {credit}")
    log("")
    log("Endpoints in use:")
    for name, mod in cfg["modules"].items():
        log(f"  {name:<11} {mod['submit']}")
    log("")
    log("Auth and the account endpoint answered, so the key, the uid and the base")
    log("url are all good. A 403 here instead would mean the plan has no API access")
    log("(Ultra and Team are MCP-only) - connect the MCP server and render there.")
    return 0


def cmd_estimate(cfg, argv):
    if not argv:
        die("usage: topview.py estimate out/<slug>/manifest.json")
    manifest, _ = load_manifest(argv[0])
    models = load_models()
    jobs = manifest["jobs"]

    by_variant = {}
    for job in jobs:
        by_variant.setdefault(job["variant"], []).append(job)

    log(f"{len(jobs)} clip(s) across {len(by_variant)} variant(s)")
    log("")
    for variant, group in by_variant.items():
        total, unpriced = summarise_cost(models, group)
        note = f" (+{unpriced} unpriced)" if unpriced else ""
        log(f"  {variant:<28} {len(group)} clips  ~{total} credits{note}")
    total, unpriced = summarise_cost(models, jobs)
    log("")
    log(f"estimated total: ~{total} credits")
    if unpriced:
        log(f"{unpriced} clip(s) use a model with no local price - the real total is higher")
    log("Estimates come from Topview's own published rate table; the invoice is authoritative.")
    return 0


def cmd_query(cfg, argv):
    if not argv:
        die("usage: topview.py query <taskId> --module t2v")
    task_id, module = argv[0], "t2v"
    rest = argv[1:]
    while rest:
        flag = rest.pop(0)
        if flag == "--module":
            module = rest.pop(0) if rest else die("--module needs a value")
        else:
            die(f"unknown flag: {flag}")
    result = Topview(cfg).query(module, task_id)
    state, url, err = task_state(result)
    log(f"{task_id}: {state}{' - ' + err if err else ''}")
    if url:
        log(f"asset: {url}")
    log(json.dumps(result, indent=2, ensure_ascii=False)[:2000])
    return 0


def cmd_render(cfg, argv):
    if not argv:
        die("usage: topview.py render out/<slug>/manifest.json")
    manifest, out_dir = load_manifest(argv[0])
    dry_run = assume_yes = retry_failed = False
    only, limit = [], None
    rest = argv[1:]
    while rest:
        flag = rest.pop(0)
        if flag == "--dry-run":
            dry_run = True
        elif flag == "--yes":
            assume_yes = True
        elif flag == "--retry-failed":
            retry_failed = True
        elif flag == "--only":
            only.append(rest.pop(0) if rest else die("--only needs a variant id"))
        elif flag == "--limit":
            limit = int(rest.pop(0)) if rest else die("--limit needs a number")
        else:
            die(f"unknown flag: {flag}")

    models = load_models()
    jobs = select(manifest["jobs"], only, limit)

    if dry_run:
        for job in jobs:
            credits = cost_of(models, job)
            log(f"--- {job['job_id']} [{job['module']}] ~{credits if credits is not None else '?'} credits")
            log(json.dumps(job["payload"], indent=2, ensure_ascii=False))
        total, unpriced = summarise_cost(models, jobs)
        log(f"\n{len(jobs)} job(s), ~{total} credits{f' (+{unpriced} unpriced)' if unpriced else ''}. Nothing was sent.")
        return 0

    client = Topview(cfg)
    state = State(out_dir / ".state.json")

    pending = []
    for job in jobs:
        entry = state.get(job["job_id"])
        if entry.get("status") == "done" and (out_dir / job["output"]).exists():
            continue
        if entry.get("status") == "failed" and not retry_failed:
            log(f"skip {job['job_id']}: failed previously ({entry.get('error', '')[:70]}) - use --retry-failed")
            continue
        pending.append(job)
    if not pending:
        log("nothing to do - every clip is already rendered")
        return 0

    total, unpriced = summarise_cost(models, pending)
    fresh = [j for j in pending if not state.get(j["job_id"]).get("task_id")]
    log(f"{len(pending)} clip(s) to render ({len(fresh)} new submissions), ~{total} credits"
        + (f" plus {unpriced} unpriced" if unpriced else ""))
    if fresh and not assume_yes:
        try:
            balance = client.credit()
            log(f"credit balance: {balance}")
        except PipelineError as exc:
            log(f"could not read credit balance: {exc}")
        answer = input("proceed? [y/N] ").strip().lower()
        if answer not in ("y", "yes"):
            log("aborted, nothing submitted")
            return 0

    queue, inflight, failures = list(pending), {}, 0
    deadline = time.time() + cfg["poll_timeout_seconds"]

    while queue or inflight:
        while queue and len(inflight) < cfg["max_concurrent_tasks"]:
            job = queue.pop(0)
            entry = state.get(job["job_id"])
            task_id = entry.get("task_id") if entry.get("status") != "failed" else None
            if task_id:
                log(f"resume {job['job_id']} (task {task_id})")
            else:
                try:
                    payload = dict(job["payload"])
                    for field in job.get("upload_fields", []):
                        ref = payload.get(field)
                        # A local path has to become a Topview fileId first; an id
                        # from a previous run passes straight through.
                        if ref and Path(ref).exists():
                            log(f"upload {Path(ref).name} for {job['job_id']}")
                            payload[field] = client.upload(ref)
                    task_id = client.submit(job["module"], payload)
                except PipelineError as exc:
                    log(f"FAIL   {job['job_id']}: {exc}")
                    state.update(job["job_id"], status="failed", error=str(exc))
                    failures += 1
                    continue
                log(f"submit {job['job_id']} -> {task_id}")
                state.update(job["job_id"], task_id=task_id, status="running")
            inflight[job["job_id"]] = job

        if not inflight:
            continue
        time.sleep(cfg["poll_interval_seconds"])

        for job_id, job in list(inflight.items()):
            task_id = state.get(job_id)["task_id"]
            try:
                result = client.query(job["module"], task_id)
            except PipelineError as exc:
                log(f"warn   {job_id}: {exc}")
                continue
            status, url, err = task_state(result)
            if status == "running":
                continue
            inflight.pop(job_id)
            if status == "failed":
                log(f"FAIL   {job_id}: {err}")
                state.update(job_id, status="failed", error=err)
                failures += 1
                continue
            dest = out_dir / job["output"]
            try:
                download(url, dest)
            except PipelineError as exc:
                # The clip rendered and was charged for; only the fetch failed, so
                # keep the task id and let a re-run pick the asset up again.
                log(f"warn   {job_id}: {exc}")
                state.update(job_id, status="running", url=url)
                failures += 1
                continue
            spent = result.get("costCredit")
            log(f"done   {job_id} -> {dest}" + (f" ({spent} credits)" if spent is not None else ""))
            state.update(job_id, status="done", url=url, file=str(dest), cost=spent)

        if time.time() > deadline and inflight:
            die(
                f"timed out with {len(inflight)} task(s) still running. Task ids are in "
                f"{out_dir / '.state.json'} - re-run the same command to resume."
            )

    done = sum(1 for v in state.data.values() if v.get("status") == "done")
    spent = sum(v.get("cost") or 0 for v in state.data.values() if v.get("status") == "done")
    log(f"\n{done} clip(s) under {out_dir / 'renders'}, {failures} failed"
        + (f", {round(spent, 2)} credits spent" if spent else ""))
    if failures:
        log("re-run with --retry-failed once you have fixed the cause")
    return 1 if failures else 0


COMMANDS = {"doctor": cmd_doctor, "estimate": cmd_estimate, "render": cmd_render, "query": cmd_query}


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    command, rest = argv[0], list(argv[1:])
    if command not in COMMANDS:
        die(f"unknown command '{command}' - one of: {', '.join(COMMANDS)}")
    config_path = None
    if "--config" in rest:
        i = rest.index("--config")
        config_path = rest[i + 1] if i + 1 < len(rest) else die("--config needs a path")
        del rest[i : i + 2]
    load_env_file()
    return COMMANDS[command](load_config(config_path)["topview"], rest)


if __name__ == "__main__":
    run_cli(main)

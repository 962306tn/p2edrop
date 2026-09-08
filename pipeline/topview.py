#!/usr/bin/env python3
"""Render a manifest on Topview (Seedance, Veo, Kling ... - whatever your key allows).

  python3 pipeline/topview.py doctor                     # check key, headers, endpoints
  python3 pipeline/topview.py render out/<slug>/manifest.json [flags]
  python3 pipeline/topview.py query <taskId> [--module video_gen]

render flags:
  --dry-run          print the payloads, submit nothing, spend nothing
  --only <variant>   render one variant (repeatable)
  --limit N          submit at most N clips this run
  --retry-failed     re-submit jobs that previously failed
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
    classify,
    die,
    dig,
    download,
    find_media_urls,
    headers_for,
    load_config,
    load_env_file,
    log,
    request_json,
    run_cli,
)

PROVIDER = "topview"


def module_cfg(config, module):
    cfg = config[PROVIDER]["modules"].get(module)
    if not cfg:
        die(f"unknown module '{module}' - known: {', '.join(config[PROVIDER]['modules'])}")
    return cfg


def submit(config, headers, module, payload):
    cfg = config[PROVIDER]
    url = cfg["base_url"].rstrip("/") + module_cfg(config, module)["submit"]
    status, body = request_json("POST", url, headers, payload)
    if status >= 400:
        raise PipelineError(f"submit failed ({status}) at {url}: {json.dumps(body)[:400]}")
    task_id = dig(body, cfg["task_id_keys"])
    if not task_id:
        raise PipelineError(f"no task id in submit response from {url}: {json.dumps(body)[:400]}")
    return str(task_id), body


def query(config, headers, module, task_id):
    cfg = config[PROVIDER]
    base = cfg["base_url"].rstrip("/") + module_cfg(config, module)["query"]
    status, body = request_json("GET", f"{base}?taskId={task_id}", headers)
    if status >= 400 or not isinstance(body, dict):
        # Some Topview modules take the id in a POST body instead of the query string.
        status, body = request_json("POST", base, headers, {"taskId": task_id})
    if status >= 400:
        raise PipelineError(f"query failed ({status}) for {task_id}: {json.dumps(body)[:400]}")
    return classify(dig(body, cfg["status_keys"]), cfg), body


def cmd_doctor(config, argv):
    cfg = config[PROVIDER]
    log(f"base_url: {cfg['base_url']}")
    headers = headers_for(cfg, PROVIDER)
    shown = {k: (v[:12] + "..." if k == cfg["auth_header"] else v) for k, v in headers.items()}
    log(f"headers:  {json.dumps(shown)}")
    log("")
    log("Probing endpoints with a deliberately empty body. 401/403 means the key or")
    log("Uid is wrong; 404 means the path is wrong; 400/422 means the path is RIGHT")
    log("and it is only complaining about the empty body - that is the answer you want.")
    log("")
    for name, mod in cfg["modules"].items():
        for path in mod.get("candidates", [mod["submit"]]):
            url = cfg["base_url"].rstrip("/") + path
            try:
                status, body = request_json("POST", url, headers, {})
            except PipelineError as exc:
                log(f"  [{name}] {path} -> {exc}")
                continue
            verdict = {
                400: "PATH OK (rejected empty body)",
                422: "PATH OK (rejected empty body)",
                401: "AUTH FAILED - check TOPVIEW_API_KEY",
                403: "FORBIDDEN - key lacks API access (Ultra/Team plans are MCP-only)",
                404: "not this path",
            }.get(status, "unexpected")
            marker = "*" if path == mod["submit"] else " "
            log(f" {marker}[{name}] {status} {path} - {verdict}")
            snippet = json.dumps(body)[:160] if not isinstance(body, str) else body[:160]
            log(f"      {snippet}")
    log("")
    log("Set 'submit'/'query' in pipeline/providers.json to whichever path answered")
    log("400/422. Lines marked * are the paths currently configured.")
    return 0


def cmd_query(config, argv):
    if not argv:
        die("usage: topview.py query <taskId> [--module video_gen]")
    task_id = argv[0]
    module = "video_gen"
    rest = argv[1:]
    while rest:
        flag = rest.pop(0)
        if flag == "--module":
            module = rest.pop(0) if rest else die("--module needs a value")
        else:
            die(f"unknown flag: {flag}")
    headers = headers_for(config[PROVIDER], PROVIDER)
    state, body = query(config, headers, module, task_id)
    log(f"{task_id}: {state}")
    log(json.dumps(body, indent=2, ensure_ascii=False)[:2000])
    for url in find_media_urls(body):
        log(f"asset: {url}")
    return 0


def cmd_render(config, argv):
    if not argv:
        die("usage: topview.py render out/<slug>/manifest.json")
    manifest_path = Path(argv[0])
    if not manifest_path.exists():
        die(f"manifest not found: {manifest_path}")
    dry_run = False
    only, limit, retry_failed = [], None, False
    rest = argv[1:]
    while rest:
        flag = rest.pop(0)
        if flag == "--dry-run":
            dry_run = True
        elif flag == "--only":
            only.append(rest.pop(0) if rest else die("--only needs a variant id"))
        elif flag == "--limit":
            limit = int(rest.pop(0)) if rest else die("--limit needs a number")
        elif flag == "--retry-failed":
            retry_failed = True
        else:
            die(f"unknown flag: {flag}")

    manifest = json.loads(manifest_path.read_text())
    out_dir = manifest_path.parent
    jobs = [j for j in manifest["jobs"] if j["provider"] == PROVIDER]
    if only:
        jobs = [j for j in jobs if j["variant"] in only]
    if not jobs:
        die("no jobs matched")

    if dry_run:
        for job in jobs[: limit or len(jobs)]:
            log(f"--- {job['job_id']} ({job['module']})")
            log(json.dumps(job["payload"], indent=2, ensure_ascii=False))
        log(f"\n{len(jobs)} jobs would be submitted. Nothing was sent.")
        return 0

    cfg = config[PROVIDER]
    headers = headers_for(cfg, PROVIDER)
    state = State(out_dir / ".state.json")

    pending = []
    for job in jobs:
        entry = state.get(job["job_id"])
        if entry.get("status") == "done" and (out_dir / job["output"]).exists():
            continue
        if entry.get("status") == "failed" and not retry_failed:
            log(f"skip {job['job_id']}: failed previously ({entry.get('error', '')[:80]}) - use --retry-failed")
            continue
        pending.append(job)
    if limit:
        pending = pending[:limit]
    if not pending:
        log("nothing to do - every clip is already rendered")
        return 0

    log(f"{len(pending)} clip(s) to render, up to {cfg['max_concurrent_tasks']} at a time")

    queue = list(pending)
    inflight = {}
    deadline = time.time() + cfg["poll_timeout_seconds"]
    failures = 0

    while queue or inflight:
        while queue and len(inflight) < cfg["max_concurrent_tasks"]:
            job = queue.pop(0)
            entry = state.get(job["job_id"])
            task_id = entry.get("task_id") if entry.get("status") != "failed" else None
            if task_id:
                log(f"resume {job['job_id']} (task {task_id})")
            else:
                try:
                    task_id, _ = submit(config, headers, job["module"], job["payload"])
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
                status, body = query(config, headers, job["module"], task_id)
            except PipelineError as exc:
                log(f"warn   {job_id}: {exc}")
                continue
            if status == "running":
                continue
            inflight.pop(job_id)
            if status == "failed":
                msg = str(dig(body, ["errorMsg", "error_msg", "message", "error"]) or "unknown error")
                log(f"FAIL   {job_id}: {msg}")
                state.update(job_id, status="failed", error=msg)
                failures += 1
                continue
            urls = find_media_urls(body)
            if not urls:
                log(f"FAIL   {job_id}: task succeeded but no asset url in response")
                state.update(job_id, status="failed", error="no asset url")
                failures += 1
                continue
            dest = out_dir / job["output"]
            download(urls[0], dest)
            log(f"done   {job_id} -> {dest}")
            state.update(job_id, status="done", url=urls[0], file=str(dest))

        if time.time() > deadline and inflight:
            for job_id in inflight:
                state.update(job_id, status="running")
            die(
                f"timed out with {len(inflight)} task(s) still running. Task ids are in "
                f"{out_dir / '.state.json'} - re-run the same command to resume."
            )

    done = sum(1 for v in state.data.values() if v.get("status") == "done")
    log(f"\n{done} clip(s) rendered under {out_dir / 'renders'}, {failures} failed")
    if failures:
        log("re-run with --retry-failed once you have fixed the cause")
    return 1 if failures else 0


COMMANDS = {"doctor": cmd_doctor, "render": cmd_render, "query": cmd_query}


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
    return COMMANDS[command](load_config(config_path), rest)


if __name__ == "__main__":
    run_cli(main)

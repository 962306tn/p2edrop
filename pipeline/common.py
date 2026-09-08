"""Shared plumbing for the render backends: config, HTTP, task polling, state.

Stdlib only on purpose - the pipeline has to run on a laptop with nothing
installed but Python 3.9+.
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = ROOT / "providers.json"

_ENV_REF = re.compile(r"\$\{([A-Z0-9_]+)\}")


class PipelineError(Exception):
    """Anything the user can fix by editing config, env or a brief."""


def die(msg):
    raise PipelineError(msg)


def load_config(path=None):
    path = Path(path) if path else DEFAULT_CONFIG
    if not path.exists():
        die(f"config not found: {path}")
    return json.loads(path.read_text())


def load_env_file(path=None):
    """Read KEY=VALUE lines from .env without overwriting the real environment."""
    path = Path(path) if path else ROOT.parent / ".env"
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip("'\"")
        os.environ.setdefault(key, value)


def expand(value):
    """Replace ${VAR} with the environment, leaving unset vars visible as-is."""
    return _ENV_REF.sub(lambda m: os.environ.get(m.group(1), m.group(0)), value)


def headers_for(provider_cfg, provider_name):
    key_env = provider_cfg.get("api_key_env", "")
    key = os.environ.get(key_env, "").strip()
    if not key:
        die(
            f"{key_env} is not set - export it or put it in .env "
            f"(see docs/topview-superscale.md for where {provider_name} shows the key)"
        )
    scheme = provider_cfg.get("auth_scheme", "Bearer")
    headers = {
        provider_cfg.get("auth_header", "Authorization"): f"{scheme} {key}".strip(),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    for name, value in (provider_cfg.get("extra_headers") or {}).items():
        resolved = expand(value)
        if _ENV_REF.search(resolved):
            missing = _ENV_REF.findall(resolved)[0]
            die(f"{provider_name} needs header {name}, but ${{{missing}}} is not set")
        headers[name] = resolved
    return headers


def request_json(method, url, headers, payload=None, timeout=60):
    """One HTTP call. Returns (status_code, parsed_body_or_text)."""
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "replace")
            return resp.status, _maybe_json(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        return exc.code, _maybe_json(body)
    except urllib.error.URLError as exc:
        die(f"cannot reach {url}: {exc.reason}")


def _maybe_json(text):
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return text


def dig(obj, keys):
    """First value found under any of `keys`, searched depth-first."""
    if isinstance(obj, dict):
        for key in keys:
            if key in obj and obj[key] not in (None, ""):
                return obj[key]
        for value in obj.values():
            found = dig(value, keys)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = dig(item, keys)
            if found is not None:
                return found
    return None


def find_media_urls(obj):
    """Every http(s) URL in a response that looks like a rendered asset."""
    out = []

    def walk(node):
        if isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, str) and node.startswith("http"):
            clean = node.split("?", 1)[0].lower()
            if clean.endswith((".mp4", ".mov", ".webm", ".png", ".jpg", ".jpeg", ".mp3", ".wav")):
                out.append(node)

    walk(obj)
    return list(dict.fromkeys(out))


def classify(status_value, provider_cfg):
    """Map a provider's status string onto done / failed / running."""
    text = str(status_value or "").strip().lower()
    if any(text == v or text.startswith(v) for v in provider_cfg.get("success_values", [])):
        return "done"
    if any(v in text for v in provider_cfg.get("failure_values", [])):
        return "failed"
    return "running"


def download(url, dest, timeout=300):
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "p2edrop-pipeline"})
    with urllib.request.urlopen(req, timeout=timeout) as resp, open(dest, "wb") as fh:
        while True:
            chunk = resp.read(1 << 16)
            if not chunk:
                break
            fh.write(chunk)
    return dest


class State:
    """Resume file. Rendering costs credits, so a re-run must never re-submit
    a job that already has a taskId."""

    def __init__(self, path):
        self.path = Path(path)
        self.data = json.loads(self.path.read_text()) if self.path.exists() else {}

    def get(self, job_id):
        return self.data.get(job_id, {})

    def update(self, job_id, **fields):
        entry = self.data.setdefault(job_id, {})
        entry.update(fields)
        self.save()
        return entry

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False))


def log(msg):
    print(msg, flush=True)


def run_cli(main):
    """Turn PipelineError into a clean message instead of a traceback."""
    try:
        sys.exit(main(sys.argv[1:]) or 0)
    except PipelineError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        sys.exit(130)

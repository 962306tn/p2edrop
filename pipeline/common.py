"""Shared plumbing: config, the Topview HTTP envelope, task state, downloads.

Stdlib only on purpose - the pipeline has to run on a laptop with nothing
installed but Python 3.9+.
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = ROOT / "providers.json"
MODELS_FILE = ROOT / "models.json"

# Topview returns HTTP 200 with a code field for business errors, so the code is
# the real status. These are the ones worth naming in an error message.
RESPONSE_CODES = {
    "401": "unauthorized - check TOPVIEW_API_KEY and TOPVIEW_UID",
    "4000": "request parameter error",
    "4003": "a required parameter was null",
    "4004": "resource not found",
    "4006": "request refused",
    "4007": "an unfinished task already exists, wait for it",
    "4100": "not enough credits",
    "5000": "internal server error at Topview",
    "5003": "Topview is busy, try again later",
    "6001": "content flagged by Topview's safety check",
}


class PipelineError(Exception):
    """Anything the user can fix by editing config, env, or a plan."""


def die(msg):
    raise PipelineError(msg)


def load_config(path=None):
    path = Path(path) if path else DEFAULT_CONFIG
    if not path.exists():
        die(f"config not found: {path}")
    return json.loads(path.read_text())


def load_models():
    return json.loads(MODELS_FILE.read_text())


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
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


class Topview:
    """Authenticated client for api.topview.ai.

    Mirrors the request/response contract of Topview's own published client:
    two auth headers, a {code, message, result} envelope, and task endpoints
    that take taskId as a query parameter.
    """

    def __init__(self, cfg):
        self.cfg = cfg
        self.base = cfg["base_url"].rstrip("/")
        key = os.environ.get(cfg["api_key_env"], "").strip()
        uid = os.environ.get(cfg["uid_env"], "").strip()
        missing = [n for n, v in ((cfg["api_key_env"], key), (cfg["uid_env"], uid)) if not v]
        if missing:
            die(
                f"{' and '.join(missing)} not set - put them in .env or export them. "
                "Topview shows both under Settings -> API Keys."
            )
        self.headers = {
            "Authorization": f"Bearer {key}",
            "Topview-Uid": uid,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def module(self, name):
        mod = self.cfg["modules"].get(name)
        if not mod:
            die(f"unknown module '{name}' - known: {', '.join(self.cfg['modules'])}")
        return mod

    def _call(self, method, path, params=None, payload=None, timeout=60):
        url = self.base + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(url, data=data, headers=self.headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")
            if exc.code == 401:
                die("401 from Topview - the API key or uid is wrong")
            die(f"HTTP {exc.code} from {path}: {body[:300]}")
        except urllib.error.URLError as exc:
            die(f"cannot reach {url}: {exc.reason}")
        try:
            parsed = json.loads(body)
        except ValueError:
            die(f"{path} did not return JSON: {body[:300]}")
        return self._unwrap(parsed, path)

    @staticmethod
    def _unwrap(parsed, path):
        """Topview signals failure inside a 200 response, so check code, not status."""
        if not isinstance(parsed, dict):
            return parsed
        code = str(parsed.get("code", "200"))
        if code != "200":
            known = RESPONSE_CODES.get(code, "")
            msg = parsed.get("message") or known or "unknown error"
            detail = f" ({known})" if known and known != msg else ""
            raise PipelineError(f"Topview [{code}] {msg}{detail} at {path}")
        return parsed.get("result", parsed)

    def get(self, path, params=None, timeout=60):
        return self._call("GET", path, params=params, timeout=timeout)

    def post(self, path, payload=None, timeout=60):
        return self._call("POST", path, payload=payload, timeout=timeout)

    def credit(self):
        result = self.get(self.cfg["credit_path"])
        return result.get("credit", result) if isinstance(result, dict) else result

    def submit(self, module, payload):
        result = self.post(self.module(module)["submit"], payload)
        task_id = result.get("taskId") if isinstance(result, dict) else None
        if not task_id:
            die(f"no taskId in submit response: {json.dumps(result)[:300]}")
        return str(task_id)

    def query(self, module, task_id):
        return self.get(self.module(module)["query"], params={"taskId": task_id})

    def upload(self, file_path):
        """Three-step upload: credential -> PUT to S3 -> verify. Returns a fileId."""
        path = Path(file_path)
        if not path.exists():
            die(f"file not found: {path}")
        fmt = path.suffix.lstrip(".").lower()
        if fmt not in {"png", "jpg", "jpeg", "bmp", "webp", "mp3", "wav", "m4a", "mp4", "avi", "mov"}:
            die(f"Topview does not accept .{fmt} uploads")
        cred = self.get(self.cfg["upload"]["credential"], params={"format": fmt, "needAccelerateUrl": ""})
        file_id, upload_url = cred["fileId"], cred["uploadUrl"]
        req = urllib.request.Request(upload_url, data=path.read_bytes(), method="PUT")
        try:
            urllib.request.urlopen(req, timeout=300)
        except urllib.error.URLError as exc:
            die(f"upload of {path.name} failed: {exc}")
        check = self.get(self.cfg["upload"]["check"], params={"fileId": file_id})
        if check is not True and str(check).lower() != "true":
            die(f"Topview did not accept the upload of {path.name}")
        return file_id


def task_state(result):
    """(state, url, error) for a finished or running task result.

    A task carries an overall status plus a videos/images list whose entries have
    their own status - a clip can fail inside a task that reports success.
    """
    status = str((result or {}).get("status", "")).lower()
    items = (result or {}).get("videos") or (result or {}).get("images") or []
    if status in ("failed", "fail", "error"):
        first_err = next((i.get("errorMsg") for i in items if i.get("errorMsg")), "")
        return "failed", None, result.get("errorMsg") or first_err or "task failed"
    if status != "success":
        return "running", None, None
    for item in items:
        if str(item.get("status", "")).lower() == "success" and item.get("filePath"):
            return "done", item["filePath"], None
    err = next((i.get("errorMsg") for i in items if i.get("errorMsg")), "")
    return "failed", None, err or "task reported success but returned no file"


def download(url, dest, timeout=600):
    """Fetch a rendered asset. The url is pre-signed, so it carries no auth headers.

    A download that dies must not take the run with it: the clip is already paid
    for and the task id is in the state file, so the caller reports it and moves on.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "p2edrop-pipeline"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp, open(dest, "wb") as fh:
            while True:
                chunk = resp.read(1 << 16)
                if not chunk:
                    break
                fh.write(chunk)
    except (urllib.error.URLError, OSError) as exc:
        dest.unlink(missing_ok=True)
        die(f"could not download {url[:80]}: {exc}")
    return dest


def resolve_model(models, task_type, name):
    """Registry key for a model name, tolerating Topview's display-name aliases."""
    return models["aliases"].get(name, name)


def api_model_name(models, task_type, name):
    """The exact string the submit endpoint wants - it differs per task type."""
    key = resolve_model(models, task_type, name)
    return models["api_names"].get(task_type, {}).get(key, key)


def model_warnings(models, task_type, name, aspect_ratio, resolution, duration):
    """Parameter mismatches, as warnings. The API is the authority, not this table:
    Topview ships models faster than the table is regenerated, so an unknown model
    is reported once and then sent anyway."""
    key = resolve_model(models, task_type, name)
    registry = models["models"].get(task_type, {})
    spec = registry.get(key)
    if not spec:
        return [f"model '{name}' is not in the local table for {task_type} - sending it anyway"]

    out = []
    if aspect_ratio:
        allowed = spec.get("aspectRatio")
        if allowed is None:
            out.append(f"'{key}' ignores aspectRatio (sent '{aspect_ratio}')")
        elif aspect_ratio not in allowed:
            out.append(f"'{key}' supports aspectRatio {allowed}, got '{aspect_ratio}'")
    if resolution:
        allowed = spec.get("resolution")
        if allowed is None:
            out.append(f"'{key}' ignores resolution (sent {resolution})")
        elif resolution not in allowed:
            out.append(f"'{key}' supports resolution {allowed}, got {resolution}")
    if duration and spec.get("duration"):
        spec_dur = spec["duration"]
        if "," in spec_dur:
            ok = duration in [int(x) for x in spec_dur.split(",")]
        elif "-" in spec_dur:
            lo, hi = (int(x) for x in spec_dur.split("-"))
            ok = lo <= duration <= hi
        else:
            ok = duration == int(spec_dur)
        if not ok:
            out.append(f"'{key}' supports duration {spec_dur}s, got {duration}s")
    return out


def estimate_credits(models, model, resolution, duration, sound=False, count=1):
    """Credits for one clip, or None when the model is not in the rate table."""
    key = resolve_model(models, None, model)
    rates = models["rates"].get(key)
    if not rates or not duration:
        return None
    res = resolution or 0
    tone = "on" if sound else "off"
    for candidate in (f"{res}|{tone}", f"{res}|any", f"0|{tone}", "0|any"):
        if candidate in rates:
            return round(rates[candidate] * duration * (count or 1), 2)
    return None


class State:
    """Resume file. Rendering costs credits, so a re-run must never re-submit a
    job that already has a task id."""

    def __init__(self, path):
        self.path = Path(path)
        self.data = json.loads(self.path.read_text()) if self.path.exists() else {}

    def get(self, job_id):
        return self.data.get(job_id, {})

    def update(self, job_id, **fields):
        entry = self.data.setdefault(job_id, {})
        entry.update(fields)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False))
        return entry


def log(msg=""):
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

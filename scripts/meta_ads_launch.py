#!/usr/bin/env python3
"""Pipeline chay quang cao Meta tu file ke hoach, dung Meta Ads CLI chinh chu.

Luong: anh/video local + bang creative/copy/URL/UTM
   -> validate  : kiem tra truoc khi goi API (khong ton request nao)
   -> plan      : in ra dung nhung lenh `meta ads ...` se chay (dry-run)
   -> launch    : tao campaign + N ad set + creative + ad, TAT CA deu PAUSED
   -> verify    : soi lai status / URL / UTM / pixel tracking tren landing page
   -> preview   : xuat file HTML gom preview that cua tung ad
   -> activate  : sau khi ban duyet moi bat chay (bat buoc --yes)
   -> pause     : phanh gap, tat het

Moi thao tac ghi/doc deu di qua binary `meta` (PyPI: meta-ads). Rieng preview
va doc mot vai field creative thi Graph API duoc goi truc tiep vi CLI chua ho tro.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ADS_DIR = REPO_ROOT / "ads"
STATE_DIR = ADS_DIR / "state"
OUT_DIR = ADS_DIR / "out"
GRAPH_VERSION = os.environ.get("GRAPH_API_VERSION", "v26.0")

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
VIDEO_EXT = {".mp4", ".mov", ".avi", ".mkv", ".wmv"}
UTM_KEYS = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"]
REQUIRED_COLS = ["adset", "ad_name", "media", "body"]
CTA_VALUES = {
    "APPLY_NOW", "BOOK_TRAVEL", "BUY_NOW", "CONTACT_US", "DOWNLOAD", "GET_OFFER",
    "GET_QUOTE", "LEARN_MORE", "NO_BUTTON", "OPEN_LINK", "SHOP_NOW", "SIGN_UP",
    "SUBSCRIBE", "WATCH_MORE",
}
DEFAULT_PREVIEW_FORMATS = ["MOBILE_FEED_STANDARD", "DESKTOP_FEED_STANDARD", "INSTAGRAM_STANDARD"]

C_RED, C_GRN, C_YEL, C_CYA, C_DIM, C_RST = "\033[31m", "\033[32m", "\033[33m", "\033[36m", "\033[2m", "\033[0m"
if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
    C_RED = C_GRN = C_YEL = C_CYA = C_DIM = C_RST = ""


_SECRETS: set[str] = set()


def redact(text: str) -> str:
    """Xoa token khoi moi thu duoc in ra hoac ghi vao bao cao."""
    text = str(text)
    for secret in _SECRETS:
        if secret and len(secret) > 8:
            text = text.replace(secret, "***REDACTED***")
    return re.sub(r"(access_token=)[^&\s\"']+", r"\1***REDACTED***", text)


def info(msg: str) -> None:
    print(f"{C_CYA}==>{C_RST} {msg}")


def ok(msg: str) -> None:
    print(f"{C_GRN}  OK{C_RST}  {msg}")


def warn(msg: str) -> None:
    print(f"{C_YEL}  WARN{C_RST} {msg}")


def fail(msg: str) -> None:
    print(f"{C_RED}  FAIL{C_RST} {msg}")


def die(msg: str, code: int = 1):
    print(f"{C_RED}[x]{C_RST} {msg}", file=sys.stderr)
    sys.exit(code)


# --------------------------------------------------------------------------- env / config
def load_dotenv(path: Path) -> dict:
    """Doc .env don gian (KEY=VALUE). Khong ghi de bien moi truong da co."""
    env = {}
    if not path.exists():
        return env
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if value[:1] == value[-1:] and value[:1] in {'"', "'"} and len(value) >= 2:
            value = value[1:-1]
        env[key] = value
    return env


ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def expand_env(value, env: dict):
    if isinstance(value, str):
        return ENV_PATTERN.sub(lambda m: env.get(m.group(1), os.environ.get(m.group(1), "")), value)
    if isinstance(value, dict):
        return {k: expand_env(v, env) for k, v in value.items()}
    if isinstance(value, list):
        return [expand_env(v, env) for v in value]
    return value


def load_config(path: Path, env: dict) -> dict:
    if not path.exists():
        die(f"Khong tim thay file cau hinh: {path}")
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except ImportError:
            die("Can PyYAML de doc file .yaml: pip install pyyaml (hoac dung file .json)")
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        die(f"Cau hinh {path} phai la mot object/mapping")
    return expand_env(data, env)


def render(value: str, ctx: dict) -> str:
    """Thay placeholder [[campaign]] / [[adset]] / [[ad]] (khong dung {} de khong
    dung do voi macro dong cua Meta nhu {{ad.name}})."""
    if not isinstance(value, str):
        return value
    for key, val in ctx.items():
        value = value.replace(f"[[{key}]]", str(val))
    return value


def slugify(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower())
    return text.strip("-")[:48] or "run"


# --------------------------------------------------------------------------- CLI wrapper
def meta_bin() -> str:
    found = shutil.which("meta") or shutil.which("meta", path=str(Path.home() / ".local/bin"))
    if not found:
        die("Khong tim thay lenh 'meta'. Chay: bash scripts/setup-meta-ads-cli.sh")
    return found


class MetaCLI:
    def __init__(self, env: dict, dry_run: bool = False):
        self.bin = meta_bin()
        self.dry_run = dry_run
        self.env = dict(os.environ)
        for key in ("ACCESS_TOKEN", "AD_ACCOUNT_ID", "BUSINESS_ID"):
            if env.get(key):
                self.env[key] = env[key]
        self.token = self.env.get("ACCESS_TOKEN", "")
        if self.token:
            _SECRETS.add(self.token)
        self.calls: list[list[str]] = []

    def shell(self, args: list[str]) -> str:
        parts = ["meta", "--output", "json"] + args
        return " ".join(shlex_quote(p) for p in parts)

    def run(self, args: list[str], allow_fail: bool = False):
        cmd = [self.bin, "--output", "json", "--no-input"] + args
        self.calls.append(cmd)
        if self.dry_run:
            print(f"  {C_DIM}$ {self.shell(args)}{C_RST}")
            return {"id": f"DRYRUN_{len(self.calls)}", "_dry_run": True}
        proc = subprocess.run(cmd, capture_output=True, text=True, env=self.env)
        if proc.returncode != 0:
            message = redact((proc.stderr or proc.stdout or "").strip())
            if allow_fail:
                return {"_error": message}
            raise RuntimeError(f"Lenh that bai: {redact(self.shell(args))}\n{message}")
        out = (proc.stdout or "").strip()
        if not out:
            return {}
        try:
            return json.loads(out)
        except json.JSONDecodeError:
            return {"_raw": out}


def shlex_quote(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_@%+=:,./-]+", value or ""):
        return value
    return "'" + (value or "").replace("'", "'\\''") + "'"


def first_id(payload) -> str:
    """Rut id tu nhieu dang tra ve khac nhau cua CLI."""
    if isinstance(payload, dict):
        for key in ("id", "creative_id", "campaign_id", "adset_id", "ad_id"):
            if payload.get(key):
                return str(payload[key])
        for key in ("data", "result", "campaign", "adset", "ad", "creative"):
            if payload.get(key):
                found = first_id(payload[key])
                if found:
                    return found
    if isinstance(payload, list) and payload:
        return first_id(payload[0])
    return ""


# --------------------------------------------------------------------------- Graph API (preview + field doc them)
def graph_get(path: str, params: dict, token: str, timeout: int = 30):
    query = urllib.parse.urlencode({**params, "access_token": token})
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{path}?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": "meta-ads-launch/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        try:
            return {"_error": redact(json.loads(body).get("error", {}).get("message", body))}
        except Exception:
            return {"_error": redact(body)}
    except Exception as exc:  # noqa: BLE001
        return {"_error": redact(str(exc))}


# --------------------------------------------------------------------------- plan (config + csv)
class PlanError(Exception):
    pass


def read_rows(csv_path: Path) -> list[dict]:
    if not csv_path.exists():
        die(f"Khong tim thay bang creative: {csv_path}")
    with csv_path.open(encoding="utf-8-sig", newline="") as fh:
        rows = [
            {(k or "").strip(): (v or "").strip() for k, v in row.items()}
            for row in csv.DictReader(fh)
        ]
    rows = [r for r in rows if any(r.values()) and not r.get("adset", "").startswith("#")]
    if not rows:
        die(f"{csv_path} khong co dong du lieu nao")
    missing = [c for c in REQUIRED_COLS if c not in rows[0]]
    if missing:
        die(f"{csv_path} thieu cot bat buoc: {', '.join(missing)}")
    return rows


def build_url_tags(row: dict, defaults: dict, ctx: dict) -> str:
    pairs = []
    for key in UTM_KEYS:
        value = row.get(key) or defaults.get(key) or ""
        value = render(value, ctx).strip()
        if value:
            pairs.append(f"{key}={urllib.parse.quote(value, safe='{}._~-')}")
    extra = render(row.get("url_tags_extra", "") or defaults.get("url_tags_extra", ""), ctx).strip()
    if extra:
        pairs.append(extra.lstrip("&?"))
    return "&".join(pairs)


def final_url(link: str, url_tags: str) -> str:
    if not url_tags:
        return link
    sep = "&" if "?" in link else "?"
    return f"{link}{sep}{url_tags}"


def registrable_domain(url: str) -> str:
    host = (urllib.parse.urlparse(url).hostname or "").lower()
    host = host[4:] if host.startswith("www.") else host
    return host


def build_plan(config: dict, rows: list[dict], env: dict) -> dict:
    campaign = config.get("campaign") or {}
    defaults = config.get("defaults") or {}
    adsets = config.get("adsets") or []
    errors, warnings = [], []

    name = campaign.get("name")
    if not name:
        errors.append("campaign.name con trong")
    objective = campaign.get("objective", "OUTCOME_SALES")
    budget_mode = str(campaign.get("budget_mode", "CBO")).upper()
    if budget_mode not in {"CBO", "ABO"}:
        errors.append("campaign.budget_mode chi nhan CBO hoac ABO")
    if not adsets:
        errors.append("Chua khai bao adsets nao trong file cau hinh")

    # Ngan sach: CBO => tien o campaign; ABO => tien o tung ad set.
    camp_budget = campaign.get("daily_budget") or campaign.get("lifetime_budget")
    if budget_mode == "CBO":
        if not camp_budget:
            errors.append("CBO can campaign.daily_budget (hoac lifetime_budget), don vi cent")
        for a in adsets:
            if a.get("daily_budget") or a.get("lifetime_budget"):
                errors.append(f"Ad set '{a.get('name')}' khong duoc co ngan sach khi campaign chay CBO")
    else:
        if camp_budget:
            errors.append("ABO thi campaign khong duoc dat ngan sach, hay dat o tung ad set")
        for a in adsets:
            if not (a.get("daily_budget") or a.get("lifetime_budget")):
                errors.append(f"Ad set '{a.get('name')}' thieu daily_budget (ABO)")
            if a.get("lifetime_budget") and not (a.get("end_time") or defaults.get("end_time")):
                errors.append(f"Ad set '{a.get('name')}' dung lifetime_budget nen phai co end_time")

    adset_names = [a.get("name", "") for a in adsets]
    if len(set(adset_names)) != len(adset_names):
        errors.append("Ten ad set bi trung nhau")

    ctx_campaign = {"campaign": name or "", "campaign_slug": slugify(name or "")}
    planned_ads = []
    seen_ad_names = set()
    for index, row in enumerate(rows, start=2):  # dong 2 = dong du lieu dau tien
        where = f"dong {index} ({row.get('ad_name') or 'khong ten'})"
        adset_name = row.get("adset", "")
        if adset_name not in adset_names:
            errors.append(f"{where}: cot adset='{adset_name}' khong khop ad set nao trong config")
        ad_name = row.get("ad_name", "")
        if not ad_name:
            errors.append(f"{where}: thieu ad_name")
        elif ad_name in seen_ad_names:
            errors.append(f"{where}: ad_name '{ad_name}' bi trung")
        seen_ad_names.add(ad_name)

        media_raw = row.get("media", "")
        media_path = (ADS_DIR / media_raw) if media_raw and not Path(media_raw).is_absolute() else Path(media_raw)
        kind = ""
        if not media_raw:
            errors.append(f"{where}: thieu duong dan media")
        elif not media_path.exists():
            errors.append(f"{where}: khong thay file media {media_path}")
        else:
            ext = media_path.suffix.lower()
            if ext in IMAGE_EXT:
                kind = "image"
                size_mb = media_path.stat().st_size / 1e6
                if size_mb > 30:
                    warnings.append(f"{where}: anh {size_mb:.1f}MB, Meta khuyen < 30MB")
            elif ext in VIDEO_EXT:
                kind = "video"
                size_mb = media_path.stat().st_size / 1e6
                if size_mb > 4000:
                    errors.append(f"{where}: video {size_mb:.0f}MB vuot gioi han 4GB")
            else:
                errors.append(f"{where}: duoi file '{ext}' khong duoc ho tro")

        link = row.get("link_url") or defaults.get("link_url", "")
        row_ctx = {**ctx_campaign, "adset": adset_name, "ad": ad_name,
                   "adset_slug": slugify(adset_name), "ad_slug": slugify(ad_name)}
        link = render(link, row_ctx)
        parsed = urllib.parse.urlparse(link)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            errors.append(f"{where}: link_url khong hop le: '{link}'")

        body = row.get("body", "")
        if not body:
            errors.append(f"{where}: thieu body (primary text)")
        if len(body) > 500:
            warnings.append(f"{where}: body dai {len(body)} ky tu, phan sau se bi cat trong feed")
        title = row.get("title", "")
        if title and len(title) > 60:
            warnings.append(f"{where}: headline dai {len(title)} ky tu (nen <= 40)")

        cta = (row.get("cta") or defaults.get("call_to_action") or "SHOP_NOW").upper()
        if cta not in CTA_VALUES:
            errors.append(f"{where}: cta '{cta}' khong hop le")

        url_tags = build_url_tags(row, defaults, row_ctx)
        for required in ("utm_source", "utm_medium", "utm_campaign"):
            if f"{required}=" not in url_tags:
                warnings.append(f"{where}: thieu {required} trong UTM")

        conversion_domain = row.get("conversion_domain") or defaults.get("conversion_domain", "")
        if conversion_domain and registrable_domain(link) and conversion_domain != registrable_domain(link):
            warnings.append(
                f"{where}: conversion_domain '{conversion_domain}' khac domain cua link '{registrable_domain(link)}'"
            )

        planned_ads.append({
            "adset": adset_name,
            "ad_name": ad_name,
            "media": str(media_path),
            "media_kind": kind,
            "body": body,
            "title": title,
            "description": row.get("description", ""),
            "cta": cta,
            "link_url": link,
            "url_tags": url_tags,
            "final_url": final_url(link, url_tags),
            "conversion_domain": conversion_domain,
        })

    for a in adsets:
        if not any(p["adset"] == a.get("name") for p in planned_ads):
            warnings.append(f"Ad set '{a.get('name')}' khong co ad nao trong bang creative")

    if not defaults.get("page_id"):
        errors.append("defaults.page_id con trong (lay bang: meta ads page list)")
    if objective == "OUTCOME_SALES" and not defaults.get("pixel_id"):
        warnings.append("Objective OUTCOME_SALES nhung chua co pixel_id, ad set se khong toi uu chuyen doi")
    if not env.get("ACCESS_TOKEN"):
        errors.append("ACCESS_TOKEN chua co trong ads/.env")
    if not env.get("AD_ACCOUNT_ID"):
        errors.append("AD_ACCOUNT_ID chua co trong ads/.env")

    return {
        "campaign": campaign, "defaults": defaults, "adsets": adsets,
        "ads": planned_ads, "errors": errors, "warnings": warnings,
        "budget_mode": budget_mode, "objective": objective,
    }


# --------------------------------------------------------------------------- dung lenh CLI
def campaign_args(plan: dict) -> list[str]:
    c = plan["campaign"]
    args = ["ads", "campaign", "create", "--name", c["name"], "--objective", plan["objective"], "--status", "PAUSED"]
    if plan["budget_mode"] == "CBO":
        if c.get("daily_budget"):
            args += ["--daily-budget", str(c["daily_budget"])]
        elif c.get("lifetime_budget"):
            args += ["--lifetime-budget", str(c["lifetime_budget"])]
        if c.get("bid_strategy"):
            args += ["--bid-strategy", c["bid_strategy"]]
    for flag, key in (("--spend-cap", "spend_cap"), ("--start-time", "start_time"), ("--stop-time", "stop_time"),
                      ("--special-ad-categories", "special_ad_categories"), ("--buying-type", "buying_type")):
        if c.get(key):
            args += [flag, str(c[key])]
    return args


def adset_args(plan: dict, adset: dict, campaign_id: str) -> list[str]:
    d = plan["defaults"]
    get = lambda key, default=None: adset.get(key, d.get(key, default))  # noqa: E731
    args = ["ads", "adset", "create", campaign_id, "--name", adset["name"], "--status", "PAUSED",
            "--optimization-goal", get("optimization_goal", "OFFSITE_CONVERSIONS"),
            "--billing-event", get("billing_event", "IMPRESSIONS")]
    if plan["budget_mode"] == "ABO":
        if adset.get("daily_budget"):
            args += ["--daily-budget", str(adset["daily_budget"])]
        elif adset.get("lifetime_budget"):
            args += ["--lifetime-budget", str(adset["lifetime_budget"])]
        if get("bid_strategy"):
            args += ["--bid-strategy", str(get("bid_strategy"))]
        if get("bid_amount"):
            args += ["--bid-amount", str(get("bid_amount"))]
    if get("pixel_id"):
        args += ["--pixel-id", str(get("pixel_id"))]
        if get("custom_event_type"):
            args += ["--custom-event-type", str(get("custom_event_type"))]
    targeting_file = adset.get("targeting_file")
    if targeting_file:
        path = ADS_DIR / targeting_file if not Path(targeting_file).is_absolute() else Path(targeting_file)
        args += ["--targeting", f"@{path}"]
    elif adset.get("targeting"):
        args += ["--targeting", json.dumps(adset["targeting"], ensure_ascii=False)]
    elif get("targeting_countries"):
        args += ["--targeting-countries", str(get("targeting_countries"))]
    advantage = get("advantage_audience")
    if advantage is True:
        args += ["--advantage-audience"]
    elif advantage is False:
        args += ["--no-advantage-audience"]
    if adset.get("dynamic_creative"):
        args += ["--dynamic-creative"]
    for flag, key in (("--destination-type", "destination_type"), ("--start-time", "start_time"),
                      ("--end-time", "end_time"), ("--pacing-type", "pacing_type"),
                      ("--dsa-beneficiary", "dsa_beneficiary"), ("--dsa-payor", "dsa_payor")):
        if get(key):
            args += [flag, str(get(key))]
    return args


def creative_args(plan: dict, ad: dict) -> list[str]:
    d = plan["defaults"]
    args = ["ads", "creative", "create", "--name", f"CR | {ad['ad_name']}",
            "--page-id", str(d["page_id"]), "--body", ad["body"],
            "--link-url", ad["link_url"], "--call-to-action", ad["cta"]]
    args += ["--video" if ad["media_kind"] == "video" else "--image", ad["media"]]
    if ad.get("title"):
        args += ["--title", ad["title"]]
    if ad.get("description"):
        args += ["--description", ad["description"]]
    if ad.get("url_tags"):
        args += ["--url-tags", ad["url_tags"]]
    if d.get("instagram_user_id"):
        args += ["--instagram-user-id", str(d["instagram_user_id"])]
    if d.get("stage_creatives_paused", True):
        args += ["--status", "PAUSED"]
    return args


def ad_args(plan: dict, ad: dict, adset_id: str, creative_id: str) -> list[str]:
    d = plan["defaults"]
    args = ["ads", "ad", "create", adset_id, "--name", ad["ad_name"],
            "--creative-id", creative_id, "--status", "PAUSED"]
    if d.get("pixel_id"):
        args += ["--pixel-id", str(d["pixel_id"])]
    if ad.get("conversion_domain"):
        args += ["--conversion-domain", ad["conversion_domain"]]
    return args


# --------------------------------------------------------------------------- state
def state_path(run_id: str) -> Path:
    return STATE_DIR / f"{run_id}.json"


def save_state(state: dict) -> None:
    if state.get("_dry_run"):
        return
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    path = state_path(state["run_id"])
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    (STATE_DIR / "latest.json").write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def load_state(run_id: str | None) -> dict:
    path = state_path(run_id) if run_id else STATE_DIR / "latest.json"
    if not path.exists():
        die(f"Khong thay state file {path}. Chay 'launch' truoc da.")
    return json.loads(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- cac lenh
def cmd_validate(args, config, rows, env) -> int:
    plan = build_plan(config, rows, env)
    info(f"Campaign: {plan['campaign'].get('name')} | {plan['objective']} | {plan['budget_mode']}")
    info(f"Ad set: {len(plan['adsets'])} | Ad: {len(plan['ads'])}")
    for w in plan["warnings"]:
        warn(w)
    for e in plan["errors"]:
        fail(e)
    if plan["errors"]:
        print(f"\n{C_RED}Co {len(plan['errors'])} loi, chua goi API.{C_RST}")
        return 1
    ok(f"Ke hoach hop le ({len(plan['warnings'])} canh bao). Xem lenh se chay: plan")
    return 0


def cmd_plan(args, config, rows, env) -> int:
    plan = build_plan(config, rows, env)
    for e in plan["errors"]:
        fail(e)
    if plan["errors"]:
        return 1
    cli = MetaCLI(env, dry_run=True)
    info("Cac lenh se duoc chay (dry-run, khong goi API):")
    print(f"  {C_DIM}$ {cli.shell(campaign_args(plan))}{C_RST}")
    for adset in plan["adsets"]:
        print(f"  {C_DIM}$ {cli.shell(adset_args(plan, adset, '<CAMPAIGN_ID>'))}{C_RST}")
    for ad in plan["ads"]:
        print(f"  {C_DIM}$ {cli.shell(creative_args(plan, ad))}{C_RST}")
        print(f"  {C_DIM}$ {cli.shell(ad_args(plan, ad, '<ADSET_ID>', '<CREATIVE_ID>'))}{C_RST}")
    print()
    info("URL cuoi cung sau khi gan UTM:")
    for ad in plan["ads"]:
        print(f"  {ad['ad_name']}: {ad['final_url']}")
    return 0


def cmd_launch(args, config, rows, env) -> int:
    plan = build_plan(config, rows, env)
    for w in plan["warnings"]:
        warn(w)
    for e in plan["errors"]:
        fail(e)
    if plan["errors"]:
        return die("Ke hoach con loi, dung lai truoc khi goi API.", 1)

    cli = MetaCLI(env, dry_run=args.dry_run)
    if args.resume:
        state = load_state(args.run_id)
        info(f"Tiep tuc run {state['run_id']}")
    else:
        run_id = args.run_id or f"{slugify(plan['campaign']['name'])}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        state = {"run_id": run_id, "created_at": datetime.now(timezone.utc).isoformat(),
                 "ad_account_id": env.get("AD_ACCOUNT_ID", ""), "campaign": {}, "adsets": [], "ads": [],
                 "_dry_run": args.dry_run}

    # 1. Campaign ----------------------------------------------------------
    if not state["campaign"].get("id"):
        info(f"Tao campaign (PAUSED): {plan['campaign']['name']}")
        result = cli.run(campaign_args(plan))
        campaign_id = first_id(result)
        if not campaign_id:
            return die(f"Khong lay duoc campaign id tu ket qua: {result}")
        state["campaign"] = {"id": campaign_id, "name": plan["campaign"]["name"], "status": "PAUSED"}
        save_state(state)
        ok(f"campaign_id={campaign_id}")

    # 2. Ad sets -----------------------------------------------------------
    existing = {a["name"]: a for a in state["adsets"]}
    for adset in plan["adsets"]:
        if adset["name"] in existing:
            ok(f"Ad set da co: {adset['name']} ({existing[adset['name']]['id']})")
            continue
        info(f"Tao ad set (PAUSED): {adset['name']}")
        result = cli.run(adset_args(plan, adset, state["campaign"]["id"]))
        adset_id = first_id(result)
        if not adset_id:
            save_state(state)
            return die(f"Khong lay duoc adset id: {result}")
        state["adsets"].append({"name": adset["name"], "id": adset_id, "status": "PAUSED"})
        existing[adset["name"]] = state["adsets"][-1]
        save_state(state)
        ok(f"adset_id={adset_id}")

    # 3. Creative + ad -----------------------------------------------------
    done_ads = {a["ad_name"]: a for a in state["ads"]}
    for ad in plan["ads"]:
        if ad["ad_name"] in done_ads and done_ads[ad["ad_name"]].get("ad_id"):
            ok(f"Ad da co: {ad['ad_name']} ({done_ads[ad['ad_name']]['ad_id']})")
            continue
        entry = done_ads.get(ad["ad_name"], {"ad_name": ad["ad_name"], "adset": ad["adset"]})
        if not entry.get("creative_id"):
            info(f"Upload {ad['media_kind']} + tao creative: {ad['ad_name']}")
            result = cli.run(creative_args(plan, ad))
            creative_id = first_id(result)
            if not creative_id:
                save_state(state)
                return die(f"Khong lay duoc creative id: {result}")
            entry["creative_id"] = creative_id
        adset_id = existing[ad["adset"]]["id"]
        info(f"Tao ad (PAUSED): {ad['ad_name']}")
        result = cli.run(ad_args(plan, ad, adset_id, entry["creative_id"]))
        ad_id = first_id(result)
        if not ad_id:
            save_state(state)
            return die(f"Khong lay duoc ad id: {result}")
        entry.update({"ad_id": ad_id, "adset_id": adset_id, "link_url": ad["link_url"],
                      "url_tags": ad["url_tags"], "final_url": ad["final_url"],
                      "conversion_domain": ad.get("conversion_domain", ""), "status": "PAUSED"})
        if ad["ad_name"] in done_ads:
            for i, a in enumerate(state["ads"]):
                if a["ad_name"] == ad["ad_name"]:
                    state["ads"][i] = entry
        else:
            state["ads"].append(entry)
            done_ads[ad["ad_name"]] = entry
        save_state(state)
        ok(f"ad_id={ad_id}")

    if args.dry_run:
        info("Dry-run xong, khong co gi duoc tao that.")
        return 0
    print()
    ok(f"Da tao xong, TAT CA dang PAUSED. State: ads/state/{state['run_id']}.json")
    info("Buoc tiep: python3 scripts/meta_ads_launch.py verify && ... preview")
    return 0


def unwrap(res):
    """Tach (data, error) tu ket qua CLI, chap nhan ca dang {...} lan {"data": {...}}."""
    if not isinstance(res, dict):
        return {}, "ket qua khong doc duoc"
    if res.get("_error"):
        return {}, redact(str(res["_error"]).strip().splitlines()[-1])[:200]
    data = res.get("data", res)
    if isinstance(data, list):
        data = data[0] if data else {}
    return (data if isinstance(data, dict) else {}), ""


def http_check(url: str, timeout: int = 20) -> dict:
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
        "Accept": "text/html,application/xhtml+xml",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(400_000).decode("utf-8", "replace")
            return {"status": resp.status, "final_url": resp.geturl(), "body": body}
    except urllib.error.HTTPError as exc:
        return {"status": exc.code, "final_url": url, "body": "", "error": f"HTTP {exc.code}"}
    except Exception as exc:  # noqa: BLE001
        return {"status": 0, "final_url": url, "body": "", "error": str(exc)}


def cmd_verify(args, config, rows, env) -> int:
    state = load_state(args.run_id)
    cli = MetaCLI(env)
    defaults = (config.get("defaults") or {})
    pixel_id = str(defaults.get("pixel_id") or "")
    problems, notes = [], []
    lines = [f"# Bao cao kiem tra — {state['run_id']}", "", f"Thoi diem: {datetime.now().isoformat(timespec='seconds')}", ""]

    info("1/4 Kiem tra trang thai (phai la PAUSED)")
    camp = cli.run(["ads", "campaign", "get", state["campaign"]["id"], "--fields",
                    "name,status,effective_status,objective,daily_budget,lifetime_budget,special_ad_categories"], allow_fail=True)
    camp_data, camp_err = unwrap(camp)
    if camp_err:
        problems.append(f"Khong doc duoc campaign {state['campaign']['id']}: {camp_err}")
    camp_status = str(camp_data.get("effective_status") or camp_data.get("status") or "?")
    (ok if camp_status != "ACTIVE" else fail)(f"Campaign {state['campaign']['id']}: {camp_status}")
    if camp_status == "ACTIVE":
        problems.append("Campaign dang ACTIVE (dang le phai PAUSED)")
    lines += [f"- Campaign `{state['campaign']['id']}` — {camp_data.get('name','')} — **{camp_status}**"]

    for adset in state["adsets"]:
        res = cli.run(["ads", "adset", "get", adset["id"], "--fields",
                       "name,status,effective_status,daily_budget,optimization_goal,billing_event,promoted_object,targeting"], allow_fail=True)
        data, err = unwrap(res)
        if err:
            problems.append(f"Khong doc duoc ad set '{adset['name']}': {err}")
        status = str(data.get("effective_status") or data.get("status") or "?")
        (ok if status != "ACTIVE" else fail)(f"Ad set {adset['name']}: {status}")
        if status == "ACTIVE":
            problems.append(f"Ad set '{adset['name']}' dang ACTIVE")
        promoted = data.get("promoted_object") or {}
        if pixel_id and str(promoted.get("pixel_id", "")) != pixel_id:
            notes.append(f"Ad set '{adset['name']}' chua gan pixel {pixel_id} (promoted_object={promoted})")
        lines.append(f"- Ad set `{adset['id']}` — {adset['name']} — **{status}** — promoted_object: `{promoted}`")

    info("2/4 Kiem tra ad + creative + tracking")
    for ad in state["ads"]:
        res = cli.run(["ads", "ad", "get", ad["ad_id"], "--fields",
                       "name,status,effective_status,creative,tracking_specs,conversion_domain"], allow_fail=True)
        data, err = unwrap(res)
        if err:
            problems.append(f"Khong doc duoc ad '{ad['ad_name']}': {err}")
        status = str(data.get("effective_status") or data.get("status") or "?")
        (ok if status != "ACTIVE" else fail)(f"Ad {ad['ad_name']}: {status}")
        if status == "ACTIVE":
            problems.append(f"Ad '{ad['ad_name']}' dang ACTIVE")
        tracking = data.get("tracking_specs") or []
        if pixel_id and pixel_id not in json.dumps(tracking):
            notes.append(f"Ad '{ad['ad_name']}': tracking_specs chua thay pixel {pixel_id} -> {tracking}")
        if ad.get("conversion_domain") and data.get("conversion_domain") and \
                data["conversion_domain"] != ad["conversion_domain"]:
            problems.append(f"Ad '{ad['ad_name']}': conversion_domain lech ({data['conversion_domain']})")
        # Doi chieu link/url_tags that su nam tren creative
        creative_id = ad.get("creative_id", "")
        if creative_id and cli.token:
            cdata = graph_get(creative_id, {"fields": "object_story_spec,url_tags,asset_feed_spec"}, cli.token)
            if "_error" not in cdata:
                live_tags = cdata.get("url_tags", "")
                if (live_tags or "") != (ad.get("url_tags") or ""):
                    problems.append(f"Ad '{ad['ad_name']}': url_tags tren Meta ('{live_tags}') khac ke hoach ('{ad.get('url_tags')}')")
                spec = json.dumps(cdata.get("object_story_spec") or {}, ensure_ascii=False)
                if ad.get("link_url") and ad["link_url"] not in spec:
                    problems.append(f"Ad '{ad['ad_name']}': link_url khong khop voi creative tren Meta")
        lines.append(f"- Ad `{ad['ad_id']}` — {ad['ad_name']} — **{status}** — creative `{creative_id}`")

    info("3/4 Kiem tra URL dich + UTM + pixel tren landing page")
    lines += ["", "## URL & tracking", ""]
    for ad in state["ads"]:
        url = ad.get("final_url") or ad.get("link_url", "")
        result = http_check(url)
        status_code = result.get("status", 0)
        if status_code and 200 <= status_code < 400:
            ok(f"{ad['ad_name']}: HTTP {status_code} -> {result['final_url'][:100]}")
        else:
            fail(f"{ad['ad_name']}: khong mo duoc URL ({result.get('error') or status_code}) {url}")
            problems.append(f"Ad '{ad['ad_name']}': URL loi ({result.get('error') or status_code})")
        query = urllib.parse.parse_qs(urllib.parse.urlparse(result.get("final_url", url)).query)
        missing = [k for k in ("utm_source", "utm_medium", "utm_campaign") if k not in query]
        if missing:
            warn(f"{ad['ad_name']}: URL cuoi thieu {', '.join(missing)} (co the do redirect cat query)")
            notes.append(f"Ad '{ad['ad_name']}': thieu {', '.join(missing)} sau redirect")
        body = result.get("body", "")
        has_pixel = "fbq(" in body or "connect.facebook.net" in body
        pixel_match = bool(pixel_id) and pixel_id in body
        if has_pixel and (pixel_match or not pixel_id):
            ok(f"{ad['ad_name']}: thay Meta Pixel tren landing page")
        elif has_pixel:
            warn(f"{ad['ad_name']}: co pixel nhung khong thay id {pixel_id} trong HTML (co the nap dong)")
            notes.append(f"Ad '{ad['ad_name']}': khong thay pixel id {pixel_id} trong HTML tinh")
        else:
            warn(f"{ad['ad_name']}: khong thay Meta Pixel trong HTML (kiem tra lai bang Meta Pixel Helper)")
            notes.append(f"Ad '{ad['ad_name']}': khong tim thay doan pixel trong HTML")
        lines.append(f"- **{ad['ad_name']}** — HTTP {status_code} — `{url}`")
        lines.append(f"  - URL sau redirect: `{result.get('final_url','')}`")
        lines.append(f"  - Pixel tren trang: {'co' if has_pixel else 'khong thay'}")

    info("4/4 Tong hop")
    lines += ["", "## Ket luan", ""]
    for p in problems:
        lines.append(f"- [x] LOI: {p}")
    for n in notes:
        lines.append(f"- [ ] Luu y: {n}")
    if not problems and not notes:
        lines.append("- Khong phat hien van de.")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = OUT_DIR / f"verify-{state['run_id']}.md"
    report.write_text(redact("\n".join(lines) + "\n"), encoding="utf-8")

    print()
    for n in notes:
        warn(n)
    for p in problems:
        fail(p)
    if problems:
        print(f"\n{C_RED}Co {len(problems)} van de can sua truoc khi bat chay.{C_RST} Bao cao: {report}")
        return 1
    ok(f"Moi thu on. Bao cao: {report}")
    return 0


def cmd_preview(args, config, rows, env) -> int:
    state = load_state(args.run_id)
    cli = MetaCLI(env)
    if not cli.token:
        return die("Thieu ACCESS_TOKEN de goi API preview")
    formats = args.formats.split(",") if args.formats else \
        (config.get("defaults", {}).get("preview_formats") or DEFAULT_PREVIEW_FORMATS)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    blocks = []
    success = 0
    for ad in state["ads"]:
        info(f"Preview: {ad['ad_name']}")
        frames = []
        for fmt in formats:
            data = graph_get(f"{ad['ad_id']}/previews", {"ad_format": fmt.strip()}, cli.token)
            if "_error" in data:
                warn(f"  {fmt}: {data['_error'][:140]}")
                continue
            items = data.get("data") or []
            if not items:
                warn(f"  {fmt}: khong co preview tra ve")
                continue
            ok(f"  {fmt}")
            success += 1
            frames.append(f"<div class='fmt'><h4>{fmt}</h4>{items[0].get('body','')}</div>")
        blocks.append(
            "<section><h2>{name}</h2>"
            "<p class='meta'>ad_id <code>{ad_id}</code> · ad set <code>{adset}</code> · trang thai <b>PAUSED</b></p>"
            "<p class='meta'>URL: <a href='{url}' target='_blank'>{url}</a></p>"
            "<div class='frames'>{frames}</div></section>".format(
                name=ad["ad_name"], ad_id=ad["ad_id"], adset=ad.get("adset", ""),
                url=ad.get("final_url", ""), frames="".join(frames) or "<p class='err'>Khong lay duoc preview</p>")
        )
    html = """<!doctype html><meta charset="utf-8"><title>Preview {run}</title>
<style>body{{font:14px/1.5 system-ui,sans-serif;margin:24px;background:#fafafa;color:#111}}
section{{background:#fff;border:1px solid #e3e3e3;border-radius:10px;padding:16px;margin-bottom:20px}}
h1{{font-size:20px}} h2{{font-size:16px;margin:0 0 6px}} h4{{font-size:12px;color:#666;margin:0 0 6px}}
.meta{{color:#555;font-size:12px;margin:2px 0}} .frames{{display:flex;flex-wrap:wrap;gap:16px;margin-top:10px}}
.fmt{{border:1px solid #eee;border-radius:8px;padding:8px}} .err{{color:#b00}}
iframe{{border:0;max-width:100%}}</style>
<h1>Preview — {run}</h1>
<p>Mo file nay trong trinh duyet <b>dang dang nhap Facebook</b> (tai khoan co quyen tren ad account) thi iframe moi hien.</p>
{body}""".format(run=state["run_id"], body="".join(blocks))
    out = OUT_DIR / f"previews-{state['run_id']}.html"
    out.write_text(html, encoding="utf-8")
    ok(f"Da xuat: {out}")
    info("Mo bang trinh duyet dang dang nhap Facebook de xem preview that.")
    if success == 0:
        fail("Khong lay duoc preview nao (kiem tra token/quyen hoac ad_format).")
        return 1
    return 0


def cmd_status(args, config, rows, env) -> int:
    state = load_state(args.run_id)
    cli = MetaCLI(env)
    rowsout = []
    camp = cli.run(["ads", "campaign", "get", state["campaign"]["id"], "--fields", "name,effective_status"], allow_fail=True)
    cdata, cerr = unwrap(camp)
    rowsout.append(("CAMPAIGN", state["campaign"]["id"], cdata.get("name", state["campaign"]["name"]),
                    "ERR" if cerr else str(cdata.get("effective_status", "?"))))
    for adset in state["adsets"]:
        res = cli.run(["ads", "adset", "get", adset["id"], "--fields", "name,effective_status"], allow_fail=True)
        data, err = unwrap(res)
        rowsout.append(("ADSET", adset["id"], adset["name"], "ERR" if err else str(data.get("effective_status", "?"))))
    for ad in state["ads"]:
        res = cli.run(["ads", "ad", "get", ad["ad_id"], "--fields", "name,effective_status"], allow_fail=True)
        data, err = unwrap(res)
        rowsout.append(("AD", ad["ad_id"], ad["ad_name"], "ERR" if err else str(data.get("effective_status", "?"))))
    width = max(len(r[2]) for r in rowsout) + 2
    print(f"\n{'LEVEL':<10}{'ID':<20}{'NAME':<{width}}STATUS")
    for level, oid, name, status in rowsout:
        color = C_GRN if status == "ACTIVE" else (C_YEL if status == "PAUSED" else C_RED)
        print(f"{level:<10}{oid:<20}{name:<{width}}{color}{status}{C_RST}")
    return 0


def set_status(cli: MetaCLI, state: dict, status: str, only: str | None = None) -> list[str]:
    errors = []
    targets = []
    if only in (None, "ads", "all"):
        targets += [("ad", a["ad_id"], a["ad_name"]) for a in state["ads"]]
    if only in (None, "adsets", "all"):
        targets += [("adset", a["id"], a["name"]) for a in state["adsets"]]
    if only in (None, "campaign", "all"):
        targets += [("campaign", state["campaign"]["id"], state["campaign"]["name"])]
    # Bat: ad -> ad set -> campaign; Tat: lam nguoc lai cho an toan
    if status == "PAUSED":
        targets = list(reversed(targets))
    for level, oid, name in targets:
        res = cli.run(["ads", level, "update", oid, "--status", status], allow_fail=True)
        if isinstance(res, dict) and res.get("_error"):
            fail(f"{level} {name}: {res['_error'][:160]}")
            errors.append(f"{level} {name}")
        else:
            ok(f"{level} {name} -> {status}")
    return errors


def cmd_activate(args, config, rows, env) -> int:
    state = load_state(args.run_id)
    if not args.yes:
        return die("Can --yes de xac nhan bat chay that (tien se bat dau tieu).")
    if not args.skip_verify:
        info("Chay verify truoc khi bat...")
        if cmd_verify(args, config, rows, env) != 0:
            return die("Verify that bai. Sua xong roi chay lai, hoac them --skip-verify neu ban chap nhan.")
    cli = MetaCLI(env, dry_run=args.dry_run)
    info(f"Bat chay {state['run_id']}")
    errors = set_status(cli, state, "ACTIVE")
    if errors:
        return die(f"Co {len(errors)} doi tuong khong bat duoc, xem log ben tren.")
    if not args.dry_run:
        time.sleep(3)
        info("Kiem tra lai trang thai thuc te:")
        cmd_status(args, config, rows, env)
        info("Neu ad bao WITH_ISSUES / PENDING_REVIEW thi la Meta dang duyet, doi la binh thuong.")
    return 0


def cmd_pause(args, config, rows, env) -> int:
    state = load_state(args.run_id)
    cli = MetaCLI(env, dry_run=args.dry_run)
    info(f"Tat toan bo {state['run_id']}")
    errors = set_status(cli, state, "PAUSED")
    return 1 if errors else 0


# --------------------------------------------------------------------------- main
def main() -> int:
    parser = argparse.ArgumentParser(description="Chay quang cao Meta tu file ke hoach, dung Meta Ads CLI chinh chu")
    parser.add_argument("command", choices=["validate", "plan", "launch", "verify", "preview", "status", "activate", "pause"])
    parser.add_argument("--config", default=str(ADS_DIR / "campaign.yaml"), help="File cau hinh campaign (.yaml hoac .json)")
    parser.add_argument("--csv", default=str(ADS_DIR / "plan.csv"), help="Bang creative/copy/URL/UTM")
    parser.add_argument("--env-file", default=str(ADS_DIR / ".env"))
    parser.add_argument("--run-id", default=None, help="Dinh danh lan chay (mac dinh: lan chay gan nhat)")
    parser.add_argument("--resume", action="store_true", help="Chay tiep lan launch bi dut giua chung")
    parser.add_argument("--dry-run", action="store_true", help="Chi in lenh, khong goi API")
    parser.add_argument("--yes", action="store_true", help="Xac nhan cho activate")
    parser.add_argument("--skip-verify", action="store_true", help="Bo qua verify khi activate")
    parser.add_argument("--formats", default=None, help="Danh sach ad_format cho preview, cach nhau bang dau phay")
    args = parser.parse_args()

    env_file = Path(args.env_file)
    env = load_dotenv(env_file)
    for key in ("ACCESS_TOKEN", "AD_ACCOUNT_ID", "BUSINESS_ID"):
        if os.environ.get(key):
            env[key] = os.environ[key]

    if env.get("ACCESS_TOKEN"):
        _SECRETS.add(env["ACCESS_TOKEN"])

    config_path = Path(args.config)
    csv_path = Path(args.csv)
    needs_plan = args.command in {"validate", "plan", "launch"}
    config = load_config(config_path, env) if config_path.exists() else {}
    if not config and needs_plan:
        die(f"Khong tim thay {config_path}")
    rows = read_rows(csv_path) if needs_plan else []

    handlers = {
        "validate": cmd_validate, "plan": cmd_plan, "launch": cmd_launch, "verify": cmd_verify,
        "preview": cmd_preview, "status": cmd_status, "activate": cmd_activate, "pause": cmd_pause,
    }
    try:
        return handlers[args.command](args, config, rows, env)
    except RuntimeError as exc:
        return die(str(exc))
    except KeyboardInterrupt:
        return die("Da dung theo yeu cau (Ctrl-C)", 130)


if __name__ == "__main__":
    sys.exit(main())

"""Tiện ích dùng chung: ghi CSV chuẩn hóa + gọi Apify actor."""

from __future__ import annotations

import csv
import os
import time
from pathlib import Path

import requests

# Schema chuẩn hóa — mọi nguồn đều ghi về các cột này để bước phân tích
# gộp lại dễ dàng.
FIELDNAMES = [
    "source",        # reddit | quora | amazon
    "type",          # post | comment | question | answer | product | review
    "keyword",       # từ khóa dẫn tới bản ghi này
    "title",
    "text",
    "score",         # upvote / rating (sao)
    "num_comments",  # số comment / số review
    "author",
    "date",
    "url",
    "extra",         # ASIN, subreddit, verified purchase...
]

DATA_DIR = Path(__file__).parent / "data"


def write_rows(filename: str, rows: list[dict]) -> Path:
    """Ghi list dict về file CSV trong data/, trả về đường dẫn."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            # Làm sạch text: bỏ xuống dòng thừa để CSV gọn
            if row.get("text"):
                row["text"] = " ".join(str(row["text"]).split())
            writer.writerow(row)
    print(f"  -> Đã ghi {len(rows)} dòng vào {path}")
    return path


# ---------------------------------------------------------------------------
# Apify helpers
# ---------------------------------------------------------------------------
APIFY_BASE = "https://api.apify.com/v2"


def apify_token() -> str:
    token = os.environ.get("APIFY_TOKEN", "").strip()
    if not token:
        raise SystemExit(
            "Thiếu APIFY_TOKEN. Đăng ký free tại https://apify.com, "
            "lấy token ở Settings -> Integrations, rồi:\n"
            "  export APIFY_TOKEN=apify_api_xxx"
        )
    return token


def run_apify_actor(actor_id: str, run_input: dict, timeout_s: int = 900) -> list[dict]:
    """Chạy một Apify actor đồng bộ và trả về dataset items.

    actor_id dạng "username~actor-name" (dấu ~ thay cho /).
    """
    token = apify_token()
    url = f"{APIFY_BASE}/acts/{actor_id}/runs?token={token}"
    resp = requests.post(url, json=run_input, timeout=60)
    resp.raise_for_status()
    run = resp.json()["data"]
    run_id = run["id"]
    print(f"  Apify run {run_id} ({actor_id}) đã khởi động, chờ hoàn thành...")

    started = time.time()
    while True:
        status_resp = requests.get(
            f"{APIFY_BASE}/actor-runs/{run_id}?token={token}", timeout=60
        )
        status_resp.raise_for_status()
        data = status_resp.json()["data"]
        status = data["status"]
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            break
        if time.time() - started > timeout_s:
            raise TimeoutError(f"Apify run {run_id} quá {timeout_s}s chưa xong")
        time.sleep(10)

    if status != "SUCCEEDED":
        raise RuntimeError(f"Apify run {run_id} kết thúc với status={status}")

    dataset_id = data["defaultDatasetId"]
    items: list[dict] = []
    offset = 0
    while True:
        page = requests.get(
            f"{APIFY_BASE}/datasets/{dataset_id}/items"
            f"?token={token}&format=json&offset={offset}&limit=1000",
            timeout=120,
        )
        page.raise_for_status()
        batch = page.json()
        if not batch:
            break
        items.extend(batch)
        offset += len(batch)
    print(f"  Apify trả về {len(items)} items")
    return items

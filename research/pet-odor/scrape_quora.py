"""Cào Quora qua Apify (Quora không có API chính thức).

Setup:
  export APIFY_TOKEN=apify_api_xxx   # https://apify.com -> Settings -> Integrations

Chạy:
  python scrape_quora.py

Cách hoạt động:
  Dùng Google search scraper của Apify với query `site:quora.com "<keyword>"`
  để tìm URL câu hỏi liên quan nhất, sau đó chạy Quora scraper actor để lấy
  nội dung câu hỏi + câu trả lời + upvote.

Lưu ý: tên actor trên Apify Store có thể thay đổi. Nếu actor bên dưới không
còn tồn tại, mở https://apify.com/store?search=quora và thay QUORA_ACTOR.

Output: data/quora.csv
"""

from __future__ import annotations

import config
from common import run_apify_actor, write_rows

# Actor Google SERP chính chủ của Apify
GOOGLE_ACTOR = "apify~google-search-scraper"
# Actor Quora phổ biến trên Apify Store — kiểm tra lại nếu lỗi 404
QUORA_ACTOR = "curious_coder~quora-scraper"


def find_quora_urls() -> dict[str, list[str]]:
    """Trả về {keyword: [quora urls]} bằng Google SERP."""
    queries = "\n".join(f'site:quora.com "{kw}"' for kw in config.KEYWORDS)
    items = run_apify_actor(GOOGLE_ACTOR, {
        "queries": queries,
        "resultsPerPage": config.QUORA_RESULTS_PER_KEYWORD,
        "maxPagesPerQuery": 1,
        "countryCode": "us",
        "languageCode": "en",
    })
    by_keyword: dict[str, list[str]] = {}
    for item in items:
        query = item.get("searchQuery", {}).get("term", "")
        kw = query.replace("site:quora.com", "").strip().strip('"')
        urls = [
            r.get("url", "")
            for r in item.get("organicResults", [])
            if "quora.com" in r.get("url", "")
        ]
        by_keyword.setdefault(kw, []).extend(urls)
    return by_keyword


def scrape_questions(urls_by_kw: dict[str, list[str]]) -> list[dict]:
    all_urls: list[str] = []
    url_to_kw: dict[str, str] = {}
    for kw, urls in urls_by_kw.items():
        for u in urls:
            u = u.split("?")[0]
            if u not in url_to_kw:
                url_to_kw[u] = kw
                all_urls.append(u)

    if not all_urls:
        print("Không tìm thấy URL Quora nào — kiểm tra lại keywords.")
        return []

    print(f"[quora] Cào {len(all_urls)} trang câu hỏi...")
    items = run_apify_actor(QUORA_ACTOR, {
        "startUrls": [{"url": u} for u in all_urls],
        "maxAnswers": 10,
        "proxyConfiguration": {"useApifyProxy": True},
    })

    rows: list[dict] = []
    for item in items:
        url = (item.get("url") or item.get("questionUrl") or "").split("?")[0]
        kw = url_to_kw.get(url, "")
        question = item.get("question") or item.get("title") or ""
        # Bản ghi câu hỏi
        rows.append({
            "source": "quora",
            "type": "question",
            "keyword": kw,
            "title": question,
            "text": item.get("questionDetails", "") or "",
            "score": item.get("followers", "") or "",
            "num_comments": item.get("answersCount", "") or "",
            "author": "",
            "date": "",
            "url": url,
            "extra": "",
        })
        # Các câu trả lời
        answers = item.get("answers") or []
        if isinstance(answers, dict):
            answers = [answers]
        for ans in answers:
            text = ans.get("text") or ans.get("content") or ""
            if len(text) < 40:
                continue
            rows.append({
                "source": "quora",
                "type": "answer",
                "keyword": kw,
                "title": question,
                "text": text,
                "score": ans.get("upvotes", "") or ans.get("numUpvotes", "") or "",
                "num_comments": "",
                "author": ans.get("author", "") or ans.get("authorName", "") or "",
                "date": ans.get("date", "") or "",
                "url": url,
                "extra": "",
            })
    return rows


if __name__ == "__main__":
    urls_by_kw = find_quora_urls()
    total = sum(len(v) for v in urls_by_kw.values())
    print(f"[quora] Tìm được {total} URL từ Google")
    rows = scrape_questions(urls_by_kw)
    write_rows("quora.csv", rows)

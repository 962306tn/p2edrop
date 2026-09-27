"""Cào Reddit bằng API chính thức (PRAW).

Setup:
  1. Vào https://www.reddit.com/prefs/apps -> "create another app" -> chọn "script".
  2. Lấy client_id (dòng dưới tên app) và secret.
  3. export REDDIT_CLIENT_ID=xxx REDDIT_CLIENT_SECRET=yyy REDDIT_USERNAME=zzz

Chạy:
  python scrape_reddit.py

Output: data/reddit.csv (post + top comment, schema chuẩn hóa).
"""

from __future__ import annotations

import datetime as dt
import os
import time

import praw
from prawcore.exceptions import PrawcoreException

import config
from common import write_rows


def make_reddit() -> praw.Reddit:
    client_id = os.environ.get("REDDIT_CLIENT_ID", "").strip()
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "").strip()
    username = os.environ.get("REDDIT_USERNAME", "research-bot").strip()
    if not client_id or not client_secret:
        raise SystemExit(
            "Thiếu REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET.\n"
            "Tạo app 'script' tại https://www.reddit.com/prefs/apps rồi export 2 biến này."
        )
    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=f"pet-odor-research/1.0 by u/{username}",
    )


def fmt_date(ts: float) -> str:
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%d")


def collect() -> list[dict]:
    reddit = make_reddit()
    rows: list[dict] = []
    seen_posts: set[str] = set()

    # 1) Search theo keyword trong từng subreddit
    for sub_name in config.SUBREDDITS:
        subreddit = reddit.subreddit(sub_name)
        for kw in config.KEYWORDS:
            print(f"[reddit] r/{sub_name} :: '{kw}'")
            try:
                results = subreddit.search(
                    kw,
                    sort="relevance",
                    time_filter=config.REDDIT_TIME_FILTER,
                    limit=config.REDDIT_POSTS_PER_QUERY,
                )
                for post in results:
                    if post.id in seen_posts:
                        continue
                    seen_posts.add(post.id)
                    rows.append({
                        "source": "reddit",
                        "type": "post",
                        "keyword": kw,
                        "title": post.title,
                        "text": post.selftext or "",
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "author": str(post.author) if post.author else "[deleted]",
                        "date": fmt_date(post.created_utc),
                        "url": f"https://reddit.com{post.permalink}",
                        "extra": f"subreddit=r/{sub_name}",
                    })
                    # Lấy top comments — đây là nơi chứa insight thật
                    try:
                        post.comment_sort = "top"
                        post.comments.replace_more(limit=0)
                        for c in post.comments[: config.REDDIT_COMMENTS_PER_POST]:
                            body = getattr(c, "body", "") or ""
                            if len(body) < 30:  # bỏ comment quá ngắn
                                continue
                            rows.append({
                                "source": "reddit",
                                "type": "comment",
                                "keyword": kw,
                                "title": post.title,
                                "text": body,
                                "score": c.score,
                                "num_comments": "",
                                "author": str(c.author) if c.author else "[deleted]",
                                "date": fmt_date(c.created_utc),
                                "url": f"https://reddit.com{post.permalink}{c.id}/",
                                "extra": f"subreddit=r/{sub_name}",
                            })
                    except PrawcoreException as e:
                        print(f"  ! lỗi lấy comment {post.id}: {e}")
                    time.sleep(0.5)  # lịch sự với rate limit
            except PrawcoreException as e:
                print(f"  ! lỗi search r/{sub_name} '{kw}': {e}")
                time.sleep(5)

    # 2) Search toàn Reddit cho các keyword đặc thù sản phẩm
    for kw in ["pet odor gun", "odor eliminator gun", "pet deodorizer machine"]:
        print(f"[reddit] site-wide :: '{kw}'")
        try:
            for post in reddit.subreddit("all").search(
                f'"{kw}"', sort="relevance", time_filter="all", limit=25
            ):
                if post.id in seen_posts:
                    continue
                seen_posts.add(post.id)
                rows.append({
                    "source": "reddit",
                    "type": "post",
                    "keyword": kw,
                    "title": post.title,
                    "text": post.selftext or "",
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "author": str(post.author) if post.author else "[deleted]",
                    "date": fmt_date(post.created_utc),
                    "url": f"https://reddit.com{post.permalink}",
                    "extra": f"subreddit=r/{post.subreddit.display_name}",
                })
        except PrawcoreException as e:
            print(f"  ! lỗi search site-wide '{kw}': {e}")

    return rows


if __name__ == "__main__":
    rows = collect()
    write_rows("reddit.csv", rows)

"""Cào Amazon (sản phẩm + review) qua Apify.

Setup:
  export APIFY_TOKEN=apify_api_xxx

Chạy:
  python scrape_amazon.py

Cách hoạt động:
  1. Nếu config.AMAZON_ASINS có ASIN -> cào review trực tiếp các ASIN đó.
  2. Nếu không -> search theo AMAZON_SEARCH_TERMS, lấy top sản phẩm mỗi term,
     rồi cào review của các sản phẩm đó.

Lưu ý: tên actor trên Apify Store có thể thay đổi. Nếu 404, mở
https://apify.com/store?search=amazon và thay ID actor tương ứng.
Thay thế tương đương: Rainforest API, Oxylabs, Unwrangle (đều trả JSON).

Output: data/amazon_products.csv + data/amazon_reviews.csv
"""

from __future__ import annotations

import config
from common import run_apify_actor, write_rows

# Actor phổ biến trên Apify Store — kiểm tra lại nếu lỗi 404
SEARCH_ACTOR = "junglee~free-amazon-product-scraper"
REVIEWS_ACTOR = "junglee~amazon-reviews-scraper"


def search_products() -> list[dict]:
    """Search Amazon theo keyword, trả về rows sản phẩm (kèm ASIN)."""
    urls = [
        {"url": f"https://www.{config.AMAZON_DOMAIN}/s?k={term.replace(' ', '+')}"}
        for term in config.AMAZON_SEARCH_TERMS
    ]
    print(f"[amazon] Search {len(urls)} từ khóa...")
    items = run_apify_actor(SEARCH_ACTOR, {
        "categoryOrProductUrls": urls,
        "maxItemsPerStartUrl": config.AMAZON_PRODUCTS_PER_TERM,
        "proxyCountry": "US",
    })

    rows: list[dict] = []
    for item in items:
        asin = item.get("asin", "")
        if not asin:
            continue
        rows.append({
            "source": "amazon",
            "type": "product",
            "keyword": item.get("searchTerm", "") or "",
            "title": item.get("title", ""),
            "text": " | ".join(item.get("features", []) or [])
                    or item.get("description", "") or "",
            "score": item.get("stars", "") or item.get("rating", "") or "",
            "num_comments": item.get("reviewsCount", "") or "",
            "author": item.get("brand", "") or "",
            "date": "",
            "url": item.get("url", "") or f"https://www.{config.AMAZON_DOMAIN}/dp/{asin}",
            "extra": f"asin={asin};price={item.get('price', {})}",
        })
    return rows


def scrape_reviews(asins: list[str]) -> list[dict]:
    if not asins:
        print("[amazon] Không có ASIN nào để cào review.")
        return []
    print(f"[amazon] Cào review cho {len(asins)} ASIN: {asins}")
    items = run_apify_actor(REVIEWS_ACTOR, {
        "productUrls": [
            {"url": f"https://www.{config.AMAZON_DOMAIN}/dp/{asin}"}
            for asin in asins
        ],
        "maxReviews": config.AMAZON_REVIEWS_PER_PRODUCT,
        # Ưu tiên review 1-3 sao (pain points) + 5 sao (lý do mua):
        # actor này lấy tất cả, mình lọc lúc phân tích.
        "sort": "recent",
        "proxyCountry": "US",
    }, timeout_s=1800)

    rows: list[dict] = []
    for item in items:
        text = item.get("reviewDescription", "") or item.get("text", "") or ""
        if len(text) < 20:
            continue
        rows.append({
            "source": "amazon",
            "type": "review",
            "keyword": "",
            "title": item.get("reviewTitle", "") or "",
            "text": text,
            "score": item.get("ratingScore", "") or item.get("rating", "") or "",
            "num_comments": item.get("helpfulCount", "") or "",
            "author": item.get("userProfileName", "") or "",
            "date": item.get("date", "") or "",
            "url": item.get("reviewUrl", "") or item.get("productUrl", "") or "",
            "extra": (
                f"asin={item.get('productAsin', item.get('asin', ''))};"
                f"verified={item.get('isVerified', '')}"
            ),
        })
    return rows


def extract_asins(product_rows: list[dict]) -> list[str]:
    asins: list[str] = []
    for row in product_rows:
        for part in row.get("extra", "").split(";"):
            if part.startswith("asin="):
                asin = part[len("asin="):]
                if asin and asin not in asins:
                    asins.append(asin)
    return asins


if __name__ == "__main__":
    if config.AMAZON_ASINS:
        asins = config.AMAZON_ASINS
        product_rows: list[dict] = []
    else:
        product_rows = search_products()
        write_rows("amazon_products.csv", product_rows)
        # Lấy tối đa 12 sản phẩm đầu để tiết kiệm credit
        asins = extract_asins(product_rows)[:12]

    review_rows = scrape_reviews(asins)
    write_rows("amazon_reviews.csv", review_rows)

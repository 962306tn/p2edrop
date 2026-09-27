# Pet Odor Research Pipeline

Pipeline cào dữ liệu Reddit + Quora + Amazon cho niche **pet / dog / pet odor gun**, sau đó dùng Claude phân tích thành báo cáo insight phục vụ viết content.

## Cấu trúc

```
research/pet-odor/
├── config.py            # Từ khóa, subreddit, ASIN — chỉnh ở đây
├── common.py            # Ghi CSV chuẩn hóa + gọi Apify
├── scrape_reddit.py     # Reddit qua API chính thức (PRAW) — miễn phí
├── scrape_quora.py      # Quora qua Apify (Google SERP → Quora scraper)
├── scrape_amazon.py     # Amazon products + reviews qua Apify
├── analyze_insights.py  # Gộp CSV → Claude → data/insight_report.md
├── requirements.txt
├── .env.example
└── data/                # Output CSV + báo cáo (gitignore)
```

## Setup

```bash
cd research/pet-odor
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Điền credentials (xem `.env.example`):

| Biến | Lấy ở đâu | Chi phí |
|---|---|---|
| `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` | [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) → create app → type **script** | Miễn phí |
| `APIFY_TOKEN` | [console.apify.com](https://console.apify.com/settings/integrations) | Free tier $5 credit/tháng |
| `ANTHROPIC_API_KEY` | [platform.claude.com](https://platform.claude.com) | Trả theo token |

```bash
export REDDIT_CLIENT_ID=xxx REDDIT_CLIENT_SECRET=yyy REDDIT_USERNAME=zzz
export APIFY_TOKEN=apify_api_xxx
export ANTHROPIC_API_KEY=sk-ant-xxx
```

## Chạy

```bash
python scrape_reddit.py     # → data/reddit.csv (chạy được ngay, miễn phí)
python scrape_quora.py      # → data/quora.csv
python scrape_amazon.py     # → data/amazon_products.csv + amazon_reviews.csv
python analyze_insights.py  # → data/insight_report.md
```

Có thể chạy `analyze_insights.py` với bất kỳ tập con dữ liệu nào — file CSV thiếu sẽ được bỏ qua. Ví dụ chỉ cần chạy Reddit trước là đã có báo cáo đầu tiên.

## Schema CSV chuẩn hóa

Mọi nguồn ghi về cùng các cột: `source, type, keyword, title, text, score, num_comments, author, date, url, extra` — để bước phân tích và mọi xử lý sau này (lọc, dedupe, pivot) dùng chung một format.

## Báo cáo insight gồm

1. Tổng quan dữ liệu
2. Pain points (theo tần suất, kèm trích dẫn nguyên văn)
3. Desires & dream outcome
4. Objections & trust issues
5. Giải pháp hiện tại & khoảng trống thị trường
6. Customer language bank (cụm từ nguyên văn để dùng trong copy)
7. 10 content angles + hooks (TOFU/MOFU/BOFU, tiếng Anh)
8. FAQ & objection handling

## Tùy chỉnh

- **Đổi từ khóa / subreddit / số lượng**: sửa `config.py`.
- **Đã biết ASIN đối thủ**: điền vào `AMAZON_ASINS` trong `config.py` để bỏ qua bước search và cào review trực tiếp.
- **Actor Apify đổi tên / 404**: mở [apify.com/store](https://apify.com/store) tìm actor thay thế (search "quora" hoặc "amazon reviews") và cập nhật hằng số `*_ACTOR` trong `scrape_quora.py` / `scrape_amazon.py`.

## Lưu ý pháp lý

- Reddit dùng API chính thức, tuân thủ rate limit — an toàn.
- Quora và Amazon cấm scraping trong ToS; đi qua Apify (bên thứ ba) để tránh rủi ro cho tài khoản cá nhân/seller của bạn. Chỉ dùng dữ liệu công khai, không thu thập thông tin cá nhân, không đăng lại nguyên văn nội dung — chỉ tổng hợp và trích ngắn khi phân tích.

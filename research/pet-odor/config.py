"""Cấu hình chung cho pipeline research niche: pet / dog / pet odor gun.

Chỉnh sửa file này trước khi chạy — thêm/bớt từ khóa, subreddit, ASIN.
"""

# ---------------------------------------------------------------------------
# Từ khóa chính (dùng cho Reddit search, Quora search, Amazon search)
# ---------------------------------------------------------------------------
KEYWORDS = [
    "pet odor eliminator",
    "pet odor gun",
    "odor eliminator gun",
    "deodorizer spray gun pet",
    "dog smell house",
    "dog odor remover",
    "pet smell out of carpet",
    "dog urine smell",
    "cat urine odor remover",
    "house smells like dog",
    "enzyme cleaner pet odor",
    "ozone generator pet smell",
]

# Từ khóa rút gọn cho Amazon (search term ngắn hoạt động tốt hơn)
AMAZON_SEARCH_TERMS = [
    "pet odor eliminator gun",
    "odor eliminator spray gun",
    "pet odor eliminator",
    "dog odor eliminator home",
    "pet deodorizer machine",
]

# ---------------------------------------------------------------------------
# Reddit
# ---------------------------------------------------------------------------
SUBREDDITS = [
    "dogs",
    "puppy101",
    "DogAdvice",
    "Pets",
    "CleaningTips",
    "cleaningadvice",
    "homeowners",
    "AskVet",
    "dogswithjobs",  # ít liên quan hơn, có thể bỏ
    "cats",          # cat urine là pain point lớn, giữ lại để so sánh
]

REDDIT_POSTS_PER_QUERY = 25       # số post mỗi (subreddit x keyword)
REDDIT_COMMENTS_PER_POST = 15     # số comment top lấy mỗi post
REDDIT_TIME_FILTER = "year"       # hour|day|week|month|year|all

# ---------------------------------------------------------------------------
# Quora (qua Apify)
# ---------------------------------------------------------------------------
QUORA_RESULTS_PER_KEYWORD = 20

# ---------------------------------------------------------------------------
# Amazon (qua Apify)
# ---------------------------------------------------------------------------
# Nếu đã biết ASIN đối thủ, điền vào đây để cào review trực tiếp.
# Để trống thì script sẽ tự search theo AMAZON_SEARCH_TERMS rồi lấy
# top sản phẩm để cào review.
AMAZON_ASINS: list[str] = [
    # "B0XXXXXXXX",
]
AMAZON_PRODUCTS_PER_TERM = 10     # số sản phẩm lấy mỗi search term
AMAZON_REVIEWS_PER_PRODUCT = 60   # số review lấy mỗi sản phẩm
AMAZON_DOMAIN = "amazon.com"

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
DATA_DIR = "data"  # tương đối so với thư mục research/pet-odor

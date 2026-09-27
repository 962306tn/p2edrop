"""Gộp dữ liệu đã cào và phân tích insight bằng Claude API.

Setup:
  export ANTHROPIC_API_KEY=sk-ant-xxx   # https://platform.claude.com

Chạy:
  python analyze_insights.py

Input:  data/*.csv (reddit.csv, quora.csv, amazon_reviews.csv, amazon_products.csv)
Output: data/insight_report.md — báo cáo pain points, desires, objections,
        customer language, hooks và góc content.
"""

from __future__ import annotations

import csv
from pathlib import Path

import anthropic

from common import DATA_DIR

MODEL = "claude-opus-5"
MAX_ROWS_PER_SOURCE = 400      # giới hạn để không tràn context
MAX_TEXT_LEN = 700             # cắt bớt text quá dài mỗi bản ghi

SYSTEM_PROMPT = """\
Bạn là một chuyên gia consumer insight và direct-response copywriting cho \
thị trường pet care (US market). Bạn phân tích dữ liệu thô từ Reddit, Quora \
và Amazon reviews về chủ đề mùi hôi thú cưng (pet odor) và sản phẩm dạng \
"pet odor eliminator gun / spray gun / deodorizer machine".

Nguyên tắc:
- Chỉ rút kết luận từ dữ liệu được cung cấp; khi trích dẫn, dùng NGUYÊN VĂN \
tiếng Anh của người dùng thật (kèm nguồn reddit/quora/amazon).
- Ưu tiên các mẫu lặp lại nhiều lần hơn ý kiến đơn lẻ.
- Phân biệt rõ: nỗi đau (pain), mong muốn (desire), phản đối/lo ngại \
(objection), và ngôn ngữ khách hàng (customer language).
- Viết báo cáo bằng tiếng Việt, giữ trích dẫn tiếng Anh nguyên bản.
"""

REPORT_INSTRUCTIONS = """\
Từ dữ liệu trên, viết báo cáo insight theo cấu trúc Markdown sau:

# Insight Report: Pet Odor / Pet Odor Gun

## 1. Tổng quan dữ liệu
Số lượng bản ghi theo nguồn, chủ đề nổi bật nhất.

## 2. Pain Points (xếp theo tần suất)
Mỗi pain point: mô tả + 2-3 trích dẫn nguyên văn + quy đổi thành "chi phí" \
(thời gian/tiền/cảm xúc) mà khách đang phải chịu.

## 3. Desires & Dream Outcome
Khách thực sự muốn điều gì (không chỉ hết mùi — vd: tự tin mời khách tới nhà).

## 4. Objections & Trust Issues
Lý do họ nghi ngờ sản phẩm khử mùi (đã thử X không hiệu quả, sợ hóa chất hại \
pet, sợ mùi che tạm...). Kèm trích dẫn.

## 5. Giải pháp hiện tại & khoảng trống
Họ đang dùng gì (enzyme cleaner, ozone, baking soda, nến...), điểm yếu từng \
giải pháp theo lời họ nói, và khoảng trống cho sản phẩm odor gun.

## 6. Customer Language Bank
Bảng các cụm từ nguyên văn đáng dùng trong copy, chia theo: mô tả vấn đề / \
mô tả kết quả mong muốn / cảm xúc.

## 7. Content Angles & Hooks
10 góc content + hook cụ thể (viết sẵn bằng tiếng Anh) cho TOFU/MOFU/BOFU, \
mỗi hook ghi rõ dựa trên insight nào ở mục 2-4.

## 8. FAQ & Objection Handling
8-10 câu hỏi thật khách sẽ hỏi + hướng trả lời.
"""


def load_rows(filename: str) -> list[dict]:
    path = DATA_DIR / filename
    if not path.exists():
        print(f"  (bỏ qua — chưa có {path})")
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def rank_rows(rows: list[dict]) -> list[dict]:
    """Ưu tiên bản ghi có score cao và text dài (nhiều tín hiệu)."""
    def key(r: dict) -> float:
        try:
            score = float(r.get("score") or 0)
        except ValueError:
            score = 0.0
        return score + min(len(r.get("text", "")), 500) / 100.0
    return sorted(rows, key=key, reverse=True)


def format_rows(rows: list[dict], label: str) -> str:
    lines = [f"### NGUỒN: {label} ({len(rows)} bản ghi được chọn)"]
    for r in rows:
        text = (r.get("text") or "")[:MAX_TEXT_LEN]
        title = (r.get("title") or "")[:150]
        lines.append(
            f"- [{r.get('type')}|score={r.get('score')}|{r.get('date')}] "
            f"{title} :: {text}"
        )
    return "\n".join(lines)


def build_corpus() -> str:
    sections = []
    for filename, label in [
        ("reddit.csv", "REDDIT"),
        ("quora.csv", "QUORA"),
        ("amazon_reviews.csv", "AMAZON REVIEWS"),
        ("amazon_products.csv", "AMAZON PRODUCTS"),
    ]:
        rows = load_rows(filename)
        if not rows:
            continue
        rows = rank_rows(rows)[:MAX_ROWS_PER_SOURCE]
        sections.append(format_rows(rows, label))
    if not sections:
        raise SystemExit(
            "Chưa có dữ liệu trong data/. Chạy scrape_reddit.py / "
            "scrape_quora.py / scrape_amazon.py trước."
        )
    return "\n\n".join(sections)


def main() -> None:
    corpus = build_corpus()
    client = anthropic.Anthropic()

    print(f"[analyze] Gửi {len(corpus):,} ký tự dữ liệu cho {MODEL}...")
    with client.messages.stream(
        model=MODEL,
        max_tokens=64000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": (
                "Dưới đây là dữ liệu thô đã cào:\n\n"
                f"{corpus}\n\n---\n\n{REPORT_INSTRUCTIONS}"
            ),
        }],
    ) as stream:
        response = stream.get_final_message()

    if response.stop_reason == "refusal":
        details = response.stop_details
        raise SystemExit(f"Model từ chối: {details.explanation if details else ''}")
    if response.stop_reason == "max_tokens":
        print("  ! Cảnh báo: báo cáo bị cắt vì chạm max_tokens.")

    report = "".join(b.text for b in response.content if b.type == "text")
    out = DATA_DIR / "insight_report.md"
    out.write_text(report, encoding="utf-8")
    print(f"[analyze] Đã ghi báo cáo: {out}")
    print(f"  Tokens: in={response.usage.input_tokens:,} "
          f"out={response.usage.output_tokens:,}")


if __name__ == "__main__":
    main()

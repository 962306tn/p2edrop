#!/usr/bin/env python3
"""Tính break-even ROAS, target ROAS và trần CPA cho từng SKU.

    ./scripts/break-even.py [docs/unit-economics.yml]

Đọc file unit economics (xem docs/unit-economics.example.yml) và in bảng ngưỡng.
Dùng con số này làm chuẩn đánh giá campaign — đừng để agent tự suy ROAS mục tiêu
từ dữ liệu Meta, vì Meta không biết giá vốn của bạn.

Công thức, tính trên MỘT đơn:
    contribution    = giá - cogs - ship - phí_thanh_toán - hoàn - phí_cố_định
    break_even_roas = giá / contribution
    target_roas     = giá / (contribution - lãi_mong_muốn * giá)

Cần PyYAML:  pip install pyyaml
"""
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("thiếu PyYAML — cài bằng: pip install pyyaml")

DEFAULT = "docs/unit-economics.yml"


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else DEFAULT)
    if not path.exists():
        sys.exit(f"không thấy {path}\n"
                 f"  cp docs/unit-economics.example.yml {DEFAULT}   rồi điền số thật")

    d = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    v = d.get("variable_costs") or {}
    t = d.get("thresholds") or {}
    ship = v.get("shipping_pct") or 0.0
    fee = v.get("payment_fee_pct") or 0.0
    refund = v.get("refund_rate_pct") or 0.0
    fixed = v.get("fixed_per_order") or 0.0
    profit = t.get("target_profit_pct") or 0.0

    products = [p for p in (d.get("products") or [])
                if p.get("price") is not None and p.get("cogs") is not None]
    if not products:
        sys.exit("chưa SKU nào có cả price và cogs — điền vào rồi chạy lại")

    print(f"\n{path}   (ship {ship:.1%} · fee {fee:.1%}+${fixed:.2f} · "
          f"hoàn {refund:.1%} · lãi mục tiêu {profit:.0%})\n")
    head = (f"{'SKU':<16}{'Giá':>8}{'COGS':>7}{'Lãi gộp':>9}"
            f"{'%':>7}{'BE ROAS':>9}{'Tgt ROAS':>10}{'CPA max':>9}")
    print(head)
    print("-" * len(head))

    best = None
    for p in products:
        price, cogs = float(p["price"]), float(p["cogs"])
        sku = str(p.get("sku") or p.get("title") or "?")
        contrib = price * (1 - ship - fee - refund) - cogs - fixed
        if contrib <= 0:
            print(f"{sku:<16}{price:>8.2f}{cogs:>7.2f}   LỖ ngay cả khi ads = 0")
            continue
        margin = contrib / price
        be = price / contrib
        tgt = price / (contrib - profit * price) if margin > profit else float("inf")
        tgt_s = f"{tgt:>10.2f}" if tgt != float("inf") else f"{'không đạt':>10}"
        print(f"{sku:<16}{price:>8.2f}{cogs:>7.2f}{contrib:>9.2f}"
              f"{margin:>6.1%}{be:>9.2f}{tgt_s}{contrib:>9.2f}")
        if best is None or contrib > best[1]:
            best = (sku, contrib)

    print("\nCPA max = chi tối đa mỗi đơn để HOÀ VỐN. Vượt là lỗ.")
    if best:
        print(f"Traffic lạnh: ưu tiên {best[0]} — lãi gộp ${best[1]:.2f}/đơn, "
              f"chịu được CPA cao nhất.")
    print("Lãi gộp tuyệt đối quan trọng hơn % khi chạy TOFU: % cao trên giá thấp "
          "vẫn không đủ tiền mua một click đắt.\n")


if __name__ == "__main__":
    main()

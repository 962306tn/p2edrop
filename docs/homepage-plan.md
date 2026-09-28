# Plan: Trang chủ Shopify cho All Vibes Pet (theo mẫu mynovapaw.com)

Mục tiêu: dựng trang chủ (homepage) cho store **All Vibes Pet** (allvibespet.com)
theo cấu trúc landing một-sản-phẩm của **NovaPaw** (mynovapaw.com), nhưng dùng
sản phẩm hero thật của store: **VelaHush™ Pet Odor Gun**.

> Lưu ý: mynovapaw.com bị chặn bởi network policy của môi trường cloud này nên
> không fetch trực tiếp được. Cấu trúc dưới đây được tổng hợp từ nội dung đã
> được index công khai của site (hero, pheromone tech, how-to-use 3 bước
> Place/Wash/Reuse, bảng so sánh, reviews, 90-day guarantee, FAQ) — đúng
> archetype landing DTC một sản phẩm mà NovaPaw dùng.

## 1. Phân tích cấu trúc trang chủ NovaPaw

| # | Section NovaPaw | Nội dung |
|---|-----------------|----------|
| 1 | Announcement bar | Ưu đãi + free shipping |
| 2 | Header sticky | Logo, nav anchor (How It Works `#howtouse`, Reviews, FAQ), nút CTA |
| 3 | Hero | Headline lợi ích + sao đánh giá + bullet 3 lợi ích + CTA + ảnh sản phẩm + trust badges |
| 4 | Social proof strip | Số liệu / "as seen in" |
| 5 | Problem → Solution | Nỗi đau (pad dùng 1 lần tốn kém, bẩn) → giải pháp (pheromone + giặt 300 lần) |
| 6 | Features grid | 3–4 tính năng, icon + mô tả ngắn |
| 7 | **How To Use** (`#howtouse`) | 3 bước: Place → Wash → Reuse, ảnh từng bước |
| 8 | Comparison table | NovaPaw vs pad dùng một lần |
| 9 | Offer / bundles | Các gói (1/3/6 pads), gói giữa "Most Popular", quà tặng kèm |
| 10 | Reviews | Grid review có sao + ảnh khách |
| 11 | Guarantee | 90-day money-back, badge |
| 12 | FAQ | Accordion |
| 13 | Final CTA | Nhắc lại offer + guarantee |
| 14 | Footer | Menu, policies, contact, payment icons |

## 2. Map sang All Vibes Pet / VelaHush

Toàn bộ copy lấy từ product description thật (đã có sẵn trên Shopify Admin,
product `velahush-pet-odor-gun`, GID `gid://shopify/Product/15272587166060`):

| Section | Nội dung VelaHush |
|---|---|
| Announcement | Free US shipping over $50 · Ships from California |
| Hero | "You stopped smelling it. Your guests didn't." + dry-mist gun + CTA |
| Problem→Solution | Nose-blind sau 1 tuần; nến/xịt chỉ phủ mùi — VelaHush trung hoà mùi trong sợi vải |
| Features | Dry mist khô sau vài giây · Cordless sạc lại · Không khoá pod (dùng được enzyme cleaner bất kỳ) · Trung hoà tại nguồn |
| How To Use | 1. Click in a pod → 2. Sweep the fabric → 3. Walk away |
| Comparison | VelaHush vs sprays & candles (bảng có sẵn trong description) |
| Bundles | Gun only $69 · Gun + 3 pods $99.99 (Most Popular) · Gun + 6 pods $129.99 (Best Value) |
| Reviews | Placeholder — thay bằng app review (Judge.me/Loox) khi build theme thật |
| Guarantee | 30-day money back (giữ lại pods) + 90-day warranty |
| FAQ | 7 câu từ description ("Questions, answered plainly") |
| Footer | Shop / Support / Policies + contact support@allvibefr.com |

Ảnh: dùng 12 ảnh CDN Shopify có sẵn của product (hero, triple-mist,
six-features, droplets, before-after, collage, v.v.).

## 3. Các bước thực hiện

- [x] **Bước 1 — HTML preview** (`preview/homepage.html`): 1 file tĩnh, đúng
      layout + copy + ảnh thật, gửi user duyệt trước.
- [ ] **Bước 2 — User duyệt / chỉnh sửa** (màu, thứ tự section, copy).
- [ ] **Bước 3 — Build theme bằng Shopify CLI** sau khi duyệt:
  1. `shopify theme init velahush-theme` (clone Dawn làm base) — code nằm trong
     repo này, thư mục `theme/`.
  2. Chuyển từng section HTML thành section Liquid có schema settings:
     `sections/avp-hero.liquid`, `avp-problem.liquid`, `avp-features.liquid`,
     `avp-how-to-use.liquid`, `avp-comparison.liquid`, `avp-bundles.liquid`
     (đọc variants thật từ product qua Liquid, nút Add to cart thật),
     `avp-reviews.liquid`, `avp-guarantee.liquid`, `avp-faq.liquid`.
  3. Ghép trang chủ bằng `templates/index.json` (Online Store 2.0) — merchant
     kéo-thả/sửa text được trong Theme Editor.
  4. Preview: `shopify theme dev --store allvibespet.myshopify.com`
     (cần user đăng nhập CLI) → push bản nháp:
     `shopify theme push --unpublished --theme "VelaHush Homepage"`.
  5. User xem preview trên store thật → duyệt → publish.
- [ ] **Bước 4 — Reviews thật**: gắn app review, thay section placeholder.

## 4. Ghi chú

- Trang viết tiếng Anh (store bán thị trường US, USD).
- Không copy nguyên văn thương hiệu/claim của NovaPaw (pheromone, 300 washes…)
  — chỉ mượn *cấu trúc*; copy là của VelaHush.
- Reviews trong bản preview là nội dung minh hoạ, phải thay bằng review thật
  trước khi publish.

# VelaHush — Kiểm toán giá (10/09/2026)

Quan sát trực tiếp qua Shopify Admin API. **Chưa thay đổi gì trên store** — tài
liệu này để quyết định, không phải nhật ký thay đổi.

## Hiện trạng

Product `velahush-pet-odor-gun` (ACTIVE) có 2 option:

| Option | Giá trị |
|---|---|
| **Setup** | `Gun only` · `Gun + 3 refill pods` · `Gun + 6 refill pods` |
| **Scent** | Lemon · Lavender · Peppermint · Fresh Linen |

12 variant, tất cả `availableForSale: true`, tồn kho 10, `inventoryPolicy: DENY`.

Product `velahush-refill-pods-3-pack`: **$34.99**, cả 4 mùi.

## Lỗi 1 — Bundle đắt hơn mua rời

`Gun only` bán được độc lập, nên khách so sánh được hai đường mua:

| Setup | Giá bundle | Mua rời | Chênh |
|---|---|---|---|
| Gun + 3 pods | $99.99 | $49.00 + $34.99 = $83.99 | 🔴 bundle **đắt hơn $16.00** |
| Gun + 6 pods | $129.99 | $49.00 + $69.98 = $118.98 | 🔴 bundle **đắt hơn $11.01** |

Khách nào tính nhẩm cũng thấy nên mua rời. Bundle đang trừng phạt người mua nhiều.

## Lỗi 2 — `compareAtPrice` đặt ngược chiều

4 variant `Gun + 3 refill pods`: `price = $99.99`, `compareAtPrice = $70.00`.

`compareAtPrice` phải là giá gốc **cao hơn** giá bán. Ở đây thấp hơn → theme render
thành "~~$70.00~~ $99.99", trông như vừa tăng giá. Meta catalog cũng đọc số này.

4 variant `Gun + 6 refill pods` có `compareAtPrice = null` — không hiển thị mức
tiết kiệm nào.

## Lỗi 3 — PDP viết sai giá refill

PDP viết **hai lần** "3 pods for **$21**", trong khi sản phẩm thật bán **$34.99**.
Chênh $13.99 (+67%). Vừa giết chuyển đổi, vừa là rủi ro chính sách Meta về giá gây
hiểu nhầm.

**Nguyên nhân gốc:** `$49 + $21 = $70` — đúng bằng `compareAtPrice` đang mắc kẹt.
Phương án giá cũ là pods $21, bundle $70. Khi đổi pods lên $34.99 và bundle lên
$99.99, `compareAtPrice` của phương án cũ bị bỏ quên.

## Phương án sửa

Chỉ cần nâng **súng lẻ $49 → $69** là thang giá đảo đúng chiều, không phải đụng
vào $99.99 / $129.99:

| Setup | Bundle | Mua rời | Chênh |
|---|---|---|---|
| Gun only | — | **$69.00** | — |
| Gun + 3 pods | $99.99 | $69.00 + $34.99 = $103.99 | ✅ tiết kiệm **$4.00** |
| Gun + 6 pods | $129.99 | $69.00 + $69.98 = $138.98 | ✅ tiết kiệm **$8.99** |

Bốn thay đổi cần ghi:

1. 4 variant `Gun only`: `$49.00` → `$69.00`
2. 4 variant `Gun + 3 pods`: `compareAtPrice` `$70.00` → `$103.99`
3. 4 variant `Gun + 6 pods`: `compareAtPrice` `null` → `$138.98`
4. PDP: 2 chỗ `$21` → `$34.99`

**Cân nhắc bậc giữa.** Tiết kiệm $4.00 hơi mỏng để làm bậc mặc định. Hạ xuống
`$94.99` sẽ thành tiết kiệm $9.00, cân với bậc $129.99, và tạo thang giá dốc đều
$69 / $94.99 / $129.99.

## Vấn đề tồn kho, chưa xử lý

10 chiếc/variant × 12 variant = 120. Ngân sách test $90/ngày với AOV $69–$129.99
sẽ chạm trần tồn kho giữa learning phase, buộc tắt ad set và mất dữ liệu học.

Với `inventoryPolicy: DENY`, hết hàng là variant tự chặn mua — khách bấm vào ad
rồi không mua được. Cần nâng tồn kho, hoặc thu hẹp còn 2–3 variant chủ lực trước
khi bật ads.

# VelaHush — Kiểm toán giá

Cập nhật 10/09/2026. Quan sát qua Shopify Admin API + ảnh chụp PDP thật.

## Trạng thái

| # | Vấn đề | Trạng thái |
|---|---|---|
| 1 | PDP viết refill "$21" trong khi giá thật $34.99 | ✅ **Đã sửa 10/09** |
| 2 | `compareAtPrice` đặt ngược chiều | 🔴 Còn |
| 3 | Bundle đắt hơn mua rời | ⚪ **Không áp dụng** — xem đính chính |
| 4 | Variant `Gun only` sống nhưng ẩn khỏi selector | ✅ **Đã nâng $49 → $69 (10/09)** |

---

## 1. ✅ Đã sửa — giá refill trong PDP

PDP viết hai lần "3 pods for **$21**" trong khi sản phẩm `velahush-refill-pods-3-pack`
bán **$34.99**. Đã sửa cả hai chỗ:

- Tiêu đề `<h2>`: *"Refills: 3 pods for $34.99, and we tell you when"*
- FAQ *"How do I get more pods?"*: *"Three pods are $34.99, ordered whenever you want them."*

Không đụng gì khác trong description. `updatedAt` = `2026-09-10T07:07:59Z`.

**Con số $34.99 được chính trang xác nhận.** Dòng upsell dưới selector viết
*"Upgrade to 6 refills for $30.00 more. Save $4.99 versus the Starter"* — và
$34.99 − $30.00 = **$4.99**, khớp chính xác. Logic của trang đã tính theo $34.99
từ đầu; chỉ có phần chữ là sót lại từ phương án giá cũ (pods $21, bundle $70).

## 2. 🔴 Còn — `compareAtPrice` đặt ngược chiều

| Variant | `price` | `compareAtPrice` hiện tại | Đúng phải là |
|---|---|---|---|
| Gun + 3 refill pods (×4) | $99.99 | **$70.00** | — |
| Gun + 6 refill pods (×4) | $129.99 | **`null`** | — |

`compareAtPrice` là giá gốc gạch ngang, **bắt buộc cao hơn** `price`. Giá trị
$70.00 thấp hơn $99.99 nên theme sẽ không hiện mức tiết kiệm, hoặc hiện thành
"~~$70.00~~ $99.99" — trông như vừa tăng giá.

Con số đặt vào phải cao hơn giá bán thì mới có tác dụng. Vì PDP không bán lẻ súng
(xem mục 3), mức tham chiếu hợp lý là giá trị cảm nhận của bộ, không phải phép
cộng à la carte — đây là quyết định marketing, không có đáp án từ dữ liệu.

## 3. ⚪ Đính chính — bundle KHÔNG đắt hơn mua rời

**Kết luận trước đó của tôi sai.** Tôi đọc Admin API thấy variant `Gun only` $49
với `availableForSale: true` rồi suy ra khách mua rời được, và kết luận bundle
$99.99 đắt hơn $83.99.

Ảnh chụp PDP thật cho thấy selector **chỉ render 2 lựa chọn**:

| Lựa chọn | Giá |
|---|---|
| VelaHush™ Starter Set — 1 gun + 3 pods *(chọn sẵn)* | $99.99 |
| VelaHush™ Refill Bundle — 1 gun + 6 pods *(BEST VALUE)* | $129.99 |

Không có `Gun only`. Khách vào trang này **không có đường mua rời**, nên phép so
sánh $83.99 vs $99.99 không tồn tại. Thang giá trên PDP là hợp lệ.

## 4. ✅ Đã sửa — `Gun only` nâng lên $69

Bốn variant `Gun only` đã đổi từ $49.00 → **$69.00**:

| Variant | ID |
|---|---|
| Gun only / Lemon | `54303710151020` |
| Gun only / Lavender | `54303710183788` |
| Gun only / Peppermint | `54303710216556` |
| Gun only / Fresh Linen | `54303710249324` |

Selector trên PDP vẫn chỉ hiện 2 bundle, nên với khách vào trang thì không đổi gì.
Thay đổi này là để **product feed**: Meta catalog và Google Shopping đồng bộ mọi
variant, nên trước đây feed hiện $49 trong khi trang không bán mức đó. Ở $69,
khoảng cách với bundle $99.99 đủ gần để không tạo hụt kỳ vọng.

Tiện thể nó cũng qua ngưỡng free shipping $50, thứ mà mức $49 hụt đúng $1.

## 5. ✅ Đã sửa — tồn kho nâng lên 100/variant

| Sản phẩm | Trước | Sau |
|---|---|---|
| VelaHush Pet Odor Gun (12 variant) | 10 | **100** → 1.200 |
| VelaHush Refill Pods, 3 Pack (4 variant) | 10 | **100** → 400 |

Location duy nhất là **CJ - TAM THOI** (`gid://shopify/Location/115651641708`) —
dropshipping, nên con số tồn kho là cổng chặn mua chứ không phải hàng vật lý
trong kho. `inventoryPolicy` giữ nguyên `DENY`.

1.200 chiếc thừa sức cho tuần test: $630 ngân sách ở AOV $99.99, kể cả ROAS 3
cũng chỉ khoảng 19 đơn.

**Lưu ý khi xem trong Admin:** trường tổng `totalInventory` của product cập nhật
trễ và có thể vẫn hiện `120` một lúc. Số per-variant mới là số thật.

## Trạng thái tổng kết

| # | Vấn đề | Trạng thái |
|---|---|---|
| 1 | PDP viết refill "$21" | ✅ → $34.99 |
| 2 | `compareAtPrice` đặt ngược chiều | 🔴 **Còn lại duy nhất** |
| 3 | Bundle đắt hơn mua rời | ⚪ Không áp dụng (đính chính) |
| 4 | `Gun only` $49 lệch feed | ✅ → $69 |
| 5 | Tồn kho 10/variant | ✅ → 100/variant |

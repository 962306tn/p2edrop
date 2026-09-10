# VelaHush — Kiểm toán giá

Cập nhật 10/09/2026. Quan sát qua Shopify Admin API + ảnh chụp PDP thật.

## Trạng thái

| # | Vấn đề | Trạng thái |
|---|---|---|
| 1 | PDP viết refill "$21" trong khi giá thật $34.99 | ✅ **Đã sửa 10/09** |
| 2 | `compareAtPrice` đặt ngược chiều | 🔴 Còn |
| 3 | Bundle đắt hơn mua rời | ⚪ **Không áp dụng** — xem đính chính |
| 4 | Variant `Gun only` sống nhưng ẩn khỏi selector | 🟡 Cần quyết định |

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

## 4. 🟡 Cần quyết định — variant `Gun only` sống nhưng ẩn

Bốn variant `Gun only` ($49.00, tồn kho 10, `availableForSale: true`) vẫn tồn tại
trong Admin dù selector không hiện. Chúng vẫn tới được khách qua:

- **URL variant trực tiếp** — `?variant=54303710151020` (và 3 mùi còn lại)
- **Meta catalog / Google Shopping feed** — feed đồng bộ **mọi** variant, nên $49
  sẽ xuất hiện trong catalog ads dù PDP không bán mức giá đó
- Tìm kiếm nội bộ store, một số block product recommendation

Rủi ro cụ thể ở tuần chạy ads: Advantage+ Catalog Ads hiện "$49", khách bấm vào,
PDP chỉ có $99.99. Vừa hụt kỳ vọng vừa là rủi ro chính sách giá gây hiểu nhầm.

Ba cách xử lý:

| Cách | Đánh đổi |
|---|---|
| Xoá hẳn 4 variant `Gun only` | Sạch nhất. Mất điểm giá vào cửa nếu sau này muốn dùng |
| Nâng lên $69 rồi để nguyên | Feed hiện $69, gần bundle hơn, bớt hụt kỳ vọng |
| Giữ nguyên $49 | Feed vẫn hiện $49 — phải loại trừ thủ công trong Commerce Manager |

Nên chốt trước khi bật catalog ads, không gấp cho ad set TOF tuần 1.

## Tồn kho, chưa xử lý

10 chiếc/variant × 12 variant = 120. Ngân sách $90/ngày với AOV $99.99–$129.99 sẽ
chạm trần tồn kho giữa learning phase. Với `inventoryPolicy: DENY`, hết hàng là
variant tự chặn mua — khách bấm ad rồi không mua được.

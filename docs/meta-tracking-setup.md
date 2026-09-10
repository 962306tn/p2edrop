# VelaHush — Dựng tracking Meta từ số 0

Điều kiện tiên quyết trước khi tiêu đồng ads đầu tiên. Không có bước nào ở đây là
tùy chọn: thiếu tracking thì Meta không có tín hiệu để tối ưu, và $630 ngân sách
test sẽ mua về dữ liệu không đọc được.

## Hiện trạng đo được (10/09/2026)

Quan sát trực tiếp qua Shopify Admin API:

| Trường | Giá trị | Ý nghĩa |
|---|---|---|
| Store | All Vibes Pet · `allvibespet.com` | ✅ Đã có custom domain |
| Plan · Tiền tệ · Quốc gia | Advanced · USD · United States | ✅ Đúng cấu hình cho thị trường Mỹ |
| Múi giờ | PDT | ✅ Đã sửa từ `+07` |
| **Tổng số đơn hàng** | **0** | 🔴 Pixel chưa từng nhận một event `Purchase` nào |
| Web Pixel / app đã cài | ❓ | Không đọc được — kết nối MCP thiếu scope `read_pixels` |

**Hệ quả của "0 đơn hàng":** đây là tài khoản lạnh hoàn toàn. Không có custom
audience, không có lookalike, không có dữ liệu để Meta học. Nó **không** có nghĩa
là phải chạy Traffic thay vì Purchase — vẫn chạy Purchase, nhưng phải chấp nhận
learning phase dài hơn và không được sốt ruột tắt sớm.

## Thứ tự bắt buộc

Sai thứ tự là phải làm lại. Domain verify phải xong **trước** khi cấu hình AEM.

### 1. Xác minh domain (làm trước tiên)

Business Manager → **Brand Safety → Domains** → thêm `allvibespet.com` → xác minh
bằng **DNS TXT record** (bền hơn meta-tag; theme update không làm mất).

Chưa verify domain thì không cấu hình được ưu tiên sự kiện ở bước 5, và Meta sẽ
hạn chế quyền tối ưu trên tên miền bạn không sở hữu.

### 2. Tạo Dataset (Pixel)

Events Manager → **Connect data sources → Web** → đặt tên `AllVibesPet — Web`.
Ghi lại **Dataset ID** (15–16 chữ số) — bạn sẽ cần đưa nó cho tôi.

Meta đã đổi tên "Pixel" thành "Dataset". Cùng một thứ, cùng một ID.

### 3. Gắn vào Shopify

Cài app **Facebook & Instagram** từ Shopify App Store → kết nối Business
Portfolio → chọn Dataset vừa tạo → bật **Maximum** ở phần data sharing.

Mức `Maximum` chính là Conversions API. Đây là cách bật CAPI đúng chuẩn cho
Shopify — **không** tự dựng server-side qua Zapier hay GTM, không cần thiết và dễ
gây trùng event.

### 4. Đặt một đơn hàng thật

Không phải test order của Shopify — **một đơn thật, thẻ thật, checkout thật**, rồi
tự hoàn tiền sau.

Đây là bước duy nhất chứng minh toàn bộ chuỗi hoạt động: thẻ Mỹ qua được cổng
thanh toán, `Purchase` bắn về Events Manager, giá trị đơn và currency đúng USD.
Bỏ qua bước này là cách phổ biến nhất để phát hiện checkout hỏng sau khi đã tiêu
$300 tiền ads.

Trong Events Manager → **Test Events**, đơn đó phải hiện `Purchase` với:
- `value` khớp số tiền thật, `currency` = `USD`
- Nguồn ghi **cả** Browser lẫn Server (đó là dấu hiệu CAPI đang chạy)
- **Event Match Quality ≥ 6.0** — dưới ngưỡng này nghĩa là thiếu email/phone
  hashed, tối ưu sẽ kém

### 5. Ưu tiên sự kiện (Aggregated Event Measurement)

Events Manager → Dataset → **Aggregated Event Measurement → Configure Web Events**.
Xếp đúng thứ tự này, cao nhất trước:

```
1. Purchase
2. InitiateCheckout
3. AddToCart
4. ViewContent
5. PageView
```

Chỉ 8 slot, và mỗi lần đổi có thời gian đóng băng ~72 giờ. Xếp một lần cho đúng.

### 6. Catalog (làm luôn, dùng cho retarget tuần 2)

App Facebook & Instagram sẽ tự đẩy sản phẩm sang **Commerce Manager**. Kiểm tra
catalog có đủ 12 variant VelaHush và giá khớp Shopify. Chưa cần Advantage+ Catalog
Ads ở tuần 1, nhưng catalog cần thời gian để chín.

## Checklist nghiệm thu

Chưa tick đủ thì chưa bật ads:

- [ ] `allvibespet.com` trạng thái **Verified** trong Brand Safety → Domains
- [ ] Dataset ID đã ghi lại
- [ ] App Facebook & Instagram đã kết nối, data sharing = **Maximum**
- [ ] Một đơn thật đã đi hết checkout và đã được hoàn tiền
- [ ] `Purchase` hiện trong Test Events, nguồn **Browser + Server**
- [ ] Event Match Quality ≥ 6.0
- [ ] AEM đã xếp đúng 5 sự kiện theo thứ tự trên
- [ ] Trang Privacy Policy đã có link ở footer (Meta kiểm tra khi review ads)

## Sau khi xong, gửi tôi

Ba con số này là đủ để tôi dựng campaign qua MCP:

| Cần | Định dạng |
|---|---|
| Ad Account ID | `act_XXXXXXXXX` |
| Dataset (Pixel) ID | 15–16 chữ số |
| Facebook Page ID | số, kèm tên Instagram liên kết |

Tôi sẽ đọc ngược lại qua Meta Ads MCP để xác nhận dataset đang nhận event trước
khi tạo bất kỳ campaign nào.

## Những lỗi khiến phải làm lại từ đầu

- **Cài pixel hai lần** — vừa qua app Facebook & Instagram, vừa dán code vào
  `theme.liquid`. Kết quả: mọi event đếm đôi, ROAS ảo gấp 2, tối ưu sai. Chỉ dùng
  app.
- **Đổi thứ tự AEM sau khi đã chạy** — đóng băng 72 giờ, ad set đang chạy mất tín
  hiệu giữa chừng.
- **Verify domain bằng meta-tag rồi đổi theme** — mất verify, ads tụt phân phối
  mà không có cảnh báo rõ ràng.
- **Tin vào Test Events rồi thôi** — Test Events chỉ chứng minh event bắn được.
  Phải xem **Diagnostics** sau 24 giờ chạy thật để thấy lỗi deduplication.

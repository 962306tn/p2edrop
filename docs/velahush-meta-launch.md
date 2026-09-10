# VelaHush — Cấu trúc campaign Meta & cách chạy qua MCP

Bản thực thi của `PET-ODOR-GUN-STRATEGY.md` (branch `claude/pet-odor-gun-analysis-2ev2ap`),
đã cập nhật theo hiện trạng store ngày 10/09/2026.

Strategy doc viết khi store còn là môi trường test. Từ đó tới nay Ngày 1 và phần
lớn Ngày 2 trong kế hoạch 7 ngày **đã xong**: custom domain, múi giờ Mỹ, PDP thật
với 12 variant, ảnh riêng, copy sạch về compliance. Phần còn thiếu là **tracking**
(xem `meta-tracking-setup.md`) và ba blocker dưới đây.

## 🔴 Ba blocker phải xử lý trước khi bật ads

### 1. Thang giá đang đảo chiều

`Gun only` bán độc lập được ($49), nên bundle $99.99 **đắt hơn mua rời $16.00**.
PDP còn viết refill "$21" trong khi giá thật là $34.99, và `compareAtPrice` của
bậc giữa bị đặt ngược ($70 thấp hơn giá bán $99.99).

Chi tiết và phương án sửa: **`velahush-pricing-audit.md`**. Tóm tắt: nâng súng lẻ
lên $69 là thang giá đảo đúng chiều, không phải đụng vào $99.99 / $129.99.

**Chưa sửa gì trên store** — đang chờ quyết định.

### 2. Tồn kho không đủ cho ngân sách test

Tổng 120 chiếc, 10/variant trên 12 variant. Với $90/ngày và AOV $49–$99.99, nếu
creative ăn thì hết hàng giữa learning phase, buộc phải tắt ad set — mất sạch dữ
liệu học và phải chạy lại từ đầu.

Xử lý theo một trong ba cách, trước khi bật:
- Nâng tồn kho thật, hoặc
- Thu hẹp còn 2–3 variant chủ lực (khuyến nghị: **Fresh Linen** và **Lemon**,
  bản `Gun + 3 pods` $99.99) thay vì rải đều 12, hoặc
- Bật oversell có kiểm soát kèm thời gian giao rõ ràng trên PDP

### 3. Ngưỡng free shipping đặt lệch

"Free US shipping over $50" nhưng bản `Gun only` giá **$49.00** — hụt đúng $1.
Nếu đây là chủ ý đẩy lên bundle thì được, nhưng nó cũng tạo cảm giác bị gài. Cân
nhắc hạ ngưỡng xuống $45 hoặc nâng gun lên $50.

## Cấu trúc campaign tuần 1

**Một campaign duy nhất, ba tầng phễu, ngân sách đặt ở cấp ad set (ABO).**

Objective **Purchase** cho cả ba tầng. Không dùng Traffic hay Engagement, kể cả
khi tài khoản chưa có đơn nào.

### ⚠️ Bắt buộc ABO, không được CBO

Với CBO (Advantage campaign budget), Meta tự dồn tiền về ad set có CPA rẻ nhất.
Tệp BOF nhỏ nên **luôn** trông rẻ nhất một cách giả tạo — nó sẽ hút sạch ngân sách
và bỏ đói TOF, làm hỏng hoàn toàn tỉ lệ phễu. Muốn giữ đúng tỉ lệ thì ngân sách
phải đặt ở cấp ad set.

### Ba ad set

| Ad set | Tệp | Số creative |
|---|---|---|
| **TOF — Cold** | US · 30–65+ · không interest | **6 ads (60%)** |
| **MOF — Warm** | Video viewers ≥25% · FB/IG engagers 365d · site visitors 30d | **3 ads (30%)** |
| **BOF — Hot** | ATC + InitiateCheckout 14d · PDP viewers 7d, loại trừ người đã mua | **1 ad (10%)** |

Tỉ lệ 60/30/10 là **tỉ lệ số lượng creative**, tổng 10 ads.

### 🔴 Ngân sách KHÔNG chia theo 60/30/10 ở tuần 1

Store có 0 đơn và 0 traffic, nên **pool MOF và BOF đang rỗng**. Không thể retarget
người đã xem khi chưa ai xem.

Cụ thể hơn: custom audience của Meta cần khoảng **1.000 người** mới phân phối được.
Ad set nhắm tệp rỗng sẽ không tiêu được tiền, hoặc tiêu vào vài trăm người với tần
suất cao — đốt ngân sách mà không học được gì.

Vì vậy:

| Giai đoạn | TOF | MOF | BOF |
|---|---|---|---|
| **Tuần 1** — pool rỗng | **$90/ngày** | PAUSED | PAUSED |
| **Khi pool ≥1.000 người** (thường 7–14 ngày) | $54 | $27 | $9 |

**Dựng đủ cả 3 ad set ngay bây giờ** kèm đủ 10 creative, nhưng để MOF/BOF ở
`PAUSED`. Bật khi Audiences báo tệp đã đủ lớn. Làm vậy thì cấu trúc sẵn sàng, và
không có đồng nào chảy vào tệp rỗng.

Tổng tuần 1: **$90/ngày × 7 ngày = $630**.

### Vì sao vẫn chạy Purchase khi có 0 đơn

Tài khoản lạnh ra khỏi learning phase chậm (cần 50 purchase/tuần/ad set — gần như
chắc chắn không đạt ở tuần 1). Điều đó **không** biến Purchase thành lựa chọn sai.
Tối ưu Traffic sẽ dạy Meta tìm người hay bấm chứ không phải người hay mua, và tín
hiệu rác đó ở lại trong tài khoản. Chấp nhận learning phase dài, đọc tín hiệu
creative thay vì CPA ở những ngày đầu.

## Chạy qua MCP

Sau khi `meta-ads` đã `connected` (xem `meta-ads-mcp.md`), làm theo thứ tự này ở
Claude Code **local**. Mỗi bước đọc lại kết quả trước khi sang bước sau.

**Bước 1 — xác nhận kết nối và dataset:**
```
Liệt kê các ad account Meta của tôi. Với act_XXXXXXXXX, cho tôi biết currency,
timezone, spend cap và trạng thái dataset đang gắn.
```

**Bước 2 — tạo campaign, để PAUSED:**
```
Trong act_XXXXXXXXX tạo 1 campaign PAUSED tên "VH | Funnel | US",
objective OUTCOME_SALES, buying type AUCTION, không đặt special ad category,
và KHÔNG bật Advantage campaign budget (ngân sách phải ở cấp ad set).
Đọc lại cho tôi xem trước khi tạo ad set.
```

**Bước 3 — ba ad set.** Ngân sách tính bằng **cents**: `$90` truyền là `9000`,
`$5` là `500`. Luôn bảo agent đọc ngược lại con số sau khi tạo.
```
Trong campaign "VH | Funnel | US" tạo 3 ad set, tất cả PAUSED,
optimization goal OFFSITE_CONVERSIONS, conversion event Purchase,
pixel <DATASET_ID>:
  1. "TOF | Broad"  — daily budget 9000, US, tuổi 30-65+, không interest
  2. "MOF | Warm"   — daily budget 500, custom audience video viewers 25% +
                      engagers 365d + site visitors 30d
  3. "BOF | Hot"    — daily budget 500, custom audience ATC/IC 14d +
                      PDP viewers 7d, loại trừ Purchasers 180d
Đọc lại cả 3 kèm daily_budget dạng đô-la để tôi kiểm tra.
```

**Bước 4 — 10 ad theo tỉ lệ 60/30/10.** Cần Page ID + Instagram, link tới
`/products/velahush-pet-odor-gun` hoặc advertorial, kèm UTM. Đặt 6 ad vào
`TOF | Broad`, 3 ad vào `MOF | Warm`, 1 ad vào `BOF | Hot`.

**Bước 5 — kiểm tra bằng mắt trong Ads Manager, rồi mới bật.** Tuần 1 chỉ bật
`TOF | Broad`; giữ `MOF | Warm` và `BOF | Hot` ở PAUSED cho tới khi Audiences báo
tệp đủ ~1.000 người. Việc chuyển từ PAUSED sang ACTIVE nên do bạn làm thủ công.

### UTM chuẩn

```
?utm_source=facebook&utm_medium=paid&utm_campaign={{campaign.name}}&utm_content={{ad.name}}&utm_term={{adset.name}}
```

Có UTM thì tôi đối chiếu được số liệu Meta với đơn hàng thật trong Shopify qua
MCP — đây là cách duy nhất phát hiện Meta báo thừa conversion.

## Đọc chỉ số

Ngày 5–7 đọc **tín hiệu creative**, không đọc CPA. Ngưỡng lấy từ PHẦN 10 của
strategy doc:

| Chỉ số | Ngưỡng tốt | Ý nghĩa khi hụt |
|---|---|---|
| Hook Rate (3s view / impression) | **>25%** | <15% sau 3.000 impression → hook chết, không phải sản phẩm chết |
| Hold Rate (ThruPlay / 3s view) | **>15%** | Hook tốt + Hold thấp → giữ hook, thay thân video |
| CTR (link) | >1.2% | |
| CPC | <$1.20 | |
| ATC rate | >6% | CTR cao + ATC thấp → lỗi ở landing page, không phải ở ad |

**Luật cứng:** không tắt gì trước 48 giờ. Không đổi ngân sách trước 72 giờ.

Khi có dữ liệu, dùng skill `meta-ads-analyzer-mod-by-noti` để đọc — nó xử lý đúng
Breakdown Effect, thứ mà đọc bằng mắt gần như luôn sai.

## Guardrails

- Campaign tạo qua MCP luôn ở `PAUSED`. Giữ nguyên, tự bật bằng tay.
- Đặt **spend cap** ở cấp tài khoản trước khi bật ad đầu tiên. Đây là phanh tay
  duy nhất không phụ thuộc vào việc agent hành xử đúng.
- Không "Always allow" các tool `create` / `update` / `activate`. Chỉ auto-approve
  nhóm đọc báo cáo.
- Nêu rõ `act_XXXXXXXXX` trong mỗi prompt khi có nhiều portfolio.
- Claim cấm tuyệt đối (PHẦN 8.4): *disinfect · sanitize · kills 99.9% ·
  antibacterial · mite remover · UV sterilizer · medical grade · relieves
  allergies · permanently eliminates*, và không quay cảnh xịt trực tiếp lên thú
  cưng. PDP hiện tại đã sạch — giữ nguyên chuẩn đó trong ad copy.

# VelaHush — Cấu trúc campaign Meta & cách chạy qua MCP

Bản thực thi của `PET-ODOR-GUN-STRATEGY.md` (branch `claude/pet-odor-gun-analysis-2ev2ap`),
đã cập nhật theo hiện trạng store ngày 10/09/2026.

Strategy doc viết khi store còn là môi trường test. Từ đó tới nay Ngày 1 và phần
lớn Ngày 2 trong kế hoạch 7 ngày **đã xong**: custom domain, múi giờ Mỹ, PDP thật
với 12 variant, ảnh riêng, copy sạch về compliance. Phần còn thiếu là **tracking**
(xem `meta-tracking-setup.md`) và ba blocker dưới đây.

## 🔴 Ba blocker phải xử lý trước khi bật ads

### 1. Giá refill trên PDP mâu thuẫn với giá thật

PDP `velahush-pet-odor-gun` viết **hai lần**:

> "Refills: 3 pods for **$21**, and we tell you when"
> "Three pods are **$21**, ordered whenever you want them."

Sản phẩm thật `velahush-refill-pods-3-pack` đang bán **$34.99** — cả 4 mùi.

Chênh **$13.99 (+67%)**. Đây vừa là sát thủ chuyển đổi (khách bấm vào thấy giá
khác), vừa là rủi ro chính sách Meta về giá gây hiểu nhầm. Sửa một trong hai
chiều, nhưng phải khớp trước khi chạy — đặc biệt nếu định dùng angle "Money Math"
vốn xây trên chi phí vận hành.

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

Objective **Purchase** cho cả ba. Không dùng Traffic hay Engagement — kể cả khi
tài khoản chưa có đơn nào.

| Ad set | Ngân sách | Targeting | Vai trò |
|---|---|---|---|
| **ASC** — Advantage+ Shopping | $30/ngày | Để Meta tự quyết | Đường cơ sở. Thường thắng ở tài khoản lạnh |
| **ABO Broad** | $30/ngày | US · 30–65+ · không interest | Kiểm chứng creative có tự đứng được không |
| **ABO Interest** | $30/ngày | Dog/Cat owners · Chewy · PetSmart · Nature's Miracle | Kiểm chứng giả định avatar ở PHẦN 2 |

Cả ba dùng **chung 5 creative** — đó là điều kiện để so sánh ad set có nghĩa.

Tổng: **$90/ngày × 7 ngày = $630**.

### Vì sao vẫn chạy Purchase khi có 0 đơn

Tài khoản lạnh sẽ ra khỏi learning phase chậm (cần 50 purchase/tuần/ad set — bạn
gần như chắc chắn không đạt ở tuần 1). Điều đó **không** biến Purchase thành lựa
chọn sai. Tối ưu cho Traffic sẽ dạy Meta tìm người hay bấm chứ không phải người
hay mua, và tín hiệu rác đó ở lại trong tài khoản. Chấp nhận learning phase dài,
đọc tín hiệu creative thay vì CPA ở những ngày đầu.

## Chạy qua MCP

Sau khi `meta-ads` đã `connected` (xem `meta-ads-mcp.md`), làm theo thứ tự này ở
Claude Code **local**. Mỗi bước đọc lại kết quả trước khi sang bước sau.

**Bước 1 — xác nhận kết nối và dataset:**
```
Liệt kê các ad account Meta của tôi. Với act_XXXXXXXXX, cho tôi biết currency,
timezone, spend cap và trạng thái dataset đang gắn.
```

**Bước 2 — tạo khung campaign, để PAUSED:**
```
Trong act_XXXXXXXXX tạo 3 campaign PAUSED, objective OUTCOME_SALES, không đặt
special ad category:
  1. "VH | ASC | Cold"        — Advantage+ Shopping, daily budget $30
  2. "VH | ABO Broad | Cold"  — daily budget $30
  3. "VH | ABO Interest | Cold" — daily budget $30
Đọc lại cả 3 cho tôi xem trước khi tạo ad set.
```

**Bước 3 — ad set.** Nhớ: ngân sách tính bằng **cents**, `$30` phải truyền là
`3000`. Bảo agent đọc ngược lại con số sau khi tạo.

**Bước 4 — ad.** Cần Page ID + Instagram, link tới `/products/velahush-pet-odor-gun`
hoặc advertorial, kèm UTM.

**Bước 5 — kiểm tra bằng mắt trong Ads Manager, rồi mới bật.** Việc chuyển từ
PAUSED sang ACTIVE nên do bạn làm thủ công ở tuần đầu.

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

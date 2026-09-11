# Lên ads bằng chat: MCP, Telegram, Lark

Tài liệu này trả lời: *"làm sao để ngồi trong một khung chat và bảo nó lên campaign?"*
— bằng MCP ngay trong Claude Code, bằng bot Telegram, hoặc bằng bot Lark.

> **Cảnh báo:** lên ads là tiêu tiền thật. Mọi thứ dưới đây phải chạy kèm guardrails ở
> [mục 7](#7-guardrails-bắt-buộc). Đừng bao giờ để agent vừa tạo vừa bật campaign mà
> không có người bấm duyệt.

**Mục lục**

1. [Kiến trúc 3 lớp](#1-hiểu-đúng-kiến-trúc-trước-đã)
2. [Checklist điều kiện setup](#2-checklist-điều-kiện-setup) ← bắt đầu ở đây
3. [Cắm MCP vào Claude Code](#3-cắm-mcp-vào-claude-code)
4. [Cho agent biết unit economics](#4-cho-agent-biết-unit-economics)
5. [Quy trình lên ads](#5-quy-trình-lên-ads-thật-bằng-chat)
6. [Telegram & Lark](#6-đường-telegram) · [Lark](#7-đường-lark-feishu)
7. [Guardrails](#8-guardrails-bắt-buộc) · [So sánh](#9-so-sánh-nhanh) · [Lộ trình](#10-nên-đi-đường-nào)

---

## 1. Hiểu đúng kiến trúc trước đã

Đây là chỗ 90% người mới hiểu sai. "Lên ads bằng Telegram" không phải một tính năng
— nó là 3 lớp ghép lại:

```
Lớp 3  GIAO DIỆN CHAT      Claude Code  |  Telegram bot  |  Lark bot
                                    |
Lớp 2  BỘ NÃO (AGENT)      Claude / n8n / server tự viết
                                    |
Lớp 1  DỮ LIỆU + QUYỀN     Meta Ads API  |  TikTok Ads API  |  Shopify  |  unit economics
```

- **Lớp 1 là lớp khó và bắt buộc** — vừa là quyền truy cập, vừa là dữ liệu để ra
  quyết định. Tốn thời gian nhất, và là toàn bộ nội dung của [mục 2](#2-checklist-điều-kiện-setup).
- **Lớp 2 ra quyết định** — đọc brief, chọn audience, viết copy, gọi API.
- **Lớp 3 chỉ là cái cửa sổ.** Telegram và Lark **không** lên ads; chúng chỉ chuyển
  tin nhắn của bạn xuống lớp 2.

Hệ quả: **làm lớp 1 + 2 chạy được trong Claude Code trước**, rồi mới gắn Telegram/Lark.

---

## 2. Checklist điều kiện setup

Đánh dấu từng dòng. Cột cuối cho biết **thiếu nó thì tắc ở đâu** — quan trọng vì phần
lớn lỗi ở đây không báo lỗi rõ ràng, chúng chỉ trả về rỗng và bạn tưởng MCP hỏng.

### 2.1. Meta — tài khoản và quyền

| ✓ | Điều kiện | Lấy ở đâu | Thiếu thì sao |
|---|---|---|---|
| ☐ | Tài khoản Facebook cá nhân **đã bật 2FA** | Facebook → Settings → Security | Meta bắt buộc 2FA với thành viên Business Manager. Tắc ngay ở bước OAuth |
| ☐ | **Business Manager (Business Portfolio)** | business.facebook.com | Ad account cá nhân rời không nằm trong BM sẽ khó hoặc không cắm được |
| ☐ | **Role advertiser hoặc admin** trên ad account | Business Settings → Accounts → Ad Accounts | **Lỗi hay gặp nhất.** OAuth vẫn báo thành công nhưng mọi tool trả rỗng |
| ☐ | Ad account **không bị restricted/disabled** | Ads Manager → Account Quality | Tool đọc được nhưng mọi lệnh ghi đều fail |
| ☐ | **Payment method hợp lệ**, chưa chạm hạn mức chi tiêu | Billing | Tạo được campaign, bật lên là dừng ngay |
| ☐ | Nằm trong diện **eligible** của beta | Hiện ra ở bước OAuth | Open beta từ 29/04/2026 nhưng thay đổi theo region |

### 2.2. Meta — tracking (phần quyết định ads có chạy được không)

MCP thông rồi vẫn không lên được ads nếu thiếu mấy thứ này. Đây là điều kiện của
**chính Meta Ads**, không phải của MCP:

| ✓ | Điều kiện | Thiếu thì sao |
|---|---|---|
| ☐ | **Facebook Page** (ads phải chạy dưới danh nghĩa một Page) | Không tạo được ad |
| ☐ | **Pixel / dataset** đã gắn vào Shopify | Không chọn được objective Sales |
| ☐ | Event **Purchase** bắn đúng, đã test | Chạy được nhưng tối ưu mù — tệ hơn không chạy |
| ☐ | **Domain đã verify** (allvibefr.com) | Vướng giới hạn iOS 14+, aggregated event bị khoá |
| ☐ | **Aggregated Event Measurement** đã cấu hình, Purchase ở ưu tiên 1 | Mất phần lớn conversion iOS |
| ☐ | **Conversions API** (khuyến nghị mạnh) | Mất 20-40% signal, ROAS báo về thấp giả tạo |
| ☐ | **Catalog** — chỉ khi chạy DPA / Advantage+ Shopping | Không chạy được loại campaign đó |

> Shopify có sẵn app **Facebook & Instagram** làm hộ phần lớn mục này (pixel, CAPI,
> catalog sync). Cài nó trước khi làm tay.

### 2.3. Shopify — kết nối và **vệ sinh dữ liệu**

Đây là phần trả lời trực tiếp cho *"nối hết Shopify về là ok còn gì"*. Gần đúng — nhưng
chỉ khi dữ liệu trong Shopify **đã được điền**. Nối một store rỗng thì agent vẫn mù.

| ✓ | Điều kiện | Vì sao cần |
|---|---|---|
| ☐ | Shopify MCP đã kết nối | Để agent đọc đơn, sản phẩm, tồn kho |
| ☐ | **"Cost per item" đã điền cho MỌI variant** | ⚠️ **Đây là điều kiện quan trọng nhất của cả mục này.** Không có giá vốn thì không tính được biên lợi nhuận, không có biên lợi nhuận thì không có break-even ROAS |
| ☐ | Giá bán và variant đúng như đang bán thật | Agent tính sai ngưỡng |
| ☐ | Tracking tồn kho đang bật | Để agent biết đề xuất tắt ads khi hết hàng |
| ☐ | Biết **phí ship + phí thanh toán + tỉ lệ hoàn** thực tế | Shopify không quy các khoản này về từng đơn |
| ☐ | `docs/unit-economics.yml` đã điền | [Mục 4](#4-cho-agent-biết-unit-economics) |

**Trạng thái hiện tại của store này (kiểm tra ngày 2026-09-11):**

```
Store    : All Vibes Pet — allvibefr.com (Advanced, USD)
Sản phẩm : VelaHush Pet Odor Gun        $69.00    cost per item = (trống)
           VelaHush Refill Pods, 3 Pack $34.99    cost per item = (trống)
```

→ **`unitCost` đang null trên toàn bộ variant.** Nối Shopify MCP bây giờ thì agent
đọc được doanh thu và tồn kho, nhưng **không biết bạn lãi hay lỗ**. Điền Cost per item
(Shopify admin → Products → variant → Cost per item) là việc cần làm trước tiên.

### 2.4. Client và môi trường

| ✓ | Điều kiện | Ghi chú |
|---|---|---|
| ☐ | Client hỗ trợ remote MCP | Claude Code, Claude Desktop, ChatGPT |
| ☐ | Chạy **local**, không phải Claude Code trên web | Session web đi qua egress proxy; domain Meta/TikTok thường không được allowlist |
| ☐ | Đã chọn **scope** cho Meta | Xem bảng dưới |
| ☐ | `.env` / token **không commit** | `.gitignore` đã chặn `.env` và `.mcp.json` |

**Chọn scope Meta — quyết định quan trọng nhất:**

| Scope | Làm được | Khi nào |
|---|---|---|
| **Read-only** | Đọc report, insights, chẩn đoán | **Bắt đầu ở đây.** Vài tuần đầu chỉ cho xem |
| **Read/write** | Tạo / sửa / pause campaign, ad set | Khi đã tin agent hiểu account |
| **Read/write/financial** | Đụng tới thanh toán | Chỉ khi có bước người duyệt rõ ràng |

Đừng cấp `read/write/financial` cho một agent đa dụng — một agent vừa lướt web vừa đọc
file vừa có quyền tài chính trên ad account là rủi ro không cần thiết.

### 2.5. Cái bạn **không** cần

Khác biệt lớn nhất so với đường Marketing API truyền thống:

❌ Developer app · ❌ App Review · ❌ Access token tự quản và tự rotate · ❌ Viết code

Thay bằng **một cú OAuth Business**. Setup từ vài ngày xuống vài phút.

---

## 3. Cắm MCP vào Claude Code

### 3.1. Meta

Meta mở **Ads AI Connectors** ở open beta từ 29/04/2026: remote MCP server chính chủ
tại `https://mcp.facebook.com/ads`, xác thực bằng OAuth Business.

```bash
./scripts/setup-ads-mcp.sh
# tương đương: claude mcp add --transport http meta-ads https://mcp.facebook.com/ads --scope user
```

Rồi xác thực — **thêm URL chưa phải là đăng nhập**:

```
claude
/mcp     → chọn meta-ads → OAuth trong browser → /mcp lại để xác nhận "connected"
```

Headless/SSH: `claude mcp login meta-ads --no-browser`

**Có gì:** 29 tool chia 5 nhóm — reporting/insights, campaign management, catalog,
account diagnostics, dataset/signal quality (Marketing API v25.0).

### 3.2. TikTok

**TikTok for Business MCP Server** chính chủ gói ~400 endpoint thành tool. Endpoint cấp
theo tài khoản — lấy trong TikTok Ads Manager → Business API / MCP Server:

```bash
./scripts/setup-ads-mcp.sh --skip-meta --tiktok https://<endpoint-cua-ban>
```

Chưa có quyền beta thì có hai đường vòng, đánh đổi khác nhau:

| Cách | Đánh đổi |
| --- | --- |
| Self-host ([AdsMCP/tiktok-ads-mcp-server](https://github.com/AdsMCP/tiktok-ads-mcp-server)) | Tự tạo developer app, tự giữ App ID/Secret, tự chạy OAuth |
| Hosted bên thứ ba (Composio, Ryze…) | Nhanh, nhưng token ad account đi qua hạ tầng của họ |

Với tài khoản tiêu tiền thật: **chính chủ > self-host > bên thứ ba**.

### 3.3. Shopify

```bash
claude mcp add --transport http shopify https://<endpoint> --scope user
```

Shopify MCP cho agent: đơn hàng, sản phẩm + giá, tồn kho theo location, khách hàng,
analytics (ShopifyQL), và GraphQL Admin API cho mọi thứ còn lại.

### 3.4. Kiểm tra

```bash
claude mcp list              # sức khoẻ từng server
claude mcp get meta-ads      # scope, type, URL, trạng thái auth
```

Smoke test — **đọc trước khi ghi**:

```
Liệt kê campaign đang active của ad account <tên>, kèm spend và ROAS 7 ngày qua.
```

Ra số thật là lớp 1 + lớp 2 đã thông.

---

## 4. Cho agent biết unit economics

**Nối Shopify bù được gì:**

| Agent cần biết | Shopify trả lời? |
|---|---|
| Doanh thu thật (không phải số Meta báo) | ✅ |
| Tồn kho — có nên chạy ads cho SKU này không | ✅ |
| Giá bán, variant | ✅ |
| AOV, tỉ lệ mua lại, LTV thô | ✅ qua ShopifyQL |
| **Giá vốn (COGS)** | ⚠️ **chỉ khi "Cost per item" đã điền** |
| Phí ship thực tế mỗi đơn | ❌ thường không quy về từng đơn |
| Phí thanh toán, tỉ lệ hoàn/chargeback | ❌ |
| **Break-even ROAS** | ❌ không nền tảng nào tự suy ra được |

Nên **nối Shopify là đúng hướng nhưng chưa đủ**. Phần còn lại đưa vào một file để agent
đọc — repo có sẵn template:

```bash
cp docs/unit-economics.example.yml docs/unit-economics.yml
# điền số thật, rồi mở đầu mỗi session:
```

```
Đọc docs/unit-economics.yml. Dùng break_even_roas trong đó làm ngưỡng đánh giá,
KHÔNG tự suy ra ROAS mục tiêu từ dữ liệu Meta.
```

**Công thức:**

```
contribution_margin = 1 − (cogs% + ship% + payment_fee% + refund%)

break_even_roas     = 1 / contribution_margin
target_roas         = 1 / (contribution_margin − lãi_mong_muốn%)
```

Ví dụ COGS 30%, ship 12%, phí 2.9%, hoàn 5% → CM = 0.501 →
**break-even ROAS 2.00**, muốn lãi 15% doanh thu → **target ROAS 2.85**.

Con số này đổi toàn bộ cách đọc report: ROAS 1.8 không phải "cần tối ưu thêm", nó là
**đang lỗ**. Không có file này, agent sẽ khen một campaign đang đốt tiền.

> Không biết chắc một khoản? **Đoán cao lên.** Đoán thấp làm break-even ROAS đẹp giả
> tạo và bạn scale thẳng vào lỗ.

---

## 5. Quy trình lên ads thật bằng chat

MCP cho bạn tool, không cho bạn quy trình. Chuỗi tool luôn theo thứ tự này:

```
create_campaign  →  create_adset  →  create_creative  →  create_ad  →  (người duyệt)  →  bật
   objective          budget            ảnh/video          ghép lại        review          ACTIVE
   + daily cap        + audience        + copy
                      + placement
```

Prompt mẫu:

```
Đọc docs/unit-economics.yml trước.

Lên một campaign Meta test cho <tên sản phẩm>, thị trường <US/EU/VN>:
- Objective: Sales (conversion), pixel <id>, event Purchase
- Ngân sách: $20/ngày ở cấp ad set, KHÔNG dùng CBO
- 1 campaign, 2 ad set (broad 18-65 vs interest <...>), mỗi ad set 2 ad
- Creative: file trong <đường dẫn>, copy từ <file .md>
- Đặt tên: <ngày>_<sp>_<thị trường>_<góc content>_<biến thể>

Để TẤT CẢ ở PAUSED. Tạo xong in bảng: tên, cấp, id, ngân sách, audience,
kèm break-even ROAS của sản phẩm này. KHÔNG bật cái nào.
```

Ba chi tiết khiến prompt này chạy được còn prompt chung chung thì không:

1. **Nói rõ ngân sách ở cấp nào** — không nói thì agent hay chọn CBO, test bị nhiễu.
2. **Chuẩn đặt tên** — không có thì một tuần sau bạn không đọc nổi report.
3. **Câu "KHÔNG bật cái nào"** — nhắc lại cả khi platform vốn đã tạo ra PAUSED.

Repo có sẵn skill hỗ trợ: `ads-copy` (primary text/headline theo tầng TOFU-MOFU-BOFU),
`meta-ads-analyzer-mod-by-noti` (đọc số, xử lý Breakdown Effect). Viết copy trước, lên
ads sau — đừng để agent vừa nghĩ copy vừa gọi API trong cùng một lượt.

---

## 6. Đường Telegram

Hợp khi muốn **lên/sửa ads từ điện thoại** hoặc cả team ra lệnh trong một group.

```
Bạn nhắn trong Telegram
   → Bot (BotFather cấp token)
      → n8n: Telegram Trigger → AI Agent (Claude) → MCP/HTTP Request → Meta API
         → n8n trả kết quả + nút xác nhận về lại chat
```

**Điều kiện thêm:** bot token từ [@BotFather](https://t.me/BotFather) · n8n (cloud hoặc
self-host) · **danh sách `chat_id` được phép**.

Workflow: `Telegram Trigger` → `IF` (**chặn ở đây**: chỉ đi tiếp nếu `chat_id` trong
whitelist) → `AI Agent` có MCP Client tool → `Telegram` trả bảng tóm tắt kèm inline
button **Xác nhận bật / Huỷ**. Chỉ nhánh callback của nút mới được đổi status sang ACTIVE.

Telegram **không** có phân quyền cho bot — whitelist `chat_id` là lớp bảo vệ duy nhất.
Coi token bot như mật khẩu ad account.

---

## 7. Đường Lark (Feishu)

Hợp hơn Telegram khi cần **quy trình duyệt của team** và nơi lưu lịch sử.

```
Lark Base = bảng brief campaign (sp, thị trường, ngân sách, góc content, trạng thái)
   → đổi trạng thái sang "Chờ lên"
      → Lark automation / n8n đọc record
         → agent lên ads (MCP như mục 3)
            → ghi id campaign + kết quả ngược lại Base
               → bot Lark báo vào group, kèm nút duyệt
```

Hơn hẳn chat thuần: brief có cấu trúc, không phụ thuộc việc bạn gõ đủ ý trong một tin
nhắn, và mọi campaign đều có một dòng lịch sử.

**Điều kiện thêm:** app ở [Lark Open Platform](https://open.larksuite.com) đã bật Bot ·
scope đọc/ghi Bitable + gửi tin nhắn · app đã publish vào workspace · App ID + App Secret.

Nhận lệnh — chọn một: *Event Subscription* → webhook về n8n (hai chiều đầy đủ), hoặc
*Custom Bot webhook* (một chiều, chỉ để báo kết quả — đơn giản hơn nhiều).

Để Claude đọc/ghi Lark, dùng MCP chính chủ [`larksuite/lark-openapi-mcp`](https://github.com/larksuite/lark-openapi-mcp):

```bash
claude mcp add lark -- npx -y @larksuiteoapi/lark-mcp mcp -a <APP_ID> -s <APP_SECRET>
```

Sau bước này một session Claude Code có **cả hai phía**: `lark` đọc brief từ Base và ghi
kết quả về, `meta-ads`/`tiktok-ads` lên campaign, `shopify` cấp dữ liệu kinh doanh.

---

## 8. Guardrails bắt buộc

Không thương lượng. Mỗi dòng là một cách đã có người mất tiền:

- [ ] **Luôn tạo ở PAUSED.** Bật là hành động của con người, tách hẳn khỏi việc tạo.
- [ ] **Whitelist ad account id.** Agent chỉ được đụng đúng account đó.
- [ ] **Trần ngân sách cứng** ở cấp ad set. Không CBO cho campaign test.
- [ ] **Whitelist người ra lệnh** (`chat_id` Telegram / user Lark).
- [ ] **Agent không được tăng ngân sách.** Giảm và pause thì ok, tăng thì không.
- [ ] **Không kết luận thắng/thua** khi chưa qua learning phase và chưa đủ số purchase tối thiểu.
- [ ] **Log mọi tool call** đụng tới tiền — ai, lúc nào, đổi gì.
- [ ] **Ad account phụ để test.** Chạy thử toàn bộ luồng ở $1/ngày trước.
- [ ] **Không commit** token bot, App Secret, access token, `unit-economics.yml`.
- [ ] **Đọc trước, ghi sau.** Tuần đầu chỉ cho xem báo cáo.

---

## 9. So sánh nhanh

| | Claude Code + MCP | Telegram | Lark |
| --- | --- | --- | --- |
| Thời gian dựng | ~15 phút | vài giờ | nửa ngày đến 1 ngày |
| Hạ tầng thêm | không | n8n | n8n + Lark app |
| Dùng từ điện thoại | kém | tốt nhất | tốt |
| Nhiều người dùng chung | kém | ổn | tốt nhất |
| Phân quyền / duyệt | không có sẵn | tự làm | có sẵn |
| Lưu lịch sử | transcript session | lịch sử chat | Base + approval |
| Hợp với | một người, làm nhanh | team nhỏ, chạy di động | team có quy trình |

---

## 10. Nên đi đường nào

1. **Trước tiên — điền Cost per item trong Shopify.** Không có nó thì mọi thứ sau đều
   là agent đoán mò về lãi lỗ.
2. **Tuần 1 — Claude Code + MCP, chỉ đọc.** Cắm `meta-ads` + `shopify`, hỏi report.
3. **Tuần 2 — cho tạo, vẫn PAUSED.** Lên thật bằng prompt ở mục 5, tự bật tay. Đây đã
   là ~80% giá trị.
4. **Tuần 3+ — mới gắn Telegram hoặc Lark**, và chỉ khi có nhu cầu thật: chạy từ điện
   thoại (Telegram) hay cần team duyệt (Lark).

Nhảy thẳng vào bước 4 là cách chắc chắn nhất để có một con bot mà bạn không dám tin.

---

## 11. Tham khảo

- Meta: [Ads AI Connectors / MCP chính chủ](https://mcp.facebook.com/ads) · [Marketing API](https://developers.facebook.com/docs/marketing-api/)
- TikTok: [TikTok for Business MCP Server](https://business-api.tiktok.com/portal/docs/tiktok-ads-mcp-server/v1.3) · [Campaign Management](https://business-api.tiktok.com/portal/docs?id=1735713781404673)
- Lark: [lark-openapi-mcp](https://github.com/larksuite/lark-openapi-mcp) · [Open Platform](https://open.larksuite.com)
- Telegram: [BotFather](https://t.me/BotFather) · [Bot API](https://core.telegram.org/bots/api)
- Claude Code: [Kết nối MCP](https://code.claude.com/docs/en/mcp) · [GemPages MCP trong repo này](./gempages-mcp.md)

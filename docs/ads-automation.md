# Lên ads bằng chat: MCP, Telegram, Lark

Tài liệu này trả lời câu hỏi: *"làm sao để ngồi trong một khung chat và bảo nó lên
campaign?"* — bằng MCP ngay trong Claude Code, bằng bot Telegram, hoặc bằng bot Lark.

> **Cảnh báo trước khi đọc tiếp:** lên ads là tiêu tiền thật. Mọi thứ dưới đây đều
> phải chạy kèm guardrails ở [mục 5](#5-guardrails-bắt-buộc). Đừng bao giờ để một
> agent vừa tạo vừa bật campaign mà không có người bấm duyệt.

---

## 0. Hiểu đúng kiến trúc trước đã

Đây là chỗ 90% người mới hiểu sai. "Lên ads bằng Telegram" không phải là một tính
năng — nó là 3 lớp ghép lại:

```
Lớp 3  GIAO DIỆN CHAT      Claude Code  |  Telegram bot  |  Lark bot
                                    |
Lớp 2  BỘ NÃO (AGENT)      Claude / n8n / server tự viết
                                    |
Lớp 1  QUYỀN VÀO API ADS   Meta Marketing API  |  TikTok Business API
```

- **Lớp 1 là lớp khó và bắt buộc.** Không có quyền vào ad account thì không channel
  nào lên được ads. Đây là chỗ tốn thời gian nhất.
- **Lớp 2 là nơi ra quyết định** — đọc brief, chọn audience, viết copy, gọi API.
- **Lớp 3 chỉ là cái cửa sổ.** Telegram và Lark **không** lên ads; chúng chỉ chuyển
  tin nhắn của bạn xuống lớp 2.

Hệ quả thực tế: **làm lớp 1 + 2 chạy được trong Claude Code trước**, rồi mới gắn
Telegram/Lark vào sau. Ngược lại là tự làm khổ mình.

---

## 1. Nhanh nhất: MCP ngay trong Claude Code

Đây là đường ngắn nhất từ 0 đến "lên được campaign đầu tiên" — thường dưới 15 phút,
vì cả Meta lẫn TikTok giờ đều có MCP server chính chủ, không cần tự viết code gọi API.

### 1.1. Meta (Facebook / Instagram)

Meta mở **Ads AI Connectors** ở open beta từ 29/04/2026: một remote MCP server
chính chủ tại `https://mcp.facebook.com/ads`, xác thực bằng **OAuth Business** —
không cần developer app, không cần App Review, không cần access token thủ công.

```bash
claude mcp add --transport http meta-ads https://mcp.facebook.com/ads --scope user
```

Hoặc dùng script kèm repo (đăng ký cả Meta lẫn TikTok trong một lệnh):

```bash
./scripts/setup-ads-mcp.sh
```

Rồi xác thực — **thêm URL chưa phải là đăng nhập**:

```
claude
/mcp          → chọn meta-ads → OAuth trong browser → /mcp lại để xác nhận "connected"
```

Không có browser (SSH/headless): `claude mcp login meta-ads --no-browser`

**Cần có:** một ad account mà bạn có role **advertiser hoặc admin** trong Business
Manager. Không đủ role thì OAuth xong tool vẫn trả về rỗng.

**Có gì:** 29 tool chia 5 nhóm — reporting/insights, campaign management, catalog,
account diagnostics, dataset/signal quality (trên nền Marketing API v25.0).

**Điểm quan trọng:** campaign tạo qua MCP ra ở trạng thái **PAUSED**. Phải có người
bật lên thì mới tiêu tiền. Đây là guardrail có sẵn — đừng tự tay gỡ nó đi.

### 1.2. TikTok

TikTok cũng có **TikTok for Business MCP Server** chính chủ, gói khoảng 400 endpoint
của Business API thành tool: tạo/sửa/pause campaign và ad group, upload video, tạo
ad, audience targeting, báo cáo.

Endpoint được cấp theo tài khoản, lấy trong **TikTok Ads Manager → Business API /
MCP Server** (xem [docs TikTok](https://business-api.tiktok.com/portal/docs/tiktok-ads-mcp-server/v1.3)),
rồi:

```bash
./scripts/setup-ads-mcp.sh --tiktok https://<endpoint-tiktok-cua-ban>
# tương đương:
claude mcp add --transport http tiktok-ads https://<endpoint> --scope user
```

Nếu chưa được cấp quyền beta, có hai đường vòng:

| Cách | Đánh đổi |
| --- | --- |
| Server cộng đồng self-host ([AdsMCP/tiktok-ads-mcp-server](https://github.com/AdsMCP/tiktok-ads-mcp-server)) | Phải tự tạo developer app, tự giữ App ID/Secret, tự chạy OAuth |
| Bên thứ ba hosted (Composio, Ryze...) | Nhanh, nhưng token ad account của bạn đi qua hạ tầng của họ |

Với tài khoản đang tiêu tiền thật, ưu tiên **chính chủ > self-host > bên thứ ba**.

### 1.3. Kiểm tra

```
claude mcp list                 # sức khoẻ từng server
claude mcp get meta-ads         # scope, type, URL, trạng thái auth
```

Smoke test trong session, đọc trước khi ghi:

```
Liệt kê các campaign đang active của ad account <tên>, kèm spend và ROAS 7 ngày qua.
```

Ra số thật là lớp 1 + lớp 2 đã thông.

---

## 2. Quy trình lên ads thật bằng chat

MCP cho bạn tool, không cho bạn quy trình. Chuỗi tool luôn theo thứ tự này — sai
thứ tự là lỗi:

```
create_campaign  →  create_adset  →  create_creative  →  create_ad  →  (người duyệt)  →  bật
   objective          budget            ảnh/video          ghép lại        review          ACTIVE
   + daily cap        + audience        + copy
                      + placement
```

Prompt mẫu cho một lần lên ads POD/dropship:

```
Lên một campaign Meta test cho sản phẩm <tên sản phẩm>, thị trường <US/EU/VN>:

- Objective: Sales (conversion), pixel <id>, event Purchase
- Ngân sách: $20/ngày ở cấp ad set, KHÔNG dùng CBO
- 1 campaign, 2 ad set (broad 18-65 vs interest <...>), mỗi ad set 2 ad
- Creative: dùng các file trong <đường dẫn>, copy lấy từ <file .md>
- Đặt tên theo chuẩn: <ngày>_<sp>_<thị trường>_<góc content>_<biến thể>

Để TẤT CẢ ở PAUSED. Tạo xong in ra bảng: tên, cấp, id, ngân sách, audience
để tôi review. KHÔNG bật cái nào.
```

Ba chi tiết khiến prompt này chạy được còn prompt chung chung thì không:

1. **Nói rõ ngân sách ở cấp nào** — không nói thì agent hay chọn CBO, test bị nhiễu.
2. **Chuẩn đặt tên** — không có thì một tuần sau bạn không đọc nổi report.
3. **Câu "KHÔNG bật cái nào"** — nhắc lại cả khi platform vốn đã tạo ra PAUSED.

Repo này có sẵn skill hỗ trợ phần content: `ads-copy` (primary text / headline theo
tầng TOFU-MOFU-BOFU), `meta-ads-analyzer-mod-by-noti` (đọc số, chẩn đoán, xử lý
Breakdown Effect). Viết copy trước, lên ads sau — đừng để agent vừa nghĩ copy vừa
gọi API trong cùng một lượt.

---

## 3. Đường Telegram

Telegram hợp khi bạn muốn **lên/sửa ads từ điện thoại** hoặc muốn cả team ra lệnh
trong một group.

### Kiến trúc

```
Bạn nhắn trong Telegram
   → Bot (BotFather cấp token)
      → n8n: Telegram Trigger → AI Agent (Claude) → MCP/HTTP Request → Meta API
         → n8n trả kết quả + nút xác nhận về lại chat
```

### Các bước

1. **Tạo bot:** chat với [@BotFather](https://t.me/BotFather) → `/newbot` → lấy token.
2. **Dựng n8n** (cloud hoặc self-host). Thêm credential Telegram bằng token trên.
3. **Workflow:**
   - `Telegram Trigger` — nhận message.
   - `IF` — **chặn ngay ở đây**: chỉ đi tiếp nếu `chat_id` nằm trong whitelist.
     Bot Telegram public theo mặc định; thiếu bước này là ai cũng tiêu tiền của bạn được.
   - `AI Agent` (model Claude) — có MCP Client tool trỏ tới Meta/TikTok MCP.
   - `Telegram` — trả bảng tóm tắt kèm inline button **Xác nhận bật / Huỷ**.
   - Nhánh callback của nút mới thực sự gọi tool đổi status sang ACTIVE.
4. **Test bằng ad account phụ, ngân sách $1/ngày**, trước khi đụng account chính.

### Cần biết

- Telegram **không** có khái niệm phân quyền cho bot — whitelist `chat_id` là lớp
  bảo vệ duy nhất. Coi token bot như mật khẩu ad account.
- Đừng cho agent quyền đổi ngân sách qua chat. Tạo và pause: ok. Tăng budget: người làm.

---

## 4. Đường Lark (Feishu)

Lark hợp hơn Telegram khi bạn cần **quy trình duyệt của cả team** và một nơi lưu
lịch sử — vì Lark có Base (bảng dữ liệu) và approval flow sẵn.

### Kiến trúc hay dùng nhất

```
Lark Base = bảng brief campaign (sp, thị trường, ngân sách, góc content, trạng thái)
   → đổi trạng thái sang "Chờ lên"
      → Lark automation / n8n đọc record
         → agent lên ads (MCP như mục 1)
            → ghi id campaign + kết quả ngược lại Base
               → bot Lark báo vào group, kèm nút duyệt
```

Cách này hơn hẳn chat thuần: brief có cấu trúc, không phụ thuộc vào việc bạn gõ đủ
ý trong một tin nhắn, và mọi campaign đều có một dòng lịch sử.

### Các bước

1. **Tạo app** ở [Lark Open Platform](https://open.larksuite.com) → bật **Bot**.
2. Cấp scope: đọc/ghi Bitable, gửi tin nhắn. Publish app vào workspace.
3. **Nhận lệnh** — chọn một:
   - *Event Subscription* → webhook về n8n (chat hai chiều đầy đủ), hoặc
   - *Custom Bot webhook* (một chiều, chỉ để bot báo kết quả — đơn giản hơn nhiều).
4. **Để Claude đọc/ghi Lark:** dùng MCP chính chủ của Lark —
   [`larksuite/lark-openapi-mcp`](https://github.com/larksuite/lark-openapi-mcp),
   gói gần như toàn bộ Open API (message, Bitable, doc, calendar) thành tool.

   ```bash
   claude mcp add lark -- npx -y @larksuiteoapi/lark-mcp mcp \
     -a <APP_ID> -s <APP_SECRET>
   ```

   Sau bước này, trong một session Claude Code bạn có **cả hai phía**: `lark` để đọc
   brief từ Base và ghi kết quả về, `meta-ads`/`tiktok-ads` để lên campaign.

5. **Duyệt:** dùng approval flow của Lark cho bước bật ACTIVE, thay vì tin nhắn thường.

---

## 5. Guardrails bắt buộc

Không thương lượng. Mỗi dòng ở đây đều là một cách đã có người mất tiền:

- [ ] **Luôn tạo ở PAUSED.** Việc bật là hành động của con người, tách hẳn khỏi việc tạo.
- [ ] **Whitelist ad account id** trong config. Agent chỉ được đụng đúng account đó.
- [ ] **Trần ngân sách cứng** ở cấp ad set. Không dùng CBO cho campaign test.
- [ ] **Whitelist người ra lệnh** (`chat_id` Telegram / user Lark).
- [ ] **Agent không được tăng ngân sách.** Giảm và pause thì ok, tăng thì không.
- [ ] **Log mọi tool call** có đụng tới tiền — ai, lúc nào, đổi gì.
- [ ] **Ad account phụ để test.** Chạy thử toàn bộ luồng ở $1/ngày trước.
- [ ] **Không commit** token bot, App Secret, access token. `.env` đã nằm trong `.gitignore`.
- [ ] **Đọc trước, ghi sau.** Tuần đầu chỉ cho agent xem báo cáo. Tin được rồi mới cho tạo.

---

## 6. So sánh nhanh

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

## 7. Nên đi đường nào

1. **Tuần 1 — Claude Code + MCP, chỉ đọc.** Cắm `meta-ads`, hỏi report, xem agent
   hiểu account của bạn tới đâu.
2. **Tuần 2 — cho tạo, vẫn PAUSED.** Lên thật bằng prompt ở mục 2, tự bật tay. Đây
   đã là 80% giá trị rồi.
3. **Tuần 3+ — mới gắn Telegram hoặc Lark**, và chỉ khi bạn có nhu cầu thật: cần
   chạy từ điện thoại (Telegram) hay cần cả team duyệt (Lark).

Nhảy thẳng vào bước 3 là cách chắc chắn nhất để có một con bot mà bạn không dám tin.

---

## 8. Tham khảo

- Meta: [Ads AI Connectors / MCP chính chủ](https://mcp.facebook.com/ads) · [Marketing API](https://developers.facebook.com/docs/marketing-api/)
- TikTok: [TikTok for Business MCP Server](https://business-api.tiktok.com/portal/docs/tiktok-ads-mcp-server/v1.3) · [Campaign Management](https://business-api.tiktok.com/portal/docs?id=1735713781404673)
- Lark: [lark-openapi-mcp](https://github.com/larksuite/lark-openapi-mcp) · [Open Platform](https://open.larksuite.com)
- Telegram: [BotFather](https://t.me/BotFather) · [Bot API](https://core.telegram.org/bots/api)
- Claude Code: [Kết nối MCP](https://code.claude.com/docs/en/mcp) · [GemPages MCP trong repo này](./gempages-mcp.md)

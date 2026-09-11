# Meta Ads CLI — quy trình chạy ads từ terminal

Luồng làm việc:

```
ảnh/video trong ads/media  +  bảng creative/copy/URL/UTM (ads/plan.csv)
        │
        ▼  scripts/meta_ads_launch.py  →  gọi Meta Ads CLI chính chủ (`meta`)
campaign + 5 ad set + ads  ──  tất cả ở trạng thái PAUSED
        │
        ▼  verify + preview
kiểm tra status / URL / UTM / pixel tracking / preview thật
        │
        ▼  bạn duyệt
python3 scripts/meta_ads_launch.py activate --yes      # mới bắt đầu tiêu tiền
```

## 1. Công cụ dùng ở đây

| | |
|---|---|
| Công cụ | **Meta Ads CLI** — CLI chính chủ của Meta cho Marketing API |
| Gói PyPI | `meta-ads` (publisher `facebook`), lệnh là `meta` |
| Yêu cầu | Python 3.12+ |
| Tài liệu | https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-cli |

Có một gói cộng đồng trùng tên `meta-ads-cli` (attainmentlabs) ra trước tháng 2/2026, chạy bằng file YAML.
Repo này dùng bản **chính chủ** vì được Meta bảo trì, bám sát Marketing API và có sẵn cờ
`--status PAUSED` ở cả 4 tầng campaign / ad set / creative / ad.

## 2. Cài đặt

```bash
bash scripts/setup-meta-ads-cli.sh
```

Script sẽ: cài `uv` nếu thiếu → `uv tool install meta-ads --python 3.12` → tạo `ads/.env` từ mẫu →
gọi thử API để xác nhận token sống.

Cài tay nếu muốn:

```bash
uv tool install meta-ads --python "$(which python3.12)"   # hoặc: pip install meta-ads
export PATH="$HOME/.local/bin:$PATH"
meta --version
```

> `pip install meta-ads` trên Python do uv quản lý sẽ báo `externally-managed-environment`; dùng `uv tool install`.

## 3. Token và các ID cần có

Tạo **System User** trong Business Manager (Business settings → Users → System users):

1. Add → đặt tên (ví dụ `Ads CLI`) → role **Admin**.
2. Assign assets: ad account, page, pixel (dataset), catalog nếu có.
3. Add vào app ở Meta for Developers với vai trò App Admin.
4. Generate new token, tick các quyền: `ads_management`, `ads_read`, `business_management`,
   `pages_show_list`, `pages_read_engagement`, `pages_manage_ads`, `read_insights`.

Điền vào `ads/.env` (file này đã nằm trong `.gitignore`, không bao giờ commit):

```
ACCESS_TOKEN=EAAG...
AD_ACCOUNT_ID=act_123456789
PAGE_ID=...
PIXEL_ID=...
CONVERSION_DOMAIN=shop-cua-ban.com
```

Lấy ID còn thiếu:

```bash
cd ads
meta ads adaccount list      # AD_ACCOUNT_ID
meta ads page list           # PAGE_ID
meta ads dataset list        # PIXEL_ID  (cần BUSINESS_ID trong .env)
```

> `meta auth status` chỉ kiểm tra **có** token hay không, không kiểm tra token còn sống.
> Muốn chắc thì gọi `meta ads adaccount list`.

## 4. Khai báo chiến dịch

### `ads/campaign.yaml` — campaign + 5 nhóm

Những chỗ hay phải sửa:

- `campaign.objective`: `OUTCOME_SALES` (chuyển đổi), `OUTCOME_TRAFFIC`, `OUTCOME_LEADS`, …
- `campaign.budget_mode`:
  - `CBO` → ngân sách đặt ở `campaign.daily_budget`, **các ad set không được có ngân sách**.
  - `ABO` → campaign không có ngân sách, **mỗi ad set phải có `daily_budget`**.
  - Đặt tiền ở cả hai nơi là lỗi `more than one budget specified`; script chặn trước khi gọi API.
- **Mọi số tiền tính bằng cent**: `30000` = 300.00 theo đơn vị tiền của ad account.
- `adsets`: 5 nhóm, `name` phải trùng với cột `adset` trong `plan.csv`.
  - Targeting đơn giản: `targeting_countries: "VN"`.
  - Targeting phức tạp (interest, custom audience, lookalike, age/gender): viết JSON trong
    `targeting:` hoặc để file riêng rồi trỏ `targeting_file: targeting/as3-interest.json`.
  - Khi tự siết targeting thì đặt `advantage_audience: false`.

### `ads/plan.csv` — bảng creative/copy/URL/UTM

Mỗi dòng là **một ad**. Cột:

| Cột | Bắt buộc | Ý nghĩa |
|---|---|---|
| `adset` | ✔ | Tên nhóm, khớp `campaign.yaml` |
| `ad_name` | ✔ | Tên ad, không trùng nhau |
| `media` | ✔ | Đường dẫn ảnh/video, tương đối so với `ads/` (ví dụ `media/creative-01.jpg`) |
| `body` | ✔ | Primary text |
| `title` | | Headline (nên ≤ 40 ký tự) |
| `description` | | Dòng mô tả dưới headline |
| `cta` | | `SHOP_NOW`, `BUY_NOW`, `LEARN_MORE`, `SIGN_UP`, … |
| `link_url` | | URL đích; bỏ trống thì lấy `defaults.link_url` |
| `utm_*` | | Ghi đè UTM mặc định cho riêng dòng đó |
| `conversion_domain` | | Domain đăng ký cho chuyển đổi, mặc định lấy từ `.env` |
| `url_tags_extra` | | Tham số tracking thêm, ví dụ `fbclid_test=1&aff=abc` |

Ảnh: jpg/png/gif/bmp/webp. Video: mp4/mov/avi/mkv/wmv. File để trong `ads/media/` (đã gitignore).

### UTM

UTM mặc định khai trong `defaults` của `campaign.yaml`, hỗ trợ placeholder:

- `[[campaign]]`, `[[adset]]`, `[[ad]]` — tên nguyên bản
- `[[campaign_slug]]`, `[[adset_slug]]`, `[[ad_slug]]` — bản slug, gọn và dễ đọc trong GA4

Macro động của Meta (`{{ad.id}}`, `{{adset.name}}`, `{{placement}}`…) cứ viết thẳng, script không
mã hoá dấu ngoặc nên Meta vẫn thay được lúc chạy.

## 5. Chạy

```bash
# 1. Soát trước, không tốn một request API nào
python3 scripts/meta_ads_launch.py validate

# 2. Xem đúng những lệnh `meta ads ...` sẽ chạy + URL cuối sau khi gắn UTM
python3 scripts/meta_ads_launch.py plan

# 3. Tạo thật — campaign + 5 ad set + creative + ad, TẤT CẢ PAUSED
python3 scripts/meta_ads_launch.py launch
#    đứt giữa chừng thì chạy tiếp, phần đã tạo được bỏ qua:
python3 scripts/meta_ads_launch.py launch --resume

# 4. Kiểm tra
python3 scripts/meta_ads_launch.py verify     # status, URL, UTM, pixel, conversion_domain
python3 scripts/meta_ads_launch.py preview    # xuất ads/out/previews-<run>.html
python3 scripts/meta_ads_launch.py status     # bảng trạng thái hiện tại

# 5. Duyệt xong mới bật
python3 scripts/meta_ads_launch.py activate --yes

# Phanh gấp
python3 scripts/meta_ads_launch.py pause
```

`verify` kiểm những gì:

- campaign / ad set / ad còn PAUSED (nếu đã ACTIVE thì báo lỗi)
- `promoted_object` và `tracking_specs` có đúng pixel không
- `link_url` + `url_tags` **thực tế trên Meta** có khớp bảng kế hoạch không
- mở URL cuối cùng: HTTP code, URL sau redirect, còn giữ đủ `utm_source/medium/campaign` không
- HTML trang đích có đoạn Meta Pixel và đúng pixel id không
- ghi báo cáo `ads/out/verify-<run>.md` (token luôn bị che trong mọi log/báo cáo)

`preview` gọi endpoint `/{ad_id}/previews` của Graph API (CLI chưa có lệnh preview) và gom iframe
vào một file HTML. **Mở file đó bằng trình duyệt đang đăng nhập Facebook** với tài khoản có quyền
trên ad account thì iframe mới hiện. Đổi khổ preview:

```bash
python3 scripts/meta_ads_launch.py preview --formats MOBILE_FEED_STANDARD,INSTAGRAM_STORY,INSTAGRAM_REELS
```

`activate` luôn chạy `verify` trước, còn lỗi là dừng. Cố tình bỏ qua thì thêm `--skip-verify`.
Thứ tự bật: ad → ad set → campaign; lúc tắt thì làm ngược lại.

## 6. Trạng thái từng lần chạy

Mỗi `launch` ghi `ads/state/<run-id>.json` (và cập nhật `ads/state/latest.json`) chứa toàn bộ ID
campaign / ad set / creative / ad + URL + UTM. Các lệnh sau mặc định dùng lần chạy gần nhất; muốn
chỉ định thì `--run-id <ten-run>`. Thư mục `ads/state/` không commit — ID là dữ liệu tài khoản thật.

## 7. Lỗi hay gặp

| Lỗi | Cách xử |
|---|---|
| `more than one budget specified` | Đặt tiền ở cả campaign lẫn ad set. Chọn CBO **hoặc** ABO. |
| `Dynamic Creative ads can only be created under Dynamic Creative Ad Sets` | Creative DCO phải chạy trên ad set có `dynamic_creative: true`. |
| Ad `PENDING_REVIEW` / `WITH_ISSUES` sau khi activate | Meta đang duyệt, chờ là bình thường. |
| `(#200) Requires ads_management permission` | Token thiếu quyền, tạo lại token system user. |
| `Invalid parameter` khi tạo ad set ở EU | Thiếu `dsa_beneficiary` / `dsa_payor` trong `defaults`. |
| URL mất UTM sau redirect | Trang đích redirect kiểu cắt query; sửa redirect hoặc trỏ thẳng URL cuối. |

## 8. Lệnh CLI gốc hay dùng thêm

```bash
cd ads
meta ads insights get --date-preset last_7d --fields spend,impressions,ctr,cpc,actions
meta ads guidance list                 # gợi ý tối ưu từ Meta
meta ads campaign list --fields name,status,daily_budget
meta ads ad get <AD_ID> --fields name,effective_status,creative,tracking_specs
meta --output json ads adset list <CAMPAIGN_ID>
```

Toàn bộ tuỳ chọn: `meta ads <nhóm lệnh> <lệnh> --help` — phần help của CLI này viết rất kỹ,
có cả ví dụ cho CBO/ABO/flex và Advantage+.

## 9. Nguồn

- [Ads CLI — Meta for Developers](https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-cli/ads-cli-overview)
- [meta-ads trên PyPI (publisher: facebook)](https://pypi.org/project/meta-ads/)
- [meta-ads-cli (bản cộng đồng, attainmentlabs)](https://github.com/attainmentlabs/meta-ads-cli)
- [Bài giới thiệu Ads CLI của PPC Land](https://ppc.land/metas-new-ads-cli-lets-ai-agents-manage-ad-campaigns-from-the-command-line/)

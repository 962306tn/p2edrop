# Quy chuẩn đặt tên file — thư mục Dropship

Áp dụng cho Google Drive `Dropship`
(`https://drive.google.com/drive/folders/14Pz5gD4SHK1QleSjFyTugNbmaN0Jx6su`).

**Nguyên tắc số 1: không đổi tên bất kỳ file nào đang có.** Quy chuẩn này chỉ
áp dụng cho file tạo mới kể từ **2026-09-07**. File cũ được quản lý bằng bảng
đối chiếu (mục 6), không bằng việc rename.

---

## 1. Vì sao cần quy chuẩn

Đọc thực tế thư mục hiện tại, có 6 vấn đề đang phát sinh chi phí:

| Vấn đề | Bằng chứng trong thư mục |
| --- | --- |
| 4 kiểu viết hoa/phân cách song song | `PETGUN-PDP-GRAYSCALE-10-PROMPTS.md`, `WINNING_PRODUCT_RESEARCH_US_2026-09-02.md`, `research_pet_hobby.md`, `competitor-research-pet-odor-gun-2026-09-04.md` |
| Một sản phẩm có 3 tên gọi | `PETGUN…`, `PETODORGUNSTRATEGY.md`, `…pet-odor-gun…` — đều là VelaHush pet odor gun |
| Ngày tháng lúc có lúc không, 2 định dạng | `…-2026-09-04.md` vs `260409_dropship_petgun_descriptionv2.html` vs phần lớn không có ngày |
| Bản sao không phân biệt được | `PETODORGUNSTRATEGY.md`, `_petodor2.md`, `_petodor_copy.md` — **cùng 117.608 bytes**, gần như chắc chắn là 3 bản giống hệt nhau |
| Hậu tố rác do Drive/OS tự sinh | `velahush-brand-v2-minimal 2`, `allvibe-space-brand 2`, `Shrine_1.3.0 (1).zip` |
| Chuỗi vô nghĩa trong tên | `…-10-PROMPTS-73B9F2.md` — không ai giải mã được `73B9F2` sau 2 tuần |

Hệ quả: không sort được theo thời gian, không lọc được theo brand, không biết
file nào là bản mới nhất, và trả lời câu "bản strategy dùng để chạy ads là bản
nào?" mất vài phút mỗi lần.

---

## 2. Cú pháp

```
<brand>_<type>_<slug>_<YYYYMMDD>_v<NN>.<ext>
```

5 trường, **bắt buộc đủ cả 5**, phân cách bằng `_`. Bên trong mỗi trường chỉ
dùng `-`. Toàn bộ viết thường, chỉ `a-z0-9-`.

Vì `_` chỉ xuất hiện giữa các trường nên tên file luôn tách được bằng
`split("_")` — máy đọc được, không cần đoán.

Ví dụ:

```
velahush_prompt_pdp-grayscale-10_20260905_v01.md
velahush_copy_pdp-description_20260904_v02.html
market_research_niche-pet-hobby_20260902_v01.md
footrevive_prompt_pdp-visual-10_20260905_v01.md
zela_audit_theme-speed_20260906_v01.md
```

### 2.1 `brand` — bảng mã đóng

Đây là trường quan trọng nhất: nó ép một sản phẩm chỉ có **một** tên duy nhất.

| Mã | Nghĩa | Tên cũ từng dùng |
| --- | --- | --- |
| `velahush` | Pet odor gun, brand VelaHush | `PETGUN`, `PETODOR`, `pet-odor-gun`, `FreshPaw`, `Zovelle` |
| `footrevive` | FootRevive | `FOOTREVIVE` |
| `theraease` | TheraSpine / TheraEase | `TheraSpine` |
| `allvibe` | AllVibe Space | `allvibe-space` |
| `zela` | Store/theme Zela | `zela-v2` |
| `market` | Nghiên cứu chung, chưa gắn brand nào | `research_*`, `WINNING_PRODUCT_*` |
| `ops` | Vận hành, theme, tooling, tài liệu nội bộ | — |

Thêm brand mới: thêm một dòng vào bảng này **trước** khi đặt tên file đầu tiên.
Mã brand là chữ thường liền, không dấu, không `-`.

### 2.2 `type` — bảng mã đóng

| Mã | Dùng cho |
| --- | --- |
| `research` | Nghiên cứu thị trường, winning product, niche |
| `competitor` | Phân tích đối thủ |
| `strategy` | Chiến lược sản phẩm / angle / positioning |
| `copy` | PDP description, ad copy, email, landing copy |
| `prompt` | Bộ prompt tạo hình ảnh / video |
| `creative` | Kịch bản, storyboard, brief sáng tạo |
| `audit` | Audit theme, tốc độ, UX, tracking |
| `spec` | Yêu cầu kỹ thuật, cấu hình, checklist triển khai |
| `asset` | File nguồn: zip, psd, bộ ảnh đóng gói |
| `report` | Báo cáo số liệu, kết quả test |

Danh sách này cố tình ngắn. Nếu một file không rơi vào mục nào, gần như chắc
chắn nó nên tách nhỏ ra chứ không phải cần thêm `type` mới.

### 2.3 `slug`

2–5 từ mô tả nội dung, nối bằng `-`. Không lặp lại brand hoặc type
(`velahush_prompt_velahush-prompts-…` là sai). Không chứa ngày, không chứa số
version, không chứa hash ngẫu nhiên.

Số lượng thì được giữ nếu nó có nghĩa: `pdp-visual-10`, `animal-character-11-20`.

### 2.4 `YYYYMMDD`

Ngày **tạo bản này**, không phải ngày sửa. Đã đặt rồi thì không đổi — sửa nội
dung thì tăng `v`, hoặc tạo bản mới với ngày mới nếu là làm lại từ đầu.

Dạng liền `20260905` (không `2026-09-05`) để giữ đúng 5 trường khi split.

### 2.5 `vNN`

Hai chữ số, bắt đầu từ `v01`. **Bắt buộc kể cả khi chỉ có một bản.**

Đây là chỗ giải quyết dứt điểm `_copy`, ` 2`, `(1)`, `v2` viết dính vào slug.
Sửa file → lưu thành `v02`, giữ nguyên `v01`. Không bao giờ có hai file cùng
nội dung mà không biết bản nào mới hơn.

Cấm tuyệt đối trong tên file: `final`, `final2`, `new`, `latest`, `copy`,
`bản-cuối`, ` 2`, `(1)`.

---

## 3. Tên thư mục

Cùng cú pháp, bỏ `.<ext>`, và bỏ `vNN` nếu thư mục không có bản thứ hai:

```
<brand>_<type>_<slug>_<YYYYMMDD>[_v<NN>]
```

```
velahush_prompt_pdp-grayscale_20260905
velahush_creative_facebook-ads-animals_20260905_v02
zela_audit_theme_20260906
```

Thư mục hệ thống bắt đầu bằng `_` để luôn nổi lên đầu khi sort:
`_index`, `_archive`, `_inbox`.

---

## 4. Sort ra kết quả gì

Sort theo tên trong Drive sẽ tự động nhóm: **brand → loại tài sản → chủ đề →
thời gian → version**.

```
_INDEX.md
footrevive_prompt_pdp-visual-10_20260905_v01.md
market_research_niche-home_20260902_v01.md
market_research_niche-pet-hobby_20260902_v01.md
market_research_winning-product-us_20260902_v01.md
velahush_competitor_pet-odor-gun_20260904_v01.md
velahush_copy_pdp-description_20260904_v02.html
velahush_prompt_animal-character-11-20_20260905_v01.md
velahush_prompt_pdp-grayscale-10_20260905_v01.md
velahush_strategy_pet-odor-gun_20260903_v03.md
```

Toàn bộ tài sản của một brand nằm liền một khối; trong khối đó các bản của cùng
một file nằm cạnh nhau theo đúng thứ tự thời gian.

---

## 5. Quy tắc chuyển tiếp (điều quan trọng nhất)

1. **Không rename, không xoá, không di chuyển file đang có.** Mọi link Drive,
   mọi prompt, mọi tài liệu đang trỏ tới chúng vẫn chạy nguyên.
2. Từ 2026-09-07, **file mới bắt buộc theo quy chuẩn**.
3. Khi cần cập nhật nội dung một file cũ: **không sửa tên file cũ** — tạo bản
   mới theo quy chuẩn, rồi đánh dấu bản cũ là `superseded` trong `_INDEX.md`.
   Ví dụ: cập nhật `PETODORGUNSTRATEGY.md` → tạo
   `velahush_strategy_pet-odor-gun_20260907_v02.md`.
4. Nếu về sau muốn dọn file cũ: **di chuyển vào `_archive/`, không rename**.
   Drive giữ nguyên file ID khi di chuyển nên mọi link cũ vẫn sống. Đây là việc
   tuỳ chọn, không bắt buộc.
5. `_petodor2.md` và `_petodor_copy.md` (trùng byte với `PETODORGUNSTRATEGY.md`)
   để nguyên, chỉ đánh dấu `duplicate` trong index — không xoá.

---

## 6. `_INDEX.md` — quản lý file cũ mà không đụng vào chúng

Đặt một file `_INDEX.md` ở gốc thư mục `Dropship`. Đây là nơi duy nhất trả lời
"file nào là bản đang dùng". Mỗi dòng là một file cũ, kèm tên chuẩn tương đương
để tra cứu — **tên chuẩn ở đây chỉ là nhãn, không phải lệnh rename**.

```markdown
| Tên file thật (giữ nguyên) | Brand | Type | Tên chuẩn tương đương | Trạng thái |
| --- | --- | --- | --- | --- |
| PETODORGUNSTRATEGY.md | velahush | strategy | velahush_strategy_pet-odor-gun_20260903_v01 | active |
| _petodor2.md | velahush | strategy | (trùng nội dung file trên) | duplicate |
| _petodor_copy.md | velahush | strategy | (trùng nội dung file trên) | duplicate |
| competitor-research-pet-odor-gun-2026-09-04.md | velahush | competitor | velahush_competitor_pet-odor-gun_20260904_v01 | active |
| PETGUN-PDP-GRAYSCALE-10-PROMPTS.md | velahush | prompt | velahush_prompt_pdp-grayscale-10_20260905_v01 | active |
| PETGUN-10-VISUAL-PROMPTS.md | velahush | prompt | velahush_prompt_pdp-visual-10_20260905_v01 | superseded |
| PETGUN-10-VISUAL-PROMPTS-VELAHUSH-BRAND.md | velahush | prompt | velahush_prompt_pdp-visual-10-brand_20260905_v02 | active |
| VELAHUSH-ANIMAL-CHARACTER-10-PROMPTS-11-20.md | velahush | prompt | velahush_prompt_animal-character-11-20_20260905_v01 | active |
| VELAHUSH-COMPETITOR-CONCEPT-10-PROMPTS-73B9F2.md | velahush | prompt | velahush_prompt_competitor-concept-10_20260905_v01 | active |
| FOOTREVIVE-10-VISUAL-PROMPTS.md | footrevive | prompt | footrevive_prompt_pdp-visual-10_20260905_v01 | active |
| WINNING_PRODUCT_RESEARCH_US_2026-09-02.md | market | research | market_research_winning-product-us_20260902_v01 | active |
| research_home.md | market | research | market_research_niche-home_20260902_v01 | active |
| research_pet_hobby.md | market | research | market_research_niche-pet-hobby_20260902_v01 | active |
| research_personal.md | market | research | market_research_niche-personal_20260902_v01 | active |
| 260409_dropship_petgun_descriptionv2.html | velahush | copy | velahush_copy_pdp-description_20260904_v02 | active |
```

Trạng thái dùng đúng 3 giá trị: `active`, `superseded`, `duplicate`.

Chi phí: viết một lần ~15 phút. Đổi lại, không phải nhớ `PETGUN` và `PETODOR`
là cùng một sản phẩm nữa.

---

## 7. Hai việc nên làm kèm

- **Gộp hai thư mục trùng tên.** Đang có cả `Dropship` (workspace thật) và
  `dropship` (chỉ 1 file mp4, gần như rỗng). Chuyển file mp4 sang `Dropship` rồi
  xoá thư mục rỗng — tránh việc lần sau tìm nhầm chỗ.
- **Đổi tên ảnh khi tải về.** Các file `img_v3_02157_03c534ae-….jpg` là tên do
  công cụ sinh, không tra ngược được. Ảnh mới nên vào một thư mục đúng chuẩn
  (`velahush_asset_pdp-photo_20260907`) và đánh số trong đó: `01.jpg`, `02.jpg` —
  ngữ cảnh nằm ở tên thư mục, không cần nhồi vào tên từng ảnh.

---

## 8. Kiểm tra tên trước khi lưu

```bash
scripts/check-dropship-name.sh velahush_prompt_pdp-grayscale-10_20260905_v01.md
```

Script trả về mã lỗi khác 0 và chỉ rõ trường nào sai. Xem `scripts/check-dropship-name.sh`.

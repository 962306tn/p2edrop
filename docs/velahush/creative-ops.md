# VelaHush — Vận hành kho creative
**Kho hiện có:** 95 ảnh TOF · 120 video TOF · 20 video TOF test format · 20 ảnh MOF · 2 ảnh BOF = **257 asset**

---

## 1. Con số bạn cần nhìn trước

**Kho của bạn lớn hơn budget khoảng 26 lần.**

| | |
|---|---|
| Asset TOF | **235** (95 ảnh + 140 video) |
| Ngân sách TOF | $60/ngày |
| Chi phí để "đọc" được 1 creative | ~$20 (đủ ~1.000 impression + vài chục click) |
| Tiền cần để chạm mỗi asset đúng 1 lần | **$4.700** = 78 ngày tiêu hết budget, chưa tối ưu gì |
| Mỗi tuần chạy được | **9 ads TOF** (ma trận 3 nguồn × 3 angle) |
| Kho đủ dùng trong | **~26 tuần** |

> **Kết luận: đừng "lên" đống nội dung này. Nó không phải thứ để deploy — nó là hàng đợi để rút.**
> Việc nhàn nhất không phải upload 257 file, mà là xây một cơ chế để mỗi tuần bạn biết chính xác 9 cái nào lên tiếp, tốn 20 phút.

Upload hết 257 file vào Media Library còn phản tác dụng: UI tự phát preview, cuộn không nổi, và bạn sẽ mất nhiều thời gian tìm file hơn là dựng ad. **Upload theo wave, 12–15 file/tuần.**

---

## 2. Cơ chế: đặt tên 1 lần, sau đó chạy bằng script

Repo có sẵn 2 script ở `scripts/velahush/`. Toàn bộ việc thủ công gói lại còn: **kéo file vào đúng thư mục.**

### Bước 1 — xếp file vào cây thư mục (làm 1 lần, ~30 phút)

```
raw/
  TOF/
    OWN/  7R/  MRC/  BSC/     ← video Topview + content tự tạo
    IMG/  7R/  MRC/  BSC/     ← 95 ảnh
    VID/  7R/  MRC/  BSC/     ← 120 video
  MOF/OWN/MECH/               ← 20 ảnh MOF
  BOF/OWN/OFFER/              ← 2 ảnh BOF
```

Tên thư mục **chính là tag**. Bạn không phải đặt tên file, không phải điền spreadsheet — chỉ kéo thả vào đúng 1 trong 11 thư mục.

**Cách phân loại nhanh 235 asset mà không xem hết:** đừng chấm điểm, chỉ phân loại. Nhìn frame đầu ở cỡ thumbnail, hỏi 1 câu: *cái này đang nói về mùi quay lại (7R), về đón khách (MRC), hay về chai xịt (BSC)?* Ném vào thư mục tương ứng. ~3 giây/asset → **235 asset trong ~20 phút.** Cái nào không rõ thuộc angle nào thì nó cũng không rõ với khách — để riêng, dùng sau cùng.

### Bước 2 — chạy script đổi tên + tạo manifest (1 lệnh)

```bash
python3 scripts/velahush/organize_creatives.py --root ~/velahush/raw          # xem trước
python3 scripts/velahush/organize_creatives.py --root ~/velahush/raw --apply  # chạy thật
```

Ra: file được đổi tên `TOF_VID_7R_001.mp4`, `TOF_IMG_MRC_014.jpg`… + `manifest.csv` ghi trạng thái từng asset.

Tên file này khớp đúng quy ước trong `campaign-plan.md` mục 7, nên sau khi upload lên Media Library bạn **gõ tên vào ô search** thay vì cuộn tìm.

### Bước 3 — mỗi tuần rút 1 wave (1 lệnh, ~10 giây)

```bash
python3 scripts/velahush/make_wave.py --manifest ~/velahush/raw/manifest.csv --wave 1 --apply
```

Ra `wave-1.csv` gồm 13 dòng — mỗi dòng đã có sẵn tên ad, file creative, URL advertorial đúng angle, headline, description, CTA. **Cột khớp với `build-sheet.csv`, paste thẳng vào là xong.**

Script tự đánh dấu asset đã dùng, nên tuần sau chạy `--wave 2` sẽ ra 9 cái khác, không trùng. Nó cũng báo nếu có ô nào trong ma trận 3×3 bị rỗng.

---

## 3. Luật rút wave — cái quyết định hiệu quả

**Chỉ thay đứa thua. Không bao giờ thay đứa thắng.**

| Tuần | Cách làm |
|---|---|
| W1 | Chạy full 9 ads từ `wave-1.csv` |
| W2 | Giữ nguyên ad thắng (mở `manifest.csv`, sửa `status` của nó thành `winner` → script không rút lại). Chạy `--wave 2`, chỉ lấy đủ số ad để lấp chỗ đứa thua |
| W3+ | Lặp lại |

Sau vài tuần bạn sẽ ở trạng thái kiểu 4 winner + 5 ad mới mỗi tuần. Kho rút chậm dần, và lúc nào bạn cũng đang chạy những cái tốt nhất từng có — thay vì rải đều 257 asset và không cái nào đủ tiền để chứng minh gì.

**Định nghĩa "thua" (đọc ngày 5–7):** tiêu < 1/3 mức trung bình của các ad cùng ad set, hoặc hook rate < 20%, hoặc outbound CTR < 1%.

---

## 4. 20 video "testing format" — tách riêng, đừng trộn

Đây là biến khác (format/tỉ lệ/cấu trúc hook), không phải angle. Trộn vào ma trận 3×3 sẽ làm bạn không biết kết quả đến từ nguồn creative hay từ format.

Ở $100/ngày bạn **không đủ tiền chạy một test format riêng.** Cách xử lý thực tế:
- Chọn 3 cái mạnh nhất, xếp vào `TOF/OWN/<angle>` như creative bình thường
- 17 cái còn lại: để nguyên trong thư mục riêng, không import vào manifest
- Khi nào budget lên ≥ $300/ngày thì mở test format riêng

---

## 5. Kho MOF và BOF — không có việc gì phải làm

| | Có | Cần/tuần | Đủ dùng |
|---|---|---|---|
| MOF | 20 ảnh | 3 ads | ~7 tuần, hoặc gộp 6 ảnh/carousel → 3 carousel |
| BOF | 2 ảnh | 1 ad | 1 chạy + 1 luân phiên khi frequency > 4 — **vừa đủ, đúng nhu cầu** |

BOF 2 ảnh là con số đúng, không cần thêm. Chỉ cần điền số offer + deadline (đang là `[XX]%` / `[DATE]` trong file copy).

---

## 6. Tổng thời gian tay chân

| Việc | Tần suất | Thời gian |
|---|---|---|
| Xếp 235 asset vào 11 thư mục | 1 lần | ~20 phút |
| Chạy `organize_creatives.py` | 1 lần | 10 giây |
| Chạy `make_wave.py` | mỗi tuần | 10 giây |
| Upload 12–15 file lên Media Library | mỗi tuần | ~5 phút |
| Duplicate ad + swap creative theo `wave-N.csv` | mỗi tuần | ~15 phút |
| Đánh dấu winner trong `manifest.csv` | mỗi tuần | ~2 phút |

**Setup 1 lần: ~25 phút. Sau đó ~22 phút/tuần.**

---

## 7. Lưu ý còn treo

- **95 ảnh + 120 video TOF nếu lấy từ Ad Library đối thủ:** rủi ro bản quyền ở ảnh static nặng hơn video nhiều (xem `campaign-plan.md` mục 5). Nên dùng làm layout reference và dựng lại bằng sản phẩm mới, ít nhất với những cái lọt vào wave.
- **Mọi asset vẫn phải qua rào testimonial** (`page-strategy.md` mục 2): AI được trình bày, không được làm chứng.
- **Sản phẩm cũ vs mới:** video nào còn shot hero sản phẩm cũ thì cắt, 3–4s cuối thay bằng sản phẩm mới. Làm lúc rút wave, không làm trước cho cả 235 cái.

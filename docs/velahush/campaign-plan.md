# VelaHush — Meta Ads Campaign Setup Plan (v2)
**Ngày:** 10/09/2026 · **Budget:** $100/ngày · **Market:** US (EN) · **Objective:** Sales / Purchase
**v2 thay đổi:** chuyển sang cấu trúc CBO tách theo **nguồn creative** theo đề xuất của bạn. Xem mục 1.

---

## 1. Đính chính v1 — bạn đúng, và bạn sai một chỗ khác

**Bạn đúng:** tôi nói 3 nhóm TOF broad sẽ overlap đấu giá với chính mình. Điều đó đúng với **ABO**. Với **CBO thì không** — Meta dedup ở cấp auction giữa các ad set trong cùng một CBO campaign, nên nó không tự đẩy giá của chính nó. Việc bạn chọn CBO chính là cách xử lý đúng cho vấn đề tôi nêu. Bỏ phản đối đó.

**Và tách theo *nguồn creative* khác hẳn tách theo *angle*.** Ba nguồn (video mình tự tạo / ảnh đối thủ / video đối thủ) có CPM, hook rate, tỉ lệ chuyển đổi khác nhau về bản chất — đó là biến đáng tách nhóm thật. v1 tách theo advertorial mới là cách tách vô nghĩa.

**Chỗ còn lại:** **CBO không tôn trọng tỉ lệ 60/30/10 của bạn.** CBO được thiết kế để dồn tiền vào ad set nào ra chuyển đổi rẻ nhất. Ngày 1 TOF luôn rẻ nhất (tệp lớn, chưa bão hoà) → CBO sẽ bóp MOF và BOF xuống $2–3/ngày và bạn mất luôn tầng giữa. Ép bằng min/max spend limit thì được, nhưng đó là đánh nhau với thuật toán và Meta cảnh báo trực tiếp là nó làm giảm hiệu quả delivery.

**CBO + tỉ lệ cố định là hai thứ mâu thuẫn nhau về mặt cấu trúc.** Cách thoát: đặt CBO ở đúng chỗ nó giỏi (so sánh 3 nguồn creative với nhau) và khoá tỉ lệ ở cấp **campaign**.

---

## 2. Cấu trúc — 3 campaign, 5 ad set

```
Campaign 1 · VH | TOF | CBO | $60/ngày          ← CBO ở đây, đúng chỗ
  ├─ AS1  TOF-OWN   Video Topview + content tự tạo      3 ads → advertorial
  ├─ AS2  TOF-IMG   Ảnh đối thủ (RECREATE, xem mục 5)   3 ads → advertorial
  └─ AS3  TOF-VID   Video đối thủ (re-edit)             3 ads → advertorial

Campaign 2 · VH | MOF | ABO | $30/ngày
  └─ AS4  MOF-WARM  3 ads (1 carousel + 2 static) → PDP

Campaign 3 · VH | BOF | ABO | $10/ngày
  └─ AS5  BOF-RTG   1 ad → PDP + discount code
```

**Vì sao tách 3 campaign:** budget nằm ở cấp campaign nên **60/30/10 được khoá cứng** — MOF và BOF không thể bị TOF hút mất tiền. Trong Campaign 1, CBO vẫn tự do phân bổ giữa 3 nguồn creative, đúng như bạn muốn. Bạn được cả hai thứ, không phải chọn một.

> Nếu bạn vẫn muốn **1 campaign CBO duy nhất** cho cả 5 ad set: bắt buộc phải set ad set spend limit (AS1–3 max $22/ad set; AS4 min $25; AS5 min $8). Chấp nhận delivery kém hơn. Tôi không khuyên, nhưng nó chạy được.

### Setting chi tiết

**Campaign 1 — `VH | TOF | CBO | US | 2026-09`**
| | |
|---|---|
| Budget | **$60/ngày, Advantage campaign budget BẬT** |
| Objective | Sales · Purchase · Website |
| Bid strategy | Highest volume, không bid cap |
| **Ad set spend limit (ngày 1–5)** | **Minimum $15/ad set** trên cả AS1, AS2, AS3 |
| Ad set spend limit (từ ngày 6) | **Gỡ hết** |
| Audience (cả 3 ad set) | Advantage+ Audience, US, 18–65+, all genders, để trống suggestion |
| Exclude (cả 3) | Website visitors 30d · Purchasers 180d |
| Placements | Advantage+ Placements |
| Page identity | **Creator Page** (xem `page-strategy.md`) |
| Attribution | 7-day click, 1-day view |

> **Min spend $15 trong 5 ngày đầu là bắt buộc.** Không có nó, CBO sẽ chọn người thắng trong 24h dựa trên dữ liệu gần như bằng 0, bóp AS2 và AS3 xuống $3/ngày, và bạn **không bao giờ biết được** nguồn creative nào thực sự tốt. $15 × 5 ngày = $75/nguồn, đủ để đọc directional. Ngày 6 gỡ ra cho CBO tự do.

**Campaign 2 — `VH | MOF | ABO | US | 2026-09`** · $30/ngày
- Audience từ ngày 5: Video viewers 25% (90d) + Page engagers 180d (cả 2 page) + IG engagers 180d + Website visitors 30d + LAL 1–3%
- Audience ngày 1–4: Broad + Advantage+ (pool warm chưa tồn tại)
- Exclude: ATC 14d · IC 14d · Purchasers 180d
- Page identity: **Brand Page**, hoặc **Partnership Ad (Brand × Creator)** khi có video creator
- Destination: PDP trực tiếp

**Campaign 3 — `VH | BOF | ABO | US | 2026-09`** · $10/ngày · **OFF đến ngày 5**
- Audience: ATC 14d + IC 14d + PDP viewers 7d + Advertorial readers 14d (URL contains `velahush`)
- Exclude: Purchasers 180d
- Page identity: **Brand Page**
- **1 ad thôi.** Bạn ghi "1 ảnh, 1 video gì đấy" — $10 chia 2 ad = $5/ad, không ad nào đủ dữ liệu. Chạy 1 static, để video làm bản luân phiên khi frequency > 4.

---

## 3. Ma trận creative — 3 nguồn × 3 angle

Bạn nói "tự pitch sau nhưng lẫn lộn" — tôi hiểu là **mỗi ad set chứa đủ cả 3 advertorial**, để biến duy nhất giữa các ad set là *nguồn creative*. Đúng thiết kế thí nghiệm. Cụ thể:

| | **7R** · mùi quay lại | **MRC** · đón khách | **BSC** · vấn đề ở chai xịt |
|---|---|---|---|
| **AS1 · OWN** | `TOF1_OWN_7R` ⭐ hero | `TOF1_OWN_MRC` | `TOF1_OWN_BSC` |
| **AS2 · IMG** | `TOF2_IMG_7R` | `TOF2_IMG_MRC` | `TOF2_IMG_BSC` |
| **AS3 · VID** | `TOF3_VID_7R` | `TOF3_VID_MRC` | `TOF3_VID_BSC` |

**9 ads TOF + 3 MOF + 1 BOF = 13 ads.**
Tỉ lệ theo *ngân sách* = đúng 60/30/10. Theo *số creative* = 69/23/8 — lệch nhẹ so với mục tiêu, và tôi cho là nên chấp nhận: TOF là nơi cần volume để tìm winner, ép về đúng 6 ad chỉ để cho tròn số sẽ làm mỏng ma trận.

### ⚠️ Ma trận này KHÔNG đọc được bằng thống kê ở mức $60/ngày
$60 / 9 ads ≈ $6.7/ad/ngày. Với CPM ~$20 và CTR 1.5% thì mỗi ô được ~5 click/ngày — cần 10+ ngày mới đủ mẫu cho một ô. Đừng cố đọc 9 ô.

**Cách đọc đúng ở budget này:** chính việc CBO **dồn tiền vào đâu** mới là tín hiệu.
- Ngày 3–5: ad set nào chiếm nhiều share nhất → **nguồn creative thắng**
- Trong ad set đó: ad nào ăn tiền nhất → **angle thắng**
- Ngày 6–7: gỡ min spend, tắt 2 nguồn thua, nhân bản nguồn thắng thành 3–4 variant mới cùng angle thắng

Đây là đọc directional, không phải kết luận thống kê. Ở $100/ngày thì directional là thứ tốt nhất mua được — và nó đủ để ra quyết định.

---

## 4. Lịch ngân sách theo ngày

| Ngày | C1 TOF | C2 MOF | C3 BOF | Ghi chú |
|---|---|---|---|---|
| **–14 → –1** | 0 | 0 | 0 | **Warm-up 2 page** (`page-strategy.md` mục 3). Bỏ qua bước này là rủi ro restrict ad account |
| 1–4 | **$70** | $30 (broad cold) | off | Pool retarget = 0, $10 vào BOF là tiền chết. Min spend $15/ad set đang bật |
| 5–7 | $60 | $30 (chuyển tệp warm) | $10 | Về đúng **60/30/10** |
| 6 | — | — | — | **Gỡ min spend limit** ở Campaign 1 |
| 8+ | $60 | $30 | $10 | Steady state |

**Không đụng gì trong 72h đầu.** Mọi chỉnh sửa reset learning phase.

---

## 5. ⚠️ AS2 "ảnh đối thủ" là ad set rủi ro nhất — phải xử lý

Ba vấn đề chồng lên nhau:

1. **Bản quyền nặng hơn video nhiều.** Video đối thủ bạn re-edit (đổi hook, VO, sub, 3s cuối) thì đã biến đổi đáng kể. Một **ảnh static** là một tác phẩm đơn lẻ — dùng gần như nguyên bản thì rất dễ bị match và DMCA takedown, kéo theo ad account.
2. **Vẫn là sản phẩm CŨ.** Ảnh không có "3 giây cuối" để bạn chèn sản phẩm mới vào như video. Mismatch creative ↔ PDP lộ ngay ở frame đầu tiên.
3. Đây cũng là nguồn duy nhất trong 3 nguồn mà bạn **không kiểm soát chất lượng đầu ra**.

**Cách xử lý — dùng ảnh đối thủ làm *layout reference*, không chạy trực tiếp:**
- Lấy 3 ảnh đối thủ chạy lâu nhất → phân tích cấu trúc (bố cục, thứ tự thông tin, kích cỡ chữ, vị trí sản phẩm)
- Dựng lại đúng layout đó bằng **sản phẩm mới của bạn** (ảnh Topview + Canva)
- ~30 phút/ảnh, 3 ảnh là xong AS2

Bạn giữ được đúng thứ có giá trị (bố cục đã được validate bằng tiền của đối thủ) và bỏ toàn bộ rủi ro. Layout không được bảo hộ bản quyền — file ảnh thì có.

> Với AS3 (video), giữ nguyên quy tắc v1: cắt hết shot hero sản phẩm cũ, 3–4s cuối luôn là sản phẩm mới + CTA card, hook mới, VO mới.

---

## 6. Tracking

**URL parameters — dán y hệt cho cả 13 ads:**
```
utm_source=facebook&utm_medium=paid_social&utm_campaign={{campaign.name}}&utm_content={{ad.name}}&utm_term={{adset.name}}&plc={{placement}}
```
Tên ad đã mã hoá **nguồn + angle** (`TOF2_IMG_MRC`) nên `utm_content` cho bạn đọc cả 2 chiều của ma trận ngay trong GA4/Shopify, không cần chạm Ads Manager.

**Chưa verify (bạn phải tự check):**
- PDP nhận giá trị `adv` nào — tôi đang giả định `7-reasons-v2` / `make-room-v2` / `spray-cycle-v2`
- 3 advertorial có truyền tiếp `adv` + UTM sang PDP không. Không truyền = mất attribution ở bước 2, toàn bộ ma trận thành vô nghĩa

**Trước khi bật:** CAPI bật + dedup OK · domain verified · AEM xếp Purchase → IC → ATC → ViewContent → PageView · test Events trên **URL advertorial** chứ không chỉ PDP.

---

## 7. Quy ước đặt tên

```
Campaign : VH | TOF | CBO | US | 2026-09
           VH | MOF | ABO | US | 2026-09
           VH | BOF | ABO | US | 2026-09
Ad set   : AS1 | TOF-OWN | Broad-AdvPlus | Advertorial
           AS2 | TOF-IMG | Broad-AdvPlus | Advertorial
           AS3 | TOF-VID | Broad-AdvPlus | Advertorial
           AS4 | MOF-WARM | PDP
           AS5 | BOF-RTG14 | PDP
Ad       : TOF1_OWN_7R_ProductHero_9x16
           <ADSET#>_<NGUỒN>_<ANGLE>_<MÔ TẢ>_<TỈ LỆ>
```
Nguồn: `OWN` tự tạo · `IMG` ảnh recreate · `VID` video re-edit
Angle: `7R` 7 Reasons · `MRC` Make Room for Company · `BSC` Break the Spray-Bottle Cycle

---

## 8. Cách set nhanh nhất

Build **Campaign 1 + AS1 + 3 ads** hoàn chỉnh → **Duplicate AS1 → 2 lần** (chỉ đổi tên + swap creative) → **Duplicate Campaign 1 → 2 lần** (đổi thành MOF/ABO và BOF/ABO). URL parameters dùng macro nên set 1 lần cho cả 13 ads.
**~35 phút.**

Upload **toàn bộ** video/ảnh vào Media Library trước, đặt tên đúng theo quy ước mục 7 — làm trước tiết kiệm gấp đôi thời gian so với upload lúc build ad.

**Việc tốn tay thật sự vẫn là creative, không phải campaign:**
| Việc | Cách nhanh nhất | Thời gian |
|---|---|---|
| Lọc 3 video từ kho 444 (AS3) | Ad Library → sort **"longest running"** → top 20 → chọn 3 | 15 phút |
| Re-edit 3 video | 1 template CapCut duy nhất, swap clip | 45 phút |
| Recreate 3 ảnh (AS2) | Phân tích layout ảnh đối thủ → dựng lại bằng ảnh Topview + Canva | 90 phút |
| 3 creative AS1 | Skill `topview-ugc-video-pipeline` trong repo này — gen + dựng ffmpeg (VO, sub, hook A/B, CTA) tự động | Chạy skill |
| 1 static BOF | Canva, spec trong `ads-copy-velahush-20260910.md` | 15 phút |

---

## 9. Mốc đọc số

| Thời điểm | Xem gì | Hành động |
|---|---|---|
| Ngày 3 | Hook rate (3s view / impression) cấp ad | < 20% → thay 3 giây đầu, giữ copy |
| Ngày 3 | Outbound CTR | < 1.0% → angle không chạm |
| Ngày 5 | **Share ngân sách giữa AS1/AS2/AS3** | Đây là kết quả chính: nguồn creative nào thắng |
| Ngày 6 | — | **Gỡ min spend limit** |
| Ngày 7 | Ad nào tiêu < 1/3 mức trung bình | Tắt, nhân bản nguồn+angle thắng thành variant mới |
| Ngày 10–14 | Frequency TOF > 3 | Refresh creative (đổi hook trước, copy sau) |

---

## 10. Checklist trước khi Publish

- [ ] **2 page đã warm-up ≥ 10 ngày** — xem `page-strategy.md`
- [ ] Đã quyết phương án Creator Page (A / B / C) — nếu chọn C, đọc lại rủi ro mất BM
- [ ] Pixel + CAPI verified, dedup OK, test trên URL advertorial
- [ ] Domain verified · AEM 8 events đã xếp
- [ ] 3 advertorial truyền tiếp `adv` + UTM sang PDP (**chưa verify**)
- [ ] PDP nhận đúng giá trị `adv` cho cả 3 angle (**chưa verify**)
- [ ] AS2: 3 ảnh đã **dựng lại** bằng sản phẩm mới, không dùng file gốc của đối thủ
- [ ] AS3: video đã cắt hết shot sản phẩm cũ, 3s cuối là sản phẩm mới
- [ ] Min spend limit $15 đã set trên AS1/AS2/AS3
- [ ] Campaign 3 (BOF) ở trạng thái **OFF**
- [ ] Discount code BOF đã tạo và test được ở checkout
- [ ] Không có testimonial / số review bịa trong bất kỳ creative nào
- [ ] Exclusion Purchasers 180d ở cả 3 campaign

# VelaHush — Meta Ads Campaign Setup Plan
**Ngày:** 10/09/2026 · **Budget:** $100/ngày · **Market:** US (EN) · **Objective:** Sales / Purchase

---

## 0. Kết luận nhanh (TL;DR)

| Quyết định | Phương án |
|---|---|
| Số nhóm | **3 ad set** (không phải 6) — 1 campaign ABO |
| Ngân sách | TOF $60 · MOF $30 · BOF $10 |
| Số creative | **10 ads = 6 TOF / 3 MOF / 1 BOF** → đúng tỉ lệ 60/30/10 ở CẢ budget lẫn số creative |
| Đọc angle nào thắng | Ở **cấp AD** bên trong nhóm TOF, không tách ad set |
| Tận dụng 3 advertorial | 2 ads/advertorial trong cùng nhóm TOF |
| Ngày 1–4 | BOF chưa có tệp → dồn $10 sang TOF. Ngày 5 mới về đúng 60/30/10 |
| Việc tay nhiều nhất | Không phải dựng campaign — mà là **lọc + re-edit video từ kho 444 cái** |

> **Vì sao 3 chứ không 6 nhóm:** $100/ngày chia 6 nhóm = ~$16/nhóm. Với CPA mục tiêu $25–35, mỗi nhóm không đủ 1 đơn/ngày → không nhóm nào thoát learning phase, và 3 nhóm TOF cùng target broad sẽ **overlap đấu giá với chính mình**. Bạn vẫn được phép tới 6 — nhưng dùng 6 ở đây là trả tiền để học chậm hơn. Xem "Plan B" nếu bạn vẫn muốn tách.

---

## 1. Cấu trúc campaign

**Campaign:** `VH | Sales-Purchase | ABO | US | 2026-09`
- Objective: **Sales**, conversion event **Purchase**, conversion location Website
- **ABO** (ngân sách ở cấp ad set) — bắt buộc, vì CBO sẽ không tôn trọng tỉ lệ 60/30/10
- Tắt Advantage campaign budget
- Attribution: 7-day click, 1-day view

### Ad set 1 — `TOF | Broad-AdvPlus | Advertorial | $60`
| Setting | Giá trị |
|---|---|
| Budget | **$60/ngày** (daily, ABO) |
| Audience | **Advantage+ Audience**, để trống audience suggestion (hoặc chỉ gợi ý "Pet owner" / "Dog owner") |
| Location / Age | US · 18–65+ · All genders |
| Exclude | Website visitors 30d · Purchasers 180d |
| Placements | Advantage+ Placements (bật hết) |
| Optimization | Purchase · Highest volume · **không** đặt bid cap |
| Destination | 3 advertorial (mỗi ad 1 URL) |
| Số ads | **6** |

### Ad set 2 — `MOF | Warm | PDP | $30`
| Setting | Giá trị |
|---|---|
| Budget | **$30/ngày** |
| Audience (từ ngày 5) | Video viewers 25% (all videos, 90d) + Page engagers 180d + IG engagers 180d + Website visitors 30d + LAL 1–3% (nếu đã đủ data) |
| Audience (ngày 1–4) | **Broad cold + Advantage+** — pool warm chưa tồn tại. MOF ở đây là *loại creative*, không phải *tệp*, nên chạy cold vẫn đúng logic |
| Exclude | ATC 14d · Initiate Checkout 14d · Purchasers 180d |
| Destination | **PDP trực tiếp** (đã được educate rồi, không cần advertorial nữa) |
| Số ads | **3** |

### Ad set 3 — `BOF | RTG-14d | PDP | $10`
| Setting | Giá trị |
|---|---|
| Budget | **$10/ngày** — **BẬT TỪ NGÀY 5**, không phải ngày 1 |
| Audience | ATC 14d + Initiate Checkout 14d + PDP viewers 7d + Advertorial readers 14d (URL contains `velahush`) |
| Exclude | Purchasers 180d |
| Destination | PDP + discount code |
| Số ads | **1** (1 dự phòng để luân phiên) |

> Nếu pool BOF < 1,000 người sau ngày 5 → nới window lên 30d thay vì tăng budget.

---

## 2. Bản đồ creative → advertorial (nhóm TOF)

| Ad | Angle | Nguồn video | Destination |
|---|---|---|---|
| `TOF_7R_A` | Mùi quay lại dù đã dọn | **Video Topview (sản phẩm MỚI, chuẩn)** ← hero, để ở đây | `/pages/velahush-7-reasons` |
| `TOF_7R_B` | Nose blind — bạn hết ngửi thấy, khách thì không | Kho library #1 | `/pages/velahush-7-reasons` |
| `TOF_MRC_A` | "We're 10 minutes away" panic | Kho library #2 | `/pages/velahush-make-room-for-company` |
| `TOF_MRC_B` | Ngưng mời khách vì mùi sofa | Kho library #3 | `/pages/velahush-make-room-for-company` |
| `TOF_BSC_A` | Vấn đề là chai xịt, không phải dung dịch | Kho library #4 (có demo xịt/mist) | `/pages/velahush-break-the-spray-bottle-cycle` |
| `TOF_BSC_B` | Đếm số chai dưới bồn rửa | Kho library #5 | `/pages/velahush-break-the-spray-bottle-cycle` |

### Nhóm MOF (3 ads, dùng 20 ảnh Topview + superscale)
| Ad | Format | Nội dung | Destination |
|---|---|---|---|
| `MOF_C1_Mechanism` | **Carousel 6 ảnh** | Cơ chế: trigger spray vs fine mist, đi vào sợi vải | PDP `?adv=spray-cycle-v2` |
| `MOF_S1_Compare` | Static 1080×1350 | So sánh cạnh nhau: vệt ướt vs phủ đều | PDP `?adv=spray-cycle-v2` |
| `MOF_S2_Objection` | Long-form native static | Xử lý 2 rào cản: "ướt sofa?" / "chỉ che mùi?" | PDP `?adv=7-reasons-v2` |

### Nhóm BOF (1 ad — **CHƯA CÓ, phải làm**)
| Ad | Format | Spec |
|---|---|---|
| `BOF_S1_Offer` | Static 1080×1080 | Trái 40%: sản phẩm cắt nền (lấy từ 20 ảnh MOF). Phải: `XX% OFF` cỡ lớn · deadline ngày · 3 bullet (Free shipping / 30-day return / Sofa·Rug·Bed·Car) · sao đánh giá **chỉ nếu có review thật** |

Làm bằng Canva ~15 phút. Đây là gap duy nhất phải tự tay tạo.

---

## 3. ⚠️ 3 rủi ro phải xử lý trước khi bật

**1. Video kho 444 cái đang show sản phẩm CŨ, PDP show sản phẩm MỚI.**
Ngoại hình khác → mismatch creative↔landing page: tụt CVR và có rủi ro policy "misrepresentation". Cách xử lý (giữ được tốc độ):
- Cắt bỏ mọi shot hero cận cảnh sản phẩm cũ, chỉ giữ B-roll vấn đề (thú cưng trên sofa, ngửi, khách tới, cảnh xịt).
- **3–4 giây cuối luôn thay bằng footage sản phẩm mới từ video Topview + CTA card.**
- Làm 1 template CapCut duy nhất: `[hook 0–3s từ library] + [body] + [3s cuối: sản phẩm mới + CTA]` → swap clip là xong.

**2. Quyền sử dụng video của page đối thủ.** Nếu đó là footage nhà cung cấp mà bạn cũng có quyền thì không sao. Nếu là creative do đối thủ tự sản xuất, dùng nguyên bản là rủi ro bản quyền + báo cáo. Việc re-edit ở trên (hook mới, VO mới, sub mới, sản phẩm của bạn) là mức tối thiểu — không phải là miễn trừ hoàn toàn.

**3. Chưa verify được tham số `adv` trên PDP.** Link bạn đưa có `?adv=7-reasons-v2&cta=end`. Tôi bị chặn network nên không kiểm tra được. **Bạn cần tự confirm 2 việc:**
- PDP nhận những giá trị `adv` nào (tôi đang giả định `make-room-v2`, `spray-cycle-v2` — nếu sai nó sẽ fallback về mặc định và bạn mất đúng framing).
- Nút CTA trong 3 advertorial có **truyền tiếp** `adv` + UTM sang PDP không. Nếu không, toàn bộ traffic TOF sẽ mất attribution ở bước 2.

---

## 4. Gap lớn nhất về creative: MOFU thật

Theo framework của bạn, MOF = **Native UGC & Creator video** (unboxing, GRWM, testimonial). Bạn đang có **0 video UGC** — 20 ảnh static chỉ là giải pháp tạm.

Đây là tầng quyết định trust và nó đang yếu nhất. Việc nên làm song song ngay tuần này:
- Đặt 3–5 video UGC (Billo / Insense / creator local) — 5–7 ngày giao.
- Hoặc nhanh hơn: dùng **avatar UGC của Topview** để ra 3 video testimonial trong ngày.
- 4 Creator Page trong sơ đồ hệ sinh thái của bạn chỉ phát huy khi có Partnership Ads — mà Partnership Ads cần creator video thật. Chưa có creator video thì 4 page đó chưa dùng được.

---

## 5. Lịch triển khai & ngân sách theo ngày

| Ngày | TOF | MOF | BOF | Ghi chú |
|---|---|---|---|---|
| 1–4 | **$70** | **$30** (broad cold) | **off** | Pool retarget = 0. $10 vào BOF lúc này là tiền chết |
| 5–7 | $60 | $30 (chuyển sang tệp warm) | $10 | Về đúng **60/30/10** |
| 8+ | $60 | $30 | $10 | Steady state |

**Luật không đụng tay trong 72h đầu:** không tắt ad, không sửa budget, không đổi audience. Mọi chỉnh sửa reset learning phase.

### Mốc đọc số
| Thời điểm | Xem gì | Hành động |
|---|---|---|
| Ngày 3 | Hook rate (3s view / impression) ở cấp ad | < 20% → hook hỏng, thay 3s đầu |
| Ngày 3 | CTR outbound | < 1% → creative/angle không chạm |
| Ngày 5 | Advertorial nào ra ATC nhiều nhất | Đó là angle thắng |
| Ngày 7 | Ad nào < 1/3 chi tiêu trung bình | Tắt, thay ad mới cùng angle thắng |
| Ngày 10–14 | Frequency > 3 ở TOF | Refresh creative |

---

## 6. Tracking / UTM

**Trường "URL parameters" (dán y hệt cho CẢ 10 ads):**
```
utm_source=facebook&utm_medium=paid_social&utm_campaign={{campaign.name}}&utm_content={{ad.name}}&utm_term={{adset.name}}&plc={{placement}}
```
Vì tên ad đã mã hoá angle (`TOF_7R_A`), bạn đọc được ngay trong GA4/Shopify report angle nào ra đơn — không cần tách ad set.

**Website URL theo từng ad:** xem `meta-bulk-import.csv`.

**Bắt buộc trước khi bật:**
- Conversions API (Shopify → Facebook & Instagram app) đang bật, deduplication OK
- Domain `allvibespet.com` đã verify
- 8 sự kiện Aggregated Event Measurement đã xếp: Purchase → InitiateCheckout → AddToCart → ViewContent → PageView
- Test bằng Events Manager Test Events trên đúng URL advertorial (không phải chỉ PDP)

---

## 7. Cách set nhanh nhất — xếp theo thời gian thật

| # | Cách | Thời gian | Nhận xét |
|---|---|---|---|
| **1** | **Build 1 ad hoàn chỉnh → Duplicate ×5 → chỉ đổi video + URL + tên** | **~30 phút** | **Khuyến nghị.** Ít lỗi nhất. Dùng "Duplicate → same ad set" |
| 2 | Bulk import Excel | ~40 phút | Chỉ nhanh khi ≥ 30 ads. Phải export template của chính Meta trước rồi mới paste — header tự chế sẽ lỗi |
| 3 | Advantage+ Shopping (ASC) | ~10 phút | Nhanh nhất nhưng **phá cấu trúc TOF/MOF/BOF riêng** của bạn. Chỉ hợp làm campaign thứ 2 chạy song song |
| 4 | Marketing API script | 3–4 giờ setup | Chỉ đáng nếu tuần nào cũng launch |

### Quy trình 30 phút (cách 1)
1. Upload **hết** video + ảnh vào Media Library trước, đặt tên theo đúng `TOF_7R_A...` — **đây là bước tiết kiệm thời gian nhất**, làm sau sẽ mất gấp đôi.
2. Tạo Campaign + Ad set TOF (setting mục 1).
3. Build **`TOF_7R_A`** đầy đủ: copy, headline, URL, URL parameters, CTA.
4. Duplicate ad đó 5 lần trong cùng ad set → mỗi bản chỉ sửa: **tên ad · video · primary text · headline · URL**. (URL parameters giữ nguyên vì dùng macro.)
5. Duplicate cả ad set TOF → sửa thành MOF (budget, audience, 3 ads).
6. Duplicate tiếp → BOF (budget, audience, 1 ad, **để trạng thái OFF**).
7. Review → Publish.

### Việc tốn tay thật sự: lọc 444 video (KHÔNG xem hết)
1. Meta Ad Library → lọc theo page → sort **"longest running"**. Ad chạy > 30 ngày = đã được validate bằng tiền thật.
2. Lấy top 20. Ưu tiên: 2 giây đầu có **vấn đề nhìn thấy được** (chó nằm sofa, khách bấm chuông, tủ đầy chai xịt), cảm giác native/UGC, tỉ lệ 9:16 hoặc 4:5.
3. Chọn 5 theo bảng bản đồ ở mục 2.
4. Re-edit bằng 1 template CapCut duy nhất → 5 video trong ~45 phút.

> **Đường tắt:** repo này đã có skill `topview-ugc-video-pipeline` (gen video TOF trên Topview + dựng bằng ffmpeg: VO, sub, hook A/B, CTA). Chạy skill đó là ra thẳng 6 video TOF kèm biến thể hook A/B, bạn không phải mở CapCut. Nói một tiếng là tôi chạy.

---

## 8. Plan B — nếu vẫn muốn 6 nhóm

Chỉ dùng khi bạn chấp nhận đánh đổi tốc độ học lấy dữ liệu angle sạch, hoặc khi budget lên ≥ $200/ngày.

| Ad set | Budget | Audience | Destination |
|---|---|---|---|
| `TOF-A` | $20 | Broad | `/velahush-7-reasons` |
| `TOF-B` | $20 | Broad | `/velahush-make-room-for-company` |
| `TOF-C` | $20 | Broad | `/velahush-break-the-spray-bottle-cycle` |
| `MOF-A` | $15 | Warm (VV + Engagers) | PDP |
| `MOF-B` | $15 | LAL 1–3% | PDP |
| `BOF` | $10 | RTG 14d | PDP |

**Bắt buộc:** 3 nhóm TOF-A/B/C phải chạy qua **công cụ A/B Test của Meta**, không phải tạo tay 3 ad set song song. A/B Test chia tệp loại trừ lẫn nhau → mới tránh được overlap đấu giá. Tạo tay 3 nhóm broad giống hệt nhau là tự đẩy CPM của chính mình lên.

---

## 9. Quy ước đặt tên

```
Campaign : VH | Sales-Purchase | ABO | US | 2026-09
Ad set   : TOF | Broad-AdvPlus | Advertorial | $60
           MOF | Warm-VV+Eng   | PDP         | $30
           BOF | RTG-ATC14     | PDP         | $10
Ad       : TOF_7R_A_ProductHero_9x16
           <TẦNG>_<ANGLE>_<VARIANT>_<MÔ TẢ>_<TỈ LỆ>
```
Angle code: `7R` = 7 Reasons · `MRC` = Make Room for Company · `BSC` = Break the Spray-Bottle Cycle

---

## 10. Checklist trước khi bấm Publish

- [ ] Pixel + CAPI verified, dedup OK, test trên URL advertorial
- [ ] Domain verified · AEM 8 events đã xếp
- [ ] 3 advertorial truyền tiếp `adv` + UTM sang PDP (**đang chưa verify**)
- [ ] PDP nhận đúng giá trị `adv` cho cả 3 angle (**đang chưa verify**)
- [ ] Mọi video kho library đã cắt hết shot sản phẩm cũ, 3s cuối là sản phẩm mới
- [ ] BOF static đã làm xong, ad ở trạng thái OFF
- [ ] Discount code BOF đã tạo và test được trên checkout
- [ ] Không có testimonial/số review bịa trong bất kỳ creative nào
- [ ] Đã set exclusion Purchasers 180d ở cả 3 nhóm

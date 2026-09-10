# Remotion — hướng dẫn dùng trong repo này

Remotion là framework để **làm video bằng React**. Bạn viết component React
như làm web, Remotion chạy component đó qua từng frame trong Chrome headless,
chụp lại và ghép thành file `.mp4` bằng FFmpeg.

Project nằm ở thư mục `remotion/`.

---

## 1. Mô hình tinh thần

Điểm khác biệt duy nhất so với React thường: **component của bạn được render lại
ở mỗi frame**, và bạn biết mình đang ở frame nào.

```tsx
const frame = useCurrentFrame(); // 0, 1, 2, 3, ... ở mỗi lần render
```

Vậy nên "animation" trong Remotion không phải CSS transition hay `setInterval`,
mà là **một hàm thuần từ số frame ra style**:

```tsx
const opacity = frame / 30; // sau 30 frame (1 giây ở 30fps) thì hiện hẳn
return <div style={{opacity}}>Xin chào</div>;
```

Vì nó là hàm thuần nên video luôn tái lập chính xác: render lại lần nào cũng
ra đúng kết quả đó, và Remotion có thể render nhiều frame song song.

Bốn khái niệm cần nhớ:

| Khái niệm | Là gì |
|---|---|
| **Composition** | Một video: có `id`, `fps`, `width`, `height`, `durationInFrames` |
| **Frame** | Đơn vị thời gian. Giây × fps = frame. 3 giây ở 30fps = 90 frame |
| **Sequence** | Dời gốc thời gian — bên trong nó `useCurrentFrame()` đếm lại từ 0 |
| **Studio** | Trình xem/chỉnh sửa chạy trong trình duyệt, hot-reload |

---

## 2. Cấu trúc thư mục

```
remotion/
├── remotion.config.ts          # cấu hình render (chất lượng, định dạng…)
├── package.json
├── public/                     # ảnh, nhạc, font → gọi bằng staticFile()
└── src/
    ├── index.ts                # registerRoot() — điểm vào
    ├── Root.tsx                # khai báo các <Composition>
    └── compositions/
        ├── HelloWorld.tsx      # demo API cốt lõi
        └── PromoVideo.tsx      # demo video dọc cho TikTok/Reels
```

Luồng: `index.ts` → `Root.tsx` → các composition.

---

## 3. Chạy

```bash
cd remotion
npm install          # chỉ cần lần đầu

npm run dev          # mở Remotion Studio ở http://localhost:3000
```

Trong Studio bạn có thanh timeline, tua từng frame, sửa code là preview cập nhật
ngay. Đây là nơi bạn làm việc 90% thời gian.

### Xuất video

```bash
# npx remotion render <composition-id> <file-output>
npx remotion render HelloWorld out/hello.mp4
npx remotion render PromoVideo  out/promo.mp4

# một khung hình tĩnh (ảnh)
npx remotion still PromoVideo out/thumb.png --frame=120
```

Truyền props từ dòng lệnh:

```bash
npx remotion render PromoVideo out/ao-thun.mp4 \
  --props='{"headline":"Áo thun Motard","cta":"Đặt hàng ngay →"}'
```

Vài cờ hay dùng:

| Cờ | Tác dụng |
|---|---|
| `--props='{...}'` | Truyền props (JSON, hoặc đường dẫn tới file `.json`) |
| `--frames=0-59` | Chỉ render một đoạn — rất tiện khi thử nghiệm |
| `--scale=0.5` | Render ở nửa độ phân giải cho nhanh |
| `--concurrency=4` | Số tiến trình song song |
| `--codec=h264 \| vp8 \| gif \| mp3` | Định dạng đầu ra |

---

## 4. Ba API bạn sẽ dùng suốt

### `interpolate` — ánh xạ tuyến tính

Đọc là: *"khi frame đi từ A tới B thì giá trị đi từ X tới Y"*.

```tsx
const opacity = interpolate(
  frame,
  [0, 30],   // input:  frame 0 → 30
  [0, 1],    // output: 0 → 1
  {extrapolateRight: 'clamp'}, // sau frame 30 thì giữ nguyên 1, không vượt lên
);
```

Luôn nhớ `extrapolateLeft`/`extrapolateRight: 'clamp'`, nếu không giá trị sẽ
tiếp tục tăng ngoài khoảng và cho ra kết quả lạ.

### `spring` — chuyển động có độ nảy

```tsx
const scale = spring({frame, fps, config: {damping: 200}});
```

Trả về giá trị chạy từ 0 → 1 theo vật lý lò xo. `damping` càng thấp càng nảy
nhiều. Dùng cho mọi thứ "xuất hiện" — chữ, logo, nút bấm — trông tự nhiên hơn
`interpolate` nhiều.

### `<Sequence>` — sắp xếp thời gian

```tsx
<Sequence from={30} durationInFrames={60}>
  <Title />   {/* chỉ hiện từ frame 30 đến 90 */}
</Sequence>
```

Bên trong `<Sequence from={30}>`, `useCurrentFrame()` trả về 0 tại frame 30 của
video. Nhờ vậy component con không cần biết nó nằm ở đâu trong timeline — cứ
viết animation "từ 0" là được. Đây là cách bạn tái sử dụng hiệu ứng.

Muốn xếp các cảnh nối tiếp nhau tự động, dùng `<Series>`:

```tsx
<Series>
  <Series.Sequence durationInFrames={60}><SceneA /></Series.Sequence>
  <Series.Sequence durationInFrames={90}><SceneB /></Series.Sequence>
</Series>
```

---

## 5. Ảnh, nhạc, video, font

Đặt file vào `remotion/public/` rồi gọi qua `staticFile()`:

```tsx
import {Img, Audio, Video, staticFile} from 'remotion';

<Img src={staticFile('ao-thun.png')} />
<Audio src={staticFile('nhac-nen.mp3')} volume={0.4} />
<Video src={staticFile('clip.mp4')} />
```

**Quan trọng:** dùng `<Img>`, `<Audio>`, `<Video>` của Remotion chứ **không**
dùng `<img>`, `<audio>`, `<video>` thường. Thẻ của Remotion báo cho renderer
"đợi tôi tải xong / tua tới đúng frame rồi hãy chụp", thẻ HTML thường thì không
— và bạn sẽ được video trắng hoặc thiếu tiếng.

Cùng lý do đó: nếu cần chờ dữ liệu (fetch API, load font), bọc bằng
`delayRender()` / `continueRender()`:

```tsx
const [handle] = useState(() => delayRender());
useEffect(() => {
  fetch('/api/data').then(() => continueRender(handle));
}, []);
```

---

## 6. Sửa và thêm video của bạn

**Đổi nội dung nhanh nhất:** sửa `defaultProps` trong `src/Root.tsx`, hoặc truyền
`--props` khi render.

**Thêm một video mới:**

1. Tạo `src/compositions/VideoCuaToi.tsx` export một component React.
2. Khai báo trong `src/Root.tsx`:

```tsx
<Composition
  id="VideoCuaToi"
  component={VideoCuaToi}
  durationInFrames={30 * 8}   // 8 giây
  fps={30}
  width={1080}
  height={1920}
  defaultProps={{title: 'Xin chào'}}
/>
```

3. `npm run dev` → composition mới hiện trong sidebar Studio.

Kích thước hay dùng: `1920×1080` (YouTube ngang), `1080×1920` (TikTok/Reels/
Shorts), `1080×1080` (feed vuông).

---

## 7. Ghi chú về môi trường

Lần render đầu tiên, Remotion tự tải **Chrome Headless Shell** (~150 MB) về máy.
Ở môi trường bị chặn mạng ra ngoài (CI, sandbox), việc tải này thất bại. Khi đó
trỏ sẵn tới một bản Chrome có sẵn:

```bash
REMOTION_BROWSER_EXECUTABLE=/duong/dan/chrome npx remotion render HelloWorld out/hello.mp4
```

`remotion.config.ts` đã đọc biến môi trường này sẵn. Trên máy cá nhân bạn không
cần đặt gì cả.

FFmpeg đi kèm luôn trong `@remotion/renderer`, không phải cài riêng.

---

## 8. Đi xa hơn

Các gói phụ trợ cài thêm khi cần (`npm i @remotion/...`):

| Gói | Dùng để |
|---|---|
| `@remotion/transitions` | Chuyển cảnh (fade, slide, wipe) giữa các Sequence |
| `@remotion/google-fonts` | Nạp Google Fonts đúng cách, không bị nháy chữ |
| `@remotion/media-utils` | Đọc waveform âm thanh, lấy metadata video |
| `@remotion/shapes` | Hình khối SVG dựng sẵn |
| `@remotion/lambda` | Render trên AWS Lambda, hàng trăm video song song |
| `@remotion/player` | Nhúng preview vào web app React (không cần render) |
| `zod` + `@remotion/zod-types` | Khai báo schema props → Studio sinh form chỉnh sửa trực quan |

Tài liệu chính thức: https://www.remotion.dev/docs

**Giấy phép:** Remotion miễn phí cho cá nhân và công ty nhỏ, nhưng **công ty từ
4 nhân viên trở lên cần mua license**. Xem https://remotion.dev/license.

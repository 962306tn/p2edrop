import {Config} from '@remotion/cli/config';

// Định dạng ảnh cho mỗi frame khi render (jpeg nhanh hơn, png hỗ trợ nền trong suốt)
Config.setVideoImageFormat('jpeg');

// Số tiến trình chạy song song khi render. Bỏ trống = Remotion tự chọn theo số CPU.
// Config.setConcurrency(4);

// Chất lượng H.264: 1 (đẹp nhất) → 51 (xấu nhất). 18–23 là vùng hợp lý.
Config.setCrf(18);

// Ghi đè file output nếu đã tồn tại
Config.setOverwriteOutput(true);

// Bình thường Remotion tự tải Chrome Headless Shell về khi render lần đầu.
// Nếu máy/CI chặn mạng, trỏ sẵn tới một bản Chrome có sẵn:
//   REMOTION_BROWSER_EXECUTABLE=/duong/dan/toi/chrome npm run render -- HelloWorld out/hello.mp4
if (process.env.REMOTION_BROWSER_EXECUTABLE) {
  Config.setBrowserExecutable(process.env.REMOTION_BROWSER_EXECUTABLE);
}

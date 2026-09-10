import {
  AbsoluteFill,
  Img,
  interpolate,
  Sequence,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

export type PromoProps = {
  headline: string;
  subline: string;
  cta: string;
  /** Đường dẫn ảnh. Dùng staticFile('ten-anh.png') cho file trong public/. */
  productImage?: string;
  accent: string;
};

export const promoDefaultProps: PromoProps = {
  headline: 'Tên sản phẩm của bạn',
  subline: 'Một câu bán hàng ngắn, rõ ràng',
  cta: 'Mua ngay →',
  accent: '#ff5a1f',
};

// Một hiệu ứng dùng lại được: trôi lên + hiện dần, có độ nảy.
const RiseIn: React.FC<{children: React.ReactNode; delay?: number}> = ({
  children,
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const progress = spring({
    frame: frame - delay,
    fps,
    config: {damping: 200},
  });

  return (
    <div
      style={{
        opacity: progress,
        transform: `translateY(${interpolate(progress, [0, 1], [60, 0])}px)`,
      }}
    >
      {children}
    </div>
  );
};

export const PromoVideo: React.FC<PromoProps> = ({
  headline,
  subline,
  cta,
  productImage,
  accent,
}) => {
  const frame = useCurrentFrame();

  // Nền chuyển màu chậm suốt video
  const hue = interpolate(frame, [0, 300], [0, 40]);

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(160deg, hsl(${220 + hue} 40% 10%), hsl(${
          260 + hue
        } 45% 18%))`,
        fontFamily: 'system-ui, sans-serif',
        padding: 90,
        justifyContent: 'center',
        gap: 40,
      }}
    >
      {/* <Sequence> dời gốc thời gian: bên trong nó, useCurrentFrame() bắt đầu lại từ 0. */}
      <Sequence from={0}>
        <RiseIn>
          <div
            style={{
              display: 'inline-block',
              padding: '12px 28px',
              borderRadius: 999,
              background: accent,
              color: 'white',
              fontSize: 34,
              fontWeight: 700,
              alignSelf: 'flex-start',
            }}
          >
            NEW DROP
          </div>
        </RiseIn>
      </Sequence>

      {productImage ? (
        <Sequence from={10}>
          <RiseIn>
            <Img
              src={productImage}
              style={{
                width: '100%',
                borderRadius: 32,
                objectFit: 'cover',
              }}
            />
          </RiseIn>
        </Sequence>
      ) : null}

      <Sequence from={20}>
        <RiseIn>
          <h1 style={{fontSize: 96, fontWeight: 800, color: 'white', margin: 0, lineHeight: 1.05}}>
            {headline}
          </h1>
        </RiseIn>
      </Sequence>

      <Sequence from={35}>
        <RiseIn>
          <p style={{fontSize: 44, color: '#c3cbd9', margin: 0}}>{subline}</p>
        </RiseIn>
      </Sequence>

      <Sequence from={60}>
        <RiseIn>
          <div
            style={{
              marginTop: 20,
              padding: '28px 56px',
              borderRadius: 24,
              background: 'white',
              color: '#0b0d12',
              fontSize: 48,
              fontWeight: 800,
              textAlign: 'center',
            }}
          >
            {cta}
          </div>
        </RiseIn>
      </Sequence>
    </AbsoluteFill>
  );
};

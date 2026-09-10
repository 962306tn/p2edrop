import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

type Props = {
  name: string;
};

// Composition tối giản để hiểu 3 API cốt lõi của Remotion:
// useCurrentFrame() -> frame hiện tại, interpolate() -> ánh xạ tuyến tính,
// spring() -> chuyển động vật lý có độ nảy.
export const HelloWorld: React.FC<Props> = ({name}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();

  // Phóng to có độ nảy trong ~1 giây đầu
  const scale = spring({frame, fps, config: {damping: 200}});

  // Mờ dần ở 20 frame cuối
  const opacity = interpolate(
    frame,
    [durationInFrames - 20, durationInFrames],
    [1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#0b0d12',
        alignItems: 'center',
        justifyContent: 'center',
        opacity,
      }}
    >
      <h1
        style={{
          fontFamily: 'system-ui, sans-serif',
          fontSize: 120,
          fontWeight: 800,
          color: 'white',
          transform: `scale(${scale})`,
          margin: 0,
        }}
      >
        Hello {name}
      </h1>
      <p style={{fontFamily: 'system-ui, sans-serif', fontSize: 36, color: '#8b95a5'}}>
        frame {frame} / {durationInFrames}
      </p>
    </AbsoluteFill>
  );
};

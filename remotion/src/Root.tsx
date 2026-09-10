import {Composition} from 'remotion';
import {HelloWorld} from './compositions/HelloWorld';
import {PromoVideo, promoDefaultProps} from './compositions/PromoVideo';

// Mỗi <Composition> là một "video" có thể xem trong Studio và render ra file.
// id là tên bạn truyền cho lệnh `npx remotion render <id>`.
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="HelloWorld"
        component={HelloWorld}
        durationInFrames={150} // 150 frame ÷ 30 fps = 5 giây
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{name: 'Remotion'}}
      />

      <Composition
        id="PromoVideo"
        component={PromoVideo}
        durationInFrames={300} // 10 giây
        fps={30}
        width={1080}
        height={1920} // dọc, hợp cho TikTok / Reels / Shorts
        defaultProps={promoDefaultProps}
      />
    </>
  );
};

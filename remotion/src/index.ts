import {registerRoot} from 'remotion';
import {RemotionRoot} from './Root';

// Điểm vào duy nhất của Remotion. File này chỉ làm một việc:
// đăng ký component chứa danh sách composition.
registerRoot(RemotionRoot);

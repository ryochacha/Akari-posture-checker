# posture_analyzer.py (公式サンプル準拠版)

import numpy as np

KEYPOINT_DICT = {
    'nose': 0, 'neck': 1, 'r_shoulder': 2, 'r_elbow': 3, 'r_wrist': 4,
    'l_shoulder': 5, 'l_elbow': 6, 'l_wrist': 7, 'r_hip': 8, 'r_knee': 9,
    'r_ankle': 10, 'l_hip': 11, 'l_knee': 12, 'l_ankle': 13, 'r_eye': 14,
    'l_eye': 15, 'r_ear': 16, 'l_ear': 17
}

class PostureAnalyzer:
    def __init__(self):
        self.feedback = "Initializing..."
        self.is_stooped = False

    def _calculate_angle(self, a, b, c):
        # (この関数は変更なし)
        a = np.array(a); b = np.array(b); c = np.array(c)
        ba = a - b; bc = c - b
        angle_rad = np.arctan2(bc[1], bc[0]) - np.arctan2(ba[1], ba[0])
        angle_deg = np.degrees(angle_rad)
        angle_deg = np.abs(angle_deg)
        if angle_deg > 180: angle_deg = 360 - angle_deg
        return angle_deg

    def analyze_posture(self, pose, angle_threshold=165):
        try:
            keypoints = pose['keypoints']

            def get_coord(part_name):
                kp = keypoints[KEYPOINT_DICT[part_name]]
                return kp['point'] if kp['confidence'] > 0.5 else None

            l_shoulder = get_coord('l_shoulder')
            r_shoulder = get_coord('r_shoulder')
            l_hip = get_coord('l_hip')
            r_hip = get_coord('r_hip')
            l_knee = get_coord('l_knee')
            r_knee = get_coord('r_knee')
            
            # 左右どちらかのキーポイントがあればOK
            valid_shoulders = [p for p in [l_shoulder, r_shoulder] if p is not None]
            valid_hips = [p for p in [l_hip, r_hip] if p is not None]
            valid_knees = [p for p in [l_knee, r_knee] if p is not None]

            if not (valid_shoulders and valid_hips and valid_knees):
                raise ValueError("Required keypoints not detected.")

            # 平均座標を計算
            avg_shoulder = np.mean(valid_shoulders, axis=0)
            avg_hip = np.mean(valid_hips, axis=0)
            avg_knee = np.mean(valid_knees, axis=0)

            back_angle = self._calculate_angle(avg_shoulder, avg_hip, avg_knee)

            if back_angle < angle_threshold:
                self.feedback = f"Stooped: {int(back_angle)} deg"
                self.is_stooped = True
            else:
                self.feedback = f"Good: {int(back_angle)} deg"
                self.is_stooped = False

        except Exception as e:
            self.feedback = "Analyzing..."
            self.is_stooped = False
            
        return self.feedback, self.is_stooped
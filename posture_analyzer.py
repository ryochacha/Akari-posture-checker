import numpy as np
# mediapipe_utils からキーポイントの辞書をインポート
from mediapipe_utils import KEYPOINT_DICT

class PostureAnalyzer:
    def __init__(self):
        self.feedback = "Initializing..."
        self.is_stooped = False

    def _calculate_angle(self, a, b, c):
        a = np.array(a); b = np.array(b); c = np.array(c)
        ba = a - b; bc = c - b
        angle_rad = np.arctan2(bc[1], bc[0]) - np.arctan2(ba[1], ba[0])
        angle_deg = np.degrees(angle_rad)
        angle_deg = np.abs(angle_deg)
        if angle_deg > 180: angle_deg = 360 - angle_deg
        return angle_deg

    def analyze_posture(self, body, angle_threshold=165):
        try:
            landmarks = body.landmarks # bodyオブジェクトからランドマークを取得

            def get_coord(part_name):
                # 新しいデータ構造に合わせてキーポイントを取得
                return landmarks[KEYPOINT_DICT[part_name]][:2]

            l_shoulder, r_shoulder = get_coord('left_shoulder'), get_coord('right_shoulder')
            l_hip, r_hip = get_coord('left_hip'), get_coord('right_hip')
            l_knee, r_knee = get_coord('left_knee'), get_coord('right_knee')

            avg_shoulder = np.mean([l_shoulder, r_shoulder], axis=0)
            avg_hip = np.mean([l_hip, r_hip], axis=0)
            avg_knee = np.mean([l_knee, r_knee], axis=0)

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

    def is_standing(self, body, knee_angle_threshold=160):
        try:
            landmarks = body.landmarks

            def get_coord(part_name):
                # is_visibleメソッドを使って、信頼できるキーポイントか確認
                if body.is_visible(KEYPOINT_DICT[part_name]):
                    return landmarks[KEYPOINT_DICT[part_name]][:2]
                return None

            l_hip, l_knee, l_ankle = get_coord('left_hip'), get_coord('left_knee'), get_coord('left_ankle')
            r_hip, r_knee, r_ankle = get_coord('right_hip'), get_coord('right_knee'), get_coord('right_ankle')

            if l_hip and l_knee and l_ankle:
                if self._calculate_angle(l_hip, l_knee, l_ankle) > knee_angle_threshold:
                    return True
            if r_hip and r_knee and r_ankle:
                if self._calculate_angle(r_hip, r_knee, r_ankle) > knee_angle_threshold:
                    return True
        except Exception as e:
            return False
        return False
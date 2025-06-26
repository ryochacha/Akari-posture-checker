# posture_analyzer.py (新仕様版)

import numpy as np
import mediapipe as mp

class PostureAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
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

    def analyze_posture(self, landmarks, angle_threshold=165):
        # (このメソッドは変更なし)
        try:
            def get_coord(part_enum):
                lm = landmarks[part_enum.value]
                return [lm.x, lm.y]
            l_shoulder = get_coord(self.mp_pose.PoseLandmark.LEFT_SHOULDER)
            r_shoulder = get_coord(self.mp_pose.PoseLandmark.RIGHT_SHOULDER)
            l_hip = get_coord(self.mp_pose.PoseLandmark.LEFT_HIP)
            r_hip = get_coord(self.mp_pose.PoseLandmark.RIGHT_HIP)
            l_knee = get_coord(self.mp_pose.PoseLandmark.LEFT_KNEE)
            r_knee = get_coord(self.mp_pose.PoseLandmark.RIGHT_KNEE)
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

    def is_standing(self, landmarks, knee_angle_threshold=160):
        """
        膝の角度から立っているかどうかを判定する新しいメソッド
        """
        try:
            def get_coord(part_enum):
                lm = landmarks[part_enum.value]
                # visibilityが低いキーポイントは無視
                return [lm.x, lm.y] if lm.visibility > 0.5 else None

            l_hip = get_coord(self.mp_pose.PoseLandmark.LEFT_HIP)
            l_knee = get_coord(self.mp_pose.PoseLandmark.LEFT_KNEE)
            l_ankle = get_coord(self.mp_pose.PoseLandmark.LEFT_ANKLE)

            r_hip = get_coord(self.mp_pose.PoseLandmark.RIGHT_HIP)
            r_knee = get_coord(self.mp_pose.PoseLandmark.RIGHT_KNEE)
            r_ankle = get_coord(self.mp_pose.PoseLandmark.RIGHT_ANKLE)

            # 左足の角度を計算
            if l_hip and l_knee and l_ankle:
                left_knee_angle = self._calculate_angle(l_hip, l_knee, l_ankle)
                if left_knee_angle > knee_angle_threshold:
                    return True # 左足が伸びていれば立っていると判定

            # 右足の角度を計算
            if r_hip and r_knee and r_ankle:
                right_knee_angle = self._calculate_angle(r_hip, r_knee, r_ankle)
                if right_knee_angle > knee_angle_threshold:
                    return True # 右足が伸びていれば立っていると判定

        except Exception as e:
            return False
        return False
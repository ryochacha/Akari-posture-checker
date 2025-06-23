# posture_analyzer.py (MediaPipe版)

import numpy as np
import mediapipe as mp

class PostureAnalyzer:
    """
    Mediapipeから得られた姿勢ランドマークを分析し、角度や状態を評価するクラス。
    """
    def __init__(self):
        self.mp_pose = mp.solutions.pose
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

    def analyze_posture(self, landmarks, angle_threshold=165):
        try:
            # 必要なランドマークの座標を取得
            def get_coord(part_enum):
                lm = landmarks[part_enum.value]
                return [lm.x, lm.y]

            l_shoulder = get_coord(self.mp_pose.PoseLandmark.LEFT_SHOULDER)
            r_shoulder = get_coord(self.mp_pose.PoseLandmark.RIGHT_SHOULDER)
            l_hip = get_coord(self.mp_pose.PoseLandmark.LEFT_HIP)
            r_hip = get_coord(self.mp_pose.PoseLandmark.RIGHT_HIP)
            l_knee = get_coord(self.mp_pose.PoseLandmark.LEFT_KNEE)
            r_knee = get_coord(self.mp_pose.PoseLandmark.RIGHT_KNEE)

            # 肩、腰、膝の平均座標を計算
            avg_shoulder = np.mean([l_shoulder, r_shoulder], axis=0)
            avg_hip = np.mean([l_hip, r_hip], axis=0)
            avg_knee = np.mean([l_knee, r_knee], axis=0)

            # 背中の角度を計算 (肩-腰-膝の角度)
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
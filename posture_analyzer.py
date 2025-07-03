import numpy as np
import mediapipe as mp

class PostureAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.feedback = "Initializing..."
        self.is_stooped = False
        # 前のフレームの情報を記憶するための変数
        self.prev_knee_angle = None
        self.prev_hip_y = None

    def _calculate_angle(self, a, b, c):
        a = np.array(a); b = np.array(b); c = np.array(c)
        ba = a - b; bc = c - b
        angle_rad = np.arctan2(bc[1], bc[0]) - np.arctan2(ba[1], ba[0])
        angle_deg = np.degrees(angle_rad)
        angle_deg = np.abs(angle_deg)
        if angle_deg > 180: angle_deg = 360 - angle_deg
        return angle_deg

    def analyze_posture(self, landmarks, angle_threshold=165):
        try:
            def get_coord(part_enum): return [landmarks[part_enum.value].x, landmarks[part_enum.value].y]
            l_shoulder, r_shoulder = get_coord(self.mp_pose.PoseLandmark.LEFT_SHOULDER), get_coord(self.mp_pose.PoseLandmark.RIGHT_SHOULDER)
            l_hip, r_hip = get_coord(self.mp_pose.PoseLandmark.LEFT_HIP), get_coord(self.mp_pose.PoseLandmark.RIGHT_HIP)
            l_knee, r_knee = get_coord(self.mp_pose.PoseLandmark.LEFT_KNEE), get_coord(self.mp_pose.PoseLandmark.RIGHT_KNEE)
            avg_shoulder = np.mean([l_shoulder, r_shoulder], axis=0)
            avg_hip = np.mean([l_hip, r_hip], axis=0)
            avg_knee = np.mean([l_knee, r_knee], axis=0)
            back_angle = self._calculate_angle(avg_shoulder, avg_hip, avg_knee)
            if back_angle < angle_threshold:
                self.feedback = f"Stooped: {int(back_angle)} deg"; self.is_stooped = True
            else:
                self.feedback = f"Good: {int(back_angle)} deg"; self.is_stooped = False
        except Exception as e:
            self.feedback = "Analyzing..."; self.is_stooped = False
        return self.feedback, self.is_stooped

    def detect_standing_up_action(self, landmarks, angle_delta_threshold, hip_y_delta_threshold):
        standing_up = False
        current_knee_angle = None
        current_hip_y = None
        try:
            def get_coord_and_visibility(part_enum):
                lm = landmarks[part_enum.value]
                return [lm.x, lm.y] if lm.visibility > 0.5 else None
            
            l_hip, l_knee, l_ankle = get_coord_and_visibility(self.mp_pose.PoseLandmark.LEFT_HIP), get_coord_and_visibility(self.mp_pose.PoseLandmark.LEFT_KNEE), get_coord_and_visibility(self.mp_pose.PoseLandmark.LEFT_ANKLE)
            r_hip, r_knee, r_ankle = get_coord_and_visibility(self.mp_pose.PoseLandmark.RIGHT_HIP), get_coord_and_visibility(self.mp_pose.PoseLandmark.RIGHT_KNEE), get_coord_and_visibility(self.mp_pose.PoseLandmark.RIGHT_ANKLE)
            
            valid_hips = [p for p in [l_hip, r_hip] if p is not None]
            valid_knees = [p for p in [l_knee, r_knee] if p is not None]
            valid_ankles = [p for p in [l_ankle, r_ankle] if p is not None]

            if valid_hips and valid_knees and valid_ankles:
                avg_hip = np.mean(valid_hips, axis=0)
                avg_knee = np.mean(valid_knees, axis=0)
                avg_ankle = np.mean(valid_ankles, axis=0)
                current_knee_angle = self._calculate_angle(avg_hip, avg_knee, avg_ankle)
                current_hip_y = avg_hip[1]

            if self.prev_knee_angle is not None and self.prev_hip_y is not None and \
               current_knee_angle is not None and current_hip_y is not None:
                angle_delta = current_knee_angle - self.prev_knee_angle
                hip_y_delta = self.prev_hip_y - current_hip_y
                if angle_delta > angle_delta_threshold and hip_y_delta > hip_y_delta_threshold:
                    standing_up = True
            
            self.prev_knee_angle = current_knee_angle
            self.prev_hip_y = current_hip_y
        except Exception as e:
            self.prev_knee_angle = None
            self.prev_hip_y = None
        return standing_up
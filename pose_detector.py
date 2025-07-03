import cv2
import mediapipe as mp

class PoseDetector:
    """
    MediapipeのPoseを利用して、画像から姿勢を検出するクラス。
    """
    def __init__(self,
                 min_detection_confidence=0.5,
                 min_tracking_confidence=0.5):
        """
        クラスの初期化。Mediapipe Poseのモデルを準備する。
        """
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence)
        self.mp_drawing = mp.solutions.drawing_utils

    def find_pose(self, image, draw=True):
        """
        画像内の姿勢を検出し、骨格を描画する。
        """
        image.flags.writeable = False
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)
        image.flags.writeable = True
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks and draw:
            self.mp_drawing.draw_landmarks(
                image_bgr,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS)
        return image_bgr, results

    def close(self):
        """
        リソースを解放する。
        """
        self.pose.close()
# pose_detector.py (公式サンプル準拠版)

import depthai as dai
import numpy as np
import cv2

# human-pose-estimation-0001モデルのキーポイント定義
KEYPOINTS = {
    'nose': 0, 'neck': 1, 'r_shoulder': 2, 'r_elbow': 3, 'r_wrist': 4,
    'l_shoulder': 5, 'l_elbow': 6, 'l_wrist': 7, 'r_hip': 8, 'r_knee': 9,
    'r_ankle': 10, 'l_hip': 11, 'l_knee': 12, 'l_ankle': 13, 'r_eye': 14,
    'l_eye': 15, 'r_ear': 16, 'l_ear': 17
}
POSE_PAIRS = [
    [1, 2], [1, 5], [2, 3], [3, 4], [5, 6], [6, 7], [1, 8], [8, 9],
    [9, 10], [1, 11], [11, 12], [12, 13], [1, 0], [0, 14], [14, 16],
    [0, 15], [15, 17]
]
COLOR_MAP = [
    [0, 100, 255], [0, 100, 255], [0, 255, 255], [0, 100, 255], [0, 255, 255],
    [0, 100, 255], [0, 255, 0], [255, 200, 100], [255, 0, 255], [0, 255, 0],
    [255, 200, 100], [255, 0, 255], [0, 0, 255], [255, 0, 0], [255, 0, 0],
    [255, 0, 0], [255, 0, 0]
]# pose_detector.py (MediaPipe版)

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
        # 高速化のため、画像を書き込み不可にして参照渡しにする
        image.flags.writeable = False
        # Mediapipeで処理するために、BGR画像をRGBに変換
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 姿勢を検出
        results = self.pose.process(image_rgb)

        # 画面に描画するために、画像を書き込み可能に戻す
        image.flags.writeable = True
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        # 検出した骨格を描画
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
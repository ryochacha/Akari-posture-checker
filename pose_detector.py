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
]

class PoseDetector:
    def __init__(self):
        self.pipeline = dai.Pipeline()
        
        # --- ノード定義 ---
        # 1. カメラノード
        cam_rgb = self.pipeline.create(dai.node.ColorCamera)
        cam_rgb.setPreviewSize(456, 256) # モデルの入力サイズに合わせる
        cam_rgb.setInterleaved(False)

        # 2. ニューラルネットワークノード (ここが重要)
        # 汎用のNeuralNetworkノードを使い、姿勢推定モデルを読み込む
        nn = self.pipeline.create(dai.node.NeuralNetwork)
        nn.setBlobPath("pose_detection.blob")
        cam_rgb.preview.link(nn.input)

        # --- 出力ノード定義 ---
        xout_rgb = self.pipeline.create(dai.node.XLinkOut)
        xout_rgb.setStreamName("rgb")
        cam_rgb.preview.link(xout_rgb.input)

        xout_nn = self.pipeline.create(dai.node.XLinkOut)
        xout_nn.setStreamName("nn")
        nn.out.link(xout_nn.input)

        # --- デバイスへの接続 ---
        try:
            self.device = dai.Device(self.pipeline)
            self.q_rgb = self.device.getOutputQueue("rgb", maxSize=4, blocking=False)
            self.q_nn = self.device.getOutputQueue("nn", maxSize=4, blocking=False)
            self.poses = []
        except Exception as e:
            print(f"DepthAIデバイスの初期化に失敗: {e}")
            self.device = None

    def _decode_poses(self, nn_output, frame_shape):
        """
        ニューラルネットワークの生出力から姿勢データをデコード(解析)する
        """
        h, w = frame_shape
        heatmaps = np.array(nn_output.getLayerFp16('Mconv7_stage2_L2')).reshape((1, 19, 32, 57))
        pafs = np.array(nn_output.getLayerFp16('Mconv7_stage2_L1')).reshape((1, 38, 32, 57))
        heatmaps = heatmaps.astype('float32')
        pafs = pafs.astype('float32')

        # この部分はOpenPoseの複雑な後処理のため、ここでは簡易的なキーポイント抽出に留めます
        # 検出されたキーポイントを格納するリスト
        detected_keypoints = []
        for i in range(len(KEYPOINTS)):
            heatmap = heatmaps[0, i, :, :]
            _, conf, _, point = cv2.minMaxLoc(heatmap)
            x = int((w / heatmap.shape[1]) * point[0])
            y = int((h / heatmap.shape[0]) * point[1])
            detected_keypoints.append({'point': (x, y), 'confidence': conf})
        
        # 1つの姿勢オブジェクトとしてラップする
        self.poses = [{'keypoints': detected_keypoints}]


    def next_frame(self):
        if self.device is None: return None, []
            
        in_rgb = self.q_rgb.tryGet()
        in_nn = self.q_nn.tryGet()

        frame = None
        if in_rgb is not None:
            frame = in_rgb.getCvFrame()
            if in_nn is not None:
                self._decode_poses(in_nn, frame.shape)
        
        return frame, self.poses

    def draw_poses(self, frame, poses):
        if frame is None: return
        for pose in poses:
            points = [kp['point'] for kp in pose['keypoints']]
            for i, (p1_idx, p2_idx) in enumerate(POSE_PAIRS):
                if pose['keypoints'][p1_idx]['confidence'] > 0.5 and pose['keypoints'][p2_idx]['confidence'] > 0.5:
                    p1 = points[p1_idx]
                    p2 = points[p2_idx]
                    cv2.line(frame, p1, p2, COLOR_MAP[i], 3)
            for kp in pose['keypoints']:
                 if kp['confidence'] > 0.5:
                      cv2.circle(frame, kp['point'], 5, (0,255,0), -1)

    def close(self):
        if self.device is not None:
            self.device.close()
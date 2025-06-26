
# posture_checker.py
"""
Posture Checker (gRPC Akari Version)
===================================
DepthAI + BlazePose + Akari ロボット（gRPC 明示接続）を使ったリアルタイム姿勢矯正ツール。

Requirements:
    depthai
    pygame
    akari_client
    git+https://github.com/geaxgx/depthai_blazepose.git

vendor:
    third_party.BlazeposeDepthai, mediapipe_utils, FPS  を含む
"""

from __future__ import annotations

import math
import time
from pathlib import Path
from typing import Dict, Tuple

import pygame
from third_party.BlazeposeDepthai import BlazeposeDepthai

from akari_client import AkariClient
from akari_client.config import (
    AkariClientConfig,
    JointManagerGrpcConfig,
    M5StackGrpcConfig,
)

from posture_app.config import (
    ANGLE_THRESHOLD_DEG,
    MAX_SLOUCH_EVENTS,
    SITTING_ALERT_MINUTES,
    BEEP_FILE,
)
from posture_app.state import PostureState
from posture_app.analyzer import is_slouch
from posture_app.interaction import play_sound, notify_stretch, notify_sitting

# ------------------ Akari 初期化 ------------------

def create_akari_client() -> AkariClient:
    """gRPC 経由で AkariClient を生成する。IP/PORT は環境に合わせて変更可"""
    akari_ip = "172.31.14.11"   # ← 実機 IP に書き換えてください
    akari_port = "51001"          # デフォルト 51001
    endpoint = f"{akari_ip}:{akari_port}"

    joint_cfg = JointManagerGrpcConfig(type="grpc", endpoint=endpoint)
    m5_cfg = M5StackGrpcConfig(type="grpc", endpoint=endpoint)

    client_cfg = AkariClientConfig(joint_manager=joint_cfg, m5stack=m5_cfg)
    return AkariClient(client_cfg)

# ------------------ メイン処理 ------------------

def main() -> None:
    # --- サウンド初期化 ---
    pygame.mixer.init()
    beep_sound = pygame.mixer.Sound(str(BEEP_FILE))

    # --- DepthAI BlazePose ---
    pose = BlazeposeDepthai(input_src="rgb", xyz=True)

    # --- Akari gRPC 接続 ---
    akari = create_akari_client()
    joints = akari.joints
    m5 = akari.m5stack

    # --- 状態管理 ---
    state = PostureState()

    print("[INFO] Posture checker started. Press Ctrl+C to exit.")

    for packet in pose:
        if packet.body is None:
            continue

        landmarks: Dict[int, Tuple[float, float, float]] = {
            lm.id: (
                lm.world_coordinates.x,
                lm.world_coordinates.y,
                lm.world_coordinates.z,
            )
            for lm in packet.body.landmarks
        }

        slouch, angle = is_slouch(landmarks)
        if slouch:
            play_sound(beep_sound)
            count = state.increment_slouch()
            print(f"[WARN] Slouch detected! angle={angle:.1f}°, count={count}")
            if count >= MAX_SLOUCH_EVENTS:
                notify_stretch(m5, joints)
                state.reset_slouch()

        if state.check_timer():
            notify_sitting(m5)
            state.reset_timer()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[INFO] Exiting posture checker…")

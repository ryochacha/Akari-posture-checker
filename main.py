#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from akari_client import AkariClient
from akari_client.config import (
   AkariClientConfig,
   JointManagerGrpcConfig,
   M5StackGrpcConfig,
)


def main() -> None:
   """
   メイン関数
   """
   # AKARI本体のIPアドレスを指定する。
   # 実際のAKARIのIPアドレスに合わせて変更すること。
   akari_ip = "172.31.14.11"
   # portは初期設定のままであれば51001固定
   akari_port = "51001"
   akari_endpoint = f"{akari_ip}:{akari_port}"

   joint_config: JointManagerGrpcConfig = JointManagerGrpcConfig(
      type="grpc", endpoint=akari_endpoint
   )
   m5_config: M5StackGrpcConfig = M5StackGrpcConfig(
      type="grpc", endpoint=akari_endpoint
   )
   akari_client_config = AkariClientConfig(
      joint_manager=joint_config, m5stack=m5_config
   )
   # akari_client_configを引数にしてAkariClientを作成する。
   akari = AkariClient(akari_client_config)

<<<<<<< HEAD
<<<<<<< HEAD
        if person_detected:
            # --- 2. 姿勢を分析 ---
            feedback, is_stooped = analyzer.analyze_posture(
                body, angle_threshold=cfg.ANGLE_THRESHOLD
            )
            standing = analyzer.is_standing(
                body, knee_angle_threshold=cfg.STANDING_KNEE_ANGLE_THRESHOLD
            )
=======
=======
>>>>>>> parent of f6d47e2 (Merge pull request #1 from ryochacha/akari_my_branch)
   # 処理を記載。下記は例
   joints = akari.joints
   # サーボトルクをONする。
   joints.enable_all_servo()
   # 初期位置に移動する。
<<<<<<< HEAD
   joints.move_joint_positions(sync=True, pan=0, tilt=0)
>>>>>>> parent of efd76f7 (main更新)
=======
   joints.move_joint_positions(sync=True, pan=0.4, tilt=0)
>>>>>>> parent of f6d47e2 (Merge pull request #1 from ryochacha/akari_my_branch)


if __name__ == "__main__":
   main()
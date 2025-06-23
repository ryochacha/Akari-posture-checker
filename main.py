# main.py

import cv2
import time

# 作成した各モジュールと設定ファイルをインポート
import config as cfg
from pose_detector import PoseDetector
from posture_analyzer import PostureAnalyzer
from state_manager import StateManager
from interaction import InteractionManager

# AKARIクライアントのライブラリをインポート
from akari_client import AkariClient
from akari_client.config import (
   AkariClientConfig,
   JointManagerGrpcConfig,
   M5StackGrpcConfig,
)

def draw_info_panel(image, state_manager, analyzer_feedback):
    # (この関数は以前のものから変更なし)
    info = state_manager.get_info()
    state = info.get("state", "IDLE")
    count = info.get("bad_posture_count", 0)
    duration = info.get("session_duration_min", 0)
    cv2.rectangle(image, (0, 0), (350, 140), (50, 50, 50), -1)
    color = cfg.TEXT_COLOR_ERROR if state in ["WARNING", "BREAK_TIME", "STRETCH_MODE"] else cfg.TEXT_COLOR_NORMAL
    cv2.putText(image, f"STATE: {state}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    cv2.putText(image, analyzer_feedback, (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, cfg.TEXT_COLOR_INFO, 2)
    cv2.putText(image, f"COUNT: {count}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, cfg.TEXT_COLOR_INFO, 2)
    cv2.putText(image, f"TIME: {duration} min", (180, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, cfg.TEXT_COLOR_INFO, 2)


def main() -> None:
    # === 初期化 ===
    akari_ip = "172.31.14.11"
    akari_port = "51001"
    akari_endpoint = f"{akari_ip}:{akari_port}"
    joint_config = JointManagerGrpcConfig(type="grpc", endpoint=akari_endpoint)
    m5_config = M5StackGrpcConfig(type="grpc", endpoint=akari_endpoint)
    akari_client_config = AkariClientConfig(joint_manager=joint_config, m5stack=m5_config)
    akari = AkariClient(akari_client_config)
    joints = akari.joints
    joints.enable_all_servo()
    joints.move_joint_positions(sync=True, pan=0, tilt=0)

    # --- 各モジュールのインスタンスを作成 ---
    detector = PoseDetector()
    if detector.device is None: return # デバイス初期化失敗時は終了
    
    analyzer = PostureAnalyzer()
    state_mgr = StateManager(
        bad_posture_limit=cfg.BAD_POSTURE_LIMIT,
        session_time_limit=cfg.SESSION_TIME_LIMIT_SEC
    )
    interaction_mgr = InteractionManager(
        warning_sound_path=cfg.WARNING_SOUND_PATH
    )

    # === メインループ ===
    while True:
        # --- 1. 姿勢を検出 ---
        frame, poses = detector.next_frame()
        if frame is None: continue

        # --- 2. 姿勢を分析 ---
        person_detected = len(poses) > 0
        feedback, is_stooped = ("No person", False)
        if person_detected:
            # 最初の1人だけを分析対象とする
            feedback, is_stooped = analyzer.analyze_posture(
                poses[0], angle_threshold=cfg.ANGLE_THRESHOLD
            )
            detector.draw_poses(frame, poses) # 骨格を描画

        # --- 3. 状態を更新 ---
        current_state = state_mgr.update_state(is_stooped, person_detected)

        # --- 4. 状態に応じたアクション ---
        if current_state == "WARNING":
            interaction_mgr.play_warning_sound()
        elif current_state == "BREAK_TIME":
            interaction_mgr.say("長時間の作業、お疲れ様です。ストレッチをしましょう。")
            joints.move_joint_positions(pan=0, tilt=-0.5, sync=False)
            state_mgr.force_stretch_mode()
        elif current_state == "STRETCH_MODE":
            interaction_mgr.say("ストレッチが終わったら、Rキーを押してください。", force=False)

        # --- 5. 画面表示 ---
        draw_info_panel(frame, state_mgr, feedback)
        cv2.imshow('Akari Posture Checker - DepthAI', frame)

        # --- 6. キー入力処理 ---
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): break
        if key == ord('r') and state_mgr.state == "STRETCH_MODE":
            interaction_mgr.say("お疲れ様でした。作業を再開します。")
            state_mgr.reset_after_stretch()
            joints.move_joint_positions(pan=0, tilt=0, sync=False)

    # === 終了処理 ===
    detector.close()
    cv2.destroyAllWindows()
    joints.disable_all_servo()
    print("アプリケーションを終了しました。")


if __name__ == "__main__":
    main()
# main.py (MediaPipe・PCカメラ版)

import cv2
import time

# 作成した各モジュールと設定ファイルをインポート
import config as cfg
from pose_detector import PoseDetector
from posture_analyzer import PostureAnalyzer
from state_manager import StateManager
from interaction import InteractionManager

def draw_info_panel(image, state_manager, analyzer_feedback):
    # (この関数は変更なし)
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
    detector = PoseDetector(
        min_detection_confidence=cfg.MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=cfg.MIN_TRACKING_CONFIDENCE
    )
    analyzer = PostureAnalyzer()
    state_mgr = StateManager(
        bad_posture_limit=cfg.BAD_POSTURE_LIMIT,
        session_time_limit=cfg.SESSION_TIME_LIMIT_SEC
    )
    interaction_mgr = InteractionManager(
        warning_sound_path=cfg.WARNING_SOUND_PATH
    )

    # === PCのWebカメラを起動 ===
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("カメラが見つかりません。")
        return

    # === メインループ ===
    while cap.isOpened():
        success, image = cap.read()
        if not success: continue

        # --- 1. 姿勢を検出 ---
        image, results = detector.find_pose(image, draw=True)
        person_detected = results.pose_landmarks is not None

        # --- 2. 姿勢を分析 ---
        feedback, is_stooped = ("No person", False)
        if person_detected:
            feedback, is_stooped = analyzer.analyze_posture(
                results.pose_landmarks.landmark, angle_threshold=cfg.ANGLE_THRESHOLD
            )

        # --- 3. 状態を更新 ---
        current_state = state_mgr.update_state(is_stooped, person_detected)

        # --- 4. 状態に応じたアクション ---
        if current_state == "WARNING":
            interaction_mgr.play_warning_sound()
        elif current_state == "BREAK_TIME":
            interaction_mgr.say("長時間の作業、お疲れ様です。ストレッチをしましょう。")
            state_mgr.force_stretch_mode()
        elif current_state == "STRETCH_MODE":
            interaction_mgr.say("ストレッチが終わったら、Rキーを押してください。", force=False)

        # --- 5. 画面表示 ---
        flipped_image = cv2.flip(image, 1)
        draw_info_panel(flipped_image, state_mgr, feedback)
        cv2.imshow('Posture Checker - MediaPipe', flipped_image)

        # --- 6. キー入力処理 ---
        key = cv2.waitKey(5) & 0xFF
        if key == ord('q'): break
        if key == ord('r') and state_mgr.state == "STRETCH_MODE":
            interaction_mgr.say("お疲れ様でした。作業を再開します。")
            state_mgr.reset_after_stretch()

    # === 終了処理 ===
    detector.close()
    cap.release()
    cv2.destroyAllWindows()
    print("アプリケーションを終了しました。")

if __name__ == "__main__":
    main()
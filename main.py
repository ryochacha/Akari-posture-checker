# main.py (新仕様版)

import cv2
import time

# 作成した各モジュールと設定ファイルをインポート
import config as cfg
from pose_detector import PoseDetector
from posture_analyzer import PostureAnalyzer
from state_manager import StateManager
from interaction import InteractionManager

def draw_info_panel(image, state_manager, analyzer_feedback):
    # (session_duration_minの表示を削除)
    info = state_manager.get_info()
    state = info.get("state", "IDLE")
    count = info.get("bad_posture_count", 0)
    cv2.rectangle(image, (0, 0), (350, 110), (50, 50, 50), -1) # パネルサイズを調整
    color = cfg.TEXT_COLOR_ERROR if state in ["WARNING", "PERSISTENT_WARNING"] else cfg.TEXT_COLOR_NORMAL
    cv2.putText(image, f"STATE: {state}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    cv2.putText(image, analyzer_feedback, (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, cfg.TEXT_COLOR_INFO, 2)
    cv2.putText(image, f"COUNT: {count}", (10, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.7, cfg.TEXT_COLOR_INFO, 2)

def main() -> None:
    # === 初期化 ===
    detector = PoseDetector(
        min_detection_confidence=cfg.MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=cfg.MIN_TRACKING_CONFIDENCE
    )
    analyzer = PostureAnalyzer()
    state_mgr = StateManager(
        bad_posture_limit=cfg.BAD_POSTURE_LIMIT,
    )
    # configから永続警告の間隔を渡す
    interaction_mgr = InteractionManager(
        warning_sound_path=cfg.WARNING_SOUND_PATH,
        persistent_interval=cfg.PERSISTENT_WARNING_INTERVAL_SEC
    )

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("カメラが見つかりません。")
        return

    # === メインループ ===
    while cap.isOpened():
        success, image = cap.read()
        if not success: continue

        image, results = detector.find_pose(image, draw=True)
        person_detected = results.pose_landmarks is not None

        is_stooped = False
        standing = False
        feedback = "No person"

        if person_detected:
            feedback, is_stooped = analyzer.analyze_posture(
                results.pose_landmarks.landmark, angle_threshold=cfg.ANGLE_THRESHOLD
            )
            standing = analyzer.is_standing(
                results.pose_landmarks.landmark, knee_angle_threshold=cfg.STANDING_KNEE_ANGLE_THRESHOLD
            )

        current_state = state_mgr.update_state(is_stooped, person_detected)

        # --- 新しいアクションロジック ---
        if current_state == "WARNING":
            interaction_mgr.play_warning_sound()
        elif current_state == "PERSISTENT_WARNING":
            interaction_mgr.play_persistent_warning() # 警告を鳴らし続ける
            # 立っていることを検知したらリセット
            if standing:
                interaction_mgr.say("姿勢がリセットされました。")
                state_mgr.reset()

        # --- 画面表示とキー入力 ---
        flipped_image = cv2.flip(image, 1)
        draw_info_panel(flipped_image, state_mgr, feedback)
        cv2.imshow('Posture Checker', flipped_image)

        if cv2.waitKey(5) & 0xFF == ord('q'): break

    # === 終了処理 ===
    detector.close()
    cap.release()
    cv2.destroyAllWindows()
    print("アプリケーションを終了しました。")

if __name__ == "__main__":
    main()
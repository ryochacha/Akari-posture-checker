import cv2
import config as cfg
from BlazeposeDepthai import BlazeposeDepthai
from posture_analyzer import PostureAnalyzer
from state_manager import StateManager
from interaction import InteractionManager

def draw_info_panel(image, state_manager, analyzer_feedback):
    info = state_manager.get_info()
    state = info.get("state", "IDLE")
    count = info.get("bad_posture_count", 0)
    cv2.rectangle(image, (0, 0), (350, 110), (50, 50, 50), -1)
    color = cfg.TEXT_COLOR_ERROR if state in ["WARNING", "PERSISTENT_WARNING"] else cfg.TEXT_COLOR_NORMAL
    cv2.putText(image, f"STATE: {state}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    cv2.putText(image, analyzer_feedback, (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, cfg.TEXT_COLOR_INFO, 2)
    cv2.putText(image, f"COUNT: {count}", (10, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.7, cfg.TEXT_COLOR_INFO, 2)

def main():
    # === 初期化 ===
    # input_srcをNoneにすると、AKARIのOAK-Dカメラを自動で使います
    # 手元のPCのWebカメラで試す場合は input_src=0 とします
    pose_detector = BlazeposeDepthai(input_src=0) 
    analyzer = PostureAnalyzer()
    state_mgr = StateManager(bad_posture_limit=cfg.BAD_POSTURE_LIMIT)
    interaction_mgr = InteractionManager(
        warning_sound_path=cfg.WARNING_SOUND_PATH,
        persistent_interval=cfg.PERSISTENT_WARNING_INTERVAL_SEC
    )

    # === メインループ ===
    while True:
        # --- 1. Blazeposeでフレームと姿勢を検出 ---
        # next_frame()で、描画済みのフレームとbodyオブジェクトが返ってくる
        frame, body = pose_detector.next_frame()
        if frame is None: break

        person_detected = body is not None
        is_stooped = False
        standing = False
        feedback = "No person"

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
   # 処理を記載。下記は例
   joints = akari.joints
   # サーボトルクをONする。
   joints.enable_all_servo()
   # 初期位置に移動する。
   joints.move_joint_positions(sync=True, pan=0, tilt=0)
>>>>>>> parent of efd76f7 (main更新)

        # --- 3. 状態を更新 ---
        current_state = state_mgr.update_state(is_stooped, person_detected)

        # --- 4. 状態に応じたアクション ---
        if current_state == "WARNING":
            interaction_mgr.play_warning_sound()
        elif current_state == "PERSISTENT_WARNING":
            interaction_mgr.play_persistent_warning()
            if standing:
                interaction_mgr.say("リセットします。")
                state_mgr.reset()

        # --- 5. 画面表示 ---
        draw_info_panel(frame, state_mgr, feedback)
        cv2.imshow('Posture Checker - Blazepose', frame)

        if cv2.waitKey(1) == ord('q'):
            break

    # === 終了処理 ===
    pose_detector.exit()
    cv2.destroyAllWindows()
    print("アプリケーションを終了しました。")

if __name__ == "__main__":
    main()
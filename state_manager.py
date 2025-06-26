# state_manager.py (新仕様版)

import time

class StateManager:
    def __init__(self, bad_posture_limit=3):
        # --- 設定値 ---
        self.BAD_POSTURE_LIMIT = bad_posture_limit
        self.BAD_POSTURE_COOLDOWN_SEC = 5

        # --- 内部状態変数 ---
        self.state = "IDLE"  # IDLE, NORMAL, WARNING, PERSISTENT_WARNING
        self.bad_posture_count = 0
        self.last_warning_time = 0
        self.person_detected = False

    def update_state(self, is_stooped, person_detected):
        if not person_detected:
            self.state = "IDLE"
            # 誰もいなくなったらカウンターをリセット
            if self.person_detected:
                self.reset()
            self.person_detected = False
            return self.state
        
        self.person_detected = True

        # 永続警告モードからは、外部からのリセットでのみ復帰
        if self.state == "PERSISTENT_WARNING":
            return self.state

        if is_stooped:
            if time.time() - self.last_warning_time > self.BAD_POSTURE_COOLDOWN_SEC:
                self.bad_posture_count += 1
                self.last_warning_time = time.time()
                self.state = "WARNING"
                
                if self.bad_posture_count >= self.BAD_POSTURE_LIMIT:
                    self.state = "PERSISTENT_WARNING" # 永続警告モードに移行
        else:
            self.state = "NORMAL"

        return self.state

    def reset(self):
        """状態を完全にリセットする"""
        self.bad_posture_count = 0
        self.last_warning_time = 0
        self.state = "NORMAL"
        print("State has been reset.")

    def get_info(self):
        # session_duration_minを削除
        return {
            "state": self.state,
            "bad_posture_count": self.bad_posture_count,
        }
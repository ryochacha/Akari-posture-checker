import time

class StateManager:
    """
    アプリケーションの状態を管理するクラス。
    猫背の回数やセッション時間を追跡し、適切な行動を決定する。
    """
    def __init__(self, bad_posture_limit=3, session_time_limit=3600):
        """
        クラスの初期化。

        Args:
            bad_posture_limit (int): 休憩を促すまでの猫背回数の上限。
            session_time_limit (int): 休憩を促すまでのセッション時間の上限(秒)。
        """
        # --- 設定値 ---
        self.BAD_POSTURE_LIMIT = bad_posture_limit
        self.SESSION_TIME_LIMIT = session_time_limit
        self.BAD_POSTURE_COOLDOWN_SEC = 10  # 一度猫背と判定したら、次の判定まで空ける時間
        self.GOOD_POSTURE_RESET_SEC = 10   # この秒数良い姿勢を保つとカウンターがリセットされる

        # --- 内部状態変数 ---
        self.state = "IDLE"  # IDLE, NORMAL, WARNING, BREAK_TIME, STRETCH_MODE
        self.bad_posture_count = 0
        self.session_start_time = None
        self.last_warning_time = 0
        self.good_posture_start_time = None
        self.person_detected = False

    def update_state(self, is_stooped, person_detected):
        """
        現在の状態を更新し、実行すべきアクションを返す。

        Args:
            is_stooped (bool): PostureAnalyzerによる猫背判定結果。
            person_detected (bool): PoseDetectorによる人物検出結果。

        Returns:
            str: 現在の状態 (e.g., "NORMAL", "WARNING")
        """
        current_time = time.time()

        # --- 人物検出のハンドリング ---
        if not person_detected:
            # 誰もいなければアイドル状態に
            self.state = "IDLE"
            self.session_start_time = None
            self.good_posture_start_time = None
            return self.state

        if self.session_start_time is None:
            # 人物が検出され始めたらセッション開始
            self.session_start_time = current_time
            self.state = "NORMAL"

        # --- メインロジック ---
        # 休憩モードやストレッチモードの場合は、状態を更新しない
        if self.state in ["BREAK_TIME", "STRETCH_MODE"]:
            return self.state

        # --- 時間経過による休憩勧告 ---
        if current_time - self.session_start_time > self.SESSION_TIME_LIMIT:
            self.state = "BREAK_TIME"
            return self.state

        # --- 姿勢による状態遷移 ---
        if is_stooped:
            self.good_posture_start_time = None # 良い姿勢タイマーをリセット
            # クールダウン時間を過ぎていたら、猫背カウンターを増やす
            if current_time - self.last_warning_time > self.BAD_POSTURE_COOLDOWN_SEC:
                self.bad_posture_count += 1
                self.last_warning_time = current_time
                self.state = "WARNING"
                # 猫背回数が上限に達したら休憩モードへ
                if self.bad_posture_count >= self.BAD_POSTURE_LIMIT:
                    self.state = "BREAK_TIME"
        else: # 良い姿勢の場合
            self.state = "NORMAL"
            if self.good_posture_start_time is None:
                self.good_posture_start_time = current_time
            # 一定時間、良い姿勢を保ったらカウンターをリセット
            if current_time - self.good_posture_start_time > self.GOOD_POSTURE_RESET_SEC:
                self.bad_posture_count = 0

        return self.state

    def force_stretch_mode(self):
        """外部からストレッチモードに移行させる"""
        self.state = "STRETCH_MODE"

    def reset_after_stretch(self):
        """ストレッチ完了後に状態をリセットする"""
        self.bad_posture_count = 0
        self.session_start_time = time.time() # セッションタイマーもリセット
        self.state = "NORMAL"
        print("Session reset after stretch.")

    def get_info(self):
        """画面表示用に現在の状態を辞書で返す"""
        if self.session_start_time:
            session_duration = int(time.time() - self.session_start_time)
        else:
            session_duration = 0

        return {
            "state": self.state,
            "bad_posture_count": self.bad_posture_count,
            "session_duration_min": session_duration // 60,
        }

def main():
    """
    このファイルはクラス定義が主目的であり、単体で実行しても
    大きな処理は行いません。
    `main.py`からインポートして使用します。
    """
    print("StateManager class is defined in this file.")
    print("Import this into your main script to manage application state.")

if __name__ == "__main__":
    main()
# --- 姿勢分析に関する設定 ---
ANGLE_THRESHOLD = 165 # この角度(度)より小さい場合、「猫背」と判定
STANDING_KNEE_ANGLE_THRESHOLD = 160 # この角度(度)より大きい場合、「立っている」と判定

# --- 状態管理に関する設定 ---
BAD_POSTURE_LIMIT = 3
BAD_POSTURE_COOLDOWN_SEC = 5

# --- ユーザーインタラクションに関する設定 ---
WARNING_SOUND_PATH = "assets/alert.wav"
PERSISTENT_WARNING_INTERVAL_SEC = 2
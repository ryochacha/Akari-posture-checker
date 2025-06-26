# config.py (新仕様版)

"""
アプリケーションの全設定値を管理するファイル。
"""

# --- 姿勢分析に関する設定 ---
# この角度(度)より小さい場合、「猫背」と判定されます。
ANGLE_THRESHOLD = 170
# この角度(度)より大きい場合、「立っている」と判定します。
STANDING_KNEE_ANGLE_THRESHOLD = 160


# --- 状態管理に関する設定 ---
# この回数だけ猫背(WARNING)を検出したら、永続的な警告(PERSISTENT_WARNING)を開始します。
BAD_POSTURE_LIMIT = 3
# 一度猫背の警告(WARNING)を出したら、次の警告まで最低でもこの秒数だけ待ちます。
BAD_POSTURE_COOLDOWN_SEC = 5


# --- ユーザーインタラクションに関する設定 ---
WARNING_SOUND_PATH = "assets/alert.wav"
# 永続警告モードの際の、警告音の再生間隔（秒）
PERSISTENT_WARNING_INTERVAL_SEC = 2


# --- 姿勢検出に関する設定 ---
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5


# --- 画面表示に関する設定 ---
TEXT_COLOR_NORMAL = (0, 255, 0)
TEXT_COLOR_WARNING = (0, 165, 255)
TEXT_COLOR_ERROR = (0, 0, 255)
TEXT_COLOR_INFO = (255, 255, 255)
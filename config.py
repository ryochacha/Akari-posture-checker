# --- 姿勢分析に関する設定 ---
ANGLE_THRESHOLD = 165 # この角度(度)より小さい場合、「猫背」と判定

# --- 「立ち上がり動作」を検知するためのしきい値 ---
# 膝の角度が、前のフレームからこの値(度)以上大きくなったら「立ち上がり中」と見なす
STANDING_ACTION_ANGLE_DELTA = 25
# 腰のY座標が、前のフレームからこの値(画面全体の高さに対する割合)以上、上に移動したか
STANDING_ACTION_HIP_Y_DELTA = 0.03 # 画面の高さの3%分

# --- 状態管理に関する設定 ---
BAD_POSTURE_LIMIT = 3
BAD_POSTURE_COOLDOWN_SEC = 5

# --- ユーザーインタラクションに関する設定 ---
WARNING_SOUND_PATH = "assets/alert.wav"
PERSISTENT_WARNING_INTERVAL_SEC = 2

# --- 姿勢検出に関する設定 ---
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5

# --- 画面表示に関する設定 ---
TEXT_COLOR_NORMAL = (0, 255, 0)
TEXT_COLOR_WARNING = (0, 165, 255)
TEXT_COLOR_ERROR = (0, 0, 255)
TEXT_COLOR_INFO = (255, 255, 255)
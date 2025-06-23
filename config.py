# -*- coding: utf-8 -*-

"""
アプリケーションの全設定値を管理するファイル。
このファイルの値を変更することで、プログラムの動作を調整できます。
"""

# --- 姿勢分析に関する設定 (posture_analyzer.py) ---
# この角度(度)より小さい場合、「猫背」と判定されます。
# 理想は180度に近い値です。165-170あたりが現実的なしきい値かもしれません。
ANGLE_THRESHOLD = 165

# --- 状態管理に関する設定 (state_manager.py) ---
# この回数だけ猫背(WARNING)を検出したら、休憩(BREAK_TIME)を促します。
BAD_POSTURE_LIMIT = 3

# この時間(秒)だけ連続で座っていたら、休憩(BREAK_TIME)を促します。
# 1時間 = 3600秒
SESSION_TIME_LIMIT_SEC = 3600

# 一度猫背の警告(WARNING)を出したら、次の警告まで最低でもこの秒数だけ待ちます。
# 短時間に警告が連続するのを防ぎます。
BAD_POSTURE_COOLDOWN_SEC = 10

# この秒数だけ良い姿勢を続けると、猫背のカウンターがリセットされます。
GOOD_POSTURE_RESET_SEC = 15

# --- ユーザーインタラクションに関する設定 (interaction.py) ---
# 警告音ファイルのパス
WARNING_SOUND_PATH = "assets/alert.mp3"#変える

# --- 姿勢検出に関する設定 (pose_detector.py) ---
# Mediapipeの検出信頼度のしきい値 (0.0 ~ 1.0)
# 値を上げると、より確信度が高いものだけを検出するようになり、誤検出が減りますが、検出感度は下がります。
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5

# --- 画面表示に関する設定 (main.py) ---
# 画面に表示する情報のテキスト色 (BGR形式)
TEXT_COLOR_NORMAL = (0, 255, 0)      # 緑 (良い姿勢)
TEXT_COLOR_WARNING = (0, 165, 255)   # オレンジ (警告)
TEXT_COLOR_ERROR = (0, 0, 255)       # 赤 (エラー/休憩)
TEXT_COLOR_INFO = (255, 255, 255)    # 白 (情報)
import os
import sys
import math
import time
import cv2
import mediapipe as mp
import absl.logging
import subprocess

# --- ログ抑制 ---
absl.logging.set_verbosity(absl.logging.ERROR)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
devnull = os.open(os.devnull, os.O_WRONLY)
os.dup2(devnull, sys.stderr.fileno())

# --- MediaPipe 初期化 ---
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# --- 設定値 ---
POSTURE_THRESHOLD = 140    # 角度しきい値（140度未満で猫背判定）
MAX_COUNTER = 3            # 猫背判定最大回数
DETECTION_COOLDOWN = 5.0   # 猫背検知後のインターバル(秒)

bad_posture_count = 0
consecutive_bad_posture = 0
last_detection_time = 0.0  # 最後の猫背判定時刻

def calculate_angle(a, b, c):
    ang = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0]) -
        math.atan2(a[1] - b[1], a[0] - b[0])
    )
    return abs(ang if ang < 180 else 360 - ang)

def detect_feet(landmarks):
    return (
        landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].visibility > 0.5 or
        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].visibility > 0.5
    )

def get_side_angle(landmarks, side='right'):
    if side == 'right':
        shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
        knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
    else:
        shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]

    a = [shoulder.x, shoulder.y]
    b = [hip.x, hip.y]
    c = [knee.x, knee.y]

    return calculate_angle(a, b, c)

def draw_text_with_background(img, text, pos, text_color=(255,255,255), bg_color=(0,0,0)):
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 1.0
    thickness = 3
    size = cv2.getTextSize(text, font, scale, thickness)[0]
    x, y = pos
    cv2.rectangle(img, (x - 10, y - size[1] - 10), (x + size[0] + 10, y + 10), bg_color, -1)
    cv2.putText(img, text, (x, y), font, scale, text_color, thickness)

cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("カメラが開けませんでした。")
    exit()

with mp_pose.Pose(min_detection_confidence=0.5,
                  min_tracking_confidence=0.5) as pose:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("フレームを取得できませんでした。")
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        current_time = time.time()

        try:
            if results.pose_landmarks is not None:
                landmarks = results.pose_landmarks.landmark

                angle = get_side_angle(landmarks, side='right')

                if detect_feet(landmarks):
                    bad_posture_count = 0
                    consecutive_bad_posture = 0
                    last_detection_time = 0.0
                    subprocess.run(["afplay", "Blow.aiff"])
                    draw_text_with_background(image, "✅ 足を検出：カウンターをリセットしました", (10, 70), (255, 255, 255), (0, 150, 0))

                elif angle < POSTURE_THRESHOLD:
                    consecutive_bad_posture += 1
                    if consecutive_bad_posture >= 3:
                        # 5秒インターバルチェック
                        if current_time - last_detection_time >= DETECTION_COOLDOWN:
                            bad_posture_count += 1
                            last_detection_time = current_time
                            subprocess.run(["afplay", "Glass.aiff"])  # ← ここで1回検出ごとに音が鳴る
                        consecutive_bad_posture = 0
                    draw_text_with_background(image, f"⚠️ 猫背が {bad_posture_count} 回検出されました", (10, 70), (255, 255, 255), (0, 0, 200))

                else:
                    consecutive_bad_posture = 0
                    draw_text_with_background(image, f"🧍 良い姿勢：現在 {bad_posture_count} 回", (10, 70), (0, 0, 0), (200, 220, 255))

                if bad_posture_count >= MAX_COUNTER:
                    print("猫背が3回検出されたためプログラムを終了します。")
                    subprocess.run(["afplay", "Ping.aiff"])
                    break

                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            else:
                draw_text_with_background(image, "姿勢を検出できません", (10, 70), (200, 200, 200), (50, 50, 50))

        except Exception as e:
            print("Error:", e)

        cv2.imshow('Posture Checker (Right Side Camera)', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

import cv2

print("Trying to open camera...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("エラー: カメラを開けませんでした。")
    exit()

print("Camera opened successfully. Press 'q' to quit.")
while True:
    # フレームを1枚読み込む
    ret, frame = cap.read()

    # フレームが正しく読み込めなかった場合は、ループを抜ける
    if not ret:
        print("エラー: フレームを読み込めません。")
        break

    # フレームをウィンドウに表示
    cv2.imshow('Camera Test', frame)

    # 'q'キーが押されたらループを抜ける
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 後処理
cap.release()
cv2.destroyAllWindows()
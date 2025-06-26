# download_model.py

import blobconverter
import os
import sys

# ダウンロードしたいモデルの名前
# 以前お伝えした'pose-detection-0001'ではなく、こちらが正式名称です
MODEL_NAME = "human-pose-estimation-0001"
SHAVES = 6
TARGET_FILENAME = "pose_detection.blob"

print("--- モデルのダウンロードを開始します ---")
print(f"モデル名: {MODEL_NAME}")
print(f"SHAVEs: {SHAVES}")

try:
    # blobconverterライブラリを使って、モデルを直接ダウンロード
    # from_zooは、OpenVINO Model Zooからモデルを探してくれます
    blob_path = blobconverter.from_zoo(
        name=MODEL_NAME,
        shaves=SHAVES,
        version="2022.1" # OpenVINOのバージョンを明示的に指定
    )

    print(f"\nダウンロード成功。一時パス: {blob_path}")

    # pose_detector.pyが参照するファイル名に変更
    os.rename(blob_path, TARGET_FILENAME)

    print(f"ファイル名を '{TARGET_FILENAME}' に変更しました。")
    print("\n--- 準備完了 ---")
    print(f"'{TARGET_FILENAME}'がプロジェクトフォルダに作成されました。")
    print("次に `python3 main.py` を実行してください。")

except Exception as e:
    print(f"\n--- エラー ---")
    print(f"モデルのダウンロードに失敗しました: {e}")
    print("インターネット接続を確認するか、ファイアウォール設定を見直してください。")
    sys.exit(1)
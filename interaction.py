import pygame
import pyttsx3
import threading
import time
import os

class InteractionManager:
    """
    音や音声によるユーザーへのフィードバックを管理するクラス。
    """
    def __init__(self, warning_sound_path="assets/alert.wav"):
        """
        クラスの初期化。pygameとpyttsx3を準備する。

        Args:
            warning_sound_path (str): 警告音ファイルのパス。
        """
        # --- サウンドエフェクト(SE)用の設定 ---
        pygame.mixer.init()
        if os.path.exists(warning_sound_path):
            self.warning_sound = pygame.mixer.Sound(warning_sound_path)
        else:
            print(f"警告: 音声ファイルが見つかりません: {warning_sound_path}")
            self.warning_sound = None

        # --- 音声合成(TTS)用の設定 ---
        self.tts_engine = pyttsx3.init()
        # ロックとフラグで、同時に複数のことを喋らないように制御
        self.tts_lock = threading.Lock()
        self.is_speaking = False

        # --- クールダウン設定 ---
        self.last_warning_time = 0
        self.warning_cooldown_sec = 5  # 警告音のクールダウン(秒)

    def _speak_in_thread(self, text):
        """
        [内部処理] テキストの読み上げを別スレッドで実行する。
        これにより、読み上げ中もメインプログラムが固まらない。
        """
        with self.tts_lock:
            self.is_speaking = True
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"TTSエラー: {e}")
            finally:
                self.is_speaking = False

    def say(self, text, force=False):
        """
        指定されたテキストを音声で読み上げる（非同期）。

        Args:
            text (str): 読み上げるテキスト。
            force (bool): 他の音声を中断して強制的に再生するか。
        """
        if self.is_speaking and not force:
            # 他のメッセージを読み上げ中は新しいメッセージを受け付けない
            return

        # 既存のスレッドが動いていれば終了を待つ (force=Trueの場合)
        if self.is_speaking and force:
            # 簡単のため、ここでは新しいスレッドを開始するだけで、
            # 既存のものを止める複雑な処理は省略します。
            # pyttsx3の`stop()`は不安定な場合があるため。
            pass

        # 新しいスレッドで読み上げを開始
        thread = threading.Thread(target=self._speak_in_thread, args=(text,))
        thread.daemon = True  # メインスレッドが終了したら、このスレッドも終了する
        thread.start()

    def play_warning_sound(self):
        """
        警告音を再生する（クールダウン付き）。
        """
        current_time = time.time()
        # クールダウン時間を過ぎていて、かつ何も喋っていない場合のみ再生
        if self.warning_sound and current_time - self.last_warning_time > self.warning_cooldown_sec and not self.is_speaking:
            self.warning_sound.play()
            self.last_warning_time = current_time

def main():
    """
    このファイル単体でテスト実行するためのメイン関数。
    InteractionManagerの動作を確認できる。
    """
    print("InteractionManagerのテストを開始します。")
    # assetsフォルダとalert.wavを準備してください。
    interaction_mgr = InteractionManager(warning_sound_path="assets/alert.wav")

    print("5秒後に警告音を鳴らします...")
    time.sleep(5)
    interaction_mgr.play_warning_sound()
    print("警告音を再生しました。")

    print("\n5秒後にメッセージを読み上げます...")
    time.sleep(5)
    interaction_mgr.say("これはテストメッセージです。正常に動作しています。")
    print("読み上げを開始しました。（バックグラウンドで実行されます）")

    # 読み上げが終わるまで少し待つ
    while interaction_mgr.is_speaking:
        time.sleep(0.5)

    print("\nテストを終了します。")


if __name__ == "__main__":
    main()
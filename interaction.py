# interaction.py (新仕様版)

import pygame
import pyttsx3
import threading
import time
import os

class InteractionManager:
    def __init__(self, warning_sound_path="assets/alert.wav", persistent_interval=2):
        # (pygameとttsの初期化部分は変更なし)
        pygame.mixer.init()
        if os.path.exists(warning_sound_path):
            self.warning_sound = pygame.mixer.Sound(warning_sound_path)
        else:
            print(f"警告: 音声ファイルが見つかりません: {warning_sound_path}")
            self.warning_sound = None
        self.tts_engine = pyttsx3.init()
        self.tts_lock = threading.Lock()
        self.is_speaking = False

        # クールダウン設定
        self.last_warning_time = 0
        self.warning_cooldown_sec = 5
        # 永続警告用の設定
        self.last_persistent_warning_time = 0
        self.persistent_interval_sec = persistent_interval

    # (_speak_in_thread, say メソッドは変更なし)
    def _speak_in_thread(self, text):
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
        if self.is_speaking and not force: return
        thread = threading.Thread(target=self._speak_in_thread, args=(text,))
        thread.daemon = True
        thread.start()

    def play_warning_sound(self):
        # (このメソッドは変更なし)
        current_time = time.time()
        if self.warning_sound and current_time - self.last_warning_time > self.warning_cooldown_sec and not self.is_speaking:
            self.warning_sound.play()
            self.last_warning_time = current_time

    def play_persistent_warning(self):
        """
        クールダウンなしで、一定間隔で警告音を鳴らし続ける新しいメソッド
        """
        current_time = time.time()
        if self.warning_sound and current_time - self.last_persistent_warning_time > self.persistent_interval_sec:
            self.warning_sound.play()
            self.last_persistent_warning_time = current_time
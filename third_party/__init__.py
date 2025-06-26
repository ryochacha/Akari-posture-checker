# third_party/__init__.py   ☆新規または追記
"""
third_party package
-------------------
depthai_blazepose 由来のモジュールを vendor しただけだと、
BlazeposeDepthai.py 内で `import mediapipe_utils`, `import FPS`
が解決できないので、エイリアスを張っておく。
"""
import importlib
import sys

# 「pip install 版」と同じ名前で import できるよう登録
sys.modules['mediapipe_utils'] = importlib.import_module('third_party.mediapipe_utils')
sys.modules['FPS']             = importlib.import_module('third_party.FPS')


"""Configuration values for posture checker."""
from pathlib import Path

ANGLE_THRESHOLD_DEG: int = 25          # Degrees over which posture is bad
MAX_SLOUCH_EVENTS: int = 3              # Number of slouches before forcing stretch
SITTING_ALERT_MINUTES: int = 60         # Minutes before sitting reminder

# Path to alert sound
BEEP_FILE: Path = Path(__file__).resolve().parent / "assets" / "alert.wav"

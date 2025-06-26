
"""State tracking for posture checker."""
import time
from . import config

class PostureState:
    def __init__(self):
        self.slouch_count: int = 0
        self.sitting_start: float = time.time()

    # ----- slouch -----
    def increment_slouch(self) -> int:
        self.slouch_count += 1
        return self.slouch_count

    def reset_slouch(self) -> None:
        self.slouch_count = 0

    # ----- timer -----
    def reset_timer(self) -> None:
        self.sitting_start = time.time()

    def check_timer(self) -> bool:
        """Return True if sitting time exceeds config threshold."""
        return time.time() - self.sitting_start > config.SITTING_ALERT_MINUTES * 60

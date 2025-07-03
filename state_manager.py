import time

class StateManager:
    def __init__(self, bad_posture_limit=3, cooldown_sec=5):
        self.BAD_POSTURE_LIMIT = bad_posture_limit
        self.BAD_POSTURE_COOLDOWN_SEC = cooldown_sec
        self.state = "IDLE"
        self.bad_posture_count = 0
        self.last_warning_time = 0
        self.person_detected = False

    def update_state(self, is_stooped, person_detected):
        if not person_detected:
            if self.person_detected: self.reset()
            self.state = "IDLE"
            self.person_detected = False
            return self.state
        
        self.person_detected = True

        if self.state == "PERSISTENT_WARNING":
            return self.state

        if is_stooped:
            if time.time() - self.last_warning_time > self.BAD_POSTURE_COOLDOWN_SEC:
                self.bad_posture_count += 1
                self.last_warning_time = time.time()
                self.state = "WARNING"
                if self.bad_posture_count >= self.BAD_POSTURE_LIMIT:
                    self.state = "PERSISTENT_WARNING"
        else:
            self.state = "NORMAL"
        return self.state

    def reset(self):
        self.bad_posture_count = 0
        self.last_warning_time = 0
        self.state = "NORMAL"
        print("State has been reset.")

    def get_info(self):
        return {"state": self.state, "bad_posture_count": self.bad_posture_count}
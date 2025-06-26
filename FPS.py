import time
import collections

def now():
    return time.monotonic()

class FPS:
    def __init__(self, averaging_nb_frames=50):
        self.nbf = 0
        self.averaging_nb_frames = averaging_nb_frames
        self.fps = 0
        self.internals = collections.deque(maxlen=averaging_nb_frames)
        self.last_time = now()

    def update(self):
        new_time = now()
        self.internals.append(new_time - self.last_time)
        self.last_time = new_time
        self.nbf+=1
        if len(self.internals) > 1:
            self.fps = len(self.internals) / sum(self.internals)

    def get(self):
        return self.fps

    def get_global(self):
        if self.nbf > 1:
            return self.nbf / (now() - self.start_time)
        else:
            return 0
    
    def start(self):
        self.start_time = now()
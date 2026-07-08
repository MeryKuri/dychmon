
import os
import time

class Logger:
    def __init__(self):
        base_dir = os.path.abspath(os.path.dirname(__file__))
        self.log_dir = os.path.join(base_dir, "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "dychmon.log")

    def log(self, msg):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {msg}\n")

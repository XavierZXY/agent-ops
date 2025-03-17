import random
import time
from datetime import datetime


class LogGenerator:
    def __init__(self):
        self.log_types = [
            "INFO: Normal system operation",
            "WARNING: High CPU usage detected",
            "ERROR: Unauthorized access attempt",
            "ALERT: Smoke detected in server room",
            "ERROR: Database connection failed",
        ]

    def generate_log(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = random.choice(self.log_types)
        return f"[{timestamp}] {log_entry}"

    def generate_logs(self, num_entries=1):
        return [self.generate_log() for _ in range(num_entries)]

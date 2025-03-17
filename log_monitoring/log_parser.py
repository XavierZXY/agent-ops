class LogParser:
    def __init__(self):
        self.anomaly_keywords = {
            "fire": ["smoke", "fire", "heat"],
            "security": ["unauthorized", "breach", "attack"],
        }

    def parse_log(self, log_entry):
        """Parse a single log entry and return anomaly type if found"""
        log_lower = log_entry.lower()

        for category, keywords in self.anomaly_keywords.items():
            if any(keyword in log_lower for keyword in keywords):
                return category

        return None

    def is_anomaly(self, log_entry):
        """Check if log entry contains any anomaly"""
        return self.parse_log(log_entry) is not None

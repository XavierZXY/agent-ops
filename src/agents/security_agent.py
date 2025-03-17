import time
import random
from typing import Dict, Any, List

from src.agents.base_agent import (
    BaseAgent,
    MessageType,
    MessagePriority,
    Message,
)


class SecurityAgent(BaseAgent):
    """
    Security Agent that monitors logs for anomalies and sends alerts to Admin Agent.
    """

    def __init__(
        self,
        agent_id: str = "security",
        name: str = "Security Agent",
        admin_id: str = "admin",
    ):
        super().__init__(agent_id, name)
        self.admin_id = admin_id
        self.log_file = None
        self.anomaly_patterns = {
            "fire": ["fire", "smoke", "temperature high", "heat detected"],
            "security": [
                "intrusion",
                "unauthorized",
                "breach",
                "suspicious activity",
            ],
        }

    def set_log_file(self, log_file_path: str) -> None:
        """Set the log file to monitor."""
        self.log_file = log_file_path

    def detect_anomalies(self, log_content: str) -> List[Dict[str, Any]]:
        """
        Detect anomalies in log content.
        In this simple implementation, we just check for keywords.
        """
        anomalies = []

        for line in log_content.split("\n"):
            if not line.strip():
                continue

            # Check for fire-related anomalies
            for keyword in self.anomaly_patterns["fire"]:
                if keyword in line.lower():
                    anomalies.append(
                        {
                            "type": "fire",
                            "description": f"Fire-related issue detected: {line}",
                            "severity": "high",
                            "timestamp": time.time(),
                        }
                    )
                    break

            # Check for security-related anomalies
            for keyword in self.anomaly_patterns["security"]:
                if keyword in line.lower():
                    anomalies.append(
                        {
                            "type": "security",
                            "description": f"Security issue detected: {line}",
                            "severity": "high",
                            "timestamp": time.time(),
                        }
                    )
                    break

        return anomalies

    def simulate_log_monitoring(self) -> List[Dict[str, Any]]:
        """
        Simulate log monitoring for demonstration purposes.
        In a real system, this would read from an actual log file.
        """
        # For demonstration, randomly generate anomalies
        anomalies = []
        if random.random() < 0.3:  # 30% chance of detecting an anomaly
            anomaly_type = random.choice(["fire", "security"])
            if anomaly_type == "fire":
                keyword = random.choice(self.anomaly_patterns["fire"])
                description = f"Fire-related issue detected: {keyword} in building sector A"
            else:
                keyword = random.choice(self.anomaly_patterns["security"])
                description = (
                    f"Security issue detected: {keyword} in building sector B"
                )

            anomalies.append(
                {
                    "type": anomaly_type,
                    "description": description,
                    "severity": "high",
                    "timestamp": time.time(),
                }
            )

        return anomalies

    def process_message(self, message: Message) -> None:
        """Process incoming messages."""
        if message.message_type == MessageType.RESPONSE:
            print(
                f"SecurityAgent: Received response from {message.sender}: {message.content['message']}"
            )
        else:
            print(
                f"SecurityAgent: Received message of type {message.message_type} from {message.sender}"
            )

    def run(self) -> None:
        """Main loop for security agent operation."""
        print("SecurityAgent: Starting security monitoring...")

        # In a real system, this would be a continuous loop
        # For demonstration, we'll just simulate one check
        anomalies = self.simulate_log_monitoring()

        if anomalies:
            for anomaly in anomalies:
                print(
                    f"SecurityAgent: Detected anomaly: {anomaly['description']}"
                )

                # Send alert to Admin Agent
                self.send_message(
                    receiver=self.admin_id,
                    message_type=MessageType.ALERT,
                    content={
                        "anomaly": anomaly,
                        "message": f"Alert! {anomaly['description']}",
                    },
                    priority=MessagePriority.HIGH,
                )
        else:
            print("SecurityAgent: No anomalies detected.")

        # Process any incoming messages
        self.process_messages()

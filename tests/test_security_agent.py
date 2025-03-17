import time
from unittest.mock import MagicMock, patch

import pytest

from src.agents import MessagePriority, MessageType, SecurityAgent
from src.communication.message_queue import MessageQueue


class TestSecurityAgent:
    def setup_method(self):
        self.admin_id = "admin_test"
        self.security_agent = SecurityAgent(
            agent_id="security_test", admin_id=self.admin_id
        )
        self.message_queue = MessageQueue()
        self.security_agent.connect_to_queue(self.message_queue)
        self.message_queue.register_agent(self.admin_id)

    def test_initialization(self):
        """Test agent initialization"""
        assert self.security_agent.agent_id == "security_test"
        assert self.security_agent.name == "Security Agent"
        assert self.security_agent.admin_id == self.admin_id

    def test_anomaly_detection_fire(self):
        """Test fire anomaly detection works correctly"""
        # Create a sample log with fire-related keywords
        sample_log = "WARNING: fire detected in server room 3B"

        # Detect anomalies in the log
        anomalies = self.security_agent.detect_anomalies(sample_log)

        # Verify we detected the right type of anomaly
        assert len(anomalies) == 1
        assert anomalies[0]["type"] == "fire"
        assert "Fire-related issue detected" in anomalies[0]["description"]
        assert anomalies[0]["severity"] == "high"

    def test_anomaly_detection_security(self):
        """Test security anomaly detection works correctly"""
        # Create a sample log with security-related keywords
        sample_log = "ALERT: unauthorized access detected in database server"

        # Detect anomalies in the log
        anomalies = self.security_agent.detect_anomalies(sample_log)

        # Verify we detected the right type of anomaly
        assert len(anomalies) == 1
        assert anomalies[0]["type"] == "security"
        assert "Security issue detected" in anomalies[0]["description"]
        assert anomalies[0]["severity"] == "high"

    def test_anomaly_detection_no_anomaly(self):
        """Test that normal logs don't trigger anomalies"""
        # Create a sample normal log
        sample_log = "INFO: System backup completed successfully"

        # Detect anomalies in the log
        anomalies = self.security_agent.detect_anomalies(sample_log)

        # Verify no anomalies were detected
        assert len(anomalies) == 0

    @patch("random.random")
    def test_alert_sending(self, mock_random):
        """Test that security agent sends alerts to admin when anomalies are detected"""
        # Force the simulation to generate an anomaly
        mock_random.return_value = 0.1  # Below 0.3 to trigger anomaly

        # Run the agent
        self.security_agent.run()

        # Check if a message was sent to admin
        messages = self.message_queue.get_messages(self.admin_id)
        assert len(messages) == 1
        assert messages[0].sender == "security_test"
        assert messages[0].receiver == self.admin_id
        assert messages[0].message_type == MessageType.ALERT
        assert "anomaly" in messages[0].content
        assert messages[0].priority == MessagePriority.HIGH

    @patch("random.random")
    def test_no_alert_when_no_anomaly(self, mock_random):
        """Test that security agent doesn't send alerts when no anomalies are detected"""
        # Force the simulation to not generate an anomaly
        mock_random.return_value = 0.9  # Above 0.3 to avoid triggering anomaly

        # Run the agent
        self.security_agent.run()

        # Check that no message was sent to admin
        messages = self.message_queue.get_messages(self.admin_id)
        assert len(messages) == 0

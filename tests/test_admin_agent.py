import time
from unittest.mock import MagicMock, patch

import pytest

from src.agents import AdminAgent, Message, MessagePriority, MessageType
from src.communication.message_queue import MessageQueue


class TestAdminAgent:
    def setup_method(self):
        self.admin_agent = AdminAgent(agent_id="admin_test")
        self.message_queue = MessageQueue()
        self.admin_agent.connect_to_queue(self.message_queue)

        # Register the response agents in the message queue
        self.message_queue.register_agent("security_test")
        self.message_queue.register_agent("firefighter")
        self.message_queue.register_agent("police")

    def test_initialization(self):
        """Test agent initialization"""
        assert self.admin_agent.agent_id == "admin_test"
        assert self.admin_agent.name == "Admin Agent"
        assert self.admin_agent.firefighter_id == "firefighter"
        assert self.admin_agent.police_id == "police"
        assert isinstance(self.admin_agent.incident_log, list)

    def test_determine_response_agent_fire(self):
        """Test that admin correctly routes fire incidents to the firefighter"""
        anomaly = {
            "type": "fire",
            "description": "Fire detected in server room",
            "severity": "high",
            "timestamp": time.time(),
        }

        response_agent = self.admin_agent.determine_response_agent(anomaly)
        assert response_agent == "firefighter"

    def test_determine_response_agent_security(self):
        """Test that admin correctly routes security incidents to the police"""
        anomaly = {
            "type": "security",
            "description": "Unauthorized access detected",
            "severity": "high",
            "timestamp": time.time(),
        }

        response_agent = self.admin_agent.determine_response_agent(anomaly)
        assert response_agent == "police"

    def test_determine_response_agent_unknown(self):
        """Test that admin defaults to police for unknown incident types"""
        anomaly = {
            "type": "unknown",
            "description": "Strange event detected",
            "severity": "medium",
            "timestamp": time.time(),
        }

        response_agent = self.admin_agent.determine_response_agent(anomaly)
        assert response_agent == "police"  # Default should be police

    @patch("requests.post")
    def test_determine_response_agent_with_ai_fire(self, mock_post):
        """Test that admin correctly uses AI to route fire incidents"""
        # Mock the OpenAI API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "firefighter"}}]
        }
        mock_post.return_value = mock_response

        # Set API key for testing
        self.admin_agent.openai_api_key = "test_key"

        anomaly = {
            "type": "fire",
            "description": "Fire detected in server room",
            "severity": "high",
            "timestamp": time.time(),
        }

        response_agent = self.admin_agent.determine_response_agent_with_ai(
            anomaly
        )
        assert response_agent == "firefighter"
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_determine_response_agent_with_ai_security(self, mock_post):
        """Test that admin correctly uses AI to route security incidents"""
        # Mock the OpenAI API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "police"}}]
        }
        mock_post.return_value = mock_response

        # Set API key for testing
        self.admin_agent.openai_api_key = "test_key"

        anomaly = {
            "type": "security",
            "description": "Unauthorized access detected",
            "severity": "high",
            "timestamp": time.time(),
        }

        response_agent = self.admin_agent.determine_response_agent_with_ai(
            anomaly
        )
        assert response_agent == "police"
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_determine_response_agent_with_ai_fallback(self, mock_post):
        """Test that admin falls back to rule-based when AI fails"""
        # Mock the OpenAI API to raise an exception
        mock_post.side_effect = Exception("API error")

        # Set API key for testing
        self.admin_agent.openai_api_key = "test_key"

        anomaly = {
            "type": "fire",
            "description": "Fire detected in server room",
            "severity": "high",
            "timestamp": time.time(),
        }

        response_agent = self.admin_agent.determine_response_agent_with_ai(
            anomaly
        )
        assert (
            response_agent == "firefighter"
        )  # Should fallback to rule-based decision
        mock_post.assert_called_once()

    def test_process_alert_message(self):
        """Test that admin correctly processes alert messages from security agent"""
        # Create a sample alert message
        timestamp = time.time()
        anomaly = {
            "type": "fire",
            "description": "Fire detected in server room",
            "severity": "high",
            "timestamp": timestamp,
        }

        alert_message = Message(
            sender="security_test",
            receiver="admin_test",
            message_type=MessageType.ALERT,
            content={
                "anomaly": anomaly,
                "message": "Alert! Fire detected in server room",
            },
            priority=MessagePriority.HIGH,
        )

        # Mock the AI decision to use the traditional method
        with patch.object(
            AdminAgent,
            "determine_response_agent_with_ai",
            return_value="firefighter",
        ):
            # Process the message
            self.admin_agent.process_message(alert_message)

            # Check that the incident was logged
            assert len(self.admin_agent.incident_log) == 1
            incident = self.admin_agent.incident_log[0]
            assert incident["anomaly"] == anomaly
            assert incident["assigned_to"] == "firefighter"
            assert incident["status"] == "dispatched"

            # Check that a message was sent to the firefighter
            firefighter_messages = self.message_queue.get_messages("firefighter")
            assert len(firefighter_messages) == 1
            assert firefighter_messages[0].sender == "admin_test"
            assert firefighter_messages[0].message_type == MessageType.REQUEST

            # Check that a response was sent back to security
            security_messages = self.message_queue.get_messages("security_test")
            assert len(security_messages) == 1
            assert security_messages[0].sender == "admin_test"
            assert security_messages[0].message_type == MessageType.RESPONSE
            assert "Alert received" in security_messages[0].content["message"]

    def test_process_response_message(self):
        """Test that admin correctly processes response messages from response agents"""
        # First, create and log an incident
        timestamp = time.time()
        anomaly = {
            "type": "fire",
            "description": "Fire detected in server room",
            "severity": "high",
            "timestamp": timestamp,
        }

        self.admin_agent.log_incident(anomaly, "firefighter")

        # Create a sample response message from firefighter
        response_message = Message(
            sender="firefighter",
            receiver="admin_test",
            message_type=MessageType.RESPONSE,
            content={
                "message": "Fire issue has been handled successfully.",
                "resolution": "Fire was extinguished, area is secure.",
                "original_request": {"original_alert": {"anomaly": anomaly}},
            },
            priority=MessagePriority.MEDIUM,
        )

        # Process the response
        self.admin_agent.process_message(response_message)

        # Check that the incident status was updated
        assert self.admin_agent.incident_log[0]["status"] == "resolved"
        assert (
            "Fire was extinguished"
            in self.admin_agent.incident_log[0]["resolution"]
        )

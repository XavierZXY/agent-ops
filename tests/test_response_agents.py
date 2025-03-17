from unittest.mock import MagicMock, patch

import pytest

from src.agents import (
    FirefighterAgent,
    Message,
    MessagePriority,
    MessageType,
    PoliceAgent,
)
from src.communication.message_queue import MessageQueue


class TestFirefighterAgent:
    def setup_method(self):
        self.firefighter = FirefighterAgent(agent_id="firefighter_test")
        self.message_queue = MessageQueue()
        self.firefighter.connect_to_queue(self.message_queue)
        self.message_queue.register_agent("admin_test")

    def test_initialization(self):
        """Test agent initialization"""
        assert self.firefighter.agent_id == "firefighter_test"
        assert self.firefighter.name == "Firefighter Agent"

    def test_handle_fire_issue(self):
        """Test that firefighter correctly handles fire issues"""
        description = "Fire in server room"
        severity = "high"

        result = self.firefighter.handle_fire_issue(description, severity)

        assert "Fire issue has been addressed" in result
        assert description in result

    def test_process_request_message(self):
        """Test that firefighter correctly processes request messages"""
        # Create a sample request message
        request_message = Message(
            sender="admin_test",
            receiver="firefighter_test",
            message_type=MessageType.REQUEST,
            content={
                "message": "Please handle fire issue: Fire in server room",
                "severity": "high",
                "original_alert": {
                    "anomaly": {
                        "type": "fire",
                        "description": "Fire in server room",
                    }
                },
            },
            priority=MessagePriority.HIGH,
        )

        # Process the message
        self.firefighter.process_message(request_message)

        # Check that a response was sent back to admin
        admin_messages = self.message_queue.get_messages("admin_test")
        assert len(admin_messages) == 1
        assert admin_messages[0].sender == "firefighter_test"
        assert admin_messages[0].message_type == MessageType.RESPONSE
        assert (
            "Fire issue has been handled successfully"
            in admin_messages[0].content["message"]
        )
        assert "resolution" in admin_messages[0].content
        assert "original_request" in admin_messages[0].content


class TestPoliceAgent:
    def setup_method(self):
        self.police = PoliceAgent(agent_id="police_test")
        self.message_queue = MessageQueue()
        self.police.connect_to_queue(self.message_queue)
        self.message_queue.register_agent("admin_test")

    def test_initialization(self):
        """Test agent initialization"""
        assert self.police.agent_id == "police_test"
        assert self.police.name == "Police Agent"

    def test_handle_security_issue(self):
        """Test that police correctly handles security issues"""
        description = "Unauthorized access detected"
        severity = "high"

        result = self.police.handle_security_issue(description, severity)

        assert "Security issue has been addressed" in result
        assert description in result

    def test_process_request_message(self):
        """Test that police correctly processes request messages"""
        # Create a sample request message
        request_message = Message(
            sender="admin_test",
            receiver="police_test",
            message_type=MessageType.REQUEST,
            content={
                "message": "Please handle security issue: Unauthorized access detected",
                "severity": "high",
                "original_alert": {
                    "anomaly": {
                        "type": "security",
                        "description": "Unauthorized access detected",
                    }
                },
            },
            priority=MessagePriority.HIGH,
        )

        # Process the message
        self.police.process_message(request_message)

        # Check that a response was sent back to admin
        admin_messages = self.message_queue.get_messages("admin_test")
        assert len(admin_messages) == 1
        assert admin_messages[0].sender == "police_test"
        assert admin_messages[0].message_type == MessageType.RESPONSE
        assert (
            "Security issue has been handled successfully"
            in admin_messages[0].content["message"]
        )
        assert "resolution" in admin_messages[0].content
        assert "original_request" in admin_messages[0].content

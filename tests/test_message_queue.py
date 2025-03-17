import pytest
from src.communication.message_queue import MessageQueue
from src.agents.base_agent import Message, MessageType, MessagePriority


class TestMessageQueue:
    def setup_method(self):
        self.queue = MessageQueue()
        self.queue.register_agent("agent1")
        self.queue.register_agent("agent2")

    def test_register_agent(self):
        """Test that agents can be registered to the queue"""
        self.queue.register_agent("agent3")
        assert "agent3" in self.queue.queues
        assert self.queue.queues["agent3"].empty()

    def test_send_message(self):
        """Test that messages can be sent to recipients"""
        message = Message(
            sender="agent1",
            receiver="agent2",
            message_type=MessageType.INFO,
            content={"message": "Hello"},
            priority=MessagePriority.MEDIUM,
        )

        result = self.queue.send_message(message)
        assert result is True
        assert not self.queue.queues["agent2"].empty()

    def test_send_message_unknown_receiver(self):
        """Test handling of messages to unknown receivers"""
        message = Message(
            sender="agent1",
            receiver="unknown",
            message_type=MessageType.INFO,
            content={"message": "Hello"},
            priority=MessagePriority.MEDIUM,
        )

        result = self.queue.send_message(message)
        assert result is False

    def test_get_messages(self):
        """Test that messages can be retrieved by recipients"""
        # Send a message
        message = Message(
            sender="agent1",
            receiver="agent2",
            message_type=MessageType.INFO,
            content={"message": "Hello"},
            priority=MessagePriority.MEDIUM,
        )
        self.queue.send_message(message)

        # Get messages
        messages = self.queue.get_messages("agent2")
        assert len(messages) == 1
        assert messages[0].sender == "agent1"
        assert messages[0].content["message"] == "Hello"

        # Queue should be empty after getting messages
        assert self.queue.queues["agent2"].empty()
        assert len(self.queue.get_messages("agent2")) == 0

    def test_message_priority(self):
        """Test that messages are ordered by priority"""
        # Send messages with different priorities
        low_message = Message(
            sender="agent1",
            receiver="agent2",
            message_type=MessageType.INFO,
            content={"message": "Low priority"},
            priority=MessagePriority.LOW,
        )

        medium_message = Message(
            sender="agent1",
            receiver="agent2",
            message_type=MessageType.INFO,
            content={"message": "Medium priority"},
            priority=MessagePriority.MEDIUM,
        )

        high_message = Message(
            sender="agent1",
            receiver="agent2",
            message_type=MessageType.ALERT,
            content={"message": "High priority"},
            priority=MessagePriority.HIGH,
        )

        # Send in reverse priority order
        self.queue.send_message(low_message)
        self.queue.send_message(medium_message)
        self.queue.send_message(high_message)

        # Get messages - they should come out in priority order
        messages = self.queue.get_messages("agent2")
        assert len(messages) == 3
        assert messages[0].priority == MessagePriority.HIGH
        assert messages[1].priority == MessagePriority.MEDIUM
        assert messages[2].priority == MessagePriority.LOW

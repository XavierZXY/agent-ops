import json
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional
import time
import uuid


class AgentState(Enum):
    """Possible states of an agent."""

    IDLE = "idle"
    BUSY = "busy"
    WAITING = "waiting"


class MessageType(Enum):
    """Types of messages that can be exchanged between agents."""

    ALERT = "alert"
    REQUEST = "request"
    RESPONSE = "response"
    INFO = "info"


class MessagePriority(Enum):
    """Priority levels for messages."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Message:
    """Message class for agent communication."""

    def __init__(
        self,
        sender: str,
        receiver: str,
        message_type: MessageType,
        content: Dict[str, Any],
        priority: MessagePriority = MessagePriority.MEDIUM,
    ):
        self.id = str(uuid.uuid4())
        self.sender = sender
        self.receiver = receiver
        self.message_type = message_type
        self.content = content
        self.timestamp = time.time()
        self.priority = priority

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "message_type": self.message_type.value,
            "content": self.content,
            "timestamp": self.timestamp,
            "priority": self.priority.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create message from dictionary."""
        msg = cls(
            sender=data["sender"],
            receiver=data["receiver"],
            message_type=MessageType(data["message_type"]),
            content=data["content"],
            priority=MessagePriority(data["priority"]),
        )
        msg.id = data["id"]
        msg.timestamp = data["timestamp"]
        return msg

    def to_json(self) -> str:
        """Convert message to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> "Message":
        """Create message from JSON string."""
        return cls.from_dict(json.loads(json_str))


class BaseAgent(ABC):
    """Base class for all agents in the system."""

    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.state = AgentState.IDLE
        self.inbox = []
        self.outbox = []
        self.message_queue = None  # Will be set by the system

    def connect_to_queue(self, message_queue) -> None:
        """Connect agent to the message queue system"""
        self.message_queue = message_queue
        self.message_queue.register_agent(self.agent_id)

    def send_message(
        self,
        receiver: str,
        message_type: MessageType,
        content: Dict[str, Any],
        priority: MessagePriority = MessagePriority.MEDIUM,
    ) -> Message:
        """Send a message to another agent."""
        message = Message(
            sender=self.agent_id,
            receiver=receiver,
            message_type=message_type,
            content=content,
            priority=priority,
        )
        if self.message_queue:
            self.message_queue.send_message(message)
        print(f"{self.name} sent message to {receiver}: {message.content}")
        return message

    def process_messages(self) -> None:
        """Process all messages in the inbox."""
        if self.message_queue:
            messages = self.message_queue.get_messages(self.agent_id)
            if messages:
                self.state = AgentState.BUSY
                for message in messages:
                    self.process_message(message)
                self.state = AgentState.IDLE

    @abstractmethod
    def process_message(self, message: Message) -> None:
        """Process a single message. To be implemented by subclasses."""
        pass

    @abstractmethod
    def run(self) -> None:
        """Main loop for agent operation. To be implemented by subclasses."""
        pass

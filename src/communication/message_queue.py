import queue
from typing import Dict, Optional, List
from src.agents.base_agent import Message


class MessageQueue:
    """Central message queue for agent communication"""

    def __init__(self):
        self.queues: Dict[str, queue.PriorityQueue] = {}

    def register_agent(self, agent_id: str) -> None:
        """Register a new agent to the message queue system"""
        if agent_id not in self.queues:
            self.queues[agent_id] = queue.PriorityQueue()

    def send_message(self, message: Message) -> bool:
        """Send a message to the recipient's queue"""
        if message.receiver not in self.queues:
            return False

        # Priority is inverse (lower number = higher priority)
        priority = {"high": 1, "medium": 2, "low": 3}[message.priority.value]

        self.queues[message.receiver].put((priority, message))
        return True

    def get_messages(self, agent_id: str) -> List[Message]:
        """Get all messages for an agent"""
        if agent_id not in self.queues:
            return []

        messages = []
        while not self.queues[agent_id].empty():
            _, message = self.queues[agent_id].get()
            messages.append(message)

        return messages

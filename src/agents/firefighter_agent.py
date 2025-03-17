from src.agents.base_agent import BaseAgent, MessageType, Message


class FirefighterAgent(BaseAgent):
    """
    Firefighter Agent that handles fire-related issues dispatched by Admin Agent.
    """

    def __init__(
        self, agent_id: str = "firefighter", name: str = "Firefighter Agent"
    ):
        super().__init__(agent_id, name)

    def handle_fire_issue(self, description: str, severity: str) -> str:
        """Handle a fire-related issue."""
        print(
            f"FirefighterAgent: Handling fire issue - {description} (Severity: {severity})"
        )
        return f"Fire issue has been addressed: {description}"

    def process_message(self, message: Message) -> None:
        """Process incoming messages."""
        if message.message_type == MessageType.REQUEST:
            print(
                f"FirefighterAgent: Received request from {message.sender}: {message.content['message']}"
            )

            # Extract relevant information
            description = message.content.get("message", "")
            severity = message.content.get("severity", "medium")

            # Handle the fire issue
            resolution = self.handle_fire_issue(description, severity)

            # Send response back to Admin Agent
            self.send_message(
                receiver=message.sender,
                message_type=MessageType.RESPONSE,
                content={
                    "message": "Fire issue has been handled successfully.",
                    "resolution": resolution,
                    "original_request": message.content,
                },
            )
        else:
            print(
                f"FirefighterAgent: Received message of type {message.message_type} from {message.sender}"
            )

    def run(self) -> None:
        """Main loop for firefighter agent operation."""
        print("FirefighterAgent: Ready to respond to fire emergencies...")

        # Process any incoming messages
        self.process_messages()

        # Firefighter agent primarily responds to messages, so no proactive action needed

from src.agents.base_agent import BaseAgent, MessageType, Message


class PoliceAgent(BaseAgent):
    """
    Police Agent that handles security-related issues dispatched by Admin Agent.
    """

    def __init__(self, agent_id: str = "police", name: str = "Police Agent"):
        super().__init__(agent_id, name)

    def handle_security_issue(self, description: str, severity: str) -> str:
        """Handle a security-related issue."""
        print(
            f"PoliceAgent: Handling security issue - {description} (Severity: {severity})"
        )
        return f"Security issue has been addressed: {description}"

    def process_message(self, message: Message) -> None:
        """Process incoming messages."""
        if message.message_type == MessageType.REQUEST:
            print(
                f"PoliceAgent: Received request from {message.sender}: {message.content['message']}"
            )

            # Extract relevant information
            description = message.content.get("message", "")
            severity = message.content.get("severity", "medium")

            # Handle the security issue
            resolution = self.handle_security_issue(description, severity)

            # Send response back to Admin Agent
            self.send_message(
                receiver=message.sender,
                message_type=MessageType.RESPONSE,
                content={
                    "message": "Security issue has been handled successfully.",
                    "resolution": resolution,
                    "original_request": message.content,
                },
            )
        else:
            print(
                f"PoliceAgent: Received message of type {message.message_type} from {message.sender}"
            )

    def run(self) -> None:
        """Main loop for police agent operation."""
        print("PoliceAgent: Ready to respond to security incidents...")

        # Process any incoming messages
        self.process_messages()

        # Police agent primarily responds to messages, so no proactive action needed

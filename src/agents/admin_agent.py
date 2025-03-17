import json
import os
from typing import Any, Dict

import requests
import rich

from src.agents.base_agent import (
    BaseAgent,
    Message,
    MessagePriority,
    MessageType,
)


class AdminAgent(BaseAgent):
    """
    Admin Agent that receives alerts from Security Agent and dispatches
    appropriate response agents (Police or Firefighter) using AI for decision making.
    """

    def __init__(self, agent_id: str = "admin", name: str = "Admin Agent"):
        super().__init__(agent_id, name)
        self.firefighter_id = "firefighter"
        self.police_id = "police"
        self.incident_log = []  # Store history of incidents

        # Load AI configuration from system_config.json
        try:
            with open(
                os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    "config",
                    "system_config.json",
                ),
                "r",
            ) as f:
                config = json.load(f)
                ai_config = config.get("ai_config", {})
                # Get AI settings from config, with environment variable as fallback for API key
                self.openai_api_key = os.environ.get(
                    "OPENAI_API_KEY", ai_config.get("openai_api_key", "")
                )
                self.openai_url = ai_config.get(
                    "openai_url",
                    "https://api.siliconflow.cn/v1/chat/completions",
                )
                self.model = ai_config.get("model", "Qwen/Qwen2.5-14B-Instruct")
        except Exception as e:
            print(
                f"AdminAgent: Error loading config: {e}. Using default values."
            )
            self.openai_api_key = os.environ.get("OPENAI_API_KEY", "")
            self.openai_url = "https://api.siliconflow.cn/v1/chat/completions"
            self.model = "Qwen/Qwen2.5-14B-Instruct"

    def determine_response_agent_with_ai(self, anomaly: Dict[str, Any]) -> str:
        """Use ChatGPT to determine which response agent to dispatch based on anomaly details."""
        if not self.openai_api_key:
            print(
                "AdminAgent: No OpenAI API key found. Falling back to rule-based decision."
            )
            return self.determine_response_agent(anomaly)

        # Prepare the message for ChatGPT
        messages = [
            {
                "role": "system",
                "content": "You are an emergency response coordinator AI. Your job is to determine whether a 'firefighter' or 'police' should respond to an incident based on the details provided.",
            },
            {
                "role": "user",
                "content": f"Incident details: Type: {anomaly.get('type', 'unknown')}, Description: {anomaly.get('description', 'No description')}, Severity: {anomaly.get('severity', 'unknown')}. Should 'firefighter' or 'police' respond? Answer with only one word: either 'firefighter' or 'police'.",
            },
        ]

        try:
            # Call the OpenAI API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_api_key}",
            }
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.1,  # Low temperature for more deterministic responses
            }

            response = requests.post(
                self.openai_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                rich.print(
                    f"[green]AdminAgent AI: Received response - {result}[/green]"
                )
                ai_decision = (
                    result["choices"][0]["message"]["content"].strip().lower()
                )

                # Validate the response
                if ai_decision == "firefighter":
                    print(
                        f"AdminAgent AI: Decided to dispatch Firefighter for incident: {anomaly.get('description')}"
                    )
                    return self.firefighter_id
                elif ai_decision == "police":
                    print(
                        f"AdminAgent AI: Decided to dispatch Police for incident: {anomaly.get('description')}"
                    )
                    return self.police_id
                else:
                    print(
                        f"AdminAgent AI: Got unexpected response '{ai_decision}'. Falling back to rule-based decision."
                    )
            else:
                print(
                    f"AdminAgent: API error {response.status_code}. Falling back to rule-based decision."
                )

        except Exception as e:
            print(
                f"AdminAgent: Error calling OpenAI API: {e}. Falling back to rule-based decision."
            )

        # Fallback to the traditional method if AI fails
        return self.determine_response_agent(anomaly)

    def determine_response_agent(self, anomaly: Dict[str, Any]) -> str:
        """Determine which response agent to dispatch based on anomaly type (rule-based fallback)."""
        anomaly_type = anomaly.get("type", "").lower()

        if anomaly_type == "fire":
            return self.firefighter_id
        elif anomaly_type == "security":
            return self.police_id
        else:
            print(f"AdminAgent: Unknown anomaly type: {anomaly_type}")
            # Default to security response for unknown types
            return self.police_id

    def log_incident(self, anomaly: Dict[str, Any], assigned_to: str) -> None:
        """Log an incident for record keeping."""
        incident = {
            "anomaly": anomaly,
            "assigned_to": assigned_to,
            "status": "dispatched",
            "timestamp": anomaly.get("timestamp"),
        }
        self.incident_log.append(incident)
        print(
            f"AdminAgent: Logged incident - {anomaly['description']} - assigned to {assigned_to}"
        )

    def process_message(self, message: Message) -> None:
        """Process incoming messages."""
        if message.message_type == MessageType.ALERT:
            print(
                f"AdminAgent: Received alert from {message.sender}: {message.content['message']}"
            )

            # Extract anomaly information
            anomaly = message.content.get("anomaly", {})

            # Determine which agent to dispatch using AI
            response_agent_id = self.determine_response_agent_with_ai(anomaly)

            # Log the incident
            self.log_incident(anomaly, response_agent_id)

            # Forward request to appropriate response agent
            self.send_message(
                receiver=response_agent_id,
                message_type=MessageType.REQUEST,
                content={
                    "original_alert": message.content,
                    "message": f"Please handle {anomaly['type']} issue: {anomaly['description']}",
                    "severity": anomaly.get("severity", "medium"),
                },
                priority=MessagePriority.HIGH,
            )

            # Send acknowledgment back to Security Agent
            self.send_message(
                receiver=message.sender,
                message_type=MessageType.RESPONSE,
                content={
                    "message": f"Alert received and {response_agent_id} has been dispatched.",
                    "status": "processing",
                },
            )

        elif message.message_type == MessageType.RESPONSE:
            # Handle responses from response agents
            print(
                f"AdminAgent: Received response from {message.sender}: {message.content['message']}"
            )

            # Update incident log with resolution
            if "original_request" in message.content:
                original_request = message.content["original_request"]
                if "original_alert" in original_request:
                    anomaly = original_request["original_alert"].get(
                        "anomaly", {}
                    )

                    # Find the incident in the log
                    for incident in self.incident_log:
                        if incident["anomaly"] == anomaly:
                            incident["status"] = "resolved"
                            incident["resolution"] = message.content.get(
                                "resolution", "Issue handled"
                            )
                            print(
                                f"AdminAgent: Updated incident log - {anomaly['description']} - status: resolved"
                            )
                            break

    def run(self) -> None:
        """Main loop for admin agent operation."""
        print("AdminAgent: Starting admin coordination...")

        # Process any incoming messages
        self.process_messages()

        # Admin agent primarily responds to messages, so no proactive action needed

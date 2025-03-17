import os
import json
from typing import Dict, Any, Optional


class SystemConfig:
    """Configuration management for the multi-agent system"""

    DEFAULT_CONFIG = {
        "log_file_path": "logs/system.log",
        "monitoring_interval": 5,  # seconds
        "agent_ids": {
            "security": "security",
            "admin": "admin",
            "firefighter": "firefighter",
            "police": "police",
        },
        "simulation_mode": True,  # For demonstration purposes
    }

    def __init__(self, config_file: Optional[str] = None):
        self.config_data = self.DEFAULT_CONFIG.copy()
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)

    def load_config(self, config_file: str) -> None:
        """Load configuration from a JSON file"""
        try:
            with open(config_file, "r") as f:
                loaded_config = json.load(f)
                self.config_data.update(loaded_config)
            print(f"Configuration loaded from {config_file}")
        except Exception as e:
            print(f"Error loading configuration: {e}")

    def save_config(self, config_file: str) -> None:
        """Save current configuration to a JSON file"""
        try:
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, "w") as f:
                json.dump(self.config_data, f, indent=4)
            print(f"Configuration saved to {config_file}")
        except Exception as e:
            print(f"Error saving configuration: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.config_data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value"""
        self.config_data[key] = value

    def get_agent_id(self, agent_type: str) -> str:
        """Get the ID for a specific agent type"""
        agent_ids = self.config_data.get("agent_ids", {})
        return agent_ids.get(agent_type, agent_type)

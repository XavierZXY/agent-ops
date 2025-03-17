import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from src.agents import AdminAgent, FirefighterAgent, PoliceAgent, SecurityAgent
from src.communication.message_queue import MessageQueue
from src.system.system_controller import SystemController


class TestSystemIntegration:
    def setup_method(self):
        # Create a temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(
            delete=False, suffix=".json"
        )
        self.temp_config.write(b"""{
            "log_file_path": "test_logs/system.log",
            "monitoring_interval": 1,
            "agent_ids": {
                "security": "security",
                "admin": "admin",
                "firefighter": "firefighter",
                "police": "police"
            },
            "simulation_mode": true
        }""")
        self.temp_config.close()

        # Initialize the system controller with the temp config
        self.system = SystemController(self.temp_config.name)

    def teardown_method(self):
        # Clean up the temporary file
        os.unlink(self.temp_config.name)
        if os.path.exists("test_logs"):
            for f in os.listdir("test_logs"):
                os.remove(os.path.join("test_logs", f))
            os.rmdir("test_logs")

    def test_system_initialization(self):
        """Test that system initializes correctly with all agents"""
        # Check that all agents were created
        assert len(self.system.agents) == 4

        # Check specific agent types
        assert any(
            agent.__class__.__name__ == "SecurityAgent"
            for agent in self.system.agents.values()
        )
        assert any(
            agent.__class__.__name__ == "AdminAgent"
            for agent in self.system.agents.values()
        )
        assert any(
            agent.__class__.__name__ == "FirefighterAgent"
            for agent in self.system.agents.values()
        )
        assert any(
            agent.__class__.__name__ == "PoliceAgent"
            for agent in self.system.agents.values()
        )

        # Check that the message queue was created
        assert self.system.message_queue is not None

    def test_agent_connections(self):
        """Test that all agents are connected to the message queue"""
        for agent in self.system.agents.values():
            assert agent.message_queue is not None
            assert agent.agent_id in self.system.message_queue.queues

    @patch.object(SecurityAgent, "simulate_log_monitoring")
    def test_end_to_end_fire_scenario(self, mock_simulate):
        """Test an end-to-end fire emergency scenario"""
        # Mock the security agent to detect a fire
        mock_simulate.return_value = [
            {
                "type": "fire",
                "description": "Fire detected in server room",
                "severity": "high",
                "timestamp": 1234567890,
            }
        ]

        # Start the system
        self.system.start()

        # Run one cycle to have security agent detect the fire
        self.system.run_once()

        # Get the admin agent
        admin_id = self.system.config.get_agent_id("admin")
        admin_agent = self.system.agents[admin_id]

        # Verify the admin logged the incident
        assert len(admin_agent.incident_log) == 1
        assert admin_agent.incident_log[0]["anomaly"]["type"] == "fire"
        assert admin_agent.incident_log[0]["assigned_to"] == "firefighter"

        # Run another cycle to process the firefighter's response
        self.system.run_once()

        # Verify the incident is now resolved
        assert admin_agent.incident_log[0]["status"] == "resolved"

        # Stop the system
        self.system.stop()

    @patch.object(SecurityAgent, "simulate_log_monitoring")
    def test_end_to_end_security_scenario(self, mock_simulate):
        """Test an end-to-end security incident scenario"""
        # Mock the security agent to detect a security breach
        mock_simulate.return_value = [
            {
                "type": "security",
                "description": "Unauthorized access detected",
                "severity": "high",
                "timestamp": 1234567890,
            }
        ]

        # Start the system
        self.system.start()

        # Run one cycle to have security agent detect the breach
        self.system.run_once()

        # Get the admin agent
        admin_id = self.system.config.get_agent_id("admin")
        admin_agent = self.system.agents[admin_id]

        # Verify the admin logged the incident
        assert len(admin_agent.incident_log) == 1
        assert admin_agent.incident_log[0]["anomaly"]["type"] == "security"
        assert admin_agent.incident_log[0]["assigned_to"] == "police"

        # Run another cycle to process the police's response
        self.system.run_once()

        # Verify the incident is now resolved
        assert admin_agent.incident_log[0]["status"] == "resolved"

        # Stop the system
        self.system.stop()

    def test_continuous_operation(self):
        """Test that the system can run continuously for multiple cycles"""
        # Start the system
        self.system.start()

        # Run for a fixed number of cycles
        test_cycles = 3
        self.system.run_continuous(cycles=test_cycles, interval=0.1)

        # Verify the system ran and stopped correctly
        assert not self.system.running

        # The system should have processed some messages
        admin_id = self.system.config.get_agent_id("admin")
        admin_agent = self.system.agents[admin_id]

        # Due to the random nature of anomaly generation, we can't make specific assertions
        # about the incidents, but we can verify the system ran

        # Stop the system
        self.system.stop()

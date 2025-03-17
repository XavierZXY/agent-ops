import time
import signal
import sys
import os
from typing import Dict, List, Optional

from src.agents import (
    SecurityAgent,
    AdminAgent,
    FirefighterAgent,
    PoliceAgent,
    BaseAgent,
)
from src.communication.message_queue import MessageQueue
from src.system.config import SystemConfig


class SystemController:
    """Main controller for the multi-agent system"""

    def __init__(self, config_file: Optional[str] = None):
        # Initialize configuration
        self.config = SystemConfig(config_file)

        # Create message queue
        self.message_queue = MessageQueue()

        # Initialize agents
        self.agents: Dict[str, BaseAgent] = {}
        self._initialize_agents()

        # System state
        self.running = False
        self.setup_signal_handlers()

        print("System controller initialized")

    def _initialize_agents(self) -> None:
        """Initialize all agents in the system"""
        # Create agents
        security_id = self.config.get_agent_id("security")
        admin_id = self.config.get_agent_id("admin")
        firefighter_id = self.config.get_agent_id("firefighter")
        police_id = self.config.get_agent_id("police")

        self.agents[security_id] = SecurityAgent(
            agent_id=security_id, admin_id=admin_id
        )
        self.agents[admin_id] = AdminAgent(agent_id=admin_id)
        self.agents[firefighter_id] = FirefighterAgent(agent_id=firefighter_id)
        self.agents[police_id] = PoliceAgent(agent_id=police_id)

        # Connect agents to message queue
        for agent in self.agents.values():
            agent.connect_to_queue(self.message_queue)

    def setup_signal_handlers(self) -> None:
        """Set up handlers for system signals"""
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    def handle_shutdown(self, signum, frame) -> None:
        """Handle system shutdown signals"""
        print("\nShutting down system...")
        self.stop()
        sys.exit(0)

    def start(self) -> None:
        """Start the multi-agent system"""
        if self.running:
            print("System is already running")
            return

        print("Starting multi-agent system...")
        self.running = True

        # Ensure logs directory exists
        log_file_path = self.config.get("log_file_path")
        if log_file_path:
            os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

        # If in simulation mode, set a sample log file for the security agent
        if self.config.get("simulation_mode"):
            security_agent = self.agents.get(
                self.config.get_agent_id("security")
            )
            if security_agent:
                security_agent.set_log_file(log_file_path)

    def stop(self) -> None:
        """Stop the multi-agent system"""
        if not self.running:
            print("System is not running")
            return

        print("Stopping multi-agent system...")
        self.running = False

    def run_once(self) -> None:
        """Run a single cycle of the system (for demonstration purposes)"""
        if not self.running:
            print("System is not running. Call start() first.")
            return

        print("\n--- Running system cycle ---")

        # Run each agent once
        for agent_id, agent in self.agents.items():
            print(f"\nRunning agent: {agent.name} ({agent_id})")
            agent.run()

        print("\n--- System cycle completed ---")

    def run_continuous(
        self, cycles: int = -1, interval: Optional[float] = None
    ) -> None:
        """Run the system continuously for a specified number of cycles"""
        if not self.running:
            print("System is not running. Call start() first.")
            return

        if interval is None:
            interval = self.config.get("monitoring_interval", 5)

        cycle_count = 0

        print(f"\nRunning system continuously (interval: {interval}s)")

        try:
            while self.running and (cycles == -1 or cycle_count < cycles):
                self.run_once()
                cycle_count += 1

                if cycles == -1 or cycle_count < cycles:
                    print(f"\nWaiting {interval} seconds until next cycle...")
                    time.sleep(interval)

        except KeyboardInterrupt:
            print("\nSystem execution interrupted by user")

        print(f"System executed {cycle_count} cycles")

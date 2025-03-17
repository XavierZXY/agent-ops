#!/usr/bin/env python3
"""
Demo script for the Multi-Agent Emergency Response System.
This provides a more detailed walkthrough of system operation.
"""

import os
import time

from src.agents import (
    AdminAgent,
    FirefighterAgent,
    Message,
    MessageType,
    PoliceAgent,
    SecurityAgent,
)
from src.system.system_controller import SystemController


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, "="))
    print("=" * 80)


def print_step(step_num, description):
    """Print a step in the demo"""
    print(f"\n[Step {step_num}] {description}")
    print("-" * 80)


def run_demo():
    """Run a demonstration of the multi-agent system"""
    print_header("MULTI-AGENT EMERGENCY RESPONSE SYSTEM DEMO")

    print(
        "This demo showcases the interactions between different agents in the system."
    )

    # Ensure necessary directories exist
    os.makedirs("logs", exist_ok=True)
    os.makedirs("config", exist_ok=True)

    print_step(1, "Initializing the system controller")
    system = SystemController()

    print_step(2, "Starting the system")
    system.start()
    print("System started successfully.")

    print_step(3, "Running first system cycle")
    print("The Security Agent will monitor for anomalies.")
    print("If it detects any, it will notify the Admin Agent.")
    system.run_once()

    print_step(4, "Running second system cycle")
    print(
        "The Admin Agent will process any alerts and dispatch the appropriate response agent."
    )
    system.run_once()

    print_step(5, "Running third system cycle")
    print("Response agents (Police or Firefighter) will handle the requests.")
    system.run_once()

    print_step(6, "Running fourth system cycle")
    print("Admin Agent will process any responses from the response agents.")
    system.run_once()

    print_step(7, "Shutting down the system")
    system.stop()
    print("System shutdown complete.")

    print_header("DEMO COMPLETED")
    print("""
What happened in this demo:

1. The Security Agent monitored for anomalies in the logs
2. When an anomaly was detected, it sent an alert to the Admin Agent
3. The Admin Agent analyzed the alert and dispatched the appropriate response agent
4. The response agent (Police or Firefighter) handled the issue
5. The response agent reported back to the Admin Agent
6. The Admin Agent updated its incident log

This demonstrates how a distributed multi-agent system can work together to respond
to various types of incidents in an automated fashion.
""")


if __name__ == "__main__":
    run_demo()

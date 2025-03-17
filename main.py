#!/usr/bin/env python3
import argparse
import os
import time
from src.system.system_controller import SystemController


def parse_args():
    parser = argparse.ArgumentParser(
        description="Multi-Agent Emergency Response System"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/system_config.json",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=3,
        help="Number of system cycles to run (-1 for infinite)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Interval between system cycles in seconds",
    )
    return parser.parse_args()


def main():
    """Main entry point for the multi-agent system"""
    args = parse_args()

    # Initialize the system controller
    config_path = args.config if os.path.exists(args.config) else None
    system = SystemController(config_path)

    # Start the system
    system.start()

    # Run the system
    try:
        system.run_continuous(cycles=args.cycles, interval=args.interval)
    except KeyboardInterrupt:
        print("\nSystem interrupted by user")
    finally:
        # Stop the system
        system.stop()

    print("System shutdown complete")


if __name__ == "__main__":
    main()

# Agent Architecture Design

## Base Agent Structure

All agents in the system will inherit from a common `BaseAgent` class that provides:
- Message handling capabilities
- State management
- Communication interfaces

## Agent Communication Protocol

Agents will communicate using a simple message-passing mechanism:
1. Messages will be JSON objects with a standard format
2. Each message will contain:
   - `sender`: ID of the sending agent
   - `receiver`: ID of the receiving agent
   - `message_type`: Type of message (e.g., "ALERT", "REQUEST", "RESPONSE")
   - `content`: The actual message content
   - `timestamp`: When the message was created
   - `priority`: Message priority (HIGH, MEDIUM, LOW)

## Agent Workflow

```
                 ┌─────────────┐
                 │  Security   │
                 │    Agent    │
                 └──────┬──────┘
                        │
                        │ Alerts
                        ▼
                 ┌─────────────┐
                 │    Admin    │
                 │    Agent    │
                 └──────┬──────┘
                        │
            ┌───────────┴───────────┐
            │                       │
   Fire Related              Security Related
            │                       │
            ▼                       ▼
    ┌─────────────┐         ┌─────────────┐
    │ Firefighter │         │    Police   │
    │    Agent    │         │    Agent    │
    └─────────────┘         └─────────────┘
```

## Agent States

Each agent will implement a state machine with the following states:
- IDLE: Default state when no tasks are being processed
- BUSY: Agent is processing a task
- WAITING: Agent is waiting for a response from another agent

## Agent Interaction Sequence

1. Security Agent monitors logs continuously
2. When Security Agent detects an anomaly:
   - Creates alert message
   - Sends message to Admin Agent
3. Admin Agent analyzes the alert:
   - Determines severity and type of issue
   - Decides which specialist agent to contact
4. Admin Agent forwards request to appropriate specialist agent:
   - Fire-related issues to Firefighter Agent
   - Security-related issues to Police Agent
5. Specialist agent processes the request and reports back to Admin
6. Admin Agent records resolution and maintains system state

## Implementation Plan

The agents will be implemented using Python classes with the following structure:
- BaseAgent (abstract class)
  - SecurityAgent
  - AdminAgent
  - FirefighterAgent
  - PoliceAgent

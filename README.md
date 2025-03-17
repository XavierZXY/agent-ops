# Multi-Agent Emergency Response System

A distributed multi-agent system for real-time security monitoring and emergency response coordination. The system integrates security monitoring, administrative routing, and emergency response capabilities through a network of specialized agents.

## System Architecture

The system consists of four main agent components working together:

1. **SecurityAgent**
   - Monitors system security logs (/var/log/security.log)
   - Detects anomalous login patterns (>3 failures/minute)
   - Generates ALERT level events using RFC5424 standard
   - Communicates with AdminAgent via gRPC

2. **AdminAgent**
   - Central message routing hub with AI-powered decision making
   - Uses ChatGPT to intelligently route emergency requests based on incident details
   - Routes emergency requests to correct service type:
     - FIRE_EMERGENCY → FirefighterAgent
     - POLICE_ASSISTANCE → PoliceAgent
   - Implements priority queuing (High/Medium/Low)
   - Provides load balancing for request distribution
   - Falls back to rule-based routing if AI service is unavailable

3. **FirefighterAgent**
   - Handles fire emergency requests
   - Guaranteed response time < 30 seconds
   - Standard response format: `{status: 200, unit: "消防1中队"}`
   - Automated incident report generation

4. **PoliceAgent**
   - Processes police assistance requests
   - Response time < 45 seconds
   - Standard response format: `{status: 200, unit: "巡警3组"}`
   - Implements 3-tier incident classification

## Message System

### Message Format (JSON)
```json
{
  "timestamp": "2024-01-20T10:30:00Z",
  "event_type": "SECURITY_ALERT",
  "severity": "HIGH",
  "source_ip": "192.168.1.100",
  "hmac": "sha256-signature"
}
```

## Installation

### Prerequisites

- Python 3.11+
- MetaGPT framework
- OpenAI API key (for AI-powered decision making)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/xavierzxy/agent-ops.git
cd agent-ops

```

2. Configure event settings in `/config/events.yaml`

3. Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

4. Run the demo script:
```bash
source .venv/bin/activate
python demo.py
```

## API Examples

### Security Alert Generation
```python
from security_agent import SecurityAgent

agent = SecurityAgent()
agent.monitor_logs(interval_minutes=5)
```

### Emergency Request Routing
```python
from admin_agent import AdminAgent

admin = AdminAgent()
response = admin.route_request({
    "service_type": "FIRE_EMERGENCY",
    "priority": "HIGH",
    "location": "Building A"
})
```

## Deployment Guide

### System Initialization Order

1. Start Message Queue Service
2. Launch AdminAgent
3. Start Emergency Response Agents (Fire/Police)
4. Initialize SecurityAgent

### Configuration

1. Event frequency settings in `/config/events.yaml`
2. Heartbeat interval: 60 seconds
3. Dead letter queue handling enabled
4. OpenAI API settings (model, temperature) can be modified in AdminAgent class

### Performance Metrics

- End-to-end message latency: < 2 seconds
- System throughput: 1000 events/minute
- Agent response times:
  - FirefighterAgent: < 30 seconds
  - PoliceAgent: < 45 seconds

### Monitoring

- Security alerts: Check `/var/log/security.log`
- Agent status: 60-second heartbeat intervals
- Message queue health: Dead letter queue monitoring

## Testing

### Unit Tests
```bash
python -m pytest tests/
```

Key test cases:
- SecurityAgent alert trigger accuracy
- AdminAgent 100% routing accuracy (both AI and rule-based)
- Emergency response time compliance

### Integration Tests
- End-to-end message flow
- Failover scenarios
- Load balancing verification

### Load Testing
- Sustained load: 1000 events/minute
- Response time degradation monitoring
- System resource utilization

## License

This project is licensed under the MIT License - see the LICENSE file for details.
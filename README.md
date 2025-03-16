# Log Monitoring Agent

A powerful and flexible log monitoring system that leverages GPT for intelligent log analysis. This system provides real-time log collection, processing, and analysis capabilities through a REST API interface.

## Features

- File-based log collection with extensible collector system
- Intelligent log normalization and processing
- GPT-powered log analysis for pattern detection and insights
- RESTful API for querying and analyzing logs
- Configurable monitoring parameters and analysis rules

## Quick Start

### Prerequisites

- Python 3.7+
- OpenAI API key for GPT integration

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/agent-ops.git
   cd agent-ops
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your OpenAI API key in `src/demo.py`:
   ```python
   gpt_config = GPTConfig(
       api_key="your-api-key-here",  # Replace with your API key
       model_name="gpt-3.5-turbo",
       max_tokens=1000,
       temperature=0.7
   )
   ```

## Usage

### Starting the Server

Run the demo script to start the monitoring system:

```bash
python src/demo.py
```

The server will start on `http://localhost:8000`.

### API Endpoints

#### Search Logs

```http
GET /logs/search
```

Parameters:
- `start_time`: Start timestamp (ISO format)
- `end_time`: End timestamp (ISO format)
- `log_level`: (Optional) Filter by log level
- `source`: (Optional) Filter by log source

Example:
```bash
curl "http://localhost:8000/logs/search?start_time=2023-01-01T00:00:00&end_time=2023-01-02T00:00:00&log_level=ERROR"
```

#### Analyze Logs

```http
GET /logs/analyze
```

Parameters:
- `start_time`: (Optional) Start timestamp (ISO format)
- `end_time`: (Optional) End timestamp (ISO format)

If not specified, analyzes the last hour of logs.

Example:
```bash
curl "http://localhost:8000/logs/analyze"
```

## Architecture

The system consists of three main components:

1. **Log Collector**: Monitors and collects logs from configured sources
2. **Log Processor**: Normalizes and processes raw log entries
3. **Log Analyzer**: Uses GPT to analyze logs and extract insights

All components are managed by the Agent Manager, which coordinates their operation and provides the API interface.

## Configuration

Log sources can be configured in `config/log_sources.yaml`. The system supports various log source types and processing rules.

## Development

### Project Structure

```
src/
├── agent_manager/     # Agent coordination and management
├── log_pipeline/      # Log collection and processing
├── service_layer/     # API and service handlers
└── demo.py           # Demo application
```

### Adding New Features

1. Implement new collectors in `log_pipeline/collector.py`
2. Add processing rules in `log_pipeline/processor.py`
3. Extend analysis capabilities in `log_pipeline/analyzer.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.
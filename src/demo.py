"""Minimal demo script for the log monitoring agent.

This demo implements a simple log monitoring system with:
- File-based log collection
- Basic log normalization and processing
- GPT-powered log analysis
- REST API endpoints for querying results
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI
from agent_manager.manager import AgentManager, GPTConfig
from log_pipeline.collector import FileSystemCollector
from log_pipeline.processor import LogNormalizer
from log_pipeline.analyzer import GPTAnalyzer
from service_layer.service_handlers import LogEntry, QueryProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Log Monitoring Demo")

# Initialize components
gpt_config = GPTConfig(
    api_key="your-api-key-here",  # Replace with actual API key
    model_name="gpt-3.5-turbo",
    max_tokens=1000,
    temperature=0.7,
    batch_size=10
)

# Create demo log directory
log_dir = Path("./demo_logs")
log_dir.mkdir(exist_ok=True)

# Initialize pipeline components
collector = FileSystemCollector(str(log_dir))
processor = LogNormalizer()
analyzer = GPTAnalyzer(gpt_config.__dict__)

# Initialize agent manager
agent_manager = AgentManager(gpt_config)
agent_manager.register_component("collector", collector)
agent_manager.register_component("processor", processor)
agent_manager.register_component("analyzer", analyzer)

# Initialize query processor
query_processor = QueryProcessor()

@app.on_event("startup")
async def startup_event():
    """Start all components on application startup."""
    agent_manager.start()
    logger.info("Started Log Monitoring Demo")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop all components on application shutdown."""
    agent_manager.stop()
    logger.info("Stopped Log Monitoring Demo")

@app.get("/logs/search")
async def search_logs(
    start_time: datetime,
    end_time: datetime,
    log_level: str = None,
    source: str = None
) -> List[LogEntry]:
    """Search logs with filtering."""
    return await query_processor.search_logs(
        start_time=start_time,
        end_time=end_time,
        log_level=log_level,
        source=source
    )

@app.get("/logs/analyze")
async def analyze_logs(
    start_time: datetime = None,
    end_time: datetime = None
) -> Dict:
    """Analyze logs for patterns and insights."""
    if not start_time:
        start_time = datetime.now() - timedelta(hours=1)
    if not end_time:
        end_time = datetime.now()

    logs = await query_processor.search_logs(start_time, end_time)
    return await query_processor.analyze_logs(logs)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
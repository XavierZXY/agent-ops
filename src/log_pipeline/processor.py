\"""Log processor components for normalizing and enriching log entries."""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from datetime import datetime
import logging
import re

class LogProcessor(ABC):
    """Base class for all log processors."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._running = False

    @abstractmethod
    def start(self) -> None:
        """Start the log processing."""
        self._running = True

    @abstractmethod
    def stop(self) -> None:
        """Stop the log processing."""
        self._running = False

    @abstractmethod
    def process(self, log_entry: Dict) -> Optional[Dict]:
        """Process a single log entry.

        Args:
            log_entry: The log entry to process

        Returns:
            Optional[Dict]: The processed log entry, or None if entry should be filtered out
        """
        pass

class LogNormalizer(LogProcessor):
    """Processor for normalizing log format and extracting fields."""

    def __init__(self, timestamp_format: str = "%Y-%m-%d %H:%M:%S"):
        super().__init__()
        self.timestamp_format = timestamp_format
        self._timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?',
            r'\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}',
            r'\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}'
        ]

    def start(self) -> None:
        """Start the normalizer."""
        super().start()
        self.logger.info("Started log normalizer")

    def stop(self) -> None:
        """Stop the normalizer."""
        super().stop()
        self.logger.info("Stopped log normalizer")

    def process(self, log_entry: Dict) -> Optional[Dict]:
        """Normalize and enrich a log entry.

        Args:
            log_entry: The raw log entry

        Returns:
            Optional[Dict]: The normalized log entry with extracted fields
        """
        if not self._running or not log_entry:
            return None

        try:
            normalized = {
                'original_timestamp': log_entry.get('timestamp'),
                'source': log_entry.get('source'),
                'raw_content': log_entry.get('content')
            }

            # Extract and standardize timestamp
            content = log_entry.get('content', '')
            timestamp = self._extract_timestamp(content)
            if timestamp:
                normalized['timestamp'] = timestamp

            # Extract log level
            level = self._extract_log_level(content)
            if level:
                normalized['level'] = level

            # Extract message
            message = self._extract_message(content)
            if message:
                normalized['message'] = message

            return normalized

        except Exception as e:
            self.logger.error(f"Error processing log entry: {e}")
            return None

    def _extract_timestamp(self, content: str) -> Optional[str]:
        """Extract and normalize timestamp from log content."""
        for pattern in self._timestamp_patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    timestamp = datetime.strptime(match.group(), self.timestamp_format)
                    return timestamp.isoformat()
                except ValueError:
                    continue
        return None

    def _extract_log_level(self, content: str) -> Optional[str]:
        """Extract log level from content."""
        level_pattern = r'\b(DEBUG|INFO|WARN(?:ING)?|ERROR|CRITICAL|FATAL)\b'
        match = re.search(level_pattern, content)
        return match.group(1) if match else None

    def _extract_message(self, content: str) -> Optional[str]:
        """Extract the main message from log content."""
        # Remove timestamp and log level if present
        message = content
        for pattern in self._timestamp_patterns:
            message = re.sub(pattern, '', message)
        message = re.sub(r'\b(DEBUG|INFO|WARN(?:ING)?|ERROR|CRITICAL|FATAL)\b', '', message)
        return message.strip()
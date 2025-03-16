"""Log collector components for gathering logs from various sources."""

from abc import ABC, abstractmethod
from typing import Dict, Generator, Optional
from pathlib import Path
import time
import logging
import watchdog.observers
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

class LogCollector(ABC):
    """Base class for all log collectors."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._running = False

    @abstractmethod
    def start(self) -> None:
        """Start the log collection process."""
        self._running = True

    @abstractmethod
    def stop(self) -> None:
        """Stop the log collection process."""
        self._running = False

    @abstractmethod
    def collect(self) -> Generator[Dict, None, None]:
        """Collect logs from the source.

        Yields:
            Dict: Log entry containing timestamp, source, and content
        """
        pass

class FileSystemCollector(LogCollector):
    """Collector for monitoring and collecting logs from the file system."""

    def __init__(self, path: str, pattern: str = "*.log"):
        super().__init__()
        self.path = Path(path)
        self.pattern = pattern
        self._observer = None
        self._handler = None

    def start(self) -> None:
        """Start monitoring the file system for log changes."""
        super().start()
        self._handler = LogFileHandler(self)
        self._observer = watchdog.observers.Observer()
        self._observer.schedule(self._handler, str(self.path), recursive=False)
        self._observer.start()
        self.logger.info(f"Started monitoring {self.path} for pattern {self.pattern}")

    def stop(self) -> None:
        """Stop monitoring the file system."""
        if self._observer:
            self._observer.stop()
            self._observer.join()
        super().stop()
        self.logger.info("Stopped file system monitoring")

    def collect(self) -> Generator[Dict, None, None]:
        """Collect logs from monitored files.

        Yields:
            Dict: Log entry with timestamp, source, and content
        """
        if not self._running:
            return

        for file_path in self.path.glob(self.pattern):
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        yield {
                            'timestamp': time.time(),
                            'source': str(file_path),
                            'content': line.strip()
                        }
            except Exception as e:
                self.logger.error(f"Error reading file {file_path}: {e}")

class LogFileHandler(FileSystemEventHandler):
    """Handler for file system events related to log files."""

    def __init__(self, collector: FileSystemCollector):
        self.collector = collector
        self.logger = logging.getLogger(__name__)

    def on_modified(self, event: FileModifiedEvent) -> None:
        """Handle file modification events."""
        if not event.is_directory and Path(event.src_path).match(self.collector.pattern):
            self.logger.debug(f"Log file modified: {event.src_path}")
            # Trigger collection on modification
            for entry in self.collector.collect():
                # TODO: Implement buffer management and forwarding to processors
                pass
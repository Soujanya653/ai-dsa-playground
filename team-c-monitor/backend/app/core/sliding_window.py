"""
Sliding window implementation for streaming API log events.
"""

from collections import deque
from datetime import datetime, timedelta, timezone
from typing import Deque, List
import logging

from ..models import LogEvent

logger = logging.getLogger(__name__)

WINDOW_MINUTES = 2


class SlidingWindow:
    """
    Maintains a rolling time window of log events.
    """

    def __init__(self) -> None:
        self.events: Deque[LogEvent] = deque()

    def add(self, event: LogEvent) -> None:
        """
        Add a new log event to the sliding window.

        Args:
            event: A validated LogEvent instance.

        Raises:
            ValueError: If event timestamp is invalid.
        """
        if event.timestamp is None:
            raise ValueError("LogEvent timestamp cannot be None")

        try:
            self.events.append(event)
            self._evict_old_events()
        except Exception as exc:
            logger.exception("Failed to add event to sliding window")
            raise RuntimeError("Sliding window update failed") from exc

    def get_events(self) -> List[LogEvent]:
        """
        Return all events currently inside the rolling window.
        """
        try:
            self._evict_old_events()
            return list(self.events)
        except Exception as exc:
            logger.exception("Failed to retrieve events from sliding window")
            raise RuntimeError("Failed to retrieve sliding window events") from exc

    def _evict_old_events(self) -> None:
        """
        Remove events that fall outside the rolling time window.
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=WINDOW_MINUTES)

        # Events are ordered by arrival time
        while self.events and self.events[0].timestamp < cutoff_time:
            self.events.popleft()

from collections import deque
from datetime import datetime, timedelta, timezone
from typing import Deque, List
import logging
import pytest
from pydantic import ValidationError
from backend.app.core.sliding_window import SlidingWindow
from backend.app.models import LogEvent

WINDOW_MINUTES = 3 # Define this constant
def make_event(minutes_ago: int):
    """
    Helper to create a LogEvent with timestamp in the past.
    """
    return LogEvent(
        user_id="user123",
        endpoint="/chat",
        latency_ms=120,
        tokens_used=50,      # Changed from 'tokens' to 'tokens_used'
        is_error=False,       # Changed from 'success=True' to 'is_error=False'
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=minutes_ago),
    )

def test_add_valid_event():
    window = SlidingWindow()
    event = make_event(0)

    window.add(event)

    events = window.get_events()
    assert len(events) == 1
    assert events[0] == event


def test_event_evicted_when_outside_window():
    window = SlidingWindow()

    old_event = make_event(WINDOW_MINUTES + 1)
    window.add(old_event)

    events = window.get_events()
    assert len(events) == 0  # should be evicted


def test_recent_event_not_evicted():
    window = SlidingWindow()

    recent_event = make_event(WINDOW_MINUTES - 1)
    window.add(recent_event)

    events = window.get_events()
    assert len(events) == 1
    assert events[0] == recent_event


def test_mixed_old_and_new_events():
    window = SlidingWindow()

    old_event = make_event(WINDOW_MINUTES + 2)
    new_event = make_event(0)

    window.add(old_event)
    window.add(new_event)

    events = window.get_events()
    assert len(events) == 1
    assert events[0] == new_event

def test_add_event_with_none_timestamp_raises_error():
    window = SlidingWindow()

    # Test that Pydantic validation catches None timestamp
    with pytest.raises(ValidationError):  # Change from ValueError
        event = LogEvent(
            user_id="user123",
            endpoint="/chat",
            latency_ms=120,
            tokens_used=50,
            is_error=False,
            timestamp=None,
        )
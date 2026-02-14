from datetime import datetime, timezone
import pytest
import numpy as np
from collections import defaultdict

from backend.app.models import LogEvent
from backend.app.core.anomalies import (
    detect_anomalies,
    MIN_EVENTS_FOR_ANALYSIS,
    LATENCY_STD_MULTIPLIER,
    MAX_ERROR_RATE,
)

TOKEN_COST_PER_1K = 0.002  # Example value for testing


def make_event(
    user_id: str = "user123",
    endpoint: str = "/chat",
    latency_ms: int = 100,
    tokens_used: int = 50,
    is_error: bool = False,
):
    """Helper to create a LogEvent for testing."""
    return LogEvent(
        user_id=user_id,
        endpoint=endpoint,
        latency_ms=latency_ms,
        tokens_used=tokens_used,
        is_error=is_error,
        timestamp=datetime.now(timezone.utc),
    )


def make_metrics(events, window_minutes=1):
    """Generate realistic metrics dict for anomaly detection, safely handling empty events."""
    total_requests = len(events)
    latencies_ms = [event.latency_ms for event in events if hasattr(event, "latency_ms")]
    total_errors = sum(1 for event in events if getattr(event, "is_error", False))
    total_tokens = sum(getattr(event, "tokens_used", 0) for event in events)
    per_user_requests = defaultdict(int)
    for event in events:
        if hasattr(event, "user_id"):
            per_user_requests[event.user_id] += 1

    # Safely compute metrics with empty checks
    if latencies_ms:
        avg_latency = float(np.mean(latencies_ms))
        p50_latency = float(np.percentile(latencies_ms, 50))
        p95_latency = float(np.percentile(latencies_ms, 95))
        p99_latency = float(np.percentile(latencies_ms, 99))
    else:
        avg_latency = 0.0
        p50_latency = 0.0
        p95_latency = 0.0
        p99_latency = 0.0

    error_rate = total_errors / total_requests if total_requests > 0 else 0.0

    return {
        "requests_per_min": total_requests // window_minutes,
        "avg_latency": avg_latency,
        "p50_latency": p50_latency,
        "p95_latency": p95_latency,
        "p99_latency": p99_latency,
        "error_rate": error_rate,
        "tokens_per_min": total_tokens // window_minutes,
        "estimated_cost_usd": (total_tokens / 1000) * TOKEN_COST_PER_1K,
        "per_user_requests": dict(per_user_requests),
    }



class TestDetectAnomalies:
    """Test suite for detect_anomalies function."""

    def test_empty_events_list_returns_empty_list(self):
        result = detect_anomalies([], metrics=make_metrics([]))
        assert result == []

    def test_insufficient_events_returns_empty_list(self):
        events = [make_event() for _ in range(MIN_EVENTS_FOR_ANALYSIS - 1)]
        result = detect_anomalies(events, metrics=make_metrics(events))
        assert result == []

    def test_exactly_min_events_triggers_analysis(self):
        events = [make_event(latency_ms=100) for _ in range(MIN_EVENTS_FOR_ANALYSIS)]
        result = detect_anomalies(events, metrics=make_metrics(events))
        assert isinstance(result, list)

    def test_normal_latencies_no_anomaly(self):
        events = [make_event(latency_ms=100 + i) for i in range(20)]
        result = detect_anomalies(events, metrics=make_metrics(events))
        assert "CRITICAL: Latency spike detected" not in result
        assert "WARNING: High error rate detected" not in result

    def test_latency_spike_detected(self):
        events = [make_event(latency_ms=100) for _ in range(19)]
        events.append(make_event(latency_ms=1000))
        result = detect_anomalies(events, metrics=make_metrics(events))
        assert "CRITICAL: Latency spike detected" in result

    def test_latency_spike_with_variation(self):
        latencies = [100, 110, 90, 105, 95, 100, 108, 92, 97, 103,
                     101, 99, 106, 94, 102, 98, 104, 96, 100, 1000]
        events = [make_event(latency_ms=lat) for lat in latencies]
        result = detect_anomalies(events, metrics=make_metrics(events))
        assert "CRITICAL: Latency spike detected" in result

    def test_no_latency_spike_within_threshold(self):
        latencies = [100, 110, 120, 105, 95, 100, 115, 92, 97, 103,
                     101, 99, 106, 94, 102, 98, 104, 96, 100, 108]
        events = [make_event(latency_ms=lat) for lat in latencies]
        result = detect_anomalies(events, metrics=make_metrics(events))
        assert "CRITICAL: Latency spike detected" not in result

    def test_high_error_rate_detected(self):
        events = [make_event(is_error=i < 5) for i in range(20)]  # 25% error
        result = detect_anomalies(events, metrics=make_metrics(events))
        assert "WARNING: High error rate detected" in result

    def test_error_rate_at_threshold_not_detected(self):
        num_errors = int(20 * MAX_ERROR_RATE)
        events = [make_event(is_error=i < num_errors) for i in range(20)]
        result = detect_anomalies(events, metrics=make_metrics(events))
        assert "WARNING: High error rate detected" not in result

    def test_error_rate_just_above_threshold_detected(self):
        num_errors = int(20 * MAX_ERROR_RATE) + 1
        events = [make_event(is_error=i < num_errors) for i in range(20)]
        result = detect_anomalies(events, metrics=make_metrics(events))
        assert "WARNING: High error rate detected" in result

    def test_low_error_rate_not_detected(self):
        events = [make_event(is_error=False) for _ in range(19)]
        events.append(make_event(is_error=True))
        result = detect_anomalies(events, metrics=make_metrics(events))
        assert "WARNING: High error rate detected" not in result

    def test_no_errors_no_anomaly(self):
        events = [make_event(is_error=False) for _ in range(20)]
        result = detect_anomalies(events, metrics=make_metrics(events))
        assert "WARNING: High error rate detected" not in result

    def test_all_errors_detected(self):
        events = [make_event(is_error=True) for _ in range(20)]
        result = detect_anomalies(events, metrics=make_metrics(events))
        assert "WARNING: High error rate detected" in result

    def test_both_anomalies_detected(self):
        events = []
        for i in range(20):
            is_error = i < 6  # 30% error rate
            latency = 1000 if i == 19 else 100
            events.append(make_event(latency_ms=latency, is_error=is_error))
        result = detect_anomalies(events, metrics=make_metrics(events))
        assert "CRITICAL: Latency spike detected" in result
        assert "WARNING: High error rate detected" in result
        assert len(result) == 2

    def test_no_anomalies_detected(self):
        events = [make_event(latency_ms=100 + i, is_error=False) for i in range(20)]
        result = detect_anomalies(events, metrics=make_metrics(events))
        assert result == []

    def test_invalid_event_structure_raises_value_error(self):
        class InvalidEvent:
            pass
        events = [InvalidEvent() for _ in range(MIN_EVENTS_FOR_ANALYSIS)]
        with pytest.raises(ValueError, match="Invalid log event structure"):
            detect_anomalies(events, metrics=make_metrics([]))

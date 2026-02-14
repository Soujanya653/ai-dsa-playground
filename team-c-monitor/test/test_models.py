import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from backend.app.models import LogEvent, MetricsResponse


def test_log_event_valid():
    event = LogEvent(
        timestamp=datetime.now(timezone.utc),
        user_id="alice",
        latency_ms=120,
        tokens_used=300,
        is_error=False,
    )

    assert event.user_id == "alice"
    assert event.latency_ms == 120
    assert event.is_error is False




def test_log_event_invalid_latency():
    with pytest.raises(ValidationError):
        LogEvent(
            timestamp=datetime.now(timezone.utc),
            user_id="alice",
            latency_ms=-10,   # ❌ invalid
            tokens_used=100,
            is_error=False,
        )




def test_log_event_empty_user_id():
    with pytest.raises(ValidationError):
        LogEvent(
            timestamp=datetime.now(timezone.utc),
            user_id="",       # ❌ min_length=1
            latency_ms=100,
            tokens_used=50,
            is_error=False,
        )

def test_log_event_negative_tokens():
    with pytest.raises(ValidationError):
        LogEvent(
            timestamp=datetime.now(timezone.utc),
            user_id="bob",
            latency_ms=200,
            tokens_used=-5,   # ❌ ge=0
            is_error=False,
        )
def test_metrics_response_valid():
    metrics = MetricsResponse(
        requests_per_min=10,
        avg_latency=120.5,
        p50_latency=100.0,
        p95_latency=300.0,
        p99_latency=500.0,
        error_rate=0.1,
        tokens_per_min=2000,
        estimated_cost_usd=0.004,
        per_user_requests={"alice": 5, "bob": 5},
        anomalies=["WARNING: High error rate"],
    )

    assert metrics.requests_per_min == 10
    assert metrics.error_rate == 0.1
    assert isinstance(metrics.anomalies, list)
def test_metrics_response_invalid_error_rate():
    with pytest.raises(ValidationError):
        MetricsResponse(
            requests_per_min=10,
            avg_latency=100,
            p50_latency=90,
            p95_latency=200,
            p99_latency=300,
            error_rate=1.5,  # ❌ > 1.0
            tokens_per_min=1000,
            estimated_cost_usd=0.002,
            per_user_requests={"alice": 10},
            anomalies=[],
        )
def test_metrics_response_missing_field():
    with pytest.raises(ValidationError):
        MetricsResponse(
            requests_per_min=10,
            avg_latency=100,
            p50_latency=90,
            p95_latency=200,
            p99_latency=300,
            error_rate=0.1,
            tokens_per_min=1000,
            # ❌ estimated_cost_usd missing
            per_user_requests={"alice": 10},
            anomalies=[],
        )

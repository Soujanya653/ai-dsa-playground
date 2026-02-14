"""
Unit tests for metric computation utilities.
"""

from datetime import datetime, timezone
import pytest
import numpy as np

from backend.app.models import LogEvent
from backend.app.core.metrics import compute_metrics, TOKEN_COST_PER_1K


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


class TestComputeMetrics:
    """Test suite for compute_metrics function."""

    def test_empty_events_list_returns_empty_dict(self):
        """Should return empty dict when no events provided."""
        result = compute_metrics([])
        assert result == {}

    def test_invalid_window_minutes_raises_value_error(self):
        """Should raise ValueError for invalid window_minutes."""
        events = [make_event()]
        
        with pytest.raises(ValueError, match="window_minutes must be a positive integer"):
            compute_metrics(events, window_minutes=0)
        
        with pytest.raises(ValueError, match="window_minutes must be a positive integer"):
            compute_metrics(events, window_minutes=-5)

    def test_single_event_computes_basic_metrics(self):
        """Should compute correct metrics for a single event."""
        events = [make_event(latency_ms=200, tokens_used=100)]
        
        result = compute_metrics(events, window_minutes=5)
        
        assert result["requests_per_min"] == 0  # 1 // 5 = 0
        assert result["avg_latency"] == 200.0
        assert result["p50_latency"] == 200.0
        assert result["p95_latency"] == 200.0
        assert result["p99_latency"] == 200.0
        assert result["error_rate"] == 0.0
        assert result["tokens_per_min"] == 20  # 100 // 5
        assert result["estimated_cost_usd"] == (100 / 1000) * TOKEN_COST_PER_1K
        assert result["per_user_requests"] == {"user123": 1}

    def test_multiple_events_same_user(self):
        """Should aggregate metrics correctly for same user."""
        events = [
            make_event(latency_ms=100, tokens_used=50),
            make_event(latency_ms=200, tokens_used=100),
            make_event(latency_ms=300, tokens_used=150),
        ]
        
        result = compute_metrics(events, window_minutes=1)
        
        assert result["requests_per_min"] == 3
        assert result["avg_latency"] == 200.0
        assert result["tokens_per_min"] == 300  # (50 + 100 + 150) // 1
        assert result["error_rate"] == 0.0
        assert result["per_user_requests"] == {"user123": 3}

    def test_multiple_users(self):
        """Should track requests per user correctly."""
        events = [
            make_event(user_id="user1", latency_ms=100),
            make_event(user_id="user1", latency_ms=150),
            make_event(user_id="user2", latency_ms=200),
            make_event(user_id="user3", latency_ms=250),
        ]
        
        result = compute_metrics(events, window_minutes=2)
        
        assert result["requests_per_min"] == 2  # 4 // 2
        assert result["per_user_requests"] == {
            "user1": 2,
            "user2": 1,
            "user3": 1,
        }

    def test_error_rate_calculation(self):
        """Should calculate error rate correctly."""
        events = [
            make_event(is_error=False),
            make_event(is_error=True),
            make_event(is_error=False),
            make_event(is_error=True),
        ]
        
        result = compute_metrics(events, window_minutes=1)
        
        assert result["error_rate"] == 0.5  # 2 errors out of 4 requests
        assert result["requests_per_min"] == 4

    def test_all_errors(self):
        """Should handle case where all requests are errors."""
        events = [
            make_event(is_error=True),
            make_event(is_error=True),
            make_event(is_error=True),
        ]
        
        result = compute_metrics(events, window_minutes=1)
        
        assert result["error_rate"] == 1.0

    def test_no_errors(self):
        """Should handle case where no requests are errors."""
        events = [
            make_event(is_error=False),
            make_event(is_error=False),
        ]
        
        result = compute_metrics(events, window_minutes=1)
        
        assert result["error_rate"] == 0.0

    def test_latency_percentiles(self):
        """Should calculate latency percentiles correctly."""
        # Create events with known latencies for easy verification
        latencies = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
        events = [make_event(latency_ms=lat) for lat in latencies]
        
        result = compute_metrics(events, window_minutes=1)
        
        assert result["avg_latency"] == 550.0
        assert result["p50_latency"] == 550.0
        # p95 and p99 will be close to the higher values
        assert result["p95_latency"] >= 900
        assert result["p99_latency"] >= 990

    def test_cost_estimation(self):
        """Should estimate cost correctly based on token usage."""
        events = [
            make_event(tokens_used=1000),  # 1K tokens
            make_event(tokens_used=500),   # 0.5K tokens
        ]
        
        result = compute_metrics(events, window_minutes=1)
        
        expected_cost = (1500 / 1000) * TOKEN_COST_PER_1K
        assert result["estimated_cost_usd"] == expected_cost
        assert result["tokens_per_min"] == 1500

    def test_large_window_minutes(self):
        """Should handle large window values correctly."""
        events = [make_event(tokens_used=100) for _ in range(100)]
        
        result = compute_metrics(events, window_minutes=60)
        
        assert result["requests_per_min"] == 1  # 100 // 60
        assert result["tokens_per_min"] == 166  # 10000 // 60

    def test_invalid_event_structure_raises_value_error(self):
        """Should raise ValueError for events with missing fields."""
        # Create a mock object that looks like a LogEvent but missing fields
        class InvalidEvent:
            pass
        
        events = [InvalidEvent()]
        
        with pytest.raises(ValueError, match="Invalid log event structure"):
            compute_metrics(events, window_minutes=5)

    def test_mixed_endpoints(self):
        """Should aggregate across different endpoints."""
        events = [
            make_event(endpoint="/chat", latency_ms=100),
            make_event(endpoint="/completion", latency_ms=200),
            make_event(endpoint="/embedding", latency_ms=300),
        ]
        
        result = compute_metrics(events, window_minutes=1)
        
        # Endpoints don't affect aggregation in current implementation
        assert result["requests_per_min"] == 3
        assert result["avg_latency"] == 200.0

    def test_zero_tokens_used(self):
        """Should handle events with zero tokens."""
        events = [make_event(tokens_used=0) for _ in range(5)]
        
        result = compute_metrics(events, window_minutes=1)
        
        assert result["tokens_per_min"] == 0
        assert result["estimated_cost_usd"] == 0.0

    def test_very_high_latencies(self):
        """Should handle very high latency values."""
        events = [
            make_event(latency_ms=10000),
            make_event(latency_ms=20000),
            make_event(latency_ms=30000),
        ]
        
        result = compute_metrics(events, window_minutes=1)
        
        assert result["avg_latency"] == 20000.0
        assert result["p99_latency"] == pytest.approx(29800.0, rel=1e-2)

    def test_single_window_minute(self):
        """Should work correctly with window_minutes=1."""
        events = [make_event(tokens_used=100) for _ in range(10)]
        
        result = compute_metrics(events, window_minutes=1)
        
        assert result["requests_per_min"] == 10
        assert result["tokens_per_min"] == 1000

    def test_returns_all_expected_keys(self):
        """Should return all expected metric keys."""
        events = [make_event()]
        
        result = compute_metrics(events, window_minutes=1)
        
        expected_keys = {
            "requests_per_min",
            "avg_latency",
            "p50_latency",
            "p95_latency",
            "p99_latency",
            "error_rate",
            "tokens_per_min",
            "estimated_cost_usd",
            "per_user_requests",
        }
        
        assert set(result.keys()) == expected_keys

    def test_per_user_requests_with_many_users(self):
        """Should track many users correctly."""
        events = [make_event(user_id=f"user{i}") for i in range(100)]
        
        result = compute_metrics(events, window_minutes=1)
        
        assert len(result["per_user_requests"]) == 100
        for user_id, count in result["per_user_requests"].items():
            assert count == 1

    def test_consistent_results_with_same_input(self):
        """Should produce consistent results for same input."""
        events = [
            make_event(latency_ms=100 + i, tokens_used=50 + i)
            for i in range(10)
        ]
        
        result1 = compute_metrics(events, window_minutes=5)
        result2 = compute_metrics(events, window_minutes=5)
        
        assert result1 == result2
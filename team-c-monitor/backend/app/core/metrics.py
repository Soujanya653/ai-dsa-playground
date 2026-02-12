"""
Metric computation utilities for the AI API Usage Monitor.

This module provides pure functions for aggregating metrics
from streaming API log events over a rolling time window.

Design principles:
- Stateless, deterministic computations
- No framework or I/O dependencies
- Safe for unit testing
"""

from collections import defaultdict
from typing import Dict, List
import logging

import numpy as np

from ..models import *

logger = logging.getLogger(__name__)

# Example cost model (USD per 1K tokens)
TOKEN_COST_PER_1K = 0.002


def compute_metrics(events: List[LogEvent], window_minutes: int = 2) -> Dict[str, float]:
    """
    Compute aggregated metrics over a rolling time window.

    Args:
        events: List of LogEvent objects currently inside the time window.
        window_minutes: Duration of the rolling window in minutes.
            Used to normalize per-minute metrics.

    Returns:
        Aggregated metrics dictionary.

    Raises:
        ValueError: If inputs are invalid.
        RuntimeError: If metric computation fails unexpectedly.
    """
    # ---- Guard clauses ----
    if not events:
        return {}

    if window_minutes <= 0:
        raise ValueError("window_minutes must be a positive integer")

    try:
        latencies_ms = [event.latency_ms for event in events]
        total_requests = len(events)
        total_errors = sum(event.is_error for event in events)
        total_tokens = sum(event.tokens_used for event in events)

        per_user_requests: Dict[str, int] = defaultdict(int)
        for event in events:
            per_user_requests[event.user_id] += 1

        return {
            "requests_per_min": total_requests // window_minutes,
            "avg_latency": float(np.mean(latencies_ms)),
            "p50_latency": float(np.percentile(latencies_ms, 50)),
            "p95_latency": float(np.percentile(latencies_ms, 95)),
            "p99_latency": float(np.percentile(latencies_ms, 99)),
            "error_rate": total_errors / total_requests,
            "tokens_per_min": total_tokens // window_minutes,
            "estimated_cost_usd": (total_tokens / 1000) * TOKEN_COST_PER_1K,
            "per_user_requests": dict(per_user_requests),
        }

    except AttributeError as exc:
        # Contract violation: event missing expected fields
        logger.exception("Invalid LogEvent structure in compute_metrics")
        raise ValueError("Invalid log event structure") from exc

    except Exception as exc:
        # Defensive catch: numpy/runtime errors
        logger.exception("Unexpected error during metric computation")
        raise RuntimeError("Metric computation failed") from exc

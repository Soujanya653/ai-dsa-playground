from typing import List
import numpy as np
import logging
from ..models import *

logger = logging.getLogger(__name__)

# ---- Anomaly Detection Thresholds ----
MIN_EVENTS_FOR_ANALYSIS = 5
LATENCY_STD_MULTIPLIER = 3
MAX_ERROR_RATE = 0.10


def detect_anomalies(events: List["LogEvent"], metrics: dict) -> List[str]:
    """
    Detect anomalies in a list of log events based on latency and error rate.

    Anomalies detected:
    - Latency spikes (greater than mean + N * std deviation)
    - High error rate exceeding defined threshold

    Args:
        events: Sliding window log events.

    Returns:
        Human-readable anomaly descriptions.

    Raises:
        ValueError: If events contain invalid data.
    """
    anomalies: List[str] = []

    # ---- Guard clause ----
    if not events or len(events) < MIN_EVENTS_FOR_ANALYSIS:
        return anomalies

    try:
        latencies = np.array([event.latency_ms for event in events])

        mean_latency = float(np.mean(latencies))
        std_latency = float(np.std(latencies))

        if latencies.max() > mean_latency + (LATENCY_STD_MULTIPLIER * std_latency):
            anomalies.append("CRITICAL: Latency spike detected")

        
        
        error_rate = metrics.get("error_rate", 0.0)

        if error_rate > MAX_ERROR_RATE:
            anomalies.append("WARNING: High error rate detected")

    except AttributeError as exc:
        # Programmer / data contract error
        logger.exception("Malformed LogEvent detected in anomaly detection")
        raise ValueError("Invalid log event structure") from exc

    except Exception as exc:
        # Unexpected failure (numpy, runtime, etc.)
        logger.exception("Unexpected error during anomaly detection")
        anomalies.append("ERROR: Anomaly detection failed")

    return anomalies

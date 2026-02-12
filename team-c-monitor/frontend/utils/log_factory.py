from datetime import datetime, timezone
import random


def build_log(latency_ms=None, tokens_used=None, is_error=None):
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": f"user_{random.randint(1,5)}",
        "latency_ms": latency_ms if latency_ms is not None else random.randint(100, 1200),
        "tokens_used": tokens_used if tokens_used is not None else random.randint(50, 800),
        "is_error": is_error if is_error is not None else (random.random() < 0.1),
    }

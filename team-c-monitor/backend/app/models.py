"""
Pydantic data models for the AI API Usage Monitor.

These models define:
- The structure of incoming API log events
- The structure of metrics and anomaly data returned to clients

They are used by FastAPI for:
- Request validation
- Response validation
- Automatic API documentation (OpenAPI / Swagger)
"""

from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel, Field


class LogEvent(BaseModel):
    """
    Represents a single API usage log event.

    Each event corresponds to one request made to the AI API
    and is used for computing rolling metrics and detecting anomalies.
    """

    timestamp: datetime = Field(
        ...,
        description="UTC timestamp when the API request was received"
    )

    user_id: str = Field(
        ...,
        min_length=1,
        description="Unique identifier of the user making the API request"
    )

    latency_ms: int = Field(
        ...,
        gt=0,
        description="Time taken to process the request in milliseconds"
    )

    tokens_used: int = Field(
        ...,
        ge=0,
        description="Number of tokens consumed by the API request"
    )

    is_error: bool = Field(
        ...,
        description="Indicates whether the API request resulted in an error"
    )


class MetricsResponse(BaseModel):
    """
    Aggregated metrics and anomaly information computed over
    a rolling time window.

    This model is returned by the /metrics endpoint and consumed
    by the monitoring dashboard.
    """

    requests_per_min: int = Field(
        ...,
        ge=0,
        description="Average number of API requests per minute in the time window"
    )

    avg_latency: float = Field(
        ...,
        ge=0,
        description="Average latency (in milliseconds) of API requests"
    )

    p50_latency: float = Field(
        ...,
        ge=0,
        description="Median (P50) latency in milliseconds"
    )

    p95_latency: float = Field(
        ...,
        ge=0,
        description="95th percentile latency in milliseconds"
    )

    p99_latency: float = Field(
        ...,
        ge=0,
        description="99th percentile latency in milliseconds"
    )

    error_rate: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Fraction of API requests that resulted in errors"
    )

    tokens_per_min: int = Field(
        ...,
        ge=0,
        description="Average number of tokens consumed per minute"
    )

    estimated_cost_usd: float = Field(
        ...,
        ge=0,
        description="Estimated cost in USD for token usage in the time window"
    )

    per_user_requests: Dict[str, int] = Field(
        ...,
        description="Mapping of user_id to number of API requests"
    )

    anomalies: List[str] = Field(
        ...,
        description="List of detected anomalies with severity labels"
    )

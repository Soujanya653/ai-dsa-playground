from fastapi import FastAPI, HTTPException
from .models import LogEvent, MetricsResponse
from .core.sliding_window import SlidingWindow
from .core.metrics import compute_metrics
from .core.anomalies import detect_anomalies

app = FastAPI(
    title="AI API Monitor",
    version="1.0.0",
    description="Real-time monitoring service for AI API usage and performance"
)

sliding_window = SlidingWindow()


@app.post("/ingest", status_code=201)
def ingest_log(event: LogEvent) -> dict:
    """
    Ingests a single API log event into the monitoring window.
    """
    try:
        sliding_window.add(event)
        return {"status": "ok"}

    except ValueError as e:
        # Known, expected errors
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        # Unexpected system error
        raise HTTPException(
            status_code=500,
            detail="Failed to ingest log event"
        )


@app.get("/metrics", response_model=MetricsResponse)
def get_metrics() -> MetricsResponse:
    """
    Returns aggregated metrics and detected anomalies
    for the current sliding window.
    """
    try:
        events = sliding_window.get_events()

        if not events:
            raise HTTPException(
                status_code=404,
                detail="No metrics available yet"
            )

        metrics = compute_metrics(events)
        anomalies = detect_anomalies(events ,metrics)

        return MetricsResponse(
            **metrics,
            anomalies=anomalies
        )

    except HTTPException:
        # Re-raise FastAPI HTTP errors unchanged
        raise

    except ValueError as e:
        # Calculation or data-related error
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        # Any unexpected failure
        raise HTTPException(
            status_code=500,
            detail="Failed to compute metrics"
        )

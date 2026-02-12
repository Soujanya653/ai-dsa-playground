import requests

API_URL = "http://localhost:8000"


REQUEST_TIMEOUT = 3
DEFAULT_TIMEOUT = 1


def send_log(log: dict, timeout: float | None = None) -> bool:
    try:
        final_timeout = (
            timeout
            if timeout is not None
            else REQUEST_TIMEOUT
            if REQUEST_TIMEOUT is not None
            else DEFAULT_TIMEOUT
        )

        requests.post(
            f"{API_URL}/ingest",
            json=log,
            timeout=final_timeout
        )

        return True

    except requests.RequestException:
        return False





def fetch_metrics(timeout: int | None = None) -> dict | None:
    try:
        response = requests.get(
            f"{API_URL}/metrics",
            timeout=timeout or REQUEST_TIMEOUT or 1
        )

        if response.status_code == 200:
            return response.json()

        return {}

    except requests.RequestException:
        return None

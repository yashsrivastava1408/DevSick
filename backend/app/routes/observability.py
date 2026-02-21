"""Observability endpoints backed by Prometheus."""
from typing import Optional
import httpx
from fastapi import APIRouter

from ..config import settings

router = APIRouter(prefix="/api/observability", tags=["Observability"])


def _parse_scalar_value(result: dict) -> Optional[float]:
    """Parse Prometheus query scalar result."""
    value = result.get("value")
    if not value or len(value) < 2:
        return None
    try:
        return float(value[1])
    except (TypeError, ValueError):
        return None


async def _query_prometheus(client: httpx.AsyncClient, query: str) -> Optional[float]:
    """Run a single instant query and return the first scalar value."""
    response = await client.get(
        f"{settings.PROMETHEUS_URL}/api/v1/query",
        params={"query": query},
    )
    response.raise_for_status()
    payload = response.json()

    if payload.get("status") != "success":
        return None

    results = payload.get("data", {}).get("result", [])
    if not results:
        return None

    return _parse_scalar_value(results[0])


@router.get("/summary")
async def get_observability_summary():
    """Return live backend metrics from Prometheus with graceful fallback."""
    metrics = {
        "backend_up": None,
        "requests_per_second": None,
        "error_rate_per_second": None,
        "p95_latency_seconds": None,
        "source": "prometheus",
    }
    errors = []

    queries = {
        "backend_up": 'max(up{job="devsick-backend"})',
        "requests_per_second": 'sum(rate(http_requests_total{job="devsick-backend"}[5m]))',
        "error_rate_per_second": 'sum(rate(http_requests_total{job="devsick-backend",status=~"5.."}[5m]))',
        "p95_latency_seconds": (
            'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket'
            '{job="devsick-backend"}[5m])) by (le))'
        ),
    }

    try:
        timeout = httpx.Timeout(settings.PROMETHEUS_TIMEOUT_SECONDS)
        async with httpx.AsyncClient(timeout=timeout) as client:
            for key, query in queries.items():
                try:
                    metrics[key] = await _query_prometheus(client, query)
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{key}: {exc.__class__.__name__}")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"prometheus_connection: {exc.__class__.__name__}")
        metrics["source"] = "fallback"

    metrics["healthy"] = metrics["backend_up"] is not None and metrics["backend_up"] >= 1
    if errors:
        metrics["warnings"] = errors

    return metrics

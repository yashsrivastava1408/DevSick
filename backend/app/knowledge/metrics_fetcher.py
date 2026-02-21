"""Service to fetch Prometheus metrics for AI analysis."""
import httpx
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from ..config import settings

logger = logging.getLogger(__name__)

class MetricsFetcher:
    """Fetches relevant infrastructure metrics for a given time window."""
    
    async def get_incident_metrics(self, timestamp: datetime, window_minutes: int = 5) -> Dict[str, Any]:
        """Fetch a snapshot of metrics around a specific timestamp."""
        start = timestamp - timedelta(minutes=window_minutes)
        end = timestamp + timedelta(minutes=1)
        
        # Convert to Prometheus timestamp format (seconds)
        start_ts = int(start.timestamp())
        end_ts = int(end.timestamp())
        
        queries = {
            "cpu_usage": 'sum(rate(node_cpu_seconds_total{mode!="idle"}[1m])) by (instance)',
            "memory_usage": 'node_memory_Active_bytes / node_memory_MemTotal_bytes',
            "request_rate": 'sum(rate(http_requests_total[1m])) by (service)',
            "error_rate": 'sum(rate(http_requests_total{status=~"5.."}[1m])) by (service)',
            "latency_p95": 'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[1m])) by (le, service))'
        }
        
        results = {}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for name, query in queries.items():
                try:
                    response = await client.get(
                        f"{settings.PROMETHEUS_URL}/api/v1/query",
                        params={"query": query, "time": end_ts}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        results[name] = data.get("data", {}).get("result", [])
                except Exception as e:
                    logger.error(f"Error fetching metric {name}: {e}")
                    results[name] = []
        
        return results

metrics_fetcher = MetricsFetcher()

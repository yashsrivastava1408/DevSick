"""Service to poll logs from Loki and ingest them into Devsick."""
import asyncio
import httpx
import logging
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Session

from ..config import settings
from .log_ingestor import event_store
from ..models.events import LogEventCreate, SeverityLevel
from ..database import engine
from ..knowledge.dependency_graph import dependency_graph

logger = logging.getLogger(__name__)

class LokiPoller:
    """Polls Loki for new log events and pushes them to the event store."""
    
    def __init__(self, loki_url: str = "http://loki:3100"):
        self.loki_url = loki_url
        self.last_sync_time: Optional[int] = None # Nanoseconds since epoch
        self.running = False

    def _determine_severity(self, message: str) -> SeverityLevel:
        """Simple heuristic to determine log severity."""
        message_low = message.lower()
        if any(w in message_low for w in ["fatal", "panic", "emergency"]):
            return SeverityLevel.CRITICAL
        if any(w in message_low for w in ["error", "err"]):
            return SeverityLevel.ERROR
        if any(w in message_low for w in ["warn", "warning"]):
            return SeverityLevel.WARNING
        return SeverityLevel.INFO

    async def poll(self):
        """Infinite polling loop."""
        self.running = True
        logger.info(f"Starting Loki poller targeting {self.loki_url}")
        
        async with httpx.AsyncClient() as client:
            while self.running:
                try:
                    # Query for any container log
                    query = '{container=~".+"}'
                    params = {
                        "query": query,
                        "limit": 100
                    }
                    if self.last_sync_time:
                        params["start"] = self.last_sync_time + 1
                    
                    response = await client.get(f"{self.loki_url}/loki/api/v1/query_range", params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get("data", {}).get("result", [])
                        
                        max_ts = self.last_sync_time or 0
                        
                        with Session(engine) as session:
                            for res in results:
                                stream_info = res.get("stream", {})
                                container = stream_info.get("container", "unknown")
                                
                                # Register service in dependency graph
                                dependency_graph.add_node(container, container)
                                
                                for val in res.get("values", []):
                                    ts_ns = int(val[0])
                                    message = val[1]
                                    
                                    # Simple heuristic for dependency discovery
                                    # Example: "Calling auth-service..."
                                    if "calling" in message.lower():
                                        for node_id in dependency_graph.nodes.keys():
                                            if node_id in message.lower() and node_id != container:
                                                dependency_graph.add_edge(container, node_id)
                                    
                                    if ts_ns > max_ts:
                                        max_ts = ts_ns
                                        
                                    # Ingest event
                                    event = LogEventCreate(
                                        source_service=container,
                                        severity=self._determine_severity(message),
                                        message=message,
                                        timestamp=datetime.fromtimestamp(ts_ns / 1_000_000_000, tz=timezone.utc),
                                        metadata=stream_info
                                    )
                                    event_store.ingest(session, event)
                            
                            session.commit()
                        
                        if max_ts > 0:
                            self.last_sync_time = max_ts
                            
                except Exception as e:
                    logger.error(f"Error polling Loki: {e}")
                
                await asyncio.sleep(5) # Poll every 5 seconds

    def stop(self):
        self.running = False

loki_poller = LokiPoller()

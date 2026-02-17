"""Log ingestion API endpoints."""
from fastapi import APIRouter, HTTPException
from typing import List
from ..models.events import LogEventCreate, LogEvent
from ..ingestion.log_ingestor import event_store

router = APIRouter(prefix="/api", tags=["Ingestion"])


@router.post("/ingest", response_model=LogEvent)
async def ingest_event(event: LogEventCreate):
    """Ingest a single log event."""
    stored = event_store.ingest(event)
    return stored


@router.post("/ingest/batch", response_model=List[LogEvent])
async def ingest_batch(events: List[LogEventCreate]):
    """Ingest multiple log events at once."""
    stored = event_store.ingest_batch(events)
    return stored


@router.get("/events", response_model=List[LogEvent])
async def get_events():
    """Get all ingested events."""
    return event_store.get_all()


@router.get("/events/count")
async def get_event_count():
    """Get total count of ingested events."""
    return {"count": event_store.count}

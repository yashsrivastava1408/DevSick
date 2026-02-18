"""Log ingestion API endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlmodel import Session
from ..models.events import LogEventCreate, LogEvent
from ..ingestion.log_ingestor import event_store
from ..database import get_session

router = APIRouter(prefix="/api", tags=["Ingestion"])


@router.post("/ingest", response_model=LogEvent)
async def ingest_event(event: LogEventCreate, session: Session = Depends(get_session)):
    """Ingest a single log event."""
    stored = event_store.ingest(session, event)
    return stored


@router.post("/ingest/batch", response_model=List[LogEvent])
async def ingest_batch(events: List[LogEventCreate], session: Session = Depends(get_session)):
    """Ingest multiple log events at once."""
    stored = event_store.ingest_batch(session, events)
    return stored


@router.get("/events", response_model=List[LogEvent])
async def get_events(session: Session = Depends(get_session)):
    """Get all ingested events."""
    return event_store.get_all(session)


@router.get("/events/count")
async def get_event_count(session: Session = Depends(get_session)):
    """Get total count of ingested events."""
    return {"count": event_store.count(session)}

"""Log and event ingestion layer.

Receives raw log events, validates them, and stores them in the database.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlmodel import Session, select
from ..models.events import LogEvent, LogEventCreate


class EventStore:
    """Database-backed event store for ingested log events."""

    def ingest(self, session: Session, event_data: LogEventCreate) -> LogEvent:
        """Validate and store a new log event."""
        # Map Pydantic API model to SQLModel DB entity
        event = LogEvent(
            source_service=event_data.source_service,
            severity=event_data.severity,
            message=event_data.message,
            timestamp=event_data.timestamp or datetime.utcnow(),
        )
        # Use property setter to handle JSON serialization
        event.event_metadata = event_data.metadata
        
        session.add(event)
        session.commit()
        session.refresh(event)
        return event

    def ingest_batch(self, session: Session, events: List[LogEventCreate]) -> List[LogEvent]:
        """Ingest multiple events at once."""
        return [self.ingest(session, e) for e in events]

    def get_all(self, session: Session) -> List[LogEvent]:
        """Return all stored events."""
        return session.exec(select(LogEvent)).all()

    def get_by_service(self, session: Session, service: str) -> List[LogEvent]:
        """Return events filtered by source service."""
        statement = select(LogEvent).where(LogEvent.source_service == service)
        return session.exec(statement).all()

    def get_by_id(self, session: Session, event_id: str) -> Optional[LogEvent]:
        """Return a specific event by ID."""
        return session.get(LogEvent, event_id)

    def get_recent(self, session: Session, window_seconds: int = 60) -> List[LogEvent]:
        """Return events within the specified time window."""
        cutoff = datetime.utcnow() - timedelta(seconds=window_seconds)
        statement = select(LogEvent).where(LogEvent.timestamp >= cutoff)
        return session.exec(statement).all()

    def clear(self, session: Session):
        """Clear all stored events."""
        # Using delete statement
        # statement = delete(LogEvent)
        # session.exec(statement)
        # session.commit()
        pass  # Disabled for safety in DB mode, or implement if needed

    def count(self, session: Session) -> int:
        # Optimization: Use select(func.count())
        # For now, simplistic length check of all items (not efficient but matches interface)
        return len(self.get_all(session))


# Global singleton
event_store = EventStore()

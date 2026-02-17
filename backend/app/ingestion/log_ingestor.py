"""Log and event ingestion layer.

Receives raw log events, validates them, stores them in-memory,
and triggers correlation when thresholds are reached.
"""
from datetime import datetime
from typing import List, Optional
from ..models.events import LogEvent, LogEventCreate


class EventStore:
    """In-memory event store for ingested log events."""

    def __init__(self):
        self._events: List[LogEvent] = []

    def ingest(self, event_data: LogEventCreate) -> LogEvent:
        """Validate and store a new log event."""
        event = LogEvent(
            source_service=event_data.source_service,
            severity=event_data.severity,
            message=event_data.message,
            metadata=event_data.metadata,
            timestamp=event_data.timestamp or datetime.utcnow(),
        )
        self._events.append(event)
        return event

    def ingest_batch(self, events: List[LogEventCreate]) -> List[LogEvent]:
        """Ingest multiple events at once."""
        return [self.ingest(e) for e in events]

    def get_all(self) -> List[LogEvent]:
        """Return all stored events."""
        return list(self._events)

    def get_by_service(self, service: str) -> List[LogEvent]:
        """Return events filtered by source service."""
        return [e for e in self._events if e.source_service == service]

    def get_by_id(self, event_id: str) -> Optional[LogEvent]:
        """Return a specific event by ID."""
        for e in self._events:
            if e.id == event_id:
                return e
        return None

    def get_recent(self, window_seconds: int = 60) -> List[LogEvent]:
        """Return events within the specified time window."""
        cutoff = datetime.utcnow()
        return [
            e for e in self._events
            if (cutoff - e.timestamp).total_seconds() <= window_seconds
        ]

    def clear(self):
        """Clear all stored events."""
        self._events.clear()

    @property
    def count(self) -> int:
        return len(self._events)


# Global singleton
event_store = EventStore()

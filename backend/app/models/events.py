"""Log event and alert data models."""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid
import json
from pydantic import BaseModel as IOModel  # Use Pydantic's BaseModel for API inputs to avoid confusion

class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


# API Schema (Pydantic) - Matches what the frontend/ingestor sends
class LogEventCreate(IOModel):
    """Schema for creating a new log event via API."""
    source_service: str
    severity: SeverityLevel = SeverityLevel.INFO
    message: str
    metadata: Dict[str, Any] = {}
    timestamp: Optional[datetime] = None


# Database Model (SQLModel)
class LogEvent(SQLModel, table=True):
    """Internal log event with generated ID."""
    __tablename__ = "log_events"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    source_service: str
    severity: SeverityLevel = Field(default=SeverityLevel.INFO)
    message: str
    metadata_json: str = Field(default="{}")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ingested_at: datetime = Field(default_factory=datetime.utcnow)

    # Optional foreign key to an incident if correlated
    incident_id: Optional[str] = Field(foreign_key="incidents.id", default=None)

    @property
    def event_metadata(self) -> Dict[str, Any]:
        return json.loads(self.metadata_json)

    @event_metadata.setter
    def event_metadata(self, value: Dict[str, Any]):
        self.metadata_json = json.dumps(value)


class Alert(SQLModel, table=True):
    """Alert derived from log events when thresholds are breached."""
    __tablename__ = "alerts"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    alert_type: str
    source_service: str
    severity: SeverityLevel
    message: str
    triggered_by_events_json: str = Field(default="[]")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @property
    def triggered_by_events(self) -> List[str]:
        return json.loads(self.triggered_by_events_json)

    @triggered_by_events.setter
    def triggered_by_events(self, value: List[str]):
        self.triggered_by_events_json = json.dumps(value)

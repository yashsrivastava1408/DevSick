"""Log event and alert data models."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class LogEventCreate(BaseModel):
    """Schema for creating a new log event via API."""
    source_service: str = Field(..., description="Service that generated the event")
    severity: SeverityLevel = Field(default=SeverityLevel.INFO)
    message: str = Field(..., description="Log message or error description")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: Optional[datetime] = None


class LogEvent(BaseModel):
    """Internal log event with generated ID."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_service: str
    severity: SeverityLevel
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ingested_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class Alert(BaseModel):
    """Alert derived from log events when thresholds are breached."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_type: str
    source_service: str
    severity: SeverityLevel
    message: str
    triggered_by_events: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

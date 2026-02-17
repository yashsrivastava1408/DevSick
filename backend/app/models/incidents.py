"""Incident and root cause analysis data models."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentStatus(str, Enum):
    DETECTED = "detected"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    ACTIONS_PENDING = "actions_pending"
    RESOLVED = "resolved"


class TimelineEntry(BaseModel):
    """Single entry in the incident timeline."""
    timestamp: datetime
    source_service: str
    event: str
    severity: str


class RootCauseAnalysis(BaseModel):
    """AI-generated root cause analysis."""
    summary: str = ""
    reasoning_chain: List[str] = Field(default_factory=list)
    root_cause: str = ""
    confidence_score: float = 0.0
    affected_services: List[str] = Field(default_factory=list)
    impact_description: str = ""


class Incident(BaseModel):
    """Correlated incident containing grouped events and analysis."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    severity: Severity
    status: IncidentStatus = IncidentStatus.DETECTED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    event_ids: List[str] = Field(default_factory=list)
    timeline: List[TimelineEntry] = Field(default_factory=list)
    root_cause_analysis: Optional[RootCauseAnalysis] = None
    affected_services: List[str] = Field(default_factory=list)
    scenario_type: str = ""

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

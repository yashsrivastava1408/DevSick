"""Incident and root cause analysis data models."""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid
import json


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


class RootCauseAnalysis(SQLModel):
    """AI-generated root cause analysis (DTO/Embedded)."""
    summary: str = ""
    reasoning_chain: List[str] = Field(default_factory=list)
    root_cause: str = ""
    confidence_score: float = 0.0
    affected_services: List[str] = Field(default_factory=list)
    impact_description: str = ""


class TimelineEntry(SQLModel, table=True):
    """Single entry in the incident timeline."""
    __tablename__ = "timeline_entries"

    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    timestamp: datetime
    source_service: str
    event: str
    severity: str
    incident_id: Optional[str] = Field(foreign_key="incidents.id")
    
    incident: Optional["Incident"] = Relationship(back_populates="timeline")


class Incident(SQLModel, table=True):
    """Correlated incident containing grouped events and analysis."""
    __tablename__ = "incidents"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str
    severity: Severity
    status: IncidentStatus = Field(default=IncidentStatus.DETECTED)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Store lists as JSON strings for SQLite/Simple Postgres support
    # In a full Postgres setup, we would use ARRAY types or separate tables
    event_ids_json: str = Field(default="[]")
    affected_services_json: str = Field(default="[]")
    scenario_type: str = ""

    # RCA Fields embedded for simplicity (1:1 relationship)
    rca_summary: Optional[str] = None
    rca_root_cause: Optional[str] = None
    rca_confidence_score: float = 0.0
    rca_reasoning_chain_json: str = Field(default="[]")
    rca_impact_description: Optional[str] = None

    timeline: List[TimelineEntry] = Relationship(back_populates="incident")

    @property
    def event_ids(self) -> List[str]:
        return json.loads(self.event_ids_json)

    @event_ids.setter
    def event_ids(self, value: List[str]):
        self.event_ids_json = json.dumps(value)

    @property
    def affected_services(self) -> List[str]:
        return json.loads(self.affected_services_json)

    @affected_services.setter
    def affected_services(self, value: List[str]):
        self.affected_services_json = json.dumps(value)
        
    @property
    def rca_reasoning_chain(self) -> List[str]:
        return json.loads(self.rca_reasoning_chain_json)
        
    @rca_reasoning_chain.setter
    def rca_reasoning_chain(self, value: List[str]):
        self.rca_reasoning_chain_json = json.dumps(value)

    @property
    def root_cause_analysis(self) -> Optional[RootCauseAnalysis]:
        if not self.rca_summary:
            return None
        return RootCauseAnalysis(
            summary=self.rca_summary,
            reasoning_chain=self.rca_reasoning_chain,
            root_cause=self.rca_root_cause or "",
            confidence_score=self.rca_confidence_score,
            affected_services=self.affected_services,
            impact_description=self.rca_impact_description or ""
        )


class IncidentRead(SQLModel):
    """Schema for reading incidents via API, including computed properties."""
    id: str
    title: str
    severity: Severity
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime
    scenario_type: str
    
    # Computed fields
    event_ids: List[str]
    affected_services: List[str]
    root_cause_analysis: Optional[RootCauseAnalysis]
    timeline: List[TimelineEntry] = []


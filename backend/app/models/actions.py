"""Remediation action and approval models."""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ROLLED_BACK = "rolled_back"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RemediationAction(SQLModel, table=True):
    """A suggested remediation action requiring human approval."""
    __tablename__ = "remediation_actions"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    # Link to incident
    incident_id: str = Field(foreign_key="incidents.id")
    
    title: str
    description: str
    command_hint: str = ""
    risk_level: RiskLevel = Field(default=RiskLevel.MEDIUM)
    approval_status: ApprovalStatus = Field(default=ApprovalStatus.PENDING)
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    rollback_description: str = ""

    # Optional relationship if needed later
    # incident: Optional["Incident"] = Relationship(back_populates="actions")

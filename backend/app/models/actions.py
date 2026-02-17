"""Remediation action and approval models."""
from pydantic import BaseModel, Field
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


class RemediationAction(BaseModel):
    """A suggested remediation action requiring human approval."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str
    title: str
    description: str
    command_hint: str = ""
    risk_level: RiskLevel = RiskLevel.MEDIUM
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    rollback_description: str = ""

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

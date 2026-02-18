"""Human-in-the-loop governance layer.

Manages the approval workflow for remediation actions.
No action is executed without explicit human approval.
"""
from datetime import datetime
from typing import List, Optional
from sqlmodel import Session, select
from ..models.actions import RemediationAction, ApprovalStatus, RiskLevel


class ApprovalManager:
    """Manages the approval lifecycle for remediation actions."""

    def __init__(self):
        self.auto_pilot = False  # Protocol Alpha (Manual) by default

    def register_actions(self, session: Session, actions: List[RemediationAction]):
        """Register new actions for approval tracking."""
        for action in actions:
            # Protocol Omega: Auto-approve LOW risk actions
            if self.auto_pilot and action.risk_level == RiskLevel.LOW:
                action.approval_status = ApprovalStatus.APPROVED
                action.approved_by = "auto-pilot"
                action.approved_at = datetime.utcnow()
            
            session.add(action)
        session.commit()
        # Refresh to get IDs if needed, but not strictly required for batch insert performance
    
    def get_action(self, session: Session, action_id: str) -> Optional[RemediationAction]:
        """Get a specific action by ID."""
        return session.get(RemediationAction, action_id)

    def get_actions_for_incident(self, session: Session, incident_id: str) -> List[RemediationAction]:
        """Get all actions for a specific incident."""
        statement = select(RemediationAction).where(RemediationAction.incident_id == incident_id)
        return session.exec(statement).all()

    def get_pending_actions(self, session: Session) -> List[RemediationAction]:
        """Get all actions awaiting approval."""
        statement = select(RemediationAction).where(RemediationAction.approval_status == ApprovalStatus.PENDING)
        return session.exec(statement).all()

    def approve_action(self, session: Session, action_id: str, approved_by: str = "admin") -> Optional[RemediationAction]:
        """Approve a remediation action."""
        action = session.get(RemediationAction, action_id)
        if action and action.approval_status == ApprovalStatus.PENDING:
            action.approval_status = ApprovalStatus.APPROVED
            action.approved_by = approved_by
            action.approved_at = datetime.utcnow()
            session.add(action)
            session.commit()
            session.refresh(action)
            return action
        return None

    def reject_action(self, session: Session, action_id: str, rejected_by: str = "admin") -> Optional[RemediationAction]:
        """Reject a remediation action."""
        action = session.get(RemediationAction, action_id)
        if action and action.approval_status == ApprovalStatus.PENDING:
            action.approval_status = ApprovalStatus.REJECTED
            action.approved_by = rejected_by
            action.approved_at = datetime.utcnow()
            session.add(action)
            session.commit()
            session.refresh(action)
            return action
        return None

    def rollback_action(self, session: Session, action_id: str) -> Optional[RemediationAction]:
        """Mark an approved action for rollback."""
        action = session.get(RemediationAction, action_id)
        if action and action.approval_status == ApprovalStatus.APPROVED:
            action.approval_status = ApprovalStatus.ROLLED_BACK
            session.add(action)
            session.commit()
            session.refresh(action)
            return action
        return None

    def get_all(self, session: Session) -> List[RemediationAction]:
        """Get all tracked actions."""
        return session.exec(select(RemediationAction)).all()

    def clear(self):
        """Clear all actions."""
        # Using DB, clear is handled by deleting rows in simulation reset
        pass


# Global singleton
approval_manager = ApprovalManager()

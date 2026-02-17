"""Human-in-the-loop governance layer.

Manages the approval workflow for remediation actions.
No action is executed without explicit human approval.
"""
from datetime import datetime
from typing import Dict, List, Optional
from ..models.actions import RemediationAction, ApprovalStatus


class ApprovalManager:
    """Manages the approval lifecycle for remediation actions."""

    def __init__(self):
        self._actions: Dict[str, RemediationAction] = {}

    def register_actions(self, actions: List[RemediationAction]):
        """Register new actions for approval tracking."""
        for action in actions:
            self._actions[action.id] = action

    def get_action(self, action_id: str) -> Optional[RemediationAction]:
        """Get a specific action by ID."""
        return self._actions.get(action_id)

    def get_actions_for_incident(self, incident_id: str) -> List[RemediationAction]:
        """Get all actions for a specific incident."""
        return [
            a for a in self._actions.values()
            if a.incident_id == incident_id
        ]

    def get_pending_actions(self) -> List[RemediationAction]:
        """Get all actions awaiting approval."""
        return [
            a for a in self._actions.values()
            if a.approval_status == ApprovalStatus.PENDING
        ]

    def approve_action(self, action_id: str, approved_by: str = "admin") -> Optional[RemediationAction]:
        """Approve a remediation action."""
        action = self._actions.get(action_id)
        if action and action.approval_status == ApprovalStatus.PENDING:
            action.approval_status = ApprovalStatus.APPROVED
            action.approved_by = approved_by
            action.approved_at = datetime.utcnow()
            return action
        return None

    def reject_action(self, action_id: str, rejected_by: str = "admin") -> Optional[RemediationAction]:
        """Reject a remediation action."""
        action = self._actions.get(action_id)
        if action and action.approval_status == ApprovalStatus.PENDING:
            action.approval_status = ApprovalStatus.REJECTED
            action.approved_by = rejected_by
            action.approved_at = datetime.utcnow()
            return action
        return None

    def rollback_action(self, action_id: str) -> Optional[RemediationAction]:
        """Mark an approved action for rollback."""
        action = self._actions.get(action_id)
        if action and action.approval_status == ApprovalStatus.APPROVED:
            action.approval_status = ApprovalStatus.ROLLED_BACK
            return action
        return None

    def get_all(self) -> List[RemediationAction]:
        """Get all tracked actions."""
        return list(self._actions.values())

    def clear(self):
        """Clear all actions."""
        self._actions.clear()


# Global singleton
approval_manager = ApprovalManager()

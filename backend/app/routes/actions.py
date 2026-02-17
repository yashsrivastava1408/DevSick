"""Remediation action API endpoints."""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from ..models.actions import RemediationAction
from ..governance.approval import approval_manager

router = APIRouter(prefix="/api", tags=["Actions"])


class ApprovalRequest(BaseModel):
    approved_by: str = "admin"


@router.get("/incidents/{incident_id}/actions", response_model=List[RemediationAction])
async def get_incident_actions(incident_id: str):
    """Get all remediation actions for an incident."""
    return approval_manager.get_actions_for_incident(incident_id)


@router.get("/actions/pending", response_model=List[RemediationAction])
async def get_pending_actions():
    """Get all actions awaiting approval."""
    return approval_manager.get_pending_actions()


@router.post("/actions/{action_id}/approve", response_model=RemediationAction)
async def approve_action(action_id: str, request: ApprovalRequest = ApprovalRequest()):
    """Approve a remediation action."""
    action = approval_manager.approve_action(action_id, request.approved_by)
    if not action:
        raise HTTPException(
            status_code=404,
            detail="Action not found or not in pending state"
        )
    return action


@router.post("/actions/{action_id}/reject", response_model=RemediationAction)
async def reject_action(action_id: str, request: ApprovalRequest = ApprovalRequest()):
    """Reject a remediation action."""
    action = approval_manager.reject_action(action_id, request.approved_by)
    if not action:
        raise HTTPException(
            status_code=404,
            detail="Action not found or not in pending state"
        )
    return action


@router.post("/actions/{action_id}/rollback", response_model=RemediationAction)
async def rollback_action(action_id: str):
    """Mark an approved action for rollback."""
    action = approval_manager.rollback_action(action_id)
    if not action:
        raise HTTPException(
            status_code=404,
            detail="Action not found or not in approved state"
        )
    return action

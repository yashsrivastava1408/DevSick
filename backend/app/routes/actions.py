"""Remediation action API endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from sqlmodel import Session
from ..models.actions import RemediationAction
from ..governance.approval import approval_manager
from ..database import get_session

router = APIRouter(prefix="/api", tags=["Actions"])


class ApprovalRequest(BaseModel):
    approved_by: str = "admin"


@router.get("/incidents/{incident_id}/actions", response_model=List[RemediationAction])
async def get_incident_actions(incident_id: str, session: Session = Depends(get_session)):
    """Get all remediation actions for an incident."""
    return approval_manager.get_actions_for_incident(session, incident_id)


@router.get("/actions/pending", response_model=List[RemediationAction])
async def get_pending_actions(session: Session = Depends(get_session)):
    """Get all actions awaiting approval."""
    return approval_manager.get_pending_actions(session)


@router.post("/actions/{action_id}/approve", response_model=RemediationAction)
async def approve_action(action_id: str, request: ApprovalRequest = ApprovalRequest(), session: Session = Depends(get_session)):
    """Approve a remediation action."""
    action = approval_manager.approve_action(session, action_id, request.approved_by)
    if not action:
        raise HTTPException(
            status_code=404,
            detail="Action not found or not in pending state"
        )
    return action


@router.post("/actions/{action_id}/reject", response_model=RemediationAction)
async def reject_action(action_id: str, request: ApprovalRequest = ApprovalRequest(), session: Session = Depends(get_session)):
    """Reject a remediation action."""
    action = approval_manager.reject_action(session, action_id, request.approved_by)
    if not action:
        raise HTTPException(
            status_code=404,
            detail="Action not found or not in pending state"
        )
    return action


@router.post("/actions/{action_id}/rollback", response_model=RemediationAction)
async def rollback_action(action_id: str, session: Session = Depends(get_session)):
    """Mark an approved action for rollback."""
    action = approval_manager.rollback_action(session, action_id)
    if not action:
        raise HTTPException(
            status_code=404,
            detail="Action not found or not in approved state"
        )
    return action


@router.get("/governance/status")
async def get_governance_status():
    """Get current governance mode status."""
    return {
        "auto_pilot": approval_manager.auto_pilot,
        "mode": "Protocol Omega" if approval_manager.auto_pilot else "Protocol Alpha"
    }


@router.post("/governance/toggle")
async def toggle_governance_mode():
    """Toggle between Protocol Alpha (Manual) and Protocol Omega (Auto)."""
    approval_manager.auto_pilot = not approval_manager.auto_pilot
    return {
        "auto_pilot": approval_manager.auto_pilot,
        "mode": "Protocol Omega" if approval_manager.auto_pilot else "Protocol Alpha"
    }

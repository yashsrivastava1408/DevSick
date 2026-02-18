"""Incident management API endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from sqlmodel import Session, select, func
from ..models.incidents import Incident, IncidentStatus, IncidentRead
from ..reasoning.ai_engine import analyze_incident
from ..database import get_session

router = APIRouter(prefix="/api", tags=["Incidents"])


def add_incident(session: Session, incident: Incident):
    """Add an incident to the database (called by simulation route)."""
    session.add(incident)
    session.commit()
    session.refresh(incident)
    return incident


@router.get("/incidents", response_model=List[IncidentRead])
async def list_incidents(session: Session = Depends(get_session)):
    """List all incidents, newest first."""
    statement = select(Incident).order_by(Incident.created_at.desc())
    return session.exec(statement).all()


@router.get("/incidents/{incident_id}", response_model=IncidentRead)
async def get_incident(incident_id: str, session: Session = Depends(get_session)):
    """Get details of a specific incident."""
    incident = session.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.post("/incidents/{incident_id}/analyze", response_model=IncidentRead)
async def analyze(incident_id: str, session: Session = Depends(get_session)):
    """Trigger AI-powered root cause analysis on an incident."""
    incident = session.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Update status
    incident.status = IncidentStatus.ANALYZING
    session.add(incident)
    session.commit()
    
    # Run AI analysis
    # Note: analyze_incident returns an RCA object (part of the model definition)
    rca = await analyze_incident(incident)
    
    # Update incident with RCA data
    # Flatten RCA into the incident columns
    incident.rca_summary = rca.summary
    incident.rca_root_cause = rca.root_cause
    incident.rca_confidence_score = rca.confidence_score
    incident.rca_impact_description = rca.impact_description
    incident.rca_reasoning_chain = rca.reasoning_chain
    incident.affected_services = rca.affected_services
    
    incident.status = IncidentStatus.ANALYZED
    
    session.add(incident)
    session.commit()
    session.refresh(incident)

    return incident


@router.get("/stats")
async def get_stats(session: Session = Depends(get_session)):
    """Get incident statistics."""
    # This could be optimized with specific SQL queries
    # For now, fetching all is acceptable for MVP scale
    incidents = session.exec(select(Incident)).all()
    
    total = len(incidents)
    by_severity: Dict[str, int] = {}
    by_status: Dict[str, int] = {}
    
    for inc in incidents:
        sev = inc.severity.value if hasattr(inc.severity, 'value') else str(inc.severity)
        stat = inc.status.value if hasattr(inc.status, 'value') else str(inc.status)
        by_severity[sev] = by_severity.get(sev, 0) + 1
        by_status[stat] = by_status.get(stat, 0) + 1

    return {
        "total_incidents": total,
        "by_severity": by_severity,
        "by_status": by_status,
    }

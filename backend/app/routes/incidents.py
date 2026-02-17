"""Incident management API endpoints."""
from fastapi import APIRouter, HTTPException
from typing import List, Dict
from ..models.incidents import Incident, IncidentStatus
from ..reasoning.ai_engine import analyze_incident

router = APIRouter(prefix="/api", tags=["Incidents"])

# In-memory incident store
_incidents: Dict[str, Incident] = {}


def add_incident(incident: Incident):
    """Add an incident to the store (called by simulation route)."""
    _incidents[incident.id] = incident


def get_incident_store() -> Dict[str, Incident]:
    """Get the incident store reference."""
    return _incidents


@router.get("/incidents", response_model=List[Incident])
async def list_incidents():
    """List all incidents, newest first."""
    incidents = sorted(
        _incidents.values(),
        key=lambda i: i.created_at,
        reverse=True,
    )
    return incidents


@router.get("/incidents/{incident_id}", response_model=Incident)
async def get_incident(incident_id: str):
    """Get details of a specific incident."""
    incident = _incidents.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.post("/incidents/{incident_id}/analyze", response_model=Incident)
async def analyze(incident_id: str):
    """Trigger AI-powered root cause analysis on an incident."""
    incident = _incidents.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Update status
    incident.status = IncidentStatus.ANALYZING
    
    # Run AI analysis
    rca = await analyze_incident(incident)
    incident.root_cause_analysis = rca
    incident.status = IncidentStatus.ANALYZED

    return incident


@router.get("/stats")
async def get_stats():
    """Get incident statistics."""
    total = len(_incidents)
    by_severity = {}
    by_status = {}
    
    for inc in _incidents.values():
        sev = inc.severity.value if hasattr(inc.severity, 'value') else str(inc.severity)
        stat = inc.status.value if hasattr(inc.status, 'value') else str(inc.status)
        by_severity[sev] = by_severity.get(sev, 0) + 1
        by_status[stat] = by_status.get(stat, 0) + 1

    return {
        "total_incidents": total,
        "by_severity": by_severity,
        "by_status": by_status,
    }

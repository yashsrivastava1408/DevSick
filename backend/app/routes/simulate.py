"""Simulation endpoint for demo scenarios.

Runs the full incident pipeline:
1. Ingest sample events
2. Correlate into incidents
3. Run AI analysis
4. Generate recommendations
"""
import json
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Query
from ..models.events import LogEventCreate, SeverityLevel
from ..models.incidents import IncidentStatus
from ..ingestion.log_ingestor import event_store
from ..correlation.engine import correlate_events
from ..reasoning.ai_engine import analyze_incident
from ..recommendations.engine import generate_recommendations
from ..governance.approval import approval_manager
from .incidents import add_incident, get_incident_store

router = APIRouter(prefix="/api", tags=["Simulation"])

# Load sample data
_sample_data = None


def _load_sample_data():
    global _sample_data
    if _sample_data is None:
        data_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "sample_events.json"
        )
        with open(data_path, "r") as f:
            _sample_data = json.load(f)
    return _sample_data


@router.post("/simulate")
async def simulate_scenario(
    scenario: Optional[str] = Query(
        default=None,
        description="Scenario to simulate: vault_auth_failure, database_jwt_missing, api_auth_cascade. Leave empty for all."
    )
):
    """Simulate one or all incident scenarios.
    
    Runs the full pipeline: ingest → correlate → analyze → recommend.
    """
    data = _load_sample_data()
    scenarios_to_run = data["scenarios"]

    if scenario:
        if scenario not in scenarios_to_run:
            return {"error": f"Unknown scenario: {scenario}. Available: {list(scenarios_to_run.keys())}"}
        scenarios_to_run = {scenario: scenarios_to_run[scenario]}

    results = []
    base_time = datetime.utcnow()

    for scenario_id, scenario_data in scenarios_to_run.items():
        # 1. Ingest events
        events = []
        for evt in scenario_data["events"]:
            event_create = LogEventCreate(
                source_service=evt["source_service"],
                severity=SeverityLevel(evt["severity"]),
                message=evt["message"],
                metadata=evt.get("metadata", {}),
                timestamp=base_time + timedelta(seconds=evt["timestamp_offset_seconds"]),
            )
            stored = event_store.ingest(event_create)
            events.append(stored)

        # 2. Correlate events into an incident
        incident = correlate_events(events)
        
        # 3. Run AI analysis
        rca = await analyze_incident(incident)
        incident.root_cause_analysis = rca
        incident.status = IncidentStatus.ANALYZED

        # 4. Generate recommendations
        actions = generate_recommendations(incident)
        approval_manager.register_actions(actions)
        incident.status = IncidentStatus.ACTIONS_PENDING

        # Store the incident
        add_incident(incident)

        results.append({
            "scenario": scenario_id,
            "incident_id": incident.id,
            "title": incident.title,
            "severity": incident.severity.value,
            "events_ingested": len(events),
            "root_cause": rca.root_cause,
            "confidence": rca.confidence_score,
            "actions_generated": len(actions),
        })

        # Offset base time for next scenario
        base_time += timedelta(minutes=5)

    return {
        "message": f"Simulated {len(results)} scenario(s)",
        "results": results,
    }


@router.post("/reset")
async def reset_simulation():
    """Reset all data — clear events, incidents, and actions."""
    event_store.clear()
    get_incident_store().clear()
    approval_manager.clear()
    return {"message": "All simulation data cleared"}

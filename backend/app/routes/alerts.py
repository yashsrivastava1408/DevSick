"""Alertmanager webhook receiver."""
from fastapi import APIRouter, Request, Depends
from sqlmodel import Session
import logging
from ..database import get_session
from ..correlation.engine import correlate_events
from ..reasoning.ai_engine import analyze_incident
from ..reasoning.orchestrator import sentinel_orchestrator
from ..recommendations.engine import generate_recommendations
from ..governance.approval import approval_manager
from .incidents import add_incident
from ..models.events import LogEventCreate, SeverityLevel

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])
logger = logging.getLogger(__name__)

@router.post("/webhook")
async def alert_webhook(request: Request, session: Session = Depends(get_session)):
    """Receive alerts from Alertmanager and trigger incident analysis."""
    data = await request.json()
    logger.info(f"Received alert webhook: {data}")
    
    # Process alerts
    alerts = data.get("alerts", [])
    for alert in alerts:
        status = alert.get("status")
        if status == "resolved":
            continue
            
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})
        
        # Convert Alertmanager alert to a LogEvent for the pipeline
        event_create = LogEventCreate(
            source_service=labels.get("job", "unknown"),
            severity=SeverityLevel(labels.get("severity", "error")),
            message=annotations.get("summary", "Infrastructure Alert"),
            metadata={
                "alertname": labels.get("alertname"),
                "description": annotations.get("description"),
                "instance": labels.get("instance"),
                "source": "alertmanager"
            }
        )
        
        # In this simplistic version, we trigger the pipeline per alert
        # In production, we'd wait for correlation
        
        # 1. Mock 'ingestion' by creating a list with one event
        # (Using simulate pipeline logic for now)
        from ..ingestion.log_ingestor import event_store
        stored_event = event_store.ingest(session, event_create)
        
        # 2. Correlate
        incident = correlate_events([stored_event])
        
        # 3. Analyze
        rca = await analyze_incident(incident)
        
        # Flatten RCA into incident
        incident.rca_summary = rca.summary
        incident.rca_root_cause = rca.root_cause
        incident.rca_confidence_score = rca.confidence_score
        incident.rca_impact_description = rca.impact_description
        incident.rca_reasoning_chain = rca.reasoning_chain
        incident.affected_services = rca.affected_services
        
        # 4. Generate recommendations
        actions = generate_recommendations(incident)
        approval_manager.register_actions(session, actions)
        
        # 5. Sentinel Orchestration (Multi-Agent Phase 3 Evolution)
        await sentinel_orchestrator.handle_incident(incident, rca)
        
        incident.status = "ACTIONS_PENDING"
        add_incident(session, incident)
        
    session.commit()
    return {"status": "ok", "alerts_processed": len(alerts)}

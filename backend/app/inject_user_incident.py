import asyncio
import json
from datetime import datetime, timedelta
from sqlmodel import Session

from .database import engine, create_db_and_tables
from .models.events import LogEvent, SeverityLevel
from .models.incidents import Incident, IncidentStatus
from .correlation.engine import correlate_events
from .reasoning.ai_engine import analyze_incident
from .recommendations.engine import generate_recommendations
from .governance.approval import approval_manager

# Exact logs from the latest user prompt
RAW_LOGS = [
    {"level":"error","ts":1771476477.332054,"msg":"Reconciler error","controller":"clustersecretstore","error":"could not get provider client: unable to log in to auth method: unable to log in with Kubernetes auth: Error making API request. URL: PUT https://vault.xenkrypt.me/v1/auth/kubernetes/login Code: 503. Errors: * Vault is sealed"},
    {"level":"error","ts":1771476495.5862236,"logger":"controllers.SecretStore","msg":"unable to validate store","namespace":"encryptiv-frontend","error":"could not get provider client: unable to log in to auth method: unable to log in with Kubernetes auth: Error making API request. URL: PUT https://vault.xenkrypt.me/v1/auth/kubernetes/login Code: 503. Errors: * Vault is sealed"},
    {"level":"error","ts":1771476499.0254486,"logger":"controllers.SecretStore","msg":"unable to validate store","namespace":"xenkrypt-web","error":"could not get provider client: unable to log in to auth method: unable to log in with Kubernetes auth: Error making API request. URL: PUT https://vault.xenkrypt.me/v1/auth/kubernetes/login Code: 503. Errors: * Vault is sealed"},
    {"level":"error","ts":1771476879.2014334,"msg":"Reconciler error","namespace":"database","name":"auth-db-secrets-external","error":"error processing spec.data[0] (key: encryptiv/database/auth-db), err: ClusterSecretStore \"vault-backend\" is not ready"},
    {"level":"error","ts":1771476879.4833696,"msg":"Reconciler error","namespace":"encryptiv-frontend","name":"frontend-secrets-external","error":"error processing spec.data[0] (key: encryptiv/frontend/clerk), err: SecretStore \"vault-backend\" is not ready"},
    {"level":"error","ts":1771476879.4893794,"msg":"Reconciler error","namespace":"xenkrypt-docs","name":"xendocs-vault-secret","error":"error processing spec.data[0] (key: docs), err: ClusterSecretStore \"vault-backend\" is not ready"},
    {"level":"error","ts":1771476879.495488,"msg":"Reconciler error","namespace":"xenkrypt-web","name":"xenkrypt-web-secrets-external","error":"error processing spec.data[0] (key: xenkrypt-web/supabase), err: SecretStore \"vault-backend\" is not ready"},
    {"level":"error","ts":1771476879.9629943,"msg":"Reconciler error","namespace":"auth","name":"auth-secrets-external","error":"error processing spec.data[0] (key: auth), err: ClusterSecretStore \"vault-backend\" is not ready"}
]

async def inject():
    # Ensure tables exist
    create_db_and_tables()
    
    with Session(engine) as session:
        print("Starting live injection of the full log sequence...")
        
        # 1. Create events
        events = []
        for i, log in enumerate(RAW_LOGS):
            # Map source service
            source = log.get("namespace") or log.get("controller") or "kubernetes"
            
            event = LogEvent(
                source_service=source,
                severity=SeverityLevel.HIGH,
                message=f"{log['msg']}: {log['error']}",
                timestamp=datetime.fromtimestamp(log["ts"])
            )
            session.add(event)
            events.append(event)
        
        session.commit()
        for e in events: session.refresh(e)
        
        # 2. Correlate
        incident = correlate_events(events)
        
        # 3. Analyze
        print("Running AI analysis on full sequence...")
        rca = await analyze_incident(incident)
        incident.rca_summary = rca.summary
        incident.rca_root_cause = rca.root_cause
        incident.rca_confidence_score = rca.confidence_score
        incident.rca_impact_description = rca.impact_description
        incident.rca_reasoning_chain = rca.reasoning_chain
        incident.affected_services = rca.affected_services
        incident.status = IncidentStatus.ANALYZED
        
        # 4. Recommend
        actions = generate_recommendations(incident)
        approval_manager.register_actions(session, actions)
        incident.status = IncidentStatus.ACTIONS_PENDING
        
        session.add(incident)
        session.commit()
        session.refresh(incident)
        
        print(f"\nSUCCESS! Incident '{incident.title}' is now live.")
        print(f"Incident ID: {incident.id}")
        print(f"Root Cause Identified: {incident.rca_root_cause}")

if __name__ == "__main__":
    asyncio.run(inject())

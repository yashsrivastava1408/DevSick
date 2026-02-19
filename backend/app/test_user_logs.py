import asyncio
import json
from datetime import datetime
from typing import List

from .models.events import LogEvent, SeverityLevel
from .correlation.engine import correlate_events
from .reasoning.ai_engine import analyze_incident
from .recommendations.engine import generate_recommendations

# Raw logs provided by the user
RAW_LOGS = """
{"level":"error","ts":1771476477.332054,"msg":"Reconciler error","controller":"clustersecretstore","controllerGroup":"external-secrets.io","controllerKind":"ClusterSecretStore","ClusterSecretStore":{"name":"vault-backend"},"namespace":"","name":"vault-backend","reconcileID":"62761b5f-8e6d-4416-8c45-f8dcd3b3b564","error":"could not get provider client: unable to log in to auth method: unable to log in with Kubernetes auth: Error making API request.\\n\\nURL: PUT https://vault.xenkrypt.me/v1/auth/kubernetes/login\\nCode: 503. Errors:\\n\\n* Vault is sealed"}
{"level":"error","ts":1771476495.5862236,"logger":"controllers.SecretStore","msg":"unable to validate store","secretstore":{"name":"vault-backend","namespace":"encryptiv-frontend"},"error":"could not get provider client: unable to log in to auth method: unable to log in with Kubernetes auth: Error making API request.\\n\\nURL: PUT https://vault.xenkrypt.me/v1/auth/kubernetes/login\\nCode: 503. Errors:\\n\\n* Vault is sealed"}
{"level":"error","ts":1771476499.0254486,"logger":"controllers.SecretStore","msg":"unable to validate store","secretstore":{"name":"vault-backend","namespace":"xenkrypt-web"},"error":"could not get provider client: unable to log in to auth method: unable to log in with Kubernetes auth: Error making API request.\\n\\nURL: PUT https://vault.xenkrypt.me/v1/auth/kubernetes/login\\nCode: 503. Errors:\\n\\n* Vault is sealed"}
{"level":"error","ts":1771476879.2014334,"msg":"Reconciler error","controller":"externalsecret","controllerGroup":"external-secrets.io","controllerKind":"ExternalSecret","ExternalSecret":{"name":"auth-db-secrets-external","namespace":"database"},"namespace":"database","name":"auth-db-secrets-external","reconcileID":"2e2b4a07-fff6-4b32-824e-37cbaf8de4ed","error":"error processing spec.data[0] (key: encryptiv/database/auth-db), err: ClusterSecretStore \\"vault-backend\\" is not ready"}
{"level":"error","ts":1771476879.4833696,"msg":"Reconciler error","controller":"externalsecret","controllerGroup":"external-secrets.io","controllerKind":"ExternalSecret","ExternalSecret":{"name":"frontend-secrets-external","namespace":"encryptiv-frontend"},"namespace":"encryptiv-frontend","name":"frontend-secrets-external","reconcileID":"7b076aa0-3fac-40b6-b9c1-2eeef2a25667","error":"error processing spec.data[0] (key: encryptiv/frontend/clerk), err: SecretStore \\"vault-backend\\" is not ready"}
{"level":"error","ts":1771476879.4893794,"msg":"Reconciler error","controller":"externalsecret","controllerGroup":"external-secrets.io","controllerKind":"ExternalSecret","ExternalSecret":{"name":"xendocs-vault-secret","namespace":"xenkrypt-docs"},"namespace":"xenkrypt-docs","name":"xendocs-vault-secret","reconcileID":"9a7f08e1-9725-4cf1-b7fb-803b3f537fe5","error":"error processing spec.data[0] (key: docs), err: ClusterSecretStore \\"vault-backend\\" is not ready"}
"""

def parse_logs(raw_input: str) -> List[LogEvent]:
    events = []
    for line in raw_input.strip().split('\n'):
        if not line.strip(): continue
        try:
            data = json.loads(line)
            # Determine source service from controller or namespace
            source = data.get("namespace") or data.get("controller") or "kubernetes"
            if not source and "ClusterSecretStore" in data:
                source = "cluster-secrets"
            
            # Map severity
            level = data.get("level", "info").lower()
            severity = SeverityLevel.INFO
            if level == "error": severity = SeverityLevel.HIGH
            elif level == "fatal": severity = SeverityLevel.CRITICAL
            
            event = LogEvent(
                source_service=source or "unknown",
                severity=severity,
                message=data.get("msg", "") + ": " + data.get("error", ""),
                timestamp=datetime.fromtimestamp(data.get("ts", datetime.utcnow().timestamp())),
            )
            events.append(event)
        except Exception as e:
            print(f"Failed to parse line: {line}. Error: {e}")
    return events

async def run_test():
    print("--- STARTING VAULT LOG REPRO TEST ---")
    
    # 1. Parse logs
    events = parse_logs(RAW_LOGS)
    print(f"Ingested {len(events)} events from user logs.")
    
    # 2. Correlate
    incident = correlate_events(events)
    print(f"INCIDENT DETECTED: {incident.title}")
    print(f"Scenario Type: {incident.scenario_type}")
    print(f"Severity: {incident.severity.value}")
    print(f"Affected Services: {', '.join(incident.affected_services)}")
    
    # 3. Analyze
    print("\n--- RUNNING AI ANALYSIS ---")
    rca = await analyze_incident(incident)
    print(f"ROOT CAUSE: {rca.root_cause}")
    print(f"SUMMARY: {rca.summary}")
    print("REASONING CHAIN:")
    for step in rca.reasoning_chain:
        print(f"  - {step}")
    
    # 4. Recommend
    print("\n--- GENERATING RECOMMENDATIONS ---")
    # Flatten incident for recommendations engine (like in simulate.py)
    incident.rca_summary = rca.summary
    incident.rca_root_cause = rca.root_cause
    incident.rca_confidence_score = rca.confidence_score
    incident.rca_impact_description = rca.impact_description
    incident.rca_reasoning_chain = rca.reasoning_chain
    
    actions = generate_recommendations(incident)
    print(f"Generated {len(actions)} remediation actions:")
    for i, action in enumerate(actions, 1):
        print(f"{i}. [{action.risk_level.value.upper()}] {action.title}")
        print(f"   Description: {action.description}")
        if action.command_hint:
            print(f"   Command: {action.command_hint}")
        print()

if __name__ == "__main__":
    asyncio.run(run_test())

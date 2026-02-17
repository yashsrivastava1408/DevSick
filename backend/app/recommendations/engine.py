"""Recommendation engine.

Generates remediation actions based on root cause analysis.
Maps known root causes to standard remediation playbooks.
"""
from typing import List
from ..models.actions import RemediationAction, RiskLevel
from ..models.incidents import Incident


# Remediation playbooks mapped to scenario types
PLAYBOOKS = {
    "vault_auth_failure": [
        {
            "title": "Unseal / Restart Vault",
            "description": "Check Vault seal status and unseal if necessary. If Vault pod is unresponsive, perform a controlled restart of the vault-0 pod.",
            "command_hint": "kubectl exec -it vault-0 -- vault status && kubectl delete pod vault-0",
            "risk_level": RiskLevel.HIGH,
            "rollback_description": "If Vault enters a bad state after restart, restore from the last Raft snapshot backup."
        },
        {
            "title": "Reconcile ESO SecretStore",
            "description": "Force External Secrets Operator to reconcile the vault-backend SecretStore and verify connectivity to Vault.",
            "command_hint": "kubectl annotate secretstore vault-backend force-sync=$(date +%s) --overwrite",
            "risk_level": RiskLevel.LOW,
            "rollback_description": "Remove the force-sync annotation if reconciliation causes issues."
        },
        {
            "title": "Rotate Database Credentials",
            "description": "Manually rotate the database credentials if automatic rotation via ESO cannot be restored in time.",
            "command_hint": "kubectl create secret generic db-credentials --from-literal=password=$(openssl rand -base64 32) --dry-run=client -o yaml | kubectl apply -f -",
            "risk_level": RiskLevel.MEDIUM,
            "rollback_description": "Restore previous database credentials from Vault KV store."
        },
        {
            "title": "Restart Auth Service Pods",
            "description": "After credentials are restored, restart auth-service pods to reinitialize database connection pool.",
            "command_hint": "kubectl rollout restart deployment/auth-service",
            "risk_level": RiskLevel.LOW,
            "rollback_description": "Rollback deployment: kubectl rollout undo deployment/auth-service"
        },
    ],
    "database_jwt_missing": [
        {
            "title": "Create New JWT Signing Key",
            "description": "Manually create a new JWT signing key in Vault's transit engine or KV store.",
            "command_hint": "vault write transit/keys/jwt-signing type=ecdsa-p256",
            "risk_level": RiskLevel.MEDIUM,
            "rollback_description": "Delete the newly created key if it causes signature mismatches."
        },
        {
            "title": "Restart Auth Service",
            "description": "Restart auth-service pods to force reload of signing keys from Vault.",
            "command_hint": "kubectl rollout restart deployment/auth-service",
            "risk_level": RiskLevel.LOW,
            "rollback_description": "Rollback: kubectl rollout undo deployment/auth-service"
        },
        {
            "title": "Reset API Gateway Circuit Breaker",
            "description": "Once auth-service is healthy, reset the API gateway circuit breaker to restore traffic flow.",
            "command_hint": "kubectl exec -it api-gateway-0 -- curl -X POST localhost:9901/reset_circuit_breaker",
            "risk_level": RiskLevel.LOW,
            "rollback_description": "Circuit breaker will automatically re-engage if failures continue."
        },
        {
            "title": "Audit Vault Lease Configuration",
            "description": "Review and extend JWT signing key lease TTL to prevent future expiry. Consider implementing lease renewal monitoring.",
            "command_hint": "vault read sys/leases/lookup -format=json | jq '.data'",
            "risk_level": RiskLevel.LOW,
            "rollback_description": "No rollback needed — this is an audit action."
        },
    ],
    "api_auth_cascade": [
        {
            "title": "Emergency TLS Certificate Renewal",
            "description": "Manually trigger certificate renewal or issue an emergency certificate via cert-manager.",
            "command_hint": "kubectl delete certificate api-gateway-tls && kubectl apply -f certificate.yaml",
            "risk_level": RiskLevel.MEDIUM,
            "rollback_description": "Restore the previous certificate secret from backup."
        },
        {
            "title": "Investigate ACME Challenge Failure",
            "description": "Check cert-manager logs and DNS configuration to determine why the ACME challenge failed.",
            "command_hint": "kubectl logs -l app=cert-manager -n cert-manager --tail=100",
            "risk_level": RiskLevel.LOW,
            "rollback_description": "No rollback needed — this is a diagnostic action."
        },
        {
            "title": "Restart API Gateway",
            "description": "After certificate is renewed, restart API gateway pods to load the new certificate.",
            "command_hint": "kubectl rollout restart deployment/api-gateway",
            "risk_level": RiskLevel.MEDIUM,
            "rollback_description": "Rollback: kubectl rollout undo deployment/api-gateway"
        },
        {
            "title": "Implement Certificate Expiry Alerting",
            "description": "Add Prometheus alerting for certificates expiring within 7 days to prevent future incidents.",
            "command_hint": "kubectl apply -f cert-expiry-alert-rule.yaml",
            "risk_level": RiskLevel.LOW,
            "rollback_description": "Delete the alert rule if it generates false positives."
        },
    ],
}


def generate_recommendations(incident: Incident) -> List[RemediationAction]:
    """Generate remediation actions based on the incident's scenario type."""
    playbook = PLAYBOOKS.get(incident.scenario_type, [
        {
            "title": "Manual Investigation Required",
            "description": "Unable to automatically generate recommendations for this incident type. "
                           "Investigate affected services manually and check logs for more details.",
            "command_hint": "",
            "risk_level": RiskLevel.LOW,
            "rollback_description": ""
        },
        {
            "title": "Escalate to On-Call Engineer",
            "description": "Escalate this incident to the on-call SRE for manual triage.",
            "command_hint": "",
            "risk_level": RiskLevel.LOW,
            "rollback_description": ""
        },
    ])

    actions = []
    for item in playbook:
        action = RemediationAction(
            incident_id=incident.id,
            title=item["title"],
            description=item["description"],
            command_hint=item.get("command_hint", ""),
            risk_level=item.get("risk_level", RiskLevel.MEDIUM),
            rollback_description=item.get("rollback_description", ""),
        )
        actions.append(action)

    return actions

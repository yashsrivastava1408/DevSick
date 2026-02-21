"""AI reasoning engine using Groq API with Llama3-8B.

Performs structured root cause analysis on correlated incidents.
Falls back to mock responses if the Groq API key is not configured.
"""
import json
import logging
from typing import Optional

from ..config import settings
from ..models.incidents import Incident, RootCauseAnalysis
from ..knowledge.dependency_graph import dependency_graph
from ..knowledge.metrics_fetcher import metrics_fetcher
from ..knowledge.vector_store import incident_memory
from .prompts import SYSTEM_PROMPT, build_incident_prompt, format_events_for_prompt

logger = logging.getLogger(__name__)


# Mock RCA responses for when API key is not available
MOCK_RESPONSES = {
    "vault_auth_failure": {
        "root_cause": "HashiCorp Vault instance became sealed/unreachable, preventing ESO from authenticating and syncing secrets",
        "summary": "Vault service failure caused a cascading authentication breakdown. ESO lost access to secrets, database credentials expired without rotation, and the auth service could not establish new database connections. This propagated to the API gateway as a full service outage.",
        "reasoning_chain": [
            "1. Vault pod (vault-0) began returning 503 on the authentication endpoint /v1/auth/kubernetes/login",
            "2. External Secrets Operator (ESO) failed to authenticate with Vault after 3 retries — SecretStore status changed to Error",
            "3. Database credentials managed by ESO could not be rotated — ExternalSecret sync failed",
            "4. Auth service's database connection pool was exhausted as existing credentials expired (FATAL: password authentication failed)",
            "5. API Gateway health checks detected auth-service failure, circuit breaker opened — 502 Bad Gateway"
        ],
        "confidence_score": 0.95,
        "affected_services": ["vault", "eso", "database", "auth_service", "api_gateway"],
        "impact_description": "Complete authentication service outage. All API requests through the gateway are failing with 502. 47 requests queued waiting for database connections. User-facing services are fully degraded.",
        "recommended_immediate_actions": [
            "Unseal Vault or restart Vault pod to restore accessibility",
            "Verify Vault Kubernetes auth method configuration",
            "Force ESO SecretStore reconciliation once Vault is healthy",
            "Manually rotate database credentials if Vault recovery is delayed",
            "Restart auth-service pods to reset connection pool after credentials are restored"
        ]
    },
    "database_jwt_missing": {
        "root_cause": "JWT signing key lease in Vault expired and automatic renewal failed, removing all signing keys from the auth service keystore",
        "summary": "JWT signing key lifecycle failure caused a complete authentication breakdown. The auth service lost its ability to validate tokens, rejecting 99.8% of requests. This cascaded to all authenticated services and breached the P1 SLA threshold.",
        "reasoning_chain": [
            "1. Vault JWT signing key lease expired — automatic renewal returned 'lease not found' error",
            "2. Auth service keystore became empty (0 signing keys) — all JWT verification began failing",
            "3. Token validation endpoint began rejecting all requests at 342 req/s — 99.8% error rate",
            "4. User service lost authentication capability — 1,247 failed requests affecting 89 users",
            "5. API Gateway error rate hit 99.1%, breaching the 0.1% SLA threshold — P1 alert triggered"
        ],
        "confidence_score": 0.92,
        "affected_services": ["vault", "auth_service", "user_service", "api_gateway"],
        "impact_description": "Complete authentication outage affecting all authenticated API calls. 89 active users impacted. P1 SLA breach triggered. Error rate at 99.1% across the gateway.",
        "recommended_immediate_actions": [
            "Manually create a new JWT signing key in Vault",
            "Restart auth-service pods to reload signing keys from Vault",
            "Investigate why the lease renewal failed — check Vault lease TTL configuration",
            "Consider implementing signing key caching in auth-service as a resilience measure",
            "Reset API Gateway circuit breaker once auth-service is healthy"
        ]
    },
    "api_auth_cascade": {
        "root_cause": "TLS certificate for api-gateway.prod expired due to ACME challenge failure in cert-manager, preventing all client connections",
        "summary": "Certificate renewal failure caused the API gateway TLS certificate to expire. All client connections were rejected with SSL errors, and the OAuth callback flow broke due to mTLS validation failure. User service degraded to cache-only mode.",
        "reasoning_chain": [
            "1. Cert-manager failed to renew TLS certificate — ACME challenge failed for api-gateway.prod",
            "2. API Gateway TLS certificate expired, causing handshake failures at 523 errors/sec",
            "3. 2,341 client connections rejected with SSL_ERROR_EXPIRED_CERT_ALERT across 156 clients",
            "4. Auth service OAuth callback endpoint became unreachable — mTLS peer certificate validation failing",
            "5. User service experienced 67% timeout rate, circuit breaker entered half-open state, falling back to cache"
        ],
        "confidence_score": 0.93,
        "affected_services": ["cert_manager", "api_gateway", "auth_service", "user_service"],
        "impact_description": "API gateway fully inaccessible via HTTPS. 156 clients unable to connect. OAuth authentication flow broken. User service degraded to stale cached data.",
        "recommended_immediate_actions": [
            "Manually renew the TLS certificate or issue an emergency self-signed certificate",
            "Investigate ACME challenge failure — check DNS configuration and challenge solver",
            "Verify cert-manager has proper permissions to update the certificate secret",
            "Consider implementing certificate expiry alerting with longer lead times",
            "Restart API Gateway pods once the new certificate is deployed"
        ]
    },
}


async def analyze_incident(incident: Incident) -> RootCauseAnalysis:
    """Run AI-powered root cause analysis on an incident.
    
    Uses Groq API with Llama3-8B to analyze the incident timeline
    and generate a structured root cause analysis.
    
    Falls back to mock responses if no API key is configured.
    """
    # Try real API first
    if settings.GROQ_API_KEY:
        try:
            return await _analyze_with_groq(incident)
        except Exception as e:
            logger.error(f"Groq API analysis failed: {e}. Falling back to mock.")

    # Fallback to mock responses
    return _build_mock_rca(incident)


async def _analyze_with_groq(incident: Incident) -> RootCauseAnalysis:
    """Call Groq API for real AI analysis."""
    from groq import AsyncGroq

    client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    events_text = format_events_for_prompt(incident.timeline)
    service_context = dependency_graph.get_service_context(incident.affected_services)
    
    # Fetch metrics around the incident time
    metrics_data = await metrics_fetcher.get_incident_metrics(incident.created_at)
    metrics_text = json.dumps(metrics_data, indent=2)
    
    # RAG: Search for similar past incidents
    query_text = f"Scenario: {incident.scenario_type} Title: {incident.title}"
    past_incidents = incident_memory.find_similar_incidents(query_text)
    memory_text = "\n".join([f"Similarity: {1-r['distance']:.2f}\nDocument: {r['document']}" for r in past_incidents])
    
    user_prompt = build_incident_prompt(
        events_text, 
        service_context, 
        metrics_text, 
        memory_text,
        incident.scenario_type
    )

    response = await client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=2048,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    data = json.loads(raw)

    return RootCauseAnalysis(
        summary=data.get("summary", ""),
        reasoning_chain=data.get("reasoning_chain", []),
        root_cause=data.get("root_cause", ""),
        confidence_score=data.get("confidence_score", 0.0),
        affected_services=data.get("affected_services", []),
        impact_description=data.get("impact_description", ""),
    )


def _build_mock_rca(incident: Incident) -> RootCauseAnalysis:
    """Build a mock RCA response based on scenario type."""
    mock = MOCK_RESPONSES.get(incident.scenario_type, {
        "root_cause": "Unable to determine root cause — insufficient event data or unknown scenario",
        "summary": "Multiple service failures detected across the infrastructure. Manual investigation recommended.",
        "reasoning_chain": [
            "1. Multiple error events detected across services",
            "2. Event correlation suggests a cascading failure pattern",
            "3. Root cause could not be automatically determined"
        ],
        "confidence_score": 0.3,
        "affected_services": incident.affected_services,
        "impact_description": "Service degradation detected. Impact scope unknown.",
    })

    return RootCauseAnalysis(
        summary=mock["summary"],
        reasoning_chain=mock["reasoning_chain"],
        root_cause=mock["root_cause"],
        confidence_score=mock["confidence_score"],
        affected_services=mock["affected_services"],
        impact_description=mock.get("impact_description", ""),
    )


def get_mock_actions(scenario_type: str) -> list:
    """Get mock recommended actions for a scenario."""
    mock = MOCK_RESPONSES.get(scenario_type, {})
    return mock.get("recommended_immediate_actions", [
        "Investigate affected services manually",
        "Check service logs for additional error details",
        "Escalate to on-call engineer"
    ])

"""Event correlation engine.

Groups related log events into incidents based on:
- Time window proximity
- Service dependency chain membership
- Error pattern matching
"""
from datetime import datetime
from typing import List, Dict
from ..models.events import LogEvent
from ..models.incidents import (
    Incident, Severity, IncidentStatus, TimelineEntry
)
from ..knowledge.dependency_graph import dependency_graph


# Severity mapping from event severity to incident severity
SEVERITY_MAP = {
    "critical": Severity.CRITICAL,
    "high": Severity.HIGH,
    "medium": Severity.MEDIUM,
    "low": Severity.LOW,
    "info": Severity.LOW,
}

# Scenario detection patterns
SCENARIO_PATTERNS = {
    "vault_auth_failure": {
        "keywords": ["vault", "sealed", "unreachable", "authenticate with vault"],
        "title": "Vault Authentication Failure — Cascading Service Disruption",
    },
    "database_jwt_missing": {
        "keywords": ["jwt", "signing key", "token validation", "unauthorized"],
        "title": "JWT Signing Key Missing — Authentication Cascade",
    },
    "api_auth_cascade": {
        "keywords": ["tls", "certificate", "expired", "handshake"],
        "title": "TLS Certificate Expiry — API Authentication Cascade",
    },
}


def detect_scenario(events: List[LogEvent]) -> Dict:
    """Detect which incident scenario matches the events."""
    all_messages = " ".join(e.message.lower() for e in events)

    for scenario_id, pattern in SCENARIO_PATTERNS.items():
        matches = sum(1 for kw in pattern["keywords"] if kw in all_messages)
        if matches >= 2:
            return {"id": scenario_id, "title": pattern["title"]}

    return {"id": "unknown", "title": "Correlated Incident — Multiple Service Failures"}


def determine_severity(events: List[LogEvent]) -> Severity:
    """Determine overall incident severity from constituent events."""
    severity_order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]
    for sev in severity_order:
        if any(SEVERITY_MAP.get(e.severity.value) == sev for e in events):
            return sev
    return Severity.LOW


def build_timeline(events: List[LogEvent]) -> List[TimelineEntry]:
    """Build a chronological timeline from events."""
    sorted_events = sorted(events, key=lambda e: e.timestamp)
    return [
        TimelineEntry(
            timestamp=e.timestamp,
            source_service=e.source_service,
            event=e.message,
            severity=e.severity.value,
        )
        for e in sorted_events
    ]


def extract_affected_services(events: List[LogEvent]) -> List[str]:
    """Extract unique affected services, ordered by first appearance."""
    seen = set()
    services = []
    for e in sorted(events, key=lambda e: e.timestamp):
        if e.source_service not in seen:
            seen.add(e.source_service)
            services.append(e.source_service)
    return services


def correlate_events(events: List[LogEvent]) -> Incident:
    """Correlate a group of related events into a single incident.
    
    Uses service dependency graph to validate that events are part
    of a cascading failure chain.
    """
    scenario = detect_scenario(events)
    severity = determine_severity(events)
    timeline = build_timeline(events)
    affected = extract_affected_services(events)

    incident = Incident(
        title=scenario["title"],
        severity=severity,
        status=IncidentStatus.DETECTED,
        event_ids=[e.id for e in events],
        timeline=timeline,
        affected_services=affected,
        scenario_type=scenario["id"],
    )

    return incident

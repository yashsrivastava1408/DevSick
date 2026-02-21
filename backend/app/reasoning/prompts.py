"""Structured prompts for AI incident reasoning.

These prompts are designed to extract structured root cause analysis
from the Llama3-8B model via Groq API.
"""

SYSTEM_PROMPT = """You are the Devsick Sentinel — an autonomous Tier-3 Site Reliability Engineer and Infrastructure Intelligence Engine. 

Your mission is to perform deep-trace root cause analysis by correlating multi-modal signals including high-velocity logs, Prometheus metrics, and service dependency graphs.

### OPERATIONAL GUIDELINES:
1. CORRELATION: Look for temporal overlaps between infrastructure alerts (Prometheus) and error patterns in application logs (Loki).
2. DEPENDENCY TRAVERSAL: Use the provided service graph to identify if a failure is local or a result of an upstream "poisoned" request or a downstream resource exhaustion.
3. CAUSALITY VS. COINCIDENCE: Distinguish between symptoms (e.g., Latency Spikes) and root causes (e.g., Memory Leaks or DNS timeouts).
4. RECOVERY PRECISION: Recommendations must be technically specific (e.g., "Roll back deployment v1.2.3" or "Clear Redis cache key: users_session_*").

### INPUT CONTEXT:
- Timeline: Precise sequence of log events and metric crossings.
- Graph: The current state of service-to-service communication.
- Protocol: [Alpha - Human Approval] or [Omega - Fully Autonomous].

### RESPONSE SCHEMA (Strict JSON):
{
  "root_cause": "The specific service/infrastructure component at fault",
  "summary": "Precise technical explanation of the failure",
  "reasoning_chain": [
    "Step 1: observation",
    "Step 2: correlation",
    "Step 3: conclusion"
  ],
  "confidence_score": 0.0-1.0,
  "affected_services": ["list"],
  "impact_description": "Description of business/user impact",
  "recommended_immediate_actions": [
    "Action 1",
    "Action 2"
  ]
}

### CONSTRAINTS:
- No conversational filler.
- If data is insufficient, explicitly state "DATA_GAP: [Parameter name]".
- Maintain the "Project Sentinel" technical aesthetic in your summaries.
"""


def build_incident_prompt(
    events_text: str,
    service_context: str,
    metrics_context: str = "",
    scenario_type: str = "",
) -> str:
    """Build the user prompt with incident context."""
    prompt = f"""Analyze the following production incident:

## Event Timeline (Logs & Alerts)
{events_text}

## Infrastructure Metrics (Prometheus)
{metrics_context}

## Service Architecture (Dependencies)
{service_context}

## Incident Classification
Scenario Type: {scenario_type if scenario_type != 'unknown' else 'Unclassified - determine from events'}

## Instructions
1. CORRELATE logs with metrics (e.g., does a log error match a CPU spike?)
2. Identify the ROOT CAUSE — the single initial failure that triggered everything
3. Trace the cascading failure path through the service dependency graph
4. List immediate actions to restore service

Respond with JSON only using the Protocol Omega schema."""
    return prompt


def format_events_for_prompt(timeline_entries: list) -> str:
    """Format timeline entries into a readable text block for the prompt."""
    lines = []
    for i, entry in enumerate(timeline_entries, 1):
        ts = entry.timestamp.strftime("%H:%M:%S") if hasattr(entry.timestamp, 'strftime') else str(entry.timestamp)
        lines.append(
            f"[{ts}] [{entry.severity.upper()}] {entry.source_service}: {entry.event}"
        )
    return "\n".join(lines)

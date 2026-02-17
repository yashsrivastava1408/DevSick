"""Structured prompts for AI incident reasoning.

These prompts are designed to extract structured root cause analysis
from the Llama3-8B model via Groq API.
"""

SYSTEM_PROMPT = """You are an expert Site Reliability Engineer (SRE) and incident analyst for enterprise infrastructure. Your role is to analyze correlated error events from monitoring systems and determine the root cause of incidents.

You must:
1. Analyze the timeline of events carefully
2. Consider service dependency chains
3. Identify the initial point of failure (root cause)
4. Explain the cascading failure pattern
5. Assess confidence in your analysis
6. Identify all affected services

You MUST respond with valid JSON only. No markdown, no explanation outside the JSON.
Use this exact schema:

{
  "root_cause": "Brief description of the root cause",
  "summary": "2-3 sentence executive summary of the incident",
  "reasoning_chain": [
    "Step 1: observation",
    "Step 2: correlation",
    "Step 3: conclusion"
  ],
  "confidence_score": 0.85,
  "affected_services": ["service_a", "service_b"],
  "impact_description": "Description of business/user impact",
  "recommended_immediate_actions": [
    "Action 1",
    "Action 2"
  ]
}"""


def build_incident_prompt(
    events_text: str,
    service_context: str,
    scenario_type: str = "",
) -> str:
    """Build the user prompt with incident context."""
    prompt = f"""Analyze the following production incident:

## Event Timeline
{events_text}

## Service Architecture
{service_context}

## Incident Classification
Scenario Type: {scenario_type if scenario_type != 'unknown' else 'Unclassified - determine from events'}

## Instructions
1. Identify the ROOT CAUSE — the single initial failure that triggered everything
2. Trace the cascading failure path through the service dependency graph
3. Explain why each downstream service was affected
4. Rate your confidence (0.0-1.0)
5. List immediate actions to restore service

Respond with JSON only."""
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

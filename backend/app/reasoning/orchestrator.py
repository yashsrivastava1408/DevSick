import logging
from .surgeon import Surgeon
from .scribe import Scribe
from .scout import Scout

logger = logging.getLogger(__name__)

class SentinelOrchestrator:
    """Orchestrates specialized agents to handle autonomous operations."""
    
    def __init__(self):
        self.surgeon = Surgeon()
        self.scribe = Scribe()
        self.scout = Scout()

    async def handle_incident(self, incident, analysis):
        """Coordinate agents to resolve an incident and document it."""
        logger.info(f"Orchestrating resolution for incident: {incident.id}")
        
        # 1. The Scout: Gathers final state/anomalies
        anomalies = self.scout.scan_impact(incident)
        
        # 2. The Surgeon: Executes remediation if approved/safe
        if analysis.confidence_score > 0.8:
            for action in analysis.recommended_immediate_actions:
                # Surgeon will use SafeExecutor internally
                res = await self.surgeon.remediate(action, justification=analysis.summary)
                logger.info(f"Surgeon Action Result: {res}")
        
        # 3. The Scribe: Creates the post-mortem
        self.scribe.document_incident(incident, analysis, anomalies)
        
        return {"status": "orchestration_complete"}

sentinel_orchestrator = SentinelOrchestrator()

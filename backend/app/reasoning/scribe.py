import logging
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class Scribe:
    """The Scribe documents incidents and generates post-mortems."""
    
    def __init__(self, post_mortem_dir: str = "./data/post_mortems"):
        self.post_mortem_dir = post_mortem_dir
        os.makedirs(post_mortem_dir, exist_ok=True)

    def document_incident(self, incident, analysis, anomalies):
        """Generate a technical post-mortem for the incident."""
        pm = {
            "incident_id": incident.id,
            "timestamp": datetime.utcnow().isoformat(),
            "summary": analysis.summary,
            "root_cause": analysis.root_cause,
            "reasoning_chain": analysis.reasoning_chain,
            "anomalies_detected": anomalies,
            "actions_taken": analysis.recommended_immediate_actions,
            "affected_services": analysis.affected_services
        }
        
        filename = f"PM_{incident.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(self.post_mortem_dir, filename)
        
        with open(path, "w") as f:
            json.dump(pm, f, indent=2)
            
        logger.info(f"Scribe generated post-mortem: {path}")
        return path

from ..governance.sandbox import SafeExecutor
import logging

logger = logging.getLogger(__name__)

class Surgeon:
    """The Surgeon executes precise remediation actions."""
    
    def __init__(self):
        self.executor = SafeExecutor()

    async def remediate(self, action_description: str, justification: str):
        """Translate a descriptive action into a command and execute it in dry-run by default."""
        logger.info(f"Surgeon attempting remediation: {action_description}")
        
        # In a real system, another LLM call would translate the description 
        # to a specific method in the Executor. For the prototype, we map a few.
        
        low_action = action_description.lower()
        if "restart" in low_action:
            # Heuristic: find deployment name
            # "Restart the auth-service" -> "auth-service"
            target = action_description.split()[-1] 
            return self.executor.perform_with_safety(
                "restart_deployment", 
                target, 
                justification=justification
            )
        
        if "scale" in low_action:
            target = action_description.split()[-3]
            count = 3 # default
            return self.executor.perform_with_safety(
                "scale_deployment", 
                target, 
                count,
                justification=justification
            )
            
        return {"status": "skipped", "reason": "Action mapping not found for surgeon"}

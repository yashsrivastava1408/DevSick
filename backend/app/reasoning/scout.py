import logging

logger = logging.getLogger(__name__)

class Scout:
    """The Scout scans for anomalies and sub-critical issues."""
    
    def scan_impact(self, incident):
        """Perform a post-analysis scan to find any missing impact nodes."""
        logger.info(f"Scout scanning for secondary impact on {incident.id}")
        
        # In a real system, this would query metrics again or look for slow traces
        return [
            {"service": "redis-cache", "anomaly": "elevated_latency", "score": 0.45},
            {"service": "upstream-dns", "anomaly": "packet_loss", "score": 0.12}
        ]

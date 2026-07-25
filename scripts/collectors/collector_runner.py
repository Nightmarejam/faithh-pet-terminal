#!/usr/bin/env python3
"""
Enhanced collector runner with retry logic and error handling.
"""
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/jonat/ai-stack/logs/collectors.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CollectorRunner:
    """Runs collectors with retry logic and error handling."""
    
    def __init__(self, max_retries: int = 3, base_delay: int = 60):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.error_log = []
    
    def run_with_retry(self, collector) -> Dict[str, Any]:
        """Run a collector with exponential backoff retry."""
        collector_name = getattr(collector, 'name', 'unknown')
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Running {collector_name} (attempt {attempt + 1}/{self.max_retries})")
                result = collector.run()
                
                if result.get("success"):
                    logger.info(f"✅ {collector_name} succeeded")
                    return result
                else:
                    error_msg = result.get("error", "Unknown error")
                    logger.warning(f"⚠️ {collector_name} failed: {error_msg}")
                    
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ {collector_name} exception: {error_msg}")
                result = {"success": False, "error": error_msg}
            
            # Log the error
            self.log_error(collector_name, result.get("error", "Unknown error"))
            
            # Wait before retry (exponential backoff)
            if attempt < self.max_retries - 1:
                delay = self.base_delay * (2 ** attempt)
                logger.info(f"Waiting {delay}s before retry...")
                time.sleep(delay)
        
        # All retries failed
        logger.error(f"💥 {collector_name} failed after {self.max_retries} attempts")
        return {
            "success": False,
            "error": f"Failed after {self.max_retries} attempts",
            "last_error": result.get("error", "Unknown error")
        }
    
    def log_error(self, collector_name: str, error: str):
        """Log an error for aggregation."""
        self.error_log.append({
            "collector": collector_name,
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": "medium"
        })
        
        # Keep only recent errors (last hour)
        cutoff = datetime.now(timezone.utc).timestamp() - 3600
        self.error_log = [
            e for e in self.error_log 
            if datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")).timestamp() > cutoff
        ]
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors."""
        if not self.error_log:
            return {"total_errors": 0, "by_collector": {}, "recent_errors": []}
        
        by_collector = {}
        for error in self.error_log:
            collector = error["collector"]
            by_collector[collector] = by_collector.get(collector, 0) + 1
        
        return {
            "total_errors": len(self.error_log),
            "by_collector": by_collector,
            "recent_errors": self.error_log[-5:],  # Last 5 errors
            "needs_attention": len(self.error_log) >= 5
        }

# Test the runner
if __name__ == "__main__":
    from scripts.collectors.health_collector import HealthCollector
    
    runner = CollectorRunner()
    collector = HealthCollector()
    result = runner.run_with_retry(collector)
    
    print("Result:", result)
    print("Error Summary:", runner.get_error_summary())

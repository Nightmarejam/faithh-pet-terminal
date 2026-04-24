"""
Health check and monitoring service
"""

import time
import os
from typing import Dict, Any
from ..models import HealthStatus
from ..config import config
from ..providers import provider_registry

class HealthService:
    """Health check and monitoring service"""
    
    def __init__(self):
        self.start_time = time.time()
    
    def get_health_status(self) -> HealthStatus:
        """Get overall system health status"""
        components = {}
        overall_status = "healthy"
        
        # Check configuration
        try:
            config_sections = list(config._config.keys())
            components["config"] = "ok" if config_sections else "missing"
            if not config_sections:
                overall_status = "degraded"
        except Exception as e:
            components["config"] = f"error: {str(e)}"
            overall_status = "unhealthy"
        
        # Check providers
        try:
            provider_status = provider_registry.health_check_all()
            available_providers = [name for name, status in provider_status.items() if status.available]
            
            if available_providers:
                components["providers"] = f"ok ({len(available_providers)} available)"
            else:
                components["providers"] = "none_available"
                overall_status = "degraded"
                
            # Add individual provider status
            for name, status in provider_status.items():
                components[f"provider_{name}"] = "ok" if status.available else f"error: {status.error}"
        except Exception as e:
            components["providers"] = f"error: {str(e)}"
            overall_status = "unhealthy"
        
        # Check environment
        try:
            env_vars = ["ANTHROPIC_API_KEY"]
            missing_vars = [var for var in env_vars if not os.environ.get(var)]
            
            if missing_vars:
                components["environment"] = f"missing: {', '.join(missing_vars)}"
                overall_status = "degraded"
            else:
                components["environment"] = "ok"
        except Exception as e:
            components["environment"] = f"error: {str(e)}"
            overall_status = "unhealthy"
        
        # Check file system
        try:
            config_exists = os.path.exists("config.yaml")
            components["filesystem"] = "ok" if config_exists else "config_missing"
            if not config_exists:
                overall_status = "degraded"
        except Exception as e:
            components["filesystem"] = f"error: {str(e)}"
            overall_status = "unhealthy"
        
        return HealthStatus(
            status=overall_status,
            components=components,
            timestamp=time.time(),
            uptime=time.time() - self.start_time
        )
    
    def get_detailed_health(self) -> Dict[str, Any]:
        """Get detailed health information"""
        health_status = self.get_health_status()
        
        return {
            "status": health_status.status,
            "timestamp": health_status.timestamp,
            "uptime": health_status.uptime,
            "components": health_status.components,
            "system_info": {
                "python_version": os.sys.version,
                "working_directory": os.getcwd(),
                "config_loaded": bool(config._config),
                "config_sections": list(config._config.keys()),
            },
            "providers": {
                "registered": provider_registry.list_providers(),
                "available": provider_registry.get_available_providers(),
                "health_status": provider_registry.health_check_all()
            }
        }
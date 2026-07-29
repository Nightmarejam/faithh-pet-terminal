"""
FAITHH Connection Monitor

Provides service health monitoring and graceful fallback mechanisms
for all external services that FAITHH depends on.

Priority: Phase 4.1 - Reliability Foundation
"""

import os
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Callable
import requests
import json
from enum import Enum

class ServiceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class ServiceHealth:
    """Health status for a single service"""

    def __init__(
        self,
        name: str,
        url: str,
        timeout: int = 5,
        required_for_overall: bool = True,
        auth: Optional[Tuple[str, str, str]] = None,
    ):
        self.name = name
        self.url = url
        self.timeout = timeout
        # (env_var, header_name, value_template) for authenticated probes. Resolved at
        # check time, not here — the key may be loaded after this object is built, and
        # capturing it at init made a later-set key invisible to the monitor.
        self.auth = auth
        # If False, failures never mark UNHEALTHY (clamped to DEGRADED) and do not affect
        # overall_status. Use for optional infra (remote Chroma, provider probes without keys).
        self.required_for_overall = required_for_overall
        self.status = ServiceStatus.UNKNOWN
        self.last_check = None
        self.response_time = None
        self.error_count = 0
        self.consecutive_failures = 0
        self.total_checks = 0
        self.successful_checks = 0
        self.last_error = None
        self.fallback_available = False
        self.fallback_url = None
        
    def update_status(self, status: ServiceStatus, response_time: float = None, error: str = None):
        """Update service health status"""
        self.status = status
        self.last_check = datetime.now()
        self.response_time = response_time
        self.last_error = error
        self.total_checks += 1
        
        if status == ServiceStatus.HEALTHY:
            self.successful_checks += 1
            self.consecutive_failures = 0
        else:
            self.consecutive_failures += 1
            self.error_count += 1
    
    def get_uptime_percentage(self) -> float:
        """Calculate uptime percentage"""
        if self.total_checks == 0:
            return 0.0
        return (self.successful_checks / self.total_checks) * 100
    
    def is_available(self) -> bool:
        """Check if service is available for use"""
        return self.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses"""
        return {
            'name': self.name,
            'url': self.url,
            'status': self.status.value,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'response_time': self.response_time,
            'uptime_percentage': self.get_uptime_percentage(),
            'error_count': self.error_count,
            'consecutive_failures': self.consecutive_failures,
            'last_error': self.last_error,
            'fallback_available': self.fallback_available
        }

class ConnectionMonitor:
    # Logic for Humans: Background poller that pings configured URLs (Chroma, Ollama, Groq, …), tracks healthy/degraded, and powers /api/health summaries.
    """Main connection monitoring system"""
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.services: Dict[str, ServiceHealth] = {}
        self.monitoring_thread = None
        self.monitoring_active = False
        self.fallback_handlers: Dict[str, Callable] = {}
        self.health_callbacks: List[Callable] = []
        
        # Initialize services
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all services to monitor"""
        # "Unhealthy services: 1" historically came from optional deps marked UNHEALTHY —
        # e.g. remote Chroma on servicebox timing out or connection refused while
        # the UI/backend still runs.
        #
        # Groq/Gemini used to be probed with no credentials, so they returned 401/403 on
        # every check and sat permanently "degraded" with 0% uptime whether the keys were
        # valid, invalid, or absent — a reading that carried no information. They now send
        # the configured key (see `auth` below), so degraded means something again.
        services_config = [
            # Do not HTTP-poll this Flask app from inside the same process (localhost:5557/health).
            # That produced false "Connection error" / UNHEALTHY during startup and is redundant:
            # /api/health already proves the server is accepting requests.
            {
                'name': 'chromadb',
                # Chroma v1 /api/v1/heartbeat returns HTTP 410 on current server; v2 is canonical.
                'url': 'http://servicebox.taileb8c60.ts.net:8000/api/v2/heartbeat',
                'timeout': 3,
                'fallback_url': None,
                'required_for_overall': False,
            },
            {
                'name': 'ollama',
                'url': 'http://localhost:11434/api/tags',
                'timeout': 5,
                'fallback_url': None,
                'required_for_overall': True,
            },
            {
                'name': 'groq',
                'url': 'https://api.groq.com/openai/v1/models',
                'timeout': 10,
                'fallback_url': None,
                'required_for_overall': False,
                'auth': ('GROQ_API_KEY', 'Authorization', 'Bearer {key}'),
            },
            {
                'name': 'gemini',
                # Key goes in a header, never a ?key= query param: URLs leak into logs,
                # proxies and error messages.
                'url': 'https://generativelanguage.googleapis.com/v1/models',
                'timeout': 10,
                'fallback_url': None,
                'required_for_overall': False,
                'auth': (('GEMINI_API_KEY', 'GOOGLE_API_KEY'), 'x-goog-api-key', '{key}'),
            },
        ]

        for config in services_config:
            service = ServiceHealth(
                name=config['name'],
                url=config['url'],
                timeout=config['timeout'],
                required_for_overall=config.get('required_for_overall', True),
                auth=config.get('auth'),
            )
            service.fallback_url = config['fallback_url']
            self.services[config['name']] = service
    
    def check_service_health(self, service_name: str) -> Tuple[bool, Optional[str]]:
        """Check health of a specific service"""
        if service_name not in self.services:
            return False, f"Service {service_name} not configured"
        
        service = self.services[service_name]

        # Authenticated probes: without a key, /models returns 401 (Groq) or 403 (Gemini)
        # unconditionally, so the monitor reported a health it never actually measured.
        headers = {}
        if service.auth:
            env_names, header_name, template = service.auth
            if isinstance(env_names, str):
                env_names = (env_names,)
            key = next((os.environ[n] for n in env_names if os.environ.get(n)), None)
            if not key:
                # No key is a configuration state, not a service outage. Say so plainly
                # rather than reporting the provider as broken.
                service.update_status(
                    ServiceStatus.DEGRADED, None,
                    f"API key not configured ({' or '.join(env_names)})",
                )
                return False, "API key not configured"
            headers[header_name] = template.format(key=key)

        try:
            start_time = time.time()
            response = requests.get(service.url, headers=headers, timeout=service.timeout)
            response_time = time.time() - start_time

            if response.status_code == 200:
                service.update_status(ServiceStatus.HEALTHY, response_time)
                return True, None
            elif response.status_code >= 500:
                st = (
                    ServiceStatus.UNHEALTHY
                    if service.required_for_overall
                    else ServiceStatus.DEGRADED
                )
                service.update_status(st, response_time, f"HTTP {response.status_code}")
                return False, f"Server error: HTTP {response.status_code}"
            else:
                service.update_status(ServiceStatus.DEGRADED, response_time, f"HTTP {response.status_code}")
                return True, f"Service degraded: HTTP {response.status_code}"

        except requests.exceptions.Timeout:
            # Optional services (e.g. remote Chroma): timeout should not flip /api/health to
            # "Unhealthy services: N" — treat as degraded reachability only.
            st = (
                ServiceStatus.UNHEALTHY
                if service.required_for_overall
                else ServiceStatus.DEGRADED
            )
            service.update_status(st, None, "Request timeout")
            return False, "Request timeout"
        except requests.exceptions.ConnectionError:
            st = (
                ServiceStatus.UNHEALTHY
                if service.required_for_overall
                else ServiceStatus.DEGRADED
            )
            service.update_status(st, None, "Connection error")
            return False, "Connection error"
        except Exception as e:
            st = (
                ServiceStatus.UNHEALTHY
                if service.required_for_overall
                else ServiceStatus.DEGRADED
            )
            service.update_status(st, None, str(e))
            return False, f"Unexpected error: {str(e)}"
    
    def check_all_services(self) -> Dict[str, Tuple[bool, Optional[str]]]:
        """Check health of all configured services"""
        results = {}
        for service_name in self.services:
            results[service_name] = self.check_service_health(service_name)
        return results
    
    def get_service_status(self, service_name: str) -> Optional[ServiceHealth]:
        """Get current status of a service"""
        return self.services.get(service_name)
    
    def is_service_available(self, service_name: str) -> bool:
        """Check if service is available for use"""
        service = self.get_service_status(service_name)
        return service.is_available() if service else False
    
    def get_healthy_services(self) -> List[str]:
        """Get list of healthy services"""
        return [name for name, service in self.services.items() if service.is_available()]
    
    def get_unhealthy_services(self) -> List[str]:
        """Get list of unhealthy services"""
        return [name for name, service in self.services.items() if not service.is_available()]
    
    def register_fallback_handler(self, service_name: str, handler: Callable):
        """Register a fallback handler for a service"""
        self.fallback_handlers[service_name] = handler
    
    def register_health_callback(self, callback: Callable):
        """Register a callback for health status changes"""
        self.health_callbacks.append(callback)
    
    def trigger_fallback(self, service_name: str, *args, **kwargs):
        """Trigger fallback for a service"""
        if service_name in self.fallback_handlers:
            try:
                return self.fallback_handlers[service_name](*args, **kwargs)
            except Exception as e:
                print(f"Fallback handler failed for {service_name}: {e}")
                return None
        return None
    
    def start_monitoring(self):
        """Start background monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        print("🔍 Connection monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        print("🔍 Connection monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                self.check_all_services()
                
                # Notify callbacks of any status changes
                for callback in self.health_callbacks:
                    try:
                        callback(self.get_all_statuses())
                    except Exception as e:
                        print(f"Health callback error: {e}")
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"Monitoring loop error: {e}")
                time.sleep(self.check_interval)
    
    def get_all_statuses(self) -> Dict[str, Dict]:
        """Get all service statuses"""
        return {name: service.to_dict() for name, service in self.services.items()}
    
    def get_system_health_summary(self) -> Dict:
        """Get overall system health summary"""
        all_svcs = list(self.services.values())
        required = [s for s in all_svcs if s.required_for_overall]

        total_services = len(all_svcs)
        healthy_services = len([s for s in all_svcs if s.status == ServiceStatus.HEALTHY])
        degraded_services = len([s for s in all_svcs if s.status == ServiceStatus.DEGRADED])
        unhealthy_services = len([s for s in all_svcs if s.status == ServiceStatus.UNHEALTHY])

        # Overall line matches required deps only (Ollama by default; no in-process backend self-ping).
        req_healthy = len([s for s in required if s.status == ServiceStatus.HEALTHY])
        req_degraded = len([s for s in required if s.status == ServiceStatus.DEGRADED])
        req_unhealthy = len([s for s in required if s.status == ServiceStatus.UNHEALTHY])

        overall_status = ServiceStatus.HEALTHY
        if req_unhealthy > 0:
            overall_status = ServiceStatus.UNHEALTHY
        elif req_degraded > 0:
            overall_status = ServiceStatus.DEGRADED

        return {
            'overall_status': overall_status.value,
            'total_services': total_services,
            'healthy_services': healthy_services,
            'degraded_services': degraded_services,
            'unhealthy_services': unhealthy_services,
            'required_unhealthy_services': req_unhealthy,
            'monitoring_active': self.monitoring_active,
            'last_check': max([s.last_check for s in self.services.values() if s.last_check], default=None),
            'services': self.get_all_statuses(),
        }

# Fallback handlers for common services
def ollama_fallback_handler(query: str, model: str = "qwen25-grounded:latest") -> Optional[str]:
    # Logic for Humans: Last-resort try: hit a secondary Ollama port (11435) if the primary daemon is down.
    """Fallback handler for Ollama service"""
    try:
        # Try alternative Ollama endpoint or different model
        fallback_url = "http://localhost:11435/api/generate"  # Alternative port
        payload = {
            "model": model,
            "prompt": query,
            "stream": False
        }
        
        response = requests.post(fallback_url, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json().get("response", "")
    except Exception:
        pass
    
    return None

def groq_fallback_handler(query: str, model: str = "llama-3.3-70b-versatile") -> Optional[str]:
    # Logic for Humans: Placeholder hook for when Groq fails — reserved for future cache or alternate provider logic.
    """Fallback handler for Groq service"""
    try:
        # Switch to different provider or use cached response
        # This would integrate with the local optimization system
        return None  # Placeholder - would implement actual fallback logic
    except Exception:
        pass
    
    return None

# Global instance
connection_monitor = ConnectionMonitor()

# Flask integration helper
def with_service_fallback(service_name: str):
    # Logic for Humans: Decorator — run the real function if the named service is up, otherwise try registered fallback handlers.
    """Decorator to provide automatic fallback for service calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if connection_monitor.is_service_available(service_name):
                return func(*args, **kwargs)
            else:
                # Try fallback
                fallback_result = connection_monitor.trigger_fallback(service_name, *args, **kwargs)
                if fallback_result is not None:
                    return fallback_result
                
                # Raise error if no fallback available
                service = connection_monitor.get_service_status(service_name)
                raise Exception(f"Service {service_name} unavailable and no fallback available")
        return wrapper
    return decorator

# Health check endpoint for Flask
def create_health_endpoint():
    # Logic for Humans: Factory that returns a Flask view function reporting connection_monitor’s aggregate service health (200 vs 503).
    """Create health check endpoint for Flask"""
    from flask import jsonify
    
    def health_check():
        try:
            summary = connection_monitor.get_system_health_summary()
            
            # Set HTTP status based on overall health
            status_code = 200
            if summary['overall_status'] == 'unhealthy':
                status_code = 503
            elif summary['overall_status'] == 'degraded':
                status_code = 200  # Still serve but indicate issues
            
            return jsonify(summary), status_code
            
        except Exception as e:
            return jsonify({
                'overall_status': 'error',
                'error': str(e)
            }), 500
    
    return health_check

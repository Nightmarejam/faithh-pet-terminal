#!/usr/bin/env python3
"""
FAITHH Phase 4 Monitoring Script

Monitors system health, performance, and AI optimization effectiveness.
Designed for single-user deployment with family deployment readiness.
"""

import requests
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

class Phase4Monitor:
    def __init__(self):
        self.backend_url = "http://localhost:5557"
        self.monitoring_log = Path("/home/jonat/ai-stack/monitoring/phase4_monitoring.log")
        self.monitoring_log.parent.mkdir(exist_ok=True)
        
    def log_event(self, event_type: str, message: str, status: str = "INFO"):
        """Log monitoring events"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{status}] {event_type}: {message}\n"
        
        # Write to log file
        with open(self.monitoring_log, "a") as f:
            f.write(log_entry)
        
        # Also print to console
        print(f"[{status}] {event_type}: {message}")
    
    def check_backend_health(self) -> bool:
        """Check backend health"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_event("HEALTH_CHECK", "Backend health check passed", "SUCCESS")
                return True
            else:
                self.log_event("HEALTH_CHECK", f"Backend health failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log_event("HEALTH_CHECK", f"Backend health error: {e}", "ERROR")
            return False
    
    def check_enhanced_health(self) -> dict:
        """Check enhanced health endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_event("ENHANCED_HEALTH", "Enhanced health check passed", "SUCCESS")
                return data
            else:
                self.log_event("ENHANCED_HEALTH", f"Enhanced health failed: {response.status_code}", "ERROR")
                return {}
        except Exception as e:
            self.log_event("ENHANCED_HEALTH", f"Enhanced health error: {e}", "ERROR")
            return {}
    
    def test_chat_functionality(self) -> bool:
        """Test chat endpoint functionality"""
        try:
            payload = {
                "message": "health check test",
                "model": "qwen25-grounded:latest"
            }
            response = requests.post(
                f"{self.backend_url}/api/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_event("CHAT_TEST", "Chat functionality test passed", "SUCCESS")
                    return True
                else:
                    self.log_event("CHAT_TEST", f"Chat failed: {data.get('error', 'unknown')}", "ERROR")
                    return False
            else:
                self.log_event("CHAT_TEST", f"Chat HTTP error: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log_event("CHAT_TEST", f"Chat test error: {e}", "ERROR")
            return False
    
    def test_ai_optimization(self) -> bool:
        """Test AI optimization functionality"""
        try:
            payload = {
                "message": "What are the recent changes to the FAITHH system?",
                # No model specified - should trigger optimization
            }
            response = requests.post(
                f"{self.backend_url}/api/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    model_used = data.get('model_used', 'unknown')
                    provider = data.get('provider', 'unknown')
                    self.log_event("AI_OPTIMIZATION", f"AI optimization working - Model: {model_used}, Provider: {provider}", "SUCCESS")
                    return True
                else:
                    self.log_event("AI_OPTIMIZATION", f"AI optimization failed: {data.get('error', 'unknown')}", "ERROR")
                    return False
            else:
                self.log_event("AI_OPTIMIZATION", f"AI optimization HTTP error: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log_event("AI_OPTIMIZATION", f"AI optimization error: {e}", "ERROR")
            return False
    
    def check_services_status(self) -> dict:
        """Check status of external services"""
        services = {
            'chromadb': 'http://192.158.1.10:8000',
            'ollama': 'http://localhost:11434',
        }
        
        status = {}
        for service, url in services.items():
            try:
                if service == 'chromadb':
                    response = requests.get(f"{url}/api/v2/heartbeat", timeout=5)
                else:  # ollama
                    response = requests.get(f"{url}/api/tags", timeout=5)
                
                if response.status_code == 200:
                    status[service] = "UP"
                    self.log_event("SERVICE_CHECK", f"{service} is UP", "SUCCESS")
                else:
                    status[service] = f"DOWN ({response.status_code})"
                    self.log_event("SERVICE_CHECK", f"{service} is DOWN: {response.status_code}", "WARNING")
            except Exception as e:
                status[service] = f"ERROR: {e}"
                self.log_event("SERVICE_CHECK", f"{service} error: {e}", "ERROR")
        
        return status
    
    def run_comprehensive_check(self) -> dict:
        """Run comprehensive system check"""
        self.log_event("MONITORING", "Starting comprehensive Phase 4 system check", "INFO")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        # Basic health
        results['checks']['backend_health'] = self.check_backend_health()
        
        # Enhanced health (if available)
        enhanced_health = self.check_enhanced_health()
        if enhanced_health:
            results['checks']['enhanced_health'] = enhanced_health
        
        # Chat functionality
        results['checks']['chat_functionality'] = self.test_chat_functionality()
        
        # AI optimization
        results['checks']['ai_optimization'] = self.test_ai_optimization()
        
        # External services
        results['checks']['services_status'] = self.check_services_status()
        
        # Overall status
        all_passed = all([
            results['checks']['backend_health'],
            results['checks']['chat_functionality'],
            results['checks']['ai_optimization']
        ])
        
        results['overall_status'] = "HEALTHY" if all_passed else "ISSUES_DETECTED"
        
        # Log overall result
        if all_passed:
            self.log_event("COMPREHENSIVE_CHECK", "All systems healthy", "SUCCESS")
        else:
            self.log_event("COMPREHENSIVE_CHECK", "Issues detected - check logs", "WARNING")
        
        return results
    
    def monitor_continuously(self, interval_minutes: int = 30):
        """Run continuous monitoring"""
        self.log_event("CONTINUOUS_MONITORING", f"Starting continuous monitoring (interval: {interval_minutes} minutes)", "INFO")
        
        while True:
            try:
                results = self.run_comprehensive_check()
                
                # If there are issues, wait shorter interval
                if results['overall_status'] != "HEALTHY":
                    self.log_event("CONTINUOUS_MONITORING", "Issues detected - reducing check interval", "WARNING")
                    time.sleep(300)  # 5 minutes
                else:
                    time.sleep(interval_minutes * 60)  # Normal interval
                    
            except KeyboardInterrupt:
                self.log_event("CONTINUOUS_MONITORING", "Monitoring stopped by user", "INFO")
                break
            except Exception as e:
                self.log_event("CONTINUOUS_MONITORING", f"Monitoring error: {e}", "ERROR")
                time.sleep(60)  # 1 minute retry on error

def main():
    """Main monitoring function"""
    monitor = Phase4Monitor()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        # Continuous monitoring mode
        interval = 30  # Default 30 minutes
        if len(sys.argv) > 2:
            interval = int(sys.argv[2])
        
        monitor.monitor_continuously(interval)
    else:
        # One-time check mode
        results = monitor.run_comprehensive_check()
        
        print("\n" + "="*50)
        print("🎯 PHASE 4 MONITORING RESULTS")
        print("="*50)
        print(f"Timestamp: {results['timestamp']}")
        print(f"Overall Status: {results['overall_status']}")
        print("\nCheck Results:")
        for check, result in results['checks'].items():
            status = "✅" if isinstance(result, bool) and result else "❌"
            print(f"  {status} {check}: {result}")
        print("="*50)

if __name__ == "__main__":
    main()

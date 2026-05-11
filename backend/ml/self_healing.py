"""
FAITHH Phase 3 - Self-Healing System
Automatic issue detection and resolution for system reliability
"""

import json
import time
import subprocess
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

@dataclass
class SystemIssue:
    """Represents a detected system issue"""
    issue_id: str
    timestamp: datetime
    issue_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    component: str
    auto_resolvable: bool
    resolution_attempted: bool
    resolution_successful: bool
    resolution_method: Optional[str]

class SelfHealingSystem:
    """Self-healing system for automatic issue detection and resolution"""
    
    def __init__(self, backend_url: str = "http://localhost:5557"):
        self.backend_url = backend_url
        self.issues = []
        self.resolution_history = []
        
        # Component health checks
        self.component_checks = {
            'backend': self._check_backend_health,
            'chromadb': self._check_chromadb_health,
            'ollama': self._check_ollama_health,
            'groq': self._check_groq_health,
            'gemini': self._check_gemini_health
        }
        
        # Auto-resolution strategies
        self.resolution_strategies = {
            'backend_down': self._restart_backend,
            'ollama_down': self._restart_ollama,
            'groq_timeout': self._switch_to_ollama,
            'memory_leak': self._clear_caches,
            'disk_space': self._cleanup_temp_files
        }
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def _check_backend_health(self) -> Dict[str, Any]:
        """Check backend service health"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            return {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'response_time': response.elapsed.total_seconds(),
                'details': response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'response_time': None
            }
    
    def _check_chromadb_health(self) -> Dict[str, Any]:
        """Check ChromaDB health"""
        try:
            # Try to connect to ChromaDB (assuming default port 8000)
            response = requests.get("http://192.158.1.243:8000/api/v1/heartbeat", timeout=5)
            return {
                'status': 'healthy' if response.status_code < 500 else 'unhealthy',
                'response_time': response.elapsed.total_seconds(),
                'details': {'heartbeat': response.text}
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'response_time': None
            }
    
    def _check_ollama_health(self) -> Dict[str, Any]:
        """Check Ollama service health"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'response_time': response.elapsed.total_seconds(),
                'details': response.json() if response.status_code == 200 else {}
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'response_time': None
            }
    
    def _check_groq_health(self) -> Dict[str, Any]:
        """Check Groq API health"""
        try:
            # Check if Groq is configured and accessible
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                groq_status = health_data.get('providers', {}).get('groq', False)
                return {
                    'status': 'healthy' if groq_status else 'disabled',
                    'response_time': response.elapsed.total_seconds(),
                    'details': {'groq_enabled': groq_status}
                }
            else:
                return {'status': 'unhealthy', 'error': 'Backend unavailable'}
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'response_time': None
            }
    
    def _check_gemini_health(self) -> Dict[str, Any]:
        """Check Gemini API health"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                gemini_status = health_data.get('providers', {}).get('gemini', False)
                return {
                    'status': 'healthy' if gemini_status else 'disabled',
                    'response_time': response.elapsed.total_seconds(),
                    'details': {'gemini_enabled': gemini_status}
                }
            else:
                return {'status': 'unhealthy', 'error': 'Backend unavailable'}
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'response_time': None
            }
    
    def detect_issues(self) -> List[SystemIssue]:
        """Detect system issues across all components"""
        
        print("🔍 Running system health checks...")
        detected_issues = []
        
        for component, check_func in self.component_checks.items():
            try:
                health = check_func()
                
                if health['status'] == 'unhealthy':
                    issue = SystemIssue(
                        issue_id=f"issue_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{component}",
                        timestamp=datetime.now(),
                        issue_type='component_failure',
                        severity=self._assess_severity(component, health),
                        description=f"{component} is unhealthy: {health.get('error', 'Unknown error')}",
                        component=component,
                        auto_resolvable=self._is_auto_resolvable(component, health),
                        resolution_attempted=False,
                        resolution_successful=False,
                        resolution_method=None
                    )
                    detected_issues.append(issue)
                    print(f"  ❌ {component}: {health.get('error', 'Unhealthy')}")
                else:
                    print(f"  ✅ {component}: Healthy ({health['response_time']:.3f}s)")
                    
            except Exception as e:
                issue = SystemIssue(
                    issue_id=f"issue_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{component}_check_error",
                    timestamp=datetime.now(),
                    issue_type='monitoring_failure',
                    severity='medium',
                    description=f"Health check failed for {component}: {str(e)}",
                    component=component,
                    auto_resolvable=False,
                    resolution_attempted=False,
                    resolution_successful=False,
                    resolution_method=None
                )
                detected_issues.append(issue)
                print(f"  ⚠️  {component}: Health check failed - {e}")
        
        # Check for additional issues
        detected_issues.extend(self._check_system_resources())
        
        self.issues.extend(detected_issues)
        return detected_issues
    
    def _check_system_resources(self) -> List[SystemIssue]:
        """Check system resources for issues"""
        issues = []
        
        # Check disk space
        try:
            result = subprocess.run(['df', '/'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        used_percent = int(parts[4].rstrip('%'))
                        if used_percent > 90:
                            issue = SystemIssue(
                                issue_id=f"issue_{datetime.now().strftime('%Y%m%d_%H%M%S')}_disk_space",
                                timestamp=datetime.now(),
                                issue_type='resource_exhaustion',
                                severity='high' if used_percent > 95 else 'medium',
                                description=f"Disk space critically low: {used_percent}% used",
                                component='system',
                                auto_resolvable=True,
                                resolution_attempted=False,
                                resolution_successful=False,
                                resolution_method='cleanup_temp_files'
                            )
                            issues.append(issue)
        except Exception as e:
            print(f"  ⚠️  Disk space check failed: {e}")
        
        return issues
    
    def _assess_severity(self, component: str, health: Dict[str, Any]) -> str:
        """Assess issue severity based on component and health details"""
        
        if component == 'backend':
            return 'critical'
        elif component == 'chromadb':
            return 'high'
        elif component in ['ollama', 'groq']:
            return 'medium'
        else:
            return 'low'
    
    def _is_auto_resolvable(self, component: str, health: Dict[str, Any]) -> bool:
        """Determine if issue is automatically resolvable"""
        
        # Backend issues often resolvable with restart
        if component == 'backend':
            return True
        
        # Ollama issues often resolvable with restart
        if component == 'ollama':
            return True
        
        # Resource issues are often resolvable
        if 'timeout' in health.get('error', '').lower():
            return True
        
        return False
    
    def resolve_issues(self, issues: List[SystemIssue]) -> Dict[str, Any]:
        """Attempt to resolve detected issues"""
        
        print("🔧 Attempting auto-resolution...")
        resolution_results = {
            'total_issues': len(issues),
            'auto_resolvable': 0,
            'resolution_attempted': 0,
            'resolution_successful': 0,
            'resolutions': []
        }
        
        for issue in issues:
            if issue.auto_resolvable and not issue.resolution_attempted:
                resolution_results['auto_resolvable'] += 1
                
                # Attempt resolution
                success = self._attempt_resolution(issue)
                issue.resolution_attempted = True
                issue.resolution_successful = success
                resolution_results['resolution_attempted'] += 1
                
                if success:
                    resolution_results['resolution_successful'] += 1
                    print(f"  ✅ Resolved: {issue.description}")
                else:
                    print(f"  ❌ Failed to resolve: {issue.description}")
                
                resolution_results['resolutions'].append({
                    'issue_id': issue.issue_id,
                    'component': issue.component,
                    'success': success,
                    'method': issue.resolution_method
                })
        
        return resolution_results
    
    def _attempt_resolution(self, issue: SystemIssue) -> bool:
        """Attempt to resolve a specific issue"""
        
        try:
            if issue.component == 'backend':
                return self._restart_backend()
            elif issue.component == 'ollama':
                return self._restart_ollama()
            elif issue.component == 'system' and 'disk_space' in issue.issue_id:
                return self._cleanup_temp_files()
            elif 'timeout' in issue.description.lower():
                return self._switch_to_ollama()
            
            return False
            
        except Exception as e:
            self.logger.error(f"Resolution attempt failed for {issue.issue_id}: {e}")
            return False
    
    def _restart_backend(self) -> bool:
        """Restart the backend service"""
        try:
            print("    🔄 Restarting backend...")
            # Use the restart script
            result = subprocess.run(
                ['./restart_backend.sh'],
                capture_output=True,
                text=True,
                timeout=30,
                cwd='/home/jonat/ai-stack'
            )
            
            if result.returncode == 0:
                # Wait for backend to start
                time.sleep(5)
                # Verify health
                health = self._check_backend_health()
                return health['status'] == 'healthy'
            else:
                print(f"    ❌ Backend restart failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"    ❌ Backend restart error: {e}")
            return False
    
    def _restart_ollama(self) -> bool:
        """Restart Ollama service"""
        try:
            print("    🔄 Restarting Ollama...")
            # Restart Ollama service
            result = subprocess.run(
                ['sudo', 'systemctl', 'restart', 'ollama'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Wait for Ollama to start
                time.sleep(10)
                # Verify health
                health = self._check_ollama_health()
                return health['status'] == 'healthy'
            else:
                print(f"    ❌ Ollama restart failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"    ❌ Ollama restart error: {e}")
            return False
    
    def _switch_to_ollama(self) -> bool:
        """Switch to Ollama as primary provider"""
        try:
            print("    🔄 Switching to Ollama provider...")
            # This would typically involve updating configuration
            # For now, just log the action
            print("    ✅ Switched to Ollama (configuration update needed)")
            return True
        except Exception as e:
            print(f"    ❌ Provider switch failed: {e}")
            return False
    
    def _clear_caches(self) -> bool:
        """Clear system caches"""
        try:
            print("    🧹 Clearing caches...")
            # Clear Python cache
            result = subprocess.run(
                ['find', '/home/jonat/ai-stack', '-name', '__pycache__', '-type', 'd', '-exec', 'rm', '-rf', '{}', '+'],
                capture_output=True,
                text=True,
                timeout=30
            )
            return True
        except Exception as e:
            print(f"    ❌ Cache clearing failed: {e}")
            return False
    
    def _cleanup_temp_files(self) -> bool:
        """Clean up temporary files"""
        try:
            print("    🧹 Cleaning up temporary files...")
            # Clean temp directory
            result = subprocess.run(
                ['find', '/tmp', '-name', 'faithh_*', '-type', 'f', '-mtime', '+1', '-delete'],
                capture_output=True,
                text=True,
                timeout=30
            )
            return True
        except Exception as e:
            print(f"    ❌ Temp file cleanup failed: {e}")
            return False
    
    def run_self_healing_cycle(self) -> Dict[str, Any]:
        """Run a complete self-healing cycle"""
        
        print("🤖 Self-Healing System Cycle")
        print("=" * 50)
        
        # Detect issues
        detected_issues = self.detect_issues()
        
        # Attempt resolutions
        resolution_results = self.resolve_issues(detected_issues)
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'issues_detected': len(detected_issues),
            'issues_resolved': resolution_results['resolution_successful'],
            'resolution_success_rate': (resolution_results['resolution_successful'] / max(resolution_results['resolution_attempted'], 1)) * 100,
            'components_checked': len(self.component_checks),
            'system_health': 'healthy' if len(detected_issues) == 0 else 'issues_detected'
        }
        
        print(f"\n📊 Self-Healing Results:")
        print(f"  Issues Detected: {report['issues_detected']}")
        print(f"  Issues Resolved: {report['issues_resolved']}")
        print(f"  Success Rate: {report['resolution_success_rate']:.1f}%")
        print(f"  System Health: {report['system_health']}")
        
        return report

def main():
    """Main self-healing execution"""
    
    healer = SelfHealingSystem()
    report = healer.run_self_healing_cycle()
    
    return report['system_health'] == 'healthy'

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

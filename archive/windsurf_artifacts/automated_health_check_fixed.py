#!/usr/bin/env python3
"""
Automated Health Check System (Fixed Version)
Monitors system health and generates alerts
"""

import json
import requests
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import logging

class AutomatedHealthCheck:
    """Automated health monitoring system"""
    
    def __init__(self):
        self.project_root = Path("/home/jonat/ai-stack")
        self.backend_url = "http://localhost:5557"
        self.chromadb_url = "http://100.79.85.32:8000"
        self.log_file = self.project_root / "logs" / "health_check.log"
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Health check thresholds
        self.thresholds = {
            "response_time": 5.0,  # seconds
            "uptime_percentage": 99.0,
            "error_rate": 1.0,  # percentage
            "memory_usage": 80.0,  # percentage
            "cache_hit_rate": 70.0  # percentage
        }
        
        # Setup logging
        logging.basicConfig(
            filename=str(self.log_file),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check"""
        print("🔍 Starting Automated Health Check")
        print("=" * 50)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "checks": {},
            "alerts": [],
            "metrics": {},
            "recommendations": []
        }
        
        # Run individual checks
        checks = [
            ("backend_health", self.check_backend_health),
            ("chromadb_health", self.check_chromadb_health),
            ("system_resources", self.check_system_resources),
            ("log_analysis", self.check_log_analysis),
            ("service_dependencies", self.check_service_dependencies)
        ]
        
        for check_name, check_func in checks:
            print(f"   🔍 Checking {check_name}...")
            try:
                check_result = check_func()
                results["checks"][check_name] = check_result
                
                # Add alerts if needed
                if check_result.get("status") == "error":
                    results["alerts"].append({
                        "service": check_name,
                        "severity": "high",
                        "message": check_result.get("error", "Unknown error")
                    })
                elif check_result.get("status") == "warning":
                    results["alerts"].append({
                        "service": check_name,
                        "severity": "medium",
                        "message": check_result.get("warning", "Warning condition")
                    })
                    
            except Exception as e:
                results["checks"][check_name] = {"status": "error", "error": str(e)}
                results["alerts"].append({
                    "service": check_name,
                    "severity": "high",
                    "message": f"Check failed: {str(e)}"
                })
        
        # Calculate overall status
        results["overall_status"] = self.calculate_overall_status(results)
        
        # Generate metrics
        results["metrics"] = self.calculate_metrics(results)
        
        # Generate recommendations
        results["recommendations"] = self.generate_recommendations(results)
        
        # Save results
        self.save_health_check_results(results)
        
        # Log summary
        self.log_health_summary(results)
        
        print(f"\n✅ Health Check Complete")
        print(f"📊 Overall Status: {results['overall_status']}")
        print(f"🚨 Alerts: {len(results['alerts'])}")
        print(f"💡 Recommendations: {len(results['recommendations'])}")
        
        return results
    
    def check_backend_health(self) -> Dict[str, Any]:
        """Check FAITHH backend health"""
        try:
            # Health endpoint
            start_time = time.time()
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                # Get detailed status
                status_response = requests.get(f"{self.backend_url}/api/status", timeout=10)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    
                    return {
                        "status": "healthy",
                        "response_time": response_time,
                        "backend_status": status_data,
                        "uptime": status_data.get("uptime", "unknown"),
                        "active_connections": status_data.get("active_connections", 0)
                    }
                else:
                    return {
                        "status": "warning",
                        "response_time": response_time,
                        "warning": "Status endpoint not responding"
                    }
            else:
                return {
                    "status": "error",
                    "response_time": response_time,
                    "error": f"Health check failed with status {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "error": "Backend health check timed out"
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "error": "Cannot connect to backend"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Backend health check failed: {str(e)}"
            }
    
    def check_chromadb_health(self) -> Dict[str, Any]:
        """Check ChromaDB health"""
        try:
            # ChromaDB heartbeat
            start_time = time.time()
            response = requests.get(f"{self.chromadb_url}/api/v2/heartbeat", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                # Try to get collection info (may fail, that's okay)
                try:
                    collections_response = requests.get(f"{self.chromadb_url}/api/v2/collections", timeout=10)
                    
                    if collections_response.status_code == 200:
                        collections_data = collections_response.json()
                        
                        return {
                            "status": "healthy",
                            "response_time": response_time,
                            "collections_count": len(collections_data),
                            "database_status": "operational"
                        }
                    else:
                        return {
                            "status": "healthy",
                            "response_time": response_time,
                            "warning": "Collections endpoint not responding but heartbeat works"
                        }
                except Exception as e:
                    return {
                        "status": "healthy",
                        "response_time": response_time,
                        "warning": "Collections check failed but heartbeat works"
                    }
            else:
                return {
                    "status": "error",
                    "response_time": response_time,
                    "error": f"ChromaDB heartbeat failed with status {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "error": "ChromaDB health check timed out"
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "error": "Cannot connect to ChromaDB"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"ChromaDB health check failed: {str(e)}"
            }
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            # Memory usage
            memory_result = subprocess.run(['free', '-h'], capture_output=True, text=True)
            memory_lines = memory_result.stdout.split('\n')
            
            memory_usage = 0
            for line in memory_lines:
                if line.startswith('Mem:'):
                    parts = line.split()
                    if len(parts) >= 3:
                        used = parts[2]
                        total = parts[1]
                        memory_usage = self.parse_memory_usage(used, total)
                        break
            
            # Disk usage
            disk_result = subprocess.run(['df', '-h', '/home'], capture_output=True, text=True)
            disk_lines = disk_result.stdout.split('\n')
            
            disk_usage = 0
            for line in disk_lines:
                if line.startswith('/dev/'):
                    parts = line.split()
                    if len(parts) >= 5:
                        disk_usage = int(parts[4].rstrip('%'))
                        break
            
            # CPU usage (simplified)
            cpu_result = subprocess.run(['top', '-bn1'], capture_output=True, text=True)
            cpu_usage = self.parse_cpu_usage(cpu_result.stdout)
            
            # Determine status
            status = "healthy"
            warnings = []
            
            if memory_usage > self.thresholds["memory_usage"]:
                status = "warning"
                warnings.append(f"High memory usage: {memory_usage}%")
            
            if disk_usage > 90:
                status = "warning"
                warnings.append(f"High disk usage: {disk_usage}%")
            
            if cpu_usage > 80:
                status = "warning"
                warnings.append(f"High CPU usage: {cpu_usage}%")
            
            result = {
                "status": status,
                "memory_usage": memory_usage,
                "disk_usage": disk_usage,
                "cpu_usage": cpu_usage,
                "thresholds": self.thresholds
            }
            
            if warnings:
                result["warnings"] = warnings
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"System resource check failed: {str(e)}"
            }
    
    def check_log_analysis(self) -> Dict[str, Any]:
        """Analyze log files for issues"""
        try:
            log_file = self.project_root / "backend.log"
            
            if not log_file.exists():
                return {
                    "status": "warning",
                    "warning": "Backend log file not found"
                }
            
            # Read last 100 lines
            with open(log_file, 'r') as f:
                lines = f.readlines()[-100:]
            
            error_count = 0
            warning_count = 0
            recent_errors = []
            
            for line in lines:
                if 'ERROR' in line:
                    error_count += 1
                    if len(recent_errors) < 5:
                        recent_errors.append(line.strip())
                elif 'WARNING' in line:
                    warning_count += 1
            
            # Determine status
            status = "healthy"
            warnings = []
            
            if error_count > 5:
                status = "warning"
                warnings.append(f"High error count: {error_count} in last 100 lines")
            
            if warning_count > 10:
                status = "warning"
                warnings.append(f"High warning count: {warning_count} in last 100 lines")
            
            result = {
                "status": status,
                "error_count": error_count,
                "warning_count": warning_count,
                "lines_analyzed": len(lines),
                "recent_errors": recent_errors
            }
            
            if warnings:
                result["warnings"] = warnings
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Log analysis failed: {str(e)}"
            }
    
    def check_service_dependencies(self) -> Dict[str, Any]:
        """Check service dependencies"""
        try:
            # Try docker compose first
            try:
                docker_result = subprocess.run(['docker', 'compose', 'ps'], capture_output=True, text=True)
            except FileNotFoundError:
                # Try docker-compose as separate command
                try:
                    docker_result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True)
                except FileNotFoundError:
                    return {
                        "status": "warning",
                        "warning": "Docker Compose not available - check Docker services manually"
                    }
            
            if docker_result.returncode != 0:
                return {
                    "status": "error",
                    "error": "Docker Compose command failed"
                }
            
            services = {}
            lines = docker_result.stdout.split('\n')
            
            for line in lines[2:]:  # Skip header lines
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        service_name = parts[0]
                        status = parts[1]
                        services[service_name] = status
            
            # Count unhealthy services
            unhealthy_services = [name for name, status in services.items() if status != 'Up']
            
            status = "healthy"
            warnings = []
            
            if unhealthy_services:
                status = "warning"
                warnings.append(f"Unhealthy services: {', '.join(unhealthy_services)}")
            
            result = {
                "status": status,
                "total_services": len(services),
                "healthy_services": len(services) - len(unhealthy_services),
                "unhealthy_services": unhealthy_services,
                "services": services
            }
            
            if warnings:
                result["warnings"] = warnings
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Service dependency check failed: {str(e)}"
            }
    
    def parse_memory_usage(self, used: str, total: str) -> float:
        """Parse memory usage percentage"""
        try:
            # Remove units and convert to MB
            used_mb = self.parse_memory_value(used)
            total_mb = self.parse_memory_value(total)
            
            if total_mb > 0:
                return (used_mb / total_mb) * 100
            return 0
        except:
            return 0
    
    def parse_memory_value(self, value: str) -> float:
        """Parse memory value with unit"""
        value = value.strip()
        if value.endswith('G'):
            return float(value[:-1]) * 1024
        elif value.endswith('M'):
            return float(value[:-1])
        elif value.endswith('K'):
            return float(value[:-1]) / 1024
        else:
            return float(value)
    
    def parse_cpu_usage(self, top_output: str) -> float:
        """Parse CPU usage from top output"""
        try:
            lines = top_output.split('\n')
            for line in lines:
                if '%Cpu(s):' in line:
                    # Extract idle percentage
                    parts = line.split(',')
                    for part in parts:
                        if 'id' in part:
                            idle = float(part.strip().split()[0])
                            return 100 - idle
            return 0
        except:
            return 0
    
    def calculate_overall_status(self, results: Dict[str, Any]) -> str:
        """Calculate overall system status"""
        checks = results.get("checks", {})
        
        if not checks:
            return "unknown"
        
        statuses = [check.get("status", "unknown") for check in checks.values()]
        
        if "error" in statuses:
            return "error"
        elif "warning" in statuses:
            return "warning"
        elif all(status == "healthy" for status in statuses):
            return "healthy"
        else:
            return "unknown"
    
    def calculate_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate system metrics"""
        metrics = {
            "total_checks": len(results.get("checks", {})),
            "healthy_checks": 0,
            "warning_checks": 0,
            "error_checks": 0,
            "alert_count": len(results.get("alerts", [])),
            "response_times": {},
            "resource_usage": {}
        }
        
        # Count check statuses
        for check in results.get("checks", {}).values():
            status = check.get("status", "unknown")
            if status == "healthy":
                metrics["healthy_checks"] += 1
            elif status == "warning":
                metrics["warning_checks"] += 1
            elif status == "error":
                metrics["error_checks"] += 1
        
        # Extract response times
        for check_name, check in results.get("checks", {}).items():
            if "response_time" in check:
                metrics["response_times"][check_name] = check["response_time"]
        
        # Extract resource usage
        system_resources = results.get("checks", {}).get("system_resources", {})
        if system_resources:
            metrics["resource_usage"] = {
                "memory": system_resources.get("memory_usage", 0),
                "disk": system_resources.get("disk_usage", 0),
                "cpu": system_resources.get("cpu_usage", 0)
            }
        
        return metrics
    
    def generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate health check recommendations"""
        recommendations = []
        
        # Check for errors
        if results.get("overall_status") == "error":
            recommendations.append("Critical issues detected - immediate attention required")
        
        # Check for warnings
        if results.get("overall_status") == "warning":
            recommendations.append("System performance degraded - consider optimization")
        
        # Check specific issues
        checks = results.get("checks", {})
        
        # Backend issues
        backend_check = checks.get("backend_health", {})
        if backend_check.get("status") == "error":
            recommendations.append("Restart backend service: ./restart_backend.sh")
        elif backend_check.get("response_time", 0) > 3.0:
            recommendations.append("Backend response time high - consider optimization")
        
        # ChromaDB issues
        chromadb_check = checks.get("chromadb_health", {})
        if chromadb_check.get("status") == "error":
            recommendations.append("Restart ChromaDB: docker-compose restart chromadb")
        
        # Resource issues
        resources_check = checks.get("system_resources", {})
        if resources_check.get("memory_usage", 0) > 80:
            recommendations.append("High memory usage - consider cleanup or scaling")
        
        if resources_check.get("disk_usage", 0) > 85:
            recommendations.append("High disk usage - consider cleanup or expansion")
        
        # Log issues
        log_check = checks.get("log_analysis", {})
        if log_check.get("error_count", 0) > 5:
            recommendations.append("High error count in logs - investigate root causes")
        
        # Service issues
        services_check = checks.get("service_dependencies", {})
        if services_check.get("unhealthy_services"):
            recommendations.append("Restart unhealthy services: docker-compose restart")
        
        # General recommendations
        if not recommendations:
            recommendations.append("System operating normally - continue monitoring")
        
        return recommendations
    
    def save_health_check_results(self, results: Dict[str, Any]):
        """Save health check results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"health_check_results_{timestamp}.json"
        
        try:
            with open(self.project_root / filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"   ✅ Results saved to: {filename}")
        except Exception as e:
            print(f"   ❌ Error saving results: {e}")
    
    def log_health_summary(self, results: Dict[str, Any]):
        """Log health check summary"""
        self.logger.info(f"Health Check - Status: {results['overall_status']}")
        self.logger.info(f"Alerts: {len(results['alerts'])}")
        
        for alert in results['alerts']:
            self.logger.warning(f"Alert: {alert['service']} - {alert['message']}")
        
        for recommendation in results['recommendations']:
            self.logger.info(f"Recommendation: {recommendation}")

def main():
    """Main execution function"""
    health_checker = AutomatedHealthCheck()
    results = health_checker.run_health_check()
    
    # Exit with appropriate code
    if results['overall_status'] == 'error':
        exit(1)
    elif results['overall_status'] == 'warning':
        exit(2)
    else:
        exit(0)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
FAITHH Enhanced Service Monitoring
================================
Integrates knowledge base monitoring, response quality tracking, and system health.

This module provides:
- Unified monitoring dashboard
- Automated health checks
- Performance trend analysis
- Alert generation and notification
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Import our monitoring modules
try:
    from monitor_knowledge_base import KnowledgeBaseMonitor
    from monitor_response_quality import ResponseQualityMonitor
except ImportError:
    print("Warning: Monitoring modules not available")
    KnowledgeBaseMonitor = None
    ResponseQualityMonitor = None


class EnhancedServiceMonitor:
    """Enhanced monitoring for all FAITHH services"""
    
    def __init__(self):
        self.kb_monitor = KnowledgeBaseMonitor() if KnowledgeBaseMonitor else None
        self.quality_monitor = ResponseQualityMonitor() if ResponseQualityMonitor else None
        self.system_metrics = []
        self.start_time = datetime.now()
        
    def get_system_health(self) -> Dict:
        """Get comprehensive system health status"""
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "services": {},
            "overall_health": "unknown",
            "health_score": 0.0,
            "alerts": []
        }
        
        # Monitor knowledge base
        if self.kb_monitor:
            try:
                kb_health = self.kb_monitor.generate_health_report()
                health_report["services"]["knowledge_base"] = {
                    "status": "healthy" if kb_health["health_score"] >= 0.8 else "degraded",
                    "health_score": kb_health["health_score"],
                    "total_documents": kb_health["statistics"].get("total_documents", 0),
                    "collections": kb_health["statistics"].get("total_collections", 0),
                    "anomalies": kb_health["anomaly_count"]
                }
                health_report["alerts"].extend(kb_health["anomalies"])
            except Exception as e:
                health_report["services"]["knowledge_base"] = {
                    "status": "error",
                    "error": str(e)
                }
                health_report["alerts"].append({
                    "type": "monitoring_error",
                    "service": "knowledge_base",
                    "message": f"Knowledge base monitoring error: {e}",
                    "severity": "medium",
                    "timestamp": datetime.now().isoformat()
                })
        
        # Monitor response quality
        if self.quality_monitor:
            try:
                quality_health = self.quality_monitor.generate_quality_report()
                if "error" not in quality_health:
                    health_report["services"]["response_quality"] = {
                        "status": "healthy" if quality_health["health_score"] >= 0.8 else "degraded",
                        "health_score": quality_health["health_score"],
                        "total_responses": quality_health.get("total_responses_analyzed", 0),
                        "recent_responses": quality_health.get("recent_responses", 0),
                        "degradation_alerts": quality_health.get("alert_count", 0)
                    }
                    health_report["alerts"].extend(quality_health.get("degradation_alerts", []))
                else:
                    health_report["services"]["response_quality"] = {
                        "status": "no_data",
                        "message": quality_health["error"]
                    }
            except Exception as e:
                health_report["services"]["response_quality"] = {
                    "status": "error",
                    "error": str(e)
                }
                health_report["alerts"].append({
                    "type": "monitoring_error",
                    "service": "response_quality",
                    "message": f"Response quality monitoring error: {e}",
                    "severity": "medium",
                    "timestamp": datetime.now().isoformat()
                })
        
        # Calculate overall health score
        service_scores = []
        for service_name, service_data in health_report["services"].items():
            if "health_score" in service_data:
                service_scores.append(service_data["health_score"])
            elif service_data.get("status") == "healthy":
                service_scores.append(1.0)
            elif service_data.get("status") == "degraded":
                service_scores.append(0.6)
            elif service_data.get("status") == "error":
                service_scores.append(0.3)
            elif service_data.get("status") == "no_data":
                service_scores.append(0.8)
        
        if service_scores:
            health_report["health_score"] = sum(service_scores) / len(service_scores)
        
        # Determine overall health status
        if health_report["health_score"] >= 0.9:
            health_report["overall_health"] = "excellent"
        elif health_report["health_score"] >= 0.8:
            health_report["overall_health"] = "good"
        elif health_report["health_score"] >= 0.6:
            health_report["overall_health"] = "fair"
        else:
            health_report["overall_health"] = "poor"
        
        # Add system metrics
        health_report["system_metrics"] = self._get_system_metrics()
        
        return health_report
    
    def _get_system_metrics(self) -> Dict:
        """Get basic system metrics"""
        try:
            import psutil
            
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "load_average": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else None,
                "timestamp": datetime.now().isoformat()
            }
        except ImportError:
            return {
                "cpu_percent": "unavailable",
                "memory_percent": "unavailable", 
                "disk_usage": "unavailable",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_performance_trends(self, hours: int = 24) -> Dict:
        """Get performance trends over specified period"""
        trends = {
            "period_hours": hours,
            "timestamp": datetime.now().isoformat(),
            "knowledge_base": {},
            "response_quality": {},
            "system_performance": {}
        }
        
        # Knowledge base trends
        if self.kb_monitor:
            try:
                kb_trends = self.kb_monitor.monitor_growth_trends(hours)
                trends["knowledge_base"] = kb_trends
            except Exception as e:
                trends["knowledge_base"]["error"] = str(e)
        
        # Response quality trends
        if self.quality_monitor and len(self.quality_monitor.quality_history) > 0:
            try:
                cutoff_time = datetime.now() - timedelta(hours=hours)
                recent_metrics = [
                    m for m in self.quality_monitor.quality_history
                    if datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00")) > cutoff_time
                ]
                
                if recent_metrics:
                    quality_trends = {
                        "responses_analyzed": len(recent_metrics),
                        "avg_quality": sum(m.get("overall_quality", 0) for m in recent_metrics) / len(recent_metrics),
                        "avg_response_time": sum(m.get("response_time", 0) for m in recent_metrics if m.get("response_time")) / max(sum(1 for m in recent_metrics if m.get("response_time")), 1)
                    }
                    trends["response_quality"] = quality_trends
            except Exception as e:
                trends["response_quality"]["error"] = str(e)
        
        return trends
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive monitoring report"""
        current_health = self.get_system_health()
        performance_trends = self.get_performance_trends()
        
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "report_type": "comprehensive_monitoring",
            "current_health": current_health,
            "performance_trends": performance_trends,
            "recommendations": self._generate_comprehensive_recommendations(current_health, performance_trends),
            "next_checks": self._schedule_next_checks()
        }
        
        return report
    
    def _generate_comprehensive_recommendations(self, health: Dict, trends: Dict) -> List[str]:
        """Generate comprehensive recommendations"""
        recommendations = []
        
        # Health-based recommendations
        if health["overall_health"] in ["poor", "fair"]:
            recommendations.append("Immediate attention required - system health degraded")
        
        # Knowledge base recommendations
        kb_service = health["services"].get("knowledge_base", {})
        if kb_service.get("anomalies", 0) > 0:
            recommendations.append("Address knowledge base anomalies to improve RAG performance")
        
        if kb_service.get("total_documents", 0) < 1000:
            recommendations.append("Consider adding more content to improve knowledge base coverage")
        
        # Response quality recommendations
        quality_service = health["services"].get("response_quality", {})
        if quality_service.get("degradation_alerts", 0) > 0:
            recommendations.append("Investigate response quality degradation causes")
        
        # Performance trends recommendations
        kb_trends = trends.get("knowledge_base", {})
        if "growth_rate" in kb_trends and kb_trends["growth_rate"] == "stagnant":
            recommendations.append("Knowledge base growth stagnant - consider content addition strategies")
        
        return recommendations
    
    def _schedule_next_checks(self) -> Dict:
        """Schedule next monitoring checks"""
        return {
            "knowledge_base_check": (datetime.now() + timedelta(hours=6)).isoformat(),
            "quality_metrics_check": (datetime.now() + timedelta(hours=1)).isoformat(),
            "comprehensive_report": (datetime.now() + timedelta(hours=12)).isoformat(),
            "health_check": (datetime.now() + timedelta(minutes=30)).isoformat()
        }
    
    def save_comprehensive_report(self, filename: str = "comprehensive_monitoring_report.json"):
        """Save comprehensive monitoring report"""
        report = self.generate_comprehensive_report()
        
        try:
            reports_dir = Path("ml/output")
            reports_dir.mkdir(exist_ok=True, parents=True)
            
            report_file = reports_dir / filename
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Failed to save comprehensive report: {e}")
            return False


def main():
    """Run enhanced service monitoring"""
    print("🔍 FAITHH Enhanced Service Monitoring")
    print("=" * 60)
    
    monitor = EnhancedServiceMonitor()
    
    # Generate comprehensive report
    print("\n📊 Generating comprehensive monitoring report...")
    report = monitor.generate_comprehensive_report()
    
    # Display current health
    health = report["current_health"]
    print(f"\n🎯 Overall Health: {health['overall_health'].upper()}")
    print(f"📈 Health Score: {health['health_score']:.2f}")
    print(f"⏱️  Uptime: {health['uptime_seconds']:.0f} seconds")
    print(f"⚠️  Total Alerts: {len(health['alerts'])}")
    
    # Display service status
    print(f"\n📋 Service Status:")
    for service_name, service_data in health["services"].items():
        status = service_data.get("status", "unknown")
        score = service_data.get("health_score", 0)
        print(f"   - {service_name.replace('_', ' ').title()}: {status} (score: {score:.2f})")
        
        if "total_documents" in service_data:
            print(f"     Documents: {service_data['total_documents']}")
        if "total_responses" in service_data:
            print(f"     Responses: {service_data['total_responses']}")
        if "anomalies" in service_data:
            print(f"     Anomalies: {service_data['anomalies']}")
    
    # Display system metrics
    if "system_metrics" in health:
        metrics = health["system_metrics"]
        print(f"\n💻 System Metrics:")
        if "cpu_percent" in metrics and metrics["cpu_percent"] != "unavailable":
            print(f"   - CPU: {metrics['cpu_percent']:.1f}%")
        if "memory_percent" in metrics and metrics["memory_percent"] != "unavailable":
            print(f"   - Memory: {metrics['memory_percent']:.1f}%")
        if "disk_usage" in metrics and metrics["disk_usage"] != "unavailable":
            print(f"   - Disk: {metrics['disk_usage']:.1f}%")
    
    # Display alerts if any
    if health["alerts"]:
        print(f"\n⚠️  Active Alerts:")
        for alert in health["alerts"][:5]:  # Show first 5
            print(f"   - {alert['message']} ({alert['severity']})")
        if len(health["alerts"]) > 5:
            print(f"   ... and {len(health['alerts']) - 5} more")
    
    # Display performance trends
    trends = report["performance_trends"]
    print(f"\n📈 Performance Trends (Last 24h):")
    
    kb_trends = trends.get("knowledge_base", {})
    if "current_total" in kb_trends:
        print(f"   - Knowledge Base: {kb_trends['current_total']} documents")
        if "projection_30_days" in kb_trends:
            print(f"   - 30-day projection: {kb_trends['projection_30_days']:.0f} documents")
    
    quality_trends = trends.get("response_quality", {})
    if "responses_analyzed" in quality_trends:
        print(f"   - Response Quality: {quality_trends.get('avg_quality', 0):.2f} average score")
        print(f"   - Responses Analyzed: {quality_trends['responses_analyzed']}")
        if "avg_response_time" in quality_trends:
            print(f"   - Avg Response Time: {quality_trends['avg_response_time']:.2f}s")
    
    # Display recommendations
    if report["recommendations"]:
        print(f"\n💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"   - {rec}")
    
    # Display next checks
    next_checks = report["next_checks"]
    print(f"\n⏰ Next Scheduled Checks:")
    for check_name, check_time in next_checks.items():
        check_time_dt = datetime.fromisoformat(check_time.replace("Z", "+00:00"))
        time_until = check_time_dt - datetime.now()
        hours_until = time_until.total_seconds() / 3600
        print(f"   - {check_name.replace('_', ' ').title()}: {hours_until:.1f} hours")
    
    # Save report
    print(f"\n💾 Saving comprehensive report...")
    if monitor.save_comprehensive_report():
        print("✅ Report saved to ml/output/comprehensive_monitoring_report.json")
    else:
        print("❌ Failed to save report")
    
    print(f"\n🏁 Enhanced monitoring complete!")


if __name__ == "__main__":
    main()

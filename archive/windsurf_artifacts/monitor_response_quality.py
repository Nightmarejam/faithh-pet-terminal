#!/usr/bin/env python3
"""
FAITHH Response Quality Benchmarking System
==========================================
Tracks response quality metrics and detects degradation.

This module monitors:
- Response quality scores over time
- User satisfaction trends
- Context utilization rates
- Performance degradation alerts
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import re

class ResponseQualityMonitor:
    """Monitor and benchmark response quality"""
    
    def __init__(self):
        self.quality_history = []
        self.benchmarks = self._load_benchmarks()
        self.alerts = []
        
    def _load_benchmarks(self) -> Dict:
        """Load quality benchmarks and thresholds"""
        return {
            "response_quality": {
                "excellent": 0.9,
                "good": 0.8,
                "acceptable": 0.7,
                "poor": 0.6
            },
            "user_satisfaction": {
                "excellent": 0.9,
                "good": 0.8,
                "acceptable": 0.7,
                "poor": 0.6
            },
            "context_utilization": {
                "excellent": 0.9,
                "good": 0.8,
                "acceptable": 0.6,
                "poor": 0.4
            },
            "response_time": {
                "excellent": 2.0,  # seconds
                "good": 5.0,
                "acceptable": 10.0,
                "poor": 15.0
            },
            "token_efficiency": {
                "excellent": 0.8,  # tokens per second
                "good": 0.5,
                "acceptable": 0.3,
                "poor": 0.2
            }
        }
    
    def analyze_response_quality(self, response_text: str, query: str, 
                               context_sources: List[str] = None,
                               response_time: float = None,
                               token_count: int = None) -> Dict:
        """Analyze response quality across multiple dimensions"""
        
        quality_metrics = {
            "timestamp": datetime.now().isoformat(),
            "query_length": len(query),
            "response_length": len(response_text),
            "context_sources": context_sources or [],
            "response_time": response_time,
            "token_count": token_count
        }
        
        # Calculate quality scores
        quality_metrics["relevance_score"] = self._calculate_relevance_score(response_text, query)
        quality_metrics["completeness_score"] = self._calculate_completeness_score(response_text, query)
        quality_metrics["clarity_score"] = self._calculate_clarity_score(response_text)
        quality_metrics["accuracy_score"] = self._estimate_accuracy_score(response_text, context_sources)
        quality_metrics["overall_quality"] = self._calculate_overall_quality(quality_metrics)
        
        # Calculate additional metrics
        if response_time:
            quality_metrics["response_time_score"] = self._score_response_time(response_time)
        
        if token_count and response_time:
            quality_metrics["token_efficiency"] = token_count / response_time
        
        if context_sources:
            quality_metrics["context_utilization"] = self._calculate_context_utilization(response_text, context_sources)
        
        return quality_metrics
    
    def _calculate_relevance_score(self, response: str, query: str) -> float:
        """Calculate relevance score based on query-response overlap"""
        # Simple keyword overlap analysis
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        response_words = set(re.findall(r'\b\w+\b', response.lower()))
        
        if not query_words:
            return 0.5  # Default score for empty queries
        
        overlap = query_words.intersection(response_words)
        relevance = len(overlap) / len(query_words)
        
        # Boost score for longer, more detailed responses
        length_bonus = min(len(response) / 1000, 0.3)
        
        return min(1.0, relevance + length_bonus)
    
    def _calculate_completeness_score(self, response: str, query: str) -> float:
        """Estimate completeness based on response coverage"""
        # Check for comprehensive answer indicators
        completeness_indicators = [
            "first", "second", "third", "finally", "in conclusion",
            "additionally", "furthermore", "moreover", "however",
            "therefore", "because", "since", "due to"
        ]
        
        indicator_count = sum(1 for indicator in completeness_indicators 
                            if indicator.lower() in response.lower())
        
        # Score based on indicators and length
        indicator_score = min(indicator_count / 5, 0.5)
        length_score = min(len(response) / 500, 0.5)
        
        return indicator_score + length_score
    
    def _calculate_clarity_score(self, response: str) -> float:
        """Calculate clarity based on readability metrics"""
        # Simple readability metrics
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.3
        
        # Average sentence length
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Ideal sentence length is 15-20 words
        length_score = 1.0 - abs(avg_sentence_length - 17.5) / 17.5
        length_score = max(0.3, length_score)
        
        # Check for structure indicators
        structure_indicators = ["•", "-", "1.", "2.", "3.", "first", "second"]
        structure_score = min(sum(1 for indicator in structure_indicators 
                               if indicator in response.lower()) / 3, 0.3)
        
        return length_score + structure_score
    
    def _estimate_accuracy_score(self, response: str, context_sources: List[str]) -> float:
        """Estimate accuracy based on context source usage"""
        if not context_sources:
            return 0.7  # Default score when no context sources available
        
        # Check if response cites sources or references context
        citation_indicators = ["according to", "based on", "as mentioned", "from the", "in the"]
        citation_score = sum(1 for indicator in citation_indicators 
                           if indicator.lower() in response.lower()) / len(citation_indicators)
        
        # Boost score for using multiple sources
        source_diversity_score = min(len(set(context_sources)) / 3, 0.3)
        
        return min(1.0, 0.5 + citation_score + source_diversity_score)
    
    def _calculate_overall_quality(self, metrics: Dict) -> float:
        """Calculate overall quality score"""
        weights = {
            "relevance_score": 0.3,
            "completeness_score": 0.25,
            "clarity_score": 0.2,
            "accuracy_score": 0.25
        }
        
        overall = sum(metrics.get(key, 0) * weight for key, weight in weights.items())
        return min(1.0, overall)
    
    def _score_response_time(self, response_time: float) -> float:
        """Score response time against benchmarks"""
        benchmarks = self.benchmarks["response_time"]
        
        if response_time <= benchmarks["excellent"]:
            return 1.0
        elif response_time <= benchmarks["good"]:
            return 0.8
        elif response_time <= benchmarks["acceptable"]:
            return 0.6
        elif response_time <= benchmarks["poor"]:
            return 0.4
        else:
            return 0.2
    
    def _calculate_context_utilization(self, response: str, context_sources: List[str]) -> float:
        """Calculate how well response utilizes provided context"""
        if not context_sources:
            return 0.0
        
        # Check for explicit context references
        context_references = ["context", "according to", "based on", "mentioned", "source"]
        reference_count = sum(1 for ref in context_references if ref.lower() in response.lower())
        
        # Score based on reference frequency and response length
        reference_score = min(reference_count / len(context_sources), 0.7)
        length_score = min(len(response) / 300, 0.3)  # Longer responses likely use more context
        
        return reference_score + length_score
    
    def record_quality_metrics(self, metrics: Dict):
        """Record quality metrics for tracking"""
        self.quality_history.append(metrics)
        
        # Keep only last 1000 entries
        if len(self.quality_history) > 1000:
            self.quality_history = self.quality_history[-1000:]
    
    def detect_quality_degradation(self, hours: int = 24) -> List[Dict]:
        """Detect quality degradation over specified period"""
        if len(self.quality_history) < 10:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.quality_history
            if datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00")) > cutoff_time
        ]
        
        if len(recent_metrics) < 5:
            return []
        
        degradation_alerts = []
        
        # Check overall quality trend
        recent_quality = [m.get("overall_quality", 0) for m in recent_metrics]
        avg_recent = sum(recent_quality) / len(recent_quality)
        
        # Compare with historical baseline
        older_metrics = [
            m for m in self.quality_history
            if datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00")) <= cutoff_time
        ]
        
        if older_metrics:
            historical_quality = [m.get("overall_quality", 0) for m in older_metrics[-20:]]
            avg_historical = sum(historical_quality) / len(historical_quality)
            
            # Detect degradation
            if avg_recent < avg_historical - 0.1:
                degradation_alerts.append({
                    "type": "quality_degradation",
                    "severity": "high" if avg_recent < avg_historical - 0.2 else "medium",
                    "current_avg": avg_recent,
                    "historical_avg": avg_historical,
                    "degradation": avg_historical - avg_recent,
                    "message": f"Response quality degraded by {avg_historical - avg_recent:.2f} points",
                    "timestamp": datetime.now().isoformat()
                })
        
        # Check for specific metric issues
        for metric_name in ["relevance_score", "completeness_score", "clarity_score"]:
            recent_values = [m.get(metric_name, 0) for m in recent_metrics]
            avg_recent = sum(recent_values) / len(recent_values)
            
            benchmark = self.benchmarks.get("response_quality", {})
            if avg_recent < benchmark.get("acceptable", 0.7):
                degradation_alerts.append({
                    "type": "metric_degradation",
                    "metric": metric_name,
                    "severity": "high" if avg_recent < benchmark.get("poor", 0.6) else "medium",
                    "current_value": avg_recent,
                    "benchmark": benchmark.get("acceptable", 0.7),
                    "message": f"{metric_name} below acceptable threshold: {avg_recent:.2f}",
                    "timestamp": datetime.now().isoformat()
                })
        
        return degradation_alerts
    
    def generate_quality_report(self) -> Dict:
        """Generate comprehensive quality report"""
        if not self.quality_history:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": "No quality metrics available"
            }
        
        # Calculate recent averages
        recent_metrics = self.quality_history[-50:]  # Last 50 responses
        averages = {}
        
        for metric in ["overall_quality", "relevance_score", "completeness_score", 
                      "clarity_score", "accuracy_score", "response_time", "context_utilization"]:
            values = [m.get(metric, 0) for m in recent_metrics if metric in m and m[metric] is not None]
            if values:
                averages[metric] = {
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values)
                }
        
        # Detect degradation
        degradation_alerts = self.detect_quality_degradation()
        
        # Calculate overall health score
        overall_avg = averages.get("overall_quality", {}).get("average", 0)
        health_score = overall_avg
        
        if degradation_alerts:
            for alert in degradation_alerts:
                if alert["severity"] == "high":
                    health_score -= 0.2
                elif alert["severity"] == "medium":
                    health_score -= 0.1
        
        health_score = max(0.0, health_score)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "health_score": health_score,
            "health_status": "excellent" if health_score >= 0.9 else "good" if health_score >= 0.8 else "fair" if health_score >= 0.7 else "poor",
            "total_responses_analyzed": len(self.quality_history),
            "recent_responses": len(recent_metrics),
            "metric_averages": averages,
            "degradation_alerts": degradation_alerts,
            "alert_count": len(degradation_alerts),
            "recommendations": self._generate_quality_recommendations(degradation_alerts, averages)
        }
        
        return report
    
    def _generate_quality_recommendations(self, alerts: List[Dict], averages: Dict) -> List[str]:
        """Generate recommendations based on quality analysis"""
        recommendations = []
        
        if not alerts:
            recommendations.append("Response quality appears stable - continue monitoring")
            return recommendations
        
        # Check for quality degradation
        quality_alerts = [a for a in alerts if a["type"] == "quality_degradation"]
        if quality_alerts:
            recommendations.append("Investigate causes of response quality degradation")
            recommendations.append("Review recent system changes or model parameter updates")
        
        # Check for specific metric issues
        for alert in alerts:
            if alert["type"] == "metric_degradation":
                metric = alert["metric"]
                if "relevance" in metric:
                    recommendations.append("Improve query understanding and context matching")
                elif "completeness" in metric:
                    recommendations.append("Encourage more comprehensive responses")
                elif "clarity" in metric:
                    recommendations.append("Review response formatting and structure")
        
        # Check response time issues
        if "response_time" in averages:
            avg_time = averages["response_time"]["average"]
            if avg_time > 10:
                recommendations.append("Optimize response time through caching or model selection")
        
        # Check context utilization
        if "context_utilization" in averages:
            avg_utilization = averages["context_utilization"]["average"]
            if avg_utilization < 0.6:
                recommendations.append("Improve context integration in responses")
        
        return recommendations
    
    def save_metrics(self, filename: str = "response_quality_metrics.json"):
        """Save quality metrics to file"""
        report = self.generate_quality_report()
        
        try:
            # Load existing metrics if file exists
            metrics_file = Path("ml/output") / filename
            metrics_file.parent.mkdir(exist_ok=True, parents=True)
            
            existing_data = []
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    existing_data = json.load(f)
            
            # Add current report
            existing_data.append(report)
            
            # Keep only last 30 days of data
            cutoff_date = datetime.now() - timedelta(days=30)
            existing_data = [
                entry for entry in existing_data
                if datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00")) > cutoff_date
            ]
            
            # Save updated metrics
            with open(metrics_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Failed to save quality metrics: {e}")
            return False


def main():
    """Run response quality monitoring"""
    print("📊 FAITHH Response Quality Monitoring")
    print("=" * 50)
    
    monitor = ResponseQualityMonitor()
    
    # Generate quality report
    print("\n📈 Generating quality report...")
    report = monitor.generate_quality_report()
    
    if "error" in report:
        print(f"❌ Error: {report['error']}")
        return
    
    # Display key metrics
    print(f"\n🎯 Health Score: {report['health_score']:.2f} ({report['health_status']})")
    print(f"📝 Total Responses Analyzed: {report['total_responses_analyzed']}")
    print(f"📊 Recent Responses: {report['recent_responses']}")
    print(f"⚠️  Alerts: {report['alert_count']}")
    
    # Display metric averages
    if "metric_averages" in report:
        print(f"\n📈 Recent Performance:")
        for metric, stats in report["metric_averages"].items():
            if "average" in stats:
                print(f"   - {metric}: {stats['average']:.2f} (min: {stats.get('min', 0):.2f}, max: {stats.get('max', 0):.2f})")
    
    # Display alerts if any
    if report["degradation_alerts"]:
        print(f"\n⚠️  Quality Alerts:")
        for alert in report["degradation_alerts"][:5]:  # Show first 5
            print(f"   - {alert['message']} ({alert['severity']})")
        if len(report["degradation_alerts"]) > 5:
            print(f"   ... and {len(report['degradation_alerts']) - 5} more")
    
    # Display recommendations
    if report["recommendations"]:
        print(f"\n💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"   - {rec}")
    
    # Save metrics
    print(f"\n💾 Saving metrics...")
    if monitor.save_metrics():
        print("✅ Metrics saved to ml/output/response_quality_metrics.json")
    else:
        print("❌ Failed to save metrics")
    
    print(f"\n🏁 Quality monitoring complete!")


if __name__ == "__main__":
    main()

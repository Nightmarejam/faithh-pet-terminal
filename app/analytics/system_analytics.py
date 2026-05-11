"""
System Performance Analytics - Day 6 Implementation
Following Sonnet's Implementation Excellence Framework
Advanced analytics for system performance monitoring and optimization
"""

import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

class SystemAnalytics:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.performance_history = []
        self.baseline_metrics = {}
        
    def analyze_api_performance(self, api_logs: List[Dict]) -> Dict:
        """
        Analyze API performance trends and optimization opportunities
        Following Sonnet's Performance Excellence: Fast response times (<100ms)
        """
        try:
            if not api_logs:
                return {
                    "performance_metrics": {},
                    "trends": {},
                    "optimization_recommendations": ["No API performance data available"]
                }
            
            # Extract key metrics
            response_times = []
            success_rates = []
            error_rates = []
            endpoint_stats = {}
            
            for log_entry in api_logs:
                endpoint = log_entry.get('endpoint', 'unknown')
                response_time = log_entry.get('response_time', 0)
                status = log_entry.get('status', 'unknown')
                
                # Track response times
                response_times.append(response_time)
                
                # Track success/error rates
                if status == 'success':
                    success_rates.append(1)
                    error_rates.append(0)
                else:
                    success_rates.append(0)
                    error_rates.append(1)
                
                # Track endpoint statistics
                if endpoint not in endpoint_stats:
                    endpoint_stats[endpoint] = {
                        'response_times': [],
                        'success_count': 0,
                        'error_count': 0
                    }
                
                endpoint_stats[endpoint]['response_times'].append(response_time)
                if status == 'success':
                    endpoint_stats[endpoint]['success_count'] += 1
                else:
                    endpoint_stats[endpoint]['error_count'] += 1
            
            # Calculate overall performance metrics
            overall_metrics = {
                "average_response_time": np.mean(response_times),
                "median_response_time": np.median(response_times),
                "p95_response_time": np.percentile(response_times, 95),
                "p99_response_time": np.percentile(response_times, 99),
                "success_rate": np.mean(success_rates),
                "error_rate": np.mean(error_rates),
                "total_requests": len(response_times)
            }
            
            # Calculate endpoint-specific metrics
            endpoint_metrics = {}
            for endpoint, stats in endpoint_stats.items():
                if stats['response_times']:
                    endpoint_metrics[endpoint] = {
                        "average_response_time": np.mean(stats['response_times']),
                        "success_rate": stats['success_count'] / (stats['success_count'] + stats['error_count']),
                        "request_count": len(stats['response_times'])
                    }
            
            # Analyze trends
            trends = self._analyze_performance_trends(api_logs)
            
            # Generate optimization recommendations
            recommendations = self._generate_performance_recommendations(overall_metrics, endpoint_metrics)
            
            return {
                "performance_metrics": {
                    "overall": overall_metrics,
                    "endpoints": endpoint_metrics
                },
                "trends": trends,
                "optimization_recommendations": recommendations,
                "analysis_timestamp": datetime.now().isoformat(),
                "requests_analyzed": len(response_times)
            }
            
        except Exception as e:
            self.logger.error(f"API performance analysis failed: {e}")
            return {
                "performance_metrics": {},
                "trends": {},
                "optimization_recommendations": ["Analysis failed - check data quality"]
            }
    
    def _analyze_performance_trends(self, api_logs: List[Dict]) -> Dict:
        """Analyze performance trends over time"""
        try:
            # Group logs by time windows (hourly)
            time_windows = {}
            
            for log_entry in api_logs:
                timestamp = log_entry.get('timestamp')
                if timestamp:
                    dt = datetime.fromisoformat(timestamp)
                    hour_key = dt.replace(minute=0, second=0, microsecond=0)
                    
                    if hour_key not in time_windows:
                        time_windows[hour_key] = []
                    time_windows[hour_key].append(log_entry)
            
            # Calculate metrics for each time window
            window_metrics = []
            for hour, logs in sorted(time_windows.items()):
                response_times = [log.get('response_time', 0) for log in logs]
                success_count = sum(1 for log in logs if log.get('status') == 'success')
                
                if response_times:
                    window_metrics.append({
                        "timestamp": hour.isoformat(),
                        "average_response_time": np.mean(response_times),
                        "success_rate": success_count / len(logs),
                        "request_count": len(logs)
                    })
            
            # Calculate trends
            trends = {}
            
            if len(window_metrics) >= 2:
                # Response time trend
                response_times = [w['average_response_time'] for w in window_metrics]
                response_trend = self._calculate_trend(response_times)
                trends['response_time'] = response_trend
                
                # Success rate trend
                success_rates = [w['success_rate'] for w in window_metrics]
                success_trend = self._calculate_trend(success_rates)
                trends['success_rate'] = success_trend
                
                # Request volume trend
                request_counts = [w['request_count'] for w in window_metrics]
                volume_trend = self._calculate_trend(request_counts)
                trends['request_volume'] = volume_trend
            
            return {
                "time_series": window_metrics,
                "trends": trends
            }
            
        except Exception as e:
            self.logger.error(f"Performance trend analysis failed: {e}")
            return {"trends": {}}
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from a series of values"""
        if len(values) < 3:
            return "insufficient_data"
        
        # Simple linear regression for trend
        x = np.arange(len(values))
        y = np.array(values)
        
        coeffs = np.polyfit(x, y, 1)
        slope = coeffs[0]
        
        if abs(slope) < 0.01:
            return "stable"
        elif slope > 0:
            return "increasing"
        else:
            return "decreasing"
    
    def _generate_performance_recommendations(self, overall_metrics: Dict, endpoint_metrics: Dict) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Response time recommendations
        avg_response_time = overall_metrics.get('average_response_time', 0)
        p95_response_time = overall_metrics.get('p95_response_time', 0)
        
        if avg_response_time > 100:  # Sonnet's 100ms target
            recommendations.append("Average response time exceeds 100ms target - consider optimization")
        
        if p95_response_time > 200:
            recommendations.append("P95 response time is high - investigate outliers")
        
        # Success rate recommendations
        success_rate = overall_metrics.get('success_rate', 0)
        if success_rate < 0.95:  # Sonnet's 95% success rate target
            recommendations.append("Success rate below 95% target - investigate errors")
        
        # Endpoint-specific recommendations
        slow_endpoints = []
        unreliable_endpoints = []
        
        for endpoint, metrics in endpoint_metrics.items():
            if metrics.get('average_response_time', 0) > 150:
                slow_endpoints.append(endpoint)
            if metrics.get('success_rate', 0) < 0.9:
                unreliable_endpoints.append(endpoint)
        
        if slow_endpoints:
            recommendations.append(f"Optimize slow endpoints: {', '.join(slow_endpoints[:3])}")
        
        if unreliable_endpoints:
            recommendations.append(f"Improve reliability for endpoints: {', '.join(unreliable_endpoints[:3])}")
        
        return recommendations
    
    def analyze_resource_utilization(self, resource_logs: List[Dict]) -> Dict:
        """
        Analyze system resource utilization patterns
        Following Sonnet's Implementation Excellence: Optimal resource utilization
        """
        try:
            if not resource_logs:
                return {
                    "utilization_metrics": {},
                    "patterns": {},
                    "optimization_suggestions": ["No resource data available"]
                }
            
            # Extract resource metrics
            cpu_usage = []
            memory_usage = []
            disk_usage = []
            network_usage = []
            
            for log_entry in resource_logs:
                cpu_usage.append(log_entry.get('cpu_percent', 0))
                memory_usage.append(log_entry.get('memory_percent', 0))
                disk_usage.append(log_entry.get('disk_percent', 0))
                network_usage.append(log_entry.get('network_bytes', 0))
            
            # Calculate utilization metrics
            utilization_metrics = {
                "cpu": {
                    "average": np.mean(cpu_usage),
                    "max": np.max(cpu_usage),
                    "p95": np.percentile(cpu_usage, 95)
                },
                "memory": {
                    "average": np.mean(memory_usage),
                    "max": np.max(memory_usage),
                    "p95": np.percentile(memory_usage, 95)
                },
                "disk": {
                    "average": np.mean(disk_usage),
                    "max": np.max(disk_usage),
                    "current": disk_usage[-1] if disk_usage else 0
                },
                "network": {
                    "average_bytes": np.mean(network_usage) if network_usage else 0,
                    "total_bytes": sum(network_usage)
                }
            }
            
            # Identify utilization patterns
            patterns = self._identify_utilization_patterns(cpu_usage, memory_usage, disk_usage)
            
            # Generate optimization suggestions
            suggestions = self._generate_resource_suggestions(utilization_metrics, patterns)
            
            return {
                "utilization_metrics": utilization_metrics,
                "patterns": patterns,
                "optimization_suggestions": suggestions,
                "analysis_timestamp": datetime.now().isoformat(),
                "data_points": len(resource_logs)
            }
            
        except Exception as e:
            self.logger.error(f"Resource utilization analysis failed: {e}")
            return {
                "utilization_metrics": {},
                "patterns": {},
                "optimization_suggestions": ["Analysis failed"]
            }
    
    def _identify_utilization_patterns(self, cpu: List[float], memory: List[float], disk: List[float]) -> Dict:
        """Identify patterns in resource utilization"""
        patterns = {}
        
        # CPU patterns
        if cpu:
            cpu_avg = np.mean(cpu)
            if cpu_avg > 80:
                patterns['cpu'] = "high_utilization"
            elif cpu_avg > 60:
                patterns['cpu'] = "moderate_utilization"
            else:
                patterns['cpu'] = "low_utilization"
            
            # Check for spikes
            cpu_spikes = sum(1 for val in cpu if val > 90)
            if cpu_spikes > len(cpu) * 0.1:  # More than 10% spikes
                patterns['cpu_spikes'] = "frequent_spikes"
        
        # Memory patterns
        if memory:
            memory_avg = np.mean(memory)
            if memory_avg > 85:
                patterns['memory'] = "high_utilization"
            elif memory_avg > 70:
                patterns['memory'] = "moderate_utilization"
            else:
                patterns['memory'] = "low_utilization"
        
        # Disk patterns
        if disk:
            disk_current = disk[-1] if disk else 0
            if disk_current > 90:
                patterns['disk'] = "critical_space"
            elif disk_current > 80:
                patterns['disk'] = "low_space"
            else:
                patterns['disk'] = "adequate_space"
        
        return patterns
    
    def _generate_resource_suggestions(self, metrics: Dict, patterns: Dict) -> List[str]:
        """Generate resource optimization suggestions"""
        suggestions = []
        
        # CPU suggestions
        cpu_avg = metrics.get('cpu', {}).get('average', 0)
        if cpu_avg > 80:
            suggestions.append("High CPU utilization - consider scaling or optimization")
        elif patterns.get('cpu_spikes') == "frequent_spikes":
            suggestions.append("Frequent CPU spikes - investigate resource bottlenecks")
        
        # Memory suggestions
        memory_avg = metrics.get('memory', {}).get('average', 0)
        if memory_avg > 85:
            suggestions.append("High memory utilization - consider memory optimization")
        
        # Disk suggestions
        disk_current = metrics.get('disk', {}).get('current', 0)
        if disk_current > 85:
            suggestions.append("Low disk space - consider cleanup or expansion")
        
        # General suggestions
        if cpu_avg < 30 and memory_avg < 50:
            suggestions.append("Low resource utilization - potential for consolidation")
        
        return suggestions
    
    def predict_system_bottlenecks(self, performance_data: List[Dict], resource_data: List[Dict]) -> Dict:
        """
        Predict potential system bottlenecks
        Following Sonnet's Strategic Excellence: Strong foundations and growth opportunities
        """
        try:
            if not performance_data or not resource_data:
                return {
                    "predictions": [],
                    "risk_factors": [],
                    "recommendations": ["Insufficient data for bottleneck prediction"]
                }
            
            predictions = []
            risk_factors = []
            
            # Analyze performance trends for bottlenecks
            recent_performance = performance_data[-100:] if len(performance_data) > 100 else performance_data
            response_times = [p.get('response_time', 0) for p in recent_performance]
            
            if response_times:
                # Predict response time degradation
                response_trend = self._calculate_trend(response_times)
                if response_trend == "increasing":
                    predictions.append({
                        "type": "performance_degradation",
                        "probability": 0.7,
                        "timeline": "2-4 weeks",
                        "impact": "medium"
                    })
                    risk_factors.append("Increasing response time trend")
                
                # Check for response time volatility
                response_volatility = np.std(response_times)
                if response_volatility > 50:
                    predictions.append({
                        "type": "performance_volatility",
                        "probability": 0.6,
                        "timeline": "1-2 weeks",
                        "impact": "medium"
                    })
                    risk_factors.append("High response time volatility")
            
            # Analyze resource trends for bottlenecks
            recent_resources = resource_data[-100:] if len(resource_data) > 100 else resource_data
            cpu_usage = [r.get('cpu_percent', 0) for r in recent_resources]
            memory_usage = [r.get('memory_percent', 0) for r in recent_resources]
            
            if cpu_usage:
                cpu_trend = self._calculate_trend(cpu_usage)
                cpu_avg = np.mean(cpu_usage)
                
                if cpu_trend == "increasing" and cpu_avg > 70:
                    predictions.append({
                        "type": "cpu_bottleneck",
                        "probability": 0.8,
                        "timeline": "1-3 weeks",
                        "impact": "high"
                    })
                    risk_factors.append("Increasing CPU utilization trend")
            
            if memory_usage:
                memory_trend = self._calculate_trend(memory_usage)
                memory_avg = np.mean(memory_usage)
                
                if memory_trend == "increasing" and memory_avg > 75:
                    predictions.append({
                        "type": "memory_bottleneck",
                        "probability": 0.7,
                        "timeline": "2-4 weeks",
                        "impact": "high"
                    })
                    risk_factors.append("Increasing memory utilization trend")
            
            # Generate recommendations based on predictions
            recommendations = []
            for prediction in predictions:
                if prediction['type'] == 'cpu_bottleneck':
                    recommendations.append("Monitor CPU usage and plan for scaling")
                elif prediction['type'] == 'memory_bottleneck':
                    recommendations.append("Optimize memory usage and consider expansion")
                elif prediction['type'] == 'performance_degradation':
                    recommendations.append("Investigate performance degradation causes")
                elif prediction['type'] == 'performance_volatility':
                    recommendations.append("Address performance inconsistencies")
            
            return {
                "predictions": predictions,
                "risk_factors": risk_factors,
                "recommendations": recommendations,
                "analysis_timestamp": datetime.now().isoformat(),
                "data_points": {
                    "performance": len(performance_data),
                    "resource": len(resource_data)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Bottleneck prediction failed: {e}")
            return {
                "predictions": [],
                "risk_factors": [],
                "recommendations": ["Prediction failed"]
            }
    
    def generate_system_health_report(self, performance_data: List[Dict], resource_data: List[Dict]) -> Dict:
        """
        Generate comprehensive system health report
        Following Sonnet's Implementation Excellence: Comprehensive documentation
        """
        try:
            # Generate all analytics components
            api_performance = self.analyze_api_performance(performance_data)
            resource_utilization = self.analyze_resource_utilization(resource_data)
            bottleneck_predictions = self.predict_system_bottlenecks(performance_data, resource_data)
            
            # Calculate overall system health score
            health_components = []
            
            # API performance health
            api_success_rate = api_performance.get('performance_metrics', {}).get('overall', {}).get('success_rate', 0)
            api_response_time = api_performance.get('performance_metrics', {}).get('overall', {}).get('average_response_time', 100)
            
            api_health = (api_success_rate * 0.7) + ((100 - min(api_response_time, 100)) / 100 * 0.3)
            health_components.append(api_health)
            
            # Resource utilization health
            cpu_avg = resource_utilization.get('utilization_metrics', {}).get('cpu', {}).get('average', 50)
            memory_avg = resource_utilization.get('utilization_metrics', {}).get('memory', {}).get('average', 50)
            
            # Optimal resource utilization is around 50-70%
            cpu_health = 1.0 - abs(cpu_avg - 60) / 60
            memory_health = 1.0 - abs(memory_avg - 60) / 60
            resource_health = (cpu_health + memory_health) / 2
            health_components.append(resource_health)
            
            # Bottleneck risk health (inverse of risk)
            high_risk_predictions = [p for p in bottleneck_predictions.get('predictions', []) if p.get('probability', 0) > 0.7]
            bottleneck_health = 1.0 - (len(high_risk_predictions) * 0.2)  # Each high-risk prediction reduces health
            bottleneck_health = max(0.0, bottleneck_health)
            health_components.append(bottleneck_health)
            
            # Calculate overall health
            overall_health = np.mean(health_components)
            
            # Determine health status
            if overall_health > 0.8:
                health_status = "excellent"
            elif overall_health > 0.6:
                health_status = "good"
            elif overall_health > 0.4:
                health_status = "fair"
            else:
                health_status = "poor"
            
            # Combine all recommendations
            all_recommendations = []
            all_recommendations.extend(api_performance.get('optimization_recommendations', []))
            all_recommendations.extend(resource_utilization.get('optimization_suggestions', []))
            all_recommendations.extend(bottleneck_predictions.get('recommendations', []))
            
            # Remove duplicates
            unique_recommendations = list(set(all_recommendations))
            
            # Generate key insights
            key_insights = [
                f"Overall system health: {health_status} ({overall_health:.1%})",
                f"API success rate: {api_success_rate:.1%}",
                f"Average response time: {api_response_time:.1f}ms",
                f"CPU utilization: {cpu_avg:.1f}%",
                f"Memory utilization: {memory_avg:.1f}%",
                f"High-risk predictions: {len(high_risk_predictions)}"
            ]
            
            return {
                "overall_health_score": overall_health,
                "health_status": health_status,
                "api_performance": api_performance,
                "resource_utilization": resource_utilization,
                "bottleneck_predictions": bottleneck_predictions,
                "key_insights": key_insights,
                "recommendations": unique_recommendations,
                "generated_at": datetime.now().isoformat(),
                "data_summary": {
                    "performance_data_points": len(performance_data),
                    "resource_data_points": len(resource_data)
                }
            }
            
        except Exception as e:
            self.logger.error(f"System health report generation failed: {e}")
            return {
                "overall_health_score": 0.0,
                "health_status": "error",
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
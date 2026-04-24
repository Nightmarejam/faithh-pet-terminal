"""
FAITHH Advanced Analytics System

Provides advanced analytics capabilities including:
- Predictive metrics and forecasting
- Anomaly detection for system health
- Performance trend analysis
- AI-powered insights generation
"""

import json
import time
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict, deque
import threading
import statistics

@dataclass
class PerformanceMetric:
    """Individual performance metric with timestamp"""
    timestamp: datetime
    metric_type: str
    value: float
    context: Dict[str, Any]

@dataclass
class AnomalyAlert:
    """Anomaly detection alert"""
    timestamp: datetime
    metric_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    predicted_value: float
    actual_value: float
    confidence: float

class PredictiveAnalytics:
    """Predictive analytics for performance forecasting"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.prediction_models: Dict[str, Dict] = {}
        self.lock = threading.Lock()
    
    def add_metric(self, metric_type: str, value: float, context: Dict[str, Any] = None):
        """Add a new metric value"""
        with self.lock:
            timestamp = datetime.now()
            metric = PerformanceMetric(timestamp, metric_type, value, context or {})
            self.metric_history[metric_type].append(metric)
            
            # Update prediction model if enough data
            if len(self.metric_history[metric_type]) >= 20:
                self._update_prediction_model(metric_type)
    
    def _update_prediction_model(self, metric_type: str):
        """Update prediction model for a metric type"""
        metrics = list(self.metric_history[metric_type])
        if len(metrics) < 10:
            return
        
        # Extract values and timestamps
        values = [m.value for m in metrics]
        timestamps = [(m.timestamp - metrics[0].timestamp).total_seconds() for m in metrics]
        
        # Simple linear regression for trend prediction
        if len(values) >= 3:
            # Calculate trend
            x_mean = statistics.mean(timestamps)
            y_mean = statistics.mean(values)
            
            numerator = sum((timestamps[i] - x_mean) * (values[i] - y_mean) for i in range(len(values)))
            denominator = sum((timestamps[i] - x_mean) ** 2 for i in range(len(values)))
            
            if denominator != 0:
                slope = numerator / denominator
                intercept = y_mean - slope * x_mean
                
                # Calculate R-squared for model quality
                y_pred = [slope * t + intercept for t in timestamps]
                ss_res = sum((values[i] - y_pred[i]) ** 2 for i in range(len(values)))
                ss_tot = sum((values[i] - y_mean) ** 2 for i in range(len(values)))
                r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                
                self.prediction_models[metric_type] = {
                    'slope': slope,
                    'intercept': intercept,
                    'r_squared': r_squared,
                    'last_timestamp': timestamps[-1],
                    'last_value': values[-1],
                    'updated': datetime.now()
                }
    
    def predict_metric(self, metric_type: str, horizon_seconds: int = 3600) -> Optional[Dict]:
        """Predict metric value for future time horizon"""
        with self.lock:
            if metric_type not in self.prediction_models:
                return None
            
            model = self.prediction_models[metric_type]
            if model['r_squared'] < 0.3:  # Poor model quality
                return None
            
            # Predict future value
            future_time = model['last_timestamp'] + horizon_seconds
            predicted_value = model['slope'] * future_time + model['intercept']
            
            # Calculate confidence based on model quality and data recency
            age_hours = (datetime.now() - model['updated']).total_seconds() / 3600
            confidence = max(0.1, model['r_squared'] * (1 - age_hours / 24))  # Decay over 24 hours
            
            return {
                'metric_type': metric_type,
                'predicted_value': predicted_value,
                'horizon_seconds': horizon_seconds,
                'confidence': confidence,
                'model_quality': model['r_squared'],
                'trend': 'increasing' if model['slope'] > 0 else 'decreasing' if model['slope'] < 0 else 'stable'
            }
    
    def get_trend_analysis(self, metric_type: str) -> Optional[Dict]:
        """Get trend analysis for a metric"""
        with self.lock:
            if metric_type not in self.metric_history or len(self.metric_history[metric_type]) < 10:
                return None
            
            metrics = list(self.metric_history[metric_type])
            values = [m.value for m in metrics]
            
            # Calculate statistics
            recent_values = values[-10:]  # Last 10 values
            older_values = values[-20:-10] if len(values) >= 20 else values[:-10]
            
            if not older_values:
                return None
            
            recent_avg = statistics.mean(recent_values)
            older_avg = statistics.mean(older_values)
            
            # Calculate trend
            trend_percent = ((recent_avg - older_avg) / older_avg) * 100 if older_avg != 0 else 0
            
            # Calculate volatility
            recent_volatility = statistics.stdev(recent_values) if len(recent_values) > 1 else 0
            
            return {
                'metric_type': metric_type,
                'trend_percent': trend_percent,
                'recent_average': recent_avg,
                'older_average': older_avg,
                'volatility': recent_volatility,
                'direction': 'improving' if trend_percent > 5 else 'declining' if trend_percent < -5 else 'stable',
                'data_points': len(values)
            }

class AnomalyDetector:
    """Anomaly detection for system health monitoring"""
    
    def __init__(self, threshold_std: float = 2.0):
        self.threshold_std = threshold_std
        self.baseline_stats: Dict[str, Dict] = {}
        self.anomaly_history: List[AnomalyAlert] = []
        self.lock = threading.Lock()
    
    def update_baseline(self, metric_type: str, values: List[float]):
        """Update baseline statistics for anomaly detection"""
        if len(values) < 10:
            return
        
        with self.lock:
            baseline = {
                'mean': statistics.mean(values),
                'std': statistics.stdev(values) if len(values) > 1 else 0,
                'min': min(values),
                'max': max(values),
                'count': len(values),
                'updated': datetime.now()
            }
            self.baseline_stats[metric_type] = baseline
    
    def detect_anomaly(self, metric_type: str, value: float, context: Dict[str, Any] = None) -> Optional[AnomalyAlert]:
        """Detect if a value is anomalous"""
        with self.lock:
            if metric_type not in self.baseline_stats:
                return None
            
            baseline = self.baseline_stats[metric_type]
            
            # Check if baseline is too old (older than 24 hours)
            if (datetime.now() - baseline['updated']).total_seconds() > 86400:
                return None
            
            # Calculate Z-score
            if baseline['std'] == 0:
                return None
            
            z_score = abs(value - baseline['mean']) / baseline['std']
            
            if z_score >= self.threshold_std:
                # Determine severity
                if z_score >= 4:
                    severity = 'critical'
                elif z_score >= 3:
                    severity = 'high'
                elif z_score >= 2:
                    severity = 'medium'
                else:
                    severity = 'low'
                
                alert = AnomalyAlert(
                    timestamp=datetime.now(),
                    metric_type=metric_type,
                    severity=severity,
                    description=f"Anomalous {metric_type}: {value:.3f} (baseline: {baseline['mean']:.3f} ± {baseline['std']:.3f})",
                    predicted_value=baseline['mean'],
                    actual_value=value,
                    confidence=min(0.95, z_score / 5.0)
                )
                
                self.anomaly_history.append(alert)
                
                # Keep only recent anomalies
                if len(self.anomaly_history) > 1000:
                    self.anomaly_history = self.anomaly_history[-500:]
                
                return alert
            
            return None
    
    def get_recent_anomalies(self, hours: int = 24) -> List[AnomalyAlert]:
        """Get recent anomalies"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [a for a in self.anomaly_history if a.timestamp >= cutoff_time]

class InsightsGenerator:
    """AI-powered insights generation"""
    
    def __init__(self):
        self.insights_history: List[Dict] = []
        self.patterns: Dict[str, List[Dict]] = defaultdict(list)
        self.lock = threading.Lock()
    
    def generate_insights(self, metrics: Dict[str, List[PerformanceMetric]], 
                         predictions: Dict[str, Dict], 
                         anomalies: List[AnomalyAlert]) -> List[Dict]:
        """Generate AI-powered insights from analytics data"""
        insights = []
        
        with self.lock:
            # Performance insights
            perf_insights = self._generate_performance_insights(metrics, predictions)
            insights.extend(perf_insights)
            
            # Anomaly insights
            anomaly_insights = self._generate_anomaly_insights(anomalies)
            insights.extend(anomaly_insights)
            
            # Trend insights
            trend_insights = self._generate_trend_insights(metrics)
            insights.extend(trend_insights)
            
            # System health insights
            health_insights = self._generate_health_insights(metrics, anomalies)
            insights.extend(health_insights)
            
            # Store insights
            for insight in insights:
                insight['generated_at'] = datetime.now()
                self.insights_history.append(insight)
            
            # Keep only recent insights
            if len(self.insights_history) > 1000:
                self.insights_history = self.insights_history[-500:]
            
            return insights
    
    def _generate_performance_insights(self, metrics: Dict[str, List[PerformanceMetric]], 
                                      predictions: Dict[str, Dict]) -> List[Dict]:
        """Generate performance-related insights"""
        insights = []
        
        for metric_type, prediction in predictions.items():
            if prediction['confidence'] > 0.7:
                if prediction['trend'] == 'increasing':
                    insight = {
                        'type': 'performance_trend',
                        'category': 'optimization',
                        'priority': 'medium' if prediction['confidence'] > 0.8 else 'low',
                        'title': f'{metric_type} trending upward',
                        'description': f"{metric_type} is predicted to increase by {prediction['predicted_value']:.2f} in the next hour",
                        'recommendation': 'Monitor system capacity and consider scaling if trend continues',
                        'confidence': prediction['confidence']
                    }
                    insights.append(insight)
                elif prediction['trend'] == 'decreasing':
                    insight = {
                        'type': 'performance_trend',
                        'category': 'optimization',
                        'priority': 'high' if prediction['confidence'] > 0.8 else 'medium',
                        'title': f'{metric_type} trending downward',
                        'description': f"{metric_type} is predicted to decrease by {prediction['predicted_value']:.2f} in the next hour",
                        'recommendation': 'Investigate potential performance improvements',
                        'confidence': prediction['confidence']
                    }
                    insights.append(insight)
        
        return insights
    
    def _generate_anomaly_insights(self, anomalies: List[AnomalyAlert]) -> List[Dict]:
        """Generate anomaly-related insights"""
        insights = []
        
        # Count anomalies by severity
        severity_counts = defaultdict(int)
        metric_anomalies = defaultdict(list)
        
        for anomaly in anomalies:
            severity_counts[anomaly.severity] += 1
            metric_anomalies[anomaly.metric_type].append(anomaly)
        
        # Critical anomalies
        if severity_counts['critical'] > 0:
            insight = {
                'type': 'critical_anomaly',
                'category': 'alert',
                'priority': 'critical',
                'title': f'{severity_counts["critical"]} critical anomalies detected',
                'description': f"Critical anomalies require immediate attention",
                'recommendation': 'Investigate critical anomalies immediately',
                'confidence': 0.95
            }
            insights.append(insight)
        
        # High anomalies
        if severity_counts['high'] > 2:
            insight = {
                'type': 'high_anomaly_frequency',
                'category': 'alert',
                'priority': 'high',
                'title': f'{severity_counts["high"]} high-severity anomalies detected',
                'description': f"Multiple high-severity anomalies may indicate systemic issues",
                'recommendation': 'Review system configuration and performance',
                'confidence': 0.85
            }
            insights.append(insight)
        
        # Metric-specific patterns
        for metric_type, metric_anomaly_list in metric_anomalies.items():
            if len(metric_anomaly_list) > 3:
                insight = {
                    'type': 'recurring_anomaly',
                    'category': 'pattern',
                    'priority': 'medium',
                    'title': f'Recurring anomalies in {metric_type}',
                    'description': f"{metric_type} shows {len(metric_anomaly_list)} anomalies",
                    'recommendation': f'Investigate {metric_type} configuration and stability',
                    'confidence': 0.75
                }
                insights.append(insight)
        
        return insights
    
    def _generate_trend_insights(self, metrics: Dict[str, List[PerformanceMetric]]) -> List[Dict]:
        """Generate trend-related insights"""
        insights = []
        
        for metric_type, metric_list in metrics.items():
            if len(metric_list) < 20:
                continue
            
            values = [m.value for m in metric_list]
            
            # Calculate trend
            if len(values) >= 10:
                recent_values = values[-10:]
                older_values = values[-20:-10] if len(values) >= 20 else values[:-10]
                
                if older_values:
                    recent_avg = statistics.mean(recent_values)
                    older_avg = statistics.mean(older_values)
                    
                    change_percent = ((recent_avg - older_avg) / older_avg) * 100 if older_avg != 0 else 0
                    
                    if abs(change_percent) > 15:  # Significant change
                        direction = 'improvement' if change_percent > 0 else 'degradation'
                        priority = 'high' if abs(change_percent) > 25 else 'medium'
                        
                        insight = {
                            'type': 'significant_trend',
                            'category': 'performance',
                            'priority': priority,
                            'title': f'Significant {direction} in {metric_type}',
                            'description': f"{metric_type} changed by {change_percent:.1f}% recently",
                            'recommendation': f"Investigate {direction} cause and optimize accordingly",
                            'confidence': 0.8
                        }
                        insights.append(insight)
        
        return insights
    
    def _generate_health_insights(self, metrics: Dict[str, List[PerformanceMetric]], 
                                 anomalies: List[AnomalyAlert]) -> List[Dict]:
        """Generate system health insights"""
        insights = []
        
        # System stability assessment
        total_metrics = len(metrics)
        stable_metrics = 0
        
        for metric_type, metric_list in metrics.items():
            if len(metric_list) < 10:
                continue
            
            values = [m.value for m in metric_list]
            if len(values) >= 3:
                volatility = statistics.stdev(values) if len(values) > 1 else 0
                avg_value = statistics.mean(values)
                
                # Consider stable if volatility is less than 20% of average
                if avg_value != 0 and (volatility / abs(avg_value)) < 0.2:
                    stable_metrics += 1
        
        stability_ratio = stable_metrics / total_metrics if total_metrics > 0 else 0
        
        if stability_ratio < 0.5:
            insight = {
                'type': 'system_stability',
                'category': 'health',
                'priority': 'medium',
                'title': 'System stability concerns',
                'description': f"Only {stability_ratio:.1%} of metrics are stable",
                'recommendation': 'Review system configuration and investigate instability causes',
                'confidence': 0.75
            }
            insights.append(insight)
        elif stability_ratio > 0.8:
            insight = {
                'type': 'system_stability',
                'category': 'health',
                'priority': 'low',
                'title': 'System stability good',
                'description': f"{stability_ratio:.1%} of metrics are stable",
                'recommendation': 'Continue monitoring and maintain current configuration',
                'confidence': 0.8
            }
            insights.append(insight)
        
        return insights

class AdvancedAnalyticsSystem:
    """Main advanced analytics system"""
    
    def __init__(self):
        self.predictive_analytics = PredictiveAnalytics()
        self.anomaly_detector = AnomalyDetector()
        self.insights_generator = InsightsGenerator()
        self.metrics_buffer: Dict[str, List[PerformanceMetric]] = defaultdict(list)
        self.last_analysis = datetime.now()
        self.analysis_interval = timedelta(minutes=5)  # Analyze every 5 minutes
        self.lock = threading.Lock()
    
    def add_metric(self, metric_type: str, value: float, context: Dict[str, Any] = None):
        """Add a new metric for analysis"""
        with self.lock:
            timestamp = datetime.now()
            metric = PerformanceMetric(timestamp, metric_type, value, context or {})
            
            # Add to buffer
            self.metrics_buffer[metric_type].append(metric)
            
            # Keep buffer size manageable
            if len(self.metrics_buffer[metric_type]) > 1000:
                self.metrics_buffer[metric_type] = self.metrics_buffer[metric_type][-500:]
            
            # Add to predictive analytics
            self.predictive_analytics.add_metric(metric_type, value, context)
            
            # Update anomaly detection baseline
            if len(self.metrics_buffer[metric_type]) >= 20:
                values = [m.value for m in self.metrics_buffer[metric_type]]
                self.anomaly_detector.update_baseline(metric_type, values)
            
            # Check for anomalies
            anomaly = self.anomaly_detector.detect_anomaly(metric_type, value, context)
            if anomaly:
                print(f"🚨 Anomaly detected: {anomaly.description}")
    
    def analyze_and_generate_insights(self) -> Dict:
        """Perform comprehensive analysis and generate insights"""
        with self.lock:
            # Check if it's time for analysis
            if datetime.now() - self.last_analysis < self.analysis_interval:
                return {'message': 'Analysis not yet due', 'next_analysis': self.last_analysis + self.analysis_interval}
            
            # Generate predictions
            predictions = {}
            for metric_type in self.metrics_buffer.keys():
                prediction = self.predictive_analytics.predict_metric(metric_type)
                if prediction:
                    predictions[metric_type] = prediction
            
            # Get recent anomalies
            recent_anomalies = self.anomaly_detector.get_recent_anomalies(24)
            
            # Generate insights
            insights = self.insights_generator.generate_insights(
                self.metrics_buffer, predictions, recent_anomalies
            )
            
            # Update analysis timestamp
            self.last_analysis = datetime.now()
            
            return {
                'analysis_timestamp': self.last_analysis.isoformat(),
                'predictions': predictions,
                'anomalies': [
                    {
                        'timestamp': a.timestamp.isoformat(),
                        'metric_type': a.metric_type,
                        'severity': a.severity,
                        'description': a.description,
                        'confidence': a.confidence
                    }
                    for a in recent_anomalies[-10:]  # Last 10 anomalies
                ],
                'insights': insights,
                'metrics_summary': {
                    metric_type: {
                        'count': len(metrics),
                        'latest_value': metrics[-1].value if metrics else None,
                        'latest_timestamp': metrics[-1].timestamp.isoformat() if metrics else None
                    }
                    for metric_type, metrics in self.metrics_buffer.items()
                }
            }
    
    def get_comprehensive_stats(self) -> Dict:
        """Get comprehensive analytics statistics"""
        with self.lock:
            return {
                'predictive_analytics': {
                    'metrics_tracked': len(self.predictive_analytics.metric_history),
                    'prediction_models': len(self.predictive_analytics.prediction_models),
                    'total_predictions': sum(
                        len(self.predictive_analytics.metric_history[m])
                        for m in self.predictive_analytics.metric_history
                    )
                },
                'anomaly_detection': {
                    'baselines_established': len(self.anomaly_detector.baseline_stats),
                    'recent_anomalies': len(self.anomaly_detector.get_recent_anomalies(24)),
                    'total_anomalies': len(self.anomaly_detector.anomaly_history)
                },
                'insights_generation': {
                    'total_insights': len(self.insights_generator.insights_history),
                    'patterns_identified': len(self.insights_generator.patterns),
                    'last_analysis': self.last_analysis.isoformat()
                },
                'system_metrics': {
                    'metrics_buffered': len(self.metrics_buffer),
                    'total_data_points': sum(len(metrics) for metrics in self.metrics_buffer.values()),
                    'analysis_interval_minutes': self.analysis_interval.total_seconds() / 60
                }
            }

# Global analytics system instance
advanced_analytics = AdvancedAnalyticsSystem()

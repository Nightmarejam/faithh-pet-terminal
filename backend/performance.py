"""
FAITHH Performance Tracking System

Provides comprehensive performance monitoring and optimization
for the FAITHH backend system.

Priority: Phase 4.1 - Performance Foundation
"""

import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from collections import deque, defaultdict
import json
import statistics
from dataclasses import dataclass, asdict

@dataclass
class PerformanceMetric:
    """Single performance metric"""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    tags: Dict[str, str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'metric_name': self.metric_name,
            'value': self.value,
            'unit': self.unit,
            'tags': self.tags
        }

@dataclass
class RequestMetrics:
    """Metrics for a single request"""
    request_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    model_used: str = ""
    provider_used: str = ""
    query_length: int = 0
    response_length: int = 0
    rag_used: bool = False
    rag_chunks_retrieved: int = 0
    chips_activated: List[str] = None
    cache_hit: bool = False
    success: bool = True
    error_type: Optional[str] = None
    
    def __post_init__(self):
        if self.chips_activated is None:
            self.chips_activated = []
    
    def complete(self, end_time: datetime, success: bool = True, error_type: str = None):
        """Mark request as completed"""
        self.end_time = end_time
        self.duration_ms = (end_time - self.start_time).total_seconds() * 1000
        self.success = success
        self.error_type = error_type
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

class PerformanceTracker:
    """Main performance tracking system"""
    
    def __init__(self, max_history_size: int = 10000):
        self.max_history_size = max_history_size
        self.active_requests: Dict[str, RequestMetrics] = {}
        self.completed_requests: deque = deque(maxlen=max_history_size)
        self.system_metrics: deque = deque(maxlen=1000)
        self.custom_metrics: deque = deque(maxlen=5000)
        
        # Performance thresholds
        self.thresholds = {
            'response_time_warning': 3000,  # 3 seconds
            'response_time_critical': 10000,  # 10 seconds
            'memory_warning': 80,  # 80% memory usage
            'cpu_warning': 80,     # 80% CPU usage
            'disk_warning': 90     # 90% disk usage
        }
        
        # Aggregated stats
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'avg_response_time': 0.0,
            'cache_hit_rate': 0.0,
            'rag_usage_rate': 0.0
        }
        
        # Monitoring thread
        self.monitoring_thread = None
        self.monitoring_active = False
        
        # Callbacks for alerts
        self.alert_callbacks: List[Callable] = []
    
    def start_request_tracking(self, request_id: str, model: str = "", 
                              provider: str = "", query: str = "",
                              use_rag: bool = False) -> RequestMetrics:
        """Start tracking a new request"""
        request = RequestMetrics(
            request_id=request_id,
            start_time=datetime.now(),
            model_used=model,
            provider_used=provider,
            query_length=len(query),
            rag_used=use_rag
        )
        
        self.active_requests[request_id] = request
        return request
    
    def update_request_progress(self, request_id: str, **kwargs):
        """Update request progress"""
        if request_id in self.active_requests:
            request = self.active_requests[request_id]
            for key, value in kwargs.items():
                if hasattr(request, key):
                    setattr(request, key, value)
    
    def complete_request(self, request_id: str, success: bool = True, 
                        error_type: str = None, response: str = "",
                        rag_chunks: int = 0, chips_used: List[str] = None,
                        cache_hit: bool = False):
        """Complete request tracking"""
        if request_id not in self.active_requests:
            return
        
        request = self.active_requests[request_id]
        request.complete(datetime.now(), success, error_type)
        
        # Update additional fields
        request.response_length = len(response)
        request.rag_chunks_retrieved = rag_chunks
        if chips_used:
            request.chips_activated = chips_used
        request.cache_hit = cache_hit
        
        # Move to completed requests
        self.completed_requests.append(request)
        del self.active_requests[request_id]
        
        # Update stats
        self._update_stats()
        
        # Check for performance alerts
        self._check_performance_alerts(request)
    
    def track_metric(self, metric_name: str, value: float, unit: str = "", 
                     tags: Dict[str, str] = None):
        """Track a custom metric"""
        if tags is None:
            tags = {}
        
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            metric_name=metric_name,
            value=value,
            unit=unit,
            tags=tags
        )
        
        self.custom_metrics.append(metric)
    
    def get_request_stats(self, time_window_minutes: int = 60) -> Dict:
        """Get request statistics for time window"""
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        
        recent_requests = [
            req for req in self.completed_requests
            if req.start_time >= cutoff_time
        ]
        
        if not recent_requests:
            return {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'avg_response_time': 0.0,
                'median_response_time': 0.0,
                'p95_response_time': 0.0,
                'cache_hit_rate': 0.0,
                'rag_usage_rate': 0.0,
                'error_rate': 0.0
            }
        
        # Calculate metrics
        successful_requests = [req for req in recent_requests if req.success]
        failed_requests = [req for req in recent_requests if not req.success]
        
        response_times = [req.duration_ms for req in recent_requests if req.duration_ms]
        cache_hits = [req for req in recent_requests if req.cache_hit]
        rag_requests = [req for req in recent_requests if req.rag_used]
        
        return {
            'total_requests': len(recent_requests),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'avg_response_time': statistics.mean(response_times) if response_times else 0.0,
            'median_response_time': statistics.median(response_times) if response_times else 0.0,
            'p95_response_time': self._percentile(response_times, 95) if response_times else 0.0,
            'cache_hit_rate': (len(cache_hits) / len(recent_requests)) * 100 if recent_requests else 0.0,
            'rag_usage_rate': (len(rag_requests) / len(recent_requests)) * 100 if recent_requests else 0.0,
            'error_rate': (len(failed_requests) / len(recent_requests)) * 100 if recent_requests else 0.0
        }
    
    def get_system_metrics(self) -> Dict:
        """Get current system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network I/O
            network = psutil.net_io_counters()
            
            # Process info
            process = psutil.Process()
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count()
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'process': {
                    'pid': process.pid,
                    'memory_percent': process.memory_percent(),
                    'cpu_percent': process.cpu_percent(),
                    'num_threads': process.num_threads(),
                    'create_time': process.create_time()
                }
            }
            
            # Store for history
            self.system_metrics.append({
                'timestamp': datetime.now(),
                'metrics': metrics
            })
            
            return metrics
            
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def get_model_performance(self, model: str = None, time_window_minutes: int = 60) -> Dict:
        """Get performance metrics by model"""
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        
        recent_requests = [
            req for req in self.completed_requests
            if req.start_time >= cutoff_time
        ]
        
        # Filter by model if specified
        if model:
            recent_requests = [req for req in recent_requests if req.model_used == model]
        
        if not recent_requests:
            return {}
        
        # Group by model
        model_stats = defaultdict(list)
        for req in recent_requests:
            model_stats[req.model_used].append(req)
        
        # Calculate stats for each model
        result = {}
        for model_name, requests in model_stats.items():
            response_times = [req.duration_ms for req in requests if req.duration_ms]
            successful = [req for req in requests if req.success]
            
            result[model_name] = {
                'total_requests': len(requests),
                'successful_requests': len(successful),
                'success_rate': (len(successful) / len(requests)) * 100 if requests else 0.0,
                'avg_response_time': statistics.mean(response_times) if response_times else 0.0,
                'median_response_time': statistics.median(response_times) if response_times else 0.0,
                'p95_response_time': self._percentile(response_times, 95) if response_times else 0.0,
                'rag_usage_rate': (len([req for req in requests if req.rag_used]) / len(requests)) * 100 if requests else 0.0
            }
        
        return result
    
    def get_performance_summary(self) -> Dict:
        """Get comprehensive performance summary"""
        current_requests = len(self.active_requests)
        
        # Get recent stats
        recent_stats = self.get_request_stats(60)  # Last hour
        system_metrics = self.get_system_metrics()
        
        # Get model performance
        model_performance = self.get_model_performance()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'active_requests': current_requests,
            'recent_performance': recent_stats,
            'system_metrics': system_metrics,
            'model_performance': model_performance,
            'thresholds': self.thresholds,
            'total_tracked_requests': len(self.completed_requests)
        }
    
    def _update_stats(self):
        """Update aggregated statistics"""
        if not self.completed_requests:
            return
        
        total_requests = len(self.completed_requests)
        successful_requests = len([req for req in self.completed_requests if req.success])
        
        response_times = [req.duration_ms for req in self.completed_requests if req.duration_ms]
        avg_response_time = statistics.mean(response_times) if response_times else 0.0
        
        cache_hits = len([req for req in self.completed_requests if req.cache_hit])
        cache_hit_rate = (cache_hits / total_requests) * 100 if total_requests > 0 else 0.0
        
        rag_requests = len([req for req in self.completed_requests if req.rag_used])
        rag_usage_rate = (rag_requests / total_requests) * 100 if total_requests > 0 else 0.0
        
        self.stats.update({
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': total_requests - successful_requests,
            'avg_response_time': avg_response_time,
            'cache_hit_rate': cache_hit_rate,
            'rag_usage_rate': rag_usage_rate
        })
    
    def _check_performance_alerts(self, request: RequestMetrics):
        """Check for performance alerts"""
        alerts = []
        
        # Response time alerts
        if request.duration_ms:
            if request.duration_ms > self.thresholds['response_time_critical']:
                alerts.append({
                    'type': 'critical',
                    'metric': 'response_time',
                    'value': request.duration_ms,
                    'threshold': self.thresholds['response_time_critical'],
                    'request_id': request.request_id,
                    'message': f'Critical response time: {request.duration_ms:.2f}ms'
                })
            elif request.duration_ms > self.thresholds['response_time_warning']:
                alerts.append({
                    'type': 'warning',
                    'metric': 'response_time',
                    'value': request.duration_ms,
                    'threshold': self.thresholds['response_time_warning'],
                    'request_id': request.request_id,
                    'message': f'High response time: {request.duration_ms:.2f}ms'
                })
        
        # Error alerts
        if not request.success:
            alerts.append({
                'type': 'error',
                'metric': 'request_error',
                'value': request.error_type,
                'threshold': None,
                'request_id': request.request_id,
                'message': f'Request failed: {request.error_type}'
            })
        
        # Trigger callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alerts)
            except Exception as e:
                print(f"Alert callback error: {e}")
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def start_monitoring(self, interval_seconds: int = 30):
        """Start background system monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitoring_thread.start()
        print("📊 Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        print("📊 Performance monitoring stopped")
    
    def _monitoring_loop(self, interval_seconds: int):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                self.get_system_metrics()
                time.sleep(interval_seconds)
            except Exception as e:
                print(f"Monitoring loop error: {e}")
                time.sleep(interval_seconds)
    
    def register_alert_callback(self, callback: Callable):
        """Register callback for performance alerts"""
        self.alert_callbacks.append(callback)
    
    def export_metrics(self, format: str = 'json') -> str:
        """Export metrics for analysis"""
        data = {
            'summary': self.get_performance_summary(),
            'completed_requests': [req.to_dict() for req in list(self.completed_requests)[-1000:]],
            'system_metrics': list(self.system_metrics)[-500:],
            'custom_metrics': [metric.to_dict() for metric in list(self.custom_metrics)[-1000:]]
        }
        
        if format.lower() == 'json':
            return json.dumps(data, indent=2, default=str)
        else:
            return str(data)

# Global performance tracker instance
performance_tracker = PerformanceTracker()

# Flask integration decorator
def track_request_performance():
    """Decorator to track Flask request performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            from flask import request, g, jsonify
            
            # Generate request ID
            import uuid
            request_id = str(uuid.uuid4())
            
            # Get request data
            request_data = request.get_json() or {}
            
            # Start tracking
            tracker = performance_tracker.start_request_tracking(
                request_id=request_id,
                model=request_data.get('model', ''),
                provider=request_data.get('provider', ''),
                query=request_data.get('message', ''),
                use_rag=request_data.get('use_rag', False)
            )
            
            # Store in Flask context
            g.performance_tracker = tracker
            g.request_id = request_id
            
            start_time = time.time()
            
            try:
                # Execute the function
                response = func(*args, **kwargs)
                
                # Get response data
                response_data = {}
                if hasattr(response, 'get_json'):
                    try:
                        response_data = response.get_json() or {}
                    except:
                        response_data = {}
                elif isinstance(response, dict):
                    response_data = response
                
                # Complete tracking
                performance_tracker.complete_request(
                    request_id=request_id,
                    success=True,
                    response=response_data.get('response', ''),
                    rag_chunks=len(response_data.get('rag_results', [])),
                    chips_used=response_data.get('ml_chips_activated', []),
                    cache_hit=getattr(g, 'from_cache', False)
                )
                
                return response
                
            except Exception as e:
                # Complete tracking with error
                performance_tracker.complete_request(
                    request_id=request_id,
                    success=False,
                    error_type=str(e)
                )
                
                # Re-raise the exception
                raise
        
        return wrapper
    return decorator

# Start monitoring
performance_tracker.start_monitoring()

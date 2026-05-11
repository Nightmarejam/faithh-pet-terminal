#!/usr/bin/env python3
"""
Performance Monitoring and Metrics
Tracks model performance, API calls, and system metrics
"""

import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class PerformanceLogger:
    """Tracks model performance and usage metrics"""
    
    def __init__(self, log_file: str = 'logs/performance.log'):
        self.log_file = log_file
        self.metrics = []
        self.lock = threading.Lock()
        self.start_time = datetime.utcnow()
    
    def log_api_call(self, provider: str, model: str, 
                    response_time: float, success: bool, 
                    error: Optional[str] = None, tokens_used: int = 0):
        """Log API call performance"""
        metric = {
            'timestamp': datetime.utcnow().isoformat(),
            'provider': provider,
            'model': model,
            'response_time_ms': round(response_time * 1000, 2),
            'success': success,
            'error': error,
            'tokens_used': tokens_used
        }
        
        with self.lock:
            self.metrics.append(metric)
        
        # Log to file
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(metric) + '\n')
        except Exception as e:
            print(f"Failed to write performance log: {e}")
    
    def log_model_switch(self, from_model: str, to_model: str, reason: str):
        """Log model switching events"""
        switch_event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'model_switch',
            'from_model': from_model,
            'to_model': to_model,
            'reason': reason
        }
        
        with self.lock:
            self.metrics.append(switch_event)
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(switch_event) + '\n')
        except Exception as e:
            print(f"Failed to write switch log: {e}")
    
    def log_resource_usage(self, cpu_percent: float, memory_mb: float, 
                          gpu_memory_mb: float = None):
        """Log system resource usage"""
        resource_metric = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'resource_usage',
            'cpu_percent': cpu_percent,
            'memory_mb': memory_mb,
            'gpu_memory_mb': gpu_memory_mb
        }
        
        with self.lock:
            self.metrics.append(resource_metric)
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(resource_metric) + '\n')
        except Exception as e:
            print(f"Failed to write resource log: {e}")
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Generate performance summary for specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        with self.lock:
            recent_metrics = [
                m for m in self.metrics 
                if datetime.fromisoformat(m['timestamp'].replace('Z', '+00:00')) > cutoff_time
            ]
        
        if not recent_metrics:
            return {'period_hours': hours, 'total_calls': 0}
        
        # Filter for API calls only
        api_calls = [m for m in recent_metrics if 'provider' in m]
        
        if not api_calls:
            return {'period_hours': hours, 'total_calls': 0, 'api_calls': 0}
        
        # Calculate metrics
        total_calls = len(api_calls)
        successful_calls = sum(1 for m in api_calls if m['success'])
        failed_calls = total_calls - successful_calls
        
        response_times = [m['response_time_ms'] for m in api_calls if m['success']]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Provider breakdown
        provider_stats = {}
        for call in api_calls:
            provider = call['provider']
            if provider not in provider_stats:
                provider_stats[provider] = {'calls': 0, 'success': 0, 'errors': 0}
            provider_stats[provider]['calls'] += 1
            if call['success']:
                provider_stats[provider]['success'] += 1
            else:
                provider_stats[provider]['errors'] += 1
        
        # Model breakdown
        model_stats = {}
        for call in api_calls:
            model = call['model']
            if model not in model_stats:
                model_stats[model] = {'calls': 0, 'avg_response_time': 0, 'success_rate': 0}
            model_stats[model]['calls'] += 1
        
        # Calculate model averages
        for model in model_stats:
            model_calls = [m for m in api_calls if m['model'] == model and m['success']]
            if model_calls:
                model_stats[model]['avg_response_time'] = sum(m['response_time_ms'] for m in model_calls) / len(model_calls)
                model_stats[model]['success_rate'] = len([m for m in model_calls if m['success']]) / len(model_calls) * 100
        
        return {
            'period_hours': hours,
            'total_calls': total_calls,
            'successful_calls': successful_calls,
            'failed_calls': failed_calls,
            'success_rate': (successful_calls / total_calls * 100) if total_calls > 0 else 0,
            'avg_response_time_ms': round(avg_response_time, 2),
            'providers': provider_stats,
            'models': model_stats,
            'total_tokens_used': sum(m.get('tokens_used', 0) for m in api_calls)
        }
    
    def get_error_analysis(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze error patterns"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        with self.lock:
            recent_metrics = [
                m for m in self.metrics 
                if datetime.fromisoformat(m['timestamp'].replace('Z', '+00:00')) > cutoff_time
            ]
        
        # Filter for failed calls
        failed_calls = [m for m in recent_metrics if 'provider' in m and not m['success']]
        
        if not failed_calls:
            return {'period_hours': hours, 'total_errors': 0}
        
        # Error categorization
        error_types = {}
        for call in failed_calls:
            error = call.get('error', 'Unknown error')
            error_type = 'Authentication' if 'auth' in error.lower() else \
                         'Rate Limit' if 'rate' in error.lower() else \
                         'Timeout' if 'timeout' in error.lower() else \
                         'Connection' if 'connection' in error.lower() else \
                         'Model Error' if 'model' in error.lower() else \
                         'Other'
            
            if error_type not in error_types:
                error_types[error_type] = 0
            error_types[error_type] += 1
        
        return {
            'period_hours': hours,
            'total_errors': len(failed_calls),
            'error_types': error_types,
            'most_common_error': max(error_types.items(), key=lambda x: x[1])[0] if error_types else None
        }

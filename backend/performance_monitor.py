"""
Performance Monitor for LLM Providers
Tracks response times, success rates, and implements intelligent provider selection
"""

import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque
import json

class ProviderPerformanceMonitor:
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.performance_data = defaultdict(lambda: deque(maxlen=max_history))
        self.error_counts = defaultdict(int)
        self.last_health_check = {}
        
    def record_request(self, provider: str, response_time: float, success: bool, error: str = None):
        """Record a provider request for performance tracking"""
        timestamp = datetime.now()
        
        self.performance_data[provider].append({
            'timestamp': timestamp,
            'response_time': response_time,
            'success': success,
            'error': error
        })
        
        if not success:
            self.error_counts[provider] += 1
    
    def get_provider_stats(self, provider: str) -> Dict[str, any]:
        """Get performance statistics for a specific provider"""
        if provider not in self.performance_data or not self.performance_data[provider]:
            return {
                'provider': provider,
                'total_requests': 0,
                'success_rate': 0.0,
                'avg_response_time': 0.0,
                'error_rate': 0.0,
                'last_request': None,
                'status': 'unknown'
            }
        
        data = list(self.performance_data[provider])
        successful_requests = [r for r in data if r['success']]
        
        total_requests = len(data)
        success_rate = len(successful_requests) / total_requests if total_requests > 0 else 0.0
        error_rate = 1.0 - success_rate
        
        if successful_requests:
            response_times = [r['response_time'] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = min_response_time = max_response_time = 0.0
        
        # Determine status based on recent performance
        recent_data = [r for r in data if r['timestamp'] > datetime.now() - timedelta(minutes=5)]
        if recent_data:
            recent_success_rate = sum(1 for r in recent_data if r['success']) / len(recent_data)
            if recent_success_rate >= 0.95:
                status = 'excellent'
            elif recent_success_rate >= 0.8:
                status = 'good'
            elif recent_success_rate >= 0.5:
                status = 'degraded'
            else:
                status = 'poor'
        else:
            status = 'stale'
        
        return {
            'provider': provider,
            'total_requests': total_requests,
            'success_rate': success_rate,
            'error_rate': error_rate,
            'avg_response_time': avg_response_time,
            'min_response_time': min_response_time,
            'max_response_time': max_response_time,
            'last_request': data[-1]['timestamp'] if data else None,
            'status': status
        }
    
    def get_best_provider(self, available_providers: List[str]) -> Optional[str]:
        """Select the best provider based on recent performance"""
        if not available_providers:
            return None
        
        provider_scores = {}
        for provider in available_providers:
            stats = self.get_provider_stats(provider)
            
            # Skip providers with no recent data
            if stats['total_requests'] == 0:
                continue
            
            # Calculate score (lower is better)
            # Weight: 70% response time, 30% success rate
            response_time_score = stats['avg_response_time']
            success_rate_penalty = (1.0 - stats['success_rate']) * 10  # Heavy penalty for failures
            
            # Add penalty for poor status
            status_penalty = 0
            if stats['status'] == 'poor':
                status_penalty = 5.0
            elif stats['status'] == 'degraded':
                status_penalty = 2.0
            elif stats['status'] == 'stale':
                status_penalty = 1.0
            
            total_score = response_time_score + success_rate_penalty + status_penalty
            provider_scores[provider] = total_score
        
        if not provider_scores:
            # Fallback to first available provider
            return available_providers[0]
        
        # Return provider with lowest score
        best_provider = min(provider_scores, key=provider_scores.get)
        return best_provider
    
    def get_health_summary(self) -> Dict[str, any]:
        """Get overall health summary for all providers"""
        all_providers = list(self.performance_data.keys())
        if not all_providers:
            return {
                'healthy_providers': [],
                'degraded_providers': [],
                'failed_providers': [],
                'total_requests': 0,
                'overall_status': 'unknown'
            }
        
        healthy = []
        degraded = []
        failed = []
        total_requests = 0
        
        for provider in all_providers:
            stats = self.get_provider_stats(provider)
            total_requests += stats['total_requests']
            
            if stats['status'] in ['excellent', 'good']:
                healthy.append(provider)
            elif stats['status'] in ['degraded', 'stale']:
                degraded.append(provider)
            else:
                failed.append(provider)
        
        # Determine overall status
        if healthy and not failed:
            overall_status = 'healthy'
        elif healthy:
            overall_status = 'degraded'
        else:
            overall_status = 'failed'
        
        return {
            'healthy_providers': healthy,
            'degraded_providers': degraded,
            'failed_providers': failed,
            'total_requests': total_requests,
            'overall_status': overall_status,
            'provider_stats': {p: self.get_provider_stats(p) for p in all_providers}
        }
    
    def cleanup_old_data(self, max_age_hours: int = 24):
        """Clean up old performance data"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        for provider in list(self.performance_data.keys()):
            # Filter out old data
            self.performance_data[provider] = deque(
                (r for r in self.performance_data[provider] if r['timestamp'] > cutoff_time),
                maxlen=self.max_history
            )
            
            # Remove provider if no data left
            if not self.performance_data[provider]:
                del self.performance_data[provider]
                if provider in self.error_counts:
                    del self.error_counts[provider]

# Global performance monitor instance
performance_monitor = ProviderPerformanceMonitor()

def record_provider_performance(provider: str, response_time: float, success: bool, error: str = None):
    """Convenience function to record provider performance"""
    performance_monitor.record_request(provider, response_time, success, error)

def get_optimal_provider(available_providers: List[str]) -> Optional[str]:
    """Convenience function to get the optimal provider"""
    return performance_monitor.get_best_provider(available_providers)

def get_provider_health() -> Dict[str, any]:
    """Convenience function to get provider health summary"""
    return performance_monitor.get_health_summary()

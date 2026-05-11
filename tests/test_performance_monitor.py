#!/usr/bin/env python3
"""
Unit Tests for Performance Monitor
Tests provider performance tracking, health status, and optimal selection
"""

import os
import sys
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Ensure backend is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.performance_monitor import (
    ProviderPerformanceMonitor,
    record_provider_performance,
    get_optimal_provider,
    get_provider_health
)

class TestProviderPerformanceMonitor:
    """Test provider performance monitoring functionality"""

    def test_monitor_initialization(self):
        """Test monitor initializes with empty data structures"""
        monitor = ProviderPerformanceMonitor()
        
        assert len(monitor.performance_data) == 0
        assert len(monitor.error_counts) == 0
        assert len(monitor.last_health_check) == 0
        assert monitor.max_history == 100

    def test_record_request_success(self):
        """Test recording a successful provider request"""
        monitor = ProviderPerformanceMonitor()
        
        provider = "ollama"
        response_time = 1.5
        success = True
        
        monitor.record_request(provider, response_time, success)
        
        # Verify data was recorded
        assert provider in monitor.performance_data
        assert len(monitor.performance_data[provider]) == 1
        
        request_data = monitor.performance_data[provider][0]
        assert request_data["response_time"] == response_time
        assert request_data["success"] is True
        assert request_data["error"] is None
        assert isinstance(request_data["timestamp"], datetime)

    def test_record_request_failure(self):
        """Test recording a failed provider request"""
        monitor = ProviderPerformanceMonitor()
        
        provider = "groq"
        response_time = 5.0
        success = False
        error = "timeout"
        
        monitor.record_request(provider, response_time, success, error)
        
        # Verify data was recorded
        assert provider in monitor.performance_data
        assert len(monitor.performance_data[provider]) == 1
        
        request_data = monitor.performance_data[provider][0]
        assert request_data["response_time"] == response_time
        assert request_data["success"] is False
        assert request_data["error"] == error
        
        # Verify error count was incremented
        assert provider in monitor.error_counts
        assert monitor.error_counts[provider] == 1

    def test_record_request_multiple_providers(self):
        """Test recording requests for multiple providers"""
        monitor = ProviderPerformanceMonitor()
        
        # Record requests for different providers
        monitor.record_request("ollama", 1.2, True)
        monitor.record_request("gemini", 0.8, True)
        monitor.record_request("groq", 3.5, False, "rate_limit")
        
        # Verify all providers have data
        assert len(monitor.performance_data) == 3
        assert "ollama" in monitor.performance_data
        assert "gemini" in monitor.performance_data
        assert "groq" in monitor.performance_data
        
        # Verify error count for failed provider
        assert monitor.error_counts["groq"] == 1
        assert monitor.error_counts.get("ollama", 0) == 0
        assert monitor.error_counts.get("gemini", 0) == 0

    def test_get_provider_stats_single_request(self):
        """Test getting statistics for provider with single request"""
        monitor = ProviderPerformanceMonitor()
        
        monitor.record_request("ollama", 1.5, True)
        
        stats = monitor.get_provider_stats("ollama")
        
        assert stats["provider"] == "ollama"
        assert stats["total_requests"] == 1
        assert stats["success_rate"] == 1.0
        assert stats["error_rate"] == 0.0
        assert stats["avg_response_time"] == 1.5
        assert stats["min_response_time"] == 1.5
        assert stats["max_response_time"] == 1.5
        assert stats["status"] in ["excellent", "good"]  # Based on recent performance

    def test_get_provider_stats_multiple_requests(self):
        """Test getting statistics for provider with multiple requests"""
        monitor = ProviderPerformanceMonitor()
        
        # Record multiple requests with varying performance
        monitor.record_request("gemini", 0.8, True)
        monitor.record_request("gemini", 1.2, True)
        monitor.record_request("gemini", 2.5, False, "timeout")
        monitor.record_request("gemini", 0.9, True)
        
        stats = monitor.get_provider_stats("gemini")
        
        assert stats["total_requests"] == 4
        assert stats["success_rate"] == 0.75
        assert stats["error_rate"] == 0.25
        assert abs(stats["avg_response_time"] - 0.967) < 0.02  # Only successful requests: (0.8 + 1.2 + 0.9) / 3
        assert stats["min_response_time"] == 0.8
        assert stats["max_response_time"] == 1.2  # Only successful requests
        assert "last_request" in stats

    def test_get_provider_stats_no_data(self):
        """Test getting statistics for provider with no data"""
        monitor = ProviderPerformanceMonitor()
        
        stats = monitor.get_provider_stats("nonexistent")
        
        assert stats["provider"] == "nonexistent"
        assert stats["total_requests"] == 0
        assert stats["success_rate"] == 0.0
        assert stats["error_rate"] == 0.0
        assert stats["avg_response_time"] == 0.0
        assert stats["status"] in ["stale", "unknown"]  # May vary based on implementation

    def test_get_provider_status_excellent(self):
        """Test provider status determination for excellent performance"""
        monitor = ProviderPerformanceMonitor()
        
        # Record excellent performance
        for i in range(10):
            monitor.record_request("ollama", 0.5 + i * 0.1, True)  # 0.5 to 1.4 seconds
        
        stats = monitor.get_provider_stats("ollama")
        assert stats["status"] == "excellent"

    def test_get_provider_status_healthy(self):
        """Test provider status determination for healthy performance"""
        monitor = ProviderPerformanceMonitor()
        
        # Record healthy performance with some variation
        for i in range(10):
            response_time = 1.0 + i * 0.2  # 1.0 to 2.8 seconds
            success = i < 9  # 1 failure
            monitor.record_request("gemini", response_time, success)
        
        stats = monitor.get_provider_stats("gemini")
        assert stats["status"] in ["excellent", "good", "degraded"]  # Based on recent performance

    def test_get_provider_status_degraded(self):
        """Test provider status determination for degraded performance"""
        monitor = ProviderPerformanceMonitor()
        
        # Record degraded performance
        for i in range(10):
            response_time = 3.0 + i * 0.5  # 3.0 to 7.5 seconds
            success = i < 7  # 3 failures
            monitor.record_request("groq", response_time, success)
        
        stats = monitor.get_provider_stats("groq")
        assert stats["status"] in ["degraded", "poor"]  # Based on recent performance

    def test_get_provider_status_failed(self):
        """Test provider status determination for failed performance"""
        monitor = ProviderPerformanceMonitor()
        
        # Record mostly failed requests
        for i in range(10):
            success = i < 2  # Only 2 successes
            monitor.record_request("test_provider", 5.0, success, "error")
        
        stats = monitor.get_provider_stats("test_provider")
        assert stats["status"] == "poor"  # Low success rate

    def test_get_optimal_provider_single_provider(self):
        """Test optimal provider selection with single provider"""
        monitor = ProviderPerformanceMonitor()
        
        monitor.record_request("ollama", 1.0, True)
        
        optimal = monitor.get_best_provider(["ollama"])
        assert optimal == "ollama"

    def test_get_optimal_provider_multiple_providers(self):
        """Test optimal provider selection with multiple providers"""
        monitor = ProviderPerformanceMonitor()
        
        # Record different performance for each provider
        monitor.record_request("ollama", 1.0, True)
        monitor.record_request("gemini", 0.8, True)
        monitor.record_request("groq", 2.5, True)
        
        optimal = monitor.get_best_provider(["ollama", "gemini", "groq"])
        assert optimal == "gemini"  # Fastest response time

    def test_get_optimal_provider_with_failures(self):
        """Test optimal provider selection considering failures"""
        monitor = ProviderPerformanceMonitor()
        
        # One provider has failures, another doesn't
        monitor.record_request("ollama", 1.0, True)
        monitor.record_request("ollama", 1.2, True)
        
        monitor.record_request("groq", 0.5, True)  # Faster but has failures
        monitor.record_request("groq", 0.7, False, "timeout")
        monitor.record_request("groq", 0.6, False, "rate_limit")
        
        optimal = monitor.get_best_provider(["ollama", "groq"])
        assert optimal == "ollama"  # Should choose reliable over faster with failures

    def test_get_optimal_provider_no_data(self):
        """Test optimal provider selection with no performance data"""
        monitor = ProviderPerformanceMonitor()
        
        optimal = monitor.get_best_provider(["ollama", "gemini"])
        assert optimal in ["ollama", "gemini"]  # Should return one of the available providers

    def test_get_optimal_provider_unavailable(self):
        """Test optimal provider selection when requested provider unavailable"""
        monitor = ProviderPerformanceMonitor()
        
        monitor.record_request("ollama", 1.0, True)
        
        optimal = monitor.get_best_provider(["nonexistent"])
        assert optimal == "nonexistent"  # Returns first available when no data

    def test_get_health_summary(self):
        """Test getting overall health summary"""
        monitor = ProviderPerformanceMonitor()
        
        # Add providers with different statuses
        monitor.record_request("ollama", 0.8, True)  # Excellent
        monitor.record_request("gemini", 1.5, True)  # Healthy
        monitor.record_request("groq", 5.0, False, "timeout")  # Failed
        
        health = monitor.get_health_summary()
        
        assert health["total_requests"] == 3
        assert "ollama" in health["healthy_providers"]
        assert "gemini" in health["healthy_providers"]
        assert "groq" in health["failed_providers"]
        assert len(health["degraded_providers"]) == 0
        assert health["overall_status"] == "degraded"  # One failed provider

    def test_get_health_summary_empty(self):
        """Test health summary with no data"""
        monitor = ProviderPerformanceMonitor()
        
        health = monitor.get_health_summary()
        
        assert health["total_requests"] == 0
        assert len(health["healthy_providers"]) == 0
        assert len(health["degraded_providers"]) == 0
        assert len(health["failed_providers"]) == 0
        assert health["overall_status"] == "unknown"

    def test_max_history_enforcement(self):
        """Test that performance data respects max_history limit"""
        monitor = ProviderPerformanceMonitor(max_history=5)
        
        # Add more requests than max_history
        for i in range(10):
            monitor.record_request("test_provider", i * 0.1, True)
        
        # Should only keep the most recent 5 requests
        assert len(monitor.performance_data["test_provider"]) == 5
        
        # Verify the most recent requests are kept
        requests = monitor.performance_data["test_provider"]
        response_times = [req["response_time"] for req in requests]
        # Check that we have the right values (allowing for floating point precision)
        assert len(response_times) == 5
        assert response_times[0] == 0.5
        assert response_times[-1] == 0.9
        assert all(0.5 <= rt <= 0.9 for rt in response_times)

    def test_cleanup_old_data(self):
        """Test cleanup of old performance data"""
        monitor = ProviderPerformanceMonitor()
        
        # Add requests with different timestamps
        old_time = datetime.now() - timedelta(hours=25)  # Older than 24 hours
        recent_time = datetime.now() - timedelta(hours=1)
        
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.now()
            
            # Manually add old data
            monitor.performance_data["test_provider"] = [
                {"timestamp": old_time, "response_time": 1.0, "success": True, "error": None},
                {"timestamp": recent_time, "response_time": 0.5, "success": True, "error": None}
            ]
            
            # Clean up data older than 24 hours
            monitor.cleanup_old_data()
            
            # Should only keep recent data
            assert len(monitor.performance_data["test_provider"]) == 1
            assert monitor.performance_data["test_provider"][0]["response_time"] == 0.5

class TestGlobalFunctions:
    """Test global performance monitoring functions"""

    @patch('backend.performance_monitor.performance_monitor')
    def test_record_provider_performance(self, mock_monitor):
        """Test global record_provider_performance function"""
        record_provider_performance("groq", 3.0, False, "timeout")
        
        mock_monitor.record_request.assert_called_once_with("groq", 3.0, False, "timeout")

    @patch('backend.performance_monitor.performance_monitor')
    def test_record_provider_performance_with_error(self, mock_monitor):
        """Test global record_provider_performance function with error"""
        record_provider_performance("groq", 3.0, False, "timeout")
        
        mock_monitor.record_request.assert_called_once_with("groq", 3.0, False, "timeout")

    @patch('backend.performance_monitor.performance_monitor')
    def test_get_optimal_provider_global(self, mock_monitor):
        """Test global get_optimal_provider function"""
        mock_monitor.get_best_provider.return_value = "gemini"
        
        result = get_optimal_provider(["ollama", "gemini", "groq"])
        
        assert result == "gemini"
        mock_monitor.get_best_provider.assert_called_once_with(["ollama", "gemini", "groq"])

    @patch('backend.performance_monitor.performance_monitor')
    def test_get_provider_health_global(self, mock_monitor):
        """Test global get_provider_health function"""
        mock_monitor.get_health_summary.return_value = {
            "total_requests": 10,
            "healthy_providers": ["ollama"],
            "failed_providers": []
        }
        
        result = get_provider_health()
        
        assert result["total_requests"] == 10
        assert "ollama" in result["healthy_providers"]
        mock_monitor.get_health_summary.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

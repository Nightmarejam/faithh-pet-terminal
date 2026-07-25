#!/usr/bin/env python3
"""
Unit Tests for Response Cache
Tests cache key generation, TTL enforcement, LRU eviction, and statistics
"""

import os
import sys
import pytest
import time
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Ensure backend is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.response_cache import (
    ResponseCache,
    get_cached_response,
    cache_response,
    get_cache_stats,
    cleanup_cache
)

class TestResponseCache:
    """Test response caching functionality"""

    def test_cache_initialization(self):
        """Test cache initializes with correct parameters"""
        cache = ResponseCache(max_size=100, ttl_seconds=300)
        
        assert cache.max_size == 100
        assert cache.ttl_seconds == 300
        assert len(cache.cache) == 0

    def test_generate_key_consistency(self):
        """Test cache key generation is consistent"""
        cache = ResponseCache()
        
        query = "test query"
        provider = "ollama"
        model = "qwen25-grounded"
        
        key1 = cache._generate_key(query, provider, model)
        key2 = cache._generate_key(query, provider, model)
        
        assert key1 == key2
        assert len(key1) == 32  # MD5 hash length

    def test_generate_key_uniqueness(self):
        """Test cache key generation is unique for different inputs"""
        cache = ResponseCache()
        
        key1 = cache._generate_key("query1", "ollama", "model1")
        key2 = cache._generate_key("query2", "ollama", "model1")
        key3 = cache._generate_key("query1", "gemini", "model1")
        key4 = cache._generate_key("query1", "ollama", "model2")
        
        assert key1 != key2  # Different query
        assert key1 != key3  # Different provider
        assert key1 != key4  # Different model

    def test_cache_miss_empty(self):
        """Test cache miss when cache is empty"""
        cache = ResponseCache()
        
        result = cache.get("test query", "ollama", "qwen25-grounded")
        
        assert result is None

    def test_cache_miss_no_entry(self):
        """Test cache miss when no matching entry exists"""
        cache = ResponseCache()
        
        # Add one entry
        cache.set("query1", "ollama", "model1", {"response": "test1"})
        
        # Try to get different entry
        result = cache.get("query2", "ollama", "model1")
        
        assert result is None

    def test_cache_hit_valid(self):
        """Test successful cache hit with valid TTL"""
        cache = ResponseCache(ttl_seconds=300)
        
        response_data = {"response": "test response", "timestamp": datetime.now().isoformat()}
        
        # Store response
        cache.set("test query", "ollama", "qwen25-grounded", response_data)
        
        # Retrieve response
        result = cache.get("test query", "ollama", "qwen25-grounded")
        
        assert result is not None
        assert result["response"] == "test response"

    def test_cache_hit_expired(self):
        """Test cache miss when entry is expired"""
        cache = ResponseCache(ttl_seconds=1)  # 1 second TTL
        
        response_data = {"response": "test response"}
        
        # Store response
        cache.set("test query", "ollama", "qwen25-grounded", response_data)
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Try to retrieve expired response
        result = cache.get("test query", "ollama", "qwen25-grounded")
        
        assert result is None
        assert len(cache.cache) == 0  # Expired entry should be removed

    def test_cache_set_basic(self):
        """Test basic cache set operation"""
        cache = ResponseCache()
        
        response_data = {"response": "test", "model": "test_model"}
        
        cache.set("query", "provider", "model", response_data)
        
        assert len(cache.cache) == 1
        
        # Verify cache entry structure
        for entry in cache.cache.values():
            assert "response" in entry
            assert "timestamp" in entry
            assert "last_access" in entry
            assert "access_count" in entry
            assert entry["response"] == response_data
            assert entry["access_count"] == 1

    def test_cache_set_updates_access_time(self):
        """Test that cache set updates access time and count"""
        cache = ResponseCache()
        
        # Set initial entry
        cache.set("query", "provider", "model", {"response": "test"})
        
        initial_time = cache.cache[cache._generate_key("query", "provider", "model")]["last_access"]
        initial_count = cache.cache[cache._generate_key("query", "provider", "model")]["access_count"]
        
        # Wait a bit to ensure different timestamp
        time.sleep(0.01)
        
        # Update same entry (different response data)
        new_response_data = {"response": "updated"}
        cache.set("query", "provider", "model", new_response_data)
        
        # Should have updated the entry but not access count
        updated_entry = cache.cache[cache._generate_key("query", "provider", "model")]
        assert updated_entry["response"] == new_response_data
        assert updated_entry["last_access"] > initial_time
        assert updated_entry["access_count"] == initial_count

    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full"""
        cache = ResponseCache(max_size=3)  # Small cache for testing
        
        # Fill cache to capacity
        for i in range(3):
            cache.set(f"query{i}", "provider", "model", {"response": f"response{i}"})
        
        assert len(cache.cache) == 3
        
        # Access first entry to make it most recently used
        cache.get("query0", "provider", "model")
        
        # Add one more entry (should evict least recently used)
        cache.set("query3", "provider", "model", {"response": "response3"})
        
        assert len(cache.cache) == 3
        
        # query1 should be evicted (least recently used)
        assert cache.get("query0", "provider", "model") is not None  # Was accessed
        assert cache.get("query1", "provider", "model") is None  # Should be evicted
        assert cache.get("query2", "provider", "model") is not None  # Still there
        assert cache.get("query3", "provider", "model") is not None  # New entry

    def test_cache_lru_eviction_order(self):
        """Test LRU eviction removes the oldest accessed entry"""
        cache = ResponseCache(max_size=2)
        
        # Add two entries
        cache.set("query1", "provider", "model", {"response": "1"})
        cache.set("query2", "provider", "model", {"response": "2"})
        
        # Access query1 to make it most recently used
        cache.get("query1", "provider", "model")
        
        # Add third entry (should evict query2)
        cache.set("query3", "provider", "model", {"response": "3"})
        
        # Verify query2 was evicted, query1 remains
        assert cache.get("query1", "provider", "model") is not None
        assert cache.get("query2", "provider", "model") is None
        assert cache.get("query3", "provider", "model") is not None

    def test_get_cache_stats_empty(self):
        """Test cache statistics when cache is empty"""
        cache = ResponseCache()
        
        stats = cache.get_stats()
        
        assert stats["total_items"] == 0
        assert stats["hit_rate"] == 0.0
        assert stats["oldest_item"] is None
        assert stats["newest_item"] is None
        assert stats["total_accesses"] == 0
        # Note: max_size and ttl_seconds are only included when cache has items

    def test_get_cache_stats_with_data(self):
        """Test cache statistics with cached data"""
        cache = ResponseCache()
        
        # Add some entries with different access patterns
        cache.set("query1", "provider", "model", {"response": "1"})
        cache.set("query2", "provider", "model", {"response": "2"})
        
        # Access some entries multiple times
        cache.get("query1", "provider", "model")
        cache.get("query1", "provider", "model")
        cache.get("query2", "provider", "model")
        
        stats = cache.get_stats()
        
        assert stats["total_items"] == 2
        assert stats["total_accesses"] == 5  # 2 sets + 3 gets
        assert stats["oldest_item"] is not None
        assert stats["newest_item"] is not None
        assert stats["hit_rate"] > 0.0
        assert stats["max_size"] == cache.max_size
        assert stats["ttl_seconds"] == cache.ttl_seconds

    def test_get_cache_stats_hit_rate_calculation(self):
        """Test hit rate calculation in cache statistics"""
        cache = ResponseCache()
        
        # Add entry
        cache.set("query", "provider", "model", {"response": "test"})
        
        # Access multiple times
        for i in range(9):  # 9 gets + 1 set = 10 total accesses
            cache.get("query", "provider", "model")
        
        stats = cache.get_stats()
        
        # Hit rate is based on avg_accesses / 10.0, capped at 1.0
        # avg_accesses = 10 / 1 = 10, so hit_rate = min(10/10, 1.0) = 1.0
        assert stats["total_accesses"] == 10
        assert stats["hit_rate"] == 1.0

    def test_cache_clear(self):
        """Test clearing the cache"""
        cache = ResponseCache()
        
        # Add some entries
        cache.set("query1", "provider", "model", {"response": "1"})
        cache.set("query2", "provider", "model", {"response": "2"})
        
        assert len(cache.cache) == 2
        
        # Clear cache
        cache.clear()
        
        assert len(cache.cache) == 0

    def test_cleanup_expired_entries(self):
        """Test cleanup of expired entries"""
        cache = ResponseCache(ttl_seconds=1)
        
        # Add entries
        cache.set("query1", "provider", "model", {"response": "1"})
        cache.set("query2", "provider", "model", {"response": "2"})
        
        assert len(cache.cache) == 2
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Cleanup expired entries
        expired_count = cache.cleanup_expired()
        
        assert expired_count == 2
        assert len(cache.cache) == 0

    def test_cleanup_mixed_expired_valid(self):
        """Test cleanup with mix of expired and valid entries"""
        cache = ResponseCache(ttl_seconds=2)
        
        # Add first entry
        cache.set("query1", "provider", "model", {"response": "1"})
        
        # Wait a bit
        time.sleep(1)
        
        # Add second entry (newer)
        cache.set("query2", "provider", "model", {"response": "2"})
        
        # Wait for first to expire but not second
        time.sleep(1.1)
        
        # Cleanup expired entries
        expired_count = cache.cleanup_expired()
        
        assert expired_count == 1  # Only first entry expired
        assert len(cache.cache) == 1
        assert cache.get("query2", "provider", "model") is not None

    def test_cache_key_collision_handling(self):
        """Test handling of potential cache key collisions"""
        cache = ResponseCache()
        
        # These should generate different keys
        response1 = {"response": "test1"}
        response2 = {"response": "test2"}
        
        cache.set("queryA", "providerA", "modelA", response1)
        cache.set("queryB", "providerB", "modelB", response2)
        
        # Verify both are stored separately
        assert len(cache.cache) == 2
        assert cache.get("queryA", "providerA", "modelA") == response1
        assert cache.get("queryB", "providerB", "modelB") == response2

    def test_cache_concurrent_access_simulation(self):
        """Test cache behavior under simulated concurrent access"""
        cache = ResponseCache()
        
        # Simulate multiple threads accessing same cache entry
        response_data = {"response": "shared_response"}
        
        # Set entry
        cache.set("shared_query", "provider", "model", response_data)
        
        # Multiple "concurrent" gets
        results = []
        for i in range(5):
            result = cache.get("shared_query", "provider", "model")
            results.append(result)
        
        # All should return the same result
        assert all(result == response_data for result in results)
        
        # Access count should reflect all accesses
        key = cache._generate_key("shared_query", "provider", "model")
        assert cache.cache[key]["access_count"] >= 5

class TestGlobalFunctions:
    """Test global cache functions"""

    @patch('backend.response_cache.response_cache')
    def test_get_cached_response_global(self, mock_cache):
        """Test global get_cached_response function"""
        mock_cache.get.return_value = {"response": "test"}
        
        result = get_cached_response("query", "provider", "model")
        
        assert result == {"response": "test"}
        mock_cache.get.assert_called_once_with("query", "provider", "model")

    @patch('backend.response_cache.response_cache')
    def test_cache_response_global(self, mock_cache):
        """Test global cache_response function"""
        response_data = {"response": "test"}
        cache_response("query", "provider", "model", response_data)
        
        mock_cache.set.assert_called_once_with("query", "provider", "model", response_data)

    @patch('backend.response_cache.response_cache')
    def test_get_cache_stats_global(self, mock_cache):
        """Test global get_cache_stats function"""
        mock_cache.get_stats.return_value = {
            "total_items": 5,
            "hit_rate": 0.8
        }
        
        result = get_cache_stats()
        
        assert result["total_items"] == 5
        assert result["hit_rate"] == 0.8
        mock_cache.get_stats.assert_called_once()

    @patch('backend.response_cache.response_cache')
    def test_cleanup_cache_global(self, mock_cache):
        """Test global cleanup_cache function"""
        mock_cache.cleanup_expired.return_value = 3
        
        result = cleanup_cache()
        
        assert result == 3
        mock_cache.cleanup_expired.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

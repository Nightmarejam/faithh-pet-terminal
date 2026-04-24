"""
Simple response caching for FAITHH backend
Caches identical queries to improve response times
"""

import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from threading import Lock

class ResponseCache:
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = Lock()
        
    def _generate_key(self, query: str, provider: str, model: str) -> str:
        """Generate a cache key for the query"""
        # Include query, provider, and model in the key
        key_data = f"{query}:{provider}:{model}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, query: str, provider: str, model: str) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired"""
        key = self._generate_key(query, provider, model)
        
        with self.lock:
            if key not in self.cache:
                return None
            
            cached_item = self.cache[key]
            
            # Check TTL
            if datetime.now() - cached_item['timestamp'] > timedelta(seconds=self.ttl_seconds):
                del self.cache[key]
                return None
            
            # Update access time for LRU
            cached_item['last_access'] = datetime.now()
            cached_item['access_count'] += 1
            
            return cached_item['response']
    
    def set(self, query: str, provider: str, model: str, response: Dict[str, Any]):
        """Cache a response"""
        key = self._generate_key(query, provider, model)
        
        with self.lock:
            # Remove oldest item if cache is full
            if len(self.cache) >= self.max_size:
                oldest_key = min(
                    self.cache.keys(),
                    key=lambda k: self.cache[k]['last_access']
                )
                del self.cache[oldest_key]
            
            # Store new response
            self.cache[key] = {
                'response': response,
                'timestamp': datetime.now(),
                'last_access': datetime.now(),
                'access_count': 1,
                'query': query,
                'provider': provider,
                'model': model
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_items = len(self.cache)
            if total_items == 0:
                return {
                    'total_items': 0,
                    'hit_rate': 0.0,
                    'oldest_item': None,
                    'newest_item': None,
                    'total_accesses': 0
                }
            
            oldest_time = min(item['timestamp'] for item in self.cache.values())
            newest_time = max(item['timestamp'] for item in self.cache.values())
            total_accesses = sum(item['access_count'] for item in self.cache.values())
            
            # Calculate hit rate (approximate)
            # This is simplified - in production you'd track hits vs misses separately
            avg_accesses = total_accesses / total_items if total_items > 0 else 0
            hit_rate = min(avg_accesses / 10.0, 1.0)  # Rough estimate
            
            return {
                'total_items': total_items,
                'hit_rate': hit_rate,
                'oldest_item': oldest_time.isoformat(),
                'newest_item': newest_time.isoformat(),
                'total_accesses': total_accesses,
                'max_size': self.max_size,
                'ttl_seconds': self.ttl_seconds
            }
    
    def clear(self):
        """Clear the cache"""
        with self.lock:
            self.cache.clear()
    
    def cleanup_expired(self):
        """Remove expired items from cache"""
        current_time = datetime.now()
        expired_keys = []
        
        with self.lock:
            for key, item in self.cache.items():
                if current_time - item['timestamp'] > timedelta(seconds=self.ttl_seconds):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
        
        return len(expired_keys)

# Global cache instance
response_cache = ResponseCache(max_size=500, ttl_seconds=300)  # 5 minutes TTL

def get_cached_response(query: str, provider: str, model: str) -> Optional[Dict[str, Any]]:
    """Get cached response if available"""
    return response_cache.get(query, provider, model)

def cache_response(query: str, provider: str, model: str, response: Dict[str, Any]):
    """Cache a response"""
    response_cache.set(query, provider, model, response)

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    return response_cache.get_stats()

def cleanup_cache() -> int:
    """Clean up expired cache entries"""
    return response_cache.cleanup_expired()

"""
FAITHH Response Caching System

Provides intelligent response caching to improve performance
and reduce load on backend services.

Priority: Phase 4.1 - Performance Foundation
"""

import time
import hashlib
import json
import pickle
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from threading import RLock
import re

class CacheEntry:
    """Single cache entry with metadata"""
    
    def __init__(self, key: str, value: Any, ttl_seconds: int = 3600):
        self.key = key
        self.value = value
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(seconds=ttl_seconds)
        self.access_count = 0
        self.last_accessed = self.created_at
        self.size_bytes = len(pickle.dumps(value))
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return datetime.now() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if cache entry is valid (not expired)"""
        return not self.is_expired()
    
    def access(self) -> Any:
        """Access the cache entry"""
        self.access_count += 1
        self.last_accessed = datetime.now()
        return self.value
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for monitoring"""
        return {
            'key': self.key,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat(),
            'size_bytes': self.size_bytes,
            'is_expired': self.is_expired()
        }

class ResponseCache:
    """Intelligent response caching system"""
    
    def __init__(self, max_size_mb: int = 100, default_ttl: int = 3600):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.lock = RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_requests': 0
        }
        
        # Cache configuration
        self.cache_config = {
            'query_cache_ttl': 3600,      # 1 hour for query responses
            'static_cache_ttl': 86400,    # 24 hours for static content
            'session_cache_ttl': 1800,    # 30 minutes for session data
            'rag_cache_ttl': 7200,        # 2 hours for RAG results
            'max_key_length': 255
        }
        
        # Patterns for cache invalidation
        self.invalidation_patterns = [
            r'faithh_memory\.json',
            r'decisions_log\.json',
            r'project_states\.json',
            r'scaffolding_state\.json'
        ]
    
    def _generate_cache_key(self, query: str, session_id: str = None, 
                           model: str = None, use_rag: bool = True,
                           additional_context: Dict = None) -> str:
        """Generate cache key for request"""
        # Normalize query
        normalized_query = re.sub(r'\s+', ' ', query.strip().lower())
        
        # Build key components
        key_components = [
            normalized_query,
            model or 'default',
            str(use_rag),
            session_id or 'no_session'
        ]
        
        # Add additional context if provided
        if additional_context:
            context_str = json.dumps(additional_context, sort_keys=True)
            key_components.append(context_str)
        
        # Create key string
        key_string = '|'.join(key_components)
        
        # Hash to ensure consistent length
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()
        
        # Truncate if too long
        if len(key_hash) > self.cache_config['max_key_length']:
            key_hash = key_hash[:self.cache_config['max_key_length']]
        
        return f"resp_{key_hash}"
    
    def _determine_ttl(self, query: str, use_rag: bool = True, 
                       response_type: str = 'query') -> int:
        """Determine TTL based on query characteristics"""
        if response_type == 'static':
            return self.cache_config['static_cache_ttl']
        elif response_type == 'session':
            return self.cache_config['session_cache_ttl']
        elif use_rag:
            return self.cache_config['rag_cache_ttl']
        else:
            return self.cache_config['query_cache_ttl']
    
    def _should_cache(self, query: str, response: Dict) -> bool:
        """Determine if response should be cached"""
        # Don't cache empty or error responses
        if not response or not isinstance(response, dict):
            return False
        
        if not response.get('success', False):
            return False
        
        # Don't cache very short responses (likely errors or simple acknowledgments)
        response_text = response.get('response', '')
        if len(response_text.strip()) < 10:
            return False
        
        # Don't cache responses with high variability
        high_variance_indicators = [
            'current time', 'right now', 'today is', 'as of',
            'currently', 'at the moment'
        ]
        
        response_lower = response_text.lower()
        if any(indicator in response_lower for indicator in high_variance_indicators):
            return False
        
        # Don't cache if response indicates real-time data
        real_time_indicators = [
            'live', 'real-time', 'current status', 'latest',
            'up-to-date', 'refreshed'
        ]
        
        if any(indicator in response_lower for indicator in real_time_indicators):
            return False
        
        return True
    
    def get(self, query: str, session_id: str = None, 
           model: str = None, use_rag: bool = True,
           additional_context: Dict = None) -> Optional[Dict]:
        """Get cached response"""
        with self.lock:
            self.stats['total_requests'] += 1
            
            cache_key = self._generate_cache_key(
                query, session_id, model, use_rag, additional_context
            )
            
            if cache_key not in self.cache:
                self.stats['misses'] += 1
                return None
            
            entry = self.cache[cache_key]
            
            # Check if expired
            if entry.is_expired():
                del self.cache[cache_key]
                self.stats['misses'] += 1
                return None
            
            # Access the entry
            self.stats['hits'] += 1
            return entry.access()
    
    def set(self, query: str, response: Dict, session_id: str = None,
           model: str = None, use_rag: bool = True,
           additional_context: Dict = None, ttl: int = None) -> bool:
        """Cache a response"""
        with self.lock:
            # Check if response should be cached
            if not self._should_cache(query, response):
                return False
            
            cache_key = self._generate_cache_key(
                query, session_id, model, use_rag, additional_context
            )
            
            # Determine TTL
            if ttl is None:
                ttl = self._determine_ttl(query, use_rag)
            
            # Create cache entry
            entry = CacheEntry(cache_key, response, ttl)
            
            # Check if eviction is needed
            self._evict_if_needed(entry.size_bytes)
            
            # Store entry
            self.cache[cache_key] = entry
            
            return True
    
    def invalidate(self, pattern: str = None, session_id: str = None) -> int:
        """Invalidate cache entries"""
        with self.lock:
            invalidated_count = 0
            
            if pattern:
                # Invalidate by pattern
                keys_to_remove = []
                for key in self.cache:
                    if re.search(pattern, key, re.IGNORECASE):
                        keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    del self.cache[key]
                    invalidated_count += 1
            
            elif session_id:
                # Invalidate by session
                keys_to_remove = []
                for key in self.cache:
                    if f"session_{session_id}" in key:
                        keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    del self.cache[key]
                    invalidated_count += 1
            
            else:
                # Clear all cache
                invalidated_count = len(self.cache)
                self.cache.clear()
            
            return invalidated_count
    
    def invalidate_on_data_change(self, changed_file: str) -> int:
        """Invalidate cache when data files change"""
        invalidated_count = 0
        
        for pattern in self.invalidation_patterns:
            if re.search(pattern, changed_file, re.IGNORECASE):
                invalidated_count += self.invalidate(pattern)
        
        return invalidated_count
    
    def _evict_if_needed(self, new_entry_size: int):
        """Evict entries if cache is full"""
        current_size = sum(entry.size_bytes for entry in self.cache.values())
        
        if current_size + new_entry_size > self.max_size_bytes:
            # Evict least recently used (LRU) entries
            entries_sorted = sorted(
                self.cache.items(),
                key=lambda x: x[1].last_accessed
            )
            
            bytes_to_free = new_entry_size
            for key, entry in entries_sorted:
                if bytes_to_free <= 0:
                    break
                
                del self.cache[key]
                bytes_to_free -= entry.size_bytes
                self.stats['evictions'] += 1
    
    def cleanup_expired(self) -> int:
        """Clean up expired entries"""
        with self.lock:
            expired_keys = []
            
            for key, entry in self.cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with self.lock:
            hit_rate = 0.0
            if self.stats['total_requests'] > 0:
                hit_rate = (self.stats['hits'] / self.stats['total_requests']) * 100
            
            current_size = sum(entry.size_bytes for entry in self.cache.values())
            
            return {
                'entries': len(self.cache),
                'size_bytes': current_size,
                'size_mb': current_size / (1024 * 1024),
                'max_size_mb': self.max_size_bytes / (1024 * 1024),
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'evictions': self.stats['evictions'],
                'total_requests': self.stats['total_requests'],
                'hit_rate_percent': hit_rate,
                'utilization_percent': (current_size / self.max_size_bytes) * 100
            }
    
    def get_cache_info(self) -> List[Dict]:
        """Get detailed cache entry information"""
        with self.lock:
            return [entry.to_dict() for entry in self.cache.values()]
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.stats = {
                'hits': 0,
                'misses': 0,
                'evictions': 0,
                'total_requests': 0
            }

# Flask integration
class CacheMiddleware:
    """Middleware for Flask to handle caching automatically"""
    
    def __init__(self, cache_instance: ResponseCache):
        self.cache = cache_instance
    
    def get_cache_key_from_request(self, request_data: Dict) -> str:
        """Extract cache key from Flask request"""
        query = request_data.get('message', '')
        session_id = request_data.get('session_id')
        model = request_data.get('model')
        use_rag = request_data.get('use_rag', True)
        
        return self.cache._generate_cache_key(query, session_id, model, use_rag)
    
    def should_cache_request(self, request_data: Dict, response_data: Dict) -> bool:
        """Determine if request/response should be cached"""
        # Only cache POST requests to /api/chat
        if not request_data.get('message'):
            return False
        
        return self.cache._should_cache(request_data.get('message', ''), response_data)
    
    def cache_response(self, request_data: Dict, response_data: Dict):
        """Cache a response"""
        if self.should_cache_request(request_data, response_data):
            query = request_data.get('message', '')
            session_id = request_data.get('session_id')
            model = request_data.get('model')
            use_rag = request_data.get('use_rag', True)
            
            self.cache.set(query, response_data, session_id, model, use_rag)
    
    def get_cached_response(self, request_data: Dict) -> Optional[Dict]:
        """Get cached response for request"""
        query = request_data.get('message', '')
        session_id = request_data.get('session_id')
        model = request_data.get('model')
        use_rag = request_data.get('use_rag', True)
        
        return self.cache.get(query, session_id, model, use_rag)

# Global cache instance
response_cache = ResponseCache(max_size_mb=100, default_ttl=3600)
cache_middleware = CacheMiddleware(response_cache)

# Decorator for Flask routes
def cached_response(ttl: int = None):
    """Decorator to cache Flask route responses"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            from flask import request, g
            
            # Try to get from cache
            if request.method == 'POST':
                request_data = request.get_json() or {}
                cached = cache_middleware.get_cached_response(request_data)
                
                if cached:
                    # Add cache header
                    g.from_cache = True
                    return cached
            
            # Execute function
            response = func(*args, **kwargs)
            
            # Cache the response
            if request.method == 'POST' and hasattr(response, 'get_json'):
                try:
                    request_data = request.get_json() or {}
                    response_data = response.get_json() if hasattr(response, 'get_json') else response
                    
                    if isinstance(response_data, dict):
                        cache_middleware.cache_response(request_data, response_data)
                except Exception:
                    pass  # Don't let caching errors break the request
            
            return response
        
        return wrapper
    return decorator

# Background cleanup
def start_cache_cleanup():
    """Start background cache cleanup"""
    import threading
    import time
    
    def cleanup_loop():
        while True:
            try:
                expired_count = response_cache.cleanup_expired()
                if expired_count > 0:
                    print(f"🧹 Cleaned up {expired_count} expired cache entries")
                
                time.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                print(f"Cache cleanup error: {e}")
                time.sleep(300)
    
    cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
    cleanup_thread.start()
    print("🧹 Cache cleanup thread started")

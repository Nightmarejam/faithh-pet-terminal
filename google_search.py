#!/usr/bin/env python3
"""
Google Search API Integration
Secure implementation with rate limiting and fallback mechanisms
"""

import os
import time
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
try:
    from secure_logging.secure_config import StructuredLogger
    from security.key_validator import APIKeyValidator
except ImportError:
    # Fallback if security modules not available
    import logging
    class StructuredLogger:
        def __init__(self, name, log_file=None):
            self.logger = logging.getLogger(name)
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)
            if log_file:
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
                self.logger.addHandler(file_handler)
        
        def log_model_call(self, provider, model, user_message, response_time, success):
            self.logger.info(f"Model call - Provider: {provider}, Model: {model}, Response time: {response_time:.2f}s, Success: {success}")
        
        def log_error(self, error_type, message, context=None):
            context_str = f", Context: {context}" if context else ""
            self.logger.error(f"Error - Type: {error_type}, Message: {message}{context_str}")
        
        def log_security_event(self, event_type, details):
            self.logger.warning(f"Security Event - Type: {event_type}, Details: {details}")
    
    class APIKeyValidator:
        def validate_key_format(self, key_name, key_value):
            # Basic validation without regex
            if not key_value:
                return False
            if key_name == 'GOOGLE_SEARCH_API_KEY':
                return len(key_value) > 20
            return True

class GoogleSearchAPI:
    """Secure Google Search API with rate limiting and fallbacks"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        # Initialize logging and security
        self.logger = StructuredLogger('google_search', 'logs/google_search.log')
        self.validator = APIKeyValidator()
        
        # Rate limiting: 100 queries/day maximum
        self.daily_limit = 100
        self.requests_today = 0
        self.last_reset = datetime.utcnow().date()
        
        # Validate API key format
        if self.api_key and not self.validator.validate_key_format('GOOGLE_SEARCH_API_KEY', self.api_key):
            self.logger.log_error('validation', 'Invalid Google Search API key format')
            self.api_key = None
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        today = datetime.utcnow().date()
        
        # Reset counter if new day
        if today != self.last_reset:
            self.requests_today = 0
            self.last_reset = today
        
        if self.requests_today >= self.daily_limit:
            self.logger.log_security_event('rate_limit_exceeded', {
                'requests_today': self.requests_today,
                'daily_limit': self.daily_limit
            })
            return False
        
        return True
    
    def _log_api_call(self, success: bool, query: str, response_time: float, error: str = None):
        """Log API call for monitoring"""
        self.logger.log_model_call(
            provider='google_search',
            model='custom_search',
            user_message=query[:100],  # Truncate for privacy
            response_time=response_time,
            success=success
        )
        
        if not success and error:
            self.logger.log_error('api_error', error, {'query': query[:100]})
    
    def search(self, query: str, num_results: int = 5) -> Dict:
        """Perform web search with rate limiting and error handling"""
        start_time = time.time()
        
        # Validate inputs
        if not query or not query.strip():
            error = "Empty query provided"
            self._log_api_call(False, query, time.time() - start_time, error)
            return {'error': error, 'results': []}
        
        # Check API key
        if not self.api_key:
            error = "Google Search API key not configured"
            self._log_api_call(False, query, time.time() - start_time, error)
            return {'error': error, 'results': []}
        
        # Check rate limit
        if not self._check_rate_limit():
            error = "Daily quota exceeded"
            self._log_api_call(False, query, time.time() - start_time, error)
            return {'error': error, 'results': [], 'fallback_used': True}
        
        # Limit number of results
        num_results = min(max(num_results, 1), 10)  # API limit is 10
        
        try:
            # Make API request
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': num_results
            }
            
            response = requests.get(
                self.base_url, 
                params=params, 
                timeout=10
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.requests_today += 1
                
                # Format results
                results = []
                if 'items' in data:
                    for item in data['items']:
                        results.append({
                            'title': item.get('title', ''),
                            'link': item.get('link', ''),
                            'snippet': item.get('snippet', ''),
                            'displayLink': item.get('displayLink', '')
                        })
                
                self._log_api_call(True, query, response_time)
                
                return {
                    'results': results,
                    'total_results': len(results),
                    'search_time': response_time,
                    'requests_remaining': self.daily_limit - self.requests_today
                }
            
            else:
                error_msg = f"API error: {response.status_code} - {response.text}"
                self._log_api_call(False, query, response_time, error_msg)
                return {'error': error_msg, 'results': []}
        
        except requests.Timeout:
            error = "Request timeout"
            self._log_api_call(False, query, time.time() - start_time, error)
            return {'error': error, 'results': [], 'fallback_used': True}
        
        except requests.RequestException as e:
            error = f"Network error: {str(e)}"
            self._log_api_call(False, query, time.time() - start_time, error)
            return {'error': error, 'results': [], 'fallback_used': True}
        
        except Exception as e:
            error = f"Unexpected error: {str(e)}"
            self._log_api_call(False, query, time.time() - start_time, error)
            return {'error': error, 'results': []}
    
    def get_usage_stats(self) -> Dict:
        """Get current usage statistics"""
        return {
            'requests_today': self.requests_today,
            'daily_limit': self.daily_limit,
            'requests_remaining': max(0, self.daily_limit - self.requests_today),
            'last_reset': self.last_reset.isoformat(),
            'api_configured': bool(self.api_key),
            'search_engine_configured': bool(self.search_engine_id)
        }
    
    def fallback_search(self, query: str) -> Dict:
        """Local fallback search when API is unavailable"""
        # Simple local search implementation
        # In a real implementation, this could search local documents, use a different API, etc.
        
        self.logger.log_security_event('fallback_search_used', {
            'query': query[:100],
            'reason': 'api_unavailable_or_quota_exceeded'
        })
        
        return {
            'results': [{
                'title': 'Local Search Unavailable',
                'link': '#',
                'snippet': f'Google Search API is currently unavailable. Your query "{query}" was not processed.',
                'displayLink': 'local'
            }],
            'total_results': 1,
            'fallback_used': True,
            'message': 'Using local fallback - Google Search API unavailable'
        }

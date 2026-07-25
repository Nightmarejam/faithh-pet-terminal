"""
FAITHH Security Middleware

Provides rate limiting, input validation, and request protection
for the FAITHH backend system.

Priority: Phase 4.1 - Security Foundation
"""

import time
import hashlib
import json
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional, Tuple
import re

class RateLimiter:
    """Rate limiting implementation using sliding window"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = {}
    
    def is_allowed(self, client_id: str) -> Tuple[bool, Optional[str]]:
        """Check if client is allowed to make request"""
        now = time.time()
        
        # Initialize client if not exists
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove old requests outside window
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < self.window_seconds
        ]
        
        # Check if under limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False, f"Rate limit exceeded: {self.max_requests} requests per {self.window_seconds} seconds"
        
        # Add current request
        self.requests[client_id].append(now)
        return True, None
    
    def get_client_info(self, client_id: str) -> Dict:
        """Get rate limit info for client"""
        now = time.time()
        if client_id not in self.requests:
            return {
                'current_requests': 0,
                'max_requests': self.max_requests,
                'window_seconds': self.window_seconds,
                'reset_time': now + self.window_seconds
            }
        
        # Count current requests
        current_requests = len([
            req_time for req_time in self.requests[client_id]
            if now - req_time < self.window_seconds
        ])
        
        # Find when window resets
        oldest_request = min(self.requests[client_id]) if self.requests[client_id] else now
        reset_time = oldest_request + self.window_seconds
        
        return {
            'current_requests': current_requests,
            'max_requests': self.max_requests,
            'window_seconds': self.window_seconds,
            'reset_time': reset_time
        }

class InputValidator:
    """Input validation and sanitization"""
    
    def __init__(self):
        self.max_message_length = 10000
        self.max_model_length = 100
        self.allowed_models = [
            'qwen25-grounded:latest',
            'llama31-grounded:latest',
            'llama-3.3-70b-versatile'
        ]
        
        # Patterns for dangerous content
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # XSS
            r'javascript:',                # JavaScript URLs
            r'on\w+\s*=',                 # Event handlers
            r'(union|select|insert|update|delete|drop|create|alter)\s',  # SQL injection
        ]
    
    def validate_input(self, data: Dict) -> Tuple[bool, Optional[str]]:
        """Validate input data"""
        if not isinstance(data, dict):
            return False, "Request body must be JSON object"
        
        # Validate message
        message = data.get('message', '')
        if not isinstance(message, str):
            return False, "Message must be a string"
        
        if len(message) > self.max_message_length:
            return False, f"Message too long: max {self.max_message_length} characters"
        
        if len(message.strip()) == 0:
            return False, "Message cannot be empty"
        
        # Check for dangerous content
        for pattern in self.dangerous_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return False, "Message contains potentially dangerous content"
        
        # Validate model (optional)
        model = data.get('model', '')
        if model:
            if not isinstance(model, str):
                return False, "Model must be a string"
            
            if len(model) > self.max_model_length:
                return False, f"Model name too long: max {self.max_model_length} characters"
            
            if model not in self.allowed_models:
                return False, f"Model not allowed: {model}"
        
        # Validate provider (optional)
        provider = data.get('provider', '')
        if provider:
            if not isinstance(provider, str):
                return False, "Provider must be a string"
            
            valid_providers = ['ollama', 'groq', 'gemini']
            if provider not in valid_providers:
                return False, f"Provider not allowed: {provider}"
        
        # Validate use_rag (optional)
        use_rag = data.get('use_rag')
        if use_rag is not None and not isinstance(use_rag, bool):
            return False, "use_rag must be boolean"
        
        # Validate session_id (optional)
        session_id = data.get('session_id', '')
        if session_id:
            if not isinstance(session_id, str):
                return False, "session_id must be a string"
            
            if len(session_id) > 100:
                return False, "session_id too long: max 100 characters"
        
        return True, None
    
    def sanitize_input(self, data: Dict) -> Dict:
        """Sanitize input data"""
        sanitized = data.copy()
        
        # Sanitize message
        if 'message' in sanitized:
            message = sanitized['message']
            # Remove potential script tags
            message = re.sub(r'<script[^>]*>.*?</script>', '', message, flags=re.IGNORECASE)
            # Remove JavaScript URLs
            message = re.sub(r'javascript:', '', message, flags=re.IGNORECASE)
            # Remove event handlers
            message = re.sub(r'on\w+\s*=', '', message, flags=re.IGNORECASE)
            sanitized['message'] = message.strip()
        
        return sanitized

class SecurityMiddleware:
    # Logic for Humans: Optional rate limiting + JSON body validation/sanitization; wraps Flask handlers when the decorator is enabled.
    """Main security middleware class"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600, enable_rate_limiting: bool = True):
        self.enable_rate_limiting = enable_rate_limiting
        if enable_rate_limiting:
            self.rate_limiter = RateLimiter(max_requests, window_seconds)
        else:
            self.rate_limiter = None
        self.input_validator = InputValidator()
        self.blocked_ips: Dict[str, datetime] = {}
        self.suspicious_requests: List[Dict] = []
    
    def get_client_id(self, request) -> str:
        """Get client identifier from request"""
        # Try to get real IP (considering proxies)
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
        if not client_ip:
            client_ip = request.environ.get('REMOTE_ADDR', 'unknown')
        
        # Add user agent fingerprinting for better identification
        user_agent = request.environ.get('HTTP_USER_AGENT', 'unknown')
        client_string = f"{client_ip}:{hashlib.md5(user_agent.encode()).hexdigest()[:8]}"
        
        return client_string
    
    def is_ip_blocked(self, client_ip: str) -> bool:
        """Check if IP is blocked"""
        if client_ip in self.blocked_ips:
            if datetime.now() < self.blocked_ips[client_ip]:
                return True
            else:
                # Unblock if block expired
                del self.blocked_ips[client_ip]
        return False
    
    def block_ip(self, client_ip: str, duration_minutes: int = 60):
        """Block an IP for specified duration"""
        self.blocked_ips[client_ip] = datetime.now() + timedelta(minutes=duration_minutes)
    
    def validate_request(self, request) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """Validate incoming request"""
        try:
            # Get client identifier
            client_id = self.get_client_id(request)
            client_ip = request.environ.get('REMOTE_ADDR', 'unknown')
            
            # Check if IP is blocked
            if self.is_ip_blocked(client_ip):
                return False, "IP address blocked due to suspicious activity", None
            
            # Rate limiting (if enabled)
            if self.enable_rate_limiting and self.rate_limiter:
                allowed, rate_error = self.rate_limiter.is_allowed(client_id)
                if not allowed:
                    # Log suspicious activity
                    self.suspicious_requests.append({
                        'timestamp': datetime.now(),
                        'client_id': client_id,
                        'client_ip': client_ip,
                        'reason': 'rate_limit_exceeded',
                        'details': rate_error
                    })
                    
                    # Block IP temporarily if excessive requests
                    if 'exceeded' in rate_error.lower():
                        self.block_ip(client_ip, 30)  # 30 minute block
                    
                    return False, rate_error, None
            
            # Parse and validate JSON
            try:
                data = request.get_json()
                if data is None:
                    return False, "Invalid JSON or empty request body", None
            except Exception as e:
                return False, f"JSON parsing error: {str(e)}", None
            
            # Input validation
            valid, validation_error = self.input_validator.validate_input(data)
            if not valid:
                # Log suspicious activity
                self.suspicious_requests.append({
                    'timestamp': datetime.now(),
                    'client_id': client_id,
                    'client_ip': client_ip,
                    'reason': 'input_validation_failed',
                    'details': validation_error
                })
                return False, validation_error, None
            
            # Sanitize input
            sanitized_data = self.input_validator.sanitize_input(data)

            info: Dict = {'sanitized_data': sanitized_data}
            if self.rate_limiter is not None:
                info['rate_info'] = self.rate_limiter.get_client_info(client_id)

            return True, None, info
            
        except Exception as e:
            return False, f"Security validation error: {str(e)}", None
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for response"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        }
    
    def get_security_stats(self) -> Dict:
        """Get security statistics for monitoring"""
        now = datetime.now()
        recent_suspicious = [
            req for req in self.suspicious_requests
            if now - req['timestamp'] < timedelta(hours=24)
        ]
        
        rate_limiter = self.rate_limiter
        if rate_limiter is not None:
            total_clients = len(rate_limiter.requests)
            rate_limit_config: Dict = {
                'enabled': True,
                'max_requests': rate_limiter.max_requests,
                'window_seconds': rate_limiter.window_seconds,
            }
        else:
            total_clients = 0
            rate_limit_config = {'enabled': False}

        return {
            'active_blocked_ips': len(self.blocked_ips),
            'suspicious_requests_24h': len(recent_suspicious),
            'total_clients_tracked': total_clients,
            'rate_limit_config': rate_limit_config,
            'recent_suspicious_activity': recent_suspicious[-10:]  # Last 10
        }

# Decorator for Flask routes
def require_security(middleware_instance):
    # Logic for Humans: Flask decorator — reject bad JSON / oversize messages / rate limits before the route runs; attach security headers on success.
    """Decorator to apply security middleware to Flask routes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request, jsonify
            
            # Validate request
            allowed, error, info = middleware_instance.validate_request(request)
            
            if not allowed:
                response = jsonify({
                    'success': False,
                    'error': error,
                    'error_type': 'security_validation_failed'
                })
                response.status_code = 429  # Too Many Requests
                return response
            
            # Add security headers
            response = f(*args, **kwargs)
            
            # Add rate limit headers if info available
            if info and info.get('rate_info') is not None:
                rate_info = info['rate_info']
                response.headers['X-RateLimit-Limit'] = str(rate_info['max_requests'])
                response.headers['X-RateLimit-Remaining'] = str(
                    rate_info['max_requests'] - rate_info['current_requests']
                )
                response.headers['X-RateLimit-Reset'] = str(int(rate_info['reset_time']))
            
            # Add security headers
            security_headers = middleware_instance.get_security_headers()
            for header, value in security_headers.items():
                response.headers[header] = value
            
            return response
        
        return decorated_function
    return decorator

#!/usr/bin/env python3
"""
Secure Logging Configuration
Provides secure logging with API key redaction and structured formatting
"""

import logging
import re
import json
from datetime import datetime
from typing import Any, Dict

class SecureFormatter(logging.Formatter):
    """Formatter that redacts sensitive information"""
    
    SENSITIVE_PATTERNS = [
        r'(GROQ_API_KEY|ANTHROPIC_API_KEY|GEMINI_API_KEY)[=:\s]+[A-Za-z0-9_-]+',
        r'(sk-[a-zA-Z0-9_-]+)',
        r'(gsk_[a-zA-Z0-9_-]+)',
        r'(AIzaSy[A-Za-z0-9_-]+)'
    ]
    
    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        for pattern in self.SENSITIVE_PATTERNS:
            message = re.sub(pattern, r'\1=***REDACTED***', message, flags=re.IGNORECASE)
        return message

class StructuredLogger:
    """Structured logging with security and performance tracking"""
    
    def __init__(self, name: str, log_file: str = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler with secure formatting
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(SecureFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(SecureFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(file_handler)
    
    def log_model_call(self, provider: str, model: str, user_message: str, response_time: float, success: bool):
        """Log model interaction securely"""
        self.logger.info(f"Model call - Provider: {provider}, Model: {model}, Response time: {response_time:.2f}s, Success: {success}")
    
    def log_error(self, error_type: str, message: str, context: Dict = None):
        """Log error with context"""
        context_str = f", Context: {json.dumps(context)}" if context else ""
        self.logger.error(f"Error - Type: {error_type}, Message: {message}{context_str}")
    
    def log_security_event(self, event_type: str, details: Dict):
        """Log security-related events"""
        self.logger.warning(f"Security Event - Type: {event_type}, Details: {json.dumps(details)}")
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = "ms"):
        """Log performance metrics"""
        self.logger.info(f"Performance - {metric_name}: {value}{unit}")

def setup_secure_logging():
    """Setup secure logging configuration for the application"""
    
    # Create loggers
    security_logger = StructuredLogger('security', 'logs/security.log')
    performance_logger = StructuredLogger('performance', 'logs/performance.log')
    error_logger = StructuredLogger('errors', 'logs/errors.log')
    
    return {
        'security': security_logger,
        'performance': performance_logger,
        'errors': error_logger
    }

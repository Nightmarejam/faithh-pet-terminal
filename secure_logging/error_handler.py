#!/usr/bin/env python3
"""
Comprehensive Error Handling for AI Services
Provides structured error handling and categorization
"""

import logging
import traceback
import json
from datetime import datetime
from typing import Optional, Dict, Any

class ErrorHandler:
    """Comprehensive error handling for AI services"""
    
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger('error_handler')
    
    def handle_api_error(self, provider: str, model: str, 
                        error: Exception, context: Optional[Dict] = None):
        """Handle API-related errors"""
        error_info = {
            'timestamp': datetime.utcnow().isoformat(),
            'provider': provider,
            'model': model,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {},
            'traceback': traceback.format_exc()
        }
        
        self.logger.error(f"API Error: {json.dumps(error_info)}")
        
        # Categorize error for appropriate response
        error_str = str(error).lower()
        if 'authentication' in error_str or 'unauthorized' in error_str or '401' in error_str:
            return {'type': 'auth_error', 'message': 'API authentication failed', 'retry': False}
        elif 'forbidden' in error_str or '403' in error_str:
            return {'type': 'permission_error', 'message': 'API permission denied', 'retry': False}
        elif 'timeout' in error_str or 'timed out' in error_str:
            return {'type': 'timeout_error', 'message': 'Request timed out', 'retry': True}
        elif 'rate limit' in error_str or '429' in error_str:
            return {'type': 'rate_limit_error', 'message': 'Rate limit exceeded', 'retry': True}
        elif 'connection' in error_str or 'network' in error_str:
            return {'type': 'connection_error', 'message': 'Network connection failed', 'retry': True}
        elif 'model' in error_str and 'not found' in error_str:
            return {'type': 'model_error', 'message': 'Model not available', 'retry': False}
        else:
            return {'type': 'general_error', 'message': 'Service temporarily unavailable', 'retry': True}
    
    def handle_configuration_error(self, component: str, error: Exception):
        """Handle configuration-related errors"""
        error_info = {
            'timestamp': datetime.utcnow().isoformat(),
            'component': component,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc()
        }
        
        self.logger.error(f"Configuration Error: {json.dumps(error_info)}")
        return {'type': 'config_error', 'message': f'Configuration error in {component}'}
    
    def handle_model_switch_error(self, from_model: str, to_model: str, error: Exception):
        """Handle model switching errors"""
        error_info = {
            'timestamp': datetime.utcnow().isoformat(),
            'from_model': from_model,
            'to_model': to_model,
            'error_type': type(error).__name__,
            'error_message': str(error)
        }
        
        self.logger.error(f"Model Switch Error: {json.dumps(error_info)}")
        return {'type': 'switch_error', 'message': f'Failed to switch from {from_model} to {to_model}'}
    
    def handle_resource_error(self, resource_type: str, error: Exception):
        """Handle resource-related errors (memory, GPU, etc.)"""
        error_info = {
            'timestamp': datetime.utcnow().isoformat(),
            'resource_type': resource_type,
            'error_type': type(error).__name__,
            'error_message': str(error)
        }
        
        self.logger.error(f"Resource Error: {json.dumps(error_info)}")
        return {'type': 'resource_error', 'message': f'Resource error: {resource_type}'}
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors (would read from log files in full implementation)"""
        return {
            'total_errors': 0,  # Would be calculated from logs
            'error_types': {},  # Would be aggregated from logs
            'most_common_errors': [],  # Would be determined from logs
            'recent_errors': []  # Would be read from recent log entries
        }

#!/usr/bin/env python3
"""
Security Audit Logging
Tracks security events, API key access, and configuration changes
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

class SecurityAuditLogger:
    """Logs security-related events for audit purposes"""
    
    def __init__(self, log_file: str = 'logs/security.log'):
        self.log_file = log_file
        self.logger = self._setup_secure_logger()
    
    def _setup_secure_logger(self) -> logging.Logger:
        """Setup logger with secure formatting"""
        logger = logging.getLogger('security_audit')
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # File handler with restricted access
        file_handler = logging.FileHandler(self.log_file)
        
        # Secure formatter that redacts sensitive info
        formatter = logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def log_api_key_access(self, key_name: str, action: str, source: str = "unknown"):
        """Log API key access events"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'api_key_access',
            'key_name': key_name,
            'action': action,  # 'read', 'validate', 'use'
            'source': source,
            'user': os.getenv('USER', 'unknown')
        }
        
        self.logger.info(f"API Key Access - {json.dumps(event)}")
    
    def log_configuration_change(self, component: str, change_type: str, 
                                old_value: Any = None, new_value: Any = None):
        """Log configuration changes"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'config_change',
            'component': component,
            'change_type': change_type,
            'old_value': str(old_value) if old_value is not None else None,
            'new_value': str(new_value) if new_value is not None else None,
            'user': os.getenv('USER', 'unknown')
        }
        
        self.logger.info(f"Configuration Change - {json.dumps(event)}")
    
    def log_model_access(self, provider: str, model: str, user_id: str = "anonymous"):
        """Log model access events"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'model_access',
            'provider': provider,
            'model': model,
            'user_id': user_id,
            'source_ip': '127.0.0.1'  # Would be actual IP in production
        }
        
        self.logger.info(f"Model Access - {json.dumps(event)}")
    
    def log_security_violation(self, violation_type: str, details: Dict[str, Any]):
        """Log security violations"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'security_violation',
            'violation_type': violation_type,
            'details': details,
            'severity': 'high',
            'user': os.getenv('USER', 'unknown')
        }
        
        self.logger.warning(f"Security Violation - {json.dumps(event)}")
    
    def log_authentication_event(self, provider: str, success: bool, 
                                reason: str = None):
        """Log authentication attempts"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'authentication',
            'provider': provider,
            'success': success,
            'reason': reason,
            'source': 'backend'
        }
        
        level = logging.INFO if success else logging.WARNING
        self.logger.log(level, f"Authentication Event - {json.dumps(event)}")
    
    def log_permission_check(self, resource: str, action: str, 
                           allowed: bool, user_id: str = "anonymous"):
        """Log permission checks"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'permission_check',
            'resource': resource,
            'action': action,
            'allowed': allowed,
            'user_id': user_id
        }
        
        level = logging.INFO if allowed else logging.WARNING
        self.logger.log(level, f"Permission Check - {json.dumps(event)}")
    
    def log_data_access(self, data_type: str, operation: str, 
                       record_count: int = 0, user_id: str = "anonymous"):
        """Log data access events"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'data_access',
            'data_type': data_type,
            'operation': operation,  # 'read', 'write', 'delete'
            'record_count': record_count,
            'user_id': user_id
        }
        
        self.logger.info(f"Data Access - {json.dumps(event)}")
    
    def get_security_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get security summary for specified period"""
        # In a full implementation, this would read and parse the log file
        # For now, return a placeholder structure
        return {
            'period_hours': hours,
            'total_events': 0,
            'api_key_accesses': 0,
            'authentication_failures': 0,
            'security_violations': 0,
            'model_accesses': 0,
            'configuration_changes': 0
        }

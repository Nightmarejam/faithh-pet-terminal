#!/usr/bin/env python3
"""
API Key Validation and Security Management
Handles secure validation and masking of API keys
"""

import os
import re
from typing import Dict, List, Optional

class APIKeyValidator:
    """Validates and manages API keys securely"""
    
    KEY_PATTERNS = {
        'GROQ_API_KEY': r'^gsk_[A-Za-z0-9_-]+$',
        'ANTHROPIC_API_KEY': r'^sk-ant-api03-[A-Za-z0-9_-]+$',
        'GEMINI_API_KEY': r'^AIzaSy[A-Za-z0-9_-]+$',
        'GOOGLE_SEARCH_API_KEY': r'^AIza[A-Za-z0-9_-]+$'
    }
    
    def validate_all_keys(self) -> Dict[str, bool]:
        """Validate all configured API keys"""
        results = {}
        for key_name, pattern in self.KEY_PATTERNS.items():
            key_value = os.getenv(key_name)
            if key_value:
                results[key_name] = bool(re.match(pattern, key_value))
            else:
                results[key_name] = False
        return results
    
    def mask_key_for_logging(self, key_value: str) -> str:
        """Mask API key for safe logging"""
        if len(key_value) <= 10:
            return "***MASKED***"
        return f"{key_value[:8]}...{key_value[-4:]}"
    
    def validate_key_format(self, key_name: str, key_value: str) -> bool:
        """Validate individual key format"""
        if key_name not in self.KEY_PATTERNS:
            return False
        pattern = self.KEY_PATTERNS[key_name]
        return bool(re.match(pattern, key_value))
    
    def get_key_security_status(self) -> Dict[str, Dict]:
        """Get comprehensive security status"""
        status = {}
        for key_name in self.KEY_PATTERNS.keys():
            key_value = os.getenv(key_name)
            status[key_name] = {
                'present': bool(key_value),
                'valid_format': self.validate_key_format(key_name, key_value) if key_value else False,
                'masked_value': self.mask_key_for_logging(key_value) if key_value else None
            }
        return status

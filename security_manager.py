"""
Security Manager - Handles permissions and validation

This module provides security checks for tool execution including:
- Path validation (allowed directories)
- Command validation (blocked commands)
- Permission checking
"""
import os
from typing import List, Set
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SecurityManager:
    """Manages security checks for tool execution"""
    
    def __init__(self, config: dict):
        """
        Initialize security manager with configuration
        
        Args:
            config: Security configuration dict with keys:
                - allowed_directories: List of allowed paths
                - blocked_commands: List of forbidden commands
                - default_permissions: Default permission set
        """
        self.allowed_paths: List[str] = config.get('allowed_directories', [])
        self.blocked_commands: List[str] = config.get('blocked_commands', [])
        self.default_permissions: Set[str] = set(config.get('default_permissions', []))
        
        # Normalize and expand allowed paths
        self.allowed_paths_normalized = [
            os.path.abspath(os.path.expanduser(p)) 
            for p in self.allowed_paths
        ]
        
        logger.info(f"Security Manager initialized with {len(self.allowed_paths)} allowed paths")
        logger.info(f"Blocked commands: {', '.join(self.blocked_commands)}")
    
    def validate_path(self, path: str) -> bool:
        """
        Check if path is within allowed directories
        
        Args:
            path: File or directory path to validate
            
        Returns:
            bool: True if path is allowed, False otherwise
        """
        # TODO: Implement robust path validation
        # - Resolve symlinks
        # - Handle relative paths
        # - Check for path traversal attempts
        # - Normalize path separators
        
        try:
            # Normalize the input path
            abs_path = os.path.abspath(os.path.expanduser(path))
            
            # Check against allowed paths
            for allowed in self.allowed_paths_normalized:
                if abs_path.startswith(allowed):
                    logger.debug(f"Path allowed: {path}")
                    return True
            
            logger.warning(f"Path rejected: {path}")
            return False
            
        except Exception as e:
            logger.error(f"Path validation error: {e}")
            return False
    
    def validate_command(self, command: str) -> bool:
        """
        Check if command is allowed (not in blocked list)
        
        Args:
            command: Shell command to validate
            
        Returns:
            bool: True if command allowed, False if blocked
        """
        # TODO: Implement command validation
        # - Extract command name from full command string
        # - Check for shell metacharacters
        # - Detect command chaining attempts
        # - Check for privilege escalation (sudo, etc.)
        
        # Extract base command (first word)
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return False
        
        cmd_name = cmd_parts[0]
        
        # Check if command is blocked
        if cmd_name in self.blocked_commands:
            logger.warning(f"Blocked command attempted: {cmd_name}")
            return False
        
        logger.debug(f"Command allowed: {cmd_name}")
        return True
    
    def check_permission(self, required: str, granted: Set[str]) -> bool:
        """
        Check if a required permission is in the granted set
        
        Args:
            required: Permission string (e.g., 'file.write')
            granted: Set of granted permission strings
            
        Returns:
            bool: True if permission granted, False otherwise
        """
        # Check exact match
        if required in granted:
            return True
        
        # Check wildcard permissions (e.g., 'file.*' grants 'file.read')
        parts = required.split('.')
        for i in range(len(parts)):
            wildcard = '.'.join(parts[:i+1]) + '.*'
            if wildcard in granted:
                return True
        
        return False
    
    def get_default_permissions(self) -> Set[str]:
        """Get the default permission set"""
        return self.default_permissions.copy()


# Global security manager instance
_security_manager = None

def get_security_manager(config: dict = None) -> SecurityManager:
    """Get the global security manager instance"""
    global _security_manager
    if _security_manager is None:
        if config is None:
            raise ValueError("Security manager not initialized - config required")
        _security_manager = SecurityManager(config)
    return _security_manager

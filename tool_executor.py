#!/usr/bin/env python3
"""
Tool Executor - Core execution engine for FAITHH
Orchestrates tool execution with security validation and executor routing
"""
from typing import Dict, Any, Optional
import logging
import yaml
from pathlib import Path
import asyncio

# Import our modules
from tool_registry import get_registry
from security_manager import SecurityManager

logger = logging.getLogger(__name__)

class ToolExecutionError(Exception):
    """Custom exception for tool execution failures"""
    pass

class ToolExecutor:
    """
    Core execution engine that orchestrates tool execution
    
    Flow: Registry lookup -> Security check -> Route to executor -> Return result
    """
    
    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize the tool executor"""
        self.registry = get_registry()
        self.config = self._load_config(config_path)
        # Pass security subsection to SecurityManager
        security_config = self.config.get('security', {})
        self.security = SecurityManager(security_config)
        self.executors: Dict[str, Any] = {}
        
        logger.info("Tool Executor initialized")
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Config loaded from {config_path}")
                return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def register_executor(self, executor_type: str, executor_instance: Any) -> None:
        """
        Register an executor instance for a specific type
        
        Args:
            executor_type: Type of executor (filesystem, process, rag, etc.)
            executor_instance: The executor instance that implements execute()
        """
        self.executors[executor_type] = executor_instance
        logger.info(f"Registered executor: {executor_type}")
    
    async def execute_tool(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any],
        permissions: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool with security validation
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            permissions: Optional permissions override
            
        Returns:
            Dict with execution results
        """
        try:
            # Step 1: Lookup tool in registry
            tool_def = self.registry.get_tool(tool_name)
            if not tool_def:
                raise ToolExecutionError(f"Tool not found: {tool_name}")
            
            logger.info(f"Executing tool: {tool_name}")
            
            # Step 2: Security validation
            required_perms = tool_def.get('permissions', [])
            if not self._check_permissions(required_perms, permissions):
                raise ToolExecutionError(f"Insufficient permissions for {tool_name}")
            
            # Step 3: Validate parameters based on tool type
            validated_params = self._validate_parameters(tool_def, parameters)
            
            # Step 4: Route to appropriate executor
            executor_type = tool_def.get('executor')
            if executor_type not in self.executors:
                raise ToolExecutionError(f"No executor registered for type: {executor_type}")
            
            executor = self.executors[executor_type]
            
            # Step 5: Execute with timeout
            timeout = self.config.get('tools', {}).get('execution_timeout_ms', 30000) / 1000
            result = await asyncio.wait_for(
                executor.execute(tool_name, validated_params),
                timeout=timeout
            )
            
            # Step 6: Format and return result
            return {
                'success': True,
                'tool': tool_name,
                'result': result,
                'executor': executor_type
            }
            
        except asyncio.TimeoutError:
            logger.error(f"Tool execution timeout: {tool_name}")
            return {
                'success': False,
                'error': 'Execution timeout',
                'tool': tool_name
            }
        except ToolExecutionError as e:
            logger.error(f"Tool execution error: {e}")
            return {
                'success': False,
                'error': str(e),
                'tool': tool_name
            }
        except Exception as e:
            logger.error(f"Unexpected error executing {tool_name}: {e}")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'tool': tool_name
            }
    
    def _check_permissions(self, required: list, provided: Optional[list]) -> bool:
        """
        Check if provided permissions satisfy requirements
        
        Args:
            required: List of required permissions
            provided: List of provided permissions (None means use default)
            
        Returns:
            bool: True if permissions are sufficient
        """
        if not required:
            return True
        
        # Use default permissions if none provided
        if provided is None:
            provided = self.config.get('security', {}).get('default_permissions', [])
        
        # Check if all required permissions are in provided
        return all(perm in provided for perm in required)
    
    def _validate_parameters(self, tool_def: dict, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize tool parameters
        
        Args:
            tool_def: Tool definition from registry
            parameters: User-provided parameters
            
        Returns:
            Validated parameters
        """
        validated = parameters.copy()
        
        # If tool operates on file paths, validate them
        if 'path' in validated:
            if not self.security.validate_path(validated['path']):
                raise ToolExecutionError(f"Invalid path: {validated['path']}")
        
        # If tool executes commands, validate them
        if 'command' in validated:
            if not self.security.validate_command(validated['command']):
                raise ToolExecutionError(f"Blocked command: {validated['command']}")
        
        return validated
    
    async def execute_combo(self, combo_tools: list) -> Dict[str, Any]:
        """
        Execute a combo of tools in sequence (Battle Chip combos!)
        
        Args:
            combo_tools: List of (tool_name, parameters) tuples
            
        Returns:
            Combined results with bonus if enabled
        """
        if not self.config.get('tools', {}).get('enable_combos', True):
            return {'success': False, 'error': 'Combos disabled'}
        
        results = []
        for tool_name, params in combo_tools:
            result = await self.execute_tool(tool_name, params)
            results.append(result)
            
            # Stop combo chain on first failure
            if not result.get('success'):
                break
        
        # Calculate combo bonus
        bonus_multiplier = self.config.get('tools', {}).get('combo_bonus_multiplier', 1.0)
        all_success = all(r.get('success') for r in results)
        
        return {
            'success': all_success,
            'combo_size': len(results),
            'results': results,
            'bonus_applied': all_success and bonus_multiplier > 1.0,
            'bonus_multiplier': bonus_multiplier if all_success else 1.0
        }


# Global executor instance
_executor = None

def get_executor(config_path: str = 'config.yaml') -> ToolExecutor:
    """Get the global tool executor instance"""
    global _executor
    if _executor is None:
        _executor = ToolExecutor(config_path)
    return _executor

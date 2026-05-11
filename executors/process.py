#!/usr/bin/env python3
"""
Process Executor - Handles command execution
"""
import asyncio
import subprocess
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ProcessExecutor:
    """Handles process/command execution"""
    
    async def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a process tool
        
        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters
            
        Returns:
            Execution result dict
        """
        try:
            if tool_name == 'run_command':
                return await self._run_command(parameters)
            else:
                raise ValueError(f"Unknown process tool: {tool_name}")
        except Exception as e:
            logger.error(f"Process execution error: {e}")
            raise
    
    async def _run_command(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a shell command"""
        command = params.get('command')
        if not command:
            raise ValueError("Missing required parameter: command")
        
        timeout = params.get('timeout', 30)  # Default 30 second timeout
        shell = params.get('shell', True)
        
        try:
            # Run command with timeout
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=shell
            )
            
            # Wait for completion with timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            return {
                'command': command,
                'stdout': stdout.decode('utf-8'),
                'stderr': stderr.decode('utf-8'),
                'return_code': process.returncode,
                'success': process.returncode == 0
            }
            
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return {
                'command': command,
                'error': 'Command timeout',
                'timeout': timeout,
                'success': False
            }
        except Exception as e:
            return {
                'command': command,
                'error': str(e),
                'success': False
            }

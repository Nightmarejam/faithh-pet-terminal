#!/usr/bin/env python3
"""
Filesystem Executor - Handles file operations
"""
import os
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class FilesystemExecutor:
    """Handles filesystem tool execution"""
    
    async def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a filesystem tool
        
        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters
            
        Returns:
            Execution result dict
        """
        try:
            if tool_name == 'read_file':
                return await self._read_file(parameters)
            elif tool_name == 'write_file':
                return await self._write_file(parameters)
            elif tool_name == 'list_directory':
                return await self._list_directory(parameters)
            elif tool_name == 'file_info':
                return await self._file_info(parameters)
            else:
                raise ValueError(f"Unknown filesystem tool: {tool_name}")
        except Exception as e:
            logger.error(f"Filesystem execution error: {e}")
            raise
    
    async def _read_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read file contents"""
        path = params.get('path')
        if not path:
            raise ValueError("Missing required parameter: path")
        
        # Read file
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            'path': path,
            'content': content,
            'size': len(content),
            'lines': content.count('\n') + 1
        }
    
    async def _write_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Write content to file"""
        path = params.get('path')
        content = params.get('content', '')
        mode = params.get('mode', 'w')  # 'w' or 'a' for append
        
        if not path:
            raise ValueError("Missing required parameter: path")
        
        # Create parent directory if needed
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(path, mode, encoding='utf-8') as f:
            f.write(content)
        
        return {
            'path': path,
            'bytes_written': len(content.encode('utf-8')),
            'mode': mode
        }
    
    async def _list_directory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List directory contents"""
        path = params.get('path', '.')
        
        if not os.path.isdir(path):
            raise ValueError(f"Not a directory: {path}")
        
        items = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            items.append({
                'name': item,
                'type': 'directory' if os.path.isdir(item_path) else 'file',
                'size': os.path.getsize(item_path) if os.path.isfile(item_path) else 0
            })
        
        return {
            'path': path,
            'items': items,
            'count': len(items)
        }
    
    async def _file_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get file metadata"""
        path = params.get('path')
        if not path:
            raise ValueError("Missing required parameter: path")
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        
        stat = os.stat(path)
        
        return {
            'path': path,
            'size': stat.st_size,
            'type': 'directory' if os.path.isdir(path) else 'file',
            'modified': stat.st_mtime,
            'created': stat.st_ctime,
            'readable': os.access(path, os.R_OK),
            'writable': os.access(path, os.W_OK)
        }

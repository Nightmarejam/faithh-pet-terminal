#!/usr/bin/env python3
"""
Tool System for Local AI Agent
Provides file operations, code search, and command execution capabilities
"""
import os
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class ToolSystem:
    """Function calling system for local AI agent"""

    def __init__(self, workspace_root: str = None):
        """
        Initialize the tool system

        Args:
            workspace_root: Root directory for file operations (defaults to current directory)
        """
        self.workspace_root = Path(workspace_root or os.getcwd()).resolve()
        self.tools = {
            "read_file": self.read_file,
            "write_file": self.write_file,
            "edit_file": self.edit_file,
            "list_directory": self.list_directory,
            "search_code": self.search_code,
            "run_command": self.run_command,
            "create_directory": self.create_directory,
            "delete_file": self.delete_file,
            "get_file_info": self.get_file_info,
        }

        logger.info(f"ToolSystem initialized with workspace: {self.workspace_root}")

    def _resolve_path(self, filepath: str) -> Path:
        """
        Resolve a path relative to workspace root and ensure it's within workspace

        Args:
            filepath: File path (relative or absolute)

        Returns:
            Resolved Path object

        Raises:
            ValueError: If path is outside workspace
        """
        path = Path(filepath)
        if not path.is_absolute():
            path = self.workspace_root / path

        path = path.resolve()

        # Security check: ensure path is within workspace
        try:
            path.relative_to(self.workspace_root)
        except ValueError:
            raise ValueError(f"Path {path} is outside workspace {self.workspace_root}")

        return path

    def read_file(self, filepath: str) -> Dict[str, Any]:
        """
        Read a file and return contents

        Args:
            filepath: Path to file to read

        Returns:
            Dict with success status and content or error
        """
        try:
            path = self._resolve_path(filepath)

            if not path.exists():
                return {
                    "success": False,
                    "error": f"File does not exist: {filepath}"
                }

            if not path.is_file():
                return {
                    "success": False,
                    "error": f"Path is not a file: {filepath}"
                }

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            logger.info(f"Read file: {filepath} ({len(content)} bytes)")
            return {
                "success": True,
                "filepath": str(path.relative_to(self.workspace_root)),
                "content": content,
                "size": len(content)
            }

        except UnicodeDecodeError:
            return {
                "success": False,
                "error": f"File is not text (binary file): {filepath}"
            }
        except Exception as e:
            logger.error(f"Error reading file {filepath}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """
        Write content to a file (creates new file or overwrites existing)

        Args:
            filepath: Path to file to write
            content: Content to write

        Returns:
            Dict with success status and message or error
        """
        try:
            path = self._resolve_path(filepath)

            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Wrote file: {filepath} ({len(content)} bytes)")
            return {
                "success": True,
                "filepath": str(path.relative_to(self.workspace_root)),
                "message": f"Successfully wrote {len(content)} bytes to {filepath}",
                "size": len(content)
            }

        except Exception as e:
            logger.error(f"Error writing file {filepath}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def edit_file(self, filepath: str, old_text: str, new_text: str) -> Dict[str, Any]:
        """
        Edit a file by replacing old_text with new_text

        Args:
            filepath: Path to file to edit
            old_text: Text to find and replace
            new_text: Text to replace with

        Returns:
            Dict with success status and message or error
        """
        try:
            # First read the file
            result = self.read_file(filepath)
            if not result["success"]:
                return result

            content = result["content"]

            # Check if old_text exists
            if old_text not in content:
                return {
                    "success": False,
                    "error": f"Text not found in file: {old_text[:50]}..."
                }

            # Replace the text
            new_content = content.replace(old_text, new_text, 1)  # Replace first occurrence

            # Write the modified content
            return self.write_file(filepath, new_content)

        except Exception as e:
            logger.error(f"Error editing file {filepath}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def list_directory(self, dirpath: str = ".", pattern: str = "*") -> Dict[str, Any]:
        """
        List files in a directory

        Args:
            dirpath: Path to directory to list (default: current directory)
            pattern: Glob pattern to filter files (default: all files)

        Returns:
            Dict with success status and list of files or error
        """
        try:
            path = self._resolve_path(dirpath)

            if not path.exists():
                return {
                    "success": False,
                    "error": f"Directory does not exist: {dirpath}"
                }

            if not path.is_dir():
                return {
                    "success": False,
                    "error": f"Path is not a directory: {dirpath}"
                }

            # List files matching pattern
            files = []
            for item in path.glob(pattern):
                rel_path = item.relative_to(self.workspace_root)
                files.append({
                    "name": item.name,
                    "path": str(rel_path),
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })

            logger.info(f"Listed directory: {dirpath} ({len(files)} items)")
            return {
                "success": True,
                "directory": str(path.relative_to(self.workspace_root)),
                "files": files,
                "count": len(files)
            }

        except Exception as e:
            logger.error(f"Error listing directory {dirpath}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def search_code(self, pattern: str, directory: str = ".", file_pattern: str = "*.py") -> Dict[str, Any]:
        """
        Search for code pattern in files

        Args:
            pattern: Regex pattern to search for
            directory: Directory to search in (default: current)
            file_pattern: File glob pattern (default: *.py)

        Returns:
            Dict with success status and search results or error
        """
        try:
            path = self._resolve_path(directory)

            if not path.exists() or not path.is_dir():
                return {
                    "success": False,
                    "error": f"Invalid directory: {directory}"
                }

            # Compile regex pattern
            regex = re.compile(pattern)

            # Search in files
            results = []
            for filepath in path.rglob(file_pattern):
                if not filepath.is_file():
                    continue

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.search(line):
                                results.append({
                                    "file": str(filepath.relative_to(self.workspace_root)),
                                    "line": line_num,
                                    "content": line.strip()
                                })
                except (UnicodeDecodeError, PermissionError):
                    continue

            logger.info(f"Searched code: {pattern} in {directory} ({len(results)} matches)")
            return {
                "success": True,
                "pattern": pattern,
                "directory": str(path.relative_to(self.workspace_root)),
                "matches": results,
                "count": len(results)
            }

        except Exception as e:
            logger.error(f"Error searching code: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def run_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Run a shell command (use with caution!)

        Args:
            command: Shell command to run
            timeout: Timeout in seconds (default: 30)

        Returns:
            Dict with success status, stdout, stderr, and exit code
        """
        try:
            logger.info(f"Running command: {command}")

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.workspace_root
            )

            return {
                "success": result.returncode == 0,
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds"
            }
        except Exception as e:
            logger.error(f"Error running command: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def create_directory(self, dirpath: str) -> Dict[str, Any]:
        """
        Create a directory (including parent directories)

        Args:
            dirpath: Path to directory to create

        Returns:
            Dict with success status and message or error
        """
        try:
            path = self._resolve_path(dirpath)
            path.mkdir(parents=True, exist_ok=True)

            logger.info(f"Created directory: {dirpath}")
            return {
                "success": True,
                "directory": str(path.relative_to(self.workspace_root)),
                "message": f"Successfully created directory: {dirpath}"
            }

        except Exception as e:
            logger.error(f"Error creating directory {dirpath}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def delete_file(self, filepath: str) -> Dict[str, Any]:
        """
        Delete a file (use with caution!)

        Args:
            filepath: Path to file to delete

        Returns:
            Dict with success status and message or error
        """
        try:
            path = self._resolve_path(filepath)

            if not path.exists():
                return {
                    "success": False,
                    "error": f"File does not exist: {filepath}"
                }

            if path.is_dir():
                return {
                    "success": False,
                    "error": f"Path is a directory (use rmdir): {filepath}"
                }

            path.unlink()

            logger.info(f"Deleted file: {filepath}")
            return {
                "success": True,
                "filepath": str(path.relative_to(self.workspace_root)),
                "message": f"Successfully deleted file: {filepath}"
            }

        except Exception as e:
            logger.error(f"Error deleting file {filepath}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_file_info(self, filepath: str) -> Dict[str, Any]:
        """
        Get information about a file

        Args:
            filepath: Path to file

        Returns:
            Dict with success status and file info or error
        """
        try:
            path = self._resolve_path(filepath)

            if not path.exists():
                return {
                    "success": False,
                    "error": f"Path does not exist: {filepath}"
                }

            stat = path.stat()

            return {
                "success": True,
                "filepath": str(path.relative_to(self.workspace_root)),
                "name": path.name,
                "type": "directory" if path.is_dir() else "file",
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "permissions": oct(stat.st_mode)[-3:]
            }

        except Exception as e:
            logger.error(f"Error getting file info {filepath}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool by name with arguments

        Args:
            tool_name: Name of the tool to execute
            **kwargs: Tool-specific arguments

        Returns:
            Dict with tool execution results
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "available_tools": list(self.tools.keys())
            }

        try:
            tool_func = self.tools[tool_name]
            result = tool_func(**kwargs)
            return result
        except TypeError as e:
            return {
                "success": False,
                "error": f"Invalid arguments for tool {tool_name}: {e}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing tool {tool_name}: {e}"
            }

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions in OpenAI function calling format

        Returns:
            List of tool definitions
        """
        return [
            {
                "name": "read_file",
                "description": "Read the contents of a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Path to the file to read"
                        }
                    },
                    "required": ["filepath"]
                }
            },
            {
                "name": "write_file",
                "description": "Write content to a file (creates or overwrites)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Path to the file to write"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file"
                        }
                    },
                    "required": ["filepath", "content"]
                }
            },
            {
                "name": "edit_file",
                "description": "Edit a file by replacing text",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Path to the file to edit"
                        },
                        "old_text": {
                            "type": "string",
                            "description": "Text to find and replace"
                        },
                        "new_text": {
                            "type": "string",
                            "description": "Text to replace with"
                        }
                    },
                    "required": ["filepath", "old_text", "new_text"]
                }
            },
            {
                "name": "list_directory",
                "description": "List files in a directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dirpath": {
                            "type": "string",
                            "description": "Path to directory to list (default: current directory)"
                        },
                        "pattern": {
                            "type": "string",
                            "description": "Glob pattern to filter files (default: *)"
                        }
                    }
                }
            },
            {
                "name": "search_code",
                "description": "Search for a pattern in code files",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Regex pattern to search for"
                        },
                        "directory": {
                            "type": "string",
                            "description": "Directory to search in (default: current)"
                        },
                        "file_pattern": {
                            "type": "string",
                            "description": "File glob pattern (default: *.py)"
                        }
                    },
                    "required": ["pattern"]
                }
            },
            {
                "name": "run_command",
                "description": "Run a shell command (use with caution)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Shell command to run"
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in seconds (default: 30)"
                        }
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "create_directory",
                "description": "Create a directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dirpath": {
                            "type": "string",
                            "description": "Path to directory to create"
                        }
                    },
                    "required": ["dirpath"]
                }
            },
            {
                "name": "get_file_info",
                "description": "Get information about a file or directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Path to file or directory"
                        }
                    },
                    "required": ["filepath"]
                }
            }
        ]


if __name__ == "__main__":
    # Quick test of the tool system
    import sys

    logging.basicConfig(level=logging.INFO)

    # Initialize with current directory
    tools = ToolSystem()

    print("=== Tool System Test ===\n")

    # Test 1: List current directory
    print("1. Listing current directory:")
    result = tools.list_directory(".", "*.py")
    print(f"   Found {result.get('count', 0)} Python files")

    # Test 2: Read this file
    print("\n2. Reading this file (tool_system.py):")
    result = tools.read_file("backend/tool_system.py")
    if result["success"]:
        print(f"   Successfully read {result['size']} bytes")

    # Test 3: Search for a pattern
    print("\n3. Searching for 'ToolSystem' class:")
    result = tools.search_code("class ToolSystem", "backend", "*.py")
    print(f"   Found {result.get('count', 0)} matches")

    # Test 4: Get file info
    print("\n4. Getting file info:")
    result = tools.get_file_info("backend/tool_system.py")
    if result["success"]:
        print(f"   Size: {result['size']} bytes")
        print(f"   Type: {result['type']}")

    print("\n=== All tests completed ===")

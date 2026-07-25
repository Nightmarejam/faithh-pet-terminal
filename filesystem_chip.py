#!/usr/bin/env python3
"""
FAITHH Filesystem Chip - Battle Chip for file operations.
Integrates filesystem_agent into FAITHH's chip system.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

try:
    from filesystem_agent import FilesystemAgent, OperationResult
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from filesystem_agent import FilesystemAgent, OperationResult


@dataclass
class ChipResult:
    success: bool
    message: str
    data: Any = None
    suggestions: List[str] = None


class FilesystemChip:
    NAME = "filesystem"
    DESCRIPTION = "File and folder management"
    VERSION = "1.0.0"
    
    INTENT_PATTERNS = {
        "list": [r"list\s+(.+)", r"show\s+(.+)", r"what(?:'s|\s+is)\s+in\s+(.+)", r"ls\s+(.+)"],
        "read": [r"read\s+(.+)", r"cat\s+(.+)", r"open\s+(.+)"],
        "move": [r"move\s+(.+)\s+to\s+(.+)", r"mv\s+(.+)\s+(.+)"],
        "copy": [r"copy\s+(.+)\s+to\s+(.+)", r"cp\s+(.+)\s+(.+)"],
        "delete": [r"delete\s+(.+)", r"remove\s+(.+)", r"rm\s+(.+)"],
        "organize": [r"organize\s+(.+)", r"clean\s+up\s+(.+)", r"sort\s+(.+)"],
        "mkdir": [r"create\s+(?:folder|directory)\s+(.+)", r"mkdir\s+(.+)"],
        "search": [r"find\s+(.+)\s+in\s+(.+)", r"search\s+(.+)\s+in\s+(.+)"]
    }
    
    def __init__(self, agent: FilesystemAgent = None):
        self.agent = agent or FilesystemAgent()
        self.last_result = None
    
    def execute(self, params: Dict) -> ChipResult:
        action = params.get("action", "").lower()
        path = params.get("path", "")
        dest = params.get("dest", "")
        content = params.get("content", "")
        options = params.get("options", {})
        
        handlers = {
            "list": self._handle_list,
            "read": self._handle_read,
            "write": self._handle_write,
            "move": self._handle_move,
            "copy": self._handle_copy,
            "delete": self._handle_delete,
            "metadata": self._handle_metadata,
            "mkdir": self._handle_mkdir,
            "organize": self._handle_organize,
            "search": self._handle_search,
            "status": self._handle_status,
            "exec": self._handle_exec
        }
        
        handler = handlers.get(action)
        if not handler:
            return ChipResult(False, f"Unknown action: {action}", suggestions=list(handlers.keys()))
        
        return handler(path, dest, content, options)
    
    def parse_natural_language(self, text: str) -> Tuple[str, Dict]:
        text = text.strip().lower()
        for action, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                match = re.match(pattern, text, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    params = {"action": action}
                    if len(groups) >= 1:
                        params["path"] = groups[0].strip()
                    if len(groups) >= 2:
                        params["dest"] = groups[1].strip()
                    return action, params
        return None, {}
    
    def execute_natural(self, text: str) -> ChipResult:
        action, params = self.parse_natural_language(text)
        if not action:
            return ChipResult(False, f"Could not understand: {text}",
                suggestions=["list ~/Downloads", "organize ~/Downloads", "move file.txt to ~/Documents"])
        return self.execute(params)
    
    def _handle_list(self, path, dest, content, options) -> ChipResult:
        if not path:
            path = "."
        depth = options.get("depth", 1)
        include_hidden = options.get("include_hidden", False)
        result = self.agent.list_directory(path, depth=depth, include_hidden=include_hidden)
        self.last_result = result
        if result.success:
            items = result.data or []
            dirs = sum(1 for i in items if i.get("type") == "DIR")
            files = sum(1 for i in items if i.get("type") == "FILE")
            formatted = [f"{'📁' if i.get('type')=='DIR' else '📄'} {i.get('name')}" for i in items[:30]]
            if len(items) > 30:
                formatted.append(f"... and {len(items) - 30} more")
            return ChipResult(True, f"Found {dirs} folders, {files} files", data={"items": items, "formatted": formatted})
        return ChipResult(False, result.message, suggestions=["Check path exists"])
    
    def _handle_read(self, path, dest, content, options) -> ChipResult:
        if not path:
            return ChipResult(False, "No file path provided")
        result = self.agent.read_file(path, max_lines=options.get("max_lines", 100))
        self.last_result = result
        return ChipResult(result.success, result.message, data=result.data)
    
    def _handle_write(self, path, dest, content, options) -> ChipResult:
        if not path or not content:
            return ChipResult(False, "Path and content required")
        result = self.agent.write_file(path, content, mode=options.get("mode", "write"))
        self.last_result = result
        return ChipResult(result.success, result.message)
    
    def _handle_move(self, path, dest, content, options) -> ChipResult:
        if not path or not dest:
            return ChipResult(False, "Source and destination required")
        result = self.agent.move_file(path, dest)
        self.last_result = result
        return ChipResult(result.success, result.message)
    
    def _handle_copy(self, path, dest, content, options) -> ChipResult:
        if not path or not dest:
            return ChipResult(False, "Source and destination required")
        result = self.agent.copy_file(path, dest)
        self.last_result = result
        return ChipResult(result.success, result.message)
    
    def _handle_delete(self, path, dest, content, options) -> ChipResult:
        if not path:
            return ChipResult(False, "Path required")
        if not options.get("confirm", False):
            return ChipResult(False, f"Confirm deletion of {path}?", 
                data={"requires_confirmation": True, "path": path})
        result = self.agent.delete_file(path)
        self.last_result = result
        return ChipResult(result.success, result.message)
    
    def _handle_mkdir(self, path, dest, content, options) -> ChipResult:
        if not path:
            return ChipResult(False, "Path required")
        result = self.agent.create_directory(path)
        self.last_result = result
        return ChipResult(result.success, result.message)
    
    def _handle_organize(self, path, dest, content, options) -> ChipResult:
        if not path:
            path = str(Path.home() / "Downloads")
        dry_run = options.get("dry_run", True)
        result = self.agent.organize_directory(path, dry_run=dry_run)
        self.last_result = result
        if result.success:
            plan = result.data or []
            categories = {}
            for item in plan:
                cat = item.get("category", "other")
                categories[cat] = categories.get(cat, 0) + 1
            summary = ", ".join(f"{v} {k}" for k, v in categories.items())
            return ChipResult(True, f"{'Would organize' if dry_run else 'Organized'}: {summary}",
                data={"plan": plan, "categories": categories, "dry_run": dry_run})
        return ChipResult(False, result.message)
    
    def _handle_search(self, path, dest, content, options) -> ChipResult:
        pattern = path
        search_dir = dest or str(Path.home())
        if not pattern:
            return ChipResult(False, "Search pattern required")
        limit = options.get("limit", 50)
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            limit = 50
        command = f"find {search_dir} -name '{pattern}' -type f 2>/dev/null | head -{limit}"
        result = self.agent.execute_command(command, timeout=10)
        if result.success and result.data:
            files = [f for f in result.data.strip().split('\n') if f]
            return ChipResult(True, f"Found {len(files)} files matching '{pattern}'", data=files)
        return ChipResult(True, f"No files found matching '{pattern}'", data=[])

    def _handle_metadata(self, path, dest, content, options) -> ChipResult:
        if not path:
            return ChipResult(False, "Path required")
        result = self.agent.get_metadata(path)
        self.last_result = result
        return ChipResult(result.success, result.message, data=result.data)
    
    def _handle_status(self, path, dest, content, options) -> ChipResult:
        stats = self.agent.get_stats()
        audit = self.agent.get_audit_log(last_n=5)
        return ChipResult(True, "Agent status", data={"stats": stats, "recent": audit})
    
    def _handle_exec(self, path, dest, content, options) -> ChipResult:
        if not path:
            return ChipResult(False, "No command provided")
        result = self.agent.execute_command(path, timeout=options.get("timeout", 30))
        self.last_result = result
        return ChipResult(result.success, result.message, data=result.data)
    
    def get_capabilities(self) -> Dict:
        return {
            "name": self.NAME,
            "description": self.DESCRIPTION,
            "actions": {
                "list": "List directory", "read": "Read file", "write": "Write file",
                "move": "Move file/folder", "copy": "Copy file/folder", "delete": "Delete",
                "metadata": "File metadata", "mkdir": "Create directory", "organize": "Smart organize",
                "search": "Find files", "exec": "Run command", "status": "Agent status"
            }
        }


if __name__ == "__main__":
    print("FAITHH Filesystem Chip - Test")
    chip = FilesystemChip()
    
    # Test natural language
    tests = ["list ~/Downloads", "organize my Downloads", "find *.pdf in ~/Documents"]
    for cmd in tests:
        action, params = chip.parse_natural_language(cmd)
        print(f"'{cmd}' -> {action}: {params}")
    
    # Test execution
    result = chip.execute({"action": "list", "path": str(Path.home() / "Downloads")})
    print(f"\nList result: {result.success} - {result.message}")

#!/usr/bin/env python3
"""
FAITHH Filesystem Agent
Provides file management capabilities similar to Claude's Desktop Commander.
"""

import os
import sys
import shutil
import subprocess
import hashlib
import json
import platform
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("faithh.filesystem")


class OperationType(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    MOVE = "move"
    COPY = "copy"
    CREATE_DIR = "create_dir"
    EXECUTE = "execute"
    LIST = "list"
    METADATA = "metadata"


@dataclass
class OperationResult:
    success: bool
    operation: OperationType
    path: str
    message: str
    data: Optional[any] = None
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class FilesystemAgent:
    DEFAULT_BLOCKED_COMMANDS = [
        "rm -rf /", "mkfs", "format", "dd if=", "fdisk",
        "sudo rm", "del /f /s /q", ":(){:|:&};:",
        "chmod -R 777 /", "chown -R", "> /dev/sda"
    ]
    
    FILE_CATEGORIES = {
        "documents": [".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt", ".pages"],
        "spreadsheets": [".xlsx", ".xls", ".csv", ".numbers", ".ods"],
        "presentations": [".pptx", ".ppt", ".key", ".odp"],
        "images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".tiff", ".heic"],
        "audio": [".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg", ".aiff"],
        "video": [".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"],
        "code": [".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".h", ".rb", ".go", ".rs"],
        "archives": [".zip", ".tar", ".gz", ".rar", ".7z", ".dmg"],
        "data": [".json", ".yaml", ".yml", ".xml", ".sql", ".db", ".sqlite"],
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        self.platform = platform.system().lower()
        self.home = Path.home()
        self.config_path = config_path or self.home / ".faithh" / "filesystem_config.json"
        self.audit_log_path = self.home / ".faithh" / "filesystem_audit.jsonl"
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()
        self.stats = {"operations": 0, "successes": 0, "failures": 0, "bytes_moved": 0}
    
    def _load_config(self) -> Dict:
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        config = {
            "allowed_directories": [str(self.home), "/tmp"],
            "blocked_commands": self.DEFAULT_BLOCKED_COMMANDS,
            "audit_enabled": True,
            "max_file_size_mb": 100,
            "device_name": platform.node(),
            "platform": self.platform
        }
        self._save_config(config)
        return config
    
    def _save_config(self, config: Dict = None):
        config = config or self.config
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _audit_log(self, result: OperationResult):
        if not self.config.get("audit_enabled", True):
            return
        log_entry = {
            "timestamp": result.timestamp,
            "operation": result.operation.value,
            "path": result.path,
            "success": result.success,
            "message": result.message,
            "error": result.error
        }
        with open(self.audit_log_path, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def _is_path_allowed(self, path: Path) -> bool:
        path = Path(path).resolve()
        allowed = self.config.get("allowed_directories", [])
        if not allowed:
            return True
        for allowed_dir in allowed:
            try:
                path.relative_to(allowed_dir)
                return True
            except ValueError:
                continue
        return False
    
    def _is_command_blocked(self, command: str) -> bool:
        command_lower = command.lower()
        for blocked in self.config.get("blocked_commands", []):
            if blocked.lower() in command_lower:
                return True
        return False

    def list_directory(self, path: str, depth: int = 1, include_hidden: bool = False) -> OperationResult:
        path = Path(path).expanduser().resolve()
        if not self._is_path_allowed(path):
            return OperationResult(False, OperationType.LIST, str(path), "Access denied", error="Path not allowed")
        if not path.exists():
            return OperationResult(False, OperationType.LIST, str(path), "Path not found", error="Not found")
        try:
            items = []
            self._list_recursive(path, items, depth, include_hidden, 0)
            result = OperationResult(True, OperationType.LIST, str(path), f"Listed {len(items)} items", data=items)
            self._audit_log(result)
            return result
        except Exception as e:
            return OperationResult(False, OperationType.LIST, str(path), "Failed", error=str(e))
    
    def _list_recursive(self, path: Path, items: List, max_depth: int, include_hidden: bool, current_depth: int):
        if current_depth >= max_depth:
            return
        try:
            for item in sorted(path.iterdir()):
                if not include_hidden and item.name.startswith('.'):
                    continue
                items.append({
                    "type": "DIR" if item.is_dir() else "FILE",
                    "name": item.name,
                    "path": str(item),
                    "size": item.stat().st_size if item.is_file() else None,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
                if item.is_dir() and current_depth + 1 < max_depth:
                    self._list_recursive(item, items, max_depth, include_hidden, current_depth + 1)
        except PermissionError:
            pass

    def read_file(self, path: str, max_lines: int = 1000) -> OperationResult:
        path = Path(path).expanduser().resolve()
        if not self._is_path_allowed(path):
            return OperationResult(False, OperationType.READ, str(path), "Access denied", error="Path not allowed")
        if not path.exists():
            return OperationResult(False, OperationType.READ, str(path), "Not found", error="File not found")
        try:
            with open(path, 'r', errors='replace') as f:
                lines = [line for i, line in enumerate(f) if i < max_lines]
            result = OperationResult(True, OperationType.READ, str(path), f"Read {len(lines)} lines", data=''.join(lines))
            self._audit_log(result)
            return result
        except Exception as e:
            return OperationResult(False, OperationType.READ, str(path), "Failed", error=str(e))

    def get_metadata(self, path: str) -> OperationResult:
        path = Path(path).expanduser().resolve()
        if not self._is_path_allowed(path):
            return OperationResult(False, OperationType.METADATA, str(path), "Access denied", error="Path not allowed")
        if not path.exists():
            return OperationResult(False, OperationType.METADATA, str(path), "Not found", error="File not found")
        try:
            stat = path.stat()
            data = {
                "path": str(path),
                "type": "directory" if path.is_dir() else "file",
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "created": stat.st_ctime,
                "readable": os.access(path, os.R_OK),
                "writable": os.access(path, os.W_OK),
            }
            result = OperationResult(True, OperationType.METADATA, str(path), "Metadata", data=data)
            self._audit_log(result)
            return result
        except Exception as e:
            return OperationResult(False, OperationType.METADATA, str(path), "Failed", error=str(e))

    def write_file(self, path: str, content: str, mode: str = "write") -> OperationResult:
        path = Path(path).expanduser().resolve()
        if not self._is_path_allowed(path):
            return OperationResult(False, OperationType.WRITE, str(path), "Access denied", error="Path not allowed")
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'a' if mode == "append" else 'w') as f:
                f.write(content)
            result = OperationResult(True, OperationType.WRITE, str(path), f"Wrote {len(content)} chars")
            self._audit_log(result)
            self.stats["operations"] += 1
            self.stats["successes"] += 1
            return result
        except Exception as e:
            self.stats["failures"] += 1
            return OperationResult(False, OperationType.WRITE, str(path), "Failed", error=str(e))

    def move_file(self, source: str, destination: str) -> OperationResult:
        source = Path(source).expanduser().resolve()
        destination = Path(destination).expanduser().resolve()
        if not self._is_path_allowed(source) or not self._is_path_allowed(destination):
            return OperationResult(False, OperationType.MOVE, str(source), "Access denied", error="Path not allowed")
        if not source.exists():
            return OperationResult(False, OperationType.MOVE, str(source), "Source not found", error="Not found")
        try:
            if source.is_file():
                self.stats["bytes_moved"] += source.stat().st_size
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
            result = OperationResult(True, OperationType.MOVE, str(source), f"Moved to {destination}")
            self._audit_log(result)
            self.stats["operations"] += 1
            self.stats["successes"] += 1
            return result
        except Exception as e:
            self.stats["failures"] += 1
            return OperationResult(False, OperationType.MOVE, str(source), "Failed", error=str(e))

    def copy_file(self, source: str, destination: str) -> OperationResult:
        source = Path(source).expanduser().resolve()
        destination = Path(destination).expanduser().resolve()
        if not self._is_path_allowed(source) or not self._is_path_allowed(destination):
            return OperationResult(False, OperationType.COPY, str(source), "Access denied", error="Path not allowed")
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(str(source), str(destination))
            else:
                shutil.copy2(str(source), str(destination))
            result = OperationResult(True, OperationType.COPY, str(source), f"Copied to {destination}")
            self._audit_log(result)
            return result
        except Exception as e:
            return OperationResult(False, OperationType.COPY, str(source), "Failed", error=str(e))

    def delete_file(self, path: str, confirm: bool = True) -> OperationResult:
        path = Path(path).expanduser().resolve()
        if not self._is_path_allowed(path):
            return OperationResult(False, OperationType.DELETE, str(path), "Access denied", error="Path not allowed")
        protected = [self.home, Path("/"), Path("/Users"), Path("/home")]
        if path in protected:
            return OperationResult(False, OperationType.DELETE, str(path), "Protected path", error="Cannot delete")
        try:
            if path.is_dir():
                shutil.rmtree(str(path))
            else:
                path.unlink()
            result = OperationResult(True, OperationType.DELETE, str(path), "Deleted")
            self._audit_log(result)
            return result
        except Exception as e:
            return OperationResult(False, OperationType.DELETE, str(path), "Failed", error=str(e))

    def create_directory(self, path: str) -> OperationResult:
        path = Path(path).expanduser().resolve()
        if not self._is_path_allowed(path):
            return OperationResult(False, OperationType.CREATE_DIR, str(path), "Access denied", error="Path not allowed")
        try:
            path.mkdir(parents=True, exist_ok=True)
            result = OperationResult(True, OperationType.CREATE_DIR, str(path), "Created")
            self._audit_log(result)
            return result
        except Exception as e:
            return OperationResult(False, OperationType.CREATE_DIR, str(path), "Failed", error=str(e))

    def execute_command(self, command: str, timeout: int = 30) -> OperationResult:
        if self._is_command_blocked(command):
            return OperationResult(False, OperationType.EXECUTE, command, "Blocked", error="Command not allowed")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
            output = result.stdout + result.stderr
            success = result.returncode == 0
            op_result = OperationResult(success, OperationType.EXECUTE, command, f"Exit: {result.returncode}", data=output, error=result.stderr if not success else None)
            self._audit_log(op_result)
            return op_result
        except subprocess.TimeoutExpired:
            return OperationResult(False, OperationType.EXECUTE, command, "Timeout", error=f"Timeout after {timeout}s")
        except Exception as e:
            return OperationResult(False, OperationType.EXECUTE, command, "Failed", error=str(e))

    def categorize_file(self, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        for category, extensions in self.FILE_CATEGORIES.items():
            if ext in extensions:
                return category
        return "other"

    def organize_directory(self, source_dir: str, target_dir: str = None, dry_run: bool = True) -> OperationResult:
        source = Path(source_dir).expanduser().resolve()
        target = Path(target_dir).expanduser().resolve() if target_dir else source
        if not self._is_path_allowed(source):
            return OperationResult(False, OperationType.MOVE, str(source), "Access denied", error="Path not allowed")
        plan = []
        try:
            for item in source.iterdir():
                if item.is_file() and not item.name.startswith('.'):
                    category = self.categorize_file(item.name)
                    dest_file = target / category / item.name
                    plan.append({"source": str(item), "destination": str(dest_file), "category": category})
            if dry_run:
                return OperationResult(True, OperationType.LIST, str(source), f"Would organize {len(plan)} files", data=plan)
            moved = 0
            for item in plan:
                dest_path = Path(item["destination"])
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(item["source"], str(dest_path))
                moved += 1
            result = OperationResult(True, OperationType.MOVE, str(source), f"Organized {moved} files", data=plan)
            self._audit_log(result)
            return result
        except Exception as e:
            return OperationResult(False, OperationType.MOVE, str(source), "Failed", error=str(e))

    def get_stats(self) -> Dict:
        return {**self.stats, "platform": self.platform, "home": str(self.home)}

    def get_audit_log(self, last_n: int = 20) -> List[Dict]:
        if not self.audit_log_path.exists():
            return []
        entries = []
        with open(self.audit_log_path) as f:
            for line in f:
                entries.append(json.loads(line))
        return entries[-last_n:]


if __name__ == "__main__":
    print("FAITHH Filesystem Agent - Test")
    agent = FilesystemAgent()
    result = agent.list_directory(str(Path.home() / "Downloads"), depth=1)
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    if result.data:
        for item in result.data[:10]:
            print(f"  [{item['type']}] {item['name']}")

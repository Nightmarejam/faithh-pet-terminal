# Passive Collection System Specification (Patched)

**Date:** 2026-01-15 (Updated: 2026-01-16)
**For:** Windsurf + GPT 5.2 Codex XHigh
**Goal:** Auto-capture system activity so AI assistants always have current context

---

## Overview

Build a passive collection layer that captures git activity, file changes, terminal commands, and system health - writing to standardized JSON files that feed into the existing synthesis pipeline.

**Design Principles:**
- Zero manual overhead for Jonathan
- Machine-readable outputs (JSON primary, markdown secondary)
- Incremental updates (don't reprocess everything each run)
- Fail gracefully (one collector failing shouldn't break others)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     PASSIVE COLLECTORS                          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Git Collector│  │File Collector│  │Health Checker│          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         ▼                 ▼                 ▼                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              collectors/state/                           │   │
│  │  git.json | file_changes.json | health.json | terminal.json│
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              AGGREGATOR                                  │   │
│  │  Combines all collector outputs into unified state       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  parity/system_state_latest.json (existing)             │   │
│  │  collectors/daily/YYYY-MM-DD.json (new)                 │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Naming Convention (IMPORTANT)

**Collector output files use the collector's `name` attribute:**
- Git collector: `name = "git"` → outputs to `git.json`
- File collector: `name = "file_changes"` → outputs to `file_changes.json`
- Health collector: `name = "health"` → outputs to `health.json`
- Terminal collector: `name = "terminal"` → outputs to `terminal.json`

**Daily snapshots:** `collectors/daily/YYYY-MM-DD.json` (e.g., `2026-01-15.json`)

This ensures the aggregator can find files using `{collector_name}.json` pattern.

---

## Directory Structure

```
~/ai-stack/
├── scripts/
│   └── collectors/
│       ├── __init__.py            # Package marker + exports
│       ├── base_collector.py      # Abstract base class
│       ├── git_collector.py       # Git activity
│       ├── file_collector.py      # File changes
│       ├── health_collector.py    # Service health
│       ├── terminal_collector.py  # Command history (optional)
│       ├── aggregator.py          # Combines all outputs
│       └── run_collectors.py      # Main entry point
│
├── collectors/                    # Output directory
│   ├── state/                     # Latest state from each collector
│   │   ├── git.json               # <- matches collector name
│   │   ├── file_changes.json      # <- matches collector name
│   │   ├── health.json            # <- matches collector name
│   │   └── terminal.json          # <- matches collector name
│   ├── daily/                     # Daily snapshots
│   │   └── 2026-01-15.json        # <- YYYY-MM-DD.json format
│   └── config.json                # Collector configuration
│
├── logs/                          # Log directory (create if missing)
│   └── collectors.log
```

---

## Collector Specifications

### 1. Git Collector (`git_collector.py`)

**Purpose:** Capture recent git activity for AI context

**Triggers:** On-demand, cron (every 4 hours), or pre-commit hook

**Output:** `collectors/state/git.json`

```json
{
  "collected_at": "2026-01-15T16:30:00Z",
  "collector": "git",
  "version": "1.0",
  "success": true,
  "data": {
    "repository": {
      "name": "ai-stack",
      "branch": "main",
      "remote": "origin",
      "remote_url": "github.com:Nightmarejam/faithh-pet-terminal.git"
    },
    "status": {
      "is_dirty": true,
      "ahead": 3,
      "behind": 0,
      "staged_count": 0,
      "modified_count": 43,
      "untracked_count": 25
    },
    "recent_commits": [
      {
        "hash": "abc1234",
        "short_hash": "abc1234",
        "message": "Reconcile UI + fix model references",
        "author": "Jonathan",
        "date": "2026-01-13T10:00:00Z",
        "files_changed": 5
      }
    ],
    "modified_files": [
      {
        "path": "faithh_pet_v4.html",
        "status": "modified",
        "category": "ui"
      },
      {
        "path": "docs/MASTER_CONTEXT.md",
        "status": "modified", 
        "category": "documentation"
      }
    ],
    "file_categories": {
      "ui": 2,
      "backend": 1,
      "documentation": 15,
      "config": 3,
      "data": 5
    }
  }
}
```

**Implementation:**
```python
# scripts/collectors/git_collector.py

from .base_collector import BaseCollector
import subprocess
import re

class GitCollector(BaseCollector):
    name = "git"  # Output: git.json
    
    def collect(self) -> dict:
        return {
            "repository": self._get_repo_info(),
            "status": self._get_status(),
            "recent_commits": self._get_recent_commits(limit=10),
            "modified_files": self._get_modified_files(),
            "file_categories": self._categorize_files(),
        }
    
    def _get_repo_info(self) -> dict:
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"], text=True
        ).strip()
        remote_url = subprocess.check_output(
            ["git", "remote", "get-url", "origin"], text=True
        ).strip()
        return {
            "name": "ai-stack",
            "branch": branch,
            "remote": "origin",
            "remote_url": remote_url
        }
    
    def _get_status(self) -> dict:
        status = subprocess.check_output(
            ["git", "status", "--porcelain", "-b"], text=True
        )
        lines = status.strip().split('\n')
        
        # Parse branch line for ahead/behind
        branch_line = lines[0] if lines else ""
        ahead = 0
        behind = 0
        if "ahead" in branch_line:
            match = re.search(r'ahead (\d+)', branch_line)
            if match:
                ahead = int(match.group(1))
        if "behind" in branch_line:
            match = re.search(r'behind (\d+)', branch_line)
            if match:
                behind = int(match.group(1))
        
        # Count file statuses
        modified = staged = untracked = 0
        for line in lines[1:]:
            if line.startswith('??'):
                untracked += 1
            elif line[0] != ' ':
                staged += 1
            elif line[1] != ' ':
                modified += 1
        
        return {
            "is_dirty": len(lines) > 1,
            "ahead": ahead,
            "behind": behind,
            "staged_count": staged,
            "modified_count": modified,
            "untracked_count": untracked
        }
    
    def _get_recent_commits(self, limit: int = 10) -> list:
        log = subprocess.check_output([
            "git", "log", f"-{limit}",
            "--format=%H|%h|%s|%an|%aI|%ct"
        ], text=True)
        
        commits = []
        for line in log.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|')
            if len(parts) >= 5:
                commits.append({
                    "hash": parts[0],
                    "short_hash": parts[1],
                    "message": parts[2],
                    "author": parts[3],
                    "date": parts[4]
                })
        return commits
    
    def _get_modified_files(self) -> list:
        status = subprocess.check_output(
            ["git", "status", "--porcelain"], text=True
        )
        
        files = []
        for line in status.strip().split('\n'):
            if not line:
                continue
            status_code = line[:2]
            path = line[3:]
            
            file_status = "modified"
            if status_code.startswith('?'):
                file_status = "untracked"
            elif status_code.startswith('A'):
                file_status = "added"
            elif status_code.startswith('D'):
                file_status = "deleted"
            
            files.append({
                "path": path,
                "status": file_status,
                "category": self._categorize_file(path)
            })
        return files
    
    def _categorize_file(self, path: str) -> str:
        if path.endswith(('.html', '.css', '.js')):
            return "ui"
        elif path.endswith('.py'):
            return "backend"
        elif path.endswith('.md') or path.startswith('docs/'):
            return "documentation"
        elif path.endswith(('.json', '.yaml', '.yml', '.env')):
            return "config"
        return "other"
    
    def _categorize_files(self) -> dict:
        files = self._get_modified_files()
        categories = {}
        for f in files:
            cat = f["category"]
            categories[cat] = categories.get(cat, 0) + 1
        return categories
```

---

### 2. File Collector (`file_collector.py`)

**Purpose:** Track file changes since last collection

**Triggers:** Cron (every hour), or on-demand

**Output:** `collectors/state/file_changes.json`

```json
{
  "collected_at": "2026-01-15T16:30:00Z",
  "collector": "file_changes",
  "version": "1.0",
  "success": true,
  "data": {
    "since": "2026-01-15T12:30:00Z",
    "watched_paths": [
      "/home/jonat/ai-stack/"
    ],
    "changes": [
      {
        "path": "project_states.json",
        "type": "modified",
        "mtime": "2026-01-15T15:00:00Z",
        "size_bytes": 4523,
        "category": "state"
      }
    ],
    "summary": {
      "total_changes": 12,
      "by_type": {
        "modified": 8,
        "created": 3,
        "deleted": 1
      },
      "by_category": {
        "state": 2,
        "documentation": 5,
        "code": 3,
        "other": 2
      }
    },
    "notable_files": [
      {
        "path": "project_states.json",
        "reason": "Source of truth updated"
      }
    ]
  }
}
```

**Implementation:**
```python
# scripts/collectors/file_collector.py

from .base_collector import BaseCollector
from pathlib import Path
from datetime import datetime
import os

class FileCollector(BaseCollector):
    name = "file_changes"  # Output: file_changes.json
    
    # Files to always highlight when changed
    NOTABLE_FILES = {
        "project_states.json": "Source of truth updated",
        "faithh_professional_backend_fixed.py": "Core backend modified",
        "faithh_pet_v4.html": "Main UI modified",
        "MASTER_CONTEXT.md": "Context documentation updated",
        ".env": "Environment configuration changed"
    }
    
    # Directories/patterns to ignore
    IGNORE_PATTERNS = [
        '__pycache__', '.git', 'node_modules', '*.pyc', 
        '.venv', 'venv', '*.log', 'collectors/state',
        'worktrees'
    ]
    
    def collect(self) -> dict:
        previous = self.load_previous()
        since = previous.get("collected_at", "1970-01-01T00:00:00Z")
        since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
        
        root = Path.home() / "ai-stack"
        changes = []
        
        for path in root.rglob("*"):
            if self._should_ignore(path):
                continue
            if not path.is_file():
                continue
            
            try:
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                if mtime > since_dt.replace(tzinfo=None):
                    changes.append({
                        "path": str(path.relative_to(root)),
                        "type": "modified",
                        "mtime": mtime.isoformat(),
                        "size_bytes": path.stat().st_size,
                        "category": self._categorize(path)
                    })
            except (OSError, ValueError):
                continue
        
        return {
            "since": since,
            "watched_paths": [str(root)],
            "changes": changes,
            "summary": self._build_summary(changes),
            "notable_files": self._find_notable(changes)
        }
    
    def _should_ignore(self, path: Path) -> bool:
        path_str = str(path)
        for pattern in self.IGNORE_PATTERNS:
            if pattern in path_str:
                return True
        return False
    
    def _categorize(self, path: Path) -> str:
        name = path.name
        if name in ["project_states.json", "decisions_log.json", "work_log.json"]:
            return "state"
        elif path.suffix == ".md":
            return "documentation"
        elif path.suffix == ".py":
            return "code"
        elif path.suffix in [".html", ".css", ".js"]:
            return "ui"
        elif path.suffix == ".json":
            return "config"
        return "other"
    
    def _build_summary(self, changes: list) -> dict:
        by_type = {}
        by_category = {}
        for c in changes:
            t = c["type"]
            cat = c["category"]
            by_type[t] = by_type.get(t, 0) + 1
            by_category[cat] = by_category.get(cat, 0) + 1
        
        return {
            "total_changes": len(changes),
            "by_type": by_type,
            "by_category": by_category
        }
    
    def _find_notable(self, changes: list) -> list:
        notable = []
        for c in changes:
            filename = Path(c["path"]).name
            if filename in self.NOTABLE_FILES:
                notable.append({
                    "path": c["path"],
                    "reason": self.NOTABLE_FILES[filename]
                })
        return notable
```

---

### 3. Health Collector (`health_collector.py`)

**Purpose:** Check service health across infrastructure

**Triggers:** Cron (every 15 minutes), or on-demand

**Output:** `collectors/state/health.json`

```json
{
  "collected_at": "2026-01-15T16:30:00Z",
  "collector": "health",
  "version": "1.0",
  "success": true,
  "data": {
    "overall_status": "degraded",
    "services": {
      "faithh_backend": {
        "url": "http://localhost:5557",
        "status": "healthy",
        "response_time_ms": 45,
        "version": "v3.4-filesystem"
      },
      "ollama": {
        "url": "http://localhost:11434",
        "status": "healthy",
        "response_time_ms": 12,
        "models": ["llama31-faithh:latest", "qwen3-faithh:latest"]
      },
      "chromadb_gen8": {
        "url": "http://192.158.1.243:8000",
        "status": "degraded",
        "response_time_ms": 89,
        "reachable": true,
        "connected": false,
        "documents": 0,
        "expected_documents": 28876,
        "issue": "Collection not connecting despite server reachable"
      }
    },
    "issues": [
      {
        "service": "chromadb_gen8",
        "severity": "high",
        "message": "ChromaDB showing 0 documents, expected 28,876",
        "suggested_action": "Check collection name or API version"
      }
    ]
  }
}
```

**Implementation:**
```python
# scripts/collectors/health_collector.py

from .base_collector import BaseCollector
import requests
import time

class HealthCollector(BaseCollector):
    name = "health"  # Output: health.json
    
    SERVICES = {
        "faithh_backend": {
            "url": "http://localhost:5557/health",
            "type": "http"
        },
        "ollama": {
            "url": "http://localhost:11434/api/tags",
            "type": "http"
        },
        "chromadb_gen8": {
            "url": "http://192.158.1.243:8000/api/v2/heartbeat",
            "type": "chromadb",
            "expected_docs": 28876
        }
    }
    
    def collect(self) -> dict:
        services = {}
        issues = []
        
        for name, config in self.SERVICES.items():
            result = self._check_service(name, config)
            services[name] = result
            
            if result["status"] != "healthy":
                issues.append(self._create_issue(name, result))
        
        return {
            "overall_status": self._compute_overall(services),
            "services": services,
            "issues": issues
        }
    
    def _check_service(self, name: str, config: dict) -> dict:
        url = config["url"]
        result = {
            "url": url,
            "status": "unknown",
            "response_time_ms": 0
        }
        
        try:
            start = time.time()
            response = requests.get(url, timeout=10)
            result["response_time_ms"] = int((time.time() - start) * 1000)
            
            if response.status_code == 200:
                result["status"] = "healthy"
                data = response.json()
                
                # Service-specific parsing
                if name == "faithh_backend":
                    result["version"] = data.get("service", "").split()[-1]
                
                elif name == "ollama":
                    models = [m["name"] for m in data.get("models", [])]
                    result["models"] = models
                
                elif name == "chromadb_gen8":
                    result["reachable"] = True
                    # Check if we can get collections
                    try:
                        coll_resp = requests.get(
                            "http://192.158.1.243:8000/api/v2/collections",
                            timeout=5
                        )
                        if coll_resp.status_code == 200:
                            collections = coll_resp.json()
                            # Find our collection
                            for c in collections:
                                if c.get("name") == "faithh_knowledge_base":
                                    result["connected"] = True
                                    result["documents"] = c.get("count", 0)
                                    break
                            else:
                                result["connected"] = False
                                result["documents"] = 0
                                result["status"] = "degraded"
                                result["issue"] = "Collection not found"
                    except:
                        result["connected"] = False
                        result["status"] = "degraded"
            else:
                result["status"] = "error"
                result["error"] = f"HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            result["status"] = "timeout"
            result["error"] = "Connection timed out"
        except requests.exceptions.ConnectionError:
            result["status"] = "unreachable"
            result["error"] = "Connection refused"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def _compute_overall(self, services: dict) -> str:
        statuses = [s["status"] for s in services.values()]
        if all(s == "healthy" for s in statuses):
            return "healthy"
        elif any(s in ["unreachable", "error"] for s in statuses):
            return "critical"
        else:
            return "degraded"
    
    def _create_issue(self, name: str, result: dict) -> dict:
        return {
            "service": name,
            "severity": "high" if result["status"] in ["unreachable", "error"] else "medium",
            "message": result.get("issue") or result.get("error") or f"Status: {result['status']}",
            "suggested_action": self._suggest_action(name, result)
        }
    
    def _suggest_action(self, name: str, result: dict) -> str:
        if result["status"] == "unreachable":
            return f"Check if {name} service is running"
        elif name == "chromadb_gen8" and result.get("status") == "degraded":
            return "Check collection name matches 'faithh_knowledge_base'"
        return "Investigate service logs"
```

---

### 4. Terminal Collector (`terminal_collector.py`) [Optional]

**Purpose:** Capture recent terminal commands for context

**Output:** `collectors/state/terminal.json`

```python
# scripts/collectors/terminal_collector.py

from .base_collector import BaseCollector
from pathlib import Path
from datetime import datetime
import os

class TerminalCollector(BaseCollector):
    name = "terminal"  # Output: terminal.json
    
    # Patterns to filter out (security)
    SENSITIVE_PATTERNS = [
        'password', 'token', 'secret', 'key=', 'api_key',
        'AWS_', 'GROQ_', 'export ', 'ssh-add'
    ]
    
    def collect(self) -> dict:
        history_path = Path.home() / ".bash_history"
        
        if not history_path.exists():
            return {
                "error": "No bash history found",
                "commands": [],
                "summary": {}
            }
        
        commands = []
        with open(history_path, 'r', errors='ignore') as f:
            for line in f.readlines()[-100:]:  # Last 100 commands
                line = line.strip()
                if not line or self._is_sensitive(line):
                    continue
                commands.append({
                    "command": line,
                    "category": self._categorize(line)
                })
        
        return {
            "commands": commands[-50:],  # Return last 50 safe commands
            "summary": self._build_summary(commands)
        }
    
    def _is_sensitive(self, cmd: str) -> bool:
        cmd_lower = cmd.lower()
        return any(p in cmd_lower for p in self.SENSITIVE_PATTERNS)
    
    def _categorize(self, cmd: str) -> str:
        if cmd.startswith('git'):
            return "git"
        elif cmd.startswith(('cd', 'ls', 'pwd', 'cat', 'head', 'tail')):
            return "navigation"
        elif cmd.startswith(('python', 'pip')):
            return "python"
        elif cmd.startswith('curl'):
            return "http"
        elif cmd.startswith(('docker', 'docker-compose')):
            return "docker"
        return "other"
    
    def _build_summary(self, commands: list) -> dict:
        by_category = {}
        for c in commands:
            cat = c["category"]
            by_category[cat] = by_category.get(cat, 0) + 1
        return {
            "total_commands": len(commands),
            "by_category": by_category
        }
```

---

## Base Collector Class

```python
# scripts/collectors/base_collector.py

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
import json

class BaseCollector(ABC):
    """Base class for all passive collectors"""
    
    name: str = "base"
    version: str = "1.0"
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path.home() / "ai-stack" / "collectors" / "state"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def collect(self) -> dict:
        """Collect data and return as dict. Override in subclasses."""
        pass
    
    def run(self) -> dict:
        """Run collection and save output"""
        try:
            data = self.collect()
            output = {
                "collected_at": datetime.utcnow().isoformat() + "Z",
                "collector": self.name,
                "version": self.version,
                "success": True,
                "data": data
            }
        except Exception as e:
            output = {
                "collected_at": datetime.utcnow().isoformat() + "Z",
                "collector": self.name,
                "version": self.version,
                "success": False,
                "error": str(e),
                "data": {}
            }
        
        self._save(output)
        return output
    
    def _save(self, data: dict):
        """Save output to JSON file using collector name"""
        output_path = self.output_dir / f"{self.name}.json"
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_previous(self) -> dict:
        """Load previous collection for delta comparison"""
        output_path = self.output_dir / f"{self.name}.json"
        if output_path.exists():
            with open(output_path) as f:
                return json.load(f)
        return {}
```

---

## Package Init

```python
# scripts/collectors/__init__.py

"""
Passive Collection System for FAITHH

Usage:
    from scripts.collectors import GitCollector, HealthCollector, Aggregator
    
    # Run single collector
    result = GitCollector().run()
    
    # Aggregate all
    aggregated = Aggregator().aggregate()
"""

from .base_collector import BaseCollector
from .git_collector import GitCollector
from .file_collector import FileCollector
from .health_collector import HealthCollector
from .terminal_collector import TerminalCollector
from .aggregator import Aggregator

__all__ = [
    'BaseCollector',
    'GitCollector', 
    'FileCollector',
    'HealthCollector',
    'TerminalCollector',
    'Aggregator'
]
```

---

## Aggregator

```python
# scripts/collectors/aggregator.py

from datetime import datetime
from pathlib import Path
import json

class Aggregator:
    """Combines all collector outputs into unified state"""
    
    # Collector names must match the `name` attribute in each collector class
    COLLECTORS = ['git', 'file_changes', 'health', 'terminal']
    
    def __init__(self, collectors_dir: Path = None):
        self.collectors_dir = collectors_dir or Path.home() / "ai-stack" / "collectors"
        self.state_dir = self.collectors_dir / "state"
        self.daily_dir = self.collectors_dir / "daily"
        self.daily_dir.mkdir(parents=True, exist_ok=True)
    
    def aggregate(self) -> dict:
        """Combine all collector outputs"""
        aggregated = {
            "aggregated_at": datetime.utcnow().isoformat() + "Z",
            "collectors": {},
            "summary": {},
            "issues": [],
            "ai_context": {}
        }
        
        for collector in self.COLLECTORS:
            path = self.state_dir / f"{collector}.json"
            if path.exists():
                with open(path) as f:
                    data = json.load(f)
                    aggregated["collectors"][collector] = data
                    
                    # Collect issues from health collector
                    if collector == "health" and data.get("success"):
                        aggregated["issues"].extend(
                            data.get("data", {}).get("issues", [])
                        )
        
        # Build summary for AI
        aggregated["summary"] = self._build_summary(aggregated["collectors"])
        aggregated["ai_context"] = self._build_ai_context(aggregated)
        
        return aggregated
    
    def _build_summary(self, collectors: dict) -> dict:
        """Build human/AI readable summary"""
        summary = {
            "system_status": "unknown",
            "git_dirty": False,
            "files_changed_today": 0,
            "active_issues": 0
        }
        
        if "health" in collectors:
            health = collectors["health"].get("data", {})
            summary["system_status"] = health.get("overall_status", "unknown")
            summary["active_issues"] = len(health.get("issues", []))
        
        if "git" in collectors:
            git = collectors["git"].get("data", {})
            summary["git_dirty"] = git.get("status", {}).get("is_dirty", False)
        
        if "file_changes" in collectors:
            fc = collectors["file_changes"].get("data", {})
            summary["files_changed_today"] = fc.get("summary", {}).get("total_changes", 0)
        
        return summary
    
    def _build_ai_context(self, aggregated: dict) -> dict:
        """Build context packet optimized for AI consumption"""
        return {
            "status_line": self._generate_status_line(aggregated),
            "attention_needed": aggregated["issues"],
            "recent_activity": self._recent_activity_summary(aggregated),
            "suggested_actions": self._suggest_actions(aggregated)
        }
    
    def _generate_status_line(self, agg: dict) -> str:
        """One-line status for AI"""
        summary = agg.get("summary", {})
        status = summary.get("system_status", "unknown")
        issues = summary.get("active_issues", 0)
        dirty = "dirty" if summary.get("git_dirty") else "clean"
        
        return f"System: {status} | Git: {dirty} | Issues: {issues}"
    
    def _recent_activity_summary(self, agg: dict) -> dict:
        """Summarize recent activity"""
        activity = {}
        
        if "git" in agg["collectors"]:
            git_data = agg["collectors"]["git"].get("data", {})
            activity["commits_ahead"] = git_data.get("status", {}).get("ahead", 0)
            activity["modified_files"] = git_data.get("status", {}).get("modified_count", 0)
        
        if "file_changes" in agg["collectors"]:
            fc_data = agg["collectors"]["file_changes"].get("data", {})
            activity["files_changed"] = fc_data.get("summary", {}).get("total_changes", 0)
            activity["notable"] = fc_data.get("notable_files", [])
        
        return activity
    
    def _suggest_actions(self, agg: dict) -> list:
        """Generate suggested actions based on state"""
        actions = []
        
        summary = agg.get("summary", {})
        
        if summary.get("git_dirty"):
            ahead = 0
            if "git" in agg["collectors"]:
                ahead = agg["collectors"]["git"].get("data", {}).get("status", {}).get("ahead", 0)
            if ahead > 0:
                actions.append({
                    "priority": "medium",
                    "action": f"Push {ahead} commits to origin",
                    "command": "git push"
                })
        
        for issue in agg.get("issues", []):
            actions.append({
                "priority": issue.get("severity", "medium"),
                "action": issue.get("suggested_action", "Investigate"),
                "source": issue.get("service")
            })
        
        return actions
    
    def save_daily_snapshot(self) -> Path:
        """Save aggregated state as daily snapshot"""
        aggregated = self.aggregate()
        today = datetime.now().strftime("%Y-%m-%d")
        
        output_path = self.daily_dir / f"{today}.json"
        with open(output_path, 'w') as f:
            json.dump(aggregated, f, indent=2)
        
        return output_path
```

---

## Main Entry Point

```python
#!/usr/bin/env python3
# scripts/collectors/run_collectors.py

"""
Run all passive collectors and aggregate results.

Usage:
    python -m scripts.collectors.run_collectors              # Run all collectors
    python -m scripts.collectors.run_collectors --git        # Run only git collector
    python -m scripts.collectors.run_collectors --aggregate  # Only aggregate existing data
    python -m scripts.collectors.run_collectors --snapshot   # Create daily snapshot
    
Or from repo root:
    python scripts/collectors/run_collectors.py --all
"""

import argparse
import sys
from pathlib import Path

# Add parent to path for direct script execution
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.collectors.git_collector import GitCollector
from scripts.collectors.file_collector import FileCollector
from scripts.collectors.health_collector import HealthCollector
from scripts.collectors.terminal_collector import TerminalCollector
from scripts.collectors.aggregator import Aggregator

def main():
    parser = argparse.ArgumentParser(description='Run passive collectors')
    parser.add_argument('--git', action='store_true', help='Run git collector')
    parser.add_argument('--files', action='store_true', help='Run file collector')
    parser.add_argument('--health', action='store_true', help='Run health collector')
    parser.add_argument('--terminal', action='store_true', help='Run terminal collector')
    parser.add_argument('--aggregate', action='store_true', help='Aggregate results')
    parser.add_argument('--snapshot', action='store_true', help='Save daily snapshot')
    parser.add_argument('--all', action='store_true', help='Run all collectors')
    
    args = parser.parse_args()
    
    # Determine which collectors to run
    run_all = args.all or not any([
        args.git, args.files, args.health, args.terminal, 
        args.aggregate, args.snapshot
    ])
    
    results = {}
    
    if run_all or args.git:
        print("Running git collector...")
        results['git'] = GitCollector().run()
        print(f"  ✓ Saved to collectors/state/git.json")
    
    if run_all or args.files:
        print("Running file collector...")
        results['file_changes'] = FileCollector().run()
        print(f"  ✓ Saved to collectors/state/file_changes.json")
    
    if run_all or args.health:
        print("Running health collector...")
        results['health'] = HealthCollector().run()
        print(f"  ✓ Saved to collectors/state/health.json")
    
    if run_all or args.terminal:
        print("Running terminal collector...")
        results['terminal'] = TerminalCollector().run()
        print(f"  ✓ Saved to collectors/state/terminal.json")
    
    # Always aggregate after running collectors
    if run_all or args.aggregate or results:
        print("Aggregating results...")
        aggregator = Aggregator()
        aggregated = aggregator.aggregate()
        print(f"  Status: {aggregated['ai_context']['status_line']}")
    
    if args.snapshot or run_all:
        print("Saving daily snapshot...")
        aggregator = Aggregator()
        path = aggregator.save_daily_snapshot()
        print(f"  ✓ Snapshot saved to: {path}")
    
    print("\nDone!")
    return results

if __name__ == '__main__':
    main()
```

---

## Cron Setup

```bash
# Add to crontab (crontab -e)

# IMPORTANT: Use absolute paths to venv python
# Ensure logs directory exists: mkdir -p ~/ai-stack/logs

# Health check every 15 minutes
*/15 * * * * /home/jonat/ai-stack/venv/bin/python -m scripts.collectors.run_collectors --health >> /home/jonat/ai-stack/logs/collectors.log 2>&1

# Git + file collectors every 4 hours
0 */4 * * * cd /home/jonat/ai-stack && /home/jonat/ai-stack/venv/bin/python -m scripts.collectors.run_collectors --git --files >> /home/jonat/ai-stack/logs/collectors.log 2>&1

# Full collection + daily snapshot at midnight
0 0 * * * cd /home/jonat/ai-stack && /home/jonat/ai-stack/venv/bin/python -m scripts.collectors.run_collectors --all --snapshot >> /home/jonat/ai-stack/logs/collectors.log 2>&1
```

**Setup commands:**
```bash
# Create logs directory
mkdir -p ~/ai-stack/logs

# Create collectors output directory  
mkdir -p ~/ai-stack/collectors/{state,daily}

# Test run
cd ~/ai-stack
python -m scripts.collectors.run_collectors --all

# Install to cron
crontab -e
# (paste the cron lines above)
```

---

## Integration with FAITHH Backend

Add this endpoint to `faithh_professional_backend_fixed.py`:

```python
@app.route('/api/context/collectors')
def get_collector_context():
    """Return aggregated collector data for AI consumption"""
    from scripts.collectors.aggregator import Aggregator
    
    try:
        aggregator = Aggregator()
        return jsonify(aggregator.aggregate())
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
```

---

## Success Criteria

After implementation:

1. ✅ `python -m scripts.collectors.run_collectors --all` produces 4 JSON files in `collectors/state/`
2. ✅ Files are named: `git.json`, `file_changes.json`, `health.json`, `terminal.json`
3. ✅ Aggregator successfully reads all files
4. ✅ Daily snapshots save to `collectors/daily/YYYY-MM-DD.json`
5. ✅ Cron jobs run using venv python
6. ✅ `/api/context/collectors` endpoint returns aggregated data

---

## Changelog (Patches Applied)

1. **Fixed filename consistency**: All collectors now output `{name}.json` matching their `name` attribute
2. **Fixed daily snapshot path**: Now uses `collectors/daily/YYYY-MM-DD.json` consistently
3. **Fixed imports**: Using package-relative imports (`from .base_collector import ...`)
4. **Fixed cron paths**: Using absolute venv python path and explicit working directory
5. **Added setup commands**: Creating required directories before first run

---

**End of Specification (Patched)**

*Ready for Windsurf implementation*

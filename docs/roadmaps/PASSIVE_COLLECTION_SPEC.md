# Passive Collection System Specification

**Date:** 2026-01-15
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
│  │  git_activity.json | file_changes.json | health.json     │   │
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
│  │  collectors/daily_snapshot_{date}.json (new)            │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
~/ai-stack/
├── scripts/
│   └── collectors/
│       ├── __init__.py
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
│   │   ├── git_activity.json
│   │   ├── file_changes.json
│   │   ├── health.json
│   │   └── terminal_history.json
│   ├── daily/                     # Daily snapshots
│   │   └── 2026-01-15.json
│   └── config.json                # Collector configuration
```

---

## Collector Specifications

### 1. Git Collector (`git_collector.py`)

**Purpose:** Capture recent git activity for AI context

**Triggers:** On-demand, cron (every 4 hours), or pre-commit hook

**Output:** `collectors/state/git_activity.json`

```json
{
  "collected_at": "2026-01-15T16:30:00Z",
  "collector": "git",
  "version": "1.0",
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
class GitCollector(BaseCollector):
    name = "git"
    
    def collect(self) -> dict:
        return {
            "repository": self._get_repo_info(),
            "status": self._get_status(),
            "recent_commits": self._get_recent_commits(limit=10),
            "modified_files": self._get_modified_files(),
            "file_categories": self._categorize_files(),
        }
    
    def _categorize_files(self) -> dict:
        """Categorize modified files for AI understanding"""
        categories = {
            'ui': ['*.html', '*.css', '*.js'],
            'backend': ['*.py'],
            'documentation': ['*.md', 'docs/*'],
            'config': ['*.json', '*.yaml', '*.env*'],
            'data': ['*.json'],  # in specific dirs
        }
        # ... implementation
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
  "data": {
    "since": "2026-01-15T12:30:00Z",
    "watched_paths": [
      "/home/jonat/ai-stack/",
      "/home/jonat/ai-stack/projects/"
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
      },
      {
        "path": "faithh_professional_backend_fixed.py",
        "reason": "Core backend modified"
      }
    ]
  }
}
```

**Implementation Notes:**
- Use file mtimes for change detection
- Store last collection time in state
- Ignore common noise: `__pycache__`, `.git`, `node_modules`, `*.pyc`
- Highlight "notable files" that AI should pay attention to

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
  "data": {
    "overall_status": "degraded",
    "services": {
      "faithh_backend": {
        "url": "http://localhost:5557",
        "status": "healthy",
        "response_time_ms": 45,
        "version": "v3.4-filesystem",
        "features": ["chat", "rag", "pulse", "compass"]
      },
      "ollama": {
        "url": "http://localhost:11434",
        "status": "healthy",
        "response_time_ms": 12,
        "models": ["llama31-faithh:latest", "qwen3-faithh:latest"]
      },
      "chromadb_gen8": {
        "url": "http://servicebox.taileb8c60.ts.net:8000",
        "status": "degraded",
        "response_time_ms": 89,
        "reachable": true,
        "connected": false,
        "documents": 0,
        "expected_documents": 28876,
        "issue": "Collection not connecting despite server reachable"
      },
      "gen8_ssh": {
        "host": "servicebox.taileb8c60.ts.net",
        "status": "healthy",
        "response_time_ms": 23
      }
    },
    "issues": [
      {
        "service": "chromadb_gen8",
        "severity": "high",
        "message": "ChromaDB showing 0 documents, expected 28,876",
        "suggested_action": "Check collection name or API version"
      }
    ],
    "infrastructure": {
      "wsl_disk_free_gb": 45.2,
      "wsl_memory_used_pct": 62,
      "gen8_reachable": true
    }
  }
}
```

**Implementation:**
```python
class HealthCollector(BaseCollector):
    name = "health"
    
    def collect(self) -> dict:
        services = {}
        issues = []
        
        # Check each service
        services["faithh_backend"] = self._check_faithh()
        services["ollama"] = self._check_ollama()
        services["chromadb_gen8"] = self._check_chromadb()
        services["gen8_ssh"] = self._check_ssh("servicebox.taileb8c60.ts.net")
        
        # Detect issues
        for name, svc in services.items():
            if svc["status"] != "healthy":
                issues.append(self._create_issue(name, svc))
        
        return {
            "overall_status": self._compute_overall(services),
            "services": services,
            "issues": issues,
            "infrastructure": self._check_infrastructure()
        }
```

---

### 4. Terminal Collector (`terminal_collector.py`) [Optional]

**Purpose:** Capture recent terminal commands for context

**Triggers:** On-demand only (privacy-sensitive)

**Output:** `collectors/state/terminal_history.json`

```json
{
  "collected_at": "2026-01-15T16:30:00Z",
  "collector": "terminal",
  "version": "1.0",
  "data": {
    "since": "2026-01-15T00:00:00Z",
    "commands": [
      {
        "command": "git status",
        "timestamp": "2026-01-15T14:00:00Z",
        "category": "git"
      },
      {
        "command": "curl localhost:5557/health",
        "timestamp": "2026-01-15T14:05:00Z",
        "category": "health_check"
      }
    ],
    "summary": {
      "total_commands": 45,
      "by_category": {
        "git": 12,
        "navigation": 15,
        "python": 8,
        "health_check": 5,
        "other": 5
      }
    },
    "patterns": [
      "Heavy git usage today",
      "Multiple health checks (debugging?)"
    ]
  }
}
```

**Privacy Notes:**
- Filter out sensitive commands (containing passwords, tokens)
- Only collect from bash_history with explicit opt-in
- Redact paths containing sensitive keywords

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
        """Save output to JSON file"""
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

## Aggregator

```python
# scripts/collectors/aggregator.py

from datetime import datetime
from pathlib import Path
import json

class Aggregator:
    """Combines all collector outputs into unified state"""
    
    def __init__(self, collectors_dir: Path = None):
        self.collectors_dir = collectors_dir or Path.home() / "ai-stack" / "collectors"
        self.state_dir = self.collectors_dir / "state"
        self.daily_dir = self.collectors_dir / "daily"
        self.daily_dir.mkdir(parents=True, exist_ok=True)
    
    def aggregate(self) -> dict:
        """Combine all collector outputs"""
        collectors = ['git', 'file_changes', 'health', 'terminal']
        
        aggregated = {
            "aggregated_at": datetime.utcnow().isoformat() + "Z",
            "collectors": {},
            "summary": {},
            "issues": [],
            "ai_context": {}
        }
        
        for collector in collectors:
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
    
    def save_daily_snapshot(self):
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
# scripts/collectors/run_collectors.py

#!/usr/bin/env python3
"""
Run all passive collectors and aggregate results.

Usage:
    python run_collectors.py              # Run all collectors
    python run_collectors.py --git        # Run only git collector
    python run_collectors.py --aggregate  # Only aggregate existing data
    python run_collectors.py --snapshot   # Create daily snapshot
"""

import argparse
from pathlib import Path

from git_collector import GitCollector
from file_collector import FileCollector
from health_collector import HealthCollector
from terminal_collector import TerminalCollector
from aggregator import Aggregator

COLLECTORS = {
    'git': GitCollector,
    'file_changes': FileCollector,
    'health': HealthCollector,
    'terminal': TerminalCollector,
}

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
    run_all = args.all or not any([args.git, args.files, args.health, args.terminal, args.aggregate, args.snapshot])
    
    results = {}
    
    if run_all or args.git:
        print("Running git collector...")
        results['git'] = GitCollector().run()
    
    if run_all or args.files:
        print("Running file collector...")
        results['file_changes'] = FileCollector().run()
    
    if run_all or args.health:
        print("Running health collector...")
        results['health'] = HealthCollector().run()
    
    if run_all or args.terminal:
        print("Running terminal collector...")
        results['terminal'] = TerminalCollector().run()
    
    # Always aggregate after running collectors
    if run_all or args.aggregate:
        print("Aggregating results...")
        aggregator = Aggregator()
        aggregated = aggregator.aggregate()
        print(f"Status: {aggregated['ai_context']['status_line']}")
    
    if args.snapshot:
        print("Saving daily snapshot...")
        aggregator = Aggregator()
        path = aggregator.save_daily_snapshot()
        print(f"Snapshot saved to: {path}")
    
    print("Done!")
    return results

if __name__ == '__main__':
    main()
```

---

## Cron Setup

```bash
# Add to crontab (crontab -e)

# Run health check every 15 minutes
*/15 * * * * cd ~/ai-stack && python scripts/collectors/run_collectors.py --health >> logs/collectors.log 2>&1

# Run git + file collectors every 4 hours
0 */4 * * * cd ~/ai-stack && python scripts/collectors/run_collectors.py --git --files >> logs/collectors.log 2>&1

# Create daily snapshot at midnight
0 0 * * * cd ~/ai-stack && python scripts/collectors/run_collectors.py --all --snapshot >> logs/collectors.log 2>&1
```

---

## Integration with Existing Systems

### 1. Update `project_states.json` Automatically

The aggregator can update `project_states.json` with current health status:

```python
def update_project_states(self):
    """Update services section of project_states.json"""
    project_states_path = Path.home() / "ai-stack" / "project_states.json"
    
    with open(project_states_path) as f:
        states = json.load(f)
    
    # Update services from health collector
    health = self.load_collector("health")
    if health.get("success"):
        states["services"]["chroma_heartbeat"] = {
            "ok": health["data"]["services"]["chromadb_gen8"]["status"] == "healthy"
        }
        states["services"]["chroma_stats"]["documents"] = (
            health["data"]["services"]["chromadb_gen8"].get("documents", "unreachable")
        )
    
    states["meta"]["generated_at_utc"] = datetime.utcnow().isoformat() + "Z"
    
    with open(project_states_path, 'w') as f:
        json.dump(states, f, indent=2)
```

### 2. Feed into Weekly Synthesis

The daily snapshots become input for weekly synthesis:

```python
def get_week_activity(self) -> list:
    """Get all daily snapshots from past week"""
    daily_dir = Path.home() / "ai-stack" / "collectors" / "daily"
    week_ago = datetime.now() - timedelta(days=7)
    
    snapshots = []
    for path in sorted(daily_dir.glob("*.json")):
        date = datetime.strptime(path.stem, "%Y-%m-%d")
        if date >= week_ago:
            with open(path) as f:
                snapshots.append(json.load(f))
    
    return snapshots
```

### 3. API Endpoint for AI Context

Add to FAITHH backend:

```python
@app.route('/api/context/collectors')
def get_collector_context():
    """Return aggregated collector data for AI consumption"""
    aggregator = Aggregator()
    return jsonify(aggregator.aggregate())
```

---

## Success Criteria

After implementation:

1. ✅ Running `python run_collectors.py` produces 4 JSON files in `collectors/state/`
2. ✅ Health collector detects ChromaDB issue automatically
3. ✅ Git collector shows current dirty state
4. ✅ Aggregator produces AI-readable summary
5. ✅ Daily snapshots accumulate in `collectors/daily/`
6. ✅ Cron jobs run without manual intervention
7. ✅ `project_states.json` services section auto-updates

---

## Next Steps After Implementation

1. **Auto-Generated Docs** - Use collector data to regenerate MASTER_CONTEXT.md
2. **Drift Detection** - Compare collector data to documentation, alert on mismatch
3. **Context API** - Single endpoint returning everything AI needs
4. **Weekly Synthesis Integration** - Feed collector data into journal generation

---

## Future: Windsurf Session Indexing (2026-02-16 idea)

Capture Windsurf/Cascade AI coding sessions as indexable context:
- **Source**: Windsurf conversation logs / session transcripts
- **Goal**: Index what was discussed and decided in each Cascade session into ChromaDB
- **Benefit**: FAITHH can reference past Windsurf sessions ("In our last coding session, we fixed the anti-hallucination pipeline...")
- **Implementation**: Parse session exports → chunk → embed → index alongside existing conversation data
- **Priority**: Medium — adds significant continuity across AI tools

## Future: Auto-Journaling Source Intakes (2026-02-16 idea)

Multi-source intake system for automatic daily/weekly journaling:
- **Sources to consider**:
  - Git commits (already captured by git collector)
  - Windsurf/Cascade session summaries
  - Browser history highlights (opt-in)
  - Calendar events / task completions
  - Health/fitness data (if available)
  - Manual voice notes (transcribed)
- **Output**: Structured daily journal entries (markdown + JSON)
- **Integration**: Feed into FAITHH memory for personal context awareness
- **Key question**: Where to start? → Git + Windsurf sessions are the easiest first sources (already digital, structured)
- **Priority**: High interest — needs design session to scope MVP

---

**End of Specification**

*Ready for Windsurf implementation*

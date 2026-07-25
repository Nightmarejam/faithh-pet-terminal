# Windsurf Handoff: Compass Director Module
**Date:** 2026-01-18
**Model:** GPT 5.1 Codex Max Low (free tier)
**Task:** Build the "Director" module that synthesizes collector data into actionable intelligence

---

## TL;DR

Build a lightweight "Director" that reads existing collector outputs and generates:
1. Prioritized attention items
2. Suggested next actions
3. Context packet for AI sessions

**This is ~150 lines of Python + one backend endpoint.**

---

## Why This Matters

Jonathan has passive collectors running (git, files, health, terminal) but no way for FAITHH to USE that data to self-direct. The Director bridges this gap - it's the "brain" that looks at system state and says "here's what needs attention."

---

## Current State (Already Working)

### Collectors ✅
```
~/ai-stack/collectors/state/
├── git.json           # Git status, commits, dirty files
├── file_changes.json  # Files changed since last collection
├── health.json        # Service health (backend, ollama, chromadb)
└── terminal.json      # Recent commands
```

### Cron Jobs ✅
```bash
*/15 * * * * ... --health      # Every 15 min
0 */4 * * *  ... --git --files # Every 4 hours
0 0 * * *    ... --all         # Daily snapshot
```

### Existing Endpoints ✅
- `/api/context/collectors/status` - Returns aggregated collector data
- `/collectors/status` - HTML status page
- `/api/compass` - Compass dashboard data (projects)

---

## What to Build

### 1. Director Module (`scripts/collectors/director.py`)

```python
#!/usr/bin/env python3
"""
Compass Director - Synthesizes collector data into actionable intelligence.

Reads:
  - collectors/state/*.json (health, git, files, terminal)
  - project_states.json (active projects)

Produces:
  - Prioritized attention items
  - Suggested actions
  - Context packet for AI sessions
"""

from pathlib import Path
from datetime import datetime, timedelta
import json

class CompassDirector:
    """Analyzes system state and generates actionable intelligence."""
    
    def __init__(self, ai_stack_root: Path = None):
        self.root = ai_stack_root or Path.home() / "ai-stack"
        self.collectors_dir = self.root / "collectors" / "state"
    
    def analyze(self) -> dict:
        """Main entry point - analyze all data and return director output."""
        collectors = self._load_collectors()
        project_states = self._load_project_states()
        
        attention_items = []
        suggested_actions = []
        
        # Analyze health
        attention_items.extend(self._analyze_health(collectors.get("health", {})))
        
        # Analyze git
        git_items, git_actions = self._analyze_git(collectors.get("git", {}))
        attention_items.extend(git_items)
        suggested_actions.extend(git_actions)
        
        # Analyze file changes
        file_items, file_actions = self._analyze_files(collectors.get("file_changes", {}))
        attention_items.extend(file_items)
        suggested_actions.extend(file_actions)
        
        # Analyze collector freshness
        stale_items = self._check_collector_freshness(collectors)
        attention_items.extend(stale_items)
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        attention_items.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 99))
        
        return {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "attention_items": attention_items,
            "suggested_actions": suggested_actions[:5],  # Top 5 actions
            "context_for_ai": self._generate_context_summary(collectors, attention_items),
            "raw_summary": {
                "total_issues": len(attention_items),
                "critical": len([i for i in attention_items if i.get("priority") == "critical"]),
                "high": len([i for i in attention_items if i.get("priority") == "high"]),
                "services_healthy": self._count_healthy_services(collectors.get("health", {}))
            }
        }
    
    def _load_collectors(self) -> dict:
        """Load all collector JSON files."""
        collectors = {}
        for name in ["health", "git", "file_changes", "terminal"]:
            path = self.collectors_dir / f"{name}.json"
            if path.exists():
                try:
                    with open(path) as f:
                        collectors[name] = json.load(f)
                except json.JSONDecodeError:
                    collectors[name] = {"success": False, "error": "Invalid JSON"}
        return collectors
    
    def _load_project_states(self) -> dict:
        """Load project_states.json if it exists."""
        path = self.root / "project_states.json"
        if path.exists():
            try:
                with open(path) as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _analyze_health(self, health_data: dict) -> list:
        """Analyze health collector output for issues."""
        items = []
        if not health_data.get("success", False):
            items.append({
                "priority": "high",
                "type": "health",
                "message": "Health collector failed to run",
                "source": "health.json"
            })
            return items
        
        data = health_data.get("data", {})
        overall = data.get("overall_status", "unknown")
        
        if overall == "critical":
            items.append({
                "priority": "critical",
                "type": "health",
                "message": "System health is CRITICAL - services down",
                "source": "health.json"
            })
        elif overall == "degraded":
            items.append({
                "priority": "high",
                "type": "health",
                "message": "System health is degraded",
                "source": "health.json"
            })
        
        # Check individual services
        services = data.get("services", {})
        for name, svc in services.items():
            status = svc.get("status", "unknown")
            if status in ["unreachable", "error"]:
                items.append({
                    "priority": "critical",
                    "type": "health",
                    "message": f"Service '{name}' is {status}",
                    "source": "health.json",
                    "details": svc.get("error")
                })
            elif status == "degraded":
                items.append({
                    "priority": "high",
                    "type": "health",
                    "message": f"Service '{name}' is degraded",
                    "source": "health.json",
                    "details": svc.get("issue")
                })
        
        # Add any explicit issues from health collector
        for issue in data.get("issues", []):
            items.append({
                "priority": issue.get("severity", "medium"),
                "type": "health",
                "message": issue.get("message", "Unknown issue"),
                "source": "health.json",
                "suggested_action": issue.get("suggested_action")
            })
        
        return items
    
    def _analyze_git(self, git_data: dict) -> tuple:
        """Analyze git collector output."""
        items = []
        actions = []
        
        if not git_data.get("success", False):
            return items, actions
        
        data = git_data.get("data", {})
        status = data.get("status", {})
        
        # Check if dirty
        if status.get("is_dirty", False):
            modified = status.get("modified_count", 0)
            untracked = status.get("untracked_count", 0)
            
            if modified + untracked > 20:
                items.append({
                    "priority": "medium",
                    "type": "git",
                    "message": f"Git has {modified} modified + {untracked} untracked files",
                    "source": "git.json"
                })
                actions.append("Review git status and commit or stash changes")
        
        # Check if ahead of origin
        ahead = status.get("ahead", 0)
        if ahead > 0:
            items.append({
                "priority": "low",
                "type": "git",
                "message": f"Git is {ahead} commits ahead of origin",
                "source": "git.json"
            })
            actions.append(f"Run 'git push' to sync {ahead} commits to origin")
        
        # Check if behind origin
        behind = status.get("behind", 0)
        if behind > 0:
            items.append({
                "priority": "medium",
                "type": "git",
                "message": f"Git is {behind} commits behind origin",
                "source": "git.json"
            })
            actions.append("Run 'git pull' to sync with origin")
        
        return items, actions
    
    def _analyze_files(self, file_data: dict) -> tuple:
        """Analyze file changes collector output."""
        items = []
        actions = []
        
        if not file_data.get("success", False):
            return items, actions
        
        data = file_data.get("data", {})
        summary = data.get("summary", {})
        total = summary.get("total_changes", 0)
        
        # Check for notable files
        notable = data.get("notable_files", [])
        for nf in notable:
            items.append({
                "priority": "low",
                "type": "file_change",
                "message": f"Notable file changed: {nf.get('path')}",
                "source": "file_changes.json",
                "details": nf.get("reason")
            })
        
        # High churn warning
        if total > 50:
            items.append({
                "priority": "low",
                "type": "file_change",
                "message": f"High file churn: {total} files changed since last collection",
                "source": "file_changes.json"
            })
        
        return items, actions
    
    def _check_collector_freshness(self, collectors: dict) -> list:
        """Check if any collectors are stale."""
        items = []
        now = datetime.utcnow()
        
        thresholds = {
            "health": timedelta(hours=1),      # Should run every 15 min
            "git": timedelta(hours=8),         # Should run every 4 hours
            "file_changes": timedelta(hours=8),
            "terminal": timedelta(days=2)
        }
        
        for name, threshold in thresholds.items():
            data = collectors.get(name, {})
            collected_at = data.get("collected_at")
            
            if not collected_at:
                items.append({
                    "priority": "medium",
                    "type": "collector",
                    "message": f"Collector '{name}' has never run",
                    "source": f"{name}.json"
                })
                continue
            
            try:
                collected_time = datetime.fromisoformat(collected_at.replace("Z", "+00:00")).replace(tzinfo=None)
                age = now - collected_time
                
                if age > threshold:
                    hours = int(age.total_seconds() / 3600)
                    items.append({
                        "priority": "low",
                        "type": "collector",
                        "message": f"Collector '{name}' is stale ({hours}h old)",
                        "source": f"{name}.json"
                    })
            except:
                pass
        
        return items
    
    def _count_healthy_services(self, health_data: dict) -> str:
        """Count healthy services."""
        if not health_data.get("success"):
            return "unknown"
        
        services = health_data.get("data", {}).get("services", {})
        total = len(services)
        healthy = sum(1 for s in services.values() if s.get("status") == "healthy")
        return f"{healthy}/{total}"
    
    def _generate_context_summary(self, collectors: dict, attention_items: list) -> str:
        """Generate a one-paragraph context summary for AI consumption."""
        parts = []
        
        # Health summary
        health = collectors.get("health", {}).get("data", {})
        overall = health.get("overall_status", "unknown")
        parts.append(f"System health: {overall}.")
        
        # Git summary
        git = collectors.get("git", {}).get("data", {})
        git_status = git.get("status", {})
        if git_status.get("is_dirty"):
            parts.append(f"Git: {git_status.get('modified_count', 0)} modified files.")
        else:
            parts.append("Git: clean.")
        
        # Issues summary
        critical = len([i for i in attention_items if i.get("priority") == "critical"])
        high = len([i for i in attention_items if i.get("priority") == "high"])
        
        if critical > 0:
            parts.append(f"CRITICAL: {critical} issues need immediate attention.")
        elif high > 0:
            parts.append(f"{high} high-priority items need attention.")
        else:
            parts.append("No urgent issues.")
        
        return " ".join(parts)


# CLI support
if __name__ == "__main__":
    import sys
    director = CompassDirector()
    result = director.analyze()
    
    if "--json" in sys.argv:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n=== COMPASS DIRECTOR ===")
        print(f"Generated: {result['generated_at']}")
        print(f"\nContext: {result['context_for_ai']}")
        print(f"\n--- Attention Items ({result['raw_summary']['total_issues']}) ---")
        for item in result['attention_items']:
            print(f"  [{item['priority'].upper()}] {item['message']}")
        print(f"\n--- Suggested Actions ---")
        for action in result['suggested_actions']:
            print(f"  • {action}")
```

---

### 2. Backend Endpoint (add to `faithh_professional_backend_fixed.py`)

Find the section with other `/api/compass` routes and add:

```python
@app.route('/api/compass/director')
def get_compass_director():
    """Return Director analysis - synthesized actionable intelligence."""
    try:
        from scripts.collectors.director import CompassDirector
        director = CompassDirector()
        return jsonify(director.analyze())
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "attention_items": [],
            "suggested_actions": [],
            "context_for_ai": "Director failed to analyze system state."
        }), 500
```

---

### 3. Test Commands

```bash
# Test the module directly
cd ~/ai-stack
python -m scripts.collectors.director --json | jq '.'

# Test the endpoint (after adding to backend)
curl -s http://localhost:5557/api/compass/director | jq '.'

# Check specific fields
curl -s http://localhost:5557/api/compass/director | jq '.attention_items'
curl -s http://localhost:5557/api/compass/director | jq '.context_for_ai'
```

---

## Success Criteria

✅ Implementation complete when:

1. `python -m scripts.collectors.director --json` produces valid JSON
2. Output contains: `attention_items`, `suggested_actions`, `context_for_ai`, `raw_summary`
3. `/api/compass/director` endpoint returns the analysis
4. Health issues from collectors appear as attention items
5. Git status (dirty, ahead/behind) generates appropriate items
6. Stale collectors are detected

---

## File Locations

| File | Action |
|------|--------|
| `scripts/collectors/director.py` | CREATE (new file) |
| `faithh_professional_backend_fixed.py` | EDIT (add endpoint) |
| `scripts/collectors/__init__.py` | EDIT (add export) |

### Update `__init__.py`

Add to `scripts/collectors/__init__.py`:

```python
from .director import CompassDirector

__all__ = [
    # ... existing exports ...
    'CompassDirector'
]
```

---

## Architecture Context

```
Collectors (running on cron)
    ↓
collectors/state/*.json
    ↓
CompassDirector.analyze()
    ↓
{attention_items, suggested_actions, context_for_ai}
    ↓
/api/compass/director endpoint
    ↓
AI sessions consume this to know "what needs attention"
```

---

## Notes for AI Assistant

- **Working Directory:** `/home/jonat/ai-stack` (WSL2 Ubuntu)
- **Existing collectors work** - don't modify them
- **Keep it simple** - this is ~200 lines total, don't over-engineer
- **Error handling** - if a collector file is missing, skip it gracefully
- **The goal** is actionable intelligence, not more data collection

---

## After Implementation

1. Test with `python -m scripts.collectors.director --json`
2. Restart backend: `./restart_backend.sh`
3. Test endpoint: `curl http://localhost:5557/api/compass/director | jq '.'`
4. Commit: `git add -A && git commit -m "feat(compass): add Director module for actionable intelligence"`

---

**This gives FAITHH the ability to "know what she needs" by reading her own state.**

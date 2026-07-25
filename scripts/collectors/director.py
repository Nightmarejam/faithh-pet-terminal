#!/usr/bin/env python3
"""
Compass Director - Synthesizes collector data into actionable intelligence.

Reads:
  - collectors/state/*.json (health, git, file_changes, terminal)
  - project_states.json (active projects)

Produces:
  - Prioritized attention items
  - Suggested actions
  - Context packet for AI sessions
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timedelta, timezone
import json
from typing import Dict, List, Tuple, Any


class CompassDirector:
    """Analyzes system state and generates actionable intelligence."""

    def __init__(self, ai_stack_root: Path | None = None):
        self.root = ai_stack_root or Path.home() / "ai-stack"
        self.collectors_dir = self.root / "collectors" / "state"

    def analyze(self) -> Dict[str, Any]:
        """Main entry point - analyze all data and return director output."""
        collectors = self._load_collectors()
        project_states = self._load_project_states()

        attention_items: List[Dict[str, Any]] = []
        suggested_actions: List[str] = []

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
            "success": True,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "attention_items": attention_items,
            "suggested_actions": suggested_actions[:5],
            "context_for_ai": self._generate_context_summary(collectors, attention_items),
            "raw_summary": {
                "total_issues": len(attention_items),
                "critical": len([i for i in attention_items if i.get("priority") == "critical"]),
                "high": len([i for i in attention_items if i.get("priority") == "high"]),
                "services_healthy": self._count_healthy_services(collectors.get("health", {})),
            },
            "project_states": project_states,
        }

    def _load_collectors(self) -> Dict[str, Any]:
        """Load all collector JSON files."""
        collectors: Dict[str, Any] = {}
        for name in ["health", "git", "file_changes", "terminal"]:
            path = self.collectors_dir / f"{name}.json"
            if path.exists():
                try:
                    with open(path) as f:
                        collectors[name] = json.load(f)
                except json.JSONDecodeError:
                    collectors[name] = {"success": False, "error": "Invalid JSON"}
            else:
                collectors[name] = {"success": False, "error": "Missing file"}
        return collectors

    def _load_project_states(self) -> Dict[str, Any]:
        """Load project_states.json if it exists."""
        path = self.root / "project_states.json"
        if path.exists():
            try:
                with open(path) as f:
                    return json.load(f)
            except Exception:
                return {"error": "Invalid project_states.json"}
        return {}

    def _analyze_health(self, health_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze health collector output for issues."""
        items: List[Dict[str, Any]] = []
        if not health_data.get("success", False):
            items.append(
                {
                    "priority": "high",
                    "type": "health",
                    "message": "Health collector failed to run",
                    "source": "health.json",
                }
            )
            return items

        data = health_data.get("data", {})
        overall = data.get("overall_status", "unknown")

        if overall == "critical":
            items.append(
                {
                    "priority": "critical",
                    "type": "health",
                    "message": "System health is CRITICAL - services down",
                    "source": "health.json",
                }
            )
        elif overall == "degraded":
            items.append(
                {
                    "priority": "high",
                    "type": "health",
                    "message": "System health is degraded",
                    "source": "health.json",
                }
            )

        services = data.get("services", {})
        for name, svc in services.items():
            status = svc.get("status", "unknown")
            if status in ["unreachable", "error"]:
                items.append(
                    {
                        "priority": "critical",
                        "type": "health",
                        "message": f"Service '{name}' is {status}",
                        "source": "health.json",
                        "details": svc.get("error"),
                    }
                )
            elif status == "degraded":
                items.append(
                    {
                        "priority": "high",
                        "type": "health",
                        "message": f"Service '{name}' is degraded",
                        "source": "health.json",
                        "details": svc.get("issue"),
                    }
                )

        for issue in data.get("issues", []):
            items.append(
                {
                    "priority": issue.get("severity", "medium"),
                    "type": "health",
                    "message": issue.get("message", "Unknown issue"),
                    "source": "health.json",
                    "suggested_action": issue.get("suggested_action"),
                }
            )

        return items

    def _analyze_git(self, git_data: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Analyze git collector output."""
        items: List[Dict[str, Any]] = []
        actions: List[str] = []

        if not git_data.get("success", False):
            return items, actions

        data = git_data.get("data", {})
        status = data.get("status", {})

        if status.get("is_dirty", False):
            modified = status.get("modified_count", 0)
            untracked = status.get("untracked_count", 0)
            if modified + untracked > 20:
                items.append(
                    {
                        "priority": "medium",
                        "type": "git",
                        "message": f"Git has {modified} modified + {untracked} untracked files",
                        "source": "git.json",
                    }
                )
                actions.append("Review git status and commit or stash changes")

        ahead = status.get("ahead", 0)
        if ahead > 0:
            items.append(
                {
                    "priority": "low",
                    "type": "git",
                    "message": f"Git is {ahead} commits ahead of origin",
                    "source": "git.json",
                }
            )
            actions.append(f"Run 'git push' to sync {ahead} commits to origin")

        behind = status.get("behind", 0)
        if behind > 0:
            items.append(
                {
                    "priority": "medium",
                    "type": "git",
                    "message": f"Git is {behind} commits behind origin",
                    "source": "git.json",
                }
            )
            actions.append("Run 'git pull' to sync with origin")

        return items, actions

    def _analyze_files(self, file_data: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Analyze file changes collector output."""
        items: List[Dict[str, Any]] = []
        actions: List[str] = []

        if not file_data.get("success", False):
            return items, actions

        data = file_data.get("data", {})
        summary = data.get("summary", {})
        total = summary.get("total_changes", 0)

        notable = data.get("notable_files", [])
        for nf in notable:
            items.append(
                {
                    "priority": "low",
                    "type": "file_change",
                    "message": f"Notable file changed: {nf.get('path')}",
                    "source": "file_changes.json",
                    "details": nf.get("reason"),
                }
            )

        if total > 50:
            items.append(
                {
                    "priority": "low",
                    "type": "file_change",
                    "message": f"High file churn: {total} files changed since last collection",
                    "source": "file_changes.json",
                }
            )

        return items, actions

    def _check_collector_freshness(self, collectors: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check if any collectors are stale."""
        items: List[Dict[str, Any]] = []
        now = datetime.now(timezone.utc)

        thresholds = {
            "health": timedelta(hours=1),
            "git": timedelta(hours=8),
            "file_changes": timedelta(hours=8),
            "terminal": timedelta(days=2),
        }

        for name, threshold in thresholds.items():
            data = collectors.get(name, {})
            collected_at = data.get("collected_at")

            if not collected_at:
                items.append(
                    {
                        "priority": "medium",
                        "type": "collector",
                        "message": f"Collector '{name}' has never run",
                        "source": f"{name}.json",
                    }
                )
                continue

            try:
                collected_time = datetime.fromisoformat(collected_at.replace("Z", "+00:00")).replace(tzinfo=None)
                age = now - collected_time

                if age > threshold:
                    hours = int(age.total_seconds() / 3600)
                    items.append(
                        {
                            "priority": "low",
                            "type": "collector",
                            "message": f"Collector '{name}' is stale ({hours}h old)",
                            "source": f"{name}.json",
                        }
                    )
            except Exception:
                continue

        return items

    def _count_healthy_services(self, health_data: Dict[str, Any]) -> str:
        """Count healthy services."""
        if not health_data.get("success"):
            return "unknown"

        services = health_data.get("data", {}).get("services", {})
        total = len(services)
        healthy = sum(1 for s in services.values() if s.get("status") == "healthy")
        return f"{healthy}/{total}"

    def _generate_context_summary(self, collectors: Dict[str, Any], attention_items: List[Dict[str, Any]]) -> str:
        """Generate a one-paragraph context summary for AI consumption."""
        parts: List[str] = []

        health = collectors.get("health", {}).get("data", {})
        overall = health.get("overall_status", "unknown")
        parts.append(f"System health: {overall}.")

        git = collectors.get("git", {}).get("data", {})
        git_status = git.get("status", {})
        if git_status.get("is_dirty"):
            parts.append(f"Git: {git_status.get('modified_count', 0)} modified files.")
        else:
            parts.append("Git: clean.")

        critical = len([i for i in attention_items if i.get("priority") == "critical"])
        high = len([i for i in attention_items if i.get("priority") == "high"])

        if critical > 0:
            parts.append(f"CRITICAL: {critical} issues need immediate attention.")
        elif high > 0:
            parts.append(f"{high} high-priority items need attention.")
        else:
            parts.append("No urgent issues.")

        return " ".join(parts)


if __name__ == "__main__":
    import sys

    director = CompassDirector()
    result = director.analyze()

    if "--json" in sys.argv:
        print(json.dumps(result, indent=2))
    else:
        print("\n=== COMPASS DIRECTOR ===")
        print(f"Generated: {result['generated_at']}")
        print(f"\nContext: {result['context_for_ai']}")
        print(f"\n--- Attention Items ({result['raw_summary']['total_issues']}) ---")
        for item in result["attention_items"]:
            print(f"  [{item.get('priority','?').upper()}] {item.get('message','')}")
        print("\n--- Suggested Actions ---")
        for action in result["suggested_actions"]:
            print(f"  • {action}")

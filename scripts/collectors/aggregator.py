from datetime import datetime
from pathlib import Path
import json


class Aggregator:
    """Combines all collector outputs into unified state."""

    COLLECTORS = ["git", "file_changes", "health", "terminal"]

    def __init__(self, collectors_dir: Path = None):
        self.collectors_dir = collectors_dir or Path.home() / "ai-stack" / "collectors"
        self.state_dir = self.collectors_dir / "state"
        self.daily_dir = self.collectors_dir / "daily"
        self.daily_dir.mkdir(parents=True, exist_ok=True)

    def aggregate(self) -> dict:
        aggregated = {
            "aggregated_at": datetime.utcnow().isoformat() + "Z",
            "collectors": {},
            "summary": {},
            "issues": [],
            "ai_context": {},
        }

        for collector in self.COLLECTORS:
            path = self.state_dir / f"{collector}.json"
            if path.exists():
                with path.open() as handle:
                    data = json.load(handle)
                aggregated["collectors"][collector] = data

                if collector == "health" and data.get("success"):
                    aggregated["issues"].extend(
                        data.get("data", {}).get("issues", [])
                    )

        aggregated["summary"] = self._build_summary(aggregated["collectors"])
        aggregated["ai_context"] = self._build_ai_context(aggregated)

        return aggregated

    def _build_summary(self, collectors: dict) -> dict:
        summary = {
            "system_status": "unknown",
            "git_dirty": False,
            "files_changed_today": 0,
            "active_issues": 0,
        }

        if "health" in collectors:
            health = collectors["health"].get("data", {})
            summary["system_status"] = health.get("overall_status", "unknown")
            summary["active_issues"] = len(health.get("issues", []))

        if "git" in collectors:
            git = collectors["git"].get("data", {})
            summary["git_dirty"] = git.get("status", {}).get("is_dirty", False)

        if "file_changes" in collectors:
            file_changes = collectors["file_changes"].get("data", {})
            summary["files_changed_today"] = file_changes.get("summary", {}).get(
                "total_changes", 0
            )

        return summary

    def _build_ai_context(self, aggregated: dict) -> dict:
        return {
            "status_line": self._generate_status_line(aggregated),
            "attention_needed": aggregated["issues"],
            "recent_activity": self._recent_activity_summary(aggregated),
            "suggested_actions": self._suggest_actions(aggregated),
        }

    def _generate_status_line(self, aggregated: dict) -> str:
        summary = aggregated.get("summary", {})
        status = summary.get("system_status", "unknown")
        issues = summary.get("active_issues", 0)
        dirty = "dirty" if summary.get("git_dirty") else "clean"
        return f"System: {status} | Git: {dirty} | Issues: {issues}"

    def _recent_activity_summary(self, aggregated: dict) -> dict:
        activity = {}

        if "git" in aggregated["collectors"]:
            git_data = aggregated["collectors"]["git"].get("data", {})
            activity["commits_ahead"] = git_data.get("status", {}).get("ahead", 0)
            activity["modified_files"] = git_data.get("status", {}).get(
                "modified_count", 0
            )

        if "file_changes" in aggregated["collectors"]:
            file_data = aggregated["collectors"]["file_changes"].get("data", {})
            activity["files_changed"] = file_data.get("summary", {}).get(
                "total_changes", 0
            )
            activity["notable"] = file_data.get("notable_files", [])

        return activity

    def _suggest_actions(self, aggregated: dict) -> list:
        actions = []

        summary = aggregated.get("summary", {})

        if summary.get("git_dirty"):
            ahead = 0
            if "git" in aggregated["collectors"]:
                ahead = (
                    aggregated["collectors"]["git"]
                    .get("data", {})
                    .get("status", {})
                    .get("ahead", 0)
                )
            if ahead > 0:
                actions.append({
                    "priority": "medium",
                    "action": f"Push {ahead} commits to origin",
                    "command": "git push",
                })

        for issue in aggregated.get("issues", []):
            actions.append({
                "priority": issue.get("severity", "medium"),
                "action": issue.get("suggested_action", "Investigate"),
                "source": issue.get("service"),
            })

        return actions

    def save_daily_snapshot(self) -> Path:
        aggregated = self.aggregate()
        today = datetime.now().strftime("%Y-%m-%d")

        output_path = self.daily_dir / f"{today}.json"
        with output_path.open("w") as handle:
            json.dump(aggregated, handle, indent=2)

        return output_path

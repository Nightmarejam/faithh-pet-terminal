from .base_collector import BaseCollector
from pathlib import Path
from datetime import datetime


class FileCollector(BaseCollector):
    name = "file_changes"  # Output: file_changes.json

    NOTABLE_FILES = {
        "project_states.json": "Source of truth updated",
        "faithh_professional_backend_fixed.py": "Core backend modified",
        "faithh_pet_v4.html": "Main UI modified",
        "MASTER_CONTEXT.md": "Context documentation updated",
        ".env": "Environment configuration changed",
    }

    IGNORE_PATTERNS = [
        "__pycache__",
        ".git",
        "node_modules",
        "*.pyc",
        ".venv",
        "venv",
        "*.log",
        "collectors/state",
        "collectors/daily",
        "worktrees",
    ]

    def collect(self) -> dict:
        previous = self.load_previous()
        since = previous.get("collected_at", "1970-01-01T00:00:00Z")
        since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))

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
                    changes.append(
                        {
                            "path": str(path.relative_to(root)),
                            "type": "modified",
                            "mtime": mtime.isoformat(),
                            "size_bytes": path.stat().st_size,
                            "category": self._categorize(path),
                        }
                    )
            except (OSError, ValueError):
                continue

        return {
            "since": since,
            "watched_paths": [str(root)],
            "changes": changes,
            "summary": self._build_summary(changes),
            "notable_files": self._find_notable(changes),
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
        if path.suffix == ".md":
            return "documentation"
        if path.suffix == ".py":
            return "code"
        if path.suffix in [".html", ".css", ".js"]:
            return "ui"
        if path.suffix == ".json":
            return "config"
        return "other"

    def _build_summary(self, changes: list) -> dict:
        by_type = {}
        by_category = {}
        for change in changes:
            change_type = change["type"]
            category = change["category"]
            by_type[change_type] = by_type.get(change_type, 0) + 1
            by_category[category] = by_category.get(category, 0) + 1

        return {
            "total_changes": len(changes),
            "by_type": by_type,
            "by_category": by_category,
        }

    def _find_notable(self, changes: list) -> list:
        notable = []
        for change in changes:
            filename = Path(change["path"]).name
            if filename in self.NOTABLE_FILES:
                notable.append(
                    {
                        "path": change["path"],
                        "reason": self.NOTABLE_FILES[filename],
                    }
                )
        return notable

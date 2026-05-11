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
            "remote_url": remote_url,
        }

    def _get_status(self) -> dict:
        status = subprocess.check_output(
            ["git", "status", "--porcelain", "-b"], text=True
        )
        lines = status.strip().split("\n")

        branch_line = lines[0] if lines else ""
        ahead = 0
        behind = 0
        if "ahead" in branch_line:
            match = re.search(r"ahead (\d+)", branch_line)
            if match:
                ahead = int(match.group(1))
        if "behind" in branch_line:
            match = re.search(r"behind (\d+)", branch_line)
            if match:
                behind = int(match.group(1))

        modified = staged = untracked = 0
        for line in lines[1:]:
            if line.startswith("??"):
                untracked += 1
            elif line[0] != " ":
                staged += 1
            elif line[1] != " ":
                modified += 1

        return {
            "is_dirty": len(lines) > 1,
            "ahead": ahead,
            "behind": behind,
            "staged_count": staged,
            "modified_count": modified,
            "untracked_count": untracked,
        }

    def _get_recent_commits(self, limit: int = 10) -> list:
        log = subprocess.check_output(
            [
                "git",
                "log",
                f"-{limit}",
                "--format=%H|%h|%s|%an|%aI|%ct",
            ],
            text=True,
        )

        commits = []
        for line in log.strip().split("\n"):
            if not line:
                continue
            parts = line.split("|")
            if len(parts) >= 5:
                commits.append(
                    {
                        "hash": parts[0],
                        "short_hash": parts[1],
                        "message": parts[2],
                        "author": parts[3],
                        "date": parts[4],
                    }
                )
        return commits

    def _get_modified_files(self) -> list:
        status = subprocess.check_output(
            ["git", "status", "--porcelain"], text=True
        )

        files = []
        for line in status.strip().split("\n"):
            if not line:
                continue
            status_code = line[:2]
            path = line[3:]

            file_status = "modified"
            if status_code.startswith("?"):
                file_status = "untracked"
            elif status_code.startswith("A"):
                file_status = "added"
            elif status_code.startswith("D"):
                file_status = "deleted"

            files.append(
                {
                    "path": path,
                    "status": file_status,
                    "category": self._categorize_file(path),
                }
            )
        return files

    def _categorize_file(self, path: str) -> str:
        if path.endswith((".html", ".css", ".js")):
            return "ui"
        if path.endswith(".py"):
            return "backend"
        if path.endswith(".md") or path.startswith("docs/"):
            return "documentation"
        if path.endswith((".json", ".yaml", ".yml", ".env")):
            return "config"
        return "other"

    def _categorize_files(self) -> dict:
        files = self._get_modified_files()
        categories = {}
        for file_item in files:
            cat = file_item["category"]
            categories[cat] = categories.get(cat, 0) + 1
        return categories

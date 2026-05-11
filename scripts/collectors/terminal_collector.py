from .base_collector import BaseCollector
from pathlib import Path
import os


class TerminalCollector(BaseCollector):
    name = "terminal"  # Output: terminal.json

    SENSITIVE_PATTERNS = [
        "password",
        "token",
        "secret",
        "key=",
        "api_key",
        "AWS_",
        "GROQ_",
        "export ",
        "ssh-add",
    ]

    def collect(self) -> dict:
        history_path = Path.home() / ".bash_history"

        if not history_path.exists():
            return {
                "error": "No bash history found",
                "commands": [],
                "summary": {},
            }

        commands = []
        with history_path.open("r", errors="ignore") as handle:
            for line in handle.readlines()[-100:]:
                line = line.strip()
                if not line or self._is_sensitive(line):
                    continue
                commands.append({
                    "command": line,
                    "category": self._categorize(line),
                })

        return {
            "commands": commands[-50:],
            "summary": self._build_summary(commands),
        }

    def _is_sensitive(self, cmd: str) -> bool:
        cmd_lower = cmd.lower()
        return any(pattern in cmd_lower for pattern in self.SENSITIVE_PATTERNS)

    def _categorize(self, cmd: str) -> str:
        if cmd.startswith("git"):
            return "git"
        if cmd.startswith(("cd", "ls", "pwd", "cat", "head", "tail")):
            return "navigation"
        if cmd.startswith(("python", "pip")):
            return "python"
        if cmd.startswith("curl"):
            return "http"
        if cmd.startswith(("docker", "docker-compose")):
            return "docker"
        return "other"

    def _build_summary(self, commands: list) -> dict:
        by_category = {}
        for cmd in commands:
            category = cmd["category"]
            by_category[category] = by_category.get(category, 0) + 1
        return {
            "total_commands": len(commands),
            "by_category": by_category,
        }

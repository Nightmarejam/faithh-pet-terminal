from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
import json


class BaseCollector(ABC):
    """Base class for all passive collectors."""

    name: str = "base"
    version: str = "1.0"

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path.home() / "ai-stack" / "collectors" / "state"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def collect(self) -> dict:
        """Collect data and return a dict. Override in subclasses."""
        raise NotImplementedError

    def run(self) -> dict:
        """Run collection and save output."""
        try:
            data = self.collect()
            output = {
                "collected_at": datetime.utcnow().isoformat() + "Z",
                "collector": self.name,
                "version": self.version,
                "success": True,
                "data": data,
            }
        except Exception as exc:
            output = {
                "collected_at": datetime.utcnow().isoformat() + "Z",
                "collector": self.name,
                "version": self.version,
                "success": False,
                "error": str(exc),
                "data": {},
            }

        self._save(output)
        return output

    def _save(self, data: dict) -> None:
        """Save output to JSON file using collector name."""
        output_path = self.output_dir / f"{self.name}.json"
        with output_path.open("w") as handle:
            json.dump(data, handle, indent=2)

    def load_previous(self) -> dict:
        """Load previous collection for delta comparison."""
        output_path = self.output_dir / f"{self.name}.json"
        if output_path.exists():
            with output_path.open() as handle:
                return json.load(handle)
        return {}

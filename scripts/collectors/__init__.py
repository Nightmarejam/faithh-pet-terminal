"""
Passive Collection System for FAITHH.

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
from .director import CompassDirector

__all__ = [
    "BaseCollector",
    "GitCollector",
    "FileCollector",
    "HealthCollector",
    "TerminalCollector",
    "Aggregator",
    "CompassDirector",
]

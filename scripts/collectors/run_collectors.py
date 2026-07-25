#!/usr/bin/env python3
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
import logging
from pathlib import Path
from datetime import datetime, timezone

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.collectors.git_collector import GitCollector
from scripts.collectors.file_collector import FileCollector
from scripts.collectors.health_collector import HealthCollector
from scripts.collectors.terminal_collector import TerminalCollector
from scripts.collectors.aggregator import Aggregator
from scripts.collectors.collector_runner import CollectorRunner

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/jonat/ai-stack/logs/collectors.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Run passive collectors")
    parser.add_argument("--git", action="store_true", help="Run git collector")
    parser.add_argument("--files", action="store_true", help="Run file collector")
    parser.add_argument("--health", action="store_true", help="Run health collector")
    parser.add_argument("--terminal", action="store_true", help="Run terminal collector")
    parser.add_argument("--aggregate", action="store_true", help="Aggregate results")
    parser.add_argument("--snapshot", action="store_true", help="Save daily snapshot")
    parser.add_argument("--all", action="store_true", help="Run all collectors")

    args = parser.parse_args()

    run_all = args.all or not any(
        [
            args.git,
            args.files,
            args.health,
            args.terminal,
            args.aggregate,
            args.snapshot,
        ]
    )

    # Initialize runner with retry logic
    runner = CollectorRunner(max_retries=3, base_delay=60)
    results = {}
    start_time = datetime.now(timezone.utc)

    if run_all or args.git:
        logger.info("Running git collector...")
        collector = GitCollector()
        results["git"] = runner.run_with_retry(collector)
        if results["git"]["success"]:
            logger.info("  [OK] Saved to collectors/state/git.json")
        else:
            logger.error(f"  [FAIL] {results['git'].get('error', 'Unknown error')}")

    if run_all or args.files:
        logger.info("Running file collector...")
        collector = FileCollector()
        results["file_changes"] = runner.run_with_retry(collector)
        if results["file_changes"]["success"]:
            logger.info("  [OK] Saved to collectors/state/file_changes.json")
        else:
            logger.error(f"  [FAIL] {results['file_changes'].get('error', 'Unknown error')}")

    if run_all or args.health:
        logger.info("Running health collector...")
        collector = HealthCollector()
        results["health"] = runner.run_with_retry(collector)
        if results["health"]["success"]:
            logger.info("  [OK] Saved to collectors/state/health.json")
        else:
            logger.error(f"  [FAIL] {results['health'].get('error', 'Unknown error')}")

    if run_all or args.terminal:
        logger.info("Running terminal collector...")
        collector = TerminalCollector()
        results["terminal"] = runner.run_with_retry(collector)
        if results["terminal"]["success"]:
            logger.info("  [OK] Saved to collectors/state/terminal.json")
        else:
            logger.error(f"  [FAIL] {results['terminal'].get('error', 'Unknown error')}")

    if run_all or args.aggregate or results:
        logger.info("Aggregating results...")
        aggregator = Aggregator()
        aggregated = aggregator.aggregate()
        logger.info(f"  Status: {aggregated['ai_context']['status_line']}")

    if args.snapshot or run_all:
        logger.info("Saving daily snapshot...")
        aggregator = Aggregator()
        path = aggregator.save_daily_snapshot()
        logger.info(f"  [OK] Snapshot saved to: {path}")

    # Log summary
    end_time = datetime.now(timezone.utc)
    duration = (end_time - start_time).total_seconds()
    successful = sum(1 for r in results.values() if r.get("success"))
    
    logger.info(f"\n=== Collector Run Summary ===")
    logger.info(f"Duration: {duration:.2f}s")
    logger.info(f"Successful: {successful}/{len(results)}")
    
    error_summary = runner.get_error_summary()
    if error_summary["total_errors"] > 0:
        logger.warning(f"Total errors: {error_summary['total_errors']}")
        if error_summary["needs_attention"]:
            logger.warning("⚠️ High error rate - needs attention")
    
    logger.info("Done!")
    return results


if __name__ == "__main__":
    main()

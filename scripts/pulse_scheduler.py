#!/usr/bin/env python3
"""
FAITHH PULSE Scheduler
======================
Runs PULSE sweeps on a schedule, producing fresh reports for the autonomous system.

Tiers:
  - Tier 1: Staleness detection (every 6 hours)
  - Tier 2: Decision divergence (every 24 hours) 
  - Tier 3: Branch exploration (every 48 hours)
  - Tier 4: Autonomous actions (after each sweep)

Usage:
  python scripts/pulse_scheduler.py                # Run once (all due sweeps)
  python scripts/pulse_scheduler.py --daemon       # Run as background daemon
  python scripts/pulse_scheduler.py --force-all    # Force run all tiers now
  python scripts/pulse_scheduler.py --status       # Show schedule status

The scheduler tracks last run times in ml/output/pulse_schedule.json
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
SCHEDULE_FILE = BASE_DIR / "ml" / "output" / "pulse_schedule.json"
VENV_PYTHON = BASE_DIR / "venv" / "bin" / "python3"

# Schedule intervals (in hours)
SCHEDULE = {
    "staleness": {
        "script": "scripts/staleness_detector.py",
        "interval_hours": 6,
        "description": "Tier 1: Document staleness detection",
        "timeout": 120,
    },
    "divergence": {
        "script": "scripts/decision_divergence.py",
        "interval_hours": 24,
        "description": "Tier 2: Decision divergence analysis",
        "timeout": 600,  # LLM calls can be slow
        "args": ["--model", "qwen25-grounded:latest"],
    },
    "branches": {
        "script": "scripts/branch_explorer.py",
        "interval_hours": 48,
        "description": "Tier 3: Branch exploration",
        "timeout": 300,
    },
    "autonomous": {
        "script": "scripts/pulse_autonomous.py",
        "interval_hours": 1,  # Run after any other sweep
        "description": "Tier 4: Autonomous actions & avatar state",
        "timeout": 60,
    },
    "fingerprint": {
        "script": "scripts/generate_fingerprint.py",
        "interval_hours": 4,
        "description": "System fingerprint refresh",
        "timeout": 30,
    },
}

DAEMON_CHECK_INTERVAL = 300  # Check every 5 minutes when running as daemon


def load_schedule():
    """Load last run times from schedule file."""
    if SCHEDULE_FILE.exists():
        try:
            with open(SCHEDULE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_runs": {}, "run_counts": {}}


def save_schedule(data):
    """Save schedule state."""
    SCHEDULE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SCHEDULE_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def is_due(task_name: str, schedule_data: dict) -> bool:
    """Check if a task is due to run."""
    task = SCHEDULE.get(task_name)
    if not task:
        return False
    
    last_run = schedule_data.get("last_runs", {}).get(task_name)
    if not last_run:
        return True  # Never run before
    
    try:
        last_dt = datetime.fromisoformat(last_run)
        interval = timedelta(hours=task["interval_hours"])
        return datetime.now() > last_dt + interval
    except Exception:
        return True


def run_task(task_name: str, schedule_data: dict, force: bool = False) -> dict:
    """Run a PULSE task."""
    task = SCHEDULE.get(task_name)
    if not task:
        return {"success": False, "error": f"Unknown task: {task_name}"}
    
    script_path = BASE_DIR / task["script"]
    if not script_path.exists():
        return {"success": False, "error": f"Script not found: {task['script']}"}
    
    # Check if due (unless forced)
    if not force and not is_due(task_name, schedule_data):
        return {"success": True, "skipped": True, "reason": "Not due yet"}
    
    print(f"\n🔄 Running {task['description']}...")
    print(f"   Script: {task['script']}")
    
    # Build command
    python_exe = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable
    cmd = [python_exe, str(script_path)]
    if "args" in task:
        cmd.extend(task["args"])
    
    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=task.get("timeout", 300),
        )
        elapsed = time.time() - start
        
        success = result.returncode == 0
        
        # Update schedule
        if success:
            schedule_data.setdefault("last_runs", {})[task_name] = datetime.now().isoformat()
            schedule_data.setdefault("run_counts", {})[task_name] = \
                schedule_data.get("run_counts", {}).get(task_name, 0) + 1
            save_schedule(schedule_data)
        
        status = "✅" if success else "❌"
        print(f"   {status} Completed in {elapsed:.1f}s (exit code: {result.returncode})")
        
        if not success and result.stderr:
            print(f"   Error: {result.stderr[:200]}")
        
        return {
            "success": success,
            "elapsed": round(elapsed, 1),
            "returncode": result.returncode,
            "stdout_tail": result.stdout[-500:] if result.stdout else "",
            "stderr_tail": result.stderr[-200:] if result.stderr else "",
        }
        
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timeout after {task.get('timeout', 300)}s")
        return {"success": False, "error": "timeout"}
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"success": False, "error": str(e)}


def show_status(schedule_data: dict):
    """Show current schedule status."""
    print("\n" + "=" * 60)
    print("FAITHH PULSE Schedule Status")
    print("=" * 60)
    
    now = datetime.now()
    
    for task_name, task in SCHEDULE.items():
        last_run = schedule_data.get("last_runs", {}).get(task_name)
        run_count = schedule_data.get("run_counts", {}).get(task_name, 0)
        
        if last_run:
            last_dt = datetime.fromisoformat(last_run)
            age_hours = (now - last_dt).total_seconds() / 3600
            next_due = last_dt + timedelta(hours=task["interval_hours"])
            
            if now > next_due:
                status = "🔴 OVERDUE"
                time_str = f"{age_hours:.1f}h ago"
            else:
                status = "🟢 OK"
                until = (next_due - now).total_seconds() / 3600
                time_str = f"next in {until:.1f}h"
        else:
            status = "⚪ NEVER RUN"
            time_str = "—"
        
        print(f"\n{status} {task['description']}")
        print(f"   Interval: every {task['interval_hours']}h | Last: {time_str} | Runs: {run_count}")
    
    print("\n" + "=" * 60)


def run_due_tasks(schedule_data: dict, force_all: bool = False) -> dict:
    """Run all due tasks."""
    results = {}
    any_ran = False
    
    # Run in order: staleness -> divergence -> branches -> autonomous -> fingerprint
    task_order = ["staleness", "divergence", "branches", "autonomous", "fingerprint"]
    
    for task_name in task_order:
        if force_all or is_due(task_name, schedule_data):
            results[task_name] = run_task(task_name, schedule_data, force=force_all)
            if not results[task_name].get("skipped"):
                any_ran = True
    
    if not any_ran and not force_all:
        print("\n✨ All tasks up to date. Nothing to run.")
    
    return results


def run_daemon(schedule_data: dict):
    """Run as a background daemon, checking periodically."""
    print("🐕 PULSE Scheduler Daemon starting...")
    print(f"   Check interval: {DAEMON_CHECK_INTERVAL}s")
    print("   Press Ctrl+C to stop.\n")
    
    try:
        while True:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking schedule...")
            schedule_data = load_schedule()  # Reload in case of external changes
            run_due_tasks(schedule_data)
            
            print(f"   Sleeping {DAEMON_CHECK_INTERVAL}s until next check...")
            time.sleep(DAEMON_CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Daemon stopped by user.")


def main():
    parser = argparse.ArgumentParser(description="FAITHH PULSE Scheduler")
    parser.add_argument("--daemon", action="store_true", help="Run as background daemon")
    parser.add_argument("--force-all", action="store_true", help="Force run all tiers now")
    parser.add_argument("--status", action="store_true", help="Show schedule status")
    parser.add_argument("--task", type=str, help="Run specific task (staleness, divergence, branches, autonomous, fingerprint)")
    args = parser.parse_args()
    
    schedule_data = load_schedule()
    
    if args.status:
        show_status(schedule_data)
        return
    
    if args.task:
        if args.task not in SCHEDULE:
            print(f"Unknown task: {args.task}")
            print(f"Available: {', '.join(SCHEDULE.keys())}")
            return
        run_task(args.task, schedule_data, force=True)
        return
    
    if args.daemon:
        run_daemon(schedule_data)
        return
    
    # Default: run all due tasks
    print("🔍 FAITHH PULSE Scheduler")
    print(f"   Schedule file: {SCHEDULE_FILE.relative_to(BASE_DIR)}")
    
    run_due_tasks(schedule_data, force_all=args.force_all)
    
    print("\n💡 Use --status to see full schedule, --daemon to run continuously")


if __name__ == "__main__":
    main()

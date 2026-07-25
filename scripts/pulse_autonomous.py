#!/usr/bin/env python3
"""
FAITHH PULSE Tier 4 — Autonomous Actions
==========================================
Reads Tier 1-3 reports, determines system health state,
triggers self-healing actions, and produces avatar mood for the frontend.

Actions:
  - Detect stale docs above threshold → flag for re-index
  - Detect critical divergence → flag for review
  - Surface promising branches → notify via avatar mood
  - Auto-regenerate CONTEXT.md when staleness exceeds threshold
  - Produce avatar state (mood, energy, alert level) for UI

Output: ml/output/pulse_state.json — consumed by backend /api/pulse/state

Usage:
  python scripts/pulse_autonomous.py              # Full analysis + actions
  python scripts/pulse_autonomous.py --dry-run    # Analysis only, no actions
  python scripts/pulse_autonomous.py --json       # JSON output to stdout
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
PULSE_DIR = BASE_DIR / "ml" / "output"
STATE_FILE = PULSE_DIR / "pulse_state.json"
CONTEXT_MD = BASE_DIR / "CONTEXT.md"
STALENESS_REPORT = PULSE_DIR / "staleness_report.md"
DIVERGENCE_REPORT = PULSE_DIR / "divergence_report.md"
BRANCH_REPORT = PULSE_DIR / "branch_report.md"

# Thresholds
STALENESS_CRITICAL_THRESHOLD = 3  # Number of critical files to trigger action
STALENESS_WARNING_THRESHOLD = 5
DIVERGENCE_SCORE_THRESHOLD = 2  # Alignment score <= 2 is concerning
REPORT_MAX_AGE_HOURS = 48  # Reports older than this are considered stale themselves
CONTEXT_REGEN_AGE_DAYS = 7  # Regenerate CONTEXT.md if older than this


# ============================================================
# Report Parsing
# ============================================================

def parse_staleness_report():
    """Parse the staleness report for critical/warning counts."""
    if not STALENESS_REPORT.exists():
        return None

    content = STALENESS_REPORT.read_text(encoding="utf-8")
    mtime = datetime.fromtimestamp(STALENESS_REPORT.stat().st_mtime)
    age_hours = (datetime.now() - mtime).total_seconds() / 3600

    result = {
        "available": True,
        "generated_at": mtime.isoformat(),
        "age_hours": round(age_hours, 1),
        "stale_itself": age_hours > REPORT_MAX_AGE_HOURS,
        "critical": 0,
        "warning": 0,
        "ok": 0,
        "broken_refs": 0,
        "stale_files": [],
    }

    # Parse summary section
    for line in content.split("\n"):
        line = line.strip()
        if "**Critical:**" in line:
            m = re.search(r"(\d+)", line.split("Critical:")[-1])
            if m:
                result["critical"] = int(m.group(1))
        elif "**Warning:**" in line:
            m = re.search(r"(\d+)", line.split("Warning:")[-1])
            if m:
                result["warning"] = int(m.group(1))
        elif "**OK:**" in line:
            m = re.search(r"(\d+)", line.split("OK:")[-1])
            if m:
                result["ok"] = int(m.group(1))
        elif "broken" in line.lower() and "ref" in line.lower():
            m = re.search(r"(\d+)", line)
            if m:
                result["broken_refs"] = int(m.group(1))

    return result


def parse_divergence_report():
    """Parse the divergence report for concerning decisions."""
    if not DIVERGENCE_REPORT.exists():
        return None

    content = DIVERGENCE_REPORT.read_text(encoding="utf-8")
    mtime = datetime.fromtimestamp(DIVERGENCE_REPORT.stat().st_mtime)
    age_hours = (datetime.now() - mtime).total_seconds() / 3600

    result = {
        "available": True,
        "generated_at": mtime.isoformat(),
        "age_hours": round(age_hours, 1),
        "stale_itself": age_hours > REPORT_MAX_AGE_HOURS,
        "total_decisions": 0,
        "concerning": [],
        "healthy": 0,
    }

    # Parse alignment scores
    current_decision = None
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("### ") and "faithh_" in line.lower():
            current_decision = line.replace("### ", "").strip()
        elif "alignment" in line.lower() and current_decision:
            m = re.search(r"(\d+)/5", line)
            if m:
                score = int(m.group(1))
                result["total_decisions"] += 1
                if score <= DIVERGENCE_SCORE_THRESHOLD:
                    result["concerning"].append({
                        "decision": current_decision,
                        "score": score,
                    })
                else:
                    result["healthy"] += 1
                current_decision = None

    return result


def parse_branch_report():
    """Parse the branch report for promising ideas."""
    if not BRANCH_REPORT.exists():
        return None

    content = BRANCH_REPORT.read_text(encoding="utf-8")
    mtime = datetime.fromtimestamp(BRANCH_REPORT.stat().st_mtime)
    age_hours = (datetime.now() - mtime).total_seconds() / 3600

    result = {
        "available": True,
        "generated_at": mtime.isoformat(),
        "age_hours": round(age_hours, 1),
        "stale_itself": age_hours > REPORT_MAX_AGE_HOURS,
        "total_ideas": 0,
        "high_value": [],
        "categories": {},
    }

    # Parse ideas
    current_idea = None
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("### ") or (line.startswith("**") and ":" in line):
            current_idea = line.replace("### ", "").replace("**", "").strip()
            result["total_ideas"] += 1
        elif "score" in line.lower() and current_idea:
            m = re.search(r"(\d+\.?\d*)/10", line)
            if m:
                score = float(m.group(1))
                if score >= 7.0:
                    result["high_value"].append({
                        "idea": current_idea[:80],
                        "score": score,
                    })
        elif "timing" in line.lower() and "now" in line.lower():
            if current_idea and current_idea[:80] not in [h["idea"] for h in result["high_value"]]:
                result["high_value"].append({
                    "idea": current_idea[:80],
                    "score": 0,
                    "timing": "now",
                })

    return result


# ============================================================
# Avatar State Machine
# ============================================================

def determine_avatar_state(staleness, divergence, branches):
    """Determine avatar mood, energy, and alert level from PULSE data."""

    mood = "calm"  # calm, curious, excited, concerned, alert
    energy = 0.5  # 0.0 = dormant, 1.0 = highly active
    alerts = []
    suggestions = []

    # Check staleness
    if staleness:
        if staleness["stale_itself"]:
            alerts.append("Staleness report is outdated — PULSE sweep needed")
            mood = "concerned"
            energy = max(energy, 0.6)
        if staleness["critical"] >= STALENESS_CRITICAL_THRESHOLD:
            alerts.append(f"{staleness['critical']} critical stale files detected")
            mood = "alert"
            energy = max(energy, 0.8)
        elif staleness["warning"] >= STALENESS_WARNING_THRESHOLD:
            alerts.append(f"{staleness['warning']} files have staleness warnings")
            mood = "concerned"
            energy = max(energy, 0.6)
        if staleness["broken_refs"] > 0:
            alerts.append(f"{staleness['broken_refs']} broken references found")
            mood = "concerned" if mood != "alert" else mood
            energy = max(energy, 0.7)

    # Check divergence
    if divergence:
        if divergence["stale_itself"]:
            alerts.append("Divergence report is outdated")
        if divergence["concerning"]:
            for d in divergence["concerning"][:3]:
                alerts.append(f"Decision '{d['decision']}' diverging (score {d['score']}/5)")
            mood = "alert" if len(divergence["concerning"]) >= 2 else "concerned"
            energy = max(energy, 0.7)

    # Check branches
    if branches:
        if branches["high_value"]:
            for b in branches["high_value"][:2]:
                suggestions.append(f"Promising: {b['idea']}")
            if mood in ("calm",):
                mood = "curious"
            energy = max(energy, 0.6)

    # All clear?
    if not alerts and not suggestions:
        if staleness and divergence and branches:
            mood = "calm"
            energy = 0.3
            suggestions.append("All systems healthy. Good time for creative work.")
        else:
            mood = "curious"
            energy = 0.4
            suggestions.append("Some PULSE reports missing. Consider running a sweep.")

    return {
        "mood": mood,
        "energy": round(energy, 2),
        "alerts": alerts,
        "suggestions": suggestions,
        "alert_count": len(alerts),
    }


# ============================================================
# Self-Healing Actions
# ============================================================

def check_context_freshness():
    """Check if CONTEXT.md needs regeneration."""
    if not CONTEXT_MD.exists():
        return {"needs_regen": True, "reason": "CONTEXT.md does not exist"}

    mtime = datetime.fromtimestamp(CONTEXT_MD.stat().st_mtime)
    age_days = (datetime.now() - mtime).total_seconds() / 86400

    if age_days > CONTEXT_REGEN_AGE_DAYS:
        return {
            "needs_regen": True,
            "reason": f"CONTEXT.md is {age_days:.1f} days old (threshold: {CONTEXT_REGEN_AGE_DAYS}d)",
            "last_modified": mtime.isoformat(),
        }

    return {
        "needs_regen": False,
        "age_days": round(age_days, 1),
        "last_modified": mtime.isoformat(),
    }


def execute_healing_actions(dry_run=False):
    """Execute any needed self-healing actions."""
    actions_taken = []

    # Check CONTEXT.md freshness
    ctx = check_context_freshness()
    if ctx.get("needs_regen"):
        if dry_run:
            actions_taken.append({
                "action": "regenerate_context",
                "reason": ctx["reason"],
                "status": "dry_run",
            })
        else:
            # Try to regenerate CONTEXT.md
            script = BASE_DIR / "scripts" / "generate_context.py"
            if script.exists():
                try:
                    proc = subprocess.run(
                        [sys.executable, str(script)],
                        cwd=BASE_DIR, capture_output=True, text=True, timeout=60,
                    )
                    actions_taken.append({
                        "action": "regenerate_context",
                        "reason": ctx["reason"],
                        "status": "success" if proc.returncode == 0 else "failed",
                        "output": proc.stdout[-500:] if proc.stdout else "",
                    })
                except Exception as e:
                    actions_taken.append({
                        "action": "regenerate_context",
                        "reason": ctx["reason"],
                        "status": "error",
                        "error": str(e),
                    })
            else:
                actions_taken.append({
                    "action": "regenerate_context",
                    "reason": ctx["reason"],
                    "status": "skipped",
                    "note": "generate_context.py not found",
                })

    return actions_taken


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="FAITHH PULSE Tier 4 — Autonomous Actions")
    parser.add_argument("--dry-run", action="store_true", help="Analysis only, no actions")
    parser.add_argument("--json", action="store_true", help="JSON output to stdout")
    args = parser.parse_args()

    start = time.time()

    # Parse all reports
    print("🔍 Parsing PULSE reports...")
    staleness = parse_staleness_report()
    divergence = parse_divergence_report()
    branches = parse_branch_report()

    available = sum(1 for r in [staleness, divergence, branches] if r)
    print(f"   {available}/3 reports available")

    # Determine avatar state
    print("🎭 Determining avatar state...")
    avatar = determine_avatar_state(staleness, divergence, branches)
    print(f"   Mood: {avatar['mood']}, Energy: {avatar['energy']}, Alerts: {avatar['alert_count']}")

    # Check healing needs
    print("🩺 Checking healing actions...")
    healing = execute_healing_actions(dry_run=args.dry_run)
    if healing:
        for h in healing:
            print(f"   {h['action']}: {h['status']} — {h.get('reason', '')}")
    else:
        print("   No healing actions needed")

    # Build state
    state = {
        "meta": {
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "elapsed_seconds": round(time.time() - start, 2),
            "dry_run": args.dry_run,
        },
        "avatar": avatar,
        "reports": {
            "staleness": staleness,
            "divergence": divergence,
            "branches": branches,
        },
        "context_md": check_context_freshness(),
        "healing_actions": healing,
    }

    # Save
    PULSE_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    print(f"\n💾 State saved: {STATE_FILE.relative_to(BASE_DIR)}")

    if args.json:
        print(json.dumps(state, indent=2))
    else:
        elapsed = round(time.time() - start, 2)
        print(f"⏱️  Completed in {elapsed}s")
        if avatar["alerts"]:
            print(f"\n⚠️  Alerts ({len(avatar['alerts'])}):")
            for a in avatar["alerts"]:
                print(f"   - {a}")
        if avatar["suggestions"]:
            print(f"\n💡 Suggestions:")
            for s in avatar["suggestions"]:
                print(f"   - {s}")


if __name__ == "__main__":
    main()

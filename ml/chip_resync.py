#!/usr/bin/env python3
"""
FAITHH Chip Re-Sync — Native Auto-Update for ML Chips
======================================================

Checks if the chip synthesis needs to be re-run based on ChromaDB chunk count
vs last synthesis count. If threshold exceeded, runs the full pipeline:
  chip_synthesis.py → consolidate_chips.py → reload signal

Can be triggered:
  - CLI:      python ml/chip_resync.py [--force] [--threshold 10]
  - Backend:  POST /api/ml/chips/resync
  - Cron:     0 3 * * * cd ~/ai-stack && ml/venv/bin/python ml/chip_resync.py

Usage:
    python ml/chip_resync.py                  # Check + run if needed
    python ml/chip_resync.py --force          # Force re-synthesis regardless
    python ml/chip_resync.py --check-only     # Just report status, don't run
    python ml/chip_resync.py --threshold 5    # Run if >5% new chunks
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Target RTX 3090 (GPU 1)
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

BASE_DIR = Path(__file__).parent.parent  # ~/ai-stack
ML_DIR = Path(__file__).parent            # ~/ai-stack/ml
OUTPUT_DIR = ML_DIR / "output"
CHIPS_FILE = OUTPUT_DIR / "chips.json"
CONSOLIDATED_FILE = OUTPUT_DIR / "consolidated_chips.json"
RESYNC_LOG = OUTPUT_DIR / "resync_history.json"

CHROMA_HOST = os.environ.get("CHROMA_HOST", "servicebox.taileb8c60.ts.net")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))
COLLECTION_NAME = os.environ.get("CHROMA_COLLECTION", "faithh_knowledge_base")


def get_current_chunk_count():
    """Query ChromaDB for current document count."""
    try:
        import chromadb
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        collection = client.get_collection(COLLECTION_NAME)
        return collection.count()
    except Exception as e:
        print(f"⚠️ ChromaDB query failed: {e}")
        return None


def get_last_synthesis_info():
    """Read metadata from last synthesis run."""
    if CHIPS_FILE.exists():
        try:
            with open(CHIPS_FILE) as f:
                data = json.load(f)
            pipeline = data.get("pipeline", {})
            return {
                "generated": data.get("generated", "unknown"),
                "input_docs": pipeline.get("input_docs", 0),
                "topics_discovered": pipeline.get("topics_discovered", 0),
                "version": data.get("version", "unknown"),
            }
        except Exception:
            pass
    return None


def load_resync_history():
    """Load the resync history log."""
    if RESYNC_LOG.exists():
        try:
            with open(RESYNC_LOG) as f:
                return json.load(f)
        except Exception:
            pass
    return {"runs": []}


def save_resync_history(history):
    """Save resync history."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESYNC_LOG, "w") as f:
        json.dump(history, f, indent=2)


def check_needs_resync(threshold_pct=10):
    """Check if re-synthesis is needed.
    
    Returns:
        (needs_resync: bool, status: dict)
    """
    current_count = get_current_chunk_count()
    if current_count is None:
        return False, {"error": "ChromaDB unavailable"}

    last_info = get_last_synthesis_info()
    if last_info is None:
        return True, {
            "reason": "no previous synthesis found",
            "current_chunks": current_count,
        }

    last_count = last_info["input_docs"]
    delta = current_count - last_count
    pct_change = (delta / last_count * 100) if last_count > 0 else 100

    status = {
        "current_chunks": current_count,
        "last_synthesis_chunks": last_count,
        "delta": delta,
        "pct_change": round(pct_change, 1),
        "threshold_pct": threshold_pct,
        "last_generated": last_info["generated"],
        "last_topics": last_info["topics_discovered"],
    }

    if pct_change >= threshold_pct:
        status["reason"] = f"{pct_change:.1f}% new chunks (threshold: {threshold_pct}%)"
        return True, status
    else:
        status["reason"] = f"only {pct_change:.1f}% change (threshold: {threshold_pct}%)"
        return False, status


def run_synthesis():
    """Run the full synthesis + consolidation pipeline."""
    venv_python = ML_DIR / "venv" / "bin" / "python"
    if not venv_python.exists():
        venv_python = sys.executable

    env = os.environ.copy()
    env["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    env["CUDA_VISIBLE_DEVICES"] = "1"

    # Step 1: Chip synthesis
    print("\n" + "=" * 60)
    print("🧠 Running chip synthesis...")
    print("=" * 60)
    result = subprocess.run(
        [str(venv_python), str(ML_DIR / "chip_synthesis.py")],
        cwd=str(BASE_DIR),
        env=env,
        capture_output=False,
        timeout=600,  # 10 min max
    )
    if result.returncode != 0:
        print(f"❌ Chip synthesis failed (exit code {result.returncode})")
        return False

    # Step 2: Consolidation
    print("\n" + "=" * 60)
    print("🔬 Running chip consolidation...")
    print("=" * 60)
    result = subprocess.run(
        [str(venv_python), str(ML_DIR / "consolidate_chips.py")],
        cwd=str(BASE_DIR),
        env=env,
        capture_output=False,
        timeout=120,  # 2 min max
    )
    if result.returncode != 0:
        print(f"❌ Chip consolidation failed (exit code {result.returncode})")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(description="FAITHH Chip Re-Sync")
    parser.add_argument("--force", action="store_true", help="Force re-synthesis")
    parser.add_argument("--check-only", action="store_true", help="Check status only")
    parser.add_argument("--threshold", type=float, default=10,
                        help="Percentage of new chunks to trigger resync (default: 10)")
    args = parser.parse_args()

    print("=" * 60)
    print("FAITHH CHIP RE-SYNC")
    print("=" * 60)

    # Check status
    needs_resync, status = check_needs_resync(threshold_pct=args.threshold)

    print(f"\n📊 Status:")
    for k, v in status.items():
        print(f"   {k}: {v}")

    if args.force:
        needs_resync = True
        status["reason"] = "forced by user"
        print(f"\n⚡ Force mode — running regardless of threshold")

    if args.check_only:
        print(f"\n{'✅ Resync needed' if needs_resync else '⏸️  No resync needed'}")
        return

    if not needs_resync:
        print(f"\n⏸️  No resync needed — {status.get('reason', 'threshold not met')}")
        return

    print(f"\n🚀 Starting resync — {status.get('reason', '')}")
    start_time = time.time()

    success = run_synthesis()
    elapsed = time.time() - start_time

    # Log the run
    history = load_resync_history()
    run_entry = {
        "timestamp": datetime.now().isoformat(),
        "success": success,
        "duration_seconds": round(elapsed, 1),
        "trigger": "forced" if args.force else "threshold",
        "status": status,
    }

    # Add post-synthesis info if successful
    if success:
        new_info = get_last_synthesis_info()
        if new_info:
            run_entry["result"] = new_info

    history["runs"].append(run_entry)
    # Keep last 20 runs
    history["runs"] = history["runs"][-20:]
    save_resync_history(history)

    if success:
        print(f"\n✅ Resync complete in {elapsed:.1f}s")
        print(f"   Log saved to {RESYNC_LOG}")
        print(f"\n   ⚠️  Restart the FAITHH backend to load new chips:")
        print(f"   ./restart_backend.sh")
    else:
        print(f"\n❌ Resync failed after {elapsed:.1f}s")


if __name__ == "__main__":
    main()

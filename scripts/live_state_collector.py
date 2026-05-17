#!/usr/bin/env python3
"""
FAITHH Live State Collector
============================
Polls live services and writes faithh_live_state.json.
Run every 15 minutes via cron.

Usage:
    python scripts/live_state_collector.py
    python scripts/live_state_collector.py --verbose
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).parent.parent

CHROMA_HOST = "192.158.1.10"
CHROMA_PORT = 8000
CHROMA_COLLECTION = "faithh_knowledge_base"
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 5557
STABILITY_THRESHOLD = 6  # checks before imprint is allowed
OUTPUT_FILE = BASE_DIR / "faithh_live_state.json"


def check_chromadb(verbose=False):
    """Query ChromaDB for live chunk count."""
    result = {"reachable": False, "chunk_count": None, "collection": None, "error": None}
    try:
        import chromadb
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        col = client.get_collection(CHROMA_COLLECTION)
        count = col.count()
        result.update({
            "reachable": True,
            "chunk_count": count,
            "collection": col.name,
        })
        if verbose:
            print(f"  ChromaDB: {count} chunks in {col.name}")
    except Exception as e:
        result["error"] = str(e)
        if verbose:
            print(f"  ChromaDB: unreachable ({e})")
    return result


def check_backend(verbose=False):
    """Check FAITHH backend health."""
    result = {"reachable": False, "version": None, "error": None}
    try:
        import urllib.request
        url = f"http://{BACKEND_HOST}:{BACKEND_PORT}/health"
        with urllib.request.urlopen(url, timeout=5) as r:
            data = json.loads(r.read())
            result.update({
                "reachable": True,
                "version": data.get("version") or data.get("status"),
            })
            if verbose:
                print(f"  Backend: reachable, version={result['version']}")
    except Exception as e:
        result["error"] = str(e)
        if verbose:
            print(f"  Backend: unreachable ({e})")
    return result


def compute_stability(current_count, previous_state):
    """
    Track how many consecutive checks have seen the same chunk count.
    Stability gate prevents mid-reindex values from being imprinted.
    """
    prev_count = previous_state.get("chroma", {}).get("chunk_count")
    prev_stable = previous_state.get("stability", {}).get("chunk_count_stable_for_checks", 0)

    if prev_count is not None and current_count == prev_count:
        return prev_stable + 1
    else:
        return 1  # reset — count changed


def load_previous_state():
    if OUTPUT_FILE.exists():
        try:
            return json.loads(OUTPUT_FILE.read_text())
        except Exception:
            pass
    return {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        print(f"\nFAITHH Live State Collector — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")

    previous = load_previous_state()
    chroma = check_chromadb(args.verbose)
    backend = check_backend(args.verbose)

    stable_checks = compute_stability(chroma.get("chunk_count"), previous)
    ready_to_imprint = (
        chroma["reachable"]
        and stable_checks >= STABILITY_THRESHOLD
    )

    last_imprint = previous.get("stability", {}).get("last_imprint", "never")

    state = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "chroma": chroma,
        "backend": backend,
        "stability": {
            "chunk_count_stable_for_checks": stable_checks,
            "stability_threshold": STABILITY_THRESHOLD,
            "ready_to_imprint": ready_to_imprint,
            "last_imprint": last_imprint,
        }
    }

    OUTPUT_FILE.write_text(json.dumps(state, indent=2))

    if args.verbose:
        print(f"  Stability: {stable_checks}/{STABILITY_THRESHOLD} checks")
        print(f"  Ready to imprint: {ready_to_imprint}")
        print(f"  Written: {OUTPUT_FILE}")

    # Exit code 0 = healthy, 1 = ChromaDB unreachable (useful for cron alerts)
    sys.exit(0 if chroma["reachable"] else 1)


if __name__ == "__main__":
    main()

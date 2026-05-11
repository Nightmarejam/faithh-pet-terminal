"""Update project_states.json deterministically (MERGE mode).

Goals:
- Single source of truth for machine-readable system state.
- Safe: default is dry-run; writes only with --write.
- MERGES into existing JSON - preserves projects, timezone, etc.
- Only updates: meta.generated_at_utc, repo.*, services.*, submodules

This script intentionally avoids requiring the FAITHH backend to be running.
It will query Chroma if reachable.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import urllib.request


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "project_states.json"

# Use Gen8 Chroma by default (Tailscale IP)
DEFAULT_CHROMA = os.getenv("CHROMA_HOST", "http://192.158.1.243:8000").rstrip("/")
DEFAULT_BACKEND = os.getenv("FAITHH_BACKEND_URL", "http://127.0.0.1:5557").rstrip("/")


def sh(cmd: List[str]) -> str:
    try:
        return subprocess.check_output(
            cmd,
            cwd=ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return ""


def http_json(url: str, timeout: float = 2.5) -> Optional[Dict[str, Any]]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            data = r.read().decode("utf-8", errors="ignore")
        return json.loads(data)
    except Exception:
        return None


def chroma_heartbeat(chroma_base: str) -> Dict[str, Any]:
    """Check Chroma health, return status dict."""
    for path in ("/api/v2/heartbeat", "/api/v1/heartbeat"):
        j = http_json(chroma_base + path)
        if j is not None:
            return {"ok": True, "endpoint": path, "response": j}
    return {"ok": False}


def chroma_collection_stats(chroma_base: str, collection: str = "faithh_knowledge_base") -> Dict[str, Any]:
    """Get collection document count if available."""
    # Try to get collection info
    j = http_json(f"{chroma_base}/api/v1/collections/{collection}")
    if j and "id" in j:
        count_resp = http_json(f"{chroma_base}/api/v1/collections/{collection}/count")
        return {
            "collection": collection,
            "documents": count_resp if isinstance(count_resp, int) else "unknown"
        }
    return {"collection": collection, "documents": "unreachable"}


def submodule_status() -> List[Dict[str, str]]:
    raw = sh(["git", "submodule", "status", "--recursive"])
    out: List[Dict[str, str]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        sha = parts[0].lstrip("-+")
        path = parts[1] if len(parts) > 1 else ""
        extra = " ".join(parts[2:]).strip()
        out.append({"path": path, "sha": sha, "extra": extra})
    return out


def load_existing() -> Dict[str, Any]:
    """Load existing project_states.json or return empty dict."""
    if not OUT.exists():
        return {}
    try:
        return json.loads(OUT.read_text(encoding="utf-8"))
    except Exception:
        return {}


def build_updates() -> Dict[str, Any]:
    """Build the sections we update (not the full state)."""
    now_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
    today = datetime.now().strftime("%Y-%m-%d")
    head = sh(["git", "rev-parse", "--short", "HEAD"])
    branch = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    dirty = bool(sh(["git", "status", "--porcelain"]))
    
    return {
        "last_updated": today,
        "meta": {
            "generated_at_utc": now_utc,
            "generator": "scripts/maintenance/update_project_states.py",
        },
        "repo": {
            "path": str(ROOT),
            "branch": branch,
            "head": head,
            "dirty": dirty,
        },
        "services": {
            "faithh_backend_url": DEFAULT_BACKEND,
            "chroma_url": DEFAULT_CHROMA,
            "chroma_heartbeat": chroma_heartbeat(DEFAULT_CHROMA),
            "chroma_stats": chroma_collection_stats(DEFAULT_CHROMA),
        },
        "submodules": submodule_status(),
    }


def merge_state(old: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Merge updates into existing state, preserving projects/timezone/etc."""
    state = copy.deepcopy(old)
    
    # Update top-level scalars
    state["last_updated"] = updates["last_updated"]
    
    # Merge meta (preserve existing keys like documentation, git_status docs)
    if "meta" not in state:
        state["meta"] = {}
    state["meta"]["generated_at_utc"] = updates["meta"]["generated_at_utc"]
    state["meta"]["generator"] = updates["meta"]["generator"]
    
    # Update git_status within meta
    if "git_status" not in state["meta"]:
        state["meta"]["git_status"] = {}
    state["meta"]["git_status"]["branch"] = updates["repo"]["branch"]
    state["meta"]["git_status"]["head"] = updates["repo"]["head"]
    state["meta"]["git_status"]["uncommitted_work"] = updates["repo"]["dirty"]
    
    # Update services section (merge, don't replace)
    if "services" not in state:
        state["services"] = {}
    state["services"]["faithh_backend_url"] = updates["services"]["faithh_backend_url"]
    state["services"]["chroma_url"] = updates["services"]["chroma_url"]
    state["services"]["chroma_heartbeat"] = updates["services"]["chroma_heartbeat"]
    state["services"]["chroma_stats"] = updates["services"]["chroma_stats"]
    
    # Update submodules
    state["submodules"] = updates["submodules"]
    
    return state


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Update project_states.json (merge mode - preserves existing data)"
    )
    ap.add_argument(
        "--write",
        action="store_true",
        help="Write project_states.json (default is dry-run)",
    )
    ap.add_argument(
        "--print", 
        action="store_true", 
        help="Print resulting JSON to stdout"
    )
    ap.add_argument(
        "--diff",
        action="store_true",
        help="Show what would change"
    )
    args = ap.parse_args()

    old = load_existing()
    updates = build_updates()
    new = merge_state(old, updates)

    if args.diff:
        print("=== Changes ===")
        print(f"last_updated: {old.get('last_updated')} -> {new.get('last_updated')}")
        print(f"repo.head: {old.get('meta', {}).get('git_status', {}).get('head')} -> {new.get('meta', {}).get('git_status', {}).get('head')}")
        print(f"repo.dirty: {old.get('meta', {}).get('git_status', {}).get('uncommitted_work')} -> {new.get('meta', {}).get('git_status', {}).get('uncommitted_work')}")
        print(f"chroma_heartbeat.ok: {new.get('services', {}).get('chroma_heartbeat', {}).get('ok')}")
        print(f"submodules: {len(new.get('submodules', []))} entries")
        return 0

    if args.print or not args.write:
        print(json.dumps(new, indent=2, sort_keys=False))

    if args.write:
        OUT.write_text(
            json.dumps(new, indent=2, sort_keys=False) + "\n", encoding="utf-8"
        )
        print(f"Wrote {OUT}")
    else:
        print("Dry-run: not writing (use --write to persist).")

    # Summary
    if old:
        preserved = [k for k in old.keys() if k in new]
        print(f"Preserved keys: {preserved}")
    else:
        print("No previous project_states.json found - created new.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

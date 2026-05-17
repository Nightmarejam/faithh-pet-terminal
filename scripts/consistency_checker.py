#!/usr/bin/env python3
"""
FAITHH Consistency Checker
============================
Extracts "ground truth" facts from each state file and flags contradictions.
Run this after any major change, or on a weekly cron.

Usage:
    python scripts/consistency_checker.py
    python scripts/consistency_checker.py --json      # machine-readable output
    python scripts/consistency_checker.py --fix-hints # show how to fix each mismatch

Output:
    - PASS: fact matches across all sources
    - WARN: fact is missing from one source (may be intentional)
    - MISMATCH: same fact has different values across files (needs fixing)
"""

import json
import re
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime, timezone

# ── Config ──────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent.parent  # repo root

STATE_FILES = {
    "project_states":   BASE_DIR / "project_states.json",
    "scaffolding":      BASE_DIR / "scaffolding_state.json",
    "faithh_memory":    BASE_DIR / "faithh_memory.json",
    "decisions_log":    BASE_DIR / "decisions_log.json",
    "readme":           BASE_DIR / "README.md",
    "systems_map":      BASE_DIR / "SYSTEMS_MAP.md",
    "context_md":       BASE_DIR / "CONTEXT.md",
    "agents_md":        BASE_DIR / "AGENTS.md",
    "live_state":       BASE_DIR / "faithh_live_state.json",
}

# ── Extractors ───────────────────────────────────────────────────────────────
# Each extractor returns a dict of { fact_name: value } for one file.
# Return None for a fact if the file doesn't track it (WARN, not MISMATCH).

def extract_project_states(path: Path) -> dict:
    if not path.exists():
        return {"_file_missing": True}
    data = json.loads(path.read_text())
    faithh = data.get("projects", {}).get("FAITHH", {})
    infra = faithh.get("infrastructure", {})
    services = data.get("projects", {}).get("gen8_services", {})
    chroma = services.get("services_deployed", {}).get("chromadb", {})

    return {
        "faithh_phase":         faithh.get("phase"),
        "faithh_phase_status":  faithh.get("phase_status"),
        "chroma_collection":    infra.get("collection"),
        "chroma_chunks":        infra.get("chunks_indexed"),
        "embedding_model":      infra.get("embedding"),
        "chroma_port":          chroma.get("port"),
        "backend_url":          data.get("services", {}).get("faithh_backend_url"),
        "last_updated":         data.get("last_updated"),
    }


def extract_scaffolding(path: Path) -> dict:
    if not path.exists():
        return {"_file_missing": True}
    data = json.loads(path.read_text())
    active = data.get("active_context", {})
    milestones = data.get("project_structural_milestones", {}).get("faithh", {})

    return {
        "faithh_phase":         active.get("structural_position"),  # narrative, not enum
        "scaffolding_version":  data.get("meta", {}).get("version"),
        "last_updated":         data.get("meta", {}).get("last_updated"),
        "current_next":         milestones.get("next"),
    }


def extract_faithh_memory(path: Path) -> dict:
    if not path.exists():
        return {"_file_missing": True}
    try:
        data = json.loads(path.read_text())
    except Exception:
        return {"_parse_error": True}

    # Primary location: knowledge_base_status (current structure as of 2026-03)
    kb_status = data.get("knowledge_base_status", {})
    
    # Fallback paths for older structures
    system = data.get("system", data.get("faithh_system", {}))
    chroma = data.get("chromadb", data.get("database", system.get("chromadb", {})))

    return {
        "chroma_collection":  kb_status.get("collection") or chroma.get("collection") or data.get("collection"),
        "chroma_chunks":      kb_status.get("total_documents") or chroma.get("documents") or chroma.get("chunks") or data.get("documents_indexed"),
        "embedding_model":    kb_status.get("embedding_model") or chroma.get("embedding_model") or data.get("embedding_model"),
        "memory_version":     data.get("version") or data.get("_version"),
        "last_updated":       data.get("last_updated") or data.get("_last_updated"),
    }


def extract_readme(path: Path) -> dict:
    if not path.exists():
        return {"_file_missing": True}
    text = path.read_text()

    chunks_match = re.search(r'(\d[\d,]+)\s*chunk', text, re.IGNORECASE)
    port_match   = re.search(r'port\s*[:\|]\s*(\d{4,5})', text, re.IGNORECASE)
    phase_match  = re.search(r'Phase\s+(\d+)', text)

    return {
        "chroma_chunks":   int(chunks_match.group(1).replace(",", "")) if chunks_match else None,
        "backend_port":    port_match.group(1) if port_match else None,
        "phase_mentioned": phase_match.group(0) if phase_match else None,
    }


def extract_systems_map(path: Path) -> dict:
    if not path.exists():
        return {"_file_missing": True}
    text = path.read_text()

    chunks_match    = re.search(r'(\d[\d,]+)\s*chunk', text, re.IGNORECASE)
    collection_match = re.search(r'collection[:\s]+(\w+)', text)
    embed_match     = re.search(r'(all-\S+)\s*\((\d+)-dim\)', text)

    return {
        "chroma_chunks":     int(chunks_match.group(1).replace(",", "")) if chunks_match else None,
        "chroma_collection": collection_match.group(1) if collection_match else None,
        "embedding_model":   f"{embed_match.group(1)} ({embed_match.group(2)}-dim)" if embed_match else None,
    }


def extract_context_md(path: Path) -> dict:
    if not path.exists():
        return {"_file_missing": True}
    text = path.read_text()

    generated_match = re.search(r'generated:\s+"?([^"\n]+)"?', text)
    chunks_match    = re.search(r'(\d[\d,]+)\s*chunk', text, re.IGNORECASE)
    phase_match     = re.search(r'\*\*Phase:\*\*\s+(.+)', text)

    return {
        "context_generated_at": generated_match.group(1).strip() if generated_match else None,
        "chroma_chunks":        int(chunks_match.group(1).replace(",", "")) if chunks_match else None,
        "faithh_phase":         phase_match.group(1).strip() if phase_match else None,
    }


def extract_live_state(path: Path) -> dict:
    if not path.exists():
        return {"_file_missing": True}
    try:
        data = json.loads(path.read_text())
    except Exception:
        return {"_parse_error": True}
    chroma = data.get("chroma", {})
    return {
        "chroma_chunks":     chroma.get("chunk_count"),
        "chroma_collection": chroma.get("collection"),
        "live_reachable":    chroma.get("reachable"),
        "collected_at":      data.get("collected_at"),
    }


# ── Comparison Engine ────────────────────────────────────────────────────────

# Facts to compare across multiple sources
# Format: { fact_key: [list of (source_name, extractor_key)] }
COMPARISONS = {
    "ChromaDB chunk count": [
        ("live_state",      "chroma_chunks"),
        ("project_states",  "chroma_chunks"),
        ("faithh_memory",   "chroma_chunks"),
        ("readme",          "chroma_chunks"),
        ("systems_map",     "chroma_chunks"),
        ("context_md",      "chroma_chunks"),
    ],
    "ChromaDB collection name": [
        ("project_states",  "chroma_collection"),
        ("faithh_memory",   "chroma_collection"),
        ("systems_map",     "chroma_collection"),
    ],
    "Embedding model": [
        ("project_states",  "embedding_model"),
        ("faithh_memory",   "embedding_model"),
        ("systems_map",     "embedding_model"),
    ],
    "FAITHH phase": [
        ("project_states",  "faithh_phase"),
        ("context_md",      "faithh_phase"),
    ],
    "Backend URL/port": [
        ("project_states",  "backend_url"),
        ("readme",          "backend_port"),
    ],
}


def normalize(value):
    """Normalize values for loose comparison."""
    if value is None:
        return None
    v = str(value).lower().strip()
    # Normalize chunk counts: 32499 == 32,499
    v = v.replace(",", "")
    # Normalize phase strings loosely
    v = re.sub(r'\s+', ' ', v)
    return v


def run_checks(extracted: dict) -> list:
    results = []

    for fact_label, sources in COMPARISONS.items():
        values = {}
        for (source_name, key) in sources:
            source_data = extracted.get(source_name, {})
            if source_data.get("_file_missing") or source_data.get("_parse_error"):
                values[source_name] = "__FILE_MISSING__"
            else:
                values[source_name] = source_data.get(key)

        present = {k: v for k, v in values.items() if v is not None and v != "__FILE_MISSING__"}
        missing = {k: v for k, v in values.items() if v is None}
        file_missing = {k for k, v in values.items() if v == "__FILE_MISSING__"}

        normalized_vals = set(normalize(v) for v in present.values())

        if len(normalized_vals) <= 1 and not missing and not file_missing:
            status = "PASS"
        elif len(normalized_vals) > 1:
            status = "MISMATCH"
        elif missing or file_missing:
            status = "WARN"
        else:
            status = "PASS"

        results.append({
            "fact":         fact_label,
            "status":       status,
            "values":       values,
            "present":      present,
            "missing":      list(missing.keys()),
            "file_missing": list(file_missing),
        })

    return results


# ── Fix Hints ────────────────────────────────────────────────────────────────

FIX_HINTS = {
    "ChromaDB chunk count": (
        "Run: curl http://192.158.1.10:8000/api/v2/collections/faithh_knowledge_base\n"
        "Then update faithh_memory.json → chromadb.documents and project_states.json → FAITHH.infrastructure.chunks_indexed\n"
        "Then re-run: python scripts/generate_context.py"
    ),
    "ChromaDB collection name": (
        "Verify collection name with ChromaDB API, then update faithh_memory.json and project_states.json to match."
    ),
    "Embedding model": (
        "The embedding model in faithh_memory.json is likely stale.\n"
        "Check project_states.json (reindex date Jan 25 2026 → all-MiniLM-L6-v2 384-dim is correct).\n"
        "Update faithh_memory.json to match. Then verify chips were regenerated with same model."
    ),
    "FAITHH phase": (
        "Update project_states.json.projects.FAITHH.phase to match scaffolding_state.json.active_context.structural_position\n"
        "Then re-run: python scripts/generate_context.py"
    ),
    "Backend URL/port": (
        "Verify backend is running on :5557 (curl http://localhost:5557/health)\n"
        "Update README.md if port changed."
    ),
}


# ── Reporting ─────────────────────────────────────────────────────────────────

COLORS = {
    "PASS":     "\033[92m",  # green
    "WARN":     "\033[93m",  # yellow
    "MISMATCH": "\033[91m",  # red
    "RESET":    "\033[0m",
}

def color(text, status):
    return f"{COLORS.get(status, '')}{text}{COLORS['RESET']}"


def print_report(results: list, show_fix_hints: bool = False):
    print("\n" + "="*60)
    print("  FAITHH Consistency Checker")
    print(f"  Run at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("="*60 + "\n")

    passes   = [r for r in results if r["status"] == "PASS"]
    warns    = [r for r in results if r["status"] == "WARN"]
    mismatches = [r for r in results if r["status"] == "MISMATCH"]

    # Summary line
    print(f"  {color(f'{len(passes)} PASS', 'PASS')}  |  "
          f"{color(f'{len(warns)} WARN', 'WARN')}  |  "
          f"{color(f'{len(mismatches)} MISMATCH', 'MISMATCH')}\n")

    if mismatches:
        print(color("── MISMATCHES (fix these) ──────────────────────────────", "MISMATCH"))
        for r in mismatches:
            print(f"\n  {color('MISMATCH', 'MISMATCH')}  {r['fact']}")
            for source, val in r["values"].items():
                print(f"    {source:<20} → {val}")
            if show_fix_hints and r["fact"] in FIX_HINTS:
                print(f"\n    {color('HOW TO FIX:', 'WARN')}")
                for line in FIX_HINTS[r["fact"]].split("\n"):
                    print(f"      {line}")

    if warns:
        print(color("\n── WARNINGS (missing from some sources) ───────────────", "WARN"))
        for r in warns:
            print(f"\n  {color('WARN', 'WARN')}  {r['fact']}")
            for source in r["missing"]:
                print(f"    {source:<20} → (not tracked)")
            for source in r["file_missing"]:
                print(f"    {source:<20} → FILE MISSING")

    if passes:
        print(color("\n── PASSING ─────────────────────────────────────────────", "PASS"))
        for r in passes:
            val = next(iter(r["present"].values()), "—")
            print(f"  {color('PASS', 'PASS')}  {r['fact']:<35} {val}")

    print("\n" + "="*60)

    # Exit code for CI/cron use
    if mismatches:
        sys.exit(1)
    sys.exit(0)


def print_json_report(results: list):
    output = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "pass":     sum(1 for r in results if r["status"] == "PASS"),
            "warn":     sum(1 for r in results if r["status"] == "WARN"),
            "mismatch": sum(1 for r in results if r["status"] == "MISMATCH"),
        },
        "results": results,
    }
    print(json.dumps(output, indent=2))
    if any(r["status"] == "MISMATCH" for r in results):
        sys.exit(1)
    sys.exit(0)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="FAITHH Consistency Checker")
    parser.add_argument("--json",       action="store_true", help="Output JSON (for Prometheus/Grafana)")
    parser.add_argument("--fix-hints",  action="store_true", help="Show fix instructions for mismatches")
    args = parser.parse_args()

    # Extract facts from all sources
    extracted = {
        "project_states": extract_project_states(STATE_FILES["project_states"]),
        "scaffolding":    extract_scaffolding(STATE_FILES["scaffolding"]),
        "faithh_memory":  extract_faithh_memory(STATE_FILES["faithh_memory"]),
        "readme":         extract_readme(STATE_FILES["readme"]),
        "systems_map":    extract_systems_map(STATE_FILES["systems_map"]),
        "context_md":     extract_context_md(STATE_FILES["context_md"]),
        "live_state":     extract_live_state(STATE_FILES["live_state"]),
    }

    results = run_checks(extracted)

    if args.json:
        print_json_report(results)
    else:
        print_report(results, show_fix_hints=args.fix_hints)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
FAITHH PULSE Reflection Engine — Tier 1: Staleness Detector
=============================================================
Scans active documentation, state files, and decisions log to detect:
  1. Stale documents (low similarity to recent conversations)
  2. Broken references (docs pointing to moved/deleted files)
  3. Contradictions (decisions vs current state)
  4. Forgotten open loops (scaffolding items with no recent activity)

Runs on CPU (no GPU needed). Takes ~2-5 minutes for full sweep.

Usage:
    python scripts/staleness_detector.py                # Full sweep
    python scripts/staleness_detector.py --quick         # Docs only (fastest)
    python scripts/staleness_detector.py --json          # Machine-readable output
    python scripts/staleness_detector.py --output report # Save to ml/output/staleness_report.md

Output: Staleness report with scores and recommendations.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# No GPU needed for Tier 1
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np

BASE_DIR = Path(__file__).parent.parent
CHROMA_HOST = os.environ.get("CHROMA_HOST", "192.158.1.243")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))
COLLECTION_NAME = "faithh_knowledge_base"

# Thresholds (tunable)
STALENESS_DAYS_WARNING = 30       # Warn if not modified in 30 days
STALENESS_DAYS_CRITICAL = 90      # Critical if not modified in 90 days
SIMILARITY_THRESHOLD_LOW = 0.25   # Below this = doc is disconnected from recent activity
SIMILARITY_THRESHOLD_MED = 0.40   # Below this = doc may be drifting

# Active docs to scan (mirrors reindex_project_docs.py structure)
ACTIVE_DOC_DIRS = [
    "docs/architecture",
    "docs/guides",
    "docs/reference",
    "docs/business",
    "docs/research",
    "docs/roadmaps",
]

ROOT_DOCS = [
    "AGENTS.md",
    "README.md",
    "CONTEXT.md",
    "SYSTEMS_MAP.md",
    "docs/README.md",
]

STATE_FILES = [
    "faithh_memory.json",
    "decisions_log.json",
    "project_states.json",
    "scaffolding_state.json",
    "config.yaml",
]


def get_git_last_modified(filepath: str) -> datetime | None:
    """Get last git commit date for a file."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", filepath],
            capture_output=True, text=True, cwd=BASE_DIR, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            date_str = result.stdout.strip()
            # Parse ISO format, handle timezone
            return datetime.fromisoformat(date_str.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        pass
    return None


def get_file_modified(filepath: str) -> datetime | None:
    """Get filesystem modification time."""
    full_path = BASE_DIR / filepath
    if full_path.exists():
        return datetime.fromtimestamp(full_path.stat().st_mtime)
    return None


def discover_active_docs() -> list[str]:
    """Find all active documentation files."""
    docs = list(ROOT_DOCS)
    for scan_dir in ACTIVE_DOC_DIRS:
        dpath = BASE_DIR / scan_dir
        if dpath.exists():
            for f in sorted(dpath.rglob("*.md")):
                rel = str(f.relative_to(BASE_DIR))
                if rel not in docs:
                    docs.append(rel)
    return docs


def check_broken_references(filepath: str) -> list[str]:
    """Check if a doc references files that don't exist."""
    full_path = BASE_DIR / filepath
    if not full_path.exists() or not filepath.endswith(".md"):
        return []

    broken = []
    try:
        content = full_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    # Find file references in markdown
    # Patterns: [text](path), `path/to/file`, docs/something.md
    patterns = [
        r'\[.*?\]\(((?!http)[^)]+)\)',           # Markdown links (non-http)
        r'`((?:docs|scripts|backend|ml|tests)/[^\s`]+)`',  # Backtick paths
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, content):
            ref = match.group(1).strip()
            # Clean up anchors and query strings
            ref = ref.split("#")[0].split("?")[0]
            if not ref or ref.startswith("http"):
                continue

            # Resolve relative to the file's directory or repo root
            candidates = [
                BASE_DIR / ref,
                full_path.parent / ref,
            ]
            if not any(c.exists() for c in candidates):
                broken.append(ref)

    return broken


def get_recent_conversation_embeddings(model: SentenceTransformer, collection, days: int = 30) -> np.ndarray | None:
    """Get embeddings of recent conversation activity from ChromaDB."""
    try:
        # Get recent docs by querying with time filter
        # ChromaDB doesn't have great time filtering, so we'll sample recent docs
        results = collection.get(
            where={"category": {"$eq": "conversation"}},
            limit=500,
            include=["documents"]
        )

        if not results["documents"]:
            # Fall back to any recent docs
            results = collection.get(
                limit=500,
                include=["documents"]
            )

        if not results["documents"]:
            return None

        # Embed a sample of recent documents
        sample_size = min(200, len(results["documents"]))
        sample_indices = np.random.choice(len(results["documents"]), sample_size, replace=False)
        sample_docs = [results["documents"][i] for i in sample_indices]

        embeddings = model.encode(sample_docs, show_progress_bar=False, batch_size=32)
        return embeddings

    except Exception as e:
        print(f"  Warning: Could not get conversation embeddings: {e}")
        return None


def compute_doc_relevance(model: SentenceTransformer, filepath: str, recent_embeddings: np.ndarray) -> float:
    """Compute how relevant a doc is to recent conversations (0.0 = irrelevant, 1.0 = highly relevant)."""
    full_path = BASE_DIR / filepath
    if not full_path.exists():
        return 0.0

    try:
        content = full_path.read_text(encoding="utf-8", errors="replace")
        if len(content) < 50:
            return 0.0

        # Chunk the doc and embed
        chunks = [content[i:i+1500] for i in range(0, min(len(content), 6000), 1500)]
        doc_embeddings = model.encode(chunks, show_progress_bar=False)

        # Compute max cosine similarity between any doc chunk and recent conversations
        # Normalize
        doc_norm = doc_embeddings / (np.linalg.norm(doc_embeddings, axis=1, keepdims=True) + 1e-8)
        recent_norm = recent_embeddings / (np.linalg.norm(recent_embeddings, axis=1, keepdims=True) + 1e-8)

        # Max similarity across all chunk-conversation pairs
        similarities = doc_norm @ recent_norm.T
        max_sim = float(np.max(similarities))
        mean_sim = float(np.mean(np.max(similarities, axis=1)))

        # Blend: weighted toward max but penalized by mean
        return 0.6 * max_sim + 0.4 * mean_sim

    except Exception as e:
        print(f"  Warning: Could not compute relevance for {filepath}: {e}")
        return 0.0


def check_decisions_staleness(decisions_log: dict) -> list[dict]:
    """Check decisions for staleness indicators."""
    issues = []
    now = datetime.now()

    for decision in decisions_log.get("decisions", []):
        d_id = decision.get("id", "unknown")
        d_date = decision.get("date", "")
        d_status = decision.get("status", "")
        d_related = decision.get("related_docs", [])

        # Check age
        try:
            d_dt = datetime.fromisoformat(d_date)
            age_days = (now - d_dt).days
        except (ValueError, TypeError):
            age_days = 999

        # Check if related docs still exist
        broken_refs = []
        for ref in d_related:
            if not (BASE_DIR / ref).exists():
                broken_refs.append(ref)

        if broken_refs:
            issues.append({
                "decision_id": d_id,
                "decision": decision.get("decision", ""),
                "issue": "broken_references",
                "details": f"References missing files: {broken_refs}",
                "severity": "warning",
            })

        # Check if status is "in_progress" for too long
        if d_status == "in_progress" and age_days > 90:
            issues.append({
                "decision_id": d_id,
                "decision": decision.get("decision", ""),
                "issue": "stale_in_progress",
                "details": f"In progress for {age_days} days — still active or forgotten?",
                "severity": "warning",
            })

    return issues


def check_scaffolding_staleness(scaffolding: dict) -> list[dict]:
    """Check scaffolding for forgotten loops and stale state."""
    issues = []
    now = datetime.now()

    # Check meta freshness
    last_updated = scaffolding.get("meta", {}).get("last_updated", "")
    try:
        lu_dt = datetime.fromisoformat(last_updated)
        age_days = (now - lu_dt).days
        if age_days > STALENESS_DAYS_WARNING:
            issues.append({
                "item": "scaffolding_state.json",
                "issue": "stale_meta",
                "details": f"Last updated {age_days} days ago ({last_updated})",
                "severity": "critical" if age_days > STALENESS_DAYS_CRITICAL else "warning",
            })
    except (ValueError, TypeError):
        issues.append({
            "item": "scaffolding_state.json",
            "issue": "invalid_date",
            "details": f"Cannot parse last_updated: {last_updated}",
            "severity": "warning",
        })

    # Check open loops
    for loop in scaffolding.get("open_loops", []):
        loop_id = loop.get("id", "unknown")
        created = loop.get("created", "")
        status = loop.get("status", "")
        blocked = loop.get("blocked_by")

        try:
            c_dt = datetime.fromisoformat(created)
            age_days = (now - c_dt).days
        except (ValueError, TypeError):
            age_days = 999

        if status not in ("done", "completed") and age_days > STALENESS_DAYS_WARNING:
            severity = "critical" if age_days > STALENESS_DAYS_CRITICAL else "warning"
            issues.append({
                "item": f"open_loop:{loop_id}",
                "issue": "stale_open_loop",
                "details": f"Open for {age_days} days, status='{status}'" +
                           (f", blocked by: {blocked}" if blocked else ""),
                "severity": severity,
            })

    # Check parked tangents — not stale per se, but remind about them
    for tangent in scaffolding.get("parked_tangents", []):
        revisit = tangent.get("revisit_when", "")
        issues.append({
            "item": f"parked:{tangent.get('idea', 'unknown')[:50]}",
            "issue": "parked_tangent",
            "details": f"Revisit when: {revisit}",
            "severity": "info",
        })

    return issues


def format_report(doc_results: list[dict], decision_issues: list[dict],
                  scaffolding_issues: list[dict], broken_refs: dict,
                  elapsed: float) -> str:
    """Format the staleness report as markdown."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# FAITHH Staleness Report",
        f"**Generated:** {now}",
        f"**Scan time:** {elapsed:.1f}s",
        f"**Files scanned:** {len(doc_results)}",
        "",
    ]

    # Summary counts
    critical = sum(1 for d in doc_results if d["severity"] == "critical")
    warning = sum(1 for d in doc_results if d["severity"] == "warning")
    ok = sum(1 for d in doc_results if d["severity"] == "ok")

    lines.append(f"## Summary")
    lines.append(f"- **Critical:** {critical} files")
    lines.append(f"- **Warning:** {warning} files")
    lines.append(f"- **OK:** {ok} files")
    lines.append("")

    # Critical & Warning docs
    if critical + warning > 0:
        lines.append("## Stale Documents")
        lines.append("")
        lines.append("| File | Age (days) | Relevance | Severity | Issue |")
        lines.append("|------|-----------|-----------|----------|-------|")
        for d in sorted(doc_results, key=lambda x: x["severity_rank"]):
            if d["severity"] in ("critical", "warning"):
                lines.append(f"| `{d['filepath']}` | {d['age_days']} | {d['relevance']:.2f} | {d['severity']} | {d['issue']} |")
        lines.append("")

    # Broken references
    all_broken = {fp: refs for fp, refs in broken_refs.items() if refs}
    if all_broken:
        lines.append("## Broken References")
        lines.append("")
        for fp, refs in all_broken.items():
            lines.append(f"- `{fp}` → missing: {', '.join(f'`{r}`' for r in refs)}")
        lines.append("")

    # Decision issues
    if decision_issues:
        lines.append("## Decision Log Issues")
        lines.append("")
        for issue in decision_issues:
            lines.append(f"- **{issue['decision_id']}** ({issue['severity']}): {issue['details']}")
            lines.append(f"  Decision: *{issue['decision']}*")
        lines.append("")

    # Scaffolding issues
    if scaffolding_issues:
        lines.append("## Scaffolding Issues")
        lines.append("")
        for issue in scaffolding_issues:
            icon = "🔴" if issue["severity"] == "critical" else "🟡" if issue["severity"] == "warning" else "ℹ️"
            lines.append(f"- {icon} **{issue['item']}** ({issue['issue']}): {issue['details']}")
        lines.append("")

    # OK docs (brief)
    if ok > 0:
        lines.append("## Healthy Documents")
        lines.append("")
        for d in doc_results:
            if d["severity"] == "ok":
                lines.append(f"- `{d['filepath']}` (age: {d['age_days']}d, relevance: {d['relevance']:.2f})")
        lines.append("")

    lines.append("---")
    lines.append("*Generated by FAITHH PULSE Reflection Engine — Tier 1 Staleness Detector*")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="FAITHH Staleness Detector (Tier 1)")
    parser.add_argument("--quick", action="store_true",
                        help="Skip conversation embedding comparison (faster)")
    parser.add_argument("--json", action="store_true",
                        help="Output machine-readable JSON")
    parser.add_argument("--output", type=str, default=None,
                        help="Save report to ml/output/<name>.md")
    args = parser.parse_args()

    start = time.time()
    print("=" * 60)
    print("FAITHH PULSE Reflection Engine — Tier 1: Staleness Detector")
    print("=" * 60)

    # 1. Discover active docs
    print("\n[1/5] Discovering active documents...")
    active_docs = discover_active_docs()
    print(f"  Found {len(active_docs)} active documents")

    # 2. Load embedding model (CPU)
    print("\n[2/5] Loading embedding model (CPU)...")
    model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    print("  Model loaded: all-MiniLM-L6-v2 (384-dim)")

    # 3. Get recent conversation embeddings from ChromaDB
    recent_embeddings = None
    if not args.quick:
        print("\n[3/5] Fetching recent conversation context from ChromaDB...")
        try:
            client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
            collection = client.get_collection(COLLECTION_NAME)
            doc_count = collection.count()
            print(f"  Collection: {COLLECTION_NAME} ({doc_count:,} docs)")
            recent_embeddings = get_recent_conversation_embeddings(model, collection)
            if recent_embeddings is not None:
                print(f"  Sampled {len(recent_embeddings)} conversation chunks for comparison")
            else:
                print("  Warning: No conversation chunks found, skipping relevance scoring")
        except Exception as e:
            print(f"  Warning: ChromaDB unavailable ({e}), skipping relevance scoring")
    else:
        print("\n[3/5] Skipping conversation comparison (--quick mode)")

    # 4. Analyze each document
    print("\n[4/5] Analyzing documents...")
    doc_results = []
    broken_refs_map = {}
    now = datetime.now()

    for filepath in active_docs + STATE_FILES:
        full_path = BASE_DIR / filepath
        if not full_path.exists():
            doc_results.append({
                "filepath": filepath,
                "age_days": -1,
                "relevance": 0.0,
                "severity": "critical",
                "severity_rank": 0,
                "issue": "FILE MISSING",
            })
            continue

        # Get age
        git_date = get_git_last_modified(filepath)
        fs_date = get_file_modified(filepath)
        mod_date = git_date or fs_date
        age_days = (now - mod_date).days if mod_date else 999

        # Get relevance score
        relevance = 0.5  # Default if no embedding comparison
        if recent_embeddings is not None and filepath.endswith(".md"):
            relevance = compute_doc_relevance(model, filepath, recent_embeddings)

        # Check broken references
        broken = check_broken_references(filepath)
        if broken:
            broken_refs_map[filepath] = broken

        # Determine severity
        if age_days > STALENESS_DAYS_CRITICAL and relevance < SIMILARITY_THRESHOLD_LOW:
            severity = "critical"
            issue = f"Very stale ({age_days}d) + low relevance ({relevance:.2f})"
            severity_rank = 0
        elif age_days > STALENESS_DAYS_CRITICAL:
            severity = "warning"
            issue = f"Stale ({age_days}d) but still somewhat relevant ({relevance:.2f})"
            severity_rank = 1
        elif relevance < SIMILARITY_THRESHOLD_LOW and recent_embeddings is not None:
            severity = "warning"
            issue = f"Low relevance ({relevance:.2f}) — may be disconnected from current work"
            severity_rank = 1
        elif age_days > STALENESS_DAYS_WARNING:
            severity = "warning"
            issue = f"Getting stale ({age_days}d)"
            severity_rank = 2
        else:
            severity = "ok"
            issue = "Current"
            severity_rank = 3

        doc_results.append({
            "filepath": filepath,
            "age_days": age_days,
            "relevance": round(relevance, 3),
            "severity": severity,
            "severity_rank": severity_rank,
            "issue": issue,
        })
        print(f"  {'🔴' if severity == 'critical' else '🟡' if severity == 'warning' else '✅'} {filepath} "
              f"(age: {age_days}d, rel: {relevance:.2f})")

    # 5. Check decisions and scaffolding
    print("\n[5/5] Checking decisions log and scaffolding state...")
    decision_issues = []
    scaffolding_issues = []

    decisions_path = BASE_DIR / "decisions_log.json"
    if decisions_path.exists():
        with open(decisions_path) as f:
            decisions_data = json.load(f)
        decision_issues = check_decisions_staleness(decisions_data)
        print(f"  Decisions: {len(decision_issues)} issues found")

    scaffolding_path = BASE_DIR / "scaffolding_state.json"
    if scaffolding_path.exists():
        with open(scaffolding_path) as f:
            scaffolding_data = json.load(f)
        scaffolding_issues = check_scaffolding_staleness(scaffolding_data)
        print(f"  Scaffolding: {len(scaffolding_issues)} issues found")

    elapsed = time.time() - start

    # Output
    if args.json:
        output = {
            "generated": now.isoformat(),
            "scan_time_seconds": round(elapsed, 1),
            "documents": doc_results,
            "broken_references": broken_refs_map,
            "decision_issues": decision_issues,
            "scaffolding_issues": scaffolding_issues,
        }
        print(json.dumps(output, indent=2))
    else:
        report = format_report(doc_results, decision_issues, scaffolding_issues,
                               broken_refs_map, elapsed)
        print(f"\n{'=' * 60}")
        print(report)

        if args.output:
            output_path = BASE_DIR / "ml" / "output" / f"{args.output}.md"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report)
            print(f"\nReport saved to: {output_path}")

    # Summary
    critical = sum(1 for d in doc_results if d["severity"] == "critical")
    warning = sum(1 for d in doc_results if d["severity"] == "warning")
    print(f"\n{'=' * 60}")
    print(f"Scan complete in {elapsed:.1f}s")
    print(f"  {critical} critical, {warning} warnings, {len(doc_results) - critical - warning} ok")
    if decision_issues:
        print(f"  {len(decision_issues)} decision log issues")
    if scaffolding_issues:
        print(f"  {len(scaffolding_issues)} scaffolding issues")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()

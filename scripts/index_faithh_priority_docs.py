#!/usr/bin/env python3
"""
Index Priority-1 FAITHH stack prose into HTTP Chroma (faithh_knowledge_base).

Uses scripts/indexing/index_faithh_kb_markdown.py per file so embeddings match the
collection default. Skips missing paths. For broad corpus + HTTP Chroma, prefer this
over scripts/indexing/index_documents_chromadb.py (local PersistentClient + Ollama embed).

Environment: CHROMA_HOST, CHROMA_PORT, CHROMA_COLLECTION (collection flag passed through).

Examples:
  venv/bin/python scripts/index_faithh_priority_docs.py
  venv/bin/python scripts/index_faithh_priority_docs.py --dry-run
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INDEXER = REPO_ROOT / "scripts" / "indexing" / "index_faithh_kb_markdown.py"

# Repo-relative paths; optional files are skipped with a message.
PRIORITY_1_PATHS: tuple[str, ...] = (
    "docs/RELEVANCY_REPORT.md",
    "docs/WORKSPACE_UNIFICATION_PLAN.md",
    "docs/architecture/BACKEND_API.md",
    "docs/architecture/ECOSYSTEM_METRICS.md",
    "docs/architecture/HARMONIC_ARCHITECTURE_BRIDGE.md",
    "docs/research/harmonic_body/HARMONIC_BODY.md",
    "docs/DATABASE_MAP_2026-04-10.md",
    "AGENTS.md",
    "README.md",
    ".env.example",
)


def main() -> int:
    ap = argparse.ArgumentParser(description="Index FAITHH Priority-1 docs into Chroma KB.")
    ap.add_argument("--dry-run", action="store_true", help="Print commands only")
    ap.add_argument("--force", action="store_true", help="Pass --force to indexer (bulk guard)")
    ap.add_argument(
        "--collection",
        default="faithh_knowledge_base",
        help="Chroma collection name",
    )
    args = ap.parse_args()

    if not INDEXER.is_file():
        print(f"Missing indexer: {INDEXER}", file=sys.stderr)
        return 1

    ok = 0
    skipped = 0
    for rel in PRIORITY_1_PATHS:
        path = REPO_ROOT / rel
        if not path.is_file():
            print(f"skip (missing): {rel}")
            skipped += 1
            continue
        cmd = [
            sys.executable,
            str(INDEXER),
            "--file",
            str(path.relative_to(REPO_ROOT)),
            "--domain",
            "faithh",
            "--category",
            "documentation",
            "--document-type",
            "knowledge_base",
            "--collection",
            args.collection,
        ]
        if args.force:
            cmd.append("--force")
        print(f"→ {' '.join(cmd)}")
        if args.dry_run:
            ok += 1
            continue
        r = subprocess.run(cmd, cwd=str(REPO_ROOT))
        if r.returncode != 0:
            print(f"FAILED: {rel} (exit {r.returncode})", file=sys.stderr)
            return r.returncode
        ok += 1

    print(f"Done: indexed {ok} path(s), skipped {skipped} missing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

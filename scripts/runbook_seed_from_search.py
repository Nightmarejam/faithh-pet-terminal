#!/usr/bin/env python3
"""Seed RunBook draft ideas from semantic search in ChromaDB."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, UTC
from pathlib import Path

import chromadb
from chromadb.config import Settings

from runbook_seed_core import (
    build_seed,
    query_collections,
    validate_seed,
    write_seed_outputs,
)


REPO_ROOT = Path("/home/jonat/ai-stack")
DEFAULT_OUTPUT_DIR = REPO_ROOT / "reports" / "runbook_seeds"
DEFAULT_COLLECTIONS = ("faithh_knowledge_base", "alife_lineage")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed runbook drafts from semantic search")
    parser.add_argument("--query", required=True, help="Topic/query to seed runbook ideas")
    parser.add_argument("--max-chunks", type=int, default=8, help="Max evidence chunks to include")
    parser.add_argument(
        "--collections",
        default=",".join(DEFAULT_COLLECTIONS),
        help="Comma-separated Chroma collections to query",
    )
    parser.add_argument("--host", default="192.158.1.10")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--output-prefix", default="runbook_seed")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    collections = [c.strip() for c in args.collections.split(",") if c.strip()]
    max_chunks = max(1, args.max_chunks)

    client = chromadb.HttpClient(
        host=args.host,
        port=args.port,
        settings=Settings(anonymized_telemetry=False),
    )
    evidence = query_collections(client, args.query, collections, max_chunks)
    if not evidence:
        raise SystemExit("No evidence returned from configured collections.")

    seed = build_seed(args.query, evidence)
    validation = validate_seed(seed)
    json_path = output_dir / f"{args.output_prefix}_{stamp}.json"
    md_path = output_dir / f"{args.output_prefix}_{stamp}.md"

    write_seed_outputs(seed, json_path, md_path)

    print(f"seed_json: {json_path}")
    print(f"seed_markdown: {md_path}")
    print(f"validation_ok: {validation['required_fields_ok'] and validation['source_evidence_non_empty'] and validation['step_count_ok']}")
    if validation["issues"]:
        print("validation_issues:")
        for issue in validation["issues"]:
            print(f"- {issue}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

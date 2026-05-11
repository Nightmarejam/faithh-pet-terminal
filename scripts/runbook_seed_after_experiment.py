#!/usr/bin/env python3
"""Optional post-experiment wrapper for runbook seed generation."""

from __future__ import annotations

import argparse
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


def infer_query_from_report(report_path: Path) -> str:
    try:
        import json

        data = json.loads(report_path.read_text(encoding="utf-8"))
        experiment = data.get("experiment", "experiment")
        generation = data.get("generation", "unknown")
        return f"{experiment} generation {generation} runbook"
    except Exception:
        return f"{report_path.stem.replace('_', ' ')} runbook"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Post-experiment runbook seed wrapper")
    parser.add_argument("--enable", action="store_true", help="Required to execute synthesis")
    parser.add_argument("--report", default="", help="Path to experiment report JSON")
    parser.add_argument("--query", default="", help="Explicit query override")
    parser.add_argument("--max-chunks", type=int, default=8)
    parser.add_argument("--collections", default="faithh_knowledge_base,alife_lineage")
    parser.add_argument("--host", default="192.158.1.243")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--output-prefix", default="runbook_seed_post")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.enable:
        print("Post-experiment synthesis is disabled by default. Re-run with --enable.")
        return 0

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    collections = [c.strip() for c in args.collections.split(",") if c.strip()]
    max_chunks = max(1, args.max_chunks)

    report_path = Path(args.report) if args.report else None
    if args.query.strip():
        query = args.query.strip()
    elif report_path and report_path.exists():
        query = infer_query_from_report(report_path)
    else:
        query = "experiment execution runbook"

    client = chromadb.HttpClient(
        host=args.host,
        port=args.port,
        settings=Settings(anonymized_telemetry=False),
    )
    evidence = query_collections(client, query, collections, max_chunks)
    if not evidence:
        raise SystemExit("No evidence returned from configured collections.")

    seed = build_seed(query, evidence)
    validation = validate_seed(seed)
    json_path = output_dir / f"{args.output_prefix}_{stamp}.json"
    md_path = output_dir / f"{args.output_prefix}_{stamp}.md"
    write_seed_outputs(seed, json_path, md_path)

    print(f"seed_json: {json_path}")
    print(f"seed_markdown: {md_path}")
    print(
        "validation_ok: "
        f"{validation['required_fields_ok'] and validation['source_evidence_non_empty'] and validation['step_count_ok']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

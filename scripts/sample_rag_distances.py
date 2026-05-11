#!/usr/bin/env python3
"""
Sample Chroma cosine distances for representative queries (RAG threshold calibration).

Uses the same CHROMA_HOST / CHROMA_PORT / CHROMA_COLLECTION as the FAITHH backend.
Compare printed "Best" values to RAG_MAX_DISTANCE_CONFIDENT in .env.

Examples:
  python scripts/sample_rag_distances.py
  python scripts/sample_rag_distances.py --n-results 5
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import chromadb
from chromadb.config import Settings

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_repo_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    p = REPO_ROOT / ".env"
    if p.is_file():
        load_dotenv(p, override=False)


def _parse_host_port() -> tuple[str, int]:
    raw = (os.environ.get("CHROMA_HOST") or "").strip() or "localhost"
    port = int(os.environ.get("CHROMA_PORT", "8000"))
    if raw.startswith("http://") or raw.startswith("https://"):
        u = urlparse(raw)
        return (u.hostname or "localhost"), int(os.environ.get("CHROMA_PORT", u.port or port))
    if ":" in raw and raw.count(":") == 1:
        h, _, p = raw.partition(":")
        try:
            return h, int(p)
        except ValueError:
            return raw, port
    return raw, port


DEFAULT_QUERIES = [
    "what services are active in the workspace",
    "RAG signal quality and distance threshold",
    "session metrics layer implementation",
    "FAITHH backend Flask routes",
    "ChromaDB collection structure",
    "Ollama KV cache configuration",
    "harmonic body architecture",
    "ALIFE simulation feedback loop",
]


def main() -> int:
    _load_repo_dotenv()
    ap = argparse.ArgumentParser(description="Print RAG distance samples for calibration.")
    ap.add_argument("--collection", default=os.environ.get("CHROMA_COLLECTION", "faithh_knowledge_base"))
    ap.add_argument("--n-results", type=int, default=3, help="Hits per query (default 3).")
    args = ap.parse_args()

    host, port = _parse_host_port()
    timeout_s = int(os.environ.get("CHROMA_MAINT_REQUEST_TIMEOUT_S", "120"))
    settings = Settings(
        anonymized_telemetry=False,
        chroma_query_request_timeout_seconds=timeout_s,
        chroma_sysdb_request_timeout_seconds=max(timeout_s, 60),
    )
    client = chromadb.HttpClient(host=host, port=port, settings=settings)
    col = client.get_collection(name=args.collection)
    total = col.count()
    thresh = float(os.environ.get("RAG_MAX_DISTANCE_CONFIDENT", "0.55"))

    print(f"Host: {host}:{port}  Collection: {args.collection}  count={total:,}")
    print(f"RAG_MAX_DISTANCE_CONFIDENT (env): {thresh}")
    print()

    bests: list[float] = []
    for q in DEFAULT_QUERIES:
        try:
            result = col.query(
                query_texts=[q],
                n_results=min(args.n_results, max(1, total)),
                include=["distances", "metadatas"],
            )
            distances = result["distances"][0] if result.get("distances") else []
            metas = result["metadatas"][0] if result.get("metadatas") else []
            domains = [str((m or {}).get("domain") or "UNKNOWN") for m in metas]
            print(f"Query: {q[:56]}")
            if not distances:
                print("  (no distances)")
                print()
                continue
            rounded = [round(float(d), 4) for d in distances]
            best = min(float(d) for d in distances)
            bests.append(best)
            print(f"  Distances: {rounded}")
            print(f"  Domains: {domains}")
            print(f"  Best: {round(best, 4)}  low_confidence={best > thresh}")
            print()
        except Exception as e:
            print(f"Query: {q[:56]}")
            print(f"  ERROR: {e}")
            print()

    if bests:
        bests_sorted = sorted(bests)
        p75 = bests_sorted[int(0.75 * (len(bests_sorted) - 1))]
        print(
            "Summary: best-per-query min/median/p75/max =",
            f"{min(bests):.4f} / {bests_sorted[len(bests_sorted)//2]:.4f} / {p75:.4f} / {max(bests):.4f}",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

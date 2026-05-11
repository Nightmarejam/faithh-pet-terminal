#!/usr/bin/env python3
"""
Validate governance/ALife/Constella retrieval quality and source-mix drift.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, UTC
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


QUERY_CLASSES = {
    "governance_principle": [
        "What is the Universal Civic Floor?",
        "How should constitutional governance handle minimum compliance participants?",
        "What governance mechanism maps to Penumbra in Constella?",
    ],
    "alife_mechanism": [
        "What did Exp 9 show about diversity floor stability?",
        "How does strategy escape work in ALife experiments?",
        "What founding diversity effects were observed in Exp 8b?",
    ],
    "constella_constitutional": [
        "Map ALife evidence to Constella constitutional principles.",
        "Which principles are simulation-derived versus externally sourced?",
        "How do governance concept links feed Constella mechanisms?",
    ],
}


def query_topk(collection, embedder, text: str, k: int):
    emb = embedder.encode([text], show_progress_bar=False).tolist()
    res = collection.query(
        query_embeddings=emb,
        n_results=k,
        include=["metadatas", "documents", "distances"],
    )
    return res


def summarize_mix(results: list[dict]) -> dict:
    source_counts = Counter()
    domain_counts = Counter()
    doc_type_counts = Counter()
    for meta in results:
        if not meta:
            continue
        source_counts[meta.get("source_type", "no_source_type")] += 1
        domain_counts[meta.get("domain", "no_domain")] += 1
        doc_type_counts[meta.get("document_type", "no_document_type")] += 1
    return {
        "source_type_mix": dict(source_counts),
        "domain_mix": dict(domain_counts),
        "document_type_mix": dict(doc_type_counts),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate data aggregation retrieval pipeline")
    parser.add_argument("--host", default="192.158.1.243")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--collection", default="faithh_knowledge_base")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--baseline",
        default="",
        help="Optional previous validation JSON report to compare drift against",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional output path; default reports/index_runs/validation_<timestamp>.json",
    )
    args = parser.parse_args()

    client = chromadb.HttpClient(host=args.host, port=args.port)
    col = client.get_collection(args.collection)
    embedder = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

    run = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "collection": args.collection,
        "top_k": args.top_k,
        "query_classes": {},
    }

    for class_name, queries in QUERY_CLASSES.items():
        per_query = []
        merged_metas = []
        for q in queries:
            res = query_topk(col, embedder, q, args.top_k)
            metas = (res.get("metadatas") or [[]])[0]
            dists = (res.get("distances") or [[]])[0]
            docs = (res.get("documents") or [[]])[0]
            merged_metas.extend(metas)
            per_query.append(
                {
                    "query": q,
                    "result_count": len(docs),
                    "top_distance": dists[0] if dists else None,
                    "source_types_topk": [m.get("source_type", "no_source_type") if m else "none" for m in metas],
                    "domains_topk": [m.get("domain", "no_domain") if m else "none" for m in metas],
                }
            )
        run["query_classes"][class_name] = {
            "queries": per_query,
            "aggregate_mix": summarize_mix(merged_metas),
        }

    # Optional drift comparison to previous run
    if args.baseline:
        baseline_path = Path(args.baseline)
        if baseline_path.exists():
            baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
            drift = {}
            for cls, data in run["query_classes"].items():
                now_mix = data["aggregate_mix"]["source_type_mix"]
                base_mix = (
                    baseline.get("query_classes", {})
                    .get(cls, {})
                    .get("aggregate_mix", {})
                    .get("source_type_mix", {})
                )
                keys = set(now_mix) | set(base_mix)
                drift[cls] = {k: now_mix.get(k, 0) - base_mix.get(k, 0) for k in sorted(keys)}
            run["source_mix_drift_vs_baseline"] = drift

    out_path = (
        Path(args.output)
        if args.output
        else Path(
            f"/home/jonat/ai-stack/reports/index_runs/validation_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json"
        )
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(run, indent=2), encoding="utf-8")
    print(f"Validation report: {out_path}")
    for cls, data in run["query_classes"].items():
        print(f"{cls}: {data['aggregate_mix']['source_type_mix']}")


if __name__ == "__main__":
    main()

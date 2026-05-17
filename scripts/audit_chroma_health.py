#!/usr/bin/env python3
"""
Quick ChromaDB health and indexing integrity audit.

Usage:
  python3 scripts/audit_chroma_health.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

import chromadb


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit ChromaDB collection health")
    parser.add_argument("--host", default="192.158.1.10")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--collection", default="faithh_knowledge_base")
    parser.add_argument("--top", type=int, default=20, help="Top N rows to print")
    args = parser.parse_args()

    repo_root = Path("/home/jonat/ai-stack")
    scripts_dir = repo_root / "scripts"

    client = chromadb.HttpClient(host=args.host, port=args.port)
    collection = client.get_collection(args.collection)

    total = collection.count()
    result = collection.get(limit=total, include=["metadatas"])

    domains: dict[str, int] = {}
    source_types: dict[str, int] = {}
    doc_types: dict[str, int] = {}

    for metadata in result["metadatas"]:
        if not metadata:
            continue
        domain = metadata.get("domain", "no_domain")
        source = metadata.get("source_type", "no_source_type")
        doc_type = metadata.get("document_type", "no_document_type")
        domains[domain] = domains.get(domain, 0) + 1
        source_types[source] = source_types.get(source, 0) + 1
        doc_types[doc_type] = doc_types.get(doc_type, 0) + 1

    print(f"Collection: {args.collection}")
    print(f"Total documents: {total}")
    print()

    print("Top domains:")
    for key, value in sorted(domains.items(), key=lambda x: -x[1])[: args.top]:
        print(f"  {key}: {value}")
    print()

    print("Top source_types:")
    for key, value in sorted(source_types.items(), key=lambda x: -x[1])[: args.top]:
        print(f"  {key}: {value}")
    print()

    print("Top document_types:")
    for key, value in sorted(doc_types.items(), key=lambda x: -x[1])[: args.top]:
        print(f"  {key}: {value}")
    print()

    # Fast checks for critical buckets
    limit = max(total, 1)
    critical_checks = {
        "alife": {"domain": "alife"},
        "alife_experiment": {
            "$and": [
                {"domain": {"$eq": "alife"}},
                {"source_type": {"$eq": "alife_experiment"}},
            ]
        },
        "constella_constitutional": {"domain": "constella_constitutional"},
        "faithh_core": {"domain": "faithh_core"},
    }

    print("Critical checks:")
    for label, where in critical_checks.items():
        count = len(collection.get(where=where, limit=limit, include=[])["ids"])
        print(f"  {label}: {count}")
    print()

    # Script integrity checks
    stale_scripts = [
        "index_chromadb_direct.py",
        "index_to_chromadb.py",
    ]
    present_stale = [name for name in stale_scripts if (scripts_dir / name).exists()]
    if present_stale:
        print("Stale scripts still present:")
        for name in present_stale:
            print(f"  - {name}")
    else:
        print("Stale scripts removed: OK")


if __name__ == "__main__":
    main()

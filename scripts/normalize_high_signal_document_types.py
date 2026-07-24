#!/usr/bin/env python3
"""
Normalize missing document_type metadata for high-signal domains.

Scope intentionally limited to:
- domain=alife
- domain=constella_constitutional
- domain=faithh_core

Usage:
  python3 scripts/normalize_high_signal_document_types.py
"""

from __future__ import annotations

import argparse
from datetime import datetime, UTC

import chromadb


def infer_document_type(source_type: str, doc_id: str) -> str:
    """Infer a stable document_type from source_type and id hints."""
    source = (source_type or "").strip()
    did = (doc_id or "").lower()

    if source == "alife_experiment":
        return "experiment_result"
    if source == "synthesis_document":
        if "overview" in did:
            return "overview"
        if "pattern" in did:
            return "pattern"
        return "finding"
    if source == "alife_cross_experiment_pattern":
        return "pattern"
    if source == "constella_doc":
        return "framework_doc"
    if source == "claude_memory":
        return "memory"
    if source == "project_state":
        return "state_snapshot"
    return "document"


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize high-signal document_type metadata")
    parser.add_argument("--host", default="servicebox.taileb8c60.ts.net")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--collection", default="faithh_knowledge_base")
    args = parser.parse_args()

    client = chromadb.HttpClient(host=args.host, port=args.port)
    collection = client.get_collection(args.collection)

    total = collection.count()
    data = collection.get(limit=total, include=["metadatas", "documents"])

    target_domains = {"alife", "constella_constitutional", "faithh_core"}
    updated_ids: list[str] = []
    updated_metas: list[dict] = []
    updated_docs: list[str] = []

    now_iso = datetime.now(UTC).isoformat()

    for doc_id, meta, document in zip(data["ids"], data["metadatas"], data["documents"]):
        if not meta:
            continue
        domain = meta.get("domain")
        if domain not in target_domains:
            continue
        if meta.get("document_type"):
            continue

        new_meta = dict(meta)
        new_meta["document_type"] = infer_document_type(meta.get("source_type", ""), doc_id)
        new_meta["metadata_normalized_at"] = now_iso

        updated_ids.append(doc_id)
        updated_metas.append(new_meta)
        updated_docs.append(document)

    if not updated_ids:
        print("No missing high-signal document_type metadata found.")
        return

    # Upsert with existing docs and unchanged IDs; metadata is the only intended delta.
    batch_size = 200
    for idx in range(0, len(updated_ids), batch_size):
        collection.upsert(
            ids=updated_ids[idx : idx + batch_size],
            documents=updated_docs[idx : idx + batch_size],
            metadatas=updated_metas[idx : idx + batch_size],
        )

    print(f"Updated document_type metadata for {len(updated_ids)} documents.")


if __name__ == "__main__":
    main()

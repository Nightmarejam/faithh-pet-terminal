#!/usr/bin/env python3
"""
Index reviewed archive summaries into ChromaDB.

Gate:
- Only rows with include_for_index=yes are indexed.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


def load_summary_map(path: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        out[str(rec.get("conversation_id", ""))] = rec
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Index reviewed archive summaries")
    parser.add_argument(
        "--review-queue",
        default="/home/jonat/ai-stack/reports/inventory/archive_review_queue.csv",
    )
    parser.add_argument(
        "--summaries",
        default="/home/jonat/ai-stack/reports/inventory/archive_summaries.jsonl",
    )
    parser.add_argument("--host", default=os.getenv("CHROMA_HOST", "192.158.1.10"))
    parser.add_argument("--port", type=int, default=int(os.getenv("CHROMA_PORT", "8000")))
    args = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = ""

    queue_path = Path(args.review_queue)
    summaries_path = Path(args.summaries)
    if not queue_path.exists():
        raise FileNotFoundError(queue_path)
    if not summaries_path.exists():
        raise FileNotFoundError(summaries_path)

    summary_map = load_summary_map(summaries_path)

    rows = list(csv.DictReader(queue_path.open("r", encoding="utf-8")))
    approved = [r for r in rows if str(r.get("include_for_index", "")).strip().lower() == "yes"]

    if not approved:
        print("No approved rows (include_for_index=yes). Nothing indexed.")
        return

    client = chromadb.HttpClient(host=args.host, port=args.port)
    col = client.get_collection("faithh_knowledge_base")
    embedder = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

    ids = []
    docs = []
    metas = []
    for row in approved:
        conv_id = str(row.get("conversation_id", ""))
        rec = summary_map.get(conv_id)
        if not rec:
            continue
        text = rec.get("summary_text", "").strip()
        if not text:
            continue
        ids.append(f"archive_summary_{conv_id}")
        docs.append(text)
        metas.append(
            {
                "domain": row.get("target_domain", "faithh_core"),
                "source_type": row.get("target_source_type", "archive_synthesis"),
                "document_type": "summary",
                "category": "project_docs",
                "quality_score": 0.8,
                "title": row.get("title", ""),
                "topic_tags": row.get("topic_tags", ""),
                "source_file": row.get("source_file", ""),
            }
        )

    if not ids:
        print("No valid approved records found in summary map.")
        return

    embs = embedder.encode(docs, show_progress_bar=False).tolist()
    batch = 64
    for i in range(0, len(ids), batch):
        col.upsert(
            ids=ids[i : i + batch],
            documents=docs[i : i + batch],
            embeddings=embs[i : i + batch],
            metadatas=metas[i : i + batch],
        )
    print(f"Indexed approved archive summaries: {len(ids)}")


if __name__ == "__main__":
    main()

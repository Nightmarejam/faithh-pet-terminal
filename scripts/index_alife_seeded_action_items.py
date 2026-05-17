#!/usr/bin/env python3
"""
Index seeded ALife action items into faithh_knowledge_base.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


def main() -> None:
    parser = argparse.ArgumentParser(description="Index seeded ALife action items")
    parser.add_argument(
        "--input",
        default="/home/jonat/ai-stack/reports/inventory/alife_seeded_action_items.jsonl",
    )
    parser.add_argument("--host", default=os.getenv("CHROMA_HOST", "192.158.1.10"))
    parser.add_argument("--port", type=int, default=int(os.getenv("CHROMA_PORT", "8000")))
    args = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = ""

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    rows = [json.loads(line) for line in input_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        print("No seeded action items to index.")
        return

    ids = []
    docs = []
    metas = []
    for row in rows:
        ids.append(row["doc_id"])
        docs.append(
            "\n".join(
                [
                    f"Seeded ALife action: {row['title']}",
                    f"Target experiment: {row['alife_target_experiment']}",
                    f"Task: {row['task']}",
                    f"Acceptance: {row['acceptance']}",
                    f"Input sources: {', '.join(row.get('input_sources', []))}",
                ]
            )
        )
        metas.append(
            {
                "domain": "alife",
                "source_type": "governance_seed_action_item",
                "document_type": "experiment_action_item",
                "category": "project_docs",
                "quality_score": 0.92,
                "action_id": row["action_id"],
                "priority": row.get("priority", "medium"),
                "alife_target_experiment": row["alife_target_experiment"],
                "status": row.get("status", "pending"),
            }
        )

    embedder = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    embeddings = embedder.encode(docs, show_progress_bar=False).tolist()

    client = chromadb.HttpClient(host=args.host, port=args.port)
    col = client.get_collection("faithh_knowledge_base")
    col.upsert(ids=ids, documents=docs, embeddings=embeddings, metadatas=metas)

    print(f"Indexed seeded ALife action items: {len(ids)}")


if __name__ == "__main__":
    main()

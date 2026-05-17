#!/usr/bin/env python3
"""
Index Constella synthesis set records into ChromaDB.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


def main() -> None:
    parser = argparse.ArgumentParser(description="Index Constella synthesis set")
    parser.add_argument(
        "--input",
        default="/home/jonat/ai-stack/reports/inventory/constella_synthesis_set.jsonl",
    )
    parser.add_argument("--host", default=os.getenv("CHROMA_HOST", "192.158.1.10"))
    parser.add_argument("--port", type=int, default=int(os.getenv("CHROMA_PORT", "8000")))
    args = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = ""

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    rows = [
        json.loads(line)
        for line in input_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not rows:
        print("No synthesis rows.")
        return

    ids = []
    docs = []
    metas = []
    for row in rows:
        ids.append(f"constella_synthesis_{row['synthesis_id']}")
        docs.append(row["statement"])
        metas.append(
            {
                "domain": "constella_constitutional",
                "source_type": "constella_synthesis",
                "document_type": "synthesis_entry",
                "category": "project_docs",
                "quality_score": 0.9,
                "epistemic_label": row["epistemic_label"],
                "governance_concept": row["governance_concept"],
                "alife_scenario_id": row["alife_scenario_id"],
                "constella_principle_id": row["constella_principle_id"],
                "constella_mechanism": row["constella_mechanism"],
            }
        )

    embedder = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    embeddings = embedder.encode(docs, show_progress_bar=False).tolist()

    client = chromadb.HttpClient(host=args.host, port=args.port)
    col = client.get_collection("faithh_knowledge_base")
    col.upsert(ids=ids, documents=docs, embeddings=embeddings, metadatas=metas)

    print(f"Indexed synthesis records: {len(ids)}")


if __name__ == "__main__":
    main()

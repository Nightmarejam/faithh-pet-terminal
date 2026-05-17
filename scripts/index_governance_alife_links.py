#!/usr/bin/env python3
"""
Index governance->ALife linkage records for scenario seeding.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


def main() -> None:
    parser = argparse.ArgumentParser(description="Index governance-ALife linkage records")
    parser.add_argument(
        "--input",
        default="/home/jonat/ai-stack/reports/inventory/governance_alife_links.jsonl",
    )
    parser.add_argument("--host", default=os.getenv("CHROMA_HOST", "192.158.1.10"))
    parser.add_argument("--port", type=int, default=int(os.getenv("CHROMA_PORT", "8000")))
    args = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = ""

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    records = []
    for line in input_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        records.append(json.loads(line))

    if not records:
        print("No link records found.")
        return

    docs = []
    metas = []
    ids = []
    for rec in records:
        doc = (
            f"Governance concept: {rec['governance_concept']}\n"
            f"ALife scenario: {rec['alife_scenario_id']}\n"
            f"ALife evidence: {', '.join(rec['alife_evidence'])}\n"
            f"Constella principle: {rec['constella_principle_id']}\n"
            f"Mechanism: {rec['constella_mechanism']}\n"
            f"Epistemic label: {rec['epistemic_label']}\n"
        )
        docs.append(doc)
        ids.append(rec["link_id"])
        metas.append(
            {
                "domain": "alife",
                "source_type": "governance_seed_link",
                "document_type": "scenario_link",
                "category": "project_docs",
                "quality_score": 0.95,
                "governance_concept": rec["governance_concept"],
                "alife_scenario_id": rec["alife_scenario_id"],
                "constella_principle_id": rec["constella_principle_id"],
                "epistemic_label": rec["epistemic_label"],
            }
        )

    embedder = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    embeddings = embedder.encode(docs, show_progress_bar=False).tolist()

    client = chromadb.HttpClient(host=args.host, port=args.port)
    col = client.get_collection("faithh_knowledge_base")
    col.upsert(ids=ids, documents=docs, embeddings=embeddings, metadatas=metas)

    print(f"Indexed governance seed links: {len(ids)}")


if __name__ == "__main__":
    main()

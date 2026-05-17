#!/usr/bin/env python3
"""
Index Claude export memories into ChromaDB faithh_knowledge_base with explicit
all-MiniLM-L6-v2 embeddings (CPU-only; matches FAITHH RAG query model).
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Block CUDA before any torch / sentence_transformers import (WSL sm_61 safety)
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import chromadb

MEMORIES_PATH = Path("/tmp/claude_export_2/memories.json")
CHROMA_HOST = os.getenv("CHROMA_HOST", "192.158.1.10")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
COLLECTION_NAME = "faithh_knowledge_base"

IDS = {
    "conversations": "claude_memory_conversations",
    "tomcat": "claude_memory_project_tomcat",
    "faithh": "claude_memory_project_faithh",
}


def load_memories() -> tuple[str, str, str]:
    if not MEMORIES_PATH.is_file():
        print(f"ERROR: {MEMORIES_PATH} not found", file=sys.stderr)
        sys.exit(1)
    raw = json.loads(MEMORIES_PATH.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        if not raw:
            print("ERROR: memories.json is an empty list", file=sys.stderr)
            sys.exit(1)
        record = raw[0]
    else:
        record = raw

    conv = record.get("conversations_memory") or ""
    pm = record.get("project_memories") or {}
    if not isinstance(pm, dict) or len(pm) < 2:
        print("ERROR: expected project_memories with at least two entries", file=sys.stderr)
        sys.exit(1)

    # Order preserved in JSON: first = Tom Cat / business, second = FAITHH / ALife
    vals = list(pm.values())
    return conv, vals[0], vals[1]


def build_metadata() -> dict:
    return {
        "domain": "faithh_core",
        "source_type": "claude_memory",
        "document_type": "memory",
        "quality_score": 0.95,
        "category": "project_docs",
        "indexed_at": datetime.now().strftime("%Y-%m-%d"),
    }


def main() -> None:
    from sentence_transformers import SentenceTransformer

    conv, tomcat, faithh = load_memories()
    texts = [
        (IDS["conversations"], conv),
        (IDS["tomcat"], tomcat),
        (IDS["faithh"], faithh),
    ]

    embedder = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    col = client.get_collection(COLLECTION_NAME)

    meta = build_metadata()
    ids = [t[0] for t in texts]
    documents = [t[1] for t in texts]
    embeddings = embedder.encode(documents, show_progress_bar=False).tolist()
    metadatas = [dict(meta) for _ in texts]

    col.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
    print(f"Upserted {len(ids)} memory documents into {COLLECTION_NAME}.")

    got = col.get(where={"domain": "faithh_core"}, limit=10_000, include=["metadatas"])
    n = len(got["ids"])
    print(f"Verification — documents with domain=faithh_core: {n}")


if __name__ == "__main__":
    main()

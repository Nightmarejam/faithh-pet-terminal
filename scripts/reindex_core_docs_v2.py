#!/usr/bin/env python3
"""
Re-index core orientation docs that were updated today.
Uses small chunks + per-chunk logging to avoid silent hangs.
DO NOT import torch or sentence_transformers - WSL crash risk.
"""
import sys
import hashlib
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("/home/jonat/ai-stack")
CHROMA_HOST = "servicebox.taileb8c60.ts.net"
CHROMA_PORT = 8000
CHUNK_SIZE = 1500
OVERLAP = 200

DOCS_TO_REINDEX = [
    "SYSTEMS_MAP.md",
    "CONTEXT.md",
    "scaffolding_state.json",
    "project_states.json",
]

def chunk_text(text):
    if len(text) <= CHUNK_SIZE:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunks.append(text[start:end])
        start = end - OVERLAP
    return chunks

def doc_id(docname, chunk_idx):
    h = hashlib.md5(f"{docname}:{chunk_idx}".encode()).hexdigest()[:8]
    return f"core_{docname[:15]}_{h}"

print("Starting reindex_core_docs_v2.py", flush=True)

import chromadb
client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
col = client.get_collection("faithh_knowledge_base")
before = col.count()
print(f"Connected. Before: {before} docs", flush=True)

total_chunks = 0
for docname in DOCS_TO_REINDEX:
    filepath = BASE_DIR / docname
    if not filepath.exists():
        print(f"SKIP: {docname}", flush=True)
        continue
    text = filepath.read_text(encoding="utf-8")
    chunks = chunk_text(text)
    print(f"  {docname}: {len(chunks)} chunks...", flush=True)
    for i, chunk in enumerate(chunks):
        try:
            col.upsert(
                ids=[doc_id(docname, i)],
                documents=[chunk],
                metadatas=[{
                    "source": docname,
                    "category": "core_orientation",
                    "project": "faithh",
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "timestamp": datetime.now().isoformat(),
                    "indexed_by": "reindex_core_docs_v2.py"
                }]
            )
        except Exception as e:
            print(f"    ERROR chunk {i}: {e}", flush=True)
    total_chunks += len(chunks)
    print(f"  {docname}: done", flush=True)

after = col.count()
print(f"Done. {total_chunks} chunks. Collection: {before} -> {after}")

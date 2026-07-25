#!/usr/bin/env python3
import sys
import hashlib
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
CHROMA_HOST = "servicebox.taileb8c60.ts.net"
CHROMA_PORT = 8000
CHUNK_SIZE = 1500
OVERLAP = 200

DOCS_TO_REINDEX = [
    BASE_DIR / "SYSTEMS_MAP.md",
    BASE_DIR / "CONTEXT.md",
    BASE_DIR / "scaffolding_state.json",
    BASE_DIR / "project_states.json",
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

def doc_id(filepath, chunk_idx):
    h = hashlib.md5(f"{filepath.name}:{chunk_idx}".encode()).hexdigest()[:8]
    return f"core_{filepath.stem[:25]}_{h}"

print("Starting reindex_core_docs.py", flush=True)

import chromadb
client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
col = client.get_collection("faithh_knowledge_base")
before = col.count()
print(f"Connected. Before: {before} docs", flush=True)

total_chunks = 0
for filepath in DOCS_TO_REINDEX:
    if not filepath.exists():
        print(f"SKIP: {filepath.name}", flush=True)
        continue
    text = filepath.read_text(encoding="utf-8")
    chunks = chunk_text(text)
    print(f"  {filepath.name}: {len(chunks)} chunks...", flush=True)
    for i, chunk in enumerate(chunks):
        try:
            col.upsert(
                ids=[doc_id(filepath, i)],
                documents=[chunk],
                metadatas=[{
                    "source": filepath.name,
                    "category": "core_orientation",
                    "project": "faithh",
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "timestamp": datetime.now().isoformat(),
                }]
            )
            if i % 5 == 0:
                print(f"    chunk {i+1}/{len(chunks)}", flush=True)
        except Exception as e:
            print(f"    ERROR chunk {i}: {e}", flush=True)
    total_chunks += len(chunks)
    print(f"  {filepath.name}: done", flush=True)

after = col.count()
print(f"Done. {total_chunks} chunks. Collection: {before} -> {after}")

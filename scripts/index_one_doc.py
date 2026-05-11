#!/usr/bin/env python3
"""Index just one harmony doc to test the approach."""
import sys
from pathlib import Path
from datetime import datetime

print("Starting...")
sys.stdout.flush()

BASE_DIR = Path("/home/jonat/ai-stack")
CHROMA_HOST = "192.158.1.243"
CHROMA_PORT = 8000

print("Importing chromadb...")
sys.stdout.flush()

import chromadb

print("Connecting to ChromaDB...")
sys.stdout.flush()

client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
collection = client.get_collection(name="faithh_knowledge_base")
before = collection.count()
print(f"Connected. Count: {before}")
sys.stdout.flush()

# Index one doc
doc_path = BASE_DIR / "ime/README.md"
print(f"Reading {doc_path.name}...")
sys.stdout.flush()

text = doc_path.read_text()[:1000]  # Just first 1000 chars
doc_id = "harmony_ime_readme_test"

print("Upserting...")
sys.stdout.flush()

collection.upsert(
    ids=[doc_id],
    documents=[text],
    metadatas=[{
        "source": "ime/README.md",
        "category": "ime_architecture",
        "indexed_by": "index_one_doc.py",
        "timestamp": datetime.now().isoformat()
    }]
)

after = collection.count()
print(f"Done. Count: {before} -> {after}")

# Verify
result = collection.get(ids=[doc_id])
if result['ids']:
    print(f"Verified: {result['metadatas'][0].get('source')}")
else:
    print("ERROR: Document not found after upsert")

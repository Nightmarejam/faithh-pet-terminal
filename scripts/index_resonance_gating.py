#!/usr/bin/env python3
"""Index the resonance gating architecture doc."""
import sys
import hashlib
from pathlib import Path
from datetime import datetime
import chromadb

print("Indexing resonance gating doc...")
sys.stdout.flush()

client = chromadb.HttpClient(host="servicebox.taileb8c60.ts.net", port=8000)
collection = client.get_collection(name="faithh_knowledge_base")
before = collection.count()

BASE_DIR = Path("/home/jonat/ai-stack")
doc_path = BASE_DIR / "projects/constella-framework/harmony/docs/resonance_gating_architecture_note_v1.0.md"

if not doc_path.exists():
    print(f"ERROR: {doc_path} not found")
    sys.exit(1)

text = doc_path.read_text(encoding='utf-8')
relative = str(doc_path.relative_to(BASE_DIR))

# Chunk into smaller pieces
CHUNK_SIZE = 1000  # Smaller chunks
chunks = []
start = 0
while start < len(text):
    end = min(start + CHUNK_SIZE, len(text))
    chunks.append(text[start:end])
    start = end - 200  # overlap

print(f"Indexing {len(chunks)} chunks...")
sys.stdout.flush()

for i, chunk in enumerate(chunks):
    h = hashlib.md5(f"{doc_path}:{i}".encode()).hexdigest()[:8]
    did = f"harmony_resonance_gating_{h}"
    
    collection.upsert(
        ids=[did],
        documents=[chunk],
        metadatas=[{
            "source": relative,
            "category": "ime_architecture",
            "project": "inner_monologue_engine",
            "chunk_index": i,
            "total_chunks": len(chunks),
            "indexed_by": "index_resonance_gating.py",
            "timestamp": datetime.now().isoformat()
        }]
    )

after = collection.count()
print(f"Done! {before} -> {after}")
sys.stdout.flush()

# Verify
results = collection.query(
    query_texts=["resonance gating architecture"],
    n_results=3
)

print("\nQuery results:")
for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
    source = meta.get('source', 'unknown')
    print(f"{i+1}. {source}")
    if 'resonance_gating' in source:
        print("   *** RESONANCE GATING DOC FOUND ***")

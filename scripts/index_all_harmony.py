#!/usr/bin/env python3
"""Index all harmony docs - single script, no loops that might fail."""
import sys
import hashlib
from pathlib import Path
from datetime import datetime
import chromadb

print("Connecting to ChromaDB...")
sys.stdout.flush()

client = chromadb.HttpClient(host="192.158.1.10", port=8000)
collection = client.get_collection(name="faithh_knowledge_base")
before = collection.count()
print(f"Before: {before} docs")
sys.stdout.flush()

BASE_DIR = Path("/home/jonat/ai-stack")
CHUNK_SIZE = 1500

def chunk_text(text):
    if len(text) <= CHUNK_SIZE:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunks.append(text[start:end])
        start = end - 200  # overlap
    return chunks

def index_doc(path, category="ime_architecture"):
    if not path.exists():
        print(f"  SKIP: {path.name}")
        return 0
    
    text = path.read_text(encoding='utf-8')
    chunks = chunk_text(text)
    relative = str(path.relative_to(BASE_DIR))
    
    for i, chunk in enumerate(chunks):
        h = hashlib.md5(f"{path}:{i}".encode()).hexdigest()[:8]
        did = f"harmony_{path.stem[:20]}_{h}"
        
        collection.upsert(
            ids=[did],
            documents=[chunk],
            metadatas=[{
                "source": relative,
                "category": category,
                "project": "inner_monologue_engine",
                "chunk_index": i,
                "total_chunks": len(chunks),
                "indexed_by": "index_all_harmony.py",
                "timestamp": datetime.now().isoformat()
            }]
        )
    
    print(f"  {path.name}: {len(chunks)} chunks")
    sys.stdout.flush()
    return len(chunks)

total = 0

# Index each doc explicitly
print("Indexing harmony docs...")
sys.stdout.flush()

total += index_doc(BASE_DIR / "projects/constella-framework/harmony/docs/resonance_gating_architecture_note_v1.0.md")
total += index_doc(BASE_DIR / "projects/constella-framework/harmony/docs/resonance_transformer_architecture_spec_v1.0.0.md")
total += index_doc(BASE_DIR / "projects/constella-framework/harmony/docs/harmony_ai_bridge_v1.0.0.md")
total += index_doc(BASE_DIR / "projects/constella-framework/harmony/docs/harmony_framework_complete_v4.0.0.md")
total += index_doc(BASE_DIR / "projects/constella-framework/harmony/docs/harmony_framework_handoff_v3.1.md")
total += index_doc(BASE_DIR / "projects/constella-framework/harmony/FAITHH_BACKEND_HANDOFF.md")
total += index_doc(BASE_DIR / "projects/constella-framework/harmony/harmony_faithh_context.md")
total += index_doc(BASE_DIR / "ime/README.md")
total += index_doc(BASE_DIR / "ime/docs/ARCHITECTURE.md")

after = collection.count()
print(f"\nDone! {total} chunks indexed")
print(f"Collection: {before} -> {after}")
sys.stdout.flush()

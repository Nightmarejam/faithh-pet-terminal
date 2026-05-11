#!/usr/bin/env python3
"""Index harmony docs one at a time to avoid memory issues."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Force CPU mode

import sys
import hashlib
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_DIR = Path(__file__).parent.parent
CHROMA_HOST = "192.158.1.243"
CHROMA_PORT = 8000
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200

# All harmony docs to index
HARMONY_DOCS = [
    BASE_DIR / "projects/constella-framework/harmony/docs/resonance_gating_architecture_note_v1.0.md",
    BASE_DIR / "projects/constella-framework/harmony/docs/resonance_transformer_architecture_spec_v1.0.0.md",
    BASE_DIR / "projects/constella-framework/harmony/docs/harmony_ai_bridge_v1.0.0.md",
    BASE_DIR / "projects/constella-framework/harmony/docs/harmony_framework_complete_v4.0.0.md",
    BASE_DIR / "projects/constella-framework/harmony/docs/harmony_framework_handoff_v3.1.md",
    BASE_DIR / "projects/constella-framework/harmony/FAITHH_BACKEND_HANDOFF.md",
    BASE_DIR / "projects/constella-framework/harmony/harmony_faithh_context.md",
    BASE_DIR / "ime/README.md",
    BASE_DIR / "ime/docs/ARCHITECTURE.md",
]

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            for sep in ['\n\n', '\n', '. ', ' ']:
                boundary = text.rfind(sep, start + overlap, end)
                if boundary > start + overlap:
                    end = boundary + len(sep)
                    break
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def doc_id(filepath, chunk_idx):
    h = hashlib.md5(f"{filepath}:{chunk_idx}".encode()).hexdigest()[:8]
    stem = filepath.stem[:30].replace(' ', '_')
    return f"harmony_{stem}_{h}"

for path in HARMONY_DOCS:
    exists = path.exists()
    print(f"  {path.name}: {'EXISTS' if exists else 'MISSING'}")

# Test 2: Connect to ChromaDB
print("\n=== Step 2: ChromaDB connection ===")
try:
    import chromadb
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    collection = client.get_collection(name="faithh_knowledge_base")
    print(f"  Connected! Documents: {collection.count():,}")
except Exception as e:
    print(f"  ERROR: {e}")
    sys.exit(1)

# Test 3: Load embedding model
print("\n=== Step 3: Loading embedding model ===")
try:
    from sentence_transformers import SentenceTransformer
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    test_vec = embedder.encode(["test"])
    print(f"  Loaded! Vector shape: {test_vec.shape}")
except Exception as e:
    print(f"  ERROR: {e}")
    sys.exit(1)

# Step 4: Index all harmony docs
print("\n=== Step 4: Indexing all harmony docs ===")
total_chunks = 0

for filepath in HARMONY_DOCS:
    if not filepath.exists():
        print(f"  SKIP: {filepath.name} not found")
        continue
    
    text = filepath.read_text(encoding='utf-8')
    chunks = chunk_text(text)
    relative = str(filepath.relative_to(BASE_DIR))
    
    print(f"  {filepath.name}: {len(chunks)} chunks")
    
    ids = []
    documents = []
    metadatas = []
    
    for i, chunk in enumerate(chunks):
        did = doc_id(filepath, i)
        ids.append(did)
        documents.append(chunk)
        metadatas.append({
            "source": relative,
            "category": "ime_architecture",
            "project": "inner_monologue_engine",
            "chunk_index": i,
            "total_chunks": len(chunks),
            "file_stem": filepath.stem,
            "timestamp": datetime.now().isoformat(),
            "indexed_by": "debug_indexer.py"
        })
    
    try:
        embeddings = embedder.encode(documents).tolist()
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
        print(f"    ✅ Indexed {len(ids)} chunks")
        total_chunks += len(ids)
    except Exception as e:
        print(f"    ❌ ERROR: {e}")

print(f"\n=== Done: {total_chunks} chunks indexed ===")
print(f"Collection now has: {collection.count():,} documents")

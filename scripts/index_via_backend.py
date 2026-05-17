#!/usr/bin/env python3
"""
Index harmony docs using the FAITHH backend's embedder.
This avoids loading SentenceTransformer locally which causes WSL memory issues.
"""
import requests
import hashlib
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
BACKEND_URL = "http://127.0.0.1:5557"
CHROMA_HOST = "192.158.1.10"
CHROMA_PORT = 8000
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200

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

def main():
    # Check backend health
    print("=== Checking backend ===")
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=5)
        r.raise_for_status()
        print(f"  Backend healthy")
    except Exception as e:
        print(f"  ERROR: Backend not responding: {e}")
        sys.exit(1)

    # Connect to ChromaDB directly (lightweight, no ML models)
    print("\n=== Connecting to ChromaDB ===")
    import chromadb
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    collection = client.get_collection(name="faithh_knowledge_base")
    before_count = collection.count()
    print(f"  Connected! Documents: {before_count:,}")

    # Get embeddings from backend via a simple query
    # The backend will load the embedder lazily
    print("\n=== Warming up backend embedder ===")
    try:
        r = requests.post(f"{BACKEND_URL}/api/rag_search", 
                         json={"query": "test", "n_results": 1}, timeout=30)
        print(f"  Embedder ready")
    except Exception as e:
        print(f"  Warning: {e}")

    # Now index docs one at a time using ChromaDB's default embedding
    print("\n=== Indexing harmony docs ===")
    total_chunks = 0

    for filepath in HARMONY_DOCS:
        if not filepath.exists():
            print(f"  SKIP: {filepath.name} not found")
            continue

        text = filepath.read_text(encoding='utf-8')
        chunks = chunk_text(text)
        relative = str(filepath.relative_to(BASE_DIR))

        print(f"  {filepath.name}: {len(chunks)} chunks")

        for i, chunk in enumerate(chunks):
            did = doc_id(filepath, i)
            meta = {
                "source": relative,
                "category": "ime_architecture",
                "project": "inner_monologue_engine",
                "chunk_index": i,
                "total_chunks": len(chunks),
                "file_stem": filepath.stem,
                "timestamp": datetime.now().isoformat(),
                "indexed_by": "index_via_backend.py"
            }

            try:
                # Use ChromaDB's add with documents - it will use the collection's embedding function
                collection.upsert(
                    ids=[did],
                    documents=[chunk],
                    metadatas=[meta]
                )
            except Exception as e:
                print(f"    ERROR on chunk {i}: {e}")
                continue

        total_chunks += len(chunks)
        print(f"    ✅ Indexed {len(chunks)} chunks")

    after_count = collection.count()
    print(f"\n=== Done ===")
    print(f"  Total chunks indexed: {total_chunks}")
    print(f"  Collection: {before_count:,} → {after_count:,}")

if __name__ == "__main__":
    main()

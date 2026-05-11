#!/usr/bin/env python3
"""
Index harmony docs into FAITHH ChromaDB.

Indexes specific files from projects/constella-framework/harmony/docs/
using all-MiniLM-L6-v2 (384-dim) to match the existing collection.

Usage:
    cd ~/ai-stack
    source venv/bin/activate
    python scripts/index_harmony_docs.py [--dry-run] [--force]
"""

# Force CPU mode to avoid CUDA compatibility issues with GTX 1080 Ti
# The RTX 3090 (GPU 1) should work but CUDA_VISIBLE_DEVICES doesn't work reliably in WSL2
# CPU is sufficient for embedding ~100 chunks
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Disable CUDA entirely

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
    import chromadb
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: source venv/bin/activate first")
    sys.exit(1)

CHROMA_HOST = "192.158.1.243"
CHROMA_PORT = 8000
COLLECTION_NAME = "faithh_knowledge_base"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200

BASE_DIR = Path(__file__).parent.parent  # ai-stack root

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

# IME-related docs
IME_DOCS = [
    BASE_DIR / "ime/README.md",
    BASE_DIR / "ime/docs/ARCHITECTURE.md",
]


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks."""
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        # Try to end at a sentence or newline boundary
        if end < len(text):
            for sep in ['\n\n', '\n', '. ', ' ']:
                boundary = text.rfind(sep, start + overlap, end)
                if boundary > start + overlap:
                    end = boundary + len(sep)
                    break
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def doc_id(filepath: Path, chunk_idx: int) -> str:
    """Generate stable doc ID from filepath + chunk index."""
    h = hashlib.md5(f"{filepath}:{chunk_idx}".encode()).hexdigest()[:8]
    stem = filepath.stem[:30].replace(' ', '_')
    return f"harmony_{stem}_{h}"


def main():
    parser = argparse.ArgumentParser(description="Index harmony docs into FAITHH RAG")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be indexed, don't write")
    parser.add_argument("--force", action="store_true", help="Re-index even if already present")
    args = parser.parse_args()

    # Check files exist
    docs_to_index = []
    for path in HARMONY_DOCS:
        if path.exists():
            docs_to_index.append(path)
        else:
            print(f"  ⚠️  Not found: {path.relative_to(BASE_DIR)}")

    if not docs_to_index:
        print("❌ No harmony docs found. Check paths.")
        sys.exit(1)

    print(f"📄 Found {len(docs_to_index)} docs to index")
    for p in docs_to_index:
        size = len(p.read_text(encoding='utf-8'))
        print(f"   {p.relative_to(BASE_DIR)} ({size:,} chars)")

    if args.dry_run:
        print("\n[DRY RUN] Would index the above files. Remove --dry-run to proceed.")
        return

    # Connect to ChromaDB
    print(f"\n🔌 Connecting to ChromaDB at {CHROMA_HOST}:{CHROMA_PORT}...")
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    collection = client.get_collection(name=COLLECTION_NAME)
    before_count = collection.count()
    print(f"   Collection '{COLLECTION_NAME}': {before_count:,} documents")

    # Load embedding model
    print(f"🧠 Loading {EMBEDDING_MODEL}...")
    embedder = SentenceTransformer(EMBEDDING_MODEL)

    # Index docs
    total_chunks = 0
    total_skipped = 0

    for filepath in docs_to_index:
        text = filepath.read_text(encoding='utf-8')
        chunks = chunk_text(text)
        relative = str(filepath.relative_to(BASE_DIR))

        # Determine category
        if 'constella-framework/harmony' in relative:
            category = "ime_architecture"
            project = "inner_monologue_engine"
        elif 'ime/' in relative:
            category = "ime_scaffold"
            project = "inner_monologue_engine"
        else:
            category = "project_docs"
            project = "faithh"

        print(f"\n  📝 {relative} → {len(chunks)} chunks")

        ids = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            did = doc_id(filepath, i)

            # Check if already exists
            if not args.force:
                try:
                    existing = collection.get(ids=[did])
                    if existing['ids']:
                        print(f"     chunk {i}: already indexed, skipping")
                        total_skipped += 1
                        continue
                except Exception:
                    pass

            ids.append(did)
            documents.append(chunk)
            metadatas.append({
                "source": relative,
                "category": category,
                "project": project,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "file_stem": filepath.stem,
                "timestamp": datetime.now().isoformat(),
                "indexed_by": "index_harmony_docs.py"
            })

        if not ids:
            continue

        # Embed and upsert
        embeddings = embedder.encode(documents).tolist()
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
        print(f"     ✅ Indexed {len(ids)} chunks")
        total_chunks += len(ids)

    # Final report
    after_count = collection.count()
    print(f"\n{'='*50}")
    print(f"✅ Done: {total_chunks} chunks added, {total_skipped} skipped")
    print(f"   Collection: {before_count:,} → {after_count:,} documents")
    print(f"   Net added: {after_count - before_count:,}")

    # Verify with test query
    print(f"\n🔍 Verifying with test query: 'resonance gating premature synthesis'")
    query_vec = embedder.encode(["resonance gating premature synthesis"]).tolist()
    results = collection.query(query_embeddings=query_vec, n_results=3)
    for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
        source = meta.get('source', 'unknown')
        print(f"  {i+1}. [{source}]: {doc[:100]}...")
    print("\nIf harmony docs appear above, indexing succeeded.")


if __name__ == "__main__":
    main()

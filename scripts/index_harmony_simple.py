#!/usr/bin/env python3
"""
Simple harmony docs indexer - uses ChromaDB's default embedding.
No SentenceTransformer loading, no backend dependency.
"""
import hashlib
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
CHROMA_HOST = "192.158.1.243"
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
    import sys
    import chromadb
    
    print("=== Harmony Docs Indexer (Simple) ===")
    sys.stdout.flush()
    
    # Connect to ChromaDB
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    collection = client.get_collection(name="faithh_knowledge_base")
    before_count = collection.count()
    print(f"ChromaDB connected: {before_count:,} documents")
    sys.stdout.flush()
    
    # Index each doc
    total_chunks = 0
    
    for filepath in HARMONY_DOCS:
        if not filepath.exists():
            print(f"  SKIP: {filepath.name}")
            continue
        
        text = filepath.read_text(encoding='utf-8')
        chunks = chunk_text(text)
        relative = str(filepath.relative_to(BASE_DIR))
        
        print(f"  {filepath.name}: {len(chunks)} chunks", end="", flush=True)
        
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
                "indexed_by": "index_harmony_simple.py"
            }
            
            try:
                collection.upsert(ids=[did], documents=[chunk], metadatas=[meta])
            except Exception as e:
                print(f" ERROR: {e}")
                continue
        
        total_chunks += len(chunks)
        print(" OK")
    
    after_count = collection.count()
    print(f"\n=== Done ===")
    print(f"Indexed: {total_chunks} chunks")
    print(f"Collection: {before_count:,} -> {after_count:,}")

if __name__ == "__main__":
    main()

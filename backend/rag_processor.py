#!/usr/bin/env python3
"""
RAG Document Processor
Chunks documents, generates embeddings, and stores in ChromaDB
"""

import os
import logging
import chromadb
import hashlib
from pathlib import Path
from typing import Any, List, Dict, Optional

_rag_norm_log = logging.getLogger("faithh.rag.normalize")

try:
    from sentence_transformers import SentenceTransformer
    _EMBEDDER: Optional[SentenceTransformer] = None
except ImportError:
    _EMBEDDER = None  # type: ignore
    SentenceTransformer = None  # type: ignore

# Configuration
CHROMA_HOST = os.environ.get("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))
EMBED_MODEL = os.environ.get("FAITHH_EMBED_MODEL", "BAAI/bge-base-en-v1.5")
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def _resolve_device() -> str:
    """Pick the embedding device.

    Historically pinned to CPU because SentenceTransformer detected cuda:0 and
    crashed under WSL. That constraint is gone — the backend runs on the Gen8
    (native Linux, RTX A1000). Measured 2026-07-26 on this host with
    BAAI/bge-base-en-v1.5, batch 64: CPU 3.8 docs/sec vs CUDA 135 docs/sec (~36x),
    which is the difference between a 30-hour and a 50-minute re-index.

    Override with FAITHH_EMBED_DEVICE=cpu when the GPU is busy (it is shared with
    Plex transcoding) or on a host without CUDA.
    """
    forced = os.environ.get("FAITHH_EMBED_DEVICE")
    if forced:
        return forced
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
    except Exception:  # torch missing or broken driver — fall back quietly
        pass
    return "cpu"


def _get_embedder():
    """Lazy-load the sentence-transformers model (GPU when available)."""
    global _EMBEDDER
    if _EMBEDDER is None and SentenceTransformer is not None:
        device = _resolve_device()
        try:
            _EMBEDDER = SentenceTransformer(EMBED_MODEL, device=device)
        except Exception as exc:  # noqa: BLE001 - never let device choice break RAG
            if device == "cpu":
                raise
            logging.getLogger("faithh.rag").warning(
                "embedder failed on %s (%s); falling back to CPU", device, exc
            )
            _EMBEDDER = SentenceTransformer(EMBED_MODEL, device="cpu")
    return _EMBEDDER

class RAGProcessor:
    def __init__(self):
        self.client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"description": "User documents for RAG"}
        )
    
    def chunk_text(self, text: str, filename: str) -> List[Dict]:
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + CHUNK_SIZE
            chunk_text = text[start:end]
            chunk_id = hashlib.md5(f"{filename}:{start}".encode()).hexdigest()
            
            chunks.append({
                "id": chunk_id,
                "text": chunk_text,
                "metadata": {
                    "filename": filename,
                    "start_pos": start,
                    "end_pos": end
                }
            })
            
            start += CHUNK_SIZE - CHUNK_OVERLAP
        
        return chunks
    
    def get_embedding(self, text: str) -> List[float]:
        embedder = _get_embedder()
        if embedder is None:
            raise RuntimeError("sentence-transformers not installed — pip install sentence-transformers")
        return embedder.encode([text])[0].tolist()
    
    def add_document(self, filepath: str):
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        print(f"📄 Processing: {path.name}")
        print(f"   Length: {len(text)} characters")
        
        chunks = self.chunk_text(text, path.name)
        print(f"   Created {len(chunks)} chunks")
        
        print("   Generating embeddings...")
        for i, chunk in enumerate(chunks):
            embedding = self.get_embedding(chunk["text"])
            
            self.collection.add(
                embeddings=[embedding],
                documents=[chunk["text"]],
                metadatas=[chunk["metadata"]],
                ids=[chunk["id"]]
            )
            
            if (i + 1) % 10 == 0:
                print(f"   Processed {i + 1}/{len(chunks)} chunks")
        
        print(f"✅ Added {path.name} to database")
    
    def search(self, query: str, n_results: int = 3) -> List[Dict]:
        query_embedding = self.get_embedding(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        formatted = []
        for i in range(len(results['documents'][0])):
            formatted.append({
                "text": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i] if 'distances' in results else None
            })
        
        return formatted
    
    def list_documents(self) -> List[str]:
        all_items = self.collection.get()
        filenames = set()
        
        if all_items['metadatas']:
            for metadata in all_items['metadatas']:
                filenames.add(metadata.get('filename', 'unknown'))
        
        return sorted(list(filenames))


def main():
    import sys
    
    processor = RAGProcessor()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Add document:    python rag_processor.py add <filepath>")
        print("  Search:          python rag_processor.py search <query>")
        print("  List documents:  python rag_processor.py list")
        return
    
    command = sys.argv[1]
    
    if command == "add":
        if len(sys.argv) < 3:
            print("Error: Please provide a file path")
            return
        processor.add_document(sys.argv[2])
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("Error: Please provide a search query")
            return
        query = " ".join(sys.argv[2:])
        results = processor.search(query)
        
        print(f"\n🔍 Search results for: '{query}'\n")
        for i, result in enumerate(results, 1):
            print(f"Result {i}:")
            print(f"  File: {result['metadata']['filename']}")
            print(f"  Text: {result['text'][:200]}...")
            if result['distance']:
                print(f"  Distance: {result['distance']:.4f}")
            print()
    
    elif command == "list":
        docs = processor.list_documents()
        print(f"\n📚 Indexed documents ({len(docs)}):")
        for doc in docs:
            print(f"  - {doc}")
    
    else:
        print(f"Unknown command: {command}")


def normalize_rag_hit_for_api(entry: Any) -> Dict[str, Any]:
    # Logic for Humans: Take whatever shape Chroma returned and output a dict the Canvas UI always understands (document, content, metadata, distance, id).
    """
    Normalize Chroma / RAG hits for /api/chat and the Sources UI.

    faithh_pet_v4.html uses: source.document || source.content (then JSON.stringify).
    Also set source.text to the same excerpt so any consumer expecting `text` or `snippet` works.
    """
    if isinstance(entry, str):
        return {
            "document": entry,
            "content": entry,
            "text": entry,
            "snippet": entry,
            "metadata": {},
            "distance": None,
            "id": "",
        }
    if not isinstance(entry, dict):
        s = str(entry)
        return {
            "document": s,
            "content": s,
            "text": s,
            "snippet": s,
            "metadata": {},
            "distance": None,
            "id": "",
        }

    out = dict(entry)
    meta = out.get("metadata")
    if not isinstance(meta, dict):
        meta = {}

    body = out.get("document") or out.get("text") or out.get("content") or out.get("snippet") or ""
    if isinstance(body, (dict, list)):
        body = str(body)
    body = str(body or "")
    if not body.strip():
        bits = [
            str(meta.get(k) or "")
            for k in ("title", "filename", "source", "user_preview", "path", "chunk_index")
        ]
        body = " ".join(b for b in bits if b).strip()
    if not body.strip():
        body = "(empty excerpt — metadata only; expand in Chroma if needed)"

    out["metadata"] = meta
    out["document"] = body
    out["content"] = body
    out["text"] = body
    out["snippet"] = body[:500] if len(body) > 500 else body
    if os.environ.get("FAITHH_RAG_NORMALIZE_TRACE", "").strip() in ("1", "true", "yes"):
        preview = (body or "")[:100].replace("\n", " ")
        _rag_norm_log.info("normalize_rag_hit_for_api document_preview=%r", preview)
    return out


if __name__ == "__main__":
    main()

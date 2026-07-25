#!/usr/bin/env python3
"""
Re-index current project documentation into ChromaDB.
Adds/updates 'project_docs' category chunks so FAITHH has fresh,
accurate info about the current project state.

Usage:
    source venv/bin/activate
    python scripts/reindex_project_docs.py
    python scripts/reindex_project_docs.py --purge-stale   # remove old project_docs first
"""

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import chromadb

CHROMA_HOST = os.environ.get("CHROMA_HOST", "servicebox.taileb8c60.ts.net")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))
COLLECTION_NAME = "faithh_knowledge_base"
BASE_DIR = Path(__file__).parent.parent

# Files to index (relative to BASE_DIR)
# Root-level docs + key docs in each subfolder (auto-discovery adds more below)
PROJECT_DOCS = [
    "AGENTS.md",
    "README.md",
    "CONTEXT.md",
    "SYSTEMS_MAP.md",
    "docs/README.md",
    "docs/archive/legacy/HARMONY_CONTEXT.md",
]

# Docs subfolders to scan (excludes archive/)
DOCS_SCAN_DIRS = [
    "docs/architecture",
    "docs/guides",
    "docs/reference",
    "docs/business",
    "docs/research",
    "docs/roadmaps",
]

# Also index key config/state files (as structured summaries)
STATE_FILES = [
    "project_states.json",
    "scaffolding_state.json",
    "config.yaml",
    "decisions_log.json",
]

CHUNK_SIZE = 1500  # characters per chunk
CHUNK_OVERLAP = 200


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    return chunks


def make_doc_id(filepath, chunk_index):
    """Create a deterministic ID for a document chunk."""
    key = f"project_docs:{filepath}:chunk_{chunk_index}"
    return hashlib.md5(key.encode()).hexdigest()[:16]


def purge_stale_project_docs(collection):
    """Remove all existing project_docs chunks from the collection."""
    print("Purging existing project_docs chunks...")
    try:
        results = collection.get(
            where={"category": "project_docs"},
            limit=10000,
        )
        if results and results["ids"]:
            collection.delete(ids=results["ids"])
            print(f"  Removed {len(results['ids'])} stale project_docs chunks")
        else:
            print("  No existing project_docs chunks found")
    except Exception as e:
        print(f"  Purge error (may be fine on first run): {e}")


def index_markdown_file(collection, filepath, existing_ids):
    """Index a markdown file into ChromaDB."""
    full_path = BASE_DIR / filepath
    if not full_path.exists():
        print(f"  SKIP (not found): {filepath}")
        return 0

    text = full_path.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        print(f"  SKIP (empty): {filepath}")
        return 0

    chunks = chunk_text(text)
    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        doc_id = make_doc_id(filepath, i)
        ids.append(doc_id)
        documents.append(chunk)
        metadatas.append({
            "source": f"project_docs:{filepath}",
            "title": filepath,
            "type": "project_documentation",
            "category": "project_docs",
            "chunk_index": i,
            "total_chunks": len(chunks),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "file_path": filepath,
        })

    # Upsert (add or update)
    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    print(f"  Indexed: {filepath} ({len(chunks)} chunks)")
    return len(chunks)


def index_state_file(collection, filepath):
    """Index a JSON/YAML state file as a summary."""
    full_path = BASE_DIR / filepath
    if not full_path.exists():
        print(f"  SKIP (not found): {filepath}")
        return 0

    text = full_path.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        return 0

    # For JSON files, create a readable summary
    if filepath.endswith(".json"):
        try:
            data = json.loads(text)
            # Flatten to a readable summary (first 3000 chars of pretty-printed)
            summary = json.dumps(data, indent=2)[:3000]
        except json.JSONDecodeError:
            summary = text[:3000]
    else:
        summary = text[:3000]

    chunks = chunk_text(summary)
    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        doc_id = make_doc_id(filepath, i)
        ids.append(doc_id)
        documents.append(chunk)
        metadatas.append({
            "source": f"project_docs:{filepath}",
            "title": filepath,
            "type": "project_state",
            "category": "project_docs",
            "chunk_index": i,
            "total_chunks": len(chunks),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "file_path": filepath,
        })

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    print(f"  Indexed: {filepath} ({len(chunks)} chunks)")
    return len(chunks)


def main():
    parser = argparse.ArgumentParser(description="Re-index project docs into ChromaDB")
    parser.add_argument("--purge-stale", action="store_true",
                        help="Remove old project_docs before re-indexing")
    args = parser.parse_args()

    print("=" * 50)
    print("FAITHH Project Documentation Re-Indexer")
    print("=" * 50)
    print(f"ChromaDB: {CHROMA_HOST}:{CHROMA_PORT}")
    print(f"Collection: {COLLECTION_NAME}")
    print()

    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    collection = client.get_collection(COLLECTION_NAME)
    before_count = collection.count()
    print(f"Collection has {before_count:,} docs before indexing")

    if args.purge_stale:
        purge_stale_project_docs(collection)

    # Auto-discover markdown files in active docs subfolders (not archive/)
    for scan_dir in DOCS_SCAN_DIRS:
        dpath = BASE_DIR / scan_dir
        if dpath.exists():
            for f in sorted(dpath.rglob("*.md")):
                rel = str(f.relative_to(BASE_DIR))
                if rel not in PROJECT_DOCS:
                    PROJECT_DOCS.append(rel)

    print(f"\nIndexing {len(PROJECT_DOCS)} documentation files...")
    total_chunks = 0
    for filepath in PROJECT_DOCS:
        total_chunks += index_markdown_file(collection, filepath, set())

    print(f"\nIndexing {len(STATE_FILES)} state files...")
    for filepath in STATE_FILES:
        total_chunks += index_state_file(collection, filepath)

    after_count = collection.count()
    print(f"\n{'=' * 50}")
    print(f"Done! Indexed {total_chunks} chunks from {len(PROJECT_DOCS) + len(STATE_FILES)} files")
    print(f"Collection: {before_count:,} → {after_count:,} docs")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()

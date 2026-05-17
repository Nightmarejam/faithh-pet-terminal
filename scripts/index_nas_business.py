#!/usr/bin/env python3
"""
Index NAS Business Documents to Gen 8 ChromaDB
Focuses on Tom Cat Sound LLC / Floating Garden Soundworks business docs
"""

import os
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from sentence_transformers import SentenceTransformer
import chromadb

# Configuration
GEN8_CHROMA_HOST = "192.158.1.10"
GEN8_CHROMA_PORT = 8000
COLLECTION_NAME = "faithh_knowledge_base"
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"

# NAS paths to index
NAS_PATHS = [
    ("/Volumes/AI/Tom_Cat_Sound_LLC", "tomcat"),
    ("/Volumes/AI/langflow/TRANSFER_INSTRUCTIONS.md", "tomcat"),  # Single file
]

# Chunk settings
MAX_CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200


def chunk_text(text: str) -> List[str]:
    """Split text into overlapping chunks."""
    if len(text) <= MAX_CHUNK_SIZE:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + MAX_CHUNK_SIZE
        if end < len(text):
            para_break = text.rfind('\n\n', start, end)
            if para_break > start + MAX_CHUNK_SIZE // 2:
                end = para_break + 2
        chunks.append(text[start:end].strip())
        start = end - CHUNK_OVERLAP
    return [c for c in chunks if c]


def extract_title(content: str, filepath: str) -> str:
    """Extract title from markdown or use filename."""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return Path(filepath).stem.replace('_', ' ').title()


def generate_doc_id(filepath: str, chunk_index: int) -> str:
    """Generate unique document ID."""
    path_hash = hashlib.md5(filepath.encode()).hexdigest()[:12]
    return f"nas_{path_hash}_{chunk_index}"


def detect_topics(content: str, filepath: str) -> str:
    """Detect business-related topics."""
    topics = set()
    content_lower = content.lower()
    
    if any(x in content_lower for x in ['llc', 'formation', 'operating agreement', 'ein']):
        topics.add('legal')
    if any(x in content_lower for x in ['revenue', 'income', 'pricing', 'client', 'invoice']):
        topics.add('business')
    if any(x in content_lower for x in ['grant', 'sbdc', 'funding', 'loan']):
        topics.add('funding')
    if any(x in content_lower for x in ['mastering', 'mixing', 'audio', 'production']):
        topics.add('audio')
    if any(x in content_lower for x in ['workflow', 'process', 'checklist', 'action']):
        topics.add('operations')
    if any(x in content_lower for x in ['partner', 'thomas', 'kevin', 'member']):
        topics.add('partnership')
    
    return ','.join(sorted(topics)) if topics else 'business'


def collect_files(base_path: str) -> List[str]:
    """Collect markdown files from path (file or directory)."""
    path = Path(base_path)
    if path.is_file():
        return [str(path)] if path.suffix == '.md' else []
    
    files = []
    for root, dirs, filenames in os.walk(base_path):
        for filename in filenames:
            if filename.endswith('.md'):
                files.append(os.path.join(root, filename))
    return files


def process_file(filepath: str, project: str) -> List[Dict]:
    """Process a single file into chunks."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"  Error reading {filepath}: {e}")
        return []
    
    if not content.strip():
        return []
    
    title = extract_title(content, filepath)
    topics = detect_topics(content, filepath)
    chunks = chunk_text(content)
    
    try:
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
    except:
        mtime = datetime.now().isoformat()
    
    documents = []
    for i, chunk in enumerate(chunks):
        doc_id = generate_doc_id(filepath, i)
        documents.append({
            'id': doc_id,
            'content': chunk,
            'metadata': {
                'source': 'nas_business',
                'title': title,
                'project': project,
                'topics': topics,
                'has_code': False,
                'chunk_index': i,
                'total_chunks': len(chunks),
                'filepath': filepath,
                'created_at': mtime,
                'indexed_at': datetime.now().isoformat(),
            }
        })
    return documents


def main():
    print("=" * 60)
    print("NAS Business Document Indexer → Gen 8 ChromaDB")
    print("=" * 60)
    
    # Load model
    print(f"\n📦 Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("   ✅ Model loaded")
    
    # Connect to Gen 8
    print(f"\n🔌 Connecting to Gen 8 ChromaDB...")
    try:
        client = chromadb.HttpClient(host=GEN8_CHROMA_HOST, port=GEN8_CHROMA_PORT)
        client.heartbeat()
        print("   ✅ Connected")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return
    
    # Get collection
    print(f"\n📚 Accessing collection: {COLLECTION_NAME}")
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
        current_count = collection.count()
        print(f"   ✅ Collection found ({current_count} existing documents)")
    except Exception as e:
        print(f"   ❌ Collection error: {e}")
        return
    
    # Collect files
    print("\n📁 Collecting NAS business documents...")
    all_documents = []
    
    for path, project in NAS_PATHS:
        if not os.path.exists(path):
            print(f"   ⚠️  Path not found: {path}")
            continue
        
        files = collect_files(path)
        print(f"   {project}: {len(files)} files from {path}")
        
        for filepath in files:
            docs = process_file(filepath, project)
            all_documents.extend(docs)
    
    print(f"\n📄 Total chunks to index: {len(all_documents)}")
    
    if not all_documents:
        print("No documents to index!")
        return
    
    # Generate embeddings and upsert
    print("\n🧮 Generating embeddings and indexing...")
    batch_size = 32
    
    for i in range(0, len(all_documents), batch_size):
        batch = all_documents[i:i + batch_size]
        batch_texts = [doc['content'] for doc in batch]
        
        embeddings = model.encode(batch_texts, show_progress_bar=False)
        
        ids = [doc['id'] for doc in batch]
        documents = [doc['content'] for doc in batch]
        metadatas = [doc['metadata'] for doc in batch]
        
        try:
            collection.upsert(
                ids=ids,
                embeddings=embeddings.tolist(),
                documents=documents,
                metadatas=metadatas,
            )
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
        
        progress = min(i + batch_size, len(all_documents))
        print(f"   Progress: {progress}/{len(all_documents)}")
    
    # Verify
    final_count = collection.count()
    print(f"\n✅ Indexing complete!")
    print(f"   Documents in collection: {final_count}")
    print(f"   New documents added: {final_count - current_count}")
    
    # List what was indexed
    print("\n📋 Files indexed:")
    seen_files = set()
    for doc in all_documents:
        fp = doc['metadata']['filepath']
        if fp not in seen_files:
            seen_files.add(fp)
            print(f"   - {Path(fp).name}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Index ai-stack and constella-framework documentation to Gen 8 ChromaDB.

Usage:
    cd ~/ai-stack
    source venv/bin/activate
    python scripts/index_docs_to_gen8.py

This will index markdown files and push them to the Gen 8 ChromaDB
at http://192.158.1.243:8000
"""

import os
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import requests

# Will be imported after we verify they exist
try:
    from sentence_transformers import SentenceTransformer
    import chromadb
    from chromadb.config import Settings
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: pip install sentence-transformers chromadb")
    exit(1)

# Configuration
GEN8_CHROMA_HOST = "192.158.1.243"
GEN8_CHROMA_PORT = 8000
COLLECTION_ID = "71e13a01-cbb6-48ba-a126-2a16320d40c0"
COLLECTION_NAME = "faithh_knowledge_base"
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"  # 768 dimensions

# Directories to index
DIRS_TO_INDEX = [
    ("/Users/macjohn/ai-stack", "faithh"),
    ("/Users/macjohn/Projects/constella-framework", "constella"),
]

# Files/dirs to skip
SKIP_PATTERNS = [
    "venv/", "node_modules/", ".git/", "__pycache__/",
    ".DS_Store", "*.pyc", "chroma_db/"
]

# Chunk settings
MAX_CHUNK_SIZE = 1500  # characters
CHUNK_OVERLAP = 200


def should_skip(path: str) -> bool:
    """Check if path should be skipped."""
    for pattern in SKIP_PATTERNS:
        if pattern in path:
            return True
    return False


def chunk_text(text: str, max_size: int = MAX_CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks."""
    if len(text) <= max_size:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_size
        
        # Try to break at paragraph or sentence boundary
        if end < len(text):
            # Look for paragraph break
            para_break = text.rfind('\n\n', start, end)
            if para_break > start + max_size // 2:
                end = para_break + 2
            else:
                # Look for sentence break
                sent_break = max(
                    text.rfind('. ', start, end),
                    text.rfind('.\n', start, end),
                    text.rfind('? ', start, end),
                    text.rfind('! ', start, end)
                )
                if sent_break > start + max_size // 2:
                    end = sent_break + 2
        
        chunks.append(text[start:end].strip())
        start = end - overlap
    
    return [c for c in chunks if c]  # Remove empty chunks


def extract_title(content: str, filepath: str) -> str:
    """Extract title from markdown content or use filename."""
    # Look for # header
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    # Fall back to filename
    return Path(filepath).stem.replace('_', ' ').replace('-', ' ').title()


def detect_topics(content: str, filepath: str) -> str:
    """Detect topics based on content and path."""
    topics = set()
    
    content_lower = content.lower()
    path_lower = filepath.lower()
    
    # Topic detection rules
    if any(x in content_lower for x in ['chromadb', 'rag', 'embedding', 'vector']):
        topics.add('database')
    if any(x in content_lower for x in ['docker', 'container', 'compose']):
        topics.add('infrastructure')
    if any(x in content_lower for x in ['api', 'endpoint', 'flask', 'backend']):
        topics.add('api')
    if any(x in content_lower for x in ['audio', 'mastering', 'daw', 'luna']):
        topics.add('audio')
    if any(x in content_lower for x in ['ollama', 'llm', 'model', 'ai', 'faithh']):
        topics.add('ai')
    if any(x in content_lower for x in ['def ', 'class ', 'import ', 'function']):
        topics.add('code')
    if any(x in content_lower for x in ['constella', 'governance', 'token', 'civic']):
        topics.add('governance')
    if any(x in content_lower for x in ['harmony', 'resonance', 'equilibrium']):
        topics.add('philosophy')
    if 'life_map' in path_lower or 'roadmap' in path_lower:
        topics.add('planning')
    if 'parity' in path_lower or 'architecture' in path_lower:
        topics.add('documentation')
    
    return ','.join(sorted(topics)) if topics else 'general'


def has_code(content: str) -> bool:
    """Check if content contains code blocks."""
    return '```' in content or bool(re.search(r'^\s{4,}\S', content, re.MULTILINE))


def generate_doc_id(filepath: str, chunk_index: int) -> str:
    """Generate a unique document ID."""
    path_hash = hashlib.md5(filepath.encode()).hexdigest()[:12]
    return f"doc_{path_hash}_{chunk_index}"


def collect_files(base_dir: str) -> List[str]:
    """Collect all markdown files from directory."""
    files = []
    for root, dirs, filenames in os.walk(base_dir):
        # Skip certain directories
        dirs[:] = [d for d in dirs if not should_skip(os.path.join(root, d))]
        
        for filename in filenames:
            if filename.endswith('.md'):
                filepath = os.path.join(root, filename)
                if not should_skip(filepath):
                    files.append(filepath)
    return files


def process_file(filepath: str, project: str) -> List[Dict]:
    """Process a single file into chunks with metadata."""
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
    has_code_flag = has_code(content)
    chunks = chunk_text(content)
    
    # Get file modification time
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
                'source': 'documentation',
                'title': title,
                'project': project,
                'topics': topics,
                'has_code': has_code_flag,
                'chunk_index': i,
                'total_chunks': len(chunks),
                'filepath': filepath,
                'created_at': mtime,
                'indexed_at': datetime.now().isoformat(),
            }
        })
    
    return documents


def main():
    """Main indexing function."""
    print("=" * 60)
    print("FAITHH Documentation Indexer → Gen 8 ChromaDB")
    print("=" * 60)
    
    # Load embedding model
    print(f"\n📦 Loading embedding model: {EMBEDDING_MODEL}")
    print("   (This may take a minute on first run...)")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("   ✅ Model loaded")
    
    # Connect to Gen 8 ChromaDB
    print(f"\n🔌 Connecting to Gen 8 ChromaDB at {GEN8_CHROMA_HOST}:{GEN8_CHROMA_PORT}")
    try:
        client = chromadb.HttpClient(
            host=GEN8_CHROMA_HOST,
            port=GEN8_CHROMA_PORT,
        )
        # Test connection
        client.heartbeat()
        print("   ✅ Connected")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return
    
    # Get existing collection
    print(f"\n📚 Accessing collection: {COLLECTION_NAME}")
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
        current_count = collection.count()
        print(f"   ✅ Collection found ({current_count} existing documents)")
    except Exception as e:
        print(f"   ❌ Collection not found: {e}")
        print("   Creating new collection...")
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "FAITHH Knowledge Base with BGE embeddings"}
        )
    
    # Collect all files
    print("\n📁 Collecting files to index...")
    all_documents = []
    
    for base_dir, project in DIRS_TO_INDEX:
        if not os.path.exists(base_dir):
            print(f"   ⚠️  Directory not found: {base_dir}")
            continue
            
        files = collect_files(base_dir)
        print(f"   {project}: {len(files)} files found in {base_dir}")
        
        for filepath in files:
            docs = process_file(filepath, project)
            all_documents.extend(docs)
    
    print(f"\n📄 Total chunks to index: {len(all_documents)}")
    
    if not all_documents:
        print("No documents to index!")
        return
    
    # Generate embeddings in batches
    print("\n🧮 Generating embeddings...")
    batch_size = 32
    
    for i in range(0, len(all_documents), batch_size):
        batch = all_documents[i:i + batch_size]
        batch_texts = [doc['content'] for doc in batch]
        
        # Generate embeddings
        embeddings = model.encode(batch_texts, show_progress_bar=False)
        
        # Prepare for ChromaDB
        ids = [doc['id'] for doc in batch]
        documents = [doc['content'] for doc in batch]
        metadatas = [doc['metadata'] for doc in batch]
        
        # Upsert to collection
        try:
            collection.upsert(
                ids=ids,
                embeddings=embeddings.tolist(),
                documents=documents,
                metadatas=metadatas,
            )
        except Exception as e:
            print(f"   ❌ Error upserting batch {i//batch_size + 1}: {e}")
            continue
        
        progress = min(i + batch_size, len(all_documents))
        print(f"   Progress: {progress}/{len(all_documents)} ({100*progress//len(all_documents)}%)")
    
    # Verify
    final_count = collection.count()
    print(f"\n✅ Indexing complete!")
    print(f"   Documents in collection: {final_count}")
    print(f"   New documents added: {final_count - current_count}")
    
    # Summary by project
    print("\n📊 Summary by source:")
    for base_dir, project in DIRS_TO_INDEX:
        project_docs = [d for d in all_documents if d['metadata']['project'] == project]
        print(f"   {project}: {len(project_docs)} chunks")


if __name__ == "__main__":
    main()

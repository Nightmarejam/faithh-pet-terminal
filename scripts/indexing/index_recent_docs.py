#!/usr/bin/env python3
"""
Index Recent FAITHH Documentation into ChromaDB
Adds recent markdown files and code to the documents_768 collection
"""

import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
from datetime import datetime, timedelta
import hashlib

# Configuration
CHROMA_HOST = "localhost"
CHROMA_PORT = 8000
COLLECTION_NAME = "documents_768"
AI_STACK_DIR = Path.home() / "ai-stack"

# Categories to index
INDEX_PATHS = [
    "docs/*.md",
    "docs/**/*.md",
    "*.md",          # Root level only — CONTEXT.md, AGENTS.md, README.md etc.
    "DEPS.md",
    "SYSTEMS_MAP.md",
]

# Files to skip
SKIP_PATTERNS = [
    ".backup",
    ".broken",
    "node_modules",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    # Source code — should not be indexed as knowledge
    ".py",
    ".pyc",
    ".sh",
    ".bat",
    ".ps1",
    # UI/frontend — CSS/JS/HTML is not knowledge
    ".html",
    ".css",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    # Binary and build artifacts
    ".png",
    ".jpg",
    ".gif",
    ".ico",
    ".woff",
    ".ttf",
    ".lock",
    ".bin",
    # Config and secrets
    ".env",
    ".env.local",
    "keyring.json",
    # Large generated files
    "ml/output",
    "ml/grounding_finetune",
    "collectors/state",
    "collectors/daily",
    "archive/",
    "uploads/",
    "logs/",
]

def should_skip(filepath):
    """Check if file should be skipped"""
    filepath_str = str(filepath)
    return any(pattern in filepath_str for pattern in SKIP_PATTERNS)

def get_file_hash(filepath):
    """Get MD5 hash of file for deduplication"""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def get_file_metadata(filepath):
    """Extract metadata from file"""
    stat = filepath.stat()
    rel_path = filepath.relative_to(AI_STACK_DIR)
    
    # Determine category
    if 'docs/' in str(rel_path):
        category = 'documentation'
    elif 'parity/' in str(rel_path):
        category = 'parity_file'
    elif filepath.suffix == '.py':
        category = 'backend_code'
    elif filepath.suffix == '.html':
        category = 'frontend_ui'
    elif filepath.suffix == '.md':
        category = 'markdown_doc'
    else:
        category = 'other'
    
    return {
        'source': str(rel_path),
        'category': category,
        'file_type': filepath.suffix,
        'size': stat.st_size,
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'hash': get_file_hash(filepath)
    }

def read_file_content(filepath):
    """Read file content safely"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add header with file info
        rel_path = filepath.relative_to(AI_STACK_DIR)
        header = f"# FILE: {rel_path}\n# TYPE: {filepath.suffix}\n\n"
        
        return header + content
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def main():
    print("=" * 60)
    print("FAITHH DOCUMENTATION INDEXER")
    print("=" * 60)
    
    # Connect to ChromaDB
    print(f"\n1. Connecting to ChromaDB at {CHROMA_HOST}:{CHROMA_PORT}...")
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    
    # Get collection with correct embedding function
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-mpnet-base-v2"
    )
    
    collection = client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_func
    )
    
    print(f"✅ Connected to collection '{COLLECTION_NAME}'")
    print(f"   Current documents: {collection.count()}")
    
    # Collect files to index
    print(f"\n2. Scanning for files in {AI_STACK_DIR}...")
    files_to_index = []
    
    for pattern in INDEX_PATHS:
        for filepath in AI_STACK_DIR.glob(pattern):
            if filepath.is_file() and not should_skip(filepath):
                files_to_index.append(filepath)
    
    # Remove duplicates
    files_to_index = list(set(files_to_index))
    print(f"✅ Found {len(files_to_index)} files to index")
    
    # Index files in batches
    print(f"\n3. Indexing files...")
    batch_size = 10
    indexed = 0
    skipped = 0
    errors = 0
    
    for i in range(0, len(files_to_index), batch_size):
        batch = files_to_index[i:i+batch_size]
        
        ids = []
        documents = []
        metadatas = []
        
        for filepath in batch:
            # Read content
            content = read_file_content(filepath)
            if not content:
                errors += 1
                continue
            
            # Get metadata
            metadata = get_file_metadata(filepath)
            
            # Create unique ID from hash
            doc_id = f"faithh_{metadata['hash'][:16]}"
            
            # Check if already indexed (by hash)
            try:
                existing = collection.get(
                    ids=[doc_id],
                    include=[]
                )
                if existing['ids']:
                    skipped += 1
                    continue
            except:
                pass
            
            ids.append(doc_id)
            documents.append(content)
            metadatas.append(metadata)
        
        # Add batch to collection
        if ids:
            try:
                collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
                indexed += len(ids)
                print(f"   Indexed batch {i//batch_size + 1}: {len(ids)} documents")
            except Exception as e:
                print(f"   Error indexing batch: {e}")
                errors += len(ids)
    
    print(f"\n4. Indexing complete!")
    print(f"   ✅ Indexed: {indexed} new documents")
    print(f"   ⏭️  Skipped: {skipped} (already indexed)")
    print(f"   ❌ Errors:  {errors}")
    print(f"   📊 Total in collection: {collection.count()}")
    
    # Test query
    print(f"\n5. Testing indexed documents...")
    test_query = "FAITHH professional backend system"
    results = collection.query(
        query_texts=[test_query],
        n_results=3
    )
    
    if results['documents'] and results['documents'][0]:
        print(f"✅ Test query successful!")
        print(f"   Query: '{test_query}'")
        try:
            if results['metadatas'] and results['metadatas'][0]:
                meta = results['metadatas'][0][0]
                source = meta.get('source', meta.get('filename', 'unknown'))
                print(f"   Top result: {source}")
        except (IndexError, KeyError):
            print(f"   Top result: (metadata unavailable)")
    else:
        print(f"⚠️  Test query returned no results")
    
    print("\n" + "=" * 60)
    print("INDEXING COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()

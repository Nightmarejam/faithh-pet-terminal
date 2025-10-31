#!/usr/bin/env python3
"""
Index all your text files into ChromaDB for RAG
"""

import chromadb
from pathlib import Path
import requests
from tqdm import tqdm
import time

# Configuration
OLLAMA_EMBED_URL = "http://localhost:11435"  # Your nomic-embed server
CHROMA_PATH = Path.home() / "ai-stack"
TEXT_DIRS = [
    Path.home() / "ai-stack" / "chatgpt_texts",
    Path.home() / "ai-stack" / "claude_texts",
    Path.home() / "ai-stack" / "grok_texts"
]

def get_embedding(text: str):
    """Generate embedding using nomic-embed via Ollama"""
    try:
        response = requests.post(
            f"{OLLAMA_EMBED_URL}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text},
            timeout=30
        )
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        print(f"⚠️  Embedding error: {e}")
        return None

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > chunk_size * 0.5:  # Only if we found a good break point
                chunk = chunk[:break_point + 1]
                end = start + break_point + 1
        
        chunks.append(chunk.strip())
        start = end - overlap  # Overlap for context
    
    return chunks

def index_documents():
    """Index all text files into ChromaDB"""
    
    print("🚀 Starting document indexing...\n")
    
    # Check if Ollama is running
    try:
        response = requests.get(f"{OLLAMA_EMBED_URL}/api/tags", timeout=5)
        print("✅ Connected to Ollama for embeddings\n")
    except:
        print("❌ Cannot connect to Ollama!")
        print("   Start it with: ollama serve")
        print("   Or check if it's running on port 11435")
        return
    
    # Initialize ChromaDB
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    
    # Create collection (or get if exists)
    try:
        collection = client.get_collection("documents")
        print("📚 Using existing 'documents' collection")
        print(f"   Current count: {collection.count()}\n")
    except:
        collection = client.create_collection(
            name="documents",
            metadata={"description": "AI conversation documents for RAG"}
        )
        print("📚 Created new 'documents' collection\n")
    
    # Collect all text files
    all_files = []
    for text_dir in TEXT_DIRS:
        if text_dir.exists():
            files = list(text_dir.glob("*.txt"))
            all_files.extend(files)
            print(f"  Found {len(files)} files in {text_dir.name}")
    
    if not all_files:
        print("\n❌ No text files found to index!")
        return
    
    print(f"\n📄 Total files to process: {len(all_files)}\n")
    
    # Process each file
    total_chunks = 0
    batch_ids = []
    batch_embeddings = []
    batch_documents = []
    batch_metadatas = []
    batch_size = 50  # Process in batches to avoid memory issues
    
    for file_path in tqdm(all_files, desc="Processing files"):
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                continue
            
            # Chunk the document
            chunks = chunk_text(content)
            
            # Process each chunk
            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue
                
                # Generate embedding
                embedding = get_embedding(chunk)
                if embedding is None:
                    continue
                
                # Prepare batch data
                doc_id = f"{file_path.stem}_{i}"
                batch_ids.append(doc_id)
                batch_embeddings.append(embedding)
                batch_documents.append(chunk)
                batch_metadatas.append({
                    "filename": file_path.name,
                    "source": file_path.parent.name,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })
                
                total_chunks += 1
                
                # Insert batch if full
                if len(batch_ids) >= batch_size:
                    collection.add(
                        ids=batch_ids,
                        embeddings=batch_embeddings,
                        documents=batch_documents,
                        metadatas=batch_metadatas
                    )
                    batch_ids = []
                    batch_embeddings = []
                    batch_documents = []
                    batch_metadatas = []
                    time.sleep(0.1)  # Brief pause to avoid overwhelming the server
        
        except Exception as e:
            print(f"\n⚠️  Error processing {file_path.name}: {e}")
            continue
    
    # Insert remaining batch
    if batch_ids:
        collection.add(
            ids=batch_ids,
            embeddings=batch_embeddings,
            documents=batch_documents,
            metadatas=batch_metadatas
        )
    
    # Final stats
    final_count = collection.count()
    print(f"\n\n✅ Indexing complete!")
    print(f"   📊 Total chunks indexed: {final_count}")
    print(f"   📁 Files processed: {len(all_files)}")
    print(f"   💾 Database location: {CHROMA_PATH}/chroma.sqlite3")
    
    # Test search
    print("\n🔍 Testing search...")
    try:
        results = collection.query(
            query_texts=["What is FAITHH?"],
            n_results=3
        )
        
        if results['documents'][0]:
            print(f"✅ Search works! Found {len(results['documents'][0])} results")
            print("\nTop result preview:")
            print(f"   {results['documents'][0][0][:200]}...")
        else:
            print("⚠️  No results found (database might be empty)")
    
    except Exception as e:
        print(f"⚠️  Search test failed: {e}")
    
    print("\n💡 Next steps:")
    print("   1. Your RAG API can now use this ChromaDB")
    print("   2. Start the API: python rag_api.py")
    print("   3. Open faithh_pet_v3.html in browser")
    print("   4. Toggle RAG mode and test queries!")

if __name__ == "__main__":
    index_documents()
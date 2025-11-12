#!/usr/bin/env python3
"""
Simple indexer using ChromaDB's built-in Ollama embedding function
No manual API calls - ChromaDB handles everything!
"""

import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from pathlib import Path
from tqdm import tqdm

# Configuration
CHROMA_PATH = Path.home() / "ai-stack"
TEXT_DIRS = [
    Path.home() / "ai-stack" / "chatgpt_texts",
    Path.home() / "ai-stack" / "claude_texts",
    Path.home() / "ai-stack" / "grok_texts"
]

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
            if last_period > chunk_size * 0.5:
                chunk = chunk[:last_period + 1]
                end = start + last_period + 1
        
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    
    return chunks

def index_documents():
    """Index all text files - ChromaDB handles embeddings automatically"""
    
    print("🚀 Starting simple document indexing...\n")
    
    # Initialize ChromaDB with Ollama embedding function
    ollama_ef = OllamaEmbeddingFunction(
        url="http://localhost:11435/api/embeddings",
        model_name="nomic-embed"
    )
    
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    
    # Create or get collection with embedding function
    try:
        client.delete_collection("documents")
        print("🗑️  Deleted old collection\n")
    except:
        pass
    
    collection = client.create_collection(
        name="documents",
        embedding_function=ollama_ef,
        metadata={"description": "AI conversation documents"}
    )
    
    print("📚 Created collection with Ollama embeddings\n")
    
    # Collect all text files
    all_files = []
    for text_dir in TEXT_DIRS:
        if text_dir.exists():
            files = list(text_dir.glob("*.txt"))
            all_files.extend(files)
            print(f"  Found {len(files)} files in {text_dir.name}")
    
    if not all_files:
        print("\n❌ No text files found!")
        return
    
    print(f"\n📄 Total files: {len(all_files)}\n")
    
    # Process in batches
    batch_ids = []
    batch_documents = []
    batch_metadatas = []
    batch_size = 50
    
    for file_path in tqdm(all_files, desc="Processing files"):
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                continue
            
            # Chunk the document
            chunks = chunk_text(content)
            
            # Add to batch
            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue
                
                batch_ids.append(f"{file_path.stem}_{i}")
                batch_documents.append(chunk)
                batch_metadatas.append({
                    "filename": file_path.name,
                    "source": file_path.parent.name,
                    "chunk_index": i
                })
                
                # Insert batch when full
                if len(batch_ids) >= batch_size:
                    collection.add(
                        ids=batch_ids,
                        documents=batch_documents,  # ChromaDB auto-embeds these!
                        metadatas=batch_metadatas
                    )
                    batch_ids = []
                    batch_documents = []
                    batch_metadatas = []
        
        except Exception as e:
            print(f"\n⚠️  Error with {file_path.name}: {e}")
            continue
    
    # Insert remaining
    if batch_ids:
        collection.add(
            ids=batch_ids,
            documents=batch_documents,
            metadatas=batch_metadatas
        )
    
    # Final stats
    final_count = collection.count()
    print(f"\n\n✅ Indexing complete!")
    print(f"   📊 Total chunks: {final_count}")
    print(f"   📁 Files processed: {len(all_files)}")
    
    # Test search
    print("\n🔍 Testing search...")
    try:
        results = collection.query(
            query_texts=["What is FAITHH?"],
            n_results=2
        )
        
        if results['documents'][0]:
            print(f"✅ Search works! Found {len(results['documents'][0])} results\n")
            print("Top result preview:")
            print(f"   {results['documents'][0][0][:200]}...\n")
        else:
            print("⚠️  No results (might need more documents)")
    
    except Exception as e:
        print(f"⚠️  Search test failed: {e}")
    
    print("\n💡 Next: Update rag_api.py and start using your RAG system!")

if __name__ == "__main__":
    index_documents()
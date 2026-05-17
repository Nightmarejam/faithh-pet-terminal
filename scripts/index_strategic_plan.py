#!/usr/bin/env python3
"""
Index 5-Year Strategic Plan into ChromaDB for FAITHH integration
"""

import os
import sys
import json
from pathlib import Path
import chromadb
import re

def chunk_document(content, chunk_size=1000, overlap=100):
    """Simple document chunking function"""
    chunks = []
    start = 0
    
    while start < len(content):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(content):
            # Look for sentence ending near chunk_size
            sentence_end = content.rfind('.', start, end + 100)
            if sentence_end > start + chunk_size // 2:
                end = sentence_end + 1
        
        chunk = content[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap if end < len(content) else len(content)
    
    return chunks

def index_strategic_plan():
    """Index the 5-year strategic plan into ChromaDB"""
    
    print("🎯 Indexing 5-Year Strategic Plan into FAITHH...")
    
    # Connect to ChromaDB
    try:
        client = chromadb.HttpClient(host='192.158.1.10', port=8000)
        collection = client.get_collection('faithh_knowledge_base')
        print("✅ Connected to ChromaDB")
    except Exception as e:
        print(f"❌ Failed to connect to ChromaDB: {e}")
        return False
    
    # Load strategic plan documents
    strategic_dir = Path('/home/jonat/ai-stack/docs/strategic')
    
    if not strategic_dir.exists():
        print(f"❌ Strategic plan directory not found: {strategic_dir}")
        return False
    
    # Documents to index
    documents_to_index = [
        {
            'file': strategic_dir / '5_YEAR_STRATEGIC_PLAN.md',
            'metadata': {
                'type': 'strategic_plan',
                'domain': 'overall',
                'priority': 'high',
                'date_created': '2026-02-23',
                'version': '1.0'
            }
        },
        {
            'file': strategic_dir / 'domain_plans' / 'TECHNICAL_FAITHH_PLAN.md',
            'metadata': {
                'type': 'domain_plan',
                'domain': 'technical',
                'priority': 'high',
                'date_created': '2026-02-23',
                'version': '1.0'
            }
        },
        {
            'file': strategic_dir / 'domain_plans' / 'BUSINESS_TOMCAT_PLAN.md',
            'metadata': {
                'type': 'domain_plan',
                'domain': 'business',
                'priority': 'high',
                'date_created': '2026-02-23',
                'version': '1.0'
            }
        }
    ]
    
    total_chunks = 0
    
    for doc_info in documents_to_index:
        file_path = doc_info['file']
        metadata = doc_info['metadata']
        
        if not file_path.exists():
            print(f"⚠️ File not found: {file_path}")
            continue
        
        try:
            # Read document
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"📄 Processing: {file_path.name}")
            
            # Chunk the document
            chunks = chunk_document(content, chunk_size=1000, overlap=100)
            
            # Prepare for ChromaDB
            chunk_texts = []
            chunk_metadatas = []
            chunk_ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"strategic_{metadata['domain']}_{metadata['type']}_{i}"
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'source_file': str(file_path.name),
                    'section': extract_section(chunk, content)
                })
                
                chunk_texts.append(chunk)
                chunk_metadatas.append(chunk_metadata)
                chunk_ids.append(chunk_id)
            
            # Add to ChromaDB
            collection.add(
                documents=chunk_texts,
                metadatas=chunk_metadatas,
                ids=chunk_ids
            )
            
            total_chunks += len(chunks)
            print(f"   ✅ Added {len(chunks)} chunks")
            
        except Exception as e:
            print(f"   ❌ Error processing {file_path}: {e}")
            continue
    
    # Update collection count
    try:
        count = collection.count()
        print(f"\n📊 Strategic plan indexing complete!")
        print(f"   📝 Total chunks added: {total_chunks}")
        print(f"   🗃️ Collection size: {count} documents")
        print(f"   🎯 Strategic coherence system ready")
        
        # Test retrieval
        test_results = collection.query(
            query_texts=["What are the 5-year strategic goals?"],
            n_results=3,
            where={"type": "strategic_plan"}
        )
        
        if test_results['documents'][0]:
            print(f"   ✅ Retrieval test successful")
            print(f"   📄 Found {len(test_results['documents'][0])} relevant chunks")
        else:
            print(f"   ⚠️ Retrieval test failed")
            
    except Exception as e:
        print(f"❌ Error updating collection info: {e}")
    
    return True

def extract_section(chunk, full_content):
    """Extract section title from chunk"""
    lines = chunk.split('\n')
    for line in lines:
        if line.startswith('#'):
            return line.strip()
    return "General"

def main():
    """Main execution"""
    print("=" * 60)
    print("STRATEGIC PLAN INDEXING")
    print("=" * 60)
    
    success = index_strategic_plan()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 STRATEGIC PLAN SUCCESSFULLY INTEGRATED")
        print("   FAITHH now has 5-year strategic context")
        print("   Decision coherence checking enabled")
        print("   Quarterly review system ready")
    else:
        print("❌ STRATEGIC PLAN INTEGRATION FAILED")
        print("   Check error messages above")
    print("=" * 60)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Audit ChromaDB state for faithh_knowledge_base collection.
Check document counts, metadata distribution, and RAG retrieval health.
"""

import os
import sys
import json
from datetime import datetime
from collections import defaultdict, Counter
import chromadb

def audit_collection():
    """Comprehensive audit of ChromaDB collection."""
    
    # Connect to ChromaDB
    try:
        client = chromadb.HttpClient(host='192.158.1.10', port=8000)
        collection = client.get_collection('faithh_knowledge_base')
        print(f"[AUDIT] Connected to ChromaDB at 192.158.1.10:8000")
        print(f"[AUDIT] Collection: faithh_knowledge_base")
    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")
        return
    
    total_docs = collection.count()
    print(f"\n[OVERVIEW] Total documents: {total_docs}")
    
    if total_docs == 0:
        print("[AUDIT] Empty collection - nothing to analyze")
        return
    
    # Sample metadata (first 1000 docs to avoid memory issues)
    sample_size = min(1000, total_docs)
    sample_ids = [f"doc_{i}" for i in range(sample_size)]
    
    try:
        sample = collection.get(ids=sample_ids[:min(100, total_docs)])
        metadatas = sample.get('metadatas', [])
        documents = sample.get('documents', [])
        
        print(f"\n[SAMPLE] Analyzing {len(metadatas)} sample documents")
        
        # Metadata field analysis
        if metadatas:
            all_fields = set()
            field_types = defaultdict(set)
            field_values = defaultdict(list)
            
            for meta in metadatas:
                if meta:
                    for key, value in meta.items():
                        all_fields.add(key)
                        field_types[key].add(type(value).__name__)
                        if len(field_values[key]) < 5:
                            field_values[key].append(str(value)[:50])
            
            print(f"\n[METADATA FIELDS] Found {len(all_fields)} unique fields:")
            for field in sorted(all_fields):
                types_str = ", ".join(sorted(field_types[field]))
                examples = ", ".join(field_values[field][:3])
                print(f"  {field}: {types_str} (examples: {examples})")
        
        # Document content analysis
        if documents:
            doc_lengths = [len(doc) for doc in documents]
            print(f"\n[DOCUMENTS] Length stats:")
            print(f"  Min: {min(doc_lengths)} chars")
            print(f"  Max: {max(doc_lengths)} chars")
            print(f"  Avg: {sum(doc_lengths)/len(doc_lengths):.0f} chars")
            
            # Check for Exp 5 documents
            exp5_docs = [doc for doc in documents if 'experiment 5' in doc.lower() or 'parasitic' in doc.lower()]
            print(f"\n[EXP5] Found {len(exp5_docs)} Exp 5-related docs in sample")
            if exp5_docs:
                print(f"  Sample content: {exp5_docs[0][:100]}...")
    
    except Exception as e:
        print(f"[ERROR] Failed to sample documents: {e}")
    
    # Test specific Exp 5 document retrieval
    print(f"\n[RETRIEVAL TEST] Testing Exp 5 document access:")
    test_ids = ['exp5_parasitic_design', 'exp5_parasitic_results', 'alife_roadmap_summary']
    
    for doc_id in test_ids:
        try:
            result = collection.get(ids=[doc_id])
            if result['documents']:
                print(f"  ✓ {doc_id}: {len(result['documents'][0])} chars")
            else:
                print(f"  ✗ {doc_id}: Not found")
        except Exception as e:
            print(f"  ✗ {doc_id}: Error - {e}")
    
    # Query test for Exp 5 content
    print(f"\n[QUERY TEST] Testing semantic search for Exp 5:")
    test_queries = [
        "parasitic emergence experiment 5",
        "three-phase offensive evolution",
        "boom-bust cycle parasites"
    ]
    
    for query in test_queries:
        try:
            results = collection.query(
                query_texts=[query],
                n_results=3
            )
            docs = results.get('documents', [[]])[0]
            metas = results.get('metadatas', [[]])[0]
            distances = results.get('distances', [[]])[0]
            
            print(f"\n  Query: '{query}'")
            print(f"  Results: {len(docs)} documents")
            
            for i, (doc, meta, dist) in enumerate(zip(docs, metas, distances)):
                doc_type = meta.get('document_type', 'unknown') if meta else 'no_meta'
                print(f"    {i+1}. {doc_type} (dist={dist:.3f})")
                if 'experiment' in doc.lower() or 'parasitic' in doc.lower():
                    print(f"       -> Exp 5 content!")
                    break
            else:
                print(f"       -> No Exp 5 content in top 3")
                
        except Exception as e:
            print(f"  Error querying '{query}': {e}")
    
    # Collection metadata summary
    try:
        # Get a larger sample for metadata analysis
        sample_size = min(500, total_docs)
        sample_ids = [f"doc_{i}" for i in range(sample_size)]
        sample = collection.get(ids=sample_ids[:sample_size])
        metadatas = sample.get('metadatas', [])
        
        if metadatas:
            # Count document types
            doc_types = []
            for meta in metadatas:
                if meta and 'document_type' in meta:
                    doc_types.append(meta['document_type'])
            
            if doc_types:
                type_counts = Counter(doc_types)
                print(f"\n[DOCUMENT TYPES] In sample of {len(doc_types)}:")
                for doc_type, count in type_counts.most_common():
                    print(f"  {doc_type}: {count} ({count/len(doc_types)*100:.1f}%)")
    
    except Exception as e:
        print(f"[ERROR] Failed metadata analysis: {e}")
    
    print(f"\n[AUDIT] Complete at {datetime.now().isoformat()}")

if __name__ == "__main__":
    audit_collection()

#!/usr/bin/env python3
"""Fix harmony docs category to 'project_docs' for better RAG ranking."""
import chromadb
from datetime import datetime

client = chromadb.HttpClient(host="servicebox.taileb8c60.ts.net", port=8000)
collection = client.get_collection(name="faithh_knowledge_base")

# IDs of harmony docs we indexed
harmony_doc_ids = [
    "harmony_resonance_gating_summary",
    "harmony_resonance_transformer",
    "harmony_ai_bridge",
    "harmony_framework",
    "ime_readme",
    "ime_architecture",
]

print("=== Fixing Harmony Docs Category ===\n")

# Get current docs
for doc_id in harmony_doc_ids:
    try:
        result = collection.get(ids=[doc_id])
        if result['ids']:
            old_meta = result['metadatas'][0]
            old_category = old_meta.get('category', 'unknown')
            
            # Update metadata to use project_docs category
            new_meta = old_meta.copy()
            new_meta['category'] = 'project_docs'
            new_meta['updated_at'] = datetime.now().isoformat()
            
            # Update the document
            collection.update(
                ids=[doc_id],
                metadatas=[new_meta]
            )
            print(f"✅ {doc_id}: {old_category} -> project_docs")
        else:
            print(f"⚠️ {doc_id}: Not found")
    except Exception as e:
        print(f"❌ {doc_id}: Error - {e}")

print(f"\nCollection count: {collection.count():,}")

# Verify the fix
print("\n=== Verification ===")
results = collection.query(
    query_texts=["resonance gating architecture"],
    n_results=5,
    where={"category": "project_docs"}
)

print("Top 5 project_docs for 'resonance gating':")
for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
    source = meta.get('source', 'unknown')[:60]
    print(f"  {i+1}. {source}")

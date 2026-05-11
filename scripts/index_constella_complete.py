#!/usr/bin/env python3
"""
Complete Constella indexing with smart chunking for FAITHH RAG.
"""

import os
import json
import chromadb
from chromadb.utils import embedding_functions

CONSTELLA_REPO = "./constella-framework"

# High-value docs to index whole
SINGLE_DOCS = [
    {"path": "docs/reference/v1.5.4_HR1.md", "id": "constella_v1.5.4_hr1", "desc": "Token formulas, governance"},
    {"path": "docs/reference/Robustness_Pack_v1.3.md", "id": "constella_robustness_pack", "desc": "Evidence levels, safety"},
    {"path": "docs/reference/Framework_Master_v1.2.md", "id": "constella_framework_master", "desc": "Module definitions"},
    {"path": "docs/reference/README.md", "id": "constella_reference_index", "desc": "Quick reference"},
    {"path": "docs/governance/penumbra_accord.md", "id": "constella_penumbra", "desc": "Restorative justice"},
    {"path": "docs/governance/tokens_astris_auctor.md", "id": "constella_tokens", "desc": "Astris/Auctor mechanics"},
    {"path": "docs/governance/ucf.md", "id": "constella_ucf", "desc": "Universal Civic Floor"},
    {"path": "docs/governance/civic_tome.md", "id": "constella_tome", "desc": "Protocols, precedents"},
    {"path": "docs/doctrine/README.md", "id": "constella_doctrine", "desc": "Celestial Equilibrium"},
]

# Large docs to chunk
CHUNK_DOCS = [
    {"path": "docs/conversations/constella_conversations.md", "prefix": "constella_conv"},
    {"path": "docs/conversations/harmony_conversations.md", "prefix": "harmony_conv"},
    {"path": "docs/conversations/resonant_conversations.md", "prefix": "resonant_conv"},
]

def chunk_document(content, chunk_size=2500, overlap=250):
    """Split into overlapping chunks at natural breaks."""
    chunks = []
    start = 0
    while start < len(content):
        end = start + chunk_size
        chunk = content[start:end]
        if end < len(content):
            last_break = chunk.rfind('\n\n')
            if last_break > chunk_size // 2:
                end = start + last_break
                chunk = content[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    return chunks

def main():
    print("🌌 Constella Complete Indexer")
    print("=" * 60)
    
    if not os.path.exists(CONSTELLA_REPO):
        print(f"❌ Repo not found. Run: git clone https://github.com/Nightmarejam/constella-framework.git")
        return
    
    client = chromadb.HttpClient(host="localhost", port=8000)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")
    collection = client.get_collection(name="documents_768", embedding_function=ef)
    print(f"📂 Connected! Current docs: {collection.count()}")
    
    # Clear existing constella_master docs
    print("\n🧹 Clearing old Constella entries...")
    try:
        existing = collection.get(where={"category": "constella_master"}, limit=1000)
        if existing['ids']:
            collection.delete(ids=existing['ids'])
            print(f"   Removed {len(existing['ids'])} old docs")
    except:
        pass
    
    indexed = 0
    
    # Index single docs
    print("\n📚 Indexing reference & governance...")
    for doc in SINGLE_DOCS:
        path = os.path.join(CONSTELLA_REPO, doc["path"])
        if not os.path.exists(path):
            continue
        with open(path, 'r') as f:
            content = f.read()
        meta = {"source": "constella_master", "category": "constella_master", 
                "priority": "highest", "file": doc["path"], "description": doc["desc"]}
        try:
            collection.add(documents=[content], metadatas=[meta], ids=[doc["id"]])
            print(f"   ✅ {doc['path'].split('/')[-1]}")
            indexed += 1
        except Exception as e:
            print(f"   ❌ {doc['id']}: {e}")
    
    # Index JSON sections
    json_path = os.path.join(CONSTELLA_REPO, "docs/reference/data/framework_v1.3.json")
    if os.path.exists(json_path):
        print("\n📦 Indexing JSON sections...")
        with open(json_path) as f:
            data = json.load(f)
        sections = [
            ("token_mechanics", data.get("robustness_pack", {}).get("token_mechanics", {})),
            ("evidence_levels", data.get("robustness_pack", {}).get("evidence_levels", {})),
            ("safety_ethics", data.get("robustness_pack", {}).get("safety_ethics", {})),
            ("glossary", data.get("glossary", {})),
        ]
        for name, content in sections:
            if content:
                doc = f"# {name}\n\n{json.dumps(content, indent=2)}"
                meta = {"source": "constella_master", "category": "constella_master", "priority": "highest"}
                try:
                    collection.add(documents=[doc], metadatas=[meta], ids=[f"constella_json_{name}"])
                    print(f"   ✅ {name}")
                    indexed += 1
                except:
                    pass
    
    # Index chunked conversations
    print("\n💬 Indexing conversations (chunked)...")
    for doc in CHUNK_DOCS:
        path = os.path.join(CONSTELLA_REPO, doc["path"])
        if not os.path.exists(path):
            continue
        with open(path, 'r') as f:
            content = f.read()
        chunks = chunk_document(content)
        print(f"   📄 {doc['path'].split('/')[-1]}: {len(chunks)} chunks")
        for i, chunk in enumerate(chunks):
            meta = {"source": "constella_conversation", "category": "constella_master", "priority": "high"}
            try:
                collection.add(documents=[chunk], metadatas=[meta], ids=[f"{doc['prefix']}_{i:04d}"])
                indexed += 1
            except:
                pass
    
    print("\n" + "=" * 60)
    print(f"✅ Indexed {indexed} Constella documents")
    print(f"📊 Total in collection: {collection.count()}")

if __name__ == "__main__":
    main()

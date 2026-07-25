#!/usr/bin/env python3
"""
Fix ChromaDB metadata for Constella documents.
Updates domain to 'constella' for any document that contains Constella-specific terms.
Uses batch upsert to avoid WSL crash (no sentence_transformers import).
"""
import chromadb
import time

CHROMADB_HOST = "servicebox.taileb8c60.ts.net"
CHROMADB_PORT = 8000
COLLECTION_NAME = "faithh_knowledge_base"

CONSTELLA_TERMS = [
    "Astris", "Auctor", "Penumbra Accord", "Universal Civic Floor",
    "Civic Tome", "Constella", "celestial equilibrium", "Genesis Pool",
    "civic voice", "soul-bound", "penumbra", "auctor", "astris",
    "constella framework", "token decay", "civic floor"
]

def is_constella_doc(text, metadata):
    text_lower = text.lower()
    for term in CONSTELLA_TERMS:
        if term.lower() in text_lower:
            return True
    if metadata.get("source_type") == "constella":
        return True
    if metadata.get("suggested_collection") == "constella":
        return True
    return False

def main():
    client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
    collection = client.get_collection(COLLECTION_NAME)
    
    total = collection.count()
    print(f"Total documents: {total}")
    print("Scanning for Constella documents...\n")
    
    batch_size = 500
    offset = 0
    constella_ids = []
    constella_docs = []
    constella_embeddings = []
    constella_metadatas = []
    
    while offset < total:
        batch = collection.get(
            limit=batch_size,
            offset=offset,
            include=["documents", "metadatas", "embeddings"]
        )
        
        ids = batch["ids"]
        docs = batch["documents"]
        metas = batch["metadatas"]
        embeddings = batch["embeddings"]
        
        for i, (doc_id, doc, meta, emb) in enumerate(zip(ids, docs, metas, embeddings)):
            if is_constella_doc(doc, meta):
                if meta.get("domain") != "constella":
                    new_meta = dict(meta)
                    new_meta["domain"] = "constella"
                    new_meta["source_type"] = new_meta.get("source_type") or "constella_doc"
                    constella_ids.append(doc_id)
                    constella_docs.append(doc)
                    constella_metadatas.append(new_meta)
                    constella_embeddings.append(emb)
        
        offset += batch_size
        print(f"  Scanned {min(offset, total)}/{total} | Constella found so far: {len(constella_ids)}")
    
    print(f"\nDocuments needing metadata update: {len(constella_ids)}")
    
    if not constella_ids:
        print("Nothing to update.")
        return
    
    print("\nApplying updates in batches of 100...")
    update_batch = 100
    updated = 0
    for i in range(0, len(constella_ids), update_batch):
        batch_ids = constella_ids[i:i+update_batch]
        batch_docs = constella_docs[i:i+update_batch]
        batch_metas = constella_metadatas[i:i+update_batch]
        batch_embs = constella_embeddings[i:i+update_batch]
        
        collection.upsert(
            ids=batch_ids,
            documents=batch_docs,
            metadatas=batch_metas,
            embeddings=batch_embs
        )
        updated += len(batch_ids)
        print(f"  Updated {updated}/{len(constella_ids)}")
        time.sleep(0.1)
    
    print(f"\nDone. {updated} documents updated to domain=constella.")
    
    # Verify
    print("\nVerifying — querying for Astris token...")
    verify = collection.query(
        query_texts=["Astris soul-bound merit token decay"],
        n_results=5,
        include=["metadatas", "documents"]
    )
    for meta, doc in zip(verify["metadatas"][0], verify["documents"][0]):
        print(f"  domain={meta.get('domain')} | {doc[:80]}...")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Deep analysis of Gen8 ChromaDB - sample from different offsets"""
import requests
from collections import Counter
import json

GEN8_URL = "http://100.79.85.32:8000"
COLLECTION_ID = "71e13a01-cbb6-48ba-a126-2a16320d40c0"

def get_sample_with_offset(limit=100, offset=0):
    """Get documents with offset"""
    url = f"{GEN8_URL}/api/v2/tenants/default_tenant/databases/default_database/collections/{COLLECTION_ID}/get"
    resp = requests.post(url, json={
        "limit": limit,
        "offset": offset,
        "include": ["metadatas", "documents"]
    }, timeout=30)
    return resp.json()

def get_count():
    url = f"{GEN8_URL}/api/v2/tenants/default_tenant/databases/default_database/collections/{COLLECTION_ID}/count"
    resp = requests.get(url, timeout=10)
    return resp.json()

if __name__ == "__main__":
    print("=" * 60)
    print("GEN8 CHROMADB DEEP ANALYSIS")
    print("=" * 60)
    
    count = get_count()
    print(f"\n📊 Total Documents: {count}")
    
    # Sample from different parts of the database
    all_sources = Counter()
    all_categories = Counter()
    all_types = Counter()
    all_providers = Counter()
    all_titles = set()
    sample_docs = []
    
    offsets = [0, 5000, 10000, 15000, 20000, 25000]
    
    for offset in offsets:
        if offset >= count:
            break
        print(f"\n⏳ Sampling at offset {offset}...")
        data = get_sample_with_offset(100, offset)
        metas = data.get("metadatas", [])
        docs = data.get("documents", [])
        
        for i, m in enumerate(metas):
            if not m:
                continue
            all_sources[m.get("source", "unknown")] += 1
            all_categories[m.get("category", "unknown")] += 1
            all_types[m.get("type", "unknown")] += 1
            all_providers[m.get("provider", "unknown")] += 1
            if m.get("title"):
                all_titles.add(m["title"])
            
            # Capture sample doc content
            if len(sample_docs) < 5 and docs and i < len(docs):
                sample_docs.append({
                    "source": m.get("source"),
                    "title": m.get("title", "")[:50],
                    "preview": docs[i][:200] if docs[i] else ""
                })
    
    print("\n" + "=" * 60)
    print("AGGREGATED RESULTS")
    print("=" * 60)
    
    print(f"\n📄 SOURCES (from ~{len(offsets)*100} samples):")
    for src, cnt in sorted(all_sources.items(), key=lambda x: -x[1]):
        pct = (cnt / sum(all_sources.values())) * 100
        est_total = int((cnt / sum(all_sources.values())) * count)
        print(f"   {src}: {cnt} samples (~{est_total} estimated total, {pct:.1f}%)")
    
    print(f"\n📂 CATEGORIES:")
    for cat, cnt in sorted(all_categories.items(), key=lambda x: -x[1]):
        print(f"   {cat}: {cnt}")
    
    print(f"\n🤖 PROVIDERS:")
    for p, cnt in sorted(all_providers.items(), key=lambda x: -x[1]):
        print(f"   {p}: {cnt}")
    
    print(f"\n📚 UNIQUE CONVERSATION TITLES: {len(all_titles)}")
    print("   Sample titles:")
    for title in list(all_titles)[:10]:
        print(f"   - {title[:60]}...")
    
    print(f"\n📝 SAMPLE DOCUMENT CONTENT:")
    for i, doc in enumerate(sample_docs[:3]):
        print(f"\n   [{i+1}] Source: {doc['source']}, Title: {doc['title']}")
        print(f"       Preview: {doc['preview'][:150]}...")
    
    print("\n" + "=" * 60)

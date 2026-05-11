#!/usr/bin/env python3
"""Analyze Gen8 ChromaDB contents"""
import requests
from collections import Counter
import json

GEN8_URL = "http://100.79.85.32:8000"
COLLECTION_ID = "71e13a01-cbb6-48ba-a126-2a16320d40c0"

def get_sample(limit=100):
    """Get a sample of documents with metadata"""
    url = f"{GEN8_URL}/api/v2/tenants/default_tenant/databases/default_database/collections/{COLLECTION_ID}/get"
    resp = requests.post(url, json={
        "limit": limit,
        "include": ["metadatas"]
    }, timeout=30)
    return resp.json()

def get_count():
    """Get total document count"""
    url = f"{GEN8_URL}/api/v2/tenants/default_tenant/databases/default_database/collections/{COLLECTION_ID}/count"
    resp = requests.get(url, timeout=10)
    return resp.json()

def analyze_metadata(metas):
    """Analyze metadata fields"""
    fields = Counter()
    categories = Counter()
    sources = Counter()
    types = Counter()
    providers = Counter()
    filepaths = []
    
    for m in metas:
        if not m:
            continue
        for key in m.keys():
            fields[key] += 1
        categories[m.get("category", "unknown")] += 1
        sources[m.get("source", "unknown")] += 1
        types[m.get("type", "unknown")] += 1
        providers[m.get("provider", "unknown")] += 1
        if m.get("filepath"):
            filepaths.append(m["filepath"])
    
    return {
        "fields": dict(fields),
        "categories": dict(categories),
        "sources": dict(sources),
        "types": dict(types),
        "providers": dict(providers),
        "sample_filepaths": filepaths[:10]
    }

if __name__ == "__main__":
    print("=" * 60)
    print("GEN8 CHROMADB ANALYSIS")
    print("=" * 60)
    
    # Get count
    count = get_count()
    print(f"\n📊 Total Documents: {count}")
    
    # Get sample
    print("\n⏳ Fetching sample of 200 documents...")
    data = get_sample(200)
    metas = data.get("metadatas", [])
    print(f"   Retrieved {len(metas)} metadata records")
    
    # Analyze
    analysis = analyze_metadata(metas)
    
    print("\n📁 METADATA FIELDS FOUND:")
    for field, count in sorted(analysis["fields"].items(), key=lambda x: -x[1]):
        print(f"   {field}: {count}")
    
    print("\n📂 CATEGORIES:")
    for cat, count in sorted(analysis["categories"].items(), key=lambda x: -x[1]):
        print(f"   {cat}: {count}")
    
    print("\n📄 SOURCES:")
    for src, count in sorted(analysis["sources"].items(), key=lambda x: -x[1]):
        print(f"   {src}: {count}")
    
    print("\n🏷️ TYPES:")
    for t, count in sorted(analysis["types"].items(), key=lambda x: -x[1]):
        print(f"   {t}: {count}")
    
    print("\n🤖 PROVIDERS:")
    for p, count in sorted(analysis["providers"].items(), key=lambda x: -x[1]):
        print(f"   {p}: {count}")
    
    if analysis["sample_filepaths"]:
        print("\n📝 SAMPLE FILEPATHS:")
        for fp in analysis["sample_filepaths"]:
            print(f"   {fp}")
    
    print("\n" + "=" * 60)

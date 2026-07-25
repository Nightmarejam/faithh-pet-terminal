#!/usr/bin/env python3
"""
RAG Metadata Analysis
Analyzes ChromaDB collection to understand metadata quality and distribution.
"""

import chromadb
from collections import Counter
import json

def analyze_metadata():
    print("Connecting to ChromaDB...")
    client = chromadb.HttpClient(host="localhost", port=8000)
    collection = client.get_collection("documents_768")

    total = collection.count()
    print(f"Total documents: {total:,}\n")

    # Sample metadata (can't get all 93k at once efficiently)
    print("Sampling 5000 documents for metadata analysis...")
    results = collection.get(limit=5000, include=["metadatas"])

    # Analyze fields
    sources = Counter()
    categories = Counter()
    types = Counter()
    missing_source = 0
    missing_category = 0

    for meta in results['metadatas']:
        src = meta.get('source', 'MISSING')
        cat = meta.get('category', 'MISSING')
        typ = meta.get('type', 'MISSING')

        if src in ['unknown', 'MISSING', '', None]:
            missing_source += 1
            sources['(unknown/missing)'] += 1
        else:
            sources[src[:50]] += 1  # Truncate long sources

        if cat in ['MISSING', '', None]:
            missing_category += 1
            categories['(missing)'] += 1
        else:
            categories[cat] += 1

        types[typ] += 1

    # Report
    print("\n" + "="*60)
    print("METADATA ANALYSIS REPORT")
    print("="*60)

    print(f"\nSample size: {len(results['metadatas']):,} / {total:,}")
    print(f"Missing/unknown source: {missing_source} ({missing_source/len(results['metadatas'])*100:.1f}%)")
    print(f"Missing category: {missing_category} ({missing_category/len(results['metadatas'])*100:.1f}%)")

    print("\n--- TOP 20 SOURCES ---")
    for src, count in sources.most_common(20):
        print(f"  {count:5d}  {src}")

    print("\n--- CATEGORIES ---")
    for cat, count in categories.most_common(20):
        print(f"  {count:5d}  {cat}")

    print("\n--- DOCUMENT TYPES ---")
    for typ, count in types.most_common(20):
        print(f"  {count:5d}  {typ}")

    # Save full report
    report = {
        "total_documents": total,
        "sample_size": len(results['metadatas']),
        "missing_source_count": missing_source,
        "missing_source_pct": round(missing_source/len(results['metadatas'])*100, 1),
        "missing_category_count": missing_category,
        "top_sources": dict(sources.most_common(50)),
        "categories": dict(categories),
        "types": dict(types)
    }

    with open("docs/RAG_METADATA_ANALYSIS.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nFull report saved to docs/RAG_METADATA_ANALYSIS.json")

    # Recommendations
    print("\n--- RECOMMENDATIONS ---")
    if missing_source/len(results['metadatas']) > 0.3:
        print("⚠️  HIGH: >30% docs missing source attribution")
        print("   → Run metadata enrichment script")
    if missing_category/len(results['metadatas']) > 0.5:
        print("⚠️  MEDIUM: >50% docs missing category")
        print("   → Add category inference based on content/source patterns")

    return report

if __name__ == "__main__":
    analyze_metadata()

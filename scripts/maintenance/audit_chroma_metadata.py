#!/usr/bin/env python3
"""
ChromaDB metadata audit — samples documents and reports metadata coverage.
Usage: python scripts/maintenance/audit_chroma_metadata.py
"""
import sys
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import chromadb
from dotenv import load_dotenv
import os

load_dotenv()

CHROMA_URL = os.getenv("CHROMA_URL", "http://192.158.1.10:8000")
COLLECTION_NAME = "faithh_knowledge_base"
SAMPLE_SIZE = 200

def audit():
    client = chromadb.HttpClient(host=CHROMA_URL.replace("http://", "").split(":")[0],
                                  port=int(CHROMA_URL.split(":")[-1]))
    collection = client.get_collection(COLLECTION_NAME)
    total = collection.count()
    print(f"\n=== ChromaDB Metadata Audit ===")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Total documents: {total}")
    print(f"Sample size: {SAMPLE_SIZE}\n")

    # Get a random sample
    all_ids = collection.get(limit=total, include=[])["ids"]
    sample_ids = random.sample(all_ids, min(SAMPLE_SIZE, len(all_ids)))
    results = collection.get(ids=sample_ids, include=["metadatas", "documents"])

    # Analyze metadata fields
    field_counts = Counter()
    field_values = defaultdict(Counter)
    missing_fields = []
    doc_previews = []

    for i, (doc, meta) in enumerate(zip(results["documents"], results["metadatas"])):
        if meta:
            for key, val in meta.items():
                field_counts[key] += 1
                if isinstance(val, str):
                    field_values[key][val[:50]] += 1
        else:
            missing_fields.append(results["ids"][i])

        if i < 10:
            doc_previews.append({
                "id": results["ids"][i],
                "preview": (doc or "")[:80],
                "metadata": meta or {}
            })

    # Report
    print("--- Field Coverage ---")
    for field, count in sorted(field_counts.items(), key=lambda x: -x[1]):
        pct = (count / SAMPLE_SIZE) * 100
        print(f"  {field:<30} {count:>4}/{SAMPLE_SIZE} ({pct:.0f}%)")

    print(f"\n--- Documents with NO metadata: {len(missing_fields)} ({len(missing_fields)/SAMPLE_SIZE*100:.0f}%) ---")

    print("\n--- Top values per field (top 5) ---")
    priority_fields = ["source_type", "domain", "project", "content_type", 
                       "quality_score", "privacy_level", "access_tier"]
    for field in priority_fields:
        if field in field_values:
            print(f"\n  {field}:")
            for val, cnt in field_values[field].most_common(5):
                print(f"    '{val}' — {cnt}x")
        else:
            print(f"\n  {field}: NOT PRESENT IN SAMPLE")

    print("\n--- 10 Document Previews ---")
    for p in doc_previews:
        print(f"\n  ID: {p['id'][:40]}...")
        print(f"  Content: {p['preview']}")
        print(f"  Metadata fields: {list(p['metadata'].keys()) or 'NONE'}")

    # Summary
    has_source_type = field_counts.get("source_type", 0)
    has_domain = field_counts.get("domain", 0)
    has_quality = field_counts.get("quality_score", 0)
    has_created = field_counts.get("created_at", 0)

    print("\n=== Summary ===")
    print(f"Core metadata coverage:")
    print(f"  source_type:   {has_source_type/SAMPLE_SIZE*100:.0f}%")
    print(f"  domain:        {has_domain/SAMPLE_SIZE*100:.0f}%")
    print(f"  quality_score: {has_quality/SAMPLE_SIZE*100:.0f}%")
    print(f"  created_at:    {has_created/SAMPLE_SIZE*100:.0f}%")

    if has_source_type < SAMPLE_SIZE * 0.5:
        print("\n⚠️  METADATA MIGRATION NEEDED: Less than 50% of documents have source_type")
    else:
        print("\n✅ Metadata coverage adequate for structured retrieval")

    # Save report
    report = {
        "total_documents": total,
        "sample_size": SAMPLE_SIZE,
        "field_coverage": {k: v/SAMPLE_SIZE for k, v in field_counts.items()},
        "documents_without_metadata": len(missing_fields),
        "needs_migration": has_source_type < SAMPLE_SIZE * 0.5
    }
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    with open("logs/chroma_audit_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved to logs/chroma_audit_report.json")

if __name__ == "__main__":
    audit()

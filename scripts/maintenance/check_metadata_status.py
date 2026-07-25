#!/usr/bin/env python3
"""Check current metadata status after enhancement"""

import sys
import json
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import chromadb
from dotenv import load_dotenv
import os

load_dotenv()

CHROMA_URL = os.getenv("CHROMA_URL", "http://servicebox.taileb8c60.ts.net:8000")
COLLECTION_NAME = "faithh_knowledge_base"
SAMPLE_SIZE = 50

def check_metadata():
    host = CHROMA_URL.replace("http://", "").split(":")[0]
    port = int(CHROMA_URL.split(":")[-1])
    client = chromadb.HttpClient(host=host, port=port)
    collection = client.get_collection(COLLECTION_NAME)
    total = collection.count()
    
    print(f"\n=== Post-Enhancement Metadata Check ===")
    print(f"Total documents: {total}")
    print(f"Sample size: {SAMPLE_SIZE}\n")
    
    # Get random sample
    all_ids = collection.get(limit=total, include=[])["ids"]
    sample_ids = random.sample(all_ids, min(SAMPLE_SIZE, len(all_ids)))
    results = collection.get(ids=sample_ids, include=["metadatas", "documents"])
    
    # Analyze enhanced fields
    field_counts = {}
    domain_counts = {}
    quality_scores = []
    
    for meta in results["metadatas"]:
        if meta:
            for field in ['domain', 'created_at', 'quality_score', 'enhanced_at']:
                if field in meta:
                    field_counts[field] = field_counts.get(field, 0) + 1
            
            # Count domains
            if 'domain' in meta:
                domain = meta['domain']
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
            
            # Collect quality scores
            if 'quality_score' in meta:
                try:
                    quality_scores.append(float(meta['quality_score']))
                except:
                    pass
    
    # Report results
    print("--- Enhanced Field Coverage ---")
    for field, count in field_counts.items():
        pct = (count / SAMPLE_SIZE) * 100
        print(f"  {field:<20} {count:>3}/{SAMPLE_SIZE} ({pct:.0f}%)")
    
    print(f"\n--- Domain Distribution ---")
    for domain, count in sorted(domain_counts.items(), key=lambda x: -x[1]):
        pct = (count / SAMPLE_SIZE) * 100
        print(f"  {domain:<15} {count:>3} ({pct:.0f}%)")
    
    if quality_scores:
        avg_quality = sum(quality_scores) / len(quality_scores)
        print(f"\n--- Quality Scores ---")
        print(f"  Average: {avg_quality:.3f}")
        print(f"  Min: {min(quality_scores):.3f}")
        print(f"  Max: {max(quality_scores):.3f}")
    
    # Show sample document
    print(f"\n--- Sample Enhanced Document ---")
    sample_meta = results["metadatas"][0]
    if sample_meta:
        print("Metadata fields:")
        for key, value in sorted(sample_meta.items()):
            if isinstance(value, str) and len(value) > 50:
                value = value[:50] + "..."
            print(f"  {key}: {value}")

if __name__ == "__main__":
    check_metadata()

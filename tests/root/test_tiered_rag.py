#!/usr/bin/env python3
"""Test the tiered RAG processor implementation"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.tiered_rag_processor import TieredRAGProcessor
from datetime import datetime

def test_tiered_rag():
    print("=== Testing Tiered RAG Processor ===")
    print()
    
    # Initialize processor
    processor = TieredRAGProcessor()
    print("✅ Tiered RAG Processor initialized")
    print()
    
    # Show stats
    stats = processor.get_stats()
    print("Current Stats:")
    for tier_num, tier_stats in stats['tiers'].items():
        print(f"  Tier {tier_num}: {tier_stats['count']} docs ({tier_stats['utilization']:.1%} utilized)")
    print(f"  Total: {stats['total_documents']} documents")
    print()
    
    # Test routing
    test_docs = [
        {
            'source': 'chat',
            'created_at': datetime.now().isoformat(),
            'size': 500,
            'content': 'Recent chat about ALIFE experiments'
        },
        {
            'source': 'alife',
            'created_at': datetime.now().isoformat(),
            'size': 2000,
            'content': 'ALIFE experiment results from today'
        },
        {
            'source': 'gov_api',
            'created_at': '2025-01-01T00:00:00',
            'size': 5000,
            'content': 'Old government API response'
        }
    ]
    
    print("Document Routing Test:")
    for doc in test_docs:
        tier = processor.route_document(doc)
        print(f"  {doc['source']} doc -> Tier {tier}")
    print()
    
    # Test query
    print("Query Test:")
    results = processor.query("parasitic emergence experiment 5", n_results=3)
    
    for i, result in enumerate(results):
        print(f"  Result {i+1}:")
        print(f"    Tier: {result['tier']}")
        print(f"    Distance: {result['distance']:.3f}")
        print(f"    Content: {result['document'][:100]}...")
        print()
    
    print("✅ Tiered RAG Processor test complete")

if __name__ == "__main__":
    test_tiered_rag()

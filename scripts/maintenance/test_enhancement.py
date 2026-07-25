#!/usr/bin/env python3
"""Test metadata enhancement on a small sample"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.maintenance.enhance_metadata import MetadataEnhancer

def test_enhancement():
    enhancer = MetadataEnhancer()
    
    # Get just 10 documents for testing
    results = enhancer.collection.get(limit=10, include=['documents', 'metadatas'])
    
    print("=== Testing Metadata Enhancement ===\n")
    
    for i, (doc_id, document, metadata) in enumerate(zip(results['ids'], results['documents'], results['metadatas'])):
        print(f"Document {i+1}: {doc_id[:20]}...")
        print(f"  Current metadata fields: {list(metadata.keys()) if metadata else 'None'}")
        
        # Test enhancement
        enhanced = enhancer.enhance_document(doc_id, document, metadata)
        print(f"  Enhanced metadata fields: {list(enhanced.keys())}")
        
        # Show key new fields
        if 'domain' in enhanced:
            print(f"  Domain: {enhanced['domain']}")
        if 'created_at' in enhanced:
            print(f"  Created: {enhanced['created_at']}")
        if 'quality_score' in enhanced:
            print(f"  Quality: {enhanced['quality_score']:.3f}")
        
        print()

if __name__ == "__main__":
    test_enhancement()

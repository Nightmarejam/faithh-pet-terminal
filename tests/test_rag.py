#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/jonat/ai-stack/backend')
from rag_processor import RAGProcessor

proc = RAGProcessor()
results = proc.search("Output-Coherence Sensor Attention Rebalancer Phase-Flip Controller", n_results=5)
for r in results:
    print(f"File: {r['metadata']['filename']}")
    print(f"Text: {r['text'][:200]}...")
    print(f"Distance: {r['distance']}")
    print()

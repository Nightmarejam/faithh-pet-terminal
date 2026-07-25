#!/usr/bin/env python3

import sys
sys.path.append('/home/jonat/ai-stack')

from faithh_professional_backend_fixed import smart_rag_query

# Test the smart_rag_query function directly
results = smart_rag_query("What is the Universal Civic Floor?", n_results=5, intent={'is_governance_query': True, 'is_constella_query': False, 'is_alife_query': False, 'is_self_query': False, 'is_why_question': False, 'is_next_action_query': False})

print(f"Results type: {type(results)}")
print(f"Constitutional principles in results: {'constitutional_principles' in results if isinstance(results, dict) else False}")

if isinstance(results, dict):
    print(f"Constitutional principles: {results.get('constitutional_principles')}")
    if results.get('constitutional_principles'):
        print(f"Found {len(results['constitutional_principles'])} principles")
        for principle in results['constitutional_principles']:
            print(f"  - {principle.get('title', 'No title')}")
    else:
        print("Constitutional principles key exists but is empty")
else:
    print("No constitutional principles found in results")

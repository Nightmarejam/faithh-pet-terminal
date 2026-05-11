#!/usr/bin/env python3
"""
Simple test for smart routing without backend
"""

import sys
sys.path.append('/home/jonat/ai-stack')

from backend.llm_providers import run_llm_smart_route, get_optimal_model_for_query

def test_model_selection():
    print("=== Testing Model Selection ===")
    
    test_queries = [
        "hello, how are you?",
        "why does quantum mechanics work?",
        "imagine a perfect world",
        "what does my faithh_memory.json say?"
    ]
    
    for query in test_queries:
        try:
            provider, model = get_optimal_model_for_query(query)
            print(f"✅ '{query[:30]}...' -> {provider}:{model}")
        except Exception as e:
            print(f"❌ '{query[:30]}...' -> ERROR: {e}")

def test_smart_routing():
    print("\n=== Testing Smart Routing (Dry Run) ===")
    
    # Simple test without actual API calls
    try:
        provider, model = get_optimal_model_for_query("hello")
        print(f"✅ Simple query routing: {provider}:{model}")
        
        provider, model = get_optimal_model_for_query("why does quantum entanglement work")
        print(f"✅ Complex query routing: {provider}:{model}")
        
        provider, model = get_optimal_model_for_query("imagine a future")
        print(f"✅ Creative query routing: {provider}:{model}")
        
    except Exception as e:
        print(f"❌ Smart routing error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_model_selection()
    test_smart_routing()

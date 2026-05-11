#!/usr/bin/env python3
"""
Test script for smart LLM routing
"""

import sys
sys.path.append('/home/jonat/ai-stack')

from backend.llm_providers import (
    detect_query_complexity,
    get_optimal_model_for_query,
    detect_mode
)

def test_complexity_detection():
    """Test query complexity detection"""
    
    test_cases = [
        # Simple queries
        ("hello", "simple"),
        ("what's the weather", "simple"),
        ("how are you", "simple"),
        
        # Complex queries
        ("why does quantum mechanics work", "complex"),
        ("analyze the implications of AI on society", "complex"),
        ("compare and contrast different approaches", "complex"),
        ("what is the relationship between consciousness and physics", "complex"),
        
        # Creative queries
        ("imagine a world where AI helps humanity", "creative"),
        ("brainstorm ideas for a new project", "creative"),
        ("design a solution for climate change", "creative"),
        ("what if we could travel faster than light", "creative"),
        
        # Grounded queries (these will be detected by patterns, not complexity)
        ("what does the faithh_memory.json say", "simple"),
        ("according to my docs", "simple"),
        ("in my project documentation", "simple"),
    ]
    
    print("=== Testing Query Complexity Detection ===")
    for query, expected in test_cases:
        detected = detect_query_complexity(query)
        
        status = "✅" if detected == expected else "❌"
        print(f"{status} '{query[:40]}...' -> {detected} (expected: {expected})")

def test_model_selection():
    """Test optimal model selection"""
    
    test_cases = [
        ("hello there", "ollama", "qwen25-grounded-gen5-delta:latest"),
        ("why does the quantum eraser experiment work", "ollama", "deepseek-r1:32b"),
        ("imagine a perfect AI companion", "gemini", "gemini-2.0-flash-exp"),
        ("what does my faithh_memory.json contain", "ollama", "qwen25-grounded-gen5-delta:latest"),
        ("analyze the strategic implications", "ollama", "deepseek-r1:32b"),
    ]
    
    print("\n=== Testing Optimal Model Selection ===")
    for query, exp_provider, exp_model in test_cases:
        provider, model = get_optimal_model_for_query(query)
        
        provider_match = provider == exp_provider
        model_match = model == exp_model
        
        status = "✅" if (provider_match and model_match) else "❌"
        print(f"{status} '{query[:40]}...' -> {provider}:{model}")
        if not provider_match:
            print(f"   Provider mismatch: got {provider}, expected {exp_provider}")
        if not model_match:
            print(f"   Model mismatch: got {model}, expected {exp_model}")

def test_integration():
    """Test full integration with actual routing"""
    
    print("\n=== Testing Integration (Dry Run) ===")
    
    # Test simple query
    provider, model = get_optimal_model_for_query("hello, how are you?")
    print(f"Simple query -> {provider}:{model}")
    
    # Test complex query
    provider, model = get_optimal_model_for_query("why does quantum entanglement work and what are its implications")
    print(f"Complex query -> {provider}:{model}")
    
    # Test creative query
    provider, model = get_optimal_model_for_query("imagine a future where AI and humans collaborate perfectly")
    print(f"Creative query -> {provider}:{model}")
    
    # Test grounded query
    provider, model = get_optimal_model_for_query("what does my decisions_log.json say about recent changes")
    print(f"Grounded query -> {provider}:{model}")

if __name__ == "__main__":
    test_complexity_detection()
    test_model_selection()
    test_integration()
    print("\n=== Smart Routing Test Complete ===")

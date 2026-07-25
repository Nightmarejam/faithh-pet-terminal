#!/usr/bin/env python3
"""
Test Program Advance Detection
Run this to verify the integration works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from backend.enhanced_chip_integration import detect_program_advance, PROGRAM_ADVANCES

def test_program_advances():
    """Test all Program Advance combinations."""
    
    test_cases = [
        # Context Recovery
        ("where was I with the FAITHH project?", ["scaffolding", "rag_search"], "context_recovery"),
        
        # Decision Audit  
        ("why did we choose React for the frontend?", ["decisions", "rag_search"], "decision_audit"),
        
        # Project Deep Dive
        ("what's the current phase of the Constella project?", ["project_state", "rag_search", "constella"], "project_deep_dive"),
        
        # Business Review
        ("how is Tom Cat Sound LLC doing?", ["project_state", "rag_search"], "business_review"),
        
        # Full Recall
        ("tell me everything about the FAITHH project", ["scaffolding", "rag_search", "decisions", "project_state"], "full_recall"),
        
        # No advance
        ("what's the weather like?", ["rag_search"], None),
    ]
    
    print("=== Program Advance Detection Test ===")
    print()
    
    passed = 0
    total = len(test_cases)
    
    for query, chips, expected_advance in test_cases:
        detected_advance, merge_strategy = detect_program_advance(chips, query)
        
        if detected_advance == expected_advance:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
        
        print(f"{status} Query: {query}")
        print(f"     Chips: {chips}")
        print(f"     Expected: {expected_advance}")
        print(f"     Detected: {detected_advance}")
        print(f"     Strategy: {merge_strategy}")
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Program Advances working correctly!")
    else:
        print("⚠️  Some Program Advances need adjustment")

if __name__ == "__main__":
    test_program_advances()

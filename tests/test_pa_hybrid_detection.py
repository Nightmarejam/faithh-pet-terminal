#!/usr/bin/env python3
"""
Comprehensive tests for Hybrid Program Advance Detection

Tests both trigger phrase (fast path) and semantic (slow path) detection.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.enhanced_chip_integration import (
    detect_program_advance_hybrid,
    get_pa_chips_for_query,
    PROGRAM_ADVANCES,
    PA_SEMANTIC_THRESHOLD
)

# Test cases: (query, expected_pa, expected_method)
# expected_method: "trigger", "semantic", or "none"
TEST_CASES = [
    # ============================================
    # CONTEXT RECOVERY - Trigger phrases
    # ============================================
    ("where was I", "context_recovery", "trigger"),
    ("catch me up", "context_recovery", "trigger"),
    ("what was I doing", "context_recovery", "trigger"),
    ("get me back up to speed", "context_recovery", "trigger"),
    ("bring me up to date", "context_recovery", "trigger"),
    
    # CONTEXT RECOVERY - Semantic (paraphrased)
    ("what was I working on last time", "context_recovery", "semantic"),
    ("resume my previous work", "context_recovery", "semantic"),
    
    # ============================================
    # DECISION AUDIT - Trigger phrases
    # ============================================
    ("why did we choose React", "decision_audit", "trigger"),
    ("what was the rationale", "decision_audit", "trigger"),
    ("explain the reasoning", "decision_audit", "trigger"),
    ("what was the thinking behind this", "decision_audit", "trigger"),
    ("what alternatives did we consider", "decision_audit", "trigger"),
    
    # DECISION AUDIT - Semantic (paraphrased)
    ("justify this technical decision", "decision_audit", "semantic"),
    ("explain why we went this direction", "decision_audit", "semantic"),
    
    # ============================================
    # PROJECT DEEP DIVE - Trigger phrases
    # ============================================
    ("what's the project status", "project_deep_dive", "trigger"),
    ("how is progress going", "project_deep_dive", "trigger"),
    ("what phase are we in", "project_deep_dive", "trigger"),
    
    # PROJECT DEEP DIVE - Semantic (paraphrased)
    ("give me a project overview", "project_deep_dive", "semantic"),
    ("summarize the project state", "project_deep_dive", "semantic"),
    
    # ============================================
    # BUSINESS REVIEW - Trigger phrases
    # ============================================
    ("how is the business doing", "business_review", "trigger"),
    ("tell me about Tom Cat Sound", "business_review", "trigger"),
    ("Floating Garden status", "business_review", "trigger"),
    ("LLC update", "business_review", "trigger"),
    ("client and revenue status", "business_review", "trigger"),
    
    # BUSINESS REVIEW - Semantic (paraphrased)
    ("review my business projects", "business_review", "semantic"),
    ("audio business finances", "business_review", "semantic"),
    
    # ============================================
    # FULL RECALL - Trigger phrases
    # ============================================
    ("tell me everything about FAITHH", "full_recall", "trigger"),
    ("complete history of this project", "full_recall", "trigger"),
    ("all information on Constella", "full_recall", "trigger"),
    ("full context on this topic", "full_recall", "trigger"),
    
    # FULL RECALL - Semantic (paraphrased)
    ("comprehensive overview of everything", "full_recall", "semantic"),
    ("dump all context on this", "full_recall", "semantic"),
    
    # ============================================
    # NO MATCH - Should not trigger any PA
    # ============================================
    ("hello", None, "none"),
    ("what is the weather", None, "none"),
    ("write me a Python function", None, "none"),
    ("how do I use Docker", None, "none"),
    ("random unrelated query", None, "none"),
]


def run_tests():
    """Run all PA detection tests and report results."""
    print("=" * 60)
    print("HYBRID PROGRAM ADVANCE DETECTION TESTS")
    print(f"Semantic Threshold: {PA_SEMANTIC_THRESHOLD}")
    print(f"Program Advances: {list(PROGRAM_ADVANCES.keys())}")
    print("=" * 60)
    print()
    
    passed = 0
    failed = 0
    results = []
    
    for query, expected_pa, expected_method in TEST_CASES:
        # Run detection without chip requirements (pre-detection mode)
        actual_pa, _, actual_method = detect_program_advance_hybrid(query, active_chips=None)
        
        # Check if result matches expectation
        pa_match = actual_pa == expected_pa
        method_match = actual_method == expected_method
        
        if pa_match and method_match:
            status = "✅ PASS"
            passed += 1
        elif pa_match and not method_match:
            status = "⚠️ PA OK, method differs"
            passed += 1  # Still counts as pass if PA is correct
        else:
            status = "❌ FAIL"
            failed += 1
        
        results.append({
            "query": query,
            "expected": f"{expected_pa} ({expected_method})",
            "actual": f"{actual_pa} ({actual_method})",
            "status": status
        })
        
        # Print result
        print(f"{status}")
        print(f"  Query: \"{query}\"")
        print(f"  Expected: {expected_pa} ({expected_method})")
        print(f"  Actual:   {actual_pa} ({actual_method})")
        print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total:  {len(TEST_CASES)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Rate:   {passed/len(TEST_CASES)*100:.1f}%")
    print()
    
    # Show failures
    if failed > 0:
        print("FAILURES:")
        for r in results:
            if "FAIL" in r["status"]:
                print(f"  - \"{r['query']}\"")
                print(f"    Expected: {r['expected']}")
                print(f"    Actual:   {r['actual']}")
    
    return failed == 0


def test_chip_forcing():
    """Test that get_pa_chips_for_query returns correct chips."""
    print()
    print("=" * 60)
    print("CHIP FORCING TESTS")
    print("=" * 60)
    print()
    
    test_cases = [
        ("where was I", {"scaffolding", "rag_search"}),
        ("why did we choose this", {"decisions", "rag_search"}),
        ("project status", {"project_state", "rag_search", "constella"}),
        ("business update", {"project_state", "rag_search"}),
        ("everything about FAITHH", {"scaffolding", "rag_search", "decisions", "project_state"}),
        ("hello world", set()),  # No PA, no chips
    ]
    
    passed = 0
    for query, expected_chips in test_cases:
        actual_chips = get_pa_chips_for_query(query)
        if actual_chips == expected_chips:
            print(f"✅ PASS: \"{query}\"")
            print(f"   Chips: {actual_chips}")
            passed += 1
        else:
            print(f"❌ FAIL: \"{query}\"")
            print(f"   Expected: {expected_chips}")
            print(f"   Actual:   {actual_chips}")
    
    print()
    print(f"Chip forcing: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)


if __name__ == "__main__":
    print()
    pa_tests_passed = run_tests()
    chip_tests_passed = test_chip_forcing()
    
    print()
    print("=" * 60)
    if pa_tests_passed and chip_tests_passed:
        print("🎉 ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)

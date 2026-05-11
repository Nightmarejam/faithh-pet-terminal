#!/usr/bin/env python3
"""
Integration Testing Suite for Coherence Arbiter Phase 3
Tests coherence across diverse query patterns and edge cases
"""

import json
import time
import requests
import statistics
from typing import List, Dict, Any
from datetime import datetime

class CoherenceIntegrationTester:
    def __init__(self, base_url: str = "http://localhost:5557"):
        self.base_url = base_url
        self.results = []
        
    def test_query(self, query: str, description: str) -> Dict[str, Any]:
        """Test a single query and return coherence metrics"""
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={"query": query},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                return {
                    "query": query,
                    "description": description,
                    "error": f"HTTP {response.status_code}",
                    "response_time": time.time() - start_time
                }
            
            data = response.json()
            coherence = data.get("coherence", {})
            
            result = {
                "query": query,
                "description": description,
                "response_time": time.time() - start_time,
                "convergence_score": coherence.get("convergence_score"),
                "raw_convergence": coherence.get("raw_convergence"),
                "tier": coherence.get("tier"),
                "reasons": coherence.get("reasons", []),
                "low_confidence": coherence.get("low_confidence"),
                "suggested_behavior": coherence.get("suggested_behavior"),
                "anchor_score": None,
                "signals": coherence.get("convergence_signals", [])
            }
            
            # Extract anchor score if available
            anchor_validation = coherence.get("anchor_validation", {})
            if anchor_validation and anchor_validation.get("faithh_phase"):
                result["anchor_score"] = anchor_validation["faithh_phase"].get("validation_score")
            
            return result
            
        except Exception as e:
            return {
                "query": query,
                "description": description,
                "error": str(e),
                "response_time": time.time() - start_time
            }
    
    def run_test_suite(self) -> Dict[str, Any]:
        """Run comprehensive integration tests"""
        
        test_queries = [
            # Basic coherence tests
            ("What is FAITHH?", "Basic project inquiry"),
            ("Tell me about my recent work", "Recent work summary"),
            ("What are the current project states?", "Project status query"),
            
            # High coherence expected
            ("FAITHH backend architecture and coherence measurement", "Technical domain-specific"),
            ("Coherence Arbiter Phase 1-3 implementation", "Specific feature query"),
            ("ML chip routing and RAG convergence", "Technical subsystem query"),
            
            # Medium coherence expected
            ("How does the PULSE reflection engine work?", "Subsystem explanation"),
            ("What are the ChromaDB document counts?", "Infrastructure query"),
            ("Explain the anchor validation system", "Feature explanation"),
            
            # Low coherence expected
            ("What's the weather like in Tokyo?", "Unrelated domain"),
            ("Tell me about quantum physics", "Outside knowledge domain"),
            ("Who won the last Super Bowl?", "Completely unrelated"),
            
            # Edge cases
            ("", "Empty query"),
            ("a", "Single character"),
            ("!@#$%^&*()", "Special characters only"),
            ("A" * 200, "Very long query"),
            
            # Conversation-based (signal_strength_only expected)
            ("What's the current status of FAITHH?", "Focused project query"),
            ("Should I continue with Phase 4?", "Decision-oriented query"),
            ("What are the next priorities?", "Planning query"),
            
            # Complex multi-part queries
            ("Tell me about FAITHH's architecture and how the coherence system works with ML chips", "Multi-part technical"),
            ("What are the project states and what should I work on next?", "Status + planning"),
            ("How does the Coherence Arbiter validate claims and what are the current scores?", "Technical + metrics"),
        ]
        
        print("🧪 Running Coherence Integration Test Suite...")
        print(f"📊 Testing {len(test_queries)} diverse query patterns")
        print("=" * 60)
        
        for query, description in test_queries:
            print(f"Testing: {description}")
            result = self.test_query(query, description)
            self.results.append(result)
            
            if "error" in result:
                print(f"  ❌ ERROR: {result['error']}")
            else:
                tier_icon = {"high": "🟢", "medium": "🟡", "low": "🔴", None: "⚪"}.get(result["tier"])
                behavior_icon = {"ok": "✅", "hedge": "⚠️", "recheck_sources": "🔍", None: "❓"}.get(result["suggested_behavior"])
                score = result["convergence_score"] or 0.0
                print(f"  {tier_icon} Tier: {result['tier'] or 'None'} | Score: {score:.3f} | {behavior_icon} {result['suggested_behavior'] or 'None'}")
                print(f"  📡 Signals: {', '.join(result['signals']) if result['signals'] else 'None'}")
                if result['anchor_score']:
                    print(f"  🎯 Anchor: {result['anchor_score']:.3f}")
            print()
        
        return self.analyze_results()
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze test results and generate summary statistics"""
        
        # Filter out error results
        valid_results = [r for r in self.results if "error" not in r]
        error_results = [r for r in self.results if "error" in r]
        
        if not valid_results:
            return {
                "summary": "❌ ALL TESTS FAILED",
                "total_tests": len(self.results),
                "successful_tests": 0,
                "failed_tests": len(error_results),
                "errors": [r["error"] for r in error_results]
            }
        
        # Calculate statistics
        convergence_scores = [r["convergence_score"] for r in valid_results if r["convergence_score"] is not None]
        response_times = [r["response_time"] for r in valid_results]
        
        tier_counts = {}
        behavior_counts = {}
        signal_counts = {}
        
        for result in valid_results:
            tier = result["tier"] or "None"
            behavior = result["suggested_behavior"] or "None"
            
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
            behavior_counts[behavior] = behavior_counts.get(behavior, 0) + 1
            
            for signal in result["signals"]:
                signal_counts[signal] = signal_counts.get(signal, 0) + 1
        
        analysis = {
            "summary": "✅ INTEGRATION TESTS COMPLETE",
            "total_tests": len(self.results),
            "successful_tests": len(valid_results),
            "failed_tests": len(error_results),
            "performance": {
                "avg_response_time": statistics.mean(response_times),
                "max_response_time": max(response_times),
                "min_response_time": min(response_times),
                "under_50ms": sum(1 for t in response_times if t < 0.05),
                "under_100ms": sum(1 for t in response_times if t < 0.1)
            },
            "coherence_distribution": {
                "avg_score": statistics.mean(convergence_scores) if convergence_scores else 0,
                "min_score": min(convergence_scores) if convergence_scores else 0,
                "max_score": max(convergence_scores) if convergence_scores else 0,
                "score_std": statistics.stdev(convergence_scores) if len(convergence_scores) > 1 else 0
            },
            "tier_distribution": tier_counts,
            "behavior_distribution": behavior_counts,
            "signal_distribution": signal_counts,
            "errors": [r["error"] for r in error_results]
        }
        
        # Performance assessment
        avg_time = analysis["performance"]["avg_response_time"]
        if avg_time < 0.05:
            perf_status = "🟢 EXCELLENT (<50ms)"
        elif avg_time < 0.1:
            perf_status = "🟡 GOOD (<100ms)"
        else:
            perf_status = "🔴 SLOW (>100ms)"
        
        # Coherence range assessment
        score_range = analysis["coherence_distribution"]["max_score"] - analysis["coherence_distribution"]["min_score"]
        if score_range > 0.3:
            coherence_status = "🟢 GOOD VARIATION"
        elif score_range > 0.1:
            coherence_status = "🟡 MODERATE VARIATION"
        else:
            coherence_status = "🔴 LOW VARIATION"
        
        print("=" * 60)
        print("📊 INTEGRATION TEST RESULTS")
        print("=" * 60)
        print(f"Total Tests: {analysis['total_tests']}")
        print(f"Successful: {analysis['successful_tests']} ✅")
        print(f"Failed: {analysis['failed_tests']} ❌")
        print()
        print("⚡ PERFORMANCE:")
        print(f"  Average Response Time: {avg_time*1000:.1f}ms {perf_status}")
        print(f"  Under 50ms: {analysis['performance']['under_50ms']}/{len(valid_results)}")
        print(f"  Under 100ms: {analysis['performance']['under_100ms']}/{len(valid_results)}")
        print()
        print("🎯 COHERENCE:")
        print(f"  Score Range: {analysis['coherence_distribution']['min_score']:.3f} - {analysis['coherence_distribution']['max_score']:.3f} {coherence_status}")
        print(f"  Average Score: {analysis['coherence_distribution']['avg_score']:.3f}")
        print()
        print("📈 DISTRIBUTIONS:")
        print(f"  Tiers: {dict(analysis['tier_distribution'])}")
        print(f"  Behaviors: {dict(analysis['behavior_distribution'])}")
        print(f"  Signals: {dict(analysis['signal_distribution'])}")
        
        if analysis["errors"]:
            print()
            print("❌ ERRORS:")
            for error in analysis["errors"]:
                print(f"  - {error}")
        
        print()
        print("🔍 RECOMMENDATIONS:")
        
        # Generate recommendations
        if avg_time > 0.1:
            print("  ⚠️  Consider optimizing response times (>100ms average)")
        
        if score_range < 0.1:
            print("  ⚠️  Coherence scores have low variation - check threshold settings")
        
        if analysis["failed_tests"] > 0:
            print(f"  ⚠️  {analysis['failed_tests']} tests failed - review error logs")
        
        if analysis["performance"]["under_50ms"] < len(valid_results) * 0.8:
            print("  ⚠️  Less than 80% of queries under 50ms - performance optimization needed")
        
        if not any("rag_chip_alignment" in signal for signal in signal_counts):
            print("  ⚠️  No rag_chip_alignment signals detected - check RAG embedding extraction")
        
        return analysis

def main():
    """Run integration tests"""
    tester = CoherenceIntegrationTester()
    results = tester.run_test_suite()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_integration_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "results": tester.results,
            "analysis": results
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    main()

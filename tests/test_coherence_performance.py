#!/usr/bin/env python3
"""
Performance Benchmark for Coherence Arbiter Phase 3
Tests response times and system performance under load
"""

import json
import time
import requests
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from datetime import datetime

class CoherencePerformanceTester:
    def __init__(self, base_url: str = "http://localhost:5557"):
        self.base_url = base_url
        self.results = []
        
    def single_query_test(self, query: str) -> Dict[str, Any]:
        """Test a single query and measure performance"""
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={"query": query},
                headers={"Content-Type": "application/json"}
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code != 200:
                return {
                    "query": query,
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "response_time": response_time
                }
            
            data = response.json()
            coherence = data.get("coherence", {})
            
            return {
                "query": query,
                "success": True,
                "response_time": response_time,
                "convergence_score": coherence.get("convergence_score"),
                "tier": coherence.get("tier"),
                "anchor_score": coherence.get("anchor_validation", {}).get("faithh_phase", {}).get("validation_score"),
                "signals": coherence.get("convergence_signals", [])
            }
            
        except Exception as e:
            return {
                "query": query,
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time
            }
    
    def benchmark_response_times(self, num_queries: int = 10) -> Dict[str, Any]:
        """Benchmark response times with sequential queries"""
        print(f"🚀 Running Response Time Benchmark ({num_queries} sequential queries)...")
        
        test_queries = [
            "What is FAITHH?",
            "Tell me about the Coherence Arbiter",
            "What are the current project states?",
            "How does the PULSE engine work?",
            "Explain the ML chip routing system",
            "What are the ChromaDB document counts?",
            "How does anchor validation work?",
            "What are the coherence tiers?",
            "Tell me about Phase 3 implementation",
            "How are coherence scores calculated?"
        ]
        
        results = []
        for i in range(num_queries):
            query = test_queries[i % len(test_queries)]
            result = self.single_query_test(query)
            results.append(result)
            
            if result["success"]:
                print(f"  Query {i+1}: {result['response_time']:.3f}s | Score: {result['convergence_score']:.3f} | Tier: {result['tier']}")
            else:
                print(f"  Query {i+1}: ❌ {result['error']}")
        
        # Calculate statistics
        successful_results = [r for r in results if r["success"]]
        failed_results = [r for r in results if not r["success"]]
        
        if successful_results:
            response_times = [r["response_time"] for r in successful_results]
            convergence_scores = [r["convergence_score"] for r in successful_results if r["convergence_score"] is not None]
            
            stats = {
                "total_queries": num_queries,
                "successful": len(successful_results),
                "failed": len(failed_results),
                "response_time": {
                    "mean": statistics.mean(response_times),
                    "median": statistics.median(response_times),
                    "min": min(response_times),
                    "max": max(response_times),
                    "std": statistics.stdev(response_times) if len(response_times) > 1 else 0
                },
                "coherence_scores": {
                    "mean": statistics.mean(convergence_scores) if convergence_scores else 0,
                    "min": min(convergence_scores) if convergence_scores else 0,
                    "max": max(convergence_scores) if convergence_scores else 0
                },
                "performance_rating": self._rate_performance(statistics.mean(response_times))
            }
        else:
            stats = {
                "total_queries": num_queries,
                "successful": 0,
                "failed": len(failed_results),
                "errors": [r["error"] for r in failed_results]
            }
        
        return stats
    
    def concurrent_load_test(self, num_concurrent: int = 5, queries_per_thread: int = 5) -> Dict[str, Any]:
        """Test system performance under concurrent load"""
        print(f"⚡ Running Concurrent Load Test ({num_concurrent} threads × {queries_per_thread} queries)...")
        
        test_queries = [
            "What is FAITHH?",
            "Tell me about the Coherence Arbiter",
            "What are the current project states?",
            "How does the PULSE engine work?",
            "Explain the ML chip routing system"
        ]
        
        def worker_thread(thread_id: int) -> List[Dict[str, Any]]:
            """Worker thread for concurrent testing"""
            thread_results = []
            for i in range(queries_per_thread):
                query = test_queries[i % len(test_queries)]
                result = self.single_query_test(query)
                result["thread_id"] = thread_id
                result["query_index"] = i
                thread_results.append(result)
            return thread_results
        
        # Run concurrent threads
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(worker_thread, i) for i in range(num_concurrent)]
            all_results = []
            
            for future in as_completed(futures):
                try:
                    thread_results = future.result()
                    all_results.extend(thread_results)
                except Exception as e:
                    print(f"  Thread error: {e}")
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful_results = [r for r in all_results if r["success"]]
        failed_results = [r for r in all_results if not r["success"]]
        
        if successful_results:
            response_times = [r["response_time"] for r in successful_results]
            
            stats = {
                "total_queries": num_concurrent * queries_per_thread,
                "concurrent_threads": num_concurrent,
                "queries_per_thread": queries_per_thread,
                "total_test_time": total_time,
                "successful": len(successful_results),
                "failed": len(failed_results),
                "queries_per_second": len(successful_results) / total_time if total_time > 0 else 0,
                "response_time": {
                    "mean": statistics.mean(response_times),
                    "median": statistics.median(response_times),
                    "min": min(response_times),
                    "max": max(response_times),
                    "std": statistics.stdev(response_times) if len(response_times) > 1 else 0
                },
                "concurrent_performance_rating": self._rate_performance(statistics.mean(response_times))
            }
        else:
            stats = {
                "total_queries": num_concurrent * queries_per_thread,
                "successful": 0,
                "failed": len(failed_results),
                "total_test_time": total_time,
                "errors": [r["error"] for r in failed_results]
            }
        
        return stats
    
    def _rate_performance(self, avg_response_time: float) -> str:
        """Rate performance based on average response time"""
        if avg_response_time < 1.0:
            return "🟢 EXCELLENT (<1s)"
        elif avg_response_time < 2.0:
            return "🟡 GOOD (<2s)"
        elif avg_response_time < 5.0:
            return "🟠 ACCEPTABLE (<5s)"
        else:
            return "🔴 SLOW (>5s)"
    
    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive performance benchmark"""
        print("🎯 Coherence Arbiter Performance Benchmark")
        print("=" * 50)
        
        # Sequential benchmark
        sequential_results = self.benchmark_response_times(10)
        print()
        
        # Concurrent load test
        concurrent_results = self.concurrent_load_test(3, 3)
        print()
        
        # Summary
        print("📊 PERFORMANCE SUMMARY")
        print("=" * 50)
        
        if sequential_results.get("successful", 0) > 0:
            seq_time = sequential_results["response_time"]["mean"]
            seq_rating = sequential_results["performance_rating"]
            print(f"Sequential Queries: {seq_time:.3f}s avg {seq_rating}")
        
        if concurrent_results.get("successful", 0) > 0:
            conc_time = concurrent_results["response_time"]["mean"]
            conc_rating = concurrent_results["concurrent_performance_rating"]
            qps = concurrent_results["queries_per_second"]
            print(f"Concurrent Queries: {conc_time:.3f}s avg {conc_rating}")
            print(f"Throughput: {qps:.1f} queries/second")
        
        # Recommendations
        print()
        print("🔍 PERFORMANCE RECOMMENDATIONS:")
        
        if sequential_results.get("response_time", {}).get("mean", 0) > 3.0:
            print("  ⚠️  Consider optimizing sequential response times")
        
        if concurrent_results.get("response_time", {}).get("mean", 0) > 5.0:
            print("  ⚠️  Consider optimizing for concurrent load")
        
        if concurrent_results.get("queries_per_second", 0) < 1.0:
            print("  ⚠️  Low throughput - investigate bottlenecks")
        
        total_failed = sequential_results.get("failed", 0) + concurrent_results.get("failed", 0)
        if total_failed > 0:
            print(f"  ⚠️  {total_failed} failed queries - investigate errors")
        
        if sequential_results.get("successful", 0) == sequential_results.get("total_queries", 0):
            print("  ✅ All sequential queries successful")
        
        if concurrent_results.get("successful", 0) == concurrent_results.get("total_queries", 0):
            print("  ✅ All concurrent queries successful")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "sequential": sequential_results,
            "concurrent": concurrent_results
        }

def main():
    """Run performance benchmark"""
    tester = CoherencePerformanceTester()
    results = tester.run_comprehensive_benchmark()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"benchmark_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    main()

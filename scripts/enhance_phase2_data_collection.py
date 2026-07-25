#!/usr/bin/env python3
"""
Phase 2 Data Collection Enhancement Script

This script systematically generates diverse queries to accelerate Phase 2 
data collection toward the 50-sample training target. Focuses on ALIFE 
experiment-related queries across all intent types to maximize data quality.

Usage: python enhance_phase2_data_collection.py [--samples 20] [--diversify]
"""

import sys
import os
import argparse
import json
import time
import requests
from datetime import datetime
from typing import List, Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Phase2DataCollector:
    """Systematic Phase 2 data collection with ALIFE experiment focus."""
    
    def __init__(self, backend_url: str = "http://localhost:5557"):
        self.backend_url = backend_url
        self.session = requests.Session()
        
        # Adaptive timeout configuration
        self.timeouts = {
            "low": 30,      # 30 seconds for simple queries
            "medium": 60,   # 60 seconds for medium complexity
            "high": 120     # 120 seconds for complex queries
        }
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delays = [5, 15, 30]  # Exponential backoff
        
    def generate_alife_queries(self) -> List[Dict[str, str]]:
        """Generate diverse ALIFE experiment queries across intent types."""
        
        queries = [
            # ALIFE-specific queries (alife_query intent)
            {
                "message": "What were the key findings of Experiment 6 on cognitive specialization?",
                "intent_target": "alife_query",
                "complexity": "high"
            },
            {
                "message": "How did Fibonacci frequency ratios affect agent behavior in Experiment 6?",
                "intent_target": "alife_query", 
                "complexity": "high"
            },
            {
                "message": "Compare the results of Experiments 4, 5, and 6 in terms of emergence patterns.",
                "intent_target": "alife_query",
                "complexity": "high"
            },
            {
                "message": "What mathematical cognition emerged in the Fibonacci zone experiment?",
                "intent_target": "alife_query",
                "complexity": "high"
            },
            
            # Project/next action queries (next_action_query, project_query)
            {
                "message": "What should be the next experiment after cognitive specialization?",
                "intent_target": "next_action_query",
                "complexity": "medium"
            },
            {
                "message": "How can we improve the ALIFE experimental design for better results?",
                "intent_target": "project_query",
                "complexity": "medium"
            },
            {
                "message": "What infrastructure is needed for Experiment 7 on advanced mathematical cognition?",
                "intent_target": "project_query",
                "complexity": "medium"
            },
            
            # Why questions (why_question)
            {
                "message": "Why did cognitive specialization emerge at tick 200 in Experiment 6?",
                "intent_target": "why_question",
                "complexity": "high"
            },
            {
                "message": "Why did agents prefer Zone 5 over other Fibonacci zones?",
                "intent_target": "why_question",
                "complexity": "high"
            },
            {
                "message": "Why is mathematical cognition evolution significant for ALIFE research?",
                "intent_target": "why_question",
                "complexity": "medium"
            },
            
            # Complex/analysis queries (complex_query)
            {
                "message": "Analyze the relationship between Fibonacci ratios and cognitive specialization rates.",
                "intent_target": "complex_query",
                "complexity": "high"
            },
            {
                "message": "Compare the energy efficiency of specialized vs generalist agents in Experiment 6.",
                "intent_target": "complex_query",
                "complexity": "high"
            },
            {
                "message": "Evaluate the scientific implications of mathematical cognition emergence.",
                "intent_target": "complex_query",
                "complexity": "high"
            },
            
            # Constella queries (constella_query)
            {
                "message": "How do ALIFE experiment results relate to the Constella framework principles?",
                "intent_target": "constella_query",
                "complexity": "medium"
            },
            {
                "message": "What governance insights can be drawn from cognitive specialization patterns?",
                "intent_target": "constella_query",
                "complexity": "medium"
            },
            
            # Business/technical queries (business_query, technical_query)
            {
                "message": "What are the commercial applications of mathematical cognition research?",
                "intent_target": "business_query",
                "complexity": "medium"
            },
            {
                "message": "How can the Fibonacci zone implementation be optimized for performance?",
                "intent_target": "technical_query",
                "complexity": "medium"
            },
            
            # Recent changes queries (recent_changes_query)
            {
                "message": "What were the recent changes to the ALIFE experimental framework?",
                "intent_target": "recent_changes_query",
                "complexity": "low"
            },
            {
                "message": "How has the Phase 2 data collection progressed this week?",
                "intent_target": "recent_changes_query",
                "complexity": "low"
            }
        ]
        
        return queries
    
    def generate_system_queries(self) -> List[Dict[str, str]]:
        """Generate system-level queries for broader intent coverage."""
        
        queries = [
            # Self-awareness queries (self_query)
            {
                "message": "What has FAITHH learned from the ALIFE experiments?",
                "intent_target": "self_query",
                "complexity": "medium"
            },
            {
                "message": "How has the Phase 2 system improved through ALIFE data collection?",
                "intent_target": "self_query",
                "complexity": "medium"
            },
            
            # System status queries
            {
                "message": "What is the current status of all FAITHH system components?",
                "intent_target": "project_query",
                "complexity": "low"
            },
            {
                "message": "How is the backend performing with the current Phase 2 load?",
                "intent_target": "technical_query",
                "complexity": "low"
            }
        ]
        
        return queries
    
    def execute_query(self, query: Dict[str, str]) -> Dict[str, Any]:
        """Execute a single query against the backend with adaptive timeout and retry logic."""
        
        complexity = query.get("complexity", "medium")
        timeout = self.timeouts.get(complexity, 60)
        
        for attempt in range(self.max_retries + 1):
            try:
                print(f"  Attempt {attempt + 1}/{self.max_retries + 1} (timeout: {timeout}s)...")
                
                response = self.session.post(
                    f"{self.backend_url}/api/chat",
                    json={"message": query["message"]},
                    headers={"Content-Type": "application/json"},
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "query": query["message"],
                        "intent_target": query["intent_target"],
                        "complexity": query["complexity"],
                        "response_length": len(result.get("response", "")),
                        "attempts": attempt + 1,
                        "timeout_used": timeout,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    print(f"  ❌ Failed: {error_msg}")
                    
                    if attempt < self.max_retries:
                        delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                        print(f"  ⏳ Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        return {
                            "success": False,
                            "query": query["message"],
                            "error": error_msg,
                            "attempts": attempt + 1,
                            "timeout_used": timeout,
                            "timestamp": datetime.now().isoformat()
                        }
                        
            except requests.exceptions.Timeout as e:
                error_msg = f"Timeout after {timeout}s: {e}"
                print(f"  ⏰ {error_msg}")
                
                if attempt < self.max_retries:
                    # Increase timeout for retry
                    timeout = min(timeout * 1.5, 180)  # Cap at 180 seconds
                    delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                    print(f"  ⏳ Retrying in {delay}s with timeout {timeout}s...")
                    time.sleep(delay)
                else:
                    return {
                        "success": False,
                        "query": query["message"],
                        "error": error_msg,
                        "attempts": attempt + 1,
                        "timeout_used": timeout,
                        "timestamp": datetime.now().isoformat()
                    }
                    
            except Exception as e:
                error_msg = str(e)
                print(f"  ❌ Unexpected error: {error_msg}")
                
                if attempt < self.max_retries:
                    delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                    print(f"  ⏳ Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    return {
                        "success": False,
                        "query": query["message"],
                        "error": error_msg,
                        "attempts": attempt + 1,
                        "timeout_used": timeout,
                        "timestamp": datetime.now().isoformat()
                    }
        
        # This should never be reached
        return {
            "success": False,
            "query": query["message"],
            "error": "Unknown error in execute_query",
            "timestamp": datetime.now().isoformat()
        }
    
    def collect_data(self, target_samples: int = 20, diversify: bool = True) -> Dict[str, Any]:
        """Collect Phase 2 data with systematic query execution."""
        
        print("🚀 Phase 2 Data Collection Enhancement")
        print("=" * 50)
        print(f"Target samples: {target_samples}")
        print(f"Diversify intents: {diversify}")
        print(f"Backend: {self.backend_url}")
        print("=" * 50)
        
        # Generate query pool
        alife_queries = self.generate_alife_queries()
        system_queries = self.generate_system_queries() if diversify else []
        
        all_queries = alife_queries + system_queries
        
        # Execute queries
        results = []
        intent_coverage = {}
        complexity_distribution = {"low": 0, "medium": 0, "high": 0}
        timeout_stats = {"timeouts": 0, "retries": 0, "total_attempts": 0}
        
        for i, query in enumerate(all_queries[:target_samples]):
            print(f"\n[{i+1}/{len(all_queries[:target_samples])}] Executing: {query['intent_target']}")
            print(f"Query: {query['message'][:80]}...")
            
            result = self.execute_query(query)
            results.append(result)
            
            # Track timeout and retry statistics
            timeout_stats["total_attempts"] += result.get("attempts", 1)
            if result.get("attempts", 1) > 1:
                timeout_stats["retries"] += 1
            if "timeout" in result.get("error", "").lower():
                timeout_stats["timeouts"] += 1
            
            if result["success"]:
                intent_type = result["intent_target"]
                complexity = result["complexity"]
                
                intent_coverage[intent_type] = intent_coverage.get(intent_type, 0) + 1
                complexity_distribution[complexity] += 1
                
                attempts = result.get("attempts", 1)
                timeout_used = result.get("timeout_used", 0)
                
                print(f"✅ Success (response: {result['response_length']} chars, attempts: {attempts}, timeout: {timeout_used}s)")
            else:
                attempts = result.get("attempts", 1)
                timeout_used = result.get("timeout_used", 0)
                print(f"❌ Failed: {result['error']} (attempts: {attempts}, timeout: {timeout_used}s)")
            
            # Small delay to avoid overwhelming the system
            time.sleep(1)
        
        # Generate report
        successful = sum(1 for r in results if r["success"])
        success_rate = successful / len(results) * 100
        
        print("\n" + "=" * 50)
        print("📊 COLLECTION SUMMARY")
        print("=" * 50)
        print(f"Queries executed: {len(results)}")
        print(f"Successful: {successful} ({success_rate:.1f}%)")
        print(f"Intent types covered: {len(intent_coverage)}")
        print(f"Intent distribution: {intent_coverage}")
        print(f"Complexity distribution: {complexity_distribution}")
        
        # Timeout analytics
        avg_attempts = timeout_stats["total_attempts"] / len(results) if results else 0
        timeout_rate = timeout_stats["timeouts"] / len(results) * 100 if results else 0
        retry_rate = timeout_stats["retries"] / len(results) * 100 if results else 0
        
        print(f"Timeout analytics:")
        print(f"  Timeouts: {timeout_stats['timeouts']} ({timeout_rate:.1f}%)")
        print(f"  Retries: {timeout_stats['retries']} ({retry_rate:.1f}%)")
        print(f"  Avg attempts per query: {avg_attempts:.1f}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"phase2_enhancement_report_{timestamp}.json"
        
        report_data = {
            "collection_time": datetime.now().isoformat(),
            "target_samples": target_samples,
            "queries_executed": len(results),
            "successful_queries": successful,
            "success_rate": success_rate,
            "intent_coverage": intent_coverage,
            "complexity_distribution": complexity_distribution,
            "timeout_stats": timeout_stats,
            "timeout_config": self.timeouts,
            "retry_config": {
                "max_retries": self.max_retries,
                "retry_delays": self.retry_delays
            },
            "results": results
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Report saved: {report_file}")
        
        return report_data
    
    def check_current_status(self) -> Dict[str, Any]:
        """Check current Phase 2 data collection status."""
        
        try:
            from backend.ml.performance_tracker import performance_tracker
            
            data = performance_tracker.get_recent_performance(limit=100)
            
            intents = {}
            for record in data:
                for k,v in record.intent.items():
                    if k.startswith('is_') and v:
                        intent_type = k[3:]
                        intents[intent_type] = intents.get(intent_type, 0) + 1
            
            return {
                "current_samples": len(data),
                "completion_rate": len(data) / 50 * 100,
                "intent_coverage": len(intents),
                "intent_distribution": intents,
                "samples_needed": max(0, 50 - len(data))
            }
            
        except Exception as e:
            return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Enhance Phase 2 data collection")
    parser.add_argument("--samples", type=int, default=20, help="Target samples to collect")
    parser.add_argument("--diversify", action="store_true", help="Include system-level queries")
    parser.add_argument("--check-only", action="store_true", help="Only check current status")
    
    args = parser.parse_args()
    
    collector = Phase2DataCollector()
    
    if args.check_only:
        status = collector.check_current_status()
        print("📊 Current Phase 2 Status:")
        print(f"Samples: {status.get('current_samples', 0)}/50 ({status.get('completion_rate', 0):.1f}%)")
        print(f"Intent coverage: {status.get('intent_coverage', 0)}/8 types")
        print(f"Intent distribution: {status.get('intent_distribution', {})}")
        print(f"Samples needed: {status.get('samples_needed', 50)}")
    else:
        # Check status first
        status = collector.check_current_status()
        if "error" not in status:
            print(f"📊 Current status: {status['current_samples']}/50 samples ({status['completion_rate']:.1f}%)")
            print(f"Intent coverage: {status['intent_coverage']}/8 types")
        
        # Collect data
        results = collector.collect_data(args.samples, args.diversify)
        
        print(f"\n🎯 Target achieved: {results['successful_queries']} new samples collected")
        print(f"📈 Progress update: Check status with --check-only")

if __name__ == "__main__":
    main()

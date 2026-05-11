#!/usr/bin/env python3
"""
Generate synthetic queries for missing intent types (business_query, recent_changes_query)
Use local Ollama to avoid Groq quota limitations
"""

import sys
import os
import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MissingIntentGenerator:
    """Generate synthetic queries for missing intent types using local Ollama"""
    
    def __init__(self, backend_url: str = "http://localhost:5557"):
        self.backend_url = backend_url
        self.session = requests.Session()
        
        # Missing intent queries
        self.missing_queries = [
            # Business queries
            {
                "message": "What are the current revenue projections for Tom Cat Sound LLC?",
                "intent_target": "business_query",
                "complexity": "medium"
            },
            {
                "message": "How should I structure pricing for audio production services?",
                "intent_target": "business_query",
                "complexity": "medium"
            },
            {
                "message": "What grants are available for audio engineering businesses?",
                "intent_target": "business_query",
                "complexity": "medium"
            },
            {
                "message": "How can I scale my client base for audio production?",
                "intent_target": "business_query",
                "complexity": "medium"
            },
            {
                "message": "What equipment investments make sense for the business?",
                "intent_target": "business_query",
                "complexity": "medium"
            },
            
            # Recent changes queries
            {
                "message": "What were the recent updates to the FAITHH backend?",
                "intent_target": "recent_changes_query",
                "complexity": "low"
            },
            {
                "message": "What changed in the ALIFE experiment infrastructure?",
                "intent_target": "recent_changes_query",
                "complexity": "low"
            },
            {
                "message": "What's the latest status of the Phase 2 implementation?",
                "intent_target": "recent_changes_query",
                "complexity": "low"
            },
            {
                "message": "What modifications were made to the ChromaDB configuration?",
                "intent_target": "recent_changes_query",
                "complexity": "low"
            },
            {
                "message": "What new features were added to the system recently?",
                "intent_target": "recent_changes_query",
                "complexity": "low"
            }
        ]
    
    def execute_query(self, query: Dict[str, str], timeout: int = 60) -> Dict[str, Any]:
        """Execute a single query against the backend using Ollama"""
        
        for attempt in range(3):  # 3 attempts max
            try:
                print(f"  Attempt {attempt + 1}/3 (timeout: {timeout}s)...")
                
                response = self.session.post(
                    f"{self.backend_url}/api/chat",
                    json={
                        "message": query["message"],
                        "provider": "ollama",  # Force Ollama to avoid Groq quota
                        "model": "qwen25-grounded:latest"
                    },
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
                        "response_preview": result.get("response", "")[:200] + "...",
                        "attempts": attempt + 1,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    print(f"  ❌ Failed: {error_msg}")
                    
                    if attempt < 2:
                        print(f"  ⏳ Retrying in 5s...")
                        time.sleep(5)
                    else:
                        return {
                            "success": False,
                            "query": query["message"],
                            "error": error_msg,
                            "attempts": attempt + 1,
                            "timestamp": datetime.now().isoformat()
                        }
                        
            except requests.exceptions.Timeout as e:
                error_msg = f"Timeout after {timeout}s: {e}"
                print(f"  ⏰ {error_msg}")
                
                if attempt < 2:
                    timeout = min(timeout * 1.5, 120)  # Increase timeout
                    print(f"  ⏳ Retrying in 5s with timeout {timeout}s...")
                    time.sleep(5)
                else:
                    return {
                        "success": False,
                        "query": query["message"],
                        "error": error_msg,
                        "attempts": attempt + 1,
                        "timestamp": datetime.now().isoformat()
                    }
                    
            except Exception as e:
                error_msg = str(e)
                print(f"  ❌ Unexpected error: {error_msg}")
                
                if attempt < 2:
                    print(f"  ⏳ Retrying in 5s...")
                    time.sleep(5)
                else:
                    return {
                        "success": False,
                        "query": query["message"],
                        "error": error_msg,
                        "attempts": attempt + 1,
                        "timestamp": datetime.now().isoformat()
                    }
        
        return {
            "success": False,
            "query": query["message"],
            "error": "Unknown error in execute_query",
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_missing_intents(self) -> Dict[str, Any]:
        """Generate synthetic queries for missing intent types"""
        
        print("🔧 Generating Missing Intent Queries")
        print("=" * 50)
        print(f"Backend: {self.backend_url}")
        print(f"Queries to generate: {len(self.missing_queries)}")
        print("Provider: Ollama (local, avoiding Groq quota)")
        print("=" * 50)
        
        results = []
        intent_coverage = {}
        
        for i, query in enumerate(self.missing_queries, 1):
            print(f"\n[{i}/{len(self.missing_queries)}] Generating: {query['intent_target']}")
            print(f"Query: {query['message']}")
            
            result = self.execute_query(query)
            results.append(result)
            
            if result["success"]:
                intent_type = result["intent_target"]
                intent_coverage[intent_type] = intent_coverage.get(intent_type, 0) + 1
                
                print(f"✅ Success ({result['response_length']} chars)")
                print(f"   Preview: {result['response_preview']}")
            else:
                print(f"❌ Failed: {result['error']}")
            
            # Small delay to avoid overwhelming the system
            time.sleep(1)
        
        # Generate summary
        successful = sum(1 for r in results if r["success"])
        success_rate = successful / len(results) * 100
        
        print(f"\n{'=' * 50}")
        print(f"📊 GENERATION SUMMARY")
        print(f"{'=' * 50}")
        print(f"Queries executed: {len(results)}")
        print(f"Successful: {successful} ({success_rate:.1f}%)")
        print(f"Intent types covered: {len(intent_coverage)}")
        print(f"Intent distribution: {intent_coverage}")
        
        if successful > 0:
            avg_response_length = sum(r.get('response_length', 0) for r in results if r["success"]) / successful
            print(f"Avg response length: {avg_response_length:.0f} chars")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"missing_intents_generation_report_{timestamp}.json"
        
        report_data = {
            "generation_time": datetime.now().isoformat(),
            "queries_executed": len(results),
            "successful_queries": successful,
            "success_rate": success_rate,
            "intent_coverage": intent_coverage,
            "provider_used": "ollama",
            "model_used": "qwen25-grounded:latest",
            "results": results
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Report saved: {report_file}")
        
        return report_data

def main():
    """Main execution function"""
    
    generator = MissingIntentGenerator()
    results = generator.generate_missing_intents()
    
    success_rate = results.get("success_rate", 0)
    print(f"\n🎯 Generation Result: {'SUCCESS' if success_rate >= 80 else 'PARTIAL'} ({success_rate:.1f}% success rate)")
    
    return success_rate >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

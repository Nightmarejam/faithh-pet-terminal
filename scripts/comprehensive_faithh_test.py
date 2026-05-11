#!/usr/bin/env python3
"""
Comprehensive FAITHH System Test
Tests backend, RAG, LLM providers, and response quality
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple

# Configuration
BACKEND_URL = "http://localhost:5557"
CHROMADB_URL = "http://192.158.1.243:8000"

# Test queries designed to check for hallucinations and accuracy
TEST_QUERIES = [
    {
        "query": "What is FAITHH and what does it stand for?",
        "category": "self_awareness",
        "expected_keywords": ["Friendly", "AI", "Teaching", "Helping", "Hub"],
        "should_not_contain": ["random", "unknown", "not sure"]
    },
    {
        "query": "How many chunks are in the ChromaDB knowledge base?",
        "category": "factual_accuracy",
        "expected_keywords": ["32499", "32,499", "chunks"],
        "should_not_contain": ["208", "29041", "guess"]
    },
    {
        "query": "What LLM providers does FAITHH support?",
        "category": "technical_knowledge",
        "expected_keywords": ["Groq", "Ollama", "Gemini"],
        "should_not_contain": ["OpenAI", "Anthropic", "Claude"]
    },
    {
        "query": "Tell me about the Gen8 server infrastructure",
        "category": "infrastructure_knowledge",
        "expected_keywords": ["Gen8", "ChromaDB", "services", "192.158.1.243"],
        "should_not_contain": ["localhost", "unknown"]
    },
    {
        "query": "What is the Tom Cat Sound LLC project?",
        "category": "project_awareness",
        "expected_keywords": ["audio", "business", "production"],
        "should_not_contain": ["don't know", "not familiar"]
    }
]

class FAITHHSystemTest:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "backend_health": {},
            "chromadb_health": {},
            "rag_tests": [],
            "response_quality": [],
            "hallucination_check": [],
            "summary": {}
        }
    
    def test_backend_health(self) -> bool:
        """Test backend /health endpoint"""
        print("\n🔍 Testing Backend Health...")
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.results["backend_health"] = {
                    "status": "✅ PASS",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "data": data
                }
                print(f"   ✅ Backend healthy (response: {response.elapsed.total_seconds()*1000:.0f}ms)")
                return True
            else:
                self.results["backend_health"] = {
                    "status": "❌ FAIL",
                    "error": f"Status code: {response.status_code}"
                }
                print(f"   ❌ Backend unhealthy: {response.status_code}")
                return False
        except Exception as e:
            self.results["backend_health"] = {
                "status": "❌ FAIL",
                "error": str(e)
            }
            print(f"   ❌ Backend error: {e}")
            return False
    
    def test_backend_status(self) -> bool:
        """Test backend /api/status endpoint"""
        print("\n🔍 Testing Backend Status API...")
        try:
            response = requests.get(f"{BACKEND_URL}/api/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                chromadb_docs = data.get("services", {}).get("chromadb", {}).get("documents", 0)
                
                self.results["backend_status"] = {
                    "status": "✅ PASS",
                    "chromadb_documents": chromadb_docs,
                    "services": data.get("services", {})
                }
                print(f"   ✅ Status API working")
                print(f"   📊 ChromaDB documents: {chromadb_docs}")
                return True
            else:
                self.results["backend_status"] = {
                    "status": "❌ FAIL",
                    "error": f"Status code: {response.status_code}"
                }
                print(f"   ❌ Status API failed: {response.status_code}")
                return False
        except Exception as e:
            self.results["backend_status"] = {
                "status": "❌ FAIL",
                "error": str(e)
            }
            print(f"   ❌ Status API error: {e}")
            return False
    
    def test_chromadb_direct(self) -> bool:
        """Test ChromaDB directly"""
        print("\n🔍 Testing ChromaDB Direct Connection...")
        try:
            # Heartbeat
            response = requests.get(f"{CHROMADB_URL}/api/v2/heartbeat", timeout=5)
            if response.status_code != 200:
                print(f"   ❌ ChromaDB heartbeat failed: {response.status_code}")
                return False
            
            # Use Python client to check collection
            import chromadb
            client = chromadb.HttpClient(host='192.158.1.243', port=8000)
            collection = client.get_collection('faithh_knowledge_base')
            count = collection.count()
            
            self.results["chromadb_health"] = {
                "status": "✅ PASS",
                "collection": "faithh_knowledge_base",
                "document_count": count
            }
            print(f"   ✅ ChromaDB healthy")
            print(f"   📊 Collection: faithh_knowledge_base ({count} documents)")
            return True
        except Exception as e:
            self.results["chromadb_health"] = {
                "status": "❌ FAIL",
                "error": str(e)
            }
            print(f"   ❌ ChromaDB error: {e}")
            return False
    
    def test_rag_query(self, query: str) -> Dict:
        """Test RAG query endpoint"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/rag/query",
                json={"query": query, "n_results": 5},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "✅ PASS",
                    "query": query,
                    "results_count": len(data.get("results", [])),
                    "response_time_ms": response.elapsed.total_seconds() * 1000
                }
            else:
                return {
                    "status": "❌ FAIL",
                    "query": query,
                    "error": f"Status code: {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "❌ FAIL",
                "query": query,
                "error": str(e)
            }
    
    def test_chat_response(self, query: str, use_rag: bool = True) -> Dict:
        """Test chat endpoint with quality checks"""
        print(f"\n🔍 Testing: {query[:50]}...")
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/chat",
                json={
                    "message": query,
                    "model": "groq/llama-3.3-70b-versatile",
                    "use_rag": use_rag
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "")
                
                result = {
                    "status": "✅ PASS",
                    "query": query,
                    "response_length": len(response_text),
                    "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "used_rag": use_rag
                }
                
                print(f"   ✅ Response received ({len(response_text)} chars, {response.elapsed.total_seconds()*1000:.0f}ms)")
                print(f"   📝 Preview: {response_text[:100]}...")
                
                return result
            else:
                print(f"   ❌ Chat failed: {response.status_code}")
                return {
                    "status": "❌ FAIL",
                    "query": query,
                    "error": f"Status code: {response.status_code}"
                }
        except Exception as e:
            print(f"   ❌ Chat error: {e}")
            return {
                "status": "❌ FAIL",
                "query": query,
                "error": str(e)
            }
    
    def check_hallucination(self, test_case: Dict, response_text: str) -> Dict:
        """Check for hallucinations in response"""
        query = test_case["query"]
        expected = test_case["expected_keywords"]
        forbidden = test_case["should_not_contain"]
        
        response_lower = response_text.lower()
        
        # Check for expected keywords
        found_keywords = [kw for kw in expected if kw.lower() in response_lower]
        missing_keywords = [kw for kw in expected if kw.lower() not in response_lower]
        
        # Check for forbidden content (hallucinations)
        hallucinations = [word for word in forbidden if word.lower() in response_lower]
        
        accuracy_score = len(found_keywords) / len(expected) if expected else 0
        has_hallucinations = len(hallucinations) > 0
        
        result = {
            "query": query,
            "category": test_case["category"],
            "accuracy_score": accuracy_score,
            "found_keywords": found_keywords,
            "missing_keywords": missing_keywords,
            "hallucinations": hallucinations,
            "has_hallucinations": has_hallucinations,
            "verdict": "✅ ACCURATE" if accuracy_score >= 0.5 and not has_hallucinations else "⚠️ ISSUES DETECTED"
        }
        
        return result
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("=" * 60)
        print("🧪 FAITHH COMPREHENSIVE SYSTEM TEST")
        print("=" * 60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Phase 1: Infrastructure Tests
        print("\n" + "=" * 60)
        print("PHASE 1: INFRASTRUCTURE TESTS")
        print("=" * 60)
        
        backend_ok = self.test_backend_health()
        status_ok = self.test_backend_status()
        chromadb_ok = self.test_chromadb_direct()
        
        if not (backend_ok and status_ok and chromadb_ok):
            print("\n❌ Infrastructure tests failed. Aborting.")
            return
        
        # Phase 2: RAG Tests
        print("\n" + "=" * 60)
        print("PHASE 2: RAG QUERY TESTS")
        print("=" * 60)
        
        for test_case in TEST_QUERIES[:3]:  # Test first 3 RAG queries
            rag_result = self.test_rag_query(test_case["query"])
            self.results["rag_tests"].append(rag_result)
            print(f"   {rag_result['status']} - {test_case['query'][:50]}...")
            time.sleep(1)  # Rate limiting
        
        # Phase 3: Response Quality Tests
        print("\n" + "=" * 60)
        print("PHASE 3: RESPONSE QUALITY & HALLUCINATION TESTS")
        print("=" * 60)
        
        for test_case in TEST_QUERIES:
            # Get response
            chat_result = self.test_chat_response(test_case["query"], use_rag=True)
            self.results["response_quality"].append(chat_result)
            
            if chat_result["status"] == "✅ PASS":
                # Check for hallucinations
                hallucination_check = self.check_hallucination(
                    test_case,
                    chat_result["response_preview"]
                )
                self.results["hallucination_check"].append(hallucination_check)
                
                print(f"   {hallucination_check['verdict']} - Accuracy: {hallucination_check['accuracy_score']:.0%}")
                if hallucination_check['hallucinations']:
                    print(f"   ⚠️  Hallucinations detected: {hallucination_check['hallucinations']}")
            
            time.sleep(2)  # Rate limiting
        
        # Generate Summary
        self.generate_summary()
        self.save_results()
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.results["response_quality"])
        passed_tests = sum(1 for t in self.results["response_quality"] if t["status"] == "✅ PASS")
        
        hallucination_tests = len(self.results["hallucination_check"])
        accurate_responses = sum(1 for h in self.results["hallucination_check"] if not h["has_hallucinations"])
        
        avg_accuracy = sum(h["accuracy_score"] for h in self.results["hallucination_check"]) / hallucination_tests if hallucination_tests > 0 else 0
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "pass_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "hallucination_tests": hallucination_tests,
            "accurate_responses": accurate_responses,
            "hallucination_rate": (hallucination_tests - accurate_responses) / hallucination_tests if hallucination_tests > 0 else 0,
            "average_accuracy": avg_accuracy,
            "overall_verdict": "✅ EXCELLENT" if avg_accuracy >= 0.8 and accurate_responses >= hallucination_tests * 0.8 else "⚠️ NEEDS IMPROVEMENT"
        }
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ({self.results['summary']['pass_rate']:.0%})")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"\nHallucination Analysis:")
        print(f"  Accurate Responses: {accurate_responses}/{hallucination_tests}")
        print(f"  Hallucination Rate: {self.results['summary']['hallucination_rate']:.0%}")
        print(f"  Average Accuracy: {avg_accuracy:.0%}")
        print(f"\n{self.results['summary']['overall_verdict']}")
    
    def save_results(self):
        """Save test results to file"""
        filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = f"docs/testing/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to: {filepath}")

if __name__ == "__main__":
    tester = FAITHHSystemTest()
    tester.run_all_tests()

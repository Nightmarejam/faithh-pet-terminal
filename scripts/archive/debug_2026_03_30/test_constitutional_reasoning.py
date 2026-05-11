#!/usr/bin/env python3
"""Test constitutional reasoning endpoint"""

import requests
import json

def test_constitutional_reasoning():
    """Test governance queries with constitutional reasoning"""
    
    base_url = "http://localhost:5557"
    
    # Test queries that should trigger constitutional reasoning
    governance_queries = [
        "What is the Universal Civic Floor and how does it work?",
        "Explain the Penumbra Accord and its role in governance",
        "What constitutional principles support diversity floors?",
        "How do tokens work in the Astris/Auctor system?",
        "What is the three-mechanism system for stability?",
        "Explain gamer lifecycle and minimum compliance",
        "What does the Civic Tome do for governance?",
        "How does strategy escape work as a survival mechanism?"
    ]
    
    print("=" * 60)
    print("CONSTITUTIONAL REASONING TEST")
    print("=" * 60)
    
    for i, query in enumerate(governance_queries, 1):
        print(f"\nTest {i}: {query}")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{base_url}/api/chat",
                json={
                    "message": query,
                    "use_rag": True,
                    "model": "qwen25-grounded:latest"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if constitutional reasoning was triggered
                constitutional = data.get('constitutional_reasoning')
                if constitutional:
                    print(f"✅ Constitutional reasoning activated")
                    print(f"   Principles retrieved: {constitutional['principles_retrieved']}")
                    print(f"   Mechanisms: {', '.join(constitutional['mechanisms'])}")
                    print(f"   Supporting experiments: {', '.join(constitutional['supporting_experiments'])}")
                    
                    # Show principle details
                    for principle in constitutional['principles'][:2]:  # Show first 2
                        print(f"   - {principle['title']} (confidence: {principle['confidence']})")
                else:
                    print("⚠️  No constitutional reasoning detected")
                
                # Show integrations used
                integrations = data.get('integrations_used', [])
                print(f"   Integrations: {', '.join(integrations)}")
                
                # Show RAG results
                rag_results = data.get('rag_results', [])
                print(f"   RAG results: {len(rag_results)} documents")
                
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except requests.exceptions.Timeout:
            print("⏰ Request timed out")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    test_constitutional_reasoning()

#!/usr/bin/env python3
"""Simple test for constitutional reasoning"""

import requests
import json

def test_single_query():
    """Test a single governance query"""
    
    query = "What is the Universal Civic Floor?"
    
    response = requests.post(
        "http://localhost:5557/api/chat",
        json={
            "message": query,
            "use_rag": True
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Query: {query}")
        print(f"Constitutional reasoning present: {'constitutional_reasoning' in data}")
        print(f"Integrations used: {data.get('integrations_used', [])}")
        
        if 'constitutional_reasoning' in data:
            const_data = data['constitutional_reasoning']
            print(f"Principles retrieved: {const_data.get('principles_retrieved', 0)}")
            print(f"Mechanisms: {const_data.get('mechanisms', [])}")
        else:
            print("❌ No constitutional reasoning detected")
            
        # Show some response content
        response_text = data.get('response', '')[:200]
        print(f"Response preview: {response_text}...")
        
    else:
        print(f"❌ Request failed: {response.status_code}")

if __name__ == '__main__':
    test_single_query()

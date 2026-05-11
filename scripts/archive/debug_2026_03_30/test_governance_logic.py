#!/usr/bin/env python3
"""Test the governance keyword detection logic directly"""

# Test the exact logic from smart_rag_query
def test_governance_detection():
    query_text = "What is the Universal Civic Floor?"
    
    governance_keywords = [
        'constitution', 'constitutional', 'governance', 'governing', 'ucf', 'penumbra', 
        'civic tome', 'astris', 'auctor', 'token', 'floor', 'diversity floor',
        'principle', 'framework', 'charter', 'bylaws', 'rules', 'regulation',
        'gamer', 'minimum compliance', 'structural', 'mechanism', 'policy',
        'governance design', 'participation', 'civic', 'democratic', 'decision making'
    ]
    
    query_lower = query_text.lower()
    is_governance_query = any(keyword in query_lower for keyword in governance_keywords)
    
    print(f"Query: {query_text}")
    print(f"Query lower: {query_lower}")
    print(f"Keywords found: {[k for k in governance_keywords if k in query_lower]}")
    print(f"Is governance query: {is_governance_query}")
    
    # Test constitutional collection query
    if is_governance_query:
        print("\nTesting constitutional collection query...")
        try:
            import chromadb
            client = chromadb.HttpClient(host='192.158.1.243', port=8000)
            collection = client.get_collection('faithh_knowledge_base')
            
            results = collection.query(
                query_texts=[query_text],
                n_results=5,
                where={"domain": "constella_constitutional"}
            )
            
            print(f"Constitutional results: {len(results['documents'][0]) if results['documents'] else 0}")
            if results['documents'] and results['documents'][0]:
                print(f"First document preview: {results['documents'][0][0][:100]}...")
            else:
                print("No documents found")
                
        except Exception as e:
            print(f"Error querying constitutional collection: {e}")

if __name__ == '__main__':
    test_governance_detection()

#!/usr/bin/env python3
"""
Test ALife Results Indexing
===========================
Verify that ALife experiment results were indexed correctly.
"""

import chromadb

def test_alife_indexing():
    """Test that ALife documents were indexed correctly"""
    
    print("🔍 Testing ALife Results Indexing")
    print("=" * 40)
    
    try:
        # Connect to ChromaDB
        chroma_client = chromadb.HttpClient(host="100.79.85.32", port=8000)
        collection = chroma_client.get_collection(name="faithh_knowledge_base")
        
        # Get the Experiment 3 document
        result = collection.get(ids=["exp3_verified_results"])
        
        if result['ids']:
            print("✅ Found exp3_verified_results document")
            content = result['documents'][0]
            print(f"📄 Content preview: {content[:200]}...")
            
            # Check for specific values
            expected_values = [
                "873 agents",
                "443,708",
                "443,035",
                "129,345",
                "tick 402",
                "agent_861",
                "gap=-2",
                "138.5%",
                "tick 85,000"
            ]
            
            print(f"\n🔍 Checking for expected values:")
            found_values = []
            for value in expected_values:
                if value in content:
                    found_values.append(value)
                    print(f"   ✅ Found: {value}")
                else:
                    print(f"   ❌ Missing: {value}")
            
            print(f"\n📊 Found {len(found_values)}/{len(expected_values)} expected values")
            
            # Test search
            print(f"\n🔍 Testing search for 'Experiment 3'...")
            search_results = collection.query(
                query_texts=["Experiment 3 Anticipation Gap"],
                n_results=3
            )
            
            if search_results['ids'][0]:
                print(f"✅ Search returned {len(search_results['ids'][0])} results")
                for i, doc_id in enumerate(search_results['ids'][0]):
                    print(f"   Result {i+1}: {doc_id}")
            else:
                print("❌ Search returned no results")
            
        else:
            print("❌ exp3_verified_results document not found")
        
        # Check total collection count
        total_count = collection.count()
        print(f"\n📚 Total collection count: {total_count}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_alife_indexing()

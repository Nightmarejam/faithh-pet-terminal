#!/usr/bin/env python3
"""Test Google Search API integration"""

import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_google_search():
    """Test Google Search API functionality"""
    print("🧪 Testing Google Search API Integration")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    # Check API keys
    api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
    search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
    
    print(f"API Key configured: {'✅' if api_key and api_key != 'your_google_search_api_key_here' else '❌'}")
    print(f"Search Engine ID configured: {'✅' if search_engine_id and search_engine_id != 'your_search_engine_id_here' else '❌'}")
    
    if not api_key or api_key == 'your_google_search_api_key_here':
        print("❌ Please configure GOOGLE_SEARCH_API_KEY in .env")
        return False
    
    if not search_engine_id or search_engine_id == 'your_search_engine_id_here':
        print("❌ Please configure GOOGLE_SEARCH_ENGINE_ID in .env")
        return False
    
    try:
        from google_search import GoogleSearchAPI
        
        # Initialize API
        search_api = GoogleSearchAPI()
        print("✅ Google Search API initialized successfully")
        
        # Test usage stats
        stats = search_api.get_usage_stats()
        print(f"📊 Usage Stats: {stats}")
        
        # Test search
        print("\n🔍 Testing search query...")
        result = search_api.search("Python programming", 3)
        
        if 'error' in result:
            print(f"❌ Search failed: {result['error']}")
            return False
        
        print(f"✅ Search successful!")
        print(f"📈 Results found: {result.get('total_results', 0)}")
        print(f"⏱️ Search time: {result.get('search_time', 0):.2f}s")
        
        if result.get('results'):
            print("\n📋 Sample results:")
            for i, item in enumerate(result['results'][:2], 1):
                print(f"{i}. {item.get('title', 'No title')}")
                print(f"   {item.get('snippet', 'No snippet')[:100]}...")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import google_search: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_google_search()
    print(f"\n🎯 Test result: {'PASSED' if success else 'FAILED'}")

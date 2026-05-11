#!/usr/bin/env python3
"""Test Google Search API configuration and functionality"""

import os
import sys
from dotenv import load_dotenv

def test_google_search_config():
    """Test Google Search API configuration"""
    print("🔍 Testing Google Search API Configuration")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    # Check API key
    api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
    search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
    
    print(f"API Key: {'✅ Configured' if api_key else '❌ Missing'}")
    print(f"Search Engine ID: {'✅ Configured' if search_engine_id else '❌ Missing'}")
    
    if api_key:
        print(f"API Key format: {'✅ Valid format' if api_key.startswith('AQ.Ab8') else '❌ Invalid format'}")
    
    if search_engine_id:
        print(f"Engine ID format: {'✅ Valid format' if search_engine_id != 'your_custom_search_engine_id_here' else '❌ Placeholder'}")
    
    # Test import and initialization
    try:
        from google_search import GoogleSearchAPI
        search_api = GoogleSearchAPI()
        stats = search_api.get_usage_stats()
        
        print(f"\n📊 API Status:")
        print(f"  Available: {'✅' if stats.get('api_configured') else '❌'}")
        print(f"  Daily Limit: {stats.get('daily_limit', 0)}")
        print(f"  Requests Today: {stats.get('requests_today', 0)}")
        print(f"  Requests Remaining: {stats.get('requests_remaining', 0)}")
        
        return stats.get('api_configured', False)
        
    except Exception as e:
        print(f"❌ Failed to initialize Google Search API: {e}")
        return False

if __name__ == "__main__":
    success = test_google_search_config()
    print(f"\n🎯 Configuration Status: {'✅ READY' if success else '⚠️ NEEDS SETUP'}")

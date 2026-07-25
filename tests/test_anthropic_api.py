#!/usr/bin/env python3
"""
Simple test script for Anthropic API
Replace YOUR_API_KEY_HERE with your actual API key
"""

import requests
import json
import sys

def test_anthropic_api(api_key):
    """Test Anthropic API with a simple request"""
    
    # API endpoint
    url = "https://api.anthropic.com/v1/messages"
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    # Simple test payload
    payload = {
        "model": "claude-3-haiku-20240307",  # Use smaller model for testing
        "max_tokens": 100,
        "messages": [
            {
                "role": "user",
                "content": "Hello! Please respond with 'API test successful' if you can see this message."
            }
        ]
    }
    
    print("🔍 Testing Anthropic API...")
    print(f"📡 Endpoint: {url}")
    print(f"🤖 Model: {payload['model']}")
    print(f"📝 Test message: {payload['messages'][0]['content']}")
    print("-" * 50)
    
    try:
        # Make the request
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Success!
            data = response.json()
            content = data.get("content", [{}])[0].get("text", "No content")
            print(f"✅ SUCCESS! Response: {content}")
            print(f"🎯 API key is working correctly!")
            return True
            
        elif response.status_code == 401:
            print("❌ AUTHENTICATION ERROR")
            print("   The API key is invalid or expired.")
            print("   Please check your API key in the web settings.")
            
        elif response.status_code == 429:
            print("⚠️ RATE LIMIT ERROR")
            print("   Too many requests. Please wait and try again.")
            
        elif response.status_code == 400:
            print("❌ BAD REQUEST")
            print("   Invalid request format or parameters.")
            print(f"   Response: {response.text}")
            
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT ERROR")
        print("   Request timed out. Please check your internet connection.")
        
    except requests.exceptions.ConnectionError:
        print("🌐 CONNECTION ERROR")
        print("   Could not connect to Anthropic API.")
        print("   Please check your internet connection.")
        
    except Exception as e:
        print(f"💥 UNEXPECTED ERROR: {e}")
    
    return False

def main():
    """Main function"""
    print("=" * 60)
    print("ANTHROPIC API TEST")
    print("=" * 60)
    
    # Get API key from user input (more secure than hardcoding)
    api_key = input("Enter your Anthropic API key (or press Enter to use env var): ").strip()
    
    if not api_key:
        # Try to get from environment variable
        api_key = sys.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("❌ No API key provided!")
            print("   Either:")
            print("   1. Enter your API key when prompted")
            print("   2. Set environment variable: export ANTHROPIC_API_KEY='your-key'")
            return
    
    # Mask the key for display
    masked_key = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "***"
    print(f"🔑 Using API key: {masked_key}")
    
    # Test the API
    success = test_anthropic_api(api_key)
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 RESULT: API key is working!")
        print("   You should be able to use Anthropic models in Cascade now.")
    else:
        print("❌ RESULT: API key test failed!")
        print("   Please check your API key and try again.")
    print("=" * 60)

if __name__ == "__main__":
    main()

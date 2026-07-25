#!/usr/bin/env python3
"""
Test Opus API specifically to isolate the issue
"""

import requests
import json

def test_opus_model(api_key):
    """Test Claude Opus model specifically"""
    
    url = "https://api.anthropic.com/v1/messages"
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    # Test with Opus model
    payload = {
        "model": "claude-3-opus-20240229",
        "max_tokens": 100,
        "messages": [
            {
                "role": "user",
                "content": "Hello! Please respond with 'Opus test successful' if you can see this."
            }
        ]
    }
    
    print("🔍 Testing Claude Opus API...")
    print(f"📡 Model: {payload['model']}")
    print(f"📝 Test message: {payload['messages'][0]['content']}")
    print("-" * 50)
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("content", [{}])[0].get("text", "No content")
            print(f"✅ OPUS SUCCESS! Response: {content}")
            return True
            
        elif response.status_code == 401:
            print("❌ AUTHENTICATION ERROR")
            print("   API key invalid or expired")
            
        elif response.status_code == 429:
            print("⚠️ RATE LIMIT ERROR")
            print("   Too many requests or Opus-specific limits")
            
        elif response.status_code == 400:
            print("❌ BAD REQUEST")
            print(f"   Response: {response.text}")
            
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"💥 UNEXPECTED ERROR: {e}")
    
    return False

def test_swe_model(api_key):
    """Test if SWE 1.5 is a special model variant"""
    
    # Try different SWE model names
    swe_models = [
        "claude-3-sonnet-20241022",  # Might be SWE variant
        "claude-3-opus-20240229",    # Might be SWE variant
        "claude-3-haiku-20240307",    # Baseline
    ]
    
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    print("\n🔍 Testing SWE Model Variants...")
    
    for model in swe_models:
        payload = {
            "model": model,
            "max_tokens": 50,
            "messages": [{"role": "user", "content": f"Test {model}"}]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            print(f"📊 {model}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Available")
            else:
                print(f"   ❌ {response.text[:100]}...")
                
        except Exception as e:
            print(f"   💥 Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("ANTHROPIC OPUS/SWE MODEL TEST")
    print("=" * 60)
    
    # Get API key
    import os
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        api_key = input("Enter your Anthropic API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided!")
        sys.exit(1)
    
    # Test Opus
    opus_success = test_opus_model(api_key)
    
    # Test SWE variants
    test_swe_model(api_key)
    
    print("\n" + "=" * 60)
    if opus_success:
        print("🎉 OPUS API WORKS - Issue is in Cascade configuration")
    else:
        print("❌ OPUS API FAILS - Issue is with API key or model access")
    print("=" * 60)

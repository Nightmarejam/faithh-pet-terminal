#!/usr/bin/env python3
import requests
import json

def test_anthropic_chat():
    try:
        # Test models endpoint first
        response = requests.get("http://localhost:5557/api/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print("✅ Models endpoint working!")
            print(f"   Available models: {models.get('models', [])}")
            print(f"   Anthropic available: {models.get('anthropic_available')}")
        
        # Test Anthropic chat
        chat_data = {
            "message": "Hello, can you help me with a simple test?",
            "provider": "anthropic",
            "model": "claude-3-haiku-20240307"
        }
        
        response = requests.post("http://localhost:5557/api/chat", 
                               json=chat_data, 
                               headers={'Content-Type': 'application/json'},
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Anthropic chat working!")
            print(f"   Success: {result.get('success')}")
            print(f"   Response: {result.get('response', '')[:100]}...")
            print(f"   Model used: {result.get('model_used')}")
            print(f"   Provider: {result.get('provider')}")
            return True
        else:
            print(f"❌ Anthropic chat failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Anthropic chat test failed: {e}")
        return False

if __name__ == "__main__":
    test_anthropic_chat()

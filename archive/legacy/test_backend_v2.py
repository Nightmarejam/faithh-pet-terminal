#!/usr/bin/env python3
"""
Test script for FAITHH Backend v2.0
"""

import requests
import json
import time

def test_backend_v2():
    """Test the new modular backend"""
    
    base_url = "http://localhost:5557"
    
    print("🧪 Testing FAITHH Backend v2.0")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    print("1. Testing basic connectivity...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Basic connectivity: {data.get('service')}")
            print(f"   Architecture: {data.get('architecture')}")
        else:
            print(f"❌ Basic connectivity failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Basic connectivity error: {e}")
        return False
    
    # Test 2: Health check
    print("\n2. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health status: {data.get('status')}")
            print(f"   Uptime: {data.get('uptime', 0):.1f}s")
            print(f"   Components: {list(data.get('components', {}).keys())}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 3: API status
    print("\n3. Testing API status...")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API status: {data.get('status')}")
            print(f"   Stage: {data.get('stage')}")
            health = data.get('health', {})
            print(f"   Overall health: {health.get('status')}")
        else:
            print(f"❌ API status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API status error: {e}")
        return False
    
    # Test 4: Models endpoint
    print("\n4. Testing models endpoint...")
    try:
        response = requests.get(f"{base_url}/api/models", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"✅ Models available: {len(models)}")
            for model in models[:3]:  # Show first 3 models
                print(f"   - {model.get('name')} ({model.get('provider')})")
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Models endpoint error: {e}")
        return False
    
    # Test 5: Anthropic chat
    print("\n5. Testing Anthropic chat...")
    try:
        chat_data = {
            "message": "Hello, this is a test message for the new backend!",
            "provider": "anthropic",
            "model": "claude-3-haiku-20240307"
        }
        
        response = requests.post(
            f"{base_url}/api/chat",
            json=chat_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Anthropic chat successful!")
                print(f"   Response: {data.get('response', '')[:100]}...")
                print(f"   Model used: {data.get('model_used')}")
                print(f"   Provider: {data.get('provider')}")
            else:
                print(f"❌ Anthropic chat failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Anthropic chat HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Anthropic chat error: {e}")
        return False
    
    # Test 6: Comprehensive health check
    print("\n6. Testing comprehensive health check...")
    try:
        response = requests.get(f"{base_url}/api/health/check", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Comprehensive health check: {data.get('status')}")
            providers = data.get('providers', {})
            print(f"   Registered providers: {providers.get('registered', [])}")
            print(f"   Available providers: {providers.get('available', [])}")
        else:
            print(f"❌ Comprehensive health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Comprehensive health check error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Backend v2.0 is working perfectly!")
    return True

if __name__ == "__main__":
    success = test_backend_v2()
    sys.exit(0 if success else 1)
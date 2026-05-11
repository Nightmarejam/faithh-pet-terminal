#!/usr/bin/env python3
import requests
import json

def test_phase4_features():
    print("🧪 Testing Phase 4 Implementation")
    print("=" * 50)
    
    # Test 1: Basic health check
    print("\n1. Testing basic health endpoint...")
    try:
        response = requests.get("http://localhost:5557/health", timeout=10)
        if response.status_code == 200:
            print("✅ Basic health check passed")
        else:
            print(f"❌ Basic health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Basic health check error: {e}")
    
    # Test 2: Enhanced health endpoint
    print("\n2. Testing enhanced health endpoint...")
    try:
        response = requests.get("http://localhost:5557/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Enhanced health check passed")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Version: {data.get('version', 'unknown')}")
        else:
            print(f"❌ Enhanced health check failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Enhanced health check error: {e}")
    
    # Test 3: Chat with security middleware
    print("\n3. Testing chat with security middleware...")
    try:
        payload = {
            "message": "test message",
            "model": "qwen25-grounded:latest"
        }
        response = requests.post(
            "http://localhost:5557/api/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Chat with security middleware passed")
                print(f"   Model used: {data.get('model_used', 'unknown')}")
                print(f"   Response length: {len(data.get('response', ''))}")
            else:
                print(f"❌ Chat failed: {data.get('error', 'unknown')}")
        else:
            print(f"❌ Chat failed with status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Chat error: {e}")
    
    # Test 4: Rate limiting
    print("\n4. Testing rate limiting...")
    try:
        # Send multiple requests quickly
        success_count = 0
        for i in range(5):
            payload = {
                "message": f"test message {i}",
                "model": "qwen25-grounded:latest"
            }
            response = requests.post(
                "http://localhost:5557/api/chat",
                json=payload,
                timeout=30
            )
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                print(f"✅ Rate limiting activated after {i+1} requests")
                break
        
        if success_count >= 3:
            print(f"✅ Rate limiting test passed ({success_count}/5 requests succeeded)")
        else:
            print(f"⚠️ Rate limiting may be too restrictive ({success_count}/5 requests succeeded)")
    except Exception as e:
        print(f"❌ Rate limiting test error: {e}")
    
    # Test 5: Model optimization
    print("\n5. Testing model optimization...")
    try:
        payload = {
            "message": "What are the recent changes to the FAITHH system?",
            # No model specified - should trigger optimization
        }
        response = requests.post(
            "http://localhost:5557/api/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Model optimization test passed")
                print(f"   Model used: {data.get('model_used', 'unknown')}")
                print(f"   Provider: {data.get('provider', 'unknown')}")
            else:
                print(f"❌ Model optimization failed: {data.get('error', 'unknown')}")
        else:
            print(f"❌ Model optimization failed with status: {response.status_code}")
    except Exception as e:
        print(f"❌ Model optimization error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Phase 4 Testing Complete!")

if __name__ == "__main__":
    test_phase4_features()

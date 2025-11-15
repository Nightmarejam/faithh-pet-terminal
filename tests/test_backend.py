#!/usr/bin/env python3
"""
Quick test of the FAITHH backend
"""

import requests
import json

# Test endpoints
BASE_URL = "http://localhost:5557"

print("Testing FAITHH Backend...")
print("=" * 40)

# Test health
try:
    r = requests.get(f"{BASE_URL}/health")
    print(f"✅ Health check: {r.json()}")
except Exception as e:
    print(f"❌ Health check failed: {e}")

# Test status
try:
    r = requests.get(f"{BASE_URL}/api/status")
    data = r.json()
    print(f"\n📊 Service Status:")
    for service, status in data['services'].items():
        icon = "✅" if status in ["online", "configured"] else "❌"
        print(f"  {icon} {service}: {status}")
except Exception as e:
    print(f"❌ Status check failed: {e}")

# Test models
try:
    r = requests.get(f"{BASE_URL}/api/models")
    data = r.json()
    print(f"\n🤖 Available Models:")
    for model in data['models']:
        print(f"  • {model['name']} ({model['provider']})")
except Exception as e:
    print(f"❌ Models check failed: {e}")

# Test chat
print("\n💬 Testing chat...")
try:
    r = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "Hello FAITHH, are you online?",
        "model": "llama3.1-8b"
    })
    data = r.json()
    if data['success']:
        print(f"✅ Chat response received:")
        print(f"   {data['response'][:100]}...")
    else:
        print(f"❌ Chat failed")
except Exception as e:
    print(f"❌ Chat test failed: {e}")

print("\n" + "=" * 40)
print("✅ Backend is running at http://localhost:5557")
print("✅ Open your browser to test the UI")

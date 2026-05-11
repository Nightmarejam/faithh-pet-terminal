#!/usr/bin/env python3
import requests
import json

def test_backend():
    try:
        response = requests.get("http://localhost:5557/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is working!")
            print(f"   Status: {data.get('status')}")
            print(f"   Stage: {data.get('stage')}")
            print(f"   Components: {data.get('components')}")
            print(f"   Anthropic: {data.get('anthropic_configured')}")
            return True
        else:
            print(f"❌ Backend responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

if __name__ == "__main__":
    test_backend()

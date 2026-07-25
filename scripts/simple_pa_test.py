#!/usr/bin/env python3
import requests
import json

try:
    response = requests.get("http://localhost:5001/api/health", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print("✅ PA Health Check Successful")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ PA Health Check Failed: {response.status_code}")
except Exception as e:
    print(f"❌ PA Health Check Error: {e}")

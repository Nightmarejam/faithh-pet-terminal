#!/usr/bin/env python3
"""Test coherence sensor integration"""
import requests
import json

url = "http://localhost:5557/api/chat"
payload = {
    "message": "What are the four mechanisms in the Harmony-AI Bridge?",
    "model": "gemini",
    "use_rag": True
}

response = requests.post(url, json=payload, timeout=60)
result = response.json()

print("=" * 60)
print("FAITHH Response Test with Coherence Sensor")
print("=" * 60)
print(f"\nQuery: {payload['message']}")
print(f"\nResponse (truncated):\n{result.get('response', 'No response')[:500]}...")
print(f"\n{'=' * 60}")
print("COHERENCE ANALYSIS:")
print("=" * 60)
coherence = result.get('coherence')
if coherence:
    for k, v in coherence.items():
        print(f"  {k}: {v}")
else:
    print("  No coherence data (sensor may not be loaded)")
print(f"\nRAG used: {result.get('rag_used')}")
print(f"Model: {result.get('model_used')}")

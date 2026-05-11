#!/usr/bin/env python3
"""Check Grok export format to understand structure."""
import json

filepath = "/home/jonat/ai-stack/AI_Chat_Exports/Grok_Exports/ttl/30d/export_data/6fe45935-cd7c-4b07-ab91-a6d97b844d29/prod-grok-backend.json"

with open(filepath) as f:
    data = json.load(f)

print("Type:", type(data))
print("Keys:", list(data.keys()))

convs = data.get("conversations", [])
print(f"\nConversations: {len(convs)}")

if convs:
    first = convs[0]
    print(f"\nFirst conversation keys: {list(first.keys())}")
    
    # Check 'conversation' sub-object
    conv_obj = first.get("conversation", {})
    print(f"\n'conversation' keys: {list(conv_obj.keys())[:15]}")
    
    # Check 'responses' 
    responses = first.get("responses", [])
    print(f"\n'responses': {len(responses)} items")
    if responses:
        print(f"First response wrapper keys: {list(responses[0].keys())[:15]}")
        # The actual response is nested under 'response' key
        resp_wrapper = responses[0]
        resp = resp_wrapper.get("response", {})
        print(f"Actual response keys: {list(resp.keys())[:15]}")
        print(f"  text preview: {str(resp.get('text', ''))[:100]}...")
        print(f"  sender: {resp.get('sender')}")
        print(f"  create_time: {resp.get('create_time')}")

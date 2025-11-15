#!/usr/bin/env python3
"""Quick test script for Gemini API connectivity"""
import os
import requests
import json

# Check if API key exists
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print('❌ GEMINI_API_KEY not set in environment')
    exit(1)

print(f'✓ API Key found (length: {len(api_key)})')

# Test API connectivity
url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}'

try:
    response = requests.post(url, 
        json={'contents': [{'parts': [{'text': 'Reply with: CONNECTED'}]}]},
        timeout=10
    )
    
    print(f'\n📡 Status Code: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        text = data['candidates'][0]['content']['parts'][0]['text']
        print(f'✅ API CONNECTED! Response: {text}')
    else:
        print(f'❌ API Error: {response.text}')
except Exception as e:
    print(f'❌ Connection failed: {e}')

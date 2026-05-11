#!/usr/bin/env python3
"""Test that .env loads correctly"""

from dotenv import load_dotenv
import os

load_dotenv()

gemini_key = os.getenv('GEMINI_API_KEY')

if gemini_key:
    print("✅ GEMINI_API_KEY loaded successfully")
    print(f"   Key length: {len(gemini_key)} characters")
    print(f"   Key starts with: {gemini_key[:10]}...")
else:
    print("❌ GEMINI_API_KEY not found in .env")
    print("   Please check your .env file")

print("")
print("Other environment variables:")
for key in ['OLLAMA_HOST', 'BACKEND_PORT', 'ENVIRONMENT']:
    value = os.getenv(key)
    if value:
        print(f"  ✅ {key} = {value}")
    else:
        print(f"  ⚠️  {key} not set")


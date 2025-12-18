#!/usr/bin/env python3
import os
from dotenv import load_dotenv

print("Before load_dotenv:")
print(f"  GROQ_API_KEY: {os.environ.get('GROQ_API_KEY', 'NOT SET')}")

load_dotenv(override=True)

print("After load_dotenv:")
print(f"  GROQ_API_KEY: {os.environ.get('GROQ_API_KEY', 'NOT SET')[:30] if os.environ.get('GROQ_API_KEY') else 'NOT SET'}...")

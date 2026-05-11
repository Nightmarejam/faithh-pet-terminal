#!/usr/bin/env python3
from dotenv import load_dotenv
load_dotenv()
import os

# Test validation directly
api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
print(f"API Key: {api_key}")
print(f"Length: {len(api_key) if api_key else 0}")
print(f"Length > 20: {len(api_key) > 20 if api_key else False}")

# Test the validation logic
if not api_key:
    print("Validation: False (empty key)")
elif len(api_key) > 20:
    print("Validation: True (length > 20)")
else:
    print("Validation: False (length <= 20)")

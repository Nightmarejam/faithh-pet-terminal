#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

print(f"API Key: {bool(api_key)}")
print(f"Engine ID: '{engine_id}'")
print(f"Engine ID bool: {bool(engine_id)}")
print(f"Engine ID is placeholder: {engine_id == 'your_custom_search_engine_id_here'}")

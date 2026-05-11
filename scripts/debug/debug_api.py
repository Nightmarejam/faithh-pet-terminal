#!/usr/bin/env python3
from google_search import GoogleSearchAPI

api = GoogleSearchAPI()
print(f"API Key: {bool(api.api_key)}")
print(f"Engine ID: {bool(api.search_engine_id)}")
print(f"API Configured: {bool(api.api_key)}")
print(f"Engine ID value: '{api.search_engine_id}'")

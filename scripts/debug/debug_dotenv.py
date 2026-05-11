#!/usr/bin/env python3
from dotenv import load_dotenv
load_dotenv()
import os
print(f"API Key: {os.getenv('GOOGLE_SEARCH_API_KEY')}")
print(f"Engine ID: {os.getenv('GOOGLE_SEARCH_ENGINE_ID')}")

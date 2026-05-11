#!/usr/bin/env python3
import os
from dotenv import load_dotenv

def check_env_vars():
    load_dotenv()
    
    print("Environment Variables Check:")
    print("=" * 40)
    
    vars_to_check = [
        'GROQ_API_KEY',
        'ANTHROPIC_API_KEY', 
        'GEMINI_API_KEY',
        'MODEL_PROVIDER',
        'DEFAULT_MODEL',
        'OLLAMA_HOST',
        'BACKEND_PORT'
    ]
    
    for var in vars_to_check:
        value = os.getenv(var)
        if value:
            if 'API_KEY' in var:
                # Show first 10 chars for API keys
                print(f"✅ {var}: {value[:10]}...")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")

if __name__ == "__main__":
    check_env_vars()

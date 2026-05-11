#!/usr/bin/env python3
"""Test three working Groq models respond correctly"""

import os
import groq
from dotenv import load_dotenv

def test_groq_models():
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ GROQ_API_KEY not found in .env")
        return
    
    client = groq.Groq(api_key=api_key)
    
    # Test models
    models_to_test = [
        ('llama-3.3-70b-versatile', 'Default'),
        ('llama-3.1-8b-instant', 'Fast'),
        ('openai/gpt-oss-120b', 'Reasoning')
    ]
    
    print("🧪 Testing Groq Models:")
    print("=" * 50)
    
    for model_id, model_type in models_to_test:
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": "Say hello in one word"}],
                max_tokens=10,
                temperature=0.1
            )
            
            response_text = response.choices[0].message.content.strip()
            print(f"✅ {model_type} ({model_id}): {response_text}")
            
        except Exception as e:
            print(f"❌ {model_type} ({model_id}): ERROR - {e}")

if __name__ == "__main__":
    test_groq_models()

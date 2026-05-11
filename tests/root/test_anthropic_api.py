#!/usr/bin/env python3
"""Test Anthropic API connectivity with minimal usage"""

import anthropic

def test_api():
    try:
        client = anthropic.Anthropic(api_key='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')
        
        # Use cheapest model for test
        response = client.messages.create(
            model='claude-3-haiku-20240307',
            max_tokens=10,
            messages=[{'role': 'user', 'content': 'Hi'}]
        )
        
        print("✅ Anthropic API works!")
        print(f"Response: {response.content[0].text}")
        return True
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return False

if __name__ == "__main__":
    test_api()

#!/usr/bin/env python3
import os
import sys
sys.path.append('/home/jonat/ai-stack')

# Set environment variables
os.environ['ANTHROPIC_API_KEY'] = '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'

try:
    from backend.llm_providers import call_anthropic_chat
    
    # Test the fixed API call
    messages = [{"role": "user", "content": "Hello, can you help me?"}]
    
    print("Testing Anthropic API with fixed format...")
    # Test with correct model names
    models_to_test = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet",
        "claude-3-haiku-20240307",
        "claude-3-haiku"
    ]
    
    for model in models_to_test:
        print(f"\nTesting model: {model}")
        try:
            response, usage, api_data = call_anthropic_chat(
                messages=messages,
                model=model,
                max_tokens=100,
                temperature=0.1,
                timeout_s=30,
                api_key=os.environ['ANTHROPIC_API_KEY']
            )
            print(f"✅ SUCCESS with {model}: {response[:50]}...")
            break
        except Exception as e:
            print(f"❌ ERROR with {model}: {e}")
    
    print(f"✅ SUCCESS: {response[:100]}...")
    print(f"Usage: {usage}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")

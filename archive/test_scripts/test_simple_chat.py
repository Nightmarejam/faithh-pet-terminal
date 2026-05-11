#!/usr/bin/env python3
"""
Simple test for chat functionality without async complications
"""

import sys
import os
import time
import json

# Add project path
sys.path.append("/home/jonat/ai-stack")

def test_chat_simple():
    """Test chat with simple mock response"""
    
    # Mock chat response for testing
    class MockChatResponse:
        def __init__(self):
            self.success = True
            self.response = "Hello! This is a mock response from the FAITHH backend v2.0. The chat endpoint is working correctly."
            self.model_used = "claude-3-haiku-20240307"
            self.provider = "anthropic"
            self.usage = {"prompt_tokens": 10, "completion_tokens": 25, "total_tokens": 35}
            self.timestamp = time.time()
    
    # Create mock response
    response = MockChatResponse()
    
    # Return JSON response
    return {
        "success": response.success,
        "response": response.response,
        "model_used": response.model_used,
        "provider": response.provider,
        "usage": response.usage,
        "timestamp": response.timestamp
    }

if __name__ == "__main__":
    # Test the simple chat
    result = test_chat_simple()
    print(json.dumps(result, indent=2))
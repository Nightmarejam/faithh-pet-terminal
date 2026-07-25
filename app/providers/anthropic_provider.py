"""
Anthropic provider implementation
"""

import os
import sys
import time
from typing import List
from . import BaseProvider
from ..models import ChatRequest, ChatResponse, ModelInfo, ProviderStatus, ProviderType

# Add project path for imports
sys.path.append("/home/jonat/ai-stack")

class AnthropicProvider(BaseProvider):
    """Anthropic Claude provider with fixed message format"""
    
    def __init__(self):
        super().__init__(ProviderType.ANTHROPIC)
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        self._models = [
            ModelInfo("claude-3-haiku-20240307", ProviderType.ANTHROPIC, "Fast, efficient model"),
            ModelInfo("claude-3-5-sonnet-20241022", ProviderType.ANTHROPIC, "Balanced model"),
        ]
    
    def is_available(self) -> bool:
        """Check if Anthropic API key is available"""
        return bool(self.api_key)
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Process chat request with Anthropic API"""
        if not self.is_available():
            return ChatResponse(
                success=False,
                error="ANTHROPIC_API_KEY not configured",
                provider="anthropic",
                timestamp=time.time()
            )
        
        try:
            # Import Anthropic provider
            from backend.llm_providers import call_anthropic_chat
            
            # Use fixed message format
            messages = [{"role": "user", "content": request.message}]
            model = request.model or "claude-3-haiku-20240307"
            
            print(f"   🔧 Calling Anthropic with model: {model}")
            
            # Call Anthropic API
            assistant_response, usage, api_data = call_anthropic_chat(
                messages=messages,
                model=model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                timeout_s=60,
                api_key=self.api_key
            )
            
            print(f"   ✅ Anthropic response received: {len(assistant_response)} chars")
            
            return ChatResponse(
                success=True,
                response=assistant_response,
                model_used=model,
                provider="anthropic",
                usage=usage,
                timestamp=time.time()
            )
            
        except Exception as e:
            print(f"❌ Anthropic chat error: {e}")
            return ChatResponse(
                success=False,
                error=f"Anthropic API error: {e}",
                provider="anthropic",
                model_attempted=request.model,
                timestamp=time.time()
            )
    
    def get_models(self) -> List[ModelInfo]:
        """Get available Anthropic models"""
        return self._models
    
    def health_check(self) -> ProviderStatus:
        """Check Anthropic provider health"""
        start_time = time.time()
        
        try:
            if not self.is_available():
                return ProviderStatus(
                    available=False,
                    models=[],
                    error="API key not configured",
                    response_time=time.time() - start_time
                )
            
            # Test API with minimal request
            test_request = ChatRequest(
                message="Hello",
                max_tokens=10,
                temperature=0.1
            )
            
            # Use synchronous call for health check
            from backend.llm_providers import call_anthropic_chat
            
            messages = [{"role": "user", "content": "Hello"}]
            response, usage, api_data = call_anthropic_chat(
                messages=messages,
                model="claude-3-haiku-20240307",
                max_tokens=10,
                temperature=0.1,
                timeout_s=10,
                api_key=self.api_key
            )
            
            return ProviderStatus(
                available=True,
                models=self._models,
                response_time=time.time() - start_time
            )
            
        except Exception as e:
            return ProviderStatus(
                available=False,
                models=[],
                error=str(e),
                response_time=time.time() - start_time
            )
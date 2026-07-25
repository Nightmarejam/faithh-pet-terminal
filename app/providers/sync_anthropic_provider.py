"""
Synchronous Anthropic Provider Wrapper
Resolves async/sync compatibility issues
"""

import os
import sys
import time
import asyncio
import concurrent.futures
from typing import List
from . import BaseProvider
from ..models import ChatRequest, ChatResponse, ModelInfo, ProviderStatus, ProviderType

# Add project path for imports
sys.path.append("/home/jonat/ai-stack")

class SyncAnthropicProvider(BaseProvider):
    """Synchronous wrapper for Anthropic provider"""
    
    def __init__(self):
        super().__init__(ProviderType.ANTHROPIC)
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.async_provider = None
        self._models = [
            ModelInfo("claude-3-haiku-20240307", ProviderType.ANTHROPIC, "Fast, efficient model"),
            ModelInfo("claude-3-5-sonnet-20241022", ProviderType.ANTHROPIC, "Balanced model"),
        ]
        
        # Import async provider
        try:
            from .anthropic_provider import AnthropicProvider
            self.async_provider = AnthropicProvider()
        except ImportError as e:
            print(f"❌ Could not import async AnthropicProvider: {e}")
    
    def is_available(self) -> bool:
        """Check if Anthropic API key is available"""
        return bool(self.api_key) and self.async_provider is not None
    
    def chat(self, request: ChatRequest) -> ChatResponse:
        """Synchronous chat method"""
        if not self.is_available():
            return ChatResponse(
                success=False,
                error="ANTHROPIC_API_KEY not configured or provider unavailable",
                provider="anthropic",
                timestamp=time.time()
            )
        
        try:
            # Handle async/sync boundary
            if asyncio.get_event_loop().is_running():
                # Use thread executor if event loop is running
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run, 
                        self.async_provider.chat(request)
                    )
                    return future.result(timeout=60)
            else:
                # Use asyncio.run if no event loop
                return asyncio.run(self.async_provider.chat(request))
                
        except concurrent.futures.TimeoutError:
            return ChatResponse(
                success=False,
                error="Request timeout after 60 seconds",
                provider="anthropic",
                model_attempted=request.model,
                timestamp=time.time()
            )
        except Exception as e:
            return ChatResponse(
                success=False,
                error=f"Provider error: {e}",
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
                    error="API key not configured or provider unavailable",
                    response_time=time.time() - start_time
                )
            
            # Test API with minimal request
            test_request = ChatRequest(
                message="Hello",
                max_tokens=10,
                temperature=0.1
            )
            
            # Use synchronous health check
            response = self.chat(test_request)
            
            if response.success:
                return ProviderStatus(
                    available=True,
                    models=self._models,
                    response_time=time.time() - start_time
                )
            else:
                return ProviderStatus(
                    available=False,
                    models=[],
                    error=response.error,
                    response_time=time.time() - start_time
                )
            
        except Exception as e:
            return ProviderStatus(
                available=False,
                models=[],
                error=str(e),
                response_time=time.time() - start_time
            )
"""
Chat processing service
"""

import time
from typing import Dict, Any
from ..models import ChatRequest, ChatResponse
from ..providers import provider_registry
from .provider_service import ProviderService

class ChatService:
    """Chat processing and routing service"""
    
    def __init__(self):
        self.provider_service = ProviderService()
    
    async def process_chat(self, request_data: Dict[str, Any]) -> ChatResponse:
        """Process chat request with provider routing"""
        try:
            # Create chat request
            request = ChatRequest(
                message=request_data.get('message', ''),
                provider=request_data.get('provider'),
                model=request_data.get('model'),
                temperature=request_data.get('temperature', 0.1),
                max_tokens=request_data.get('max_tokens', 4096)
            )
            
            if not request.message:
                return ChatResponse(
                    success=False,
                    error="Message is required",
                    timestamp=time.time()
                )
            
            # Route to provider
            provider_name = self.provider_service.route_request(
                provider=request.provider,
                model=request.model
            )
            
            provider = provider_registry.get_provider(provider_name)
            
            # Validate model
            if request.model and not self.provider_service.validate_model(provider_name, request.model):
                # Use default model for provider
                request.model = self.provider_service.get_default_model(provider_name)
            
            # Process chat
            response = await provider.chat(request)
            
            # Add routing info
            response.provider = provider_name
            if not response.model_used and request.model:
                response.model_used = request.model
            
            return response
            
        except Exception as e:
            print(f"❌ Chat processing error: {e}")
            return ChatResponse(
                success=False,
                error=f"Chat processing failed: {e}",
                timestamp=time.time()
            )
    
    def get_chat_info(self) -> Dict[str, Any]:
        """Get chat service information"""
        return {
            "available_providers": self.provider_service.get_available_providers(),
            "available_models": self.provider_service.get_available_models(),
            "provider_status": self.provider_service.get_provider_status(),
            "default_routing": {
                "anthropic": "claude-3-haiku-20240307",
                "fallback": "first_available"
            }
        }
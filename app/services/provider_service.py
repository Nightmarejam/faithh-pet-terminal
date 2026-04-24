"""
Provider management service
"""

from typing import List, Dict, Any
from ..providers import provider_registry
from ..models import ModelInfo

class ProviderService:
    """Provider management and routing service"""
    
    def __init__(self):
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available providers"""
        try:
            # Import and register Anthropic provider
            from ..providers.anthropic_provider import AnthropicProvider
            anthropic = AnthropicProvider()
            provider_registry.register("anthropic", anthropic)
            
            print(f"✅ Initialized {len(provider_registry.list_providers())} providers")
            
        except Exception as e:
            print(f"❌ Provider initialization failed: {e}")
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get all available models from all providers"""
        models = []
        
        for provider_name in provider_registry.get_available_providers():
            try:
                provider = provider_registry.get_provider(provider_name)
                provider_models = provider.get_models()
                
                for model in provider_models:
                    models.append({
                        "name": model.name,
                        "provider": provider_name,
                        "description": model.description
                    })
                    
            except Exception as e:
                print(f"❌ Error getting models from {provider_name}: {e}")
        
        return models
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        return {
            "registered": provider_registry.list_providers(),
            "available": provider_registry.get_available_providers(),
            "health_status": provider_registry.health_check_all()
        }
    
    def route_request(self, provider: str = None, model: str = None) -> str:
        """Route request to appropriate provider"""
        if provider and provider in provider_registry.list_providers():
            return provider
        
        # Default routing logic
        available_providers = provider_registry.get_available_providers()
        
        if not available_providers:
            raise ValueError("No providers available")
        
        # Prefer Anthropic if available
        if "anthropic" in available_providers:
            return "anthropic"
        
        # Use first available provider
        return available_providers[0]
    
    def validate_model(self, provider: str, model: str) -> bool:
        """Validate that a model is available for a provider"""
        try:
            provider_obj = provider_registry.get_provider(provider)
            available_models = [m.name for m in provider_obj.get_models()]
            return model in available_models
        except:
            return False
    
    def get_default_model(self, provider: str) -> str:
        """Get default model for a provider"""
        try:
            provider_obj = provider_registry.get_provider(provider)
            models = provider_obj.get_models()
            return models[0].name if models else None
        except:
            return None
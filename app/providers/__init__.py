"""
Provider interface and implementations
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..models import ChatRequest, ChatResponse, ModelInfo, ProviderStatus, ProviderType

class BaseProvider(ABC):
    """Abstract base class for all LLM providers"""
    
    def __init__(self, provider_type: ProviderType):
        self.provider_type = provider_type
    
    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Process chat request"""
        pass
    
    @abstractmethod
    def get_models(self) -> List[ModelInfo]:
        """Get available models"""
        pass
    
    @abstractmethod
    def health_check(self) -> ProviderStatus:
        """Check provider health"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available"""
        pass

class ProviderRegistry:
    """Registry for managing providers"""
    
    def __init__(self):
        self._providers: Dict[str, BaseProvider] = {}
    
    def register(self, name: str, provider: BaseProvider) -> None:
        """Register a provider"""
        self._providers[name] = provider
        print(f"✅ Registered provider: {name}")
    
    def get_provider(self, name: str) -> BaseProvider:
        """Get provider by name"""
        if name not in self._providers:
            raise ValueError(f"Provider {name} not found")
        return self._providers[name]
    
    def list_providers(self) -> List[str]:
        """List all registered providers"""
        return list(self._providers.keys())
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        available = []
        for name, provider in self._providers.items():
            if provider.is_available():
                available.append(name)
        return available
    
    def health_check_all(self) -> Dict[str, ProviderStatus]:
        """Health check for all providers"""
        status = {}
        for name, provider in self._providers.items():
            try:
                status[name] = provider.health_check()
            except Exception as e:
                status[name] = ProviderStatus(
                    available=False,
                    models=[],
                    error=str(e)
                )
        return status

# Global provider registry
provider_registry = ProviderRegistry()

# Initialize providers
def initialize_providers():
    """Initialize all available providers"""
    try:
        from .sync_anthropic_provider import SyncAnthropicProvider
        provider_registry.register("anthropic", SyncAnthropicProvider())
        print("✅ Initialized 1 providers")
    except Exception as e:
        print(f"❌ Failed to initialize providers: {e}")

# Auto-initialize
initialize_providers()
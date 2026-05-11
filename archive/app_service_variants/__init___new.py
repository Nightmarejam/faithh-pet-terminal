"""
Business logic services
"""

from .health_service import HealthService
from .chat_service import ChatService
from .provider_service import ProviderService
from .alife_service import AlifeService
from .standing_wave_service import StandingWaveService

# Global service instances
health_service = HealthService()
provider_service = ProviderService()
chat_service = ChatService()
alife_service = AlifeService()
standing_wave_service = StandingWaveService()
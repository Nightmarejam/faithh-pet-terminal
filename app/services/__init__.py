"""
Business logic services
"""

from .health_service import HealthService
from .chat_service import ChatService
from .provider_service import ProviderService
from .alife_service import AlifeService
from .standing_wave_service import StandingWaveService
from .standing_wave_moon_service import StandingWaveMoonService
from .parasitic_alife_service_fixed import ParasiticAlifeService
from .alife_parasitic_integration_final import AlifeParasiticIntegration
from .genomic_impedance_sensor import GenomicImpedanceSensor
from .genomic_biasing_engine import GenomicBiasingEngine

# Global service instances
health_service = HealthService()
provider_service = ProviderService()
chat_service = ChatService()
alife_service = AlifeService()
standing_wave_service = StandingWaveService()
standing_wave_moon_service = StandingWaveMoonService()
parasitic_alife_service = ParasiticAlifeService()
alife_parasitic_integration = AlifeParasiticIntegration(alife_service, parasitic_alife_service)

# Genomic services will be initialized after dependencies are available
"""
Unified health monitor facade.

Provides a single interface that delegates:
- system-level health to backend.connection_monitor
- provider quick checks to backend.llm_providers.connection_monitor
"""

from backend.connection_monitor import connection_monitor as system_connection_monitor
from backend.llm_providers import connection_monitor as provider_connection_monitor


class HealthMonitorFacade:
    """Facade that unifies provider and system monitor access."""

    def check_provider_health(self, service_name, health_check_func, check_interval=60):
        return provider_connection_monitor.check_service_health(
            service_name, health_check_func, check_interval
        )

    def get_provider_last_check(self, service_name):
        return provider_connection_monitor.last_check.get(service_name)

    def get_provider_unhealthy_services(self):
        return provider_connection_monitor.get_unhealthy_services()

    def get_system_health_summary(self):
        return system_connection_monitor.get_system_health_summary()

    def get_system_unhealthy_services(self):
        return system_connection_monitor.get_unhealthy_services()

    def get_system_statuses(self):
        return system_connection_monitor.get_all_statuses()


health_monitor_facade = HealthMonitorFacade()

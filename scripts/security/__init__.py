"""
Pulse Security Module - FAITHH's immune system

Components:
- scanner: Input/output security scanning (prompt injection, secrets, PII)
- healer: Self-healing service recovery
- audit: Structured action logging
"""
from .scanner import (
    PulseSecurityScanner,
    ScanResult,
    get_scanner,
    scan_input,
    scan_output,
)

from .healer import (
    PulseSelfHealer,
    ServiceConfig,
    HealingAction,
)

from .audit import (
    PulseAuditLogger,
    AuditEvent,
    get_audit_logger,
)

__all__ = [
    # Scanner
    "PulseSecurityScanner",
    "ScanResult",
    "get_scanner",
    "scan_input",
    "scan_output",
    # Healer
    "PulseSelfHealer",
    "ServiceConfig",
    "HealingAction",
    # Audit
    "PulseAuditLogger",
    "AuditEvent",
    "get_audit_logger",
]

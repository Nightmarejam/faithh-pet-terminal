"""Shared data models for the `app` package.

RECONSTRUCTED 2026-07-26. The original `app/models` was never committed: the
repo's top-level `.gitignore` carried a bare `models/` rule (intended for ML
weight directories) which also matched this source package, so it existed only
on the machine that wrote it and was lost with the FAITHH VM.

Field names and constructor signatures below were recovered from call sites:
  app/services/health_service.py      -> HealthStatus(status, components, timestamp, uptime)
  app/providers/anthropic_provider.py -> ChatRequest(message, max_tokens, temperature[, model, provider])
                                         ChatResponse(success, response, model_used, provider, usage, timestamp, error)
                                         ProviderStatus(available, models, error, response_time)
                                         ModelInfo(name, provider_type, description)  [positional]
  app/providers/__init__.py            -> ProviderType enum

Kept dependency-free (stdlib dataclasses/enum) so it imports under Python 3.10
without pulling in pydantic. If the original turns up, prefer it — but check the
signatures against these call sites first.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ProviderType(str, Enum):
    """LLM provider identifiers. `str` mixin so values compare/serialize as text."""

    ANTHROPIC = "anthropic"
    GROQ = "groq"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    VLLM = "vllm"


@dataclass
class ModelInfo:
    """A model offered by a provider. Constructed positionally at call sites."""

    name: str
    provider_type: ProviderType = ProviderType.ANTHROPIC
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "provider": str(getattr(self.provider_type, "value", self.provider_type)),
            "description": self.description,
        }


@dataclass
class ChatRequest:
    message: str
    model: Optional[str] = None
    provider: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1024


@dataclass
class ChatResponse:
    success: bool
    response: Optional[str] = None
    model_used: Optional[str] = None
    provider: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    timestamp: Optional[float] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "response": self.response,
            "model_used": self.model_used,
            "provider": self.provider,
            "usage": self.usage,
            "timestamp": self.timestamp,
            "error": self.error,
        }


@dataclass
class ProviderStatus:
    available: bool
    models: List[ModelInfo] = field(default_factory=list)
    response_time: Optional[float] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "available": self.available,
            "models": [m.to_dict() if hasattr(m, "to_dict") else str(m) for m in self.models],
            "response_time": self.response_time,
            "error": self.error,
        }


@dataclass
class HealthStatus:
    status: str
    components: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[float] = None
    uptime: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "components": self.components,
            "timestamp": self.timestamp,
            "uptime": self.uptime,
        }


__all__ = [
    "ProviderType",
    "ModelInfo",
    "ChatRequest",
    "ChatResponse",
    "ProviderStatus",
    "HealthStatus",
]

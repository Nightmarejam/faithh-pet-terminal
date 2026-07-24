"""
FAITHH central configuration — single source of truth for all env-driven settings.

Phase 3 step 1 (TARGET_ARCHITECTURE migration). Replaces ~51 scattered os.getenv
calls across the backend. Import `cfg` and read attributes instead of calling
os.getenv inline. Non-breaking: every value falls back to the same default the
inline call used, so existing behavior is preserved until modules migrate to it.

FIXES A REAL DRIFT BUG: the tree used BOTH `CHROMA_HOST`/`CHROMA_PORT` AND
`CHROMADB_HOST`/`CHROMADB_PORT` for the same ChromaDB — the same class of
duplicate-source drift that produced the .243-vs-.10 IP contradiction in the docs.
This module reads either name (CHROMADB_* wins if both set) and exposes ONE value.
"""
from __future__ import annotations
import os
from dataclasses import dataclass, field


def _env(*names: str, default: str | None = None) -> str | None:
    """First present env var among aliases; last alias listed wins precedence."""
    val = default
    for n in names:
        v = os.getenv(n)
        if v is not None:
            val = v
    return val


def _int(*names: str, default: int) -> int:
    v = _env(*names)
    try:
        return int(v) if v is not None else default
    except ValueError:
        return default


def _float(*names: str, default: float) -> float:
    v = _env(*names)
    try:
        return float(v) if v is not None else default
    except ValueError:
        return default


@dataclass(frozen=True)
class ChromaConfig:
    # NOTE: reads both CHROMA_* and CHROMADB_* aliases — resolves the drift.
    host: str = field(default_factory=lambda: _env("CHROMA_HOST", "CHROMADB_HOST",
                                                    default="servicebox.taileb8c60.ts.net"))  # MagicDNS; see homelab/infra/hosts.yaml
    port: int = field(default_factory=lambda: _int("CHROMA_PORT", "CHROMADB_PORT", default=8000))
    collection: str = field(default_factory=lambda: _env("CHROMA_COLLECTION",
                                                          default="faithh_knowledge_base"))


@dataclass(frozen=True)
class OllamaConfig:
    host: str = field(default_factory=lambda: _env("OLLAMA_HOST", default="http://localhost:11434"))
    model: str = field(default_factory=lambda: _env("OLLAMA_MODEL", "OLLAMA_DEFAULT_MODEL",
                                                     default="qwen2.5:7b"))
    reasoning_model: str = field(default_factory=lambda: _env("OLLAMA_REASONING_MODEL", default=""))
    connect_timeout: float = field(default_factory=lambda: _float("OLLAMA_CONNECT_TIMEOUT", default=5.0))
    read_timeout: float = field(default_factory=lambda: _float("OLLAMA_READ_TIMEOUT",
                                                               "OLLAMA_TIMEOUT_S", default=120.0))
    num_predict: int = field(default_factory=lambda: _int("OLLAMA_NUM_PREDICT", default=1024))


@dataclass(frozen=True)
class ProviderKeys:
    """Secrets — never logged. Presence, not value, is what code should check."""
    groq: str = field(default_factory=lambda: _env("GROQ_API_KEY", default="") or "")
    anthropic: str = field(default_factory=lambda: _env("ANTHROPIC_API_KEY", default="") or "")
    gemini: str = field(default_factory=lambda: _env("GEMINI_API_KEY", "GOOGLE_API_KEY", default="") or "")

    def has(self, name: str) -> bool:
        return bool(getattr(self, name, ""))


@dataclass(frozen=True)
class RagConfig:
    temporal_weight: float = field(default_factory=lambda: _float("RAG_TEMPORAL_WEIGHT", default=0.0))
    temporal_halflife_days: float = field(default_factory=lambda: _float("RAG_TEMPORAL_HALFLIFE_DAYS", default=30.0))
    source_boost: float = field(default_factory=lambda: _float("RAG_SOURCE_BOOST", default=0.0))
    max_distance_confident: float = field(default_factory=lambda: _float("RAG_MAX_DISTANCE_CONFIDENT", default=0.45))
    signal_stale_seconds: int = field(default_factory=lambda: _int("RAG_SIGNAL_STALE_SECONDS", default=300))


@dataclass(frozen=True)
class Config:
    port: int = field(default_factory=lambda: _int("PORT", default=5557))
    strict_llm_gpu: bool = field(default_factory=lambda: _env("FAITHH_STRICT_LLM_GPU", default="0") == "1")
    cuda_visible: str = field(default_factory=lambda: _env("CUDA_VISIBLE_DEVICES", default=""))
    chroma: ChromaConfig = field(default_factory=ChromaConfig)
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    keys: ProviderKeys = field(default_factory=ProviderKeys)
    rag: RagConfig = field(default_factory=RagConfig)

    def summary(self) -> str:
        """Safe to log — redacts secrets to presence flags."""
        return (f"FAITHH config: port={self.port} chroma={self.chroma.host}:{self.chroma.port}"
                f"/{self.chroma.collection} ollama={self.ollama.model} "
                f"keys=[{'groq' if self.keys.has('groq') else ''}"
                f"{' anthropic' if self.keys.has('anthropic') else ''}"
                f"{' gemini' if self.keys.has('gemini') else ''}]")


cfg = Config()

if __name__ == "__main__":
    print(cfg.summary())

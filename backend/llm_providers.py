"""
FAITHH Phase 2 - Multi-Provider LLM Module

Provides:
- Groq (OpenAI-compatible chat endpoint)
- Ollama (prompt-based generate)
- Local text-generation-webui (OpenAI-compatible chat endpoint)
- Anthropic (Claude API for SWE 1.5 and Opus)

Design goals:
- Simple, explicit routing + fallback
- Honest routing metadata returned to caller
- Safe defaults (timeouts, minimal retries)

GPU note (Logic for Humans): This module only talks to Ollama/text-generation-webui over HTTP.
The actual matrix math runs inside those **server processes**. Call ``apply_faithh_llm_cuda_env()``
after loading ``.env`` so **this** Python process only sees the intended physical GPU for any
in-process CUDA (e.g. accidental imports). **Mirror the same ``CUDA_VISIBLE_DEVICES`` on the
Ollama systemd service / docker container** so inference uses the RTX 3090 (typically PCI index ``1``).
"""

from __future__ import annotations

import copy
import os
import re
import time
import json
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

import requests

try:
    import anthropic
except ImportError:
    anthropic = None


def default_ollama_timeout_s() -> int:
    # Logic for Humans: Large grounded models can spend minutes loading weights from disk into VRAM; 120s HTTP read timeouts look like hung chat. Read env at call time (after repo-root load_dotenv), not at module import.
    """HTTP timeout (seconds) for Ollama /api/generate. Env OLLAMA_TIMEOUT_S (default 300). Clamped 30..3600."""
    try:
        raw = (os.environ.get("OLLAMA_TIMEOUT_S") or "300").strip()
        v = int(raw)
        return max(30, min(v, 3600))
    except (TypeError, ValueError):
        return 300


def default_ollama_num_predict(max_tokens_from_config: Optional[int] = None) -> int:
    """
    Max new tokens for Ollama ``options.num_predict``. Without this, /api/generate can run until
    context is full — models that echo prompt delimiters can appear to "loop" indefinitely.

    Env OLLAMA_NUM_PREDICT_CAP (default 1200) is the hard ceiling. If ``max_tokens_from_config``
    is set (e.g. YAML provider max_tokens), we use min(that, cap). If None, use the cap alone.
    """
    try:
        cap = int((os.environ.get("OLLAMA_NUM_PREDICT_CAP") or "1200").strip())
        cap = max(64, min(cap, 32000))
    except (TypeError, ValueError):
        cap = 1200
    if max_tokens_from_config is None:
        return cap
    try:
        want = int(max_tokens_from_config)
    except (TypeError, ValueError):
        return cap
    return max(64, min(want, cap))


def faithh_ollama_stop_sequences() -> List[str]:
    """
    Stop strings for Ollama to cut off runaway echo of FAITHH prompt/context delimiters.
    Override with env OLLAMA_STOP pipe-separated (e.g. ``====|\nUSER\n``).
    """
    custom = (os.environ.get("OLLAMA_STOP") or "").strip()
    if custom:
        return [s.replace("\\n", "\n") for s in custom.split("|") if s.strip()]
    return ["====", "\nUSER\n", "\n===", "[CTX:", "\nUser:", "\nAssistant:"]


def get_faithh_cuda_physical_device_index() -> str:
    """Physical GPU index for this workstation (default ``1`` = second card, e.g. RTX 3090 next to a 1080 Ti)."""
    return (os.environ.get("FAITHH_CUDA_PHYSICAL_DEVICE", "1") or "1").strip()


def apply_faithh_llm_cuda_env() -> dict:
    # Logic for Humans: After .env is loaded, force this process to only *see* one physical GPU so nothing accidentally initializes on the display card. Does not move Ollama—that daemon needs the same env at *its* startup.
    """
    Pin ``CUDA_DEVICE_ORDER`` + ``CUDA_VISIBLE_DEVICES`` for strict LLM workstation policy.

    - ``FAITHH_STRICT_LLM_GPU`` (default ``1`` / true): **overwrite** ``CUDA_VISIBLE_DEVICES``
      with ``FAITHH_CUDA_PHYSICAL_DEVICE`` (default ``1``).
    - Set ``FAITHH_STRICT_LLM_GPU=0`` to only ``setdefault`` (legacy / single-GPU setups).

    Returns a small dict for logging in the Flask app.
    """
    strict = os.environ.get("FAITHH_STRICT_LLM_GPU", "1").strip().lower() not in (
        "0",
        "false",
        "no",
        "off",
    )
    phys = get_faithh_cuda_physical_device_index()
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    if strict:
        os.environ["CUDA_VISIBLE_DEVICES"] = phys
        return {
            "strict": True,
            "cuda_visible_devices": phys,
            "cuda_device_order": "PCI_BUS_ID",
        }
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", phys)
    return {
        "strict": False,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "cuda_device_order": "PCI_BUS_ID",
    }


def faithh_strict_llm_gpu_enabled() -> bool:
    """True when ``FAITHH_STRICT_LLM_GPU`` forces ``CUDA_VISIBLE_DEVICES`` to the physical index (default on)."""
    return os.environ.get("FAITHH_STRICT_LLM_GPU", "1").strip().lower() not in (
        "0",
        "false",
        "no",
        "off",
    )


def build_gpu_hint_payload() -> JSONDict:
    # Logic for Humans: Expose whether this process's CUDA visibility string still matches FAITHH_CUDA_PHYSICAL_DEVICE so the Canvas can warn if WSL exported the wrong GPU before Flask started (Ollama is still a separate process — see response note).
    """JSON for ``GET /api/health/gpu-hint`` — MATCH vs MISMATCH for env vs configured physical index."""
    strict = faithh_strict_llm_gpu_enabled()
    target = get_faithh_cuda_physical_device_index()
    visible = os.environ.get("CUDA_VISIBLE_DEVICES")
    vnorm = (visible or "").strip()
    tnorm = (target or "1").strip()
    aligned = vnorm == tnorm
    alignment = "MATCH" if aligned else "MISMATCH"
    note_ollama = (
        "Flask env only; ensure the Ollama daemon uses the same CUDA_VISIBLE_DEVICES / physical GPU."
    )
    ui_primary_gpu = (
        "RTX 3090 (physical PCI index 1 — project default)"
        if tnorm == "1"
        else (f"physical PCI index {tnorm}" if tnorm else "unknown device index")
    )
    return {
        "alignment": alignment,
        "strict_gpu_policy": strict,
        "faithh_cuda_physical_device": tnorm,
        "cuda_visible_devices": visible if visible is not None else None,
        "cuda_device_order": os.environ.get("CUDA_DEVICE_ORDER"),
        "ui_primary_gpu": ui_primary_gpu,
        "message": (
            "CUDA visibility matches FAITHH_CUDA_PHYSICAL_DEVICE."
            if aligned
            else "CUDA_VISIBLE_DEVICES does not match FAITHH_CUDA_PHYSICAL_DEVICE — check WSL/shell exports before starting Flask."
        ),
        "ollama_note": note_ollama,
    }


# ---------------------------
# Types
# ---------------------------

Message = Dict[str, str]  # {"role": "system"|"user"|"assistant", "content": "..."}
JSONDict = Dict[str, Any]


class ProviderError(RuntimeError):
    pass


@dataclass
class LLMResult:
    text: str
    provider_key: str
    provider_type: str
    model: str
    route_key: str
    latency_ms: int
    usage: Optional[dict] = None
    raw: Optional[dict] = None


# ---------------------------
# Helpers
# ---------------------------

def _now_ms() -> int:
    return int(time.time() * 1000)


def _join_url(base_url: str, path: str) -> str:
    base = (base_url or "").rstrip("/")
    p = (path or "").lstrip("/")
    return f"{base}/{p}"


def _safe_get(d: Any, keys: List[Any], default=None):
    """Traverse dict/list JSON (e.g. choices[0].message.content). Integer steps index lists."""
    cur: Any = d
    for k in keys:
        if isinstance(cur, dict):
            if k not in cur:
                return default
            cur = cur[k]
        elif isinstance(cur, list):
            if not isinstance(k, int) or k < 0 or k >= len(cur):
                return default
            cur = cur[k]
        else:
            return default
    return cur


def groq_chat_completion_assistant_text(data: dict) -> str:
    """
    Groq chat.completions for reasoning models (e.g. qwen/qwen3-32b) may put the
    user-visible answer in message.content, message.reasoning, or split across
    both depending on reasoning_format. Never return empty if another field has text.
    """
    msg = _safe_get(data, ["choices", 0, "message"])
    legacy = normalize_assistant_text(_safe_get(data, ["choices", 0, "text"]))
    if not isinstance(msg, dict):
        return legacy if legacy.strip() else ""
    content = normalize_assistant_text(msg.get("content"))
    reasoning = normalize_assistant_text(
        msg.get("reasoning") or msg.get("reasoning_content")
    )
    if content.strip():
        return content
    if reasoning.strip():
        return reasoning
    return legacy if legacy.strip() else ""


def normalize_assistant_text(raw: Any) -> str:
    """
    Chat APIs may return message.content as a str or a list of structured parts.
    FAITHH /api/chat must always expose a string for the frontend contract.
    """
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw
    if isinstance(raw, (int, float, bool)):
        return str(raw)
    if isinstance(raw, list):
        parts: List[str] = []
        for item in raw:
            if isinstance(item, dict):
                t = item.get("text")
                if t is None:
                    t = item.get("content")
                parts.append(normalize_assistant_text(t))
            else:
                parts.append(normalize_assistant_text(item))
        return "".join(parts)
    if isinstance(raw, dict):
        return normalize_assistant_text(raw.get("text") or raw.get("content"))
    return str(raw)


def _messages_to_prompt(messages: List[Message]) -> str:
    """
    For providers that only accept a single prompt (Ollama /api/generate),
    we flatten chat messages into a readable transcript.
    """
    parts = []
    for m in messages:
        role = (m.get("role") or "user").upper()
        content = m.get("content") or ""
        parts.append(f"{role}:\n{content}")
    parts.append("ASSISTANT:\n")
    return "\n\n".join(parts)


# ---------------------------
# Retry Logic with Exponential Backoff
# ---------------------------

import random
import logging
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=30.0, backoff_factor=2.0):
    """
    Retry decorator with exponential backoff for API calls.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        backoff_factor: Multiplier for exponential backoff
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.RequestException, 
                        requests.exceptions.ConnectionError,
                        requests.exceptions.Timeout,
                        requests.exceptions.HTTPError,
                        ProviderError) as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        # Final attempt failed, log and raise
                        logging.error(f"API call failed after {max_retries + 1} attempts: {e}")
                        raise ProviderError(f"API call failed after {max_retries + 1} attempts: {e}")
                    
                    # Calculate delay with exponential backoff and jitter
                    delay = min(base_delay * (backoff_factor ** attempt) + random.uniform(0, 1), max_delay)
                    
                    logging.warning(f"API call attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator


# ---------------------------
# Connection Monitoring
# ---------------------------

class ConnectionMonitor:
    """Monitor backend service health and availability"""
    
    def __init__(self):
        self.health_checks = {}
        self.last_check = {}
        self.unhealthy_services = set()
    
    def check_service_health(self, service_name: str, health_check_func, check_interval: int = 60):
        """
        Check if a service is healthy
        
        Args:
            service_name: Name of the service
            health_check_func: Function that returns True if service is healthy
            check_interval: Minimum seconds between health checks
        """
        now = time.time()
        
        # Skip if we checked recently
        if (service_name in self.last_check and 
            now - self.last_check[service_name] < check_interval):
            return service_name not in self.unhealthy_services
        
        try:
            is_healthy = health_check_func()
            self.last_check[service_name] = now
            
            if not is_healthy:
                self.unhealthy_services.add(service_name)
                logging.warning(f"Service {service_name} is unhealthy")
                return False
            else:
                self.unhealthy_services.discard(service_name)
                logging.debug(f"Service {service_name} is healthy")
                return True
                
        except Exception as e:
            self.unhealthy_services.add(service_name)
            self.last_check[service_name] = now
            logging.error(f"Health check failed for {service_name}: {e}")
            return False
    
    def is_service_healthy(self, service_name: str) -> bool:
        """Quick check if service is marked as healthy"""
        return service_name not in self.unhealthy_services
    
    def get_unhealthy_services(self) -> set:
        """Get list of currently unhealthy services"""
        return self.unhealthy_services.copy()


# Global connection monitor instance
connection_monitor = ConnectionMonitor()

# Ollama fast health probe (cached to avoid per-request latency)
_OLLAMA_HEALTH_CACHE: dict[str, Any] = {"ts": 0.0, "ok": False, "url": ""}


def _ollama_tags_url(providers: Optional[JSONDict] = None) -> str:
    base = "http://localhost:11434"
    if providers and isinstance(providers.get("ollama"), dict):
        base = (providers["ollama"].get("base_url") or base).strip()
    if not base:
        base = "http://localhost:11434"
    base = base.rstrip("/")
    return f"{base}/api/tags"


def ollama_is_healthy(providers: Optional[JSONDict] = None) -> bool:
    """
    True if Ollama responds on /api/tags within OLLAMA_HEALTH_TIMEOUT seconds.
    Uses requests (not httpx) to avoid an extra dependency; results are TTL-cached.
    """
    url = _ollama_tags_url(providers)
    timeout_s = float(os.environ.get("OLLAMA_HEALTH_TIMEOUT", "3.0"))
    cache_ttl = float(os.environ.get("OLLAMA_HEALTH_CACHE_TTL", "2.0"))
    now = time.monotonic()
    if (
        _OLLAMA_HEALTH_CACHE["url"] == url
        and now - float(_OLLAMA_HEALTH_CACHE["ts"]) < cache_ttl
    ):
        return bool(_OLLAMA_HEALTH_CACHE["ok"])

    ok = False
    try:
        r = requests.get(url, timeout=timeout_s)
        ok = r.status_code == 200
    except (requests.exceptions.RequestException, OSError):
        ok = False

    _OLLAMA_HEALTH_CACHE["ts"] = now
    _OLLAMA_HEALTH_CACHE["ok"] = ok
    _OLLAMA_HEALTH_CACHE["url"] = url
    return ok


def _last_user_content(messages: List[Message]) -> str:
    for m in reversed(messages or []):
        if (m.get("role") or "").lower() == "user":
            return str(m.get("content") or "")
    return ""


# ---------------------------
# Provider calls
# ---------------------------

@retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=30.0)
def call_groq_chat(
    messages: List[Message],
    model: str,
    max_tokens: int = 512,
    temperature: float = 0.2,
    timeout_s: int = 45,
) -> Tuple[str, Optional[dict], dict]:
    """
    Calls Groq's OpenAI-compatible Chat Completions endpoint.
    Expects GROQ_API_KEY in environment.
    """
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise ProviderError("GROQ_API_KEY is not set")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": float(temperature),
        "max_tokens": int(max_tokens),
    }
    # Qwen3 on Groq defaults to reasoning tokens; without this, message.content can be
    # empty while reasoning lives in message.reasoning (FAITHH then shows "No response").
    if "qwen3" in (model or "").lower():
        payload["reasoning_effort"] = "none"

    r = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
    if r.status_code >= 400:
        raise ProviderError(f"Groq error {r.status_code}: {r.text[:500]}")

    data = r.json()
    text = groq_chat_completion_assistant_text(data)
    usage = data.get("usage")
    return text, usage, data


def call_openai_compatible_chat(
    base_url: str,
    model: str,
    messages: List[Message],
    max_tokens: int = 512,
    temperature: float = 0.2,
    timeout_s: int = 45,
    api_key_env: Optional[str] = None,
    extra_headers: Optional[dict] = None,
    extra_payload: Optional[dict] = None,
) -> Tuple[str, Optional[dict], dict]:
    """
    Calls an OpenAI-compatible /v1/chat/completions endpoint.
    Works for text-generation-webui's OpenAI extension, LM Studio, vLLM, etc.
    """
    url = _join_url(base_url, "/chat/completions")

    headers = {"Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)

    # Many local OpenAI-compatible servers ignore auth, but some require it.
    if api_key_env:
        api_key = os.environ.get(api_key_env, "").strip()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "messages": messages,
        "temperature": float(temperature),
        "max_tokens": int(max_tokens),
    }
    if extra_payload:
        payload.update(extra_payload)

    r = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
    if r.status_code >= 400:
        raise ProviderError(f"OpenAI-compatible error {r.status_code}: {r.text[:500]}")

    data = r.json()
    text = (
        _safe_get(data, ["choices", 0, "message", "content"])
        or _safe_get(data, ["choices", 0, "text"])
        or ""
    )
    text = normalize_assistant_text(text)
    usage = data.get("usage")
    return text, usage, data


def call_ollama_chat(
    base_url: str,
    model: str,
    prompt: str,
    temperature: float = 0.2,
    timeout_s: Optional[int] = None,
    num_ctx: Optional[int] = None,
    max_tokens_from_config: Optional[int] = None,
    stop: Optional[List[str]] = None,
) -> Tuple[str, Optional[dict], dict]:
    # Logic for Humans: This is just HTTP to Ollama — which GPU runs the model is decided when the **ollama** daemon starts (match FAITHH_CUDA_PHYSICAL_DEVICE / CUDA_VISIBLE_DEVICES there).
    """
    Calls Ollama's /api/generate with a single prompt.
    """
    url = _join_url(base_url, "/api/generate")
    # Options stay minimal: avoid num_gpu / num_thread — low num_gpu pushes layers to CPU in Ollama.
    opts: dict = {
        "temperature": float(temperature),
        "num_predict": default_ollama_num_predict(max_tokens_from_config),
    }
    if num_ctx is not None and int(num_ctx) > 0:
        opts["num_ctx"] = int(num_ctx)
    _stop = stop if stop is not None else faithh_ollama_stop_sequences()
    if _stop:
        opts["stop"] = _stop
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": opts,
    }

    if timeout_s is None:
        timeout_s = default_ollama_timeout_s()

    r = requests.post(url, json=payload, timeout=timeout_s)
    if r.status_code >= 400:
        raise ProviderError(f"Ollama error {r.status_code}: {r.text[:500]}")

    data = r.json()
    text = normalize_assistant_text(data.get("response", "") or "")
    # Ollama's usage varies; keep raw for inspection
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else None
    return text, usage, data


def iter_ollama_generate_stream(
    base_url: str,
    model: str,
    prompt: str,
    temperature: float = 0.2,
    timeout_s: Optional[int] = None,
    num_ctx: Optional[int] = None,
    max_tokens_from_config: Optional[int] = None,
    stop: Optional[List[str]] = None,
) -> Iterator[str]:
    """
    Stream decoded text deltas from Ollama /api/generate (stream: true).
    """
    url = _join_url(base_url, "/api/generate")
    # Same as call_ollama_chat: no num_gpu / num_thread — let Ollama keep layers on GPU by default.
    opts: dict = {
        "temperature": float(temperature),
        "num_predict": default_ollama_num_predict(max_tokens_from_config),
    }
    if num_ctx is not None and int(num_ctx) > 0:
        opts["num_ctx"] = int(num_ctx)
    _stop = stop if stop is not None else faithh_ollama_stop_sequences()
    if _stop:
        opts["stop"] = _stop
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": opts,
    }
    if timeout_s is None:
        timeout_s = default_ollama_timeout_s()
    with requests.post(url, json=payload, timeout=timeout_s, stream=True) as r:
        if r.status_code >= 400:
            raise ProviderError(f"Ollama error {r.status_code}: {r.text[:500]}")
        # Line-delimited JSON; decode_unicode + splitlines avoids buffering whole body.
        for line in r.iter_lines(decode_unicode=True):
            if line is None:
                continue
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            piece = obj.get("response") or ""
            if piece:
                yield piece
            if obj.get("done"):
                break


@retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=30.0)
def call_anthropic_chat(
    messages: List[Message],
    model: str,
    max_tokens: int,
    temperature: float,
    timeout_s: int,
    api_key: str,
) -> Tuple[str, Optional[dict], dict]:
    """Call Anthropic Claude API."""
    if not anthropic:
        raise ProviderError("anthropic package not installed")
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Convert messages format
    system_msg = None
    user_messages = []
    
    for msg in messages:
        if msg.get("role") == "system":
            system_msg = msg.get("content", "")
        else:
            user_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
    
    try:
        # NEWER API FORMAT: Include system message in messages array
        messages = user_messages
        
        # Add system message as first message if it exists
        if system_msg and system_msg.strip():
            messages = [{"role": "system", "content": system_msg}] + user_messages
        
        # DEBUG: Print parameters being sent
        print(f"   🔧 DEBUG: Anthropic API messages: {messages}")
        
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages,
        )
        
        text = response.content[0].text if response.content else ""
        usage = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens
        }
        
        return text, usage, {"model": model, "response": response}
        
    except Exception as e:
        raise ProviderError(f"Anthropic API error: {str(e)}")


# ---------------------------
# Dispatcher + Routing
# ---------------------------

def call_provider(
    provider_cfg: JSONDict,
    model_name: Optional[str],
    messages: List[Message],
) -> Tuple[str, Optional[dict], dict]:
    # Logic for Humans: Given one provider block from model_config.yaml, send the chat messages to Groq, Ollama, an OpenAI-compatible server, or Anthropic and return (text, usage, raw).
    """
    Provider dispatcher.

    provider_cfg examples:
      groq:
        type: groq
        model: llama-3.1-70b-versatile
        max_tokens: 800
        temperature: 0.2

      ollama:
        type: ollama
        base_url: http://localhost:11434
        model: llama31-faithh:latest
        temperature: 0.2

      local_webui:
        type: openai_compatible
        base_url: http://localhost:7001/v1
        model: qwen3-faithh:latest
    """
    ptype = (provider_cfg.get("type") or "").strip().lower()
    model = (model_name or provider_cfg.get("model") or "").strip()
    if not model and ptype not in ("ollama",):
        raise ProviderError("Missing model name")

    temperature = float(provider_cfg.get("temperature", 0.2))
    max_tokens = int(provider_cfg.get("max_tokens", 512))
    timeout_s = int(provider_cfg.get("timeout_s", 45))

    if ptype == "groq":
        return call_groq_chat(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout_s=timeout_s,
        )

    if ptype == "openai_compatible":
        base_url = provider_cfg.get("base_url", "").strip()
        if not base_url:
            raise ProviderError("openai_compatible provider missing base_url")
        api_key_env = provider_cfg.get("api_key_env")  # optional
        extra_headers = provider_cfg.get("headers")    # optional dict
        extra_payload = provider_cfg.get("payload")    # optional dict
        return call_openai_compatible_chat(
            base_url=base_url,
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout_s=timeout_s,
            api_key_env=api_key_env,
            extra_headers=extra_headers,
            extra_payload=extra_payload,
        )

    if ptype == "ollama":
        base_url = provider_cfg.get("base_url", "http://localhost:11434").strip()
        prompt = provider_cfg.get("prompt_override") or _messages_to_prompt(messages)
        # Ollama can run longer on big prompts/models (cold load from disk can exceed 120s)
        _to = provider_cfg.get("timeout_s")
        if _to is not None and str(_to).strip() != "":
            timeout_s = int(_to)
        else:
            timeout_s = default_ollama_timeout_s()
        _nc = provider_cfg.get("num_ctx")
        num_ctx = int(_nc) if _nc is not None and str(_nc).strip() != "" else None
        if num_ctx is not None and num_ctx <= 0:
            num_ctx = None
        _stop_raw = provider_cfg.get("ollama_stop")
        if isinstance(_stop_raw, list) and _stop_raw:
            ollama_stop: Optional[List[str]] = [str(x) for x in _stop_raw]
        else:
            ollama_stop = None
        return call_ollama_chat(
            base_url=base_url,
            model=model or provider_cfg.get("model", ""),
            prompt=prompt,
            temperature=temperature,
            timeout_s=timeout_s,
            num_ctx=num_ctx,
            max_tokens_from_config=max_tokens,
            stop=ollama_stop,
        )

    if ptype == "anthropic":
        api_key = provider_cfg.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ProviderError("Anthropic provider missing API key")
        return call_anthropic_chat(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout_s=timeout_s,
            api_key=api_key,
        )

    raise ProviderError(f"Unknown provider type: {ptype}")


def choose_route(intent: Optional[str], message: str) -> str:
    # Logic for Humans: Map user intent labels and quick message heuristics to a route name like "code", "fast", or "auto" for YAML routing.
    """
    Returns a route key. Keep this intentionally simple—your backend can
    pass intent tags when it knows them; otherwise we infer lightly.

    Suggested route keys:
      - "auto" (default)
      - "code" (prefer strongest coding model)
      - "fast" (prefer lowest-latency)
      - "local" (force local)
      - "cloud" (force cloud)
    """
    intent_norm = (intent or "").strip().lower()
    msg = (message or "")

    if intent_norm in ("code", "coding", "dev"):
        return "code"
    if intent_norm in ("fast", "quick"):
        return "fast"
    if intent_norm in ("local", "offline"):
        return "local"
    if intent_norm in ("cloud", "online"):
        return "cloud"

    # Heuristics
    if "```" in msg or "traceback" in msg.lower() or "stack trace" in msg.lower():
        return "code"

    return "auto"


def run_llm_route(
    route_key: str,
    messages: List[Message],
    model_config: JSONDict,
) -> LLMResult:
    # Logic for Humans: Walk the ordered provider list for a route, try each until one succeeds, raise if all fail.
    """
    Runs a route with fallback.

    Expects model_config like:
      providers: { groq: {...}, ollama: {...}, local_webui: {...} }
      routes:
        auto: [local_webui, groq, ollama]
        code: [local_webui, groq]
        fast: [groq, local_webui, ollama]
        local: [local_webui, ollama]
        cloud: [groq]

    If routes[route_key] missing, we treat route_key as a provider key.
    """
    providers: JSONDict = model_config.get("providers", {}) or {}
    routes: JSONDict = model_config.get("routes", {}) or {}

    # Determine provider order
    if route_key in routes and isinstance(routes[route_key], list):
        ordered_provider_keys = [str(x) for x in routes[route_key]]
    else:
        ordered_provider_keys = [route_key]

    # Default fallbacks (only appended if present)
    # Prefer local/Ollama before cloud fallback for predictable latency/cost.
    default_fallback = ["local_webui", "ollama", "groq"]
    for k in default_fallback:
        if k not in ordered_provider_keys:
            ordered_provider_keys.append(k)

    ordered_provider_keys = _apply_groq_gate_for_simple_local(
        ordered_provider_keys, route_key, messages, providers, "auto"
    )

    errors: List[str] = []
    start_ms = _now_ms()

    for pkey in ordered_provider_keys:
        pcfg = providers.get(pkey)
        if not isinstance(pcfg, dict):
            continue  # not configured
        try:
            call_start = _now_ms()
            text, usage, raw = call_provider(pcfg, model_name=pcfg.get("model"), messages=messages)
            latency_ms = _now_ms() - call_start

            return LLMResult(
                text=text,
                provider_key=pkey,
                provider_type=str(pcfg.get("type", "")),
                model=str(pcfg.get("model", "")),
                route_key=route_key,
                latency_ms=latency_ms,
                usage=usage,
                raw=raw,
            )
        except Exception as e:
            errors.append(f"{pkey}: {type(e).__name__}: {str(e)}")

    total_ms = _now_ms() - start_ms
    raise ProviderError(
        "All providers failed for route "
        f"'{route_key}' after {total_ms}ms. Errors: " + " | ".join(errors)
    )


# ---------------------------
# Mode Detection (Phase 2)
# ---------------------------

DOC_TRIGGER_PATTERNS = [
    r"\bfrom (my )?(docs|documents|project docs|project files)\b",
    r"\baccording to (my )?docs\b",
    r"\bbased on (my )?(docs|documents|project|project files)\b",
    r"\bsummarize from (my )?(docs|project docs)\b",
    r"\bin (my )?(docs|documentation|project)\b",
    r"\bwhat do(es)? (my )?(docs|project) say\b",
]


def is_low_complexity_chat_message(user_text: str) -> bool:
    # Logic for Humans: Return True for short greetings/small talk so we don’t route them to heavy “complex” models or cloud.
    """
    Greetings and light chit-chat → local Ollama (avoid false “complex” / cloud routing).

    **Order matters:** known greeting phrases are checked *before* the analytical
    “why/how does …” regex so strings like “Hello! How are you?” are never rejected
    by a misfire on the word “how”.
    """
    raw = (user_text or "").strip()
    if not raw:
        return True
    tl = raw.lower()

    normalized = re.sub(r"[!?.]+", " ", tl)
    normalized = re.sub(r"[,;:]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()

    _GREETING_PHRASES = frozenset(
        {
            "hi",
            "hello",
            "hey",
            "hiya",
            "howdy",
            "yo",
            "sup",
            "hi there",
            "hello there",
            "hey there",
            "good morning",
            "good afternoon",
            "good evening",
            "good day",
            "thanks",
            "thank you",
            "thx",
            "ty",
            "ok",
            "okay",
            "k",
            "how are you",
            "how are you doing",
            "hows it going",
            "how's it going",
            "how is it going",
            "whats up",
            "what's up",
            "whats the weather",
            "what's the weather",
            "hello how are you",
            "hi how are you",
            "hey how are you",
            "good morning how are you",
        }
    )
    if normalized in _GREETING_PHRASES:
        return True

    # Leading greeting + small allow-listed tail only
    if re.match(r"^(hi|hello|hey|hiya|howdy)\s+", normalized) and len(normalized) <= 48:
        tail = re.sub(r"^(hi|hello|hey|hiya|howdy)\s+", "", normalized).strip()
        if tail in frozenset({"there", "friend", "how are you", "how are you doing"}):
            return True

    _COMPLEX_KW = re.compile(
        r"\b(explain|analyze|compare|contrast|evaluate|imagine|brainstorm|design|implement|"
        r"debug|code|function|class|script|theorem|proof|quantum|entanglement)\b",
        re.I,
    )
    # Require “how/why” + analytical verb — *not* “how are you” (uses “are”)
    _WHY_HOW_ANALYTICAL = re.compile(
        r"\b(why|how)\s+(does|do|did|would|will|can)\b",
        re.I,
    )
    if _COMPLEX_KW.search(tl) or _WHY_HOW_ANALYTICAL.search(tl):
        return False

    # Very short messages: only common chit-chat tokens
    if len(raw) < 20:
        tokens = re.findall(r"[a-zA-Z']+", tl)
        _tiny_allow = frozenset(
            {
                "hi",
                "hello",
                "hey",
                "hiya",
                "howdy",
                "yo",
                "sup",
                "thanks",
                "thank",
                "you",
                "thx",
                "ty",
                "ok",
                "okay",
                "k",
                "bye",
                "goodbye",
                "yes",
                "no",
                "morning",
                "afternoon",
                "evening",
                "there",
                "friend",
                "are",
                "how",
                "doing",
                "it",
                "going",
                "is",
                "up",
                "whats",
                "what",
                "good",
                "day",
            }
        )
        if not tokens or all(t in _tiny_allow for t in tokens):
            return True

    # Broader greeting-led chit-chat (after complex-keyword gate)
    if re.match(r"^(hi|hello|hey|hiya|howdy|good\s+(morning|afternoon|evening|day))\b", normalized):
        if len(normalized) <= 52:
            return True

    return False


def detect_mode(user_text: str, intent: Optional[Union[str, dict]] = None, require_rag: Optional[bool] = None) -> str:
    # Logic for Humans: Classify the user message into a response style bucket (e.g. doc-grounded vs hybrid) used with complexity for model choice.
    """
    Detect the response mode based on user query and intent.

    Returns:
        - "doc_grounded": Must answer from docs only, refuse if no hits
        - "hybrid": Prefer docs but can supplement with general knowledge
        - "freeform": General chat, no doc requirement
    """
    t = (user_text or "").lower().strip()
    
    # Handle intent as dict or string
    intent_str = ""
    if isinstance(intent, dict):
        # Check for explicit flags in dict
        if require_rag:
            return "doc_grounded"
        if intent.get('needs_orientation') or intent.get('rag_required'):
            return "doc_grounded"
        if intent.get('rag_preferred'):
            return "hybrid"
        # Extract any relevant intent info for pattern matching
        if intent.get('patterns_matched'):
            intent_str = " ".join(intent.get('patterns_matched', []))
    elif isinstance(intent, str):
        intent_str = intent.lower()
        if require_rag:
            return "doc_grounded"
        if intent in ("doc_grounded", "project_recall", "rag_required"):
            return "doc_grounded"
        if intent in ("hybrid", "rag_preferred"):
            return "hybrid"
    
    # Combine user text and intent for pattern matching
    search_text = t + " " + intent_str

    # Check trigger patterns
    for pat in DOC_TRIGGER_PATTERNS:
        if re.search(pat, search_text, flags=re.IGNORECASE):
            return "doc_grounded"

    # Heuristic hybrid for project-specific terms
    project_terms = ["harmony", "faithh", "constella", "phase flip", "pml", "coherence sensor"]
    if any(x in search_text for x in project_terms):
        return "hybrid"

    return "freeform"


def detect_query_complexity(user_text: str, intent: Optional[Union[str, dict]] = None) -> str:
    # Logic for Humans: Label the question simple vs complex vs creative from length, keywords, and intent flags — drives which model tier we aim for.
    """
    Detect query complexity to determine optimal model routing.
    
    Returns:
        - "simple": Quick responses, use qwen25-grounded
        - "complex": Heavy reasoning, use llama3.3:70b
        - "creative": Brainstorming, use gemini
    """
    if is_low_complexity_chat_message(user_text):
        return "simple"

    t = (user_text or "").lower().strip()
    
    # Extract intent string if it's a dict
    if isinstance(intent, dict):
        # Look for specific intent flags that might indicate complexity
        if intent.get('is_complex_query'):
            return "complex"
        if intent.get('is_coding') or intent.get('is_business_query'):
            return "complex"
    elif isinstance(intent, str):
        t += " " + intent.lower()
    
    # Complex reasoning indicators
    complex_patterns = [
        r"\b(why|how) (does|do|did|would|will|can)",
        r"\b(explain|analyze|compare|contrast|evaluate)",
        r"\b(implications|consequences|effects|impact)",
        r"\b(relationship|connection|correlation)",
        r"\b(theory|principle|framework|paradigm)",
        r"\b(strategy|approach|methodology)",
        r"\b(pros and cons|advantages|disadvantages)",
        r"\b(step.by.step|detailed|in.depth)",
        r"\b(comprehensive|thorough|exhaustive)",
    ]
    
    # Creative/brainstorming indicators
    creative_patterns = [
        r"\b(imagine|envision|brainstorm|create)",
        r"\b(what if|suppose|consider|explore)",
        r"\b(invent|design|develop|innovate)",
        r"\b(story|narrative|poem|creative)",
        r"\b(inspire|vision|future|possibility)",
    ]
    
    # Check for complex patterns
    for pat in complex_patterns:
        if re.search(pat, t, flags=re.IGNORECASE):
            return "complex"
    
    # Check for creative patterns
    for pat in creative_patterns:
        if re.search(pat, t, flags=re.IGNORECASE):
            return "creative"
    
    # Length-based complexity
    if len(t) > 200:  # Long queries often need complex reasoning
        return "complex"
    
    # Question mark count (multiple questions = complex)
    if t.count('?') > 1:
        return "complex"
    
    # Default to simple
    return "simple"


def _apply_groq_gate_for_simple_local(
    ordered_keys: List[str],
    route_key: str,
    messages: List[Message],
    providers: JSONDict,
    provider_preference: str = "auto",
) -> List[str]:
    # Logic for Humans: For easy questions with a healthy local Ollama, drop Groq from the try-list so simple chat stays local and private.
    """
    When Ollama is healthy, exclude Groq from the fallback chain for simple
    queries so cloud is not used accidentally. When Ollama is unreachable,
    keep Groq and log explicitly.
    """
    if "groq" not in ordered_keys:
        return ordered_keys

    pref = (provider_preference or "auto").strip().lower()
    if pref == "groq":
        return ordered_keys

    rk = (route_key or "auto").strip().lower()
    if rk in frozenset({"cloud", "fast"}):
        return ordered_keys

    if not ollama_is_healthy(providers):
        logging.warning(
            "[Routing] Ollama unreachable — falling back to Groq if earlier providers fail."
        )
        return ordered_keys

    user_text = _last_user_content(messages)
    if detect_query_complexity(user_text) == "simple":
        logging.info(
            "[Routing] Simple query — Groq excluded from fallback (Ollama healthy)."
        )
        return [k for k in ordered_keys if k != "groq"]

    return ordered_keys


def get_optimal_model_for_query(
    user_text: str, intent: Optional[Union[str, dict]] = None, mode: Optional[str] = None
) -> Tuple[str, str]:
    # Logic for Humans: Pick (provider, model) for this utterance using complexity + mode + env overrides — used by “smart route” and some UI paths.
    """
    Determine the optimal model and provider for a given query.
    
    Returns:
        Tuple of (provider, model)
    """
    _grounded_model = os.environ.get(
        "OLLAMA_GROUNDED_MODEL", "qwen25-grounded-gen5-delta:latest"
    )
    if is_low_complexity_chat_message(user_text):
        return "ollama", _grounded_model

    complexity = detect_query_complexity(user_text, intent)
    response_mode = mode or detect_mode(user_text, intent)
    
    # Grounded responses: default gen5-delta (override with OLLAMA_GROUNDED_MODEL)
    if response_mode == "doc_grounded":
        return "ollama", _grounded_model
    
    # Check for explicit grounded patterns even if mode is hybrid
    grounded_patterns = [
        r"\b(according to|based on|from my) (docs|documentation|project|faithh_memory|decisions_log|project_states|scaffolding)",
        r"\b(what does|what do) (my )?(faithh_memory|decisions_log|project_states|scaffolding) (say|contain|show)",
        r"\b(in my|from my) (docs|documentation|project files)",
    ]
    
    for pat in grounded_patterns:
        if re.search(pat, user_text.lower(), flags=re.IGNORECASE):
            return "ollama", _grounded_model
    
    # Complex reasoning: prefer DeepSeek R1 (local Ollama); override with OLLAMA_COMPLEX_MODEL
    if complexity == "complex":
        complex_model = os.environ.get("OLLAMA_COMPLEX_MODEL", "deepseek-r1:32b")
        return "ollama", complex_model
    
    # Creative uses Gemini for speed and creativity
    if complexity == "creative":
        return "gemini", "gemini-2.0-flash-exp"
    
    # Default: use grounded model for reliability
    return "ollama", _grounded_model


def run_llm_smart_route(
    messages: List[Message],
    user_text: str,
    intent: Optional[str] = None,
    mode: Optional[str] = None,
    provider_preference: Optional[str] = None,
    model_config: Optional[JSONDict] = None,
) -> Dict[str, Any]:
    # Logic for Humans: Build a one-off provider order from get_optimal_model_for_query, inject it as route "smart_route", then delegate to run_llm_route_with_pin.
    """
    Smart routing that selects optimal model based on query complexity.
    This is the recommended entry point for FAITHH v4.
    """
    routing_config = copy.deepcopy(model_config or {})

    # Determine optimal model
    optimal_provider, optimal_model = get_optimal_model_for_query(user_text, intent, mode)

    pref = (provider_preference or "auto").strip().lower()
    if pref != "auto":
        optimal_provider = pref

    # Custom attempt order: optimal provider first, then sensible fallbacks
    attempt_order = [optimal_provider]
    if optimal_provider != "ollama":
        attempt_order.append("ollama")
    if optimal_provider != "gemini" and "gemini" in routing_config.get("providers", {}):
        attempt_order.append("gemini")

    provs = routing_config.setdefault("providers", {})
    if optimal_provider in provs and isinstance(provs[optimal_provider], dict):
        provs[optimal_provider] = dict(provs[optimal_provider])
        provs[optimal_provider]["model"] = optimal_model

    routes = routing_config.setdefault("routes", {})
    routes["smart_route"] = attempt_order

    return run_llm_route_with_pin(
        "smart_route",
        provider_preference or "auto",
        messages,
        routing_config,
    )


# ---------------------------
# Provider Pinning (Phase 2)
# ---------------------------

def build_provider_order(
    route_key: str,
    provider_preference: str,
    model_config: JSONDict,
) -> List[str]:
    # Logic for Humans: Merge “user pinned provider”, YAML route order, and default fallbacks into one deduped list of provider keys.
    """
    Build ordered list of provider keys to try.

    If provider_preference is set (not "auto"), that provider is tried first.
    Then route-specific order, then defaults.
    """
    providers = model_config.get("providers", {}) or {}
    routes = model_config.get("routes", {}) or {}

    order: List[str] = []
    pref = (provider_preference or "auto").strip().lower()

    # Pinned provider goes first
    if pref != "auto" and pref in providers:
        order.append(pref)

    # Route-specific order
    # Skip Ollama if it's not healthy (Proxmox environment - no local Ollama)
    route_list = routes.get(route_key)
    if isinstance(route_list, list):
        for k in route_list:
            k_str = str(k)
            if k_str == "ollama" and not ollama_is_healthy(providers):
                continue  # Skip unhealthy Ollama
            order.append(k_str)

    # Default fallbacks (local first, cloud last)
    # Skip Ollama if it's not healthy (Proxmox environment - no local Ollama)
    for k in ["local_webui", "ollama", "groq"]:
        if k in providers:
            if k == "ollama" and not ollama_is_healthy(providers):
                continue  # Skip unhealthy Ollama
            order.append(k)

    # Dedupe preserving order
    seen: set = set()
    return [k for k in order if not (k in seen or seen.add(k))]


def run_llm_route_with_pin(
    route_key: str,
    provider_preference: str,
    messages: List[Message],
    model_config: JSONDict,
) -> dict:
    # Logic for Humans: Primary chat LLM entry — try providers in order (with Groq gate), return text plus routing metadata for the API response.
    """
    Run LLM route with provider pinning and detailed routing metadata.

    Returns dict with:
        - text: response text
        - routing: {route, provider, model, latency_ms, used_fallback, attempted}
        - usage: token usage if available
        - raw: raw provider response
    """
    providers = model_config.get("providers", {}) or {}
    attempt_order = build_provider_order(route_key, provider_preference, model_config)
    attempt_order = _apply_groq_gate_for_simple_local(
        attempt_order, route_key, messages, providers, provider_preference
    )

    if not attempt_order:
        raise ProviderError("No providers configured")

    errors: List[str] = []
    attempted: List[str] = []
    pref = (provider_preference or "auto").strip().lower()
    pinned_first = (pref != "auto" and attempt_order and attempt_order[0] == pref)

    for idx, pkey in enumerate(attempt_order):
        pcfg = providers.get(pkey)
        if not isinstance(pcfg, dict):
            continue

        attempted.append(pkey)

        try:
            start_ms = _now_ms()
            text, usage, raw = call_provider(pcfg, pcfg.get("model"), messages)
            latency_ms = _now_ms() - start_ms

            return {
                "text": text,
                "routing": {
                    "route": route_key,
                    "provider": pkey,
                    "model": str(pcfg.get("model", "")),
                    "latency_ms": latency_ms,
                    "used_fallback": pinned_first and idx > 0,
                    "attempted": attempted,
                },
                "usage": usage,
                "raw": raw,
            }
        except Exception as e:
            errors.append(f"{pkey}: {type(e).__name__}: {str(e)}")

    raise ProviderError("All providers failed: " + " | ".join(errors))


def ollama_streaming_allowed_for_route(
    route_key: str,
    provider_preference: str,
    messages: List[Message],
    model_config: JSONDict,
    ollama_provider_key: str,
    providers_scanned_until_ollama: List[str],
) -> bool:
    """
    Allow Ollama /api/generate SSE when Ollama is ordered before Groq.

    The old guard (only stream if Ollama was first) skipped streaming whenever
    local_webui was first — the UI then fell through to buffered non-stream calls.
    """
    if providers_scanned_until_ollama and providers_scanned_until_ollama[0] == ollama_provider_key:
        return True
    providers = model_config.get("providers") or {}
    order = build_provider_order(route_key, provider_preference, model_config)
    order = _apply_groq_gate_for_simple_local(
        order, route_key, messages, providers, provider_preference
    )
    gi = order.index("groq") if "groq" in order else 10**9
    oi = order.index("ollama") if "ollama" in order else 10**9
    return oi < gi


def resolve_ollama_stream_target(
    route_key: str,
    provider_preference: str,
    messages: List[Message],
    model_config: JSONDict,
) -> Optional[Tuple[str, JSONDict, List[str]]]:
    """
    First Ollama provider entry in the routed attempt order (for SSE /api/chat).

    Returns (provider_key, ollama_provider_cfg, attempted_keys) or None.
    """
    providers = model_config.get("providers", {}) or {}
    attempt_order = build_provider_order(route_key, provider_preference, model_config)
    attempt_order = _apply_groq_gate_for_simple_local(
        attempt_order, route_key, messages, providers, provider_preference
    )
    attempted: List[str] = []
    for pkey in attempt_order:
        pcfg = providers.get(pkey)
        if not isinstance(pcfg, dict):
            continue
        attempted.append(pkey)
        if (pcfg.get("type") or "").strip().lower() == "ollama":
            return pkey, pcfg, attempted
    return None

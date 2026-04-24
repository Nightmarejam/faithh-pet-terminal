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
"""

from __future__ import annotations

import os
import re
import time
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

import requests

try:
    import anthropic
except ImportError:
    anthropic = None


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


def _safe_get(d: dict, keys: List[str], default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


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
# Provider calls
# ---------------------------

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

    r = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
    if r.status_code >= 400:
        raise ProviderError(f"Groq error {r.status_code}: {r.text[:500]}")

    data = r.json()
    text = (
        _safe_get(data, ["choices", 0, "message", "content"])
        or _safe_get(data, ["choices", 0, "text"])
        or ""
    )
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
    usage = data.get("usage")
    return text, usage, data


def call_ollama_chat(
    base_url: str,
    model: str,
    prompt: str,
    temperature: float = 0.2,
    timeout_s: int = 120,
) -> Tuple[str, Optional[dict], dict]:
    """
    Calls Ollama's /api/generate with a single prompt.
    """
    url = _join_url(base_url, "/api/generate")
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": float(temperature)},
    }

    r = requests.post(url, json=payload, timeout=timeout_s)
    if r.status_code >= 400:
        raise ProviderError(f"Ollama error {r.status_code}: {r.text[:500]}")

    data = r.json()
    text = data.get("response", "") or ""
    # Ollama's usage varies; keep raw for inspection
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else None
    return text, usage, data


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
        # Ollama can run longer on big prompts/models
        timeout_s = int(provider_cfg.get("timeout_s", 120))
        return call_ollama_chat(
            base_url=base_url,
            model=model or provider_cfg.get("model", ""),
            prompt=prompt,
            temperature=temperature,
            timeout_s=timeout_s,
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
    default_fallback = ["local_webui", "groq", "ollama"]
    for k in default_fallback:
        if k not in ordered_provider_keys:
            ordered_provider_keys.append(k)

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


def detect_mode(user_text: str, intent: Optional[Union[str, dict]] = None, require_rag: Optional[bool] = None) -> str:
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
    """
    Detect query complexity to determine optimal model routing.
    
    Returns:
        - "simple": Quick responses, use qwen25-grounded
        - "complex": Heavy reasoning, use llama3.3:70b
        - "creative": Brainstorming, use gemini
    """
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


def get_optimal_model_for_query(user_text: str, intent: Optional[str] = None, mode: Optional[str] = None) -> Tuple[str, str]:
    """
    Determine the optimal model and provider for a given query.
    
    Returns:
        Tuple of (provider, model)
    """
    complexity = detect_query_complexity(user_text, intent)
    response_mode = mode or detect_mode(user_text, intent)
    
    # Grounded responses always use qwen25-grounded
    if response_mode == "doc_grounded":
        return "ollama", "qwen25-grounded:latest"
    
    # Check for explicit grounded patterns even if mode is hybrid
    grounded_patterns = [
        r"\b(according to|based on|from my) (docs|documentation|project|faithh_memory|decisions_log|project_states|scaffolding)",
        r"\b(what does|what do) (my )?(faithh_memory|decisions_log|project_states|scaffolding) (say|contain|show)",
        r"\b(in my|from my) (docs|documentation|project files)",
    ]
    
    for pat in grounded_patterns:
        if re.search(pat, user_text.lower(), flags=re.IGNORECASE):
            return "ollama", "qwen25-grounded:latest"
    
    # Complex reasoning uses 70B model
    if complexity == "complex":
        return "ollama", "llama3.3:70b"
    
    # Creative uses Gemini for speed and creativity
    if complexity == "creative":
        return "gemini", "gemini-2.0-flash-exp"
    
    # Default: use grounded model for reliability
    return "ollama", "qwen25-grounded:latest"


def run_llm_smart_route(
    messages: List[Message],
    user_text: str,
    intent: Optional[str] = None,
    mode: Optional[str] = None,
    provider_preference: Optional[str] = None,
    model_config: Optional[JSONDict] = None,
) -> Dict[str, Any]:
    """
    Smart routing that selects optimal model based on query complexity.
    This is the recommended entry point for FAITHH v4.
    """
    model_config = model_config or {}
    
    # Determine optimal model
    optimal_provider, optimal_model = get_optimal_model_for_query(user_text, intent, mode)
    
    # Override preference if explicitly set
    if provider_preference and provider_preference != "auto":
        optimal_provider = provider_preference
    
    # Build custom attempt order with optimal model first
    attempt_order = [optimal_provider]
    if optimal_provider != "ollama":
        attempt_order.append("ollama")  # Add fallback
    if optimal_provider != "gemini" and "gemini" in model_config.get("providers", {}):
        attempt_order.append("gemini")  # Add another fallback
    
    # Override model config for optimal routing
    routing_config = model_config.copy()
    if optimal_provider in routing_config.get("providers", {}):
        routing_config["providers"][optimal_provider]["model"] = optimal_model
    
    # Use existing route_llm function
    return route_llm(
        route_key="smart_route",
        messages=messages,
        provider_preference="auto",  # We handle preference ourselves
        model_config=routing_config,
        attempt_order=attempt_order,
    )


# ---------------------------
# Provider Pinning (Phase 2)
# ---------------------------

def build_provider_order(
    route_key: str,
    provider_preference: str,
    model_config: JSONDict,
) -> List[str]:
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
    route_list = routes.get(route_key)
    if isinstance(route_list, list):
        order.extend([str(x) for x in route_list])

    # Default fallbacks
    for k in ["local_webui", "groq", "ollama"]:
        if k in providers:
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

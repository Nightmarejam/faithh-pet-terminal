# FAITHH Phase 2 Implementation - Claude Code Handoff
**Date:** 2025-12-17
**Prepared by:** GPT + Opus collaboration
**Target:** Claude Code implementation

---

## Overview

This document provides everything needed to implement:
1. Multi-provider routing with fallback
2. Doc-grounded mode enforcement
3. Evidence packets in responses
4. Provider badge in UI
5. Enhanced /api/status

---

## Files to Create

### 1. `backend/llm_providers.py`
**Location:** `~/ai-stack/backend/llm_providers.py`

```python
"""
FAITHH Phase 2 - Multi-Provider LLM Module

Provides:
- Groq (OpenAI-compatible chat endpoint)
- Ollama (prompt-based generate)
- Local text-generation-webui (OpenAI-compatible chat endpoint)
"""

from __future__ import annotations
import os
import time
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import requests

Message = Dict[str, str]
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

def _now_ms() -> int:
    return int(time.time() * 1000)

def _join_url(base_url: str, path: str) -> str:
    return f"{(base_url or '').rstrip('/')}/{(path or '').lstrip('/')}"

def _safe_get(d: dict, keys: List[str], default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

def _messages_to_prompt(messages: List[Message]) -> str:
    parts = []
    for m in messages:
        role = (m.get("role") or "user").upper()
        content = m.get("content") or ""
        parts.append(f"{role}:\n{content}")
    parts.append("ASSISTANT:\n")
    return "\n\n".join(parts)

# --- Provider Calls ---

def call_groq_chat(
    messages: List[Message],
    model: str,
    max_tokens: int = 512,
    temperature: float = 0.2,
    timeout_s: int = 45,
) -> Tuple[str, Optional[dict], dict]:
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise ProviderError("GROQ_API_KEY is not set")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "temperature": float(temperature), "max_tokens": int(max_tokens)}

    r = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
    if r.status_code >= 400:
        raise ProviderError(f"Groq error {r.status_code}: {r.text[:500]}")

    data = r.json()
    text = _safe_get(data, ["choices", 0, "message", "content"]) or ""
    return text, data.get("usage"), data

def call_openai_compatible_chat(
    base_url: str,
    model: str,
    messages: List[Message],
    max_tokens: int = 512,
    temperature: float = 0.2,
    timeout_s: int = 45,
    api_key_env: Optional[str] = None,
) -> Tuple[str, Optional[dict], dict]:
    url = _join_url(base_url, "/chat/completions")
    headers = {"Content-Type": "application/json"}
    
    if api_key_env:
        api_key = os.environ.get(api_key_env, "").strip()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

    payload = {"model": model, "messages": messages, "temperature": float(temperature), "max_tokens": int(max_tokens)}
    
    r = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
    if r.status_code >= 400:
        raise ProviderError(f"OpenAI-compatible error {r.status_code}: {r.text[:500]}")

    data = r.json()
    text = _safe_get(data, ["choices", 0, "message", "content"]) or ""
    return text, data.get("usage"), data

def call_ollama_chat(
    base_url: str,
    model: str,
    prompt: str,
    temperature: float = 0.2,
    timeout_s: int = 120,
) -> Tuple[str, Optional[dict], dict]:
    url = _join_url(base_url, "/api/generate")
    payload = {"model": model, "prompt": prompt, "stream": False, "options": {"temperature": float(temperature)}}

    r = requests.post(url, json=payload, timeout=timeout_s)
    if r.status_code >= 400:
        raise ProviderError(f"Ollama error {r.status_code}: {r.text[:500]}")

    data = r.json()
    return data.get("response", ""), data.get("usage"), data

# --- Provider Dispatcher ---

def call_provider(provider_cfg: JSONDict, model_name: Optional[str], messages: List[Message]) -> Tuple[str, Optional[dict], dict]:
    ptype = (provider_cfg.get("type") or "").strip().lower()
    model = (model_name or provider_cfg.get("model") or "").strip()
    temperature = float(provider_cfg.get("temperature", 0.2))
    max_tokens = int(provider_cfg.get("max_tokens", 512))
    timeout_s = int(provider_cfg.get("timeout_s", 45))

    if ptype == "groq":
        return call_groq_chat(messages, model, max_tokens, temperature, timeout_s)
    
    if ptype == "openai_compatible":
        base_url = provider_cfg.get("base_url", "").strip()
        if not base_url:
            raise ProviderError("openai_compatible provider missing base_url")
        return call_openai_compatible_chat(base_url, model, messages, max_tokens, temperature, timeout_s)
    
    if ptype == "ollama":
        base_url = provider_cfg.get("base_url", "http://localhost:11434").strip()
        prompt = _messages_to_prompt(messages)
        return call_ollama_chat(base_url, model or provider_cfg.get("model", ""), prompt, temperature, int(provider_cfg.get("timeout_s", 120)))

    raise ProviderError(f"Unknown provider type: {ptype}")

# --- Mode Detection ---

DOC_TRIGGER_PATTERNS = [
    r"\bfrom (my )?(docs|documents|project docs|project files)\b",
    r"\baccording to (my )?docs\b",
    r"\bbased on (my )?(docs|documents|project|project files)\b",
    r"\bsummarize from (my )?(docs|project docs)\b",
]

def detect_mode(user_text: str, intent: Optional[str], require_rag: Optional[bool]) -> str:
    t = (user_text or "").lower().strip()
    i = (intent or "").lower().strip()

    if require_rag:
        return "doc_grounded"
    if i in ("doc_grounded", "project_recall", "rag_required"):
        return "doc_grounded"
    if i in ("hybrid", "rag_preferred"):
        return "hybrid"
    
    for pat in DOC_TRIGGER_PATTERNS:
        if re.search(pat, t, flags=re.IGNORECASE):
            return "doc_grounded"
    
    # Heuristic hybrid for project-specific terms
    if any(x in t for x in ["harmony", "faithh", "constella", "phase flip", "pml"]):
        return "hybrid"
    
    return "freeform"

# --- Route Selection ---

def choose_route(intent: Optional[str], message: str) -> str:
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
    
    if "```" in msg or "traceback" in msg.lower():
        return "code"
    
    return "auto"

# --- Provider Order + Pinning ---

def build_provider_order(route_key: str, provider_preference: str, model_config: dict) -> List[str]:
    providers = model_config.get("providers", {}) or {}
    routes = model_config.get("routes", {}) or {}
    
    order = []
    pref = (provider_preference or "auto").strip().lower()
    
    if pref != "auto" and pref in providers:
        order.append(pref)
    
    route_list = routes.get(route_key)
    if isinstance(route_list, list):
        order.extend([str(x) for x in route_list])
    
    for k in ["local_webui", "groq", "ollama"]:
        if k in providers:
            order.append(k)
    
    # Dedupe preserving order
    seen = set()
    return [k for k in order if not (k in seen or seen.add(k))]

def run_llm_route_with_pin(
    route_key: str,
    provider_preference: str,
    messages: List[Message],
    model_config: dict,
) -> dict:
    providers = model_config.get("providers", {}) or {}
    attempt_order = build_provider_order(route_key, provider_preference, model_config)
    
    if not attempt_order:
        raise ProviderError("No providers configured")

    errors = []
    attempted = []
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
                    "attempted": attempted
                },
                "usage": usage,
                "raw": raw
            }
        except Exception as e:
            errors.append(f"{pkey}: {type(e).__name__}: {str(e)}")

    raise ProviderError("All providers failed: " + " | ".join(errors))
```

---

### 2. Updated `configs/model_config.yaml`
**Location:** `~/ai-stack/configs/model_config.yaml`

```yaml
# FAITHH model/provider configuration
# Phase 2: multi-provider routing enabled
# Updated: 2025-12-17

providers:
  groq:
    type: "groq"
    model: "qwen/qwen3-32b"  # Primary reasoning model
    temperature: 0.2
    max_tokens: 800
    timeout_s: 45

  ollama:
    type: "ollama"
    base_url: "http://localhost:11434"
    model: "llama3.1:8b"
    temperature: 0.2
    max_tokens: 800
    timeout_s: 120

  local_webui:
    type: "openai_compatible"
    base_url: "http://localhost:7001/v1"
    model: "qwen2.5-14b-instruct-q4_k_m"
    temperature: 0.2
    max_tokens: 900
    timeout_s: 120

routes:
  auto: ["groq", "local_webui", "ollama"]
  code: ["local_webui", "groq"]
  fast: ["groq", "local_webui", "ollama"]
  local: ["local_webui", "ollama"]
  cloud: ["groq"]
```

---

## Files to Modify

### 3. Patch `faithh_professional_backend_fixed.py`

**Changes needed:**

#### A) Add imports (near top)
```python
from backend.llm_providers import (
    detect_mode, choose_route, run_llm_route_with_pin, ProviderError
)
import yaml
```

#### B) Add globals (after imports)
```python
from datetime import datetime, timezone

RAG_ACTIVITY = {
    "last_query_ts": None,
    "last_query_summary": None,
}

def _iso_now():
    return datetime.now(timezone.utc).isoformat()

def record_rag_query(query: str, hits: int):
    RAG_ACTIVITY["last_query_ts"] = _iso_now()
    RAG_ACTIVITY["last_query_summary"] = {"query": query[:120], "hits": hits}
```

#### C) Load model config (near app init)
```python
def load_model_config():
    config_path = os.path.join(os.path.dirname(__file__), 'configs', 'model_config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

MODEL_CONFIG = load_model_config()
```

#### D) Add evidence builder helper
```python
def build_evidence(hits: list, mode: str) -> dict:
    def trunc(s: str, n: int = 240) -> str:
        s = (s or "").strip().replace("\n", " ")
        return s[:n] + ("…" if len(s) > n else "")
    
    sources = []
    snippets = []
    for h in (hits or [])[:2]:
        src = h.get("source") or h.get("doc") or h.get("id") or "unknown"
        if src not in sources:
            sources.append(src)
        snippets.append({"source": src, "text": trunc(h.get("text", ""))})
    
    return {
        "mode": mode,
        "rag_used": True,
        "rag_hits": len(hits or []),
        "sources": sources,
        "snippets": snippets
    }
```

#### E) Modify /api/chat handler

Find the existing `/api/chat` route and update the core logic:

```python
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    
    # Normalize request (backward compatible)
    intent = data.get('intent', 'auto')
    require_rag = data.get('require_rag', False)
    provider_pref = data.get('provider_preference', 'auto')
    
    # Detect mode
    mode = detect_mode(user_message, intent, require_rag)
    
    # RAG retrieval
    hits = []
    evidence = {"mode": mode, "rag_used": False, "rag_hits": 0, "sources": [], "snippets": []}
    
    if mode in ("doc_grounded", "hybrid") and data.get('use_rag', True):
        # Use existing RAG search
        hits = search_knowledge_base(user_message, k=6)  # Your existing function
        record_rag_query(user_message, len(hits))
        evidence = build_evidence(hits, mode)
        
        # Doc-grounded refusal if no hits
        if mode == "doc_grounded" and len(hits) == 0:
            return jsonify({
                "success": False,
                "response": "I couldn't find that in your indexed project docs yet. Try rephrasing or re-index the relevant file.",
                "routing": {"route": "memory_refusal", "provider": "none", "model": "none", "latency_ms": 0},
                "evidence": evidence,
                "warnings": ["RAG_EMPTY_DOC_GROUNDED"],
                "integrations_used": ["rag_search"]
            })
    
    # Build messages with evidence
    messages = build_messages_with_evidence(user_message, hits, mode)  # You'll need to implement this
    
    # Route and call LLM
    route_key = choose_route(intent, user_message)
    
    try:
        result = run_llm_route_with_pin(route_key, provider_pref, messages, MODEL_CONFIG)
        
        return jsonify({
            "success": True,
            "response": result["text"],
            "routing": result["routing"],
            "evidence": evidence,
            "integrations_used": ["rag_search"] if evidence["rag_used"] else [],
            "provider": result["routing"]["provider"],
            "model_used": result["routing"]["model"]
        })
    except ProviderError as e:
        return jsonify({
            "success": False,
            "response": f"Provider error: {str(e)}",
            "error": str(e)
        }), 500
```

#### F) Update /api/status to include RAG activity
```python
@app.route('/api/status', methods=['GET'])
def status():
    # ... existing status code ...
    
    status_data = {
        # ... existing fields ...
        "rag": {
            "enabled": True,
            "last_query_ts": RAG_ACTIVITY["last_query_ts"],
            "last_query_summary": RAG_ACTIVITY["last_query_summary"],
        },
        "memory": {
            "conversation_memory": "ephemeral",
            "project_memory": "rag"
        }
    }
    return jsonify(status_data)
```

---

### 4. UI Patch for `faithh_pet_v4.html`

#### A) Add provider badge HTML (in the HUD area)
```html
<div id="providerBadge" class="provider-badge" style="display:none;">
  <span class="provider-dot"></span>
  <span class="provider-meta">
    <span id="providerName">provider: —</span>
    <small id="providerModel">model: —</small>
    <small id="providerLatency">—ms</small>
  </span>
</div>
```

#### B) Add CSS
```css
.provider-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 10px;
  border: 1px solid rgba(255,255,255,0.18);
  border-radius: 999px;
  font-family: ui-monospace, monospace;
  font-size: 12px;
  background: rgba(0,0,0,0.25);
  color: rgba(255,255,255,0.92);
}
.provider-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: rgba(255,255,255,0.65);
}
.provider-badge[data-provider="groq"] .provider-dot { background: #7CFF6B; }
.provider-badge[data-provider="ollama"] .provider-dot { background: #6BD6FF; }
.provider-badge[data-provider="local_webui"] .provider-dot { background: #FF6BDF; }
```

#### C) Add JS function to update badge
```javascript
function updateProviderBadge(data) {
  const badge = document.getElementById('providerBadge');
  if (!badge) return;
  
  const routing = data.routing || {};
  const provider = routing.provider || data.provider || 'unknown';
  const model = routing.model || data.model_used || '—';
  const latency = routing.latency_ms || '—';
  
  badge.style.display = 'inline-flex';
  badge.dataset.provider = provider;
  document.getElementById('providerName').textContent = `provider: ${provider}`;
  document.getElementById('providerModel').textContent = `model: ${model}`;
  document.getElementById('providerLatency').textContent = `${latency}ms`;
}
```

#### D) Call updateProviderBadge after receiving response
In the fetch success handler, add:
```javascript
updateProviderBadge(data);
```

#### E) Fix port error message
Change "port 5560" to "port 5557" in error messages.

---

## Acceptance Tests

After implementation, verify:

1. **Harmony grounding**: "Describe the phase flip zone within my harmony project"
   - Expect: `evidence.rag_hits >= 1`, sources include Harmony docs

2. **FAITHH doc-grounded**: "What is FAITHH? Summarize from my project docs"
   - Expect: `mode = doc_grounded`, answer from docs not persona

3. **Refusal on missing**: "From my docs, explain the Blue Narwhal Protocol"
   - Expect: `rag_hits = 0`, refusal message, no hallucination

4. **Provider badge**: Any query shows provider/model/latency in UI

5. **Fallback**: Stop local_webui, send query
   - Expect: Falls back to Groq, `used_fallback = true`

---

## Implementation Order

1. Create `backend/llm_providers.py`
2. Update `configs/model_config.yaml`
3. Patch `faithh_professional_backend_fixed.py`
4. Patch `faithh_pet_v4.html`
5. Test with acceptance prompts
6. Verify /api/status shows RAG activity

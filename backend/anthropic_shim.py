"""
Anthropic Messages API shim for FAITHH.

Exposes POST /v1/messages (and GET /v1/models) so Claude Code CLI — and any tool
that speaks the Anthropic protocol — can route through FAITHH's local LLM stack
(Ollama / vLLM) with zero Anthropic API spend.

Usage (in the shell where you launch Claude Code):
    export ANTHROPIC_BASE_URL=http://localhost:5557
    export ANTHROPIC_API_KEY=faithh-local
    claude

Routing: uses the "local" route from configs/model_config.yaml.
  - openai_compatible providers (vLLM, text-generation-webui) get proper message format + streaming.
  - ollama providers fall back to /api/generate stream with prompt assembly.
  - Non-streaming calls go through run_llm_route_with_pin (handles fallback automatically).
"""

from __future__ import annotations

import json
import os
import time
import uuid
from typing import Iterator, List, Optional

import requests
from flask import Blueprint, Response, jsonify, request

from backend.llm_providers import (
    ProviderError,
    iter_ollama_generate_stream,
    run_llm_route_with_pin,
)

bp = Blueprint("anthropic_shim", __name__)

_MODEL_CONFIG: Optional[dict] = None


def _get_model_config() -> dict:
    global _MODEL_CONFIG
    if _MODEL_CONFIG is None:
        try:
            import yaml
            cfg_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "configs", "model_config.yaml")
            )
            with open(cfg_path) as f:
                _MODEL_CONFIG = yaml.safe_load(f) or {}
        except Exception:
            _MODEL_CONFIG = {"providers": {}, "routes": {}}
    return _MODEL_CONFIG


def reload_model_config() -> None:
    """Force reload — call after editing configs/model_config.yaml at runtime."""
    global _MODEL_CONFIG
    _MODEL_CONFIG = None


# ---------------------------------------------------------------------------
# Format conversion helpers
# ---------------------------------------------------------------------------

def _content_to_str(content) -> str:
    """Flatten Anthropic content (string or list of blocks) to plain text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type", "")
            if btype == "text":
                parts.append(block.get("text", ""))
            elif btype == "tool_result":
                inner = block.get("content", "")
                parts.append(_content_to_str(inner))
        return "\n".join(p for p in parts if p)
    return str(content or "")


def _anthropic_to_openai_messages(messages: list, system: Optional[str]) -> list:
    """Convert Anthropic messages list to OpenAI-compatible messages."""
    result: list = []
    if system:
        result.append({"role": "system", "content": system})
    for m in messages:
        role = m.get("role", "user")
        content = _content_to_str(m.get("content", ""))
        result.append({"role": role, "content": content})
    return result


def _openai_messages_to_prompt(messages: list) -> str:
    """Flatten OpenAI-format messages to a single prompt string for Ollama /api/generate."""
    parts = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        if role == "system":
            parts.append(f"[System: {content}]")
        elif role == "user":
            parts.append(f"USER: {content}")
        elif role == "assistant":
            parts.append(f"ASSISTANT: {content}")
    parts.append("ASSISTANT:")
    return "\n".join(parts)


def _msg_id() -> str:
    return "msg_" + uuid.uuid4().hex[:24]


def _build_response(text: str, model: str, input_tokens: int = 0, output_tokens: int = 0) -> dict:
    return {
        "id": _msg_id(),
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": text}],
        "model": model,
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
    }


# ---------------------------------------------------------------------------
# SSE helpers
# ---------------------------------------------------------------------------

def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _wrap_as_anthropic_sse(text_iter: Iterator[str], model: str) -> Iterator[str]:
    """Wrap a plain-text delta iterator as Anthropic SSE events."""
    msg_id = _msg_id()
    yield _sse("message_start", {
        "type": "message_start",
        "message": {
            "id": msg_id,
            "type": "message",
            "role": "assistant",
            "content": [],
            "model": model,
            "stop_reason": None,
            "stop_sequence": None,
            "usage": {"input_tokens": 0, "output_tokens": 0},
        },
    })
    yield _sse("content_block_start", {
        "type": "content_block_start",
        "index": 0,
        "content_block": {"type": "text", "text": ""},
    })
    yield _sse("ping", {"type": "ping"})

    output_tokens = 0
    for chunk in text_iter:
        if not chunk:
            continue
        output_tokens += len(chunk.split())
        yield _sse("content_block_delta", {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": chunk},
        })

    yield _sse("content_block_stop", {"type": "content_block_stop", "index": 0})
    yield _sse("message_delta", {
        "type": "message_delta",
        "delta": {"stop_reason": "end_turn", "stop_sequence": None},
        "usage": {"output_tokens": output_tokens},
    })
    yield _sse("message_stop", {"type": "message_stop"})


def _iter_openai_compat_stream(
    base_url: str,
    model: str,
    messages: list,
    max_tokens: int,
    temperature: float,
    timeout_s: int,
) -> Iterator[str]:
    """Stream text deltas from an OpenAI-compatible /v1/chat/completions endpoint."""
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": True,
    }
    with requests.post(
        url, json=payload, timeout=timeout_s, stream=True,
        headers={"Authorization": "Bearer faithh-local"},
    ) as r:
        if r.status_code >= 400:
            raise ProviderError(f"OpenAI-compat stream error {r.status_code}: {r.text[:200]}")
        for line in r.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data:"):
                continue
            raw = line[5:].strip()
            if raw == "[DONE]":
                break
            try:
                obj = json.loads(raw)
                content = obj.get("choices", [{}])[0].get("delta", {}).get("content") or ""
                if content:
                    yield content
            except (json.JSONDecodeError, IndexError):
                continue


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@bp.route("/v1/messages", methods=["POST"])
def messages_endpoint():
    """Anthropic Messages API — routes to FAITHH's local LLM stack."""
    data = request.get_json(force=True, silent=True) or {}

    stream = bool(data.get("stream", False))
    max_tokens = min(int(data.get("max_tokens", 1024)), 4096)
    temperature = float(data.get("temperature", 0.2))
    requested_model = data.get("model", "local")

    system = data.get("system") or None
    if isinstance(system, list):
        system = _content_to_str(system)

    raw_messages = data.get("messages", [])
    openai_messages = _anthropic_to_openai_messages(raw_messages, system)

    cfg = _get_model_config()
    providers = cfg.get("providers", {})
    local_route: List[str] = cfg.get("routes", {}).get("local", ["ollama"])

    # Pick display model name from first provider in route
    first_pcfg = providers.get(local_route[0], {}) if local_route else {}
    display_model = first_pcfg.get("model", requested_model)

    if stream:
        def generate():
            for pkey in local_route:
                pcfg = providers.get(pkey)
                if not isinstance(pcfg, dict):
                    continue
                ptype = pcfg.get("type", "")
                try:
                    if ptype == "openai_compatible":
                        text_iter = _iter_openai_compat_stream(
                            pcfg["base_url"],
                            pcfg["model"],
                            openai_messages,
                            max_tokens,
                            temperature,
                            pcfg.get("timeout_s", 300),
                        )
                    elif ptype == "ollama":
                        prompt = _openai_messages_to_prompt(openai_messages)
                        text_iter = iter_ollama_generate_stream(
                            pcfg.get("base_url", "http://localhost:11434"),
                            pcfg["model"],
                            prompt,
                            temperature=temperature,
                            timeout_s=pcfg.get("timeout_s", 300),
                        )
                    else:
                        continue
                    yield from _wrap_as_anthropic_sse(text_iter, display_model)
                    return
                except Exception:
                    continue

            yield _sse("error", {
                "type": "error",
                "error": {"type": "api_error", "message": "All local providers failed"},
            })

        return Response(
            generate(),
            mimetype="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # Non-streaming: delegate to run_llm_route_with_pin (handles fallback)
    try:
        result = run_llm_route_with_pin("local", "auto", openai_messages, cfg)
        text = result.get("text", "")
        usage = result.get("usage") or {}
        resp = _build_response(
            text,
            display_model,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
        )
        return jsonify(resp)
    except ProviderError as e:
        return jsonify({"type": "error", "error": {"type": "api_error", "message": str(e)}}), 503
    except Exception as e:
        return jsonify({"type": "error", "error": {"type": "api_error", "message": str(e)}}), 500


@bp.route("/v1/models", methods=["GET"])
def models_endpoint():
    """Stub /v1/models so Claude Code's startup model check passes."""
    cfg = _get_model_config()
    providers = cfg.get("providers", {})
    model_list = []
    for pcfg in providers.values():
        if isinstance(pcfg, dict) and "model" in pcfg:
            model_list.append({
                "id": pcfg["model"],
                "object": "model",
                "created": int(time.time()),
                "owned_by": "faithh",
            })
    # Stub entries so Claude Code's model validation doesn't reject the endpoint
    for stub in ["claude-opus-4-5", "claude-sonnet-4-5", "claude-haiku-4-5"]:
        model_list.append({
            "id": stub,
            "object": "model",
            "created": int(time.time()),
            "owned_by": "faithh-local",
        })
    return jsonify({"object": "list", "data": model_list})


@bp.route("/v1/messages", methods=["OPTIONS"])
@bp.route("/v1/models", methods=["OPTIONS"])
def shim_preflight():
    return Response(status=200, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, x-api-key, anthropic-version",
    })

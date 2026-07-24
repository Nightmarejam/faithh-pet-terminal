#!/usr/bin/env python3
"""
FAITHH Professional Backend v4.0-pulse
Smart integrations + PULSE Reflection Engine:
- Self-awareness boost (faithh_memory.json)
- Decision citation (decisions_log.json)
- Project state awareness (project_states.json)
- PULSE Reflection Engine (staleness, divergence, branches)

Structural map (how files talk to each other): docs/architecture/BACKEND_STRUCTURE_OVERVIEW.md
Major functions also carry inline "# Logic for Humans:" lines for plain-English behavior notes.
"""

import os

# CUDA: DISABLED for Proxmox VM environment (no GPU access)
# Original policy ran after ``load_dotenv`` via ``apply_faithh_llm_cuda_env()``
# os.environ.setdefault("CUDA_DEVICE_ORDER", "PCI_BUS_ID")
# os.environ.setdefault("CUDA_VISIBLE_DEVICES", "1")

from flask import Flask, request, jsonify, send_from_directory, g, Response, stream_with_context
from flask_cors import CORS
from werkzeug.utils import secure_filename
import copy
import requests
import json
import yaml
import sys
from pathlib import Path
import chromadb
import subprocess
from chromadb.utils import embedding_functions
from datetime import datetime, timedelta, timezone
import mimetypes
from dotenv import load_dotenv
import threading
from queue import Queue
import re
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import logging
import time
import random
import secrets
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    CONTENT_TYPE_LATEST,
    generate_latest,
)

# Phase 4 Security & Performance Systems
from backend.security_middleware import SecurityMiddleware, require_security
from backend.connection_monitor import connection_monitor, create_health_endpoint
from backend.health_monitor_facade import health_monitor_facade
from backend.cache import response_cache, cache_middleware, cached_response, start_cache_cleanup
from backend.performance import performance_tracker, track_request_performance
from backend.local_optimization import update_model_performance
from backend.session_metrics import (
    bump_from_chat_response,
    compute_summary_from_parsed_sessions,
    fetch_session_documents,
    flush_session_metrics,
    note_error,
    record_session_close,
    record_session_open,
)
from backend.chip_weight_metrics import get_chip_weights

# Import Google Search API
try:
    from google_search import GoogleSearchAPI
    GOOGLE_SEARCH_AVAILABLE = True
except ImportError:
    GOOGLE_SEARCH_AVAILABLE = False
    GoogleSearchAPI = None
import numpy as np

# Import Program Advance system
from backend.enhanced_chip_integration import (
    detect_program_advance,
    detect_program_advance_hybrid,
    get_pa_chips_for_query,
    build_enhanced_context,
    apply_merge_strategy,
    weighted_rrf_fusion,
    PROGRAM_ADVANCES
)

# Import Program Advance optimizer
from backend.program_advance_optimizer import program_advance_optimizer

# Import advanced analytics system
from backend.advanced_analytics_simple import advanced_analytics

# Import AI-driven UX system
from backend.ai_driven_ux import ai_driven_ux

# Import parasitic and universal impedance services for genomic support
from app.services.parasitic_alife_service_fixed import ParasiticAlifeService
from app.services.universal_impedance_field_optimized import UniversalImpedanceFieldOptimized
from app.services.cosmic_ripple_integration import CosmicRippleIntegration

# Phase 2 ML Components
try:
    from backend.ml.performance_tracker import performance_tracker, QueryPerformance
    from backend.ml.weight_optimizer import weight_optimizer
    from backend.ml.semantic_intent_detector import semantic_intent_detector
    PHASE2_ENABLED = True
    print("🤖 Phase 2 ML components loaded")
except ImportError as e:
    print(f"⚠️ Phase 2 ML components not available: {e}")
    PHASE2_ENABLED = False

# Phase 6: Genomic Impedance Reading Components
try:
    from app.services.genomic_impedance_sensor import GenomicImpedanceSensor
    from app.services.genomic_biasing_engine_fixed import GenomicBiasingEngine
    GENOMIC_ENABLED = True
    print("🧬 Genomic impedance components loaded")
except ImportError as e:
    print(f"⚠️ Genomic components not available: {e}")
    GENOMIC_ENABLED = False

# Phase 7: User Authentication Components
try:
    from app.services.user_authentication_service import UserAuthenticationService
    AUTH_ENABLED = True
    print("🔑 User authentication components loaded")
except ImportError as e:
    print(f"⚠️ Authentication components not available: {e}")
    AUTH_ENABLED = False

# Phase 7: Constella Constitution Components
try:
    from app.services.constella_constitution import ConstellaConstitution
    CONSTITUTION_ENABLED = True
    print("🌍 Constella Constitution components loaded")
except ImportError as e:
    print(f"⚠️ Constitution components not available: {e}")
    CONSTITUTION_ENABLED = False

# Phase 7: Focus Management Components
try:
    from app.services.focus_management import FocusManager
    FOCUS_ENABLED = True
    print("🧠 Focus management components loaded")
except ImportError as e:
    print(f"⚠️ Focus management components not available: {e}")
    FOCUS_ENABLED = False

# Import Coherence Arbiter
from backend.coherence_arbiter import CoherenceArbiter

logger = logging.getLogger(__name__)

from scripts.security import (
    get_scanner,
    scan_input,
    scan_output,
    PulseSelfHealer,
    get_audit_logger,
)

# Extracted modules (Phase 3 modularization)
from backend.data_loaders import (
    load_memory, load_decisions, load_project_states,
    load_scaffolding, save_scaffolding,
    MEMORY_FILE, DECISIONS_LOG, PROJECT_STATES, SCAFFOLDING_FILE,
)
from backend.intent_detection import detect_query_intent
from backend.llm_providers import (
    apply_faithh_llm_cuda_env,
    build_gpu_hint_payload,
    default_ollama_timeout_s,
    faithh_ollama_stop_sequences,
    get_faithh_cuda_physical_device_index,
    run_llm_route_with_pin,
    choose_route,
    ProviderError,
    get_optimal_model_for_query,
    normalize_assistant_text,
    resolve_ollama_stream_target,
    iter_ollama_generate_stream,
    is_low_complexity_chat_message,
    ollama_streaming_allowed_for_route,
)
from backend.performance_monitor import record_provider_performance, get_optimal_provider, get_provider_health
from backend.anthropic_shim import bp as anthropic_shim_bp
from backend.response_cache import get_cached_response, cache_response, get_cache_stats
from backend.ml_learning_framework import get_ml_framework
from backend.ui_layout_optimizer import record_ui_interaction, get_optimal_ui_layout, analyze_ui_usage_patterns
from backend.context_builders import (
    get_self_awareness_context, get_constella_awareness_context,
    search_decisions_log, get_project_state_context, get_scaffolding_context,
    get_faithh_personality, get_claude_personality, get_project_structure_snapshot,
    get_constella_enhanced_context, enhance_response_with_constella,
)
from backend.rag_processor import normalize_rag_hit_for_api


def _normalize_cached_chat_rag_blob(blob: dict) -> dict:
    # Logic for Humans: When we serve a cached chat reply, normalize any stored RAG hits so the UI always gets the same fields (document, distance, etc.).
    """Re-run normalize_rag_hit_for_api on cache hits (older entries may lack document/content)."""
    r = blob.get("rag_results")
    if not isinstance(r, list) or not r:
        return blob
    out = dict(blob)
    out["rag_results"] = [normalize_rag_hit_for_api(x) for x in r]
    return out


def _flush_chat_perf_metrics(
    *,
    message: str,
    request_id: str,
    chat_perf: dict,
    provider: str,
    model: str,
    cached: bool,
    streamed: bool,
) -> None:
    # Logic for Humans: Turn internal chat timing checkpoints into one JSON line in performance.log (RAG vs LLM vs overhead, plus optional GPU memory).
    """Append one JSON line to logs/performance.log (rag / llm / total + optional VRAM)."""
    wall0 = chat_perf.get("wall_t0")
    p0 = chat_perf.get("pipe_t0")
    tr = chat_perf.get("t_rag_end")
    tllm = chat_perf.get("t_llm_end")
    if wall0 is None or p0 is None or tr is None:
        return
    t_done = time.perf_counter()
    if tllm is None:
        tllm = tr
    llm_ms = 0.0 if cached else round((tllm - tr) * 1000, 2)
    row = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        "rag_ms": round((tr - p0) * 1000, 2),
        "llm_ms": llm_ms,
        "post_ms": round((t_done - tllm) * 1000, 2),
        "total_ms": round((t_done - wall0) * 1000, 2),
        "provider": provider,
        "model": model,
        "query_preview": (message[:120] if message else ""),
        "request_id": request_id,
        "cached": cached,
        "streamed": streamed,
    }
    for _k in ("request_source", "workspace_registry_json_bytes", "lean_workspace_registry"):
        if _k in chat_perf:
            row[_k] = chat_perf[_k]
    v = _sample_nvidia_vram_mib()
    if v:
        row.update(v)
    _append_chat_performance_log(row)


# Load environment variables from repo-root .env (authoritative).
# restart_backend.sh also `source`s .env in bash; bash parsing can differ from dotenv (quotes, CRLF).
# override=True so values parsed here replace any inherited/mangled os.environ entries.
_REPO_ROOT = Path(__file__).resolve().parent


def _append_chat_performance_log(row: dict) -> None:
    # Logic for Humans: Append a single metrics row to the on-disk performance log (used for tuning and debugging latency).
    """Append one JSON line to logs/performance.log (metrics lab)."""
    log_dir = _REPO_ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / "performance.log"
    try:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, default=str) + "\n")
    except OSError as exc:
        print(f"⚠️ performance log write failed: {exc}", flush=True)


def _sample_nvidia_vram_mib() -> dict | None:
    # Logic for Humans: Ask nvidia-smi how much GPU memory is in use so we can attach it to performance logs.
    """Best-effort VRAM sample via nvidia-smi (no pynvml dependency)."""
    try:
        r = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.used,memory.total",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode != 0 or not (r.stdout or "").strip():
            return None
        line = (r.stdout or "").strip().splitlines()[0]
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 2:
            return None
        return {
            "vram_used_mib": int(float(parts[0])),
            "vram_total_mib": int(float(parts[1])),
        }
    except (OSError, ValueError, subprocess.TimeoutExpired, IndexError):
        return None


_ENV_FILE = _REPO_ROOT / ".env"
if _ENV_FILE.is_file():
    load_dotenv(_ENV_FILE, override=True)
else:
    load_dotenv()

_FAITHH_CUDA_POLICY = apply_faithh_llm_cuda_env()
if _FAITHH_CUDA_POLICY.get("strict"):
    print(
        "🔒 FAITHH strict LLM GPU: "
        f"CUDA_VISIBLE_DEVICES={_FAITHH_CUDA_POLICY.get('cuda_visible_devices')} "
        "(physical PCI index; start Ollama with the same visibility so inference hits the 3090).",
        flush=True,
    )

# PULSE Tier-4 state JSON (used by /api/pulse/state and chat tool-intent augmentation)
PULSE_STATE_FILE = _REPO_ROOT / "ml" / "output" / "pulse_state.json"

# =======================================================
# GPU-AWARE MODEL SELECTION
# =======================================================
import psutil

def is_gaming_active():
    # Logic for Humans: Peek at running process names to guess if the machine is busy with games/OBS so we can pick a lighter model.
    """Check if gaming/streaming processes are running"""
    gaming_processes = [
        'steam', 'Steam', 'STEAM',
        'obs', 'OBS', 'ObsStudio',
        'elgato', 'Elgato', 'GameCapture',
        'nvidia-settings', 'nvidia-smi'  # GPU intensive apps
    ]
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if any(gaming in proc.info['name'] for gaming in gaming_processes):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def select_gpu_aware_model(intent):
    # Logic for Humans: Pick an Ollama model tag from coarse intent flags (gaming load, coding, reasoning) — parallel to YAML routing, used in some legacy paths.
    """Select model based on GPU availability and query complexity
    
    Available models (as of 2026-03-02):
    - qwen25-grounded:latest (default, fast, good for most queries)
    - deepseek-r1:32b (reasoning, complex analysis)
    - llama3.3:70b (disabled - too slow for interactive use)
    """
    # Check if gaming is active - use lightweight model
    if is_gaming_active():
        print("🎮 Gaming detected - using lightweight model", flush=True)
        return "qwen25-grounded-gen5-delta:latest"
    
    # Check intent complexity
    is_reasoning = intent.get('is_reasoning', False)
    is_coding = intent.get('is_coding', False)
    is_complex = intent.get('is_complex_query', False)
    
    print(f"🧠 Intent flags: reasoning={is_reasoning}, coding={is_coding}, complex={is_complex}", flush=True)
    
    # Coding -> grounded model (fast, accurate)
    if is_coding:
        print("💻 Coding query - using grounded model", flush=True)
        return "qwen25-grounded-gen5-delta:latest"
    
    # Complex reasoning -> deepseek-r1:32b (good reasoning, reasonable speed)
    if is_reasoning or is_complex:
        print("🧠 Complex query - using deepseek-r1:32b reasoning model", flush=True)
        return "deepseek-r1:32b"
    
    # Default -> grounded model
    print("🤖 Default query - using grounded model", flush=True)
    return "qwen25-grounded-gen5-delta:latest"

# ============================================================
# FILESYSTEM CHIP INTEGRATION (added 2025-12-29)
# ============================================================
try:
    from filesystem_chip import FilesystemChip
    from knowledge_graph import KnowledgeGraph, get_knowledge_graph
    FILESYSTEM_CHIP = FilesystemChip()
    KNOWLEDGE_GRAPH = get_knowledge_graph()
    print("✅ Filesystem chip loaded")
    print(f"✅ Knowledge graph loaded: {KNOWLEDGE_GRAPH._loaded if KNOWLEDGE_GRAPH else False}")
except ImportError as e:
    FILESYSTEM_CHIP = None
    KNOWLEDGE_GRAPH = None
    print(f"⚠️ Filesystem/Knowledge modules not available: {e}")

# ============================================================
# PULSE PATTERN TRACKER (added 2026-01-01)
# ============================================================
try:
    from pulse_pattern_tracker import pulse_tracker
    print("✅ PULSE pattern tracker loaded")
except ImportError as e:
    pulse_tracker = None
    print(f"⚠️ PULSE pattern tracker not available: {e}")

# Initialize Google Search API
google_search = None
if GOOGLE_SEARCH_AVAILABLE:
    try:
        google_search = GoogleSearchAPI()
        print("✅ Google Search API initialized")
    except Exception as e:
        print(f"❌ Google Search API initialization failed: {e}")
        google_search = None

app = Flask(__name__)
# Chrome Private Network Access: POST + JSON triggers preflight; if the browser sends
# Access-Control-Request-Private-Network, we must respond with Allow-Private-Network: true
# or the fetch fails with NetworkError (simple GETs may still appear to work).
CORS(app, allow_private_network=True)
app.register_blueprint(anthropic_shim_bp)

# Initialize Phase 4 Security & Performance Systems
# Disable rate limiting for single-user deployment
security_middleware = SecurityMiddleware(max_requests=100, window_seconds=3600, enable_rate_limiting=False)

# Start background services
connection_monitor.start_monitoring()
start_cache_cleanup()

# Initialize Genomic Services (Phase 6)
genomic_impedance_sensor = None
genomic_biasing_engine = None
if GENOMIC_ENABLED:
    try:
        # Initialize required services for genomic components
        parasitic_alife_service = ParasiticAlifeService()
        cosmic_ripple_service = CosmicRippleIntegration(parasitic_alife_service)
        universal_impedance_service = UniversalImpedanceFieldOptimized(cosmic_ripple_service)
        
        # Now initialize genomic services with their dependencies
        genomic_impedance_sensor = GenomicImpedanceSensor(parasitic_alife_service, universal_impedance_service)
        genomic_biasing_engine = GenomicBiasingEngine(genomic_impedance_sensor)
        print("🧬 Genomic services initialized with dependencies")
    except Exception as e:
        print(f"⚠️ Genomic services initialization failed: {e}")
        GENOMIC_ENABLED = False

# Initialize Authentication Service (Phase 7)
auth_service = None
if AUTH_ENABLED:
    try:
        auth_service = UserAuthenticationService()
        print("🔑 Authentication service initialized")
    except Exception as e:
        print(f"⚠️ Authentication service initialization failed: {e}")
        AUTH_ENABLED = False

# Initialize Constella Constitution (Phase 7)
constitution_service = None
if CONSTITUTION_ENABLED:
    try:
        constitution_service = ConstellaConstitution()
        print("🌍 Constella Constitution service initialized")
    except Exception as e:
        print(f"⚠️ Constitution service initialization failed: {e}")
        CONSTITUTION_ENABLED = False

# Node attestation (proof-of-life) — the SAME node-agnostic module the Lite node uses.
# The power unit now self-attests: signed heartbeats carrying liveness + real work +
# continuity (an append-only chain), offline, no central DB. Human proof-of-presence
# (binding a unique person to the node) is a LATER layer — added when the phone-sized
# model ships; see node_attestation.derive_key's PUF note for the seam.
ATTESTOR = None
ATTEST_ENABLED = False
QUERIES_SERVED = 0  # real work this node did = chat queries actually answered

def _note_query_served():
    """Increment the power unit's real-work counter (fed into proof-of-life heartbeats)."""
    global QUERIES_SERVED
    QUERIES_SERVED += 1

try:
    import sys as _sys
    _NA_DIR = str(Path(__file__).resolve().parent / "faithh-lite")
    if _NA_DIR not in _sys.path:
        _sys.path.insert(0, _NA_DIR)
    from node_attestation import NodeAttestor, derive_key
    ATTESTOR = NodeAttestor("faithh-power-unit", derive_key("faithh-power-unit"))
    ATTEST_ENABLED = True
    print("🫀 Node attestation initialized (power unit self-attests)")
except Exception as e:
    print(f"⚠️ Node attestation unavailable: {e}")

# Initialize Focus Management (Phase 7)
focus_service = None
if FOCUS_ENABLED:
    try:
        focus_service = FocusManager()
        print("🧠 Focus management service initialized")
    except Exception as e:
        print(f"⚠️ Focus management service initialization failed: {e}")
        FOCUS_ENABLED = False

# Global executor for parallel chip retrieval (5 workers = max concurrent chips)
CHIP_EXECUTOR = ThreadPoolExecutor(max_workers=5, thread_name_prefix="chip_")

# Token budget configuration (~5,400 total for chips with 8k context)
CHIP_TOKEN_BUDGETS = {
    'rag_search': 1800,      # Primary knowledge
    'scaffolding': 600,      # Project context
    'decisions': 675,        # Decision history
    'project_state': 450,    # Structured state
    'constella': 450,        # Framework
    'self_awareness': 450,   # Identity
    'project_structure': 1200, # Live file listing + git history (anti-hallucination)
    'conversation_history': 225,  # Recent turns
}

# Phase 4 — RAG distance signal (updated when RAG runs; exposed via workspace registry + /api/chat)
RAG_MAX_DISTANCE_CONFIDENT = float(os.environ.get("RAG_MAX_DISTANCE_CONFIDENT", "0.55"))
RAG_SIGNAL_STALE_SECONDS = float(os.environ.get("RAG_SIGNAL_STALE_SECONDS", "900"))
LAST_RAG_RETRIEVAL_SIGNAL: dict = {}

def count_tokens(text: str) -> int:
    # Logic for Humans: Cheap estimate of how “long” a text is in tokens so we can cap context size without a real tokenizer.
    """Rough token count (avg 4 chars per token)"""
    if not text:
        return 0
    return len(text) // 4

def truncate_to_budget(text: str, max_tokens: int) -> str:
    # Logic for Humans: Cut a long string down so it fits an approximate token budget, preferring to break at a newline or sentence.
    """Truncate text to fit within token budget"""
    if not text:
        return text
    current_tokens = count_tokens(text)
    if current_tokens <= max_tokens:
        return text
    # Truncate to approximate character limit
    max_chars = max_tokens * 4
    truncated = text[:max_chars]
    # Try to end at a sentence or newline
    last_break = max(truncated.rfind('\n'), truncated.rfind('. '))
    if last_break > max_chars * 0.8:  # Only if we keep 80%+
        truncated = truncated[:last_break + 1]
    return truncated + "\n[...truncated for context limit...]"


def is_ping_like_prompt(text: str) -> bool:
    # Logic for Humans: Detect “are you alive?” style messages so we skip heavy RAG and model calls for noise.
    """True for trivial probes where we should NOT run chips/RAG or call any model.

    Fixed to allow substantive queries while blocking actual pings.
    """
    if text is None:
        return True

    raw = str(text).strip().lower()
    if not raw or len(raw) < 5:  # Require minimum content
        return True

    # Only treat exact short commands as pings (no normalization)
    ping_commands = {"ping", "pong", "health", "status", "ok"}
    if raw in ping_commands and len(raw) <= 5:
        return True

    return False

# Configuration
BACKEND_VERSION = os.environ.get("FAITHH_BACKEND_VERSION", "v4.0-pulse")
EMBEDDING_MODEL_NAME = "BAAI/bge-base-en-v1.5 (768-dim)"
EMBEDDING_MODEL_ID = os.environ.get("FAITHH_EMBEDDER_MODEL", "BAAI/bge-base-en-v1.5")
EMBEDDER_ALLOW_DOWNLOAD = os.environ.get("FAITHH_EMBEDDER_ALLOW_DOWNLOAD", "0") == "1"
EMBEDDER_LOCAL_ONLY = os.environ.get("FAITHH_EMBEDDER_LOCAL_ONLY", "1") == "1"
DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL", "qwen25-grounded-gen5-delta:latest")

# Coherence Arbiter Configuration
COHERENCE_ARBITER_ENABLED = os.environ.get("COHERENCE_ARBITER_ENABLED", "1") == "1"
COHERENCE_TIMEOUT_MS = int(os.environ.get("COHERENCE_TIMEOUT_MS", "100"))

# Initialize Coherence Arbiter
COHERENCE_ARBITER = CoherenceArbiter(timeout_ms=COHERENCE_TIMEOUT_MS) if COHERENCE_ARBITER_ENABLED else None

MODEL_PROVIDER = os.environ.get("MODEL_PROVIDER", "ollama").lower()
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_CONNECT_TIMEOUT = int(os.environ.get("OLLAMA_CONNECT_TIMEOUT", "10"))
OLLAMA_READ_TIMEOUT = int(os.environ.get("OLLAMA_READ_TIMEOUT", "300"))  # Increased from 180 for 70B model
OLLAMA_NUM_PREDICT = int(os.environ.get("OLLAMA_NUM_PREDICT", "2048"))
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")


def _normalize_anthropic_api_key(raw: str | None) -> str | None:
    # Logic for Humans: Clean up the Anthropic API key string from .env (quotes, BOM) so auth failures aren’t from invisible characters.
    """Strip BOM/whitespace and optional wrapping quotes — common 401 causes with .env / WSL."""
    if raw is None:
        return None
    s = str(raw).strip().lstrip("\ufeff")
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        s = s[1:-1].strip()
    return s or None


ANTHROPIC_API_KEY = _normalize_anthropic_api_key(os.environ.get("ANTHROPIC_API_KEY"))
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_BASE_URL = os.environ.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
OLLAMA_DEFAULT_MODEL = os.environ.get("OLLAMA_DEFAULT_MODEL", "qwen25-grounded-gen5-delta:latest")
OLLAMA_REASONING_MODEL = os.environ.get("OLLAMA_REASONING_MODEL", "deepseek-r1:32b")
FAITHH_FORCE_LOCAL = os.environ.get("FAITHH_FORCE_LOCAL", "").strip().lower() in ("1", "true", "yes")

if ANTHROPIC_API_KEY:
    print(f"🔑 Anthropic API key configured (length={len(ANTHROPIC_API_KEY)} chars, no preview)")
    if not ANTHROPIC_API_KEY.startswith("sk-ant-"):
        print(
            "⚠️  Key does not start with sk-ant- — Anthropic Console API keys look like sk-ant-api03-... "
            "(other prefixes are usually Groq/OpenAI/etc. and will 401 on api.anthropic.com)."
        )
else:
    print("🔑 Anthropic API key not set (Claude via /api/chat requires ANTHROPIC_API_KEY in .env)")

CHROMA_URL = os.environ.get("CHROMA_URL")
CHROMA_HOST = os.environ.get("CHROMA_HOST", "servicebox.taileb8c60.ts.net")  # Updated for Proxmox (Gen8 NAS)
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", 8000))
FILESYSTEM_TOKEN = os.environ.get("FAITHH_FILESYSTEM_TOKEN")
UPLOAD_FOLDER = Path.home() / 'ai-stack' / 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'md', 'py', 'js', 'html', 'css', 'json', 'yaml', 'yml'}

# Create upload folder
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Base directory
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Phase-2 multi-provider routing config (used by /api/chat via run_llm_route_with_pin)
def _load_faithh_model_config():
    # Logic for Humans: Load configs/model_config.yaml — the routing table that says which LLM providers to try in which order.
    path = BASE_DIR / "configs" / "model_config.yaml"
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


try:
    FAITHH_MODEL_CONFIG = _load_faithh_model_config()
    print("✅ Loaded configs/model_config.yaml for LLM routing")
except Exception as e:
    FAITHH_MODEL_CONFIG = {"providers": {}, "routes": {}}
    print(f"⚠️ Could not load configs/model_config.yaml: {e}")


def _load_faithh_repo_config_yaml() -> dict:
    # Logic for Humans: Load repo-root config.yaml for high-level AI settings that aren’t per-provider routing.
    path = BASE_DIR / "config.yaml"
    if not path.is_file():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
    except Exception as e:
        print(f"⚠️ Could not load config.yaml: {e}")
        return {}


FAITHH_REPO_CONFIG = _load_faithh_repo_config_yaml()
_ai_top = FAITHH_REPO_CONFIG.get("ai")
FAITHH_CONFIG_AI: dict = _ai_top if isinstance(_ai_top, dict) else {}


def _normalize_host_port(host, port):
    # Logic for Humans: Accept Chroma host as plain hostname, host:port string, or full URL and return a clean (host, port) pair.
    if host.startswith("http://") or host.startswith("https://"):
        parsed = urlparse(host)
        host = parsed.hostname or host
        port = parsed.port or port
        return host, port
    if ":" in host and host.count(":") == 1:
        raw_host, raw_port = host.split(":", 1)
        try:
            return raw_host, int(raw_port)
        except ValueError:
            return host, port
    return host, port


def _build_chroma_base_url():
    # Logic for Humans: Build the http://host:port base URL the Chroma HTTP client will use, from CHROMA_URL or CHROMA_HOST/PORT.
    if CHROMA_URL:
        return CHROMA_URL.rstrip("/")
    if CHROMA_HOST.startswith("http://") or CHROMA_HOST.startswith("https://"):
        parsed = urlparse(CHROMA_HOST)
        scheme = parsed.scheme or "http"
        host = parsed.hostname or CHROMA_HOST
        port = parsed.port or CHROMA_PORT
        return f"{scheme}://{host}:{port}"
    if ":" in CHROMA_HOST and CHROMA_HOST.count(":") == 1:
        return f"http://{CHROMA_HOST}"
    return f"http://{CHROMA_HOST}:{CHROMA_PORT}"


if CHROMA_URL:
    try:
        parsed = urlparse(CHROMA_URL)
        if parsed.hostname:
            CHROMA_HOST = parsed.hostname
        if parsed.port:
            CHROMA_PORT = parsed.port
    except Exception as e:
        print(f"⚠️ Invalid CHROMA_URL '{CHROMA_URL}': {e}")

CHROMA_HOST, CHROMA_PORT = _normalize_host_port(CHROMA_HOST, CHROMA_PORT)
CHROMA_BASE_URL = _build_chroma_base_url()

CHROMA_COLLECTION = os.environ.get('CHROMA_COLLECTION', 'faithh_knowledge_base')
METRICS_COLLECTION_NAME = os.environ.get("CHROMA_METRICS_COLLECTION", "faithh_session_metrics")

# Load embedding model lazily for manual query embedding
# NOTE: SentenceTransformer import moved inside get_query_embedder() to prevent
# CUDA initialization at module load time (causes WSL crashes on sm_61 GPUs)
query_embedder = None
_embedder_init_attempted = False
_embedder_load_error = None
_SentenceTransformer = None  # Lazy import holder

if not EMBEDDER_ALLOW_DOWNLOAD:
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")


def get_query_embedder():
    # Logic for Humans: Load the sentence-transformer model on CPU, only when first needed, so RAG queries can be embedded without torch probing the wrong GPU at import time.
    """Lazy-load embedder; avoid blocking startup when offline.
    
    IMPORTANT: SentenceTransformer is imported here (not at module level) to prevent
    CUDA initialization at startup, which crashes WSL on sm_61 GPUs (GTX 1080 Ti).
    """
    global query_embedder, _embedder_init_attempted, _embedder_load_error, _SentenceTransformer
    if query_embedder is not None or _embedder_init_attempted:
        return query_embedder

    _embedder_init_attempted = True

    try:
        # Lazy import to avoid CUDA init at module load — temporarily hide all GPUs so ST never touches the 1080 Ti.
        if _SentenceTransformer is None:
            try:
                os.environ["CUDA_VISIBLE_DEVICES"] = ""
                from sentence_transformers import SentenceTransformer as ST
                _SentenceTransformer = ST
                print("✅ SentenceTransformer imported (CPU-only mode)")
            except Exception as e:
                _embedder_load_error = e
                print(f"⚠️ SentenceTransformer import failed: {e}")
                return None

        try:
            kwargs = {"device": "cpu"}  # force CPU for embedder to avoid CUDA kernel image issues
            if EMBEDDER_LOCAL_ONLY and not EMBEDDER_ALLOW_DOWNLOAD:
                kwargs["local_files_only"] = True
            query_embedder = _SentenceTransformer(EMBEDDING_MODEL_ID, **kwargs)
            print("✅ Query embedder loaded (BAAI/bge-base-en-v1.5, 384-dim)")
        except TypeError as e:
            _embedder_load_error = e
            if EMBEDDER_ALLOW_DOWNLOAD:
                try:
                    query_embedder = _SentenceTransformer(EMBEDDING_MODEL_ID, device='cpu')
                    print("✅ Query embedder loaded (BAAI/bge-base-en-v1.5, 384-dim, CPU-only)")
                except Exception as inner:
                    _embedder_load_error = inner
                    query_embedder = None
                    print(f"⚠️ Query embedder not loaded: {inner}")
            else:
                query_embedder = None
                print(f"⚠️ Query embedder not loaded: {e}")
        except Exception as e:
            _embedder_load_error = e
            query_embedder = None
            print(f"⚠️ Query embedder not loaded: {e}")

        return query_embedder
    finally:
        apply_faithh_llm_cuda_env()

# Initialize ChromaDB WITHOUT embedding function (Gen 8 collection handles its own)
try:
    chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    
    # Get main collection without embedding function to avoid conflict
    collection = chroma_client.get_collection(name=CHROMA_COLLECTION)
    
    # Get ALIFE collection for experiment data
    try:
        alife_collection = chroma_client.get_collection(name="alife_lineage")
        alife_doc_count = alife_collection.count()
        print(f"✅ ALIFE collection 'alife_lineage': {alife_doc_count} documents")
    except Exception as e:
        alife_collection = None
        print(f"⚠️ ALIFE collection not available: {e}")
    
    CHROMA_CONNECTED = True
    doc_count = collection.count()
    print(f"✅ ChromaDB connected to {CHROMA_HOST}:{CHROMA_PORT}")
    print(f"✅ Collection '{CHROMA_COLLECTION}': {doc_count} documents")
except Exception as e:
    CHROMA_CONNECTED = False
    collection = None
    alife_collection = None
    chroma_client = None
    print(f"⚠️ ChromaDB not connected: {e}")

metrics_collection = None
if CHROMA_CONNECTED and chroma_client is not None:
    try:
        metrics_collection = chroma_client.get_or_create_collection(
            name=METRICS_COLLECTION_NAME,
            metadata={"description": "FAITHH session operational telemetry"},
        )
        print(f"✅ Session metrics collection '{METRICS_COLLECTION_NAME}' ready")
    except Exception as e:
        logger.warning("Session metrics collection unavailable: %s", e)
        metrics_collection = None

# Prometheus /metrics (prometheus_client) — separate registry from /api/metrics text exposition
_FAITHH_PROM_REGISTRY = CollectorRegistry()
faithh_http_requests_total = Counter(
    "faithh_http_requests_total",
    "Total HTTP requests handled by the FAITHH backend",
    ("method", "handler"),
    registry=_FAITHH_PROM_REGISTRY,
)
faithh_http_request_duration_seconds = Histogram(
    "faithh_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ("method", "handler"),
    registry=_FAITHH_PROM_REGISTRY,
)
faithh_chromadb_documents_sampled = Gauge(
    "faithh_chromadb_documents_sampled",
    "ChromaDB document count for the primary collection (refreshed every 5 minutes, not per request)",
    registry=_FAITHH_PROM_REGISTRY,
)

# Compatibility stub metrics for external Prometheus/Grafana wiring.
FAITHH_REQUEST_COUNT = Counter(
    "faithh_requests_total",
    "Total requests to FAITHH backend",
    ["endpoint"],
)
FAITHH_REQUEST_LATENCY = Histogram(
    "faithh_request_latency_seconds",
    "Request latency by endpoint",
    ["endpoint"],
)
FAITHH_CHROMA_DOCS = Gauge(
    "faithh_chroma_document_count",
    "Total documents in ChromaDB faithh_knowledge_base",
)


def _faithh_refresh_chroma_sample_loop():
    # Logic for Humans: Every few minutes, re-count Chroma documents in the background so Prometheus/Grafana gauges stay fresh without hammering count() on each HTTP request.
    """Background refresh for Chroma document gauge (avoids count() on every scrape)."""
    while True:
        try:
            if CHROMA_CONNECTED and collection is not None:
                docs = float(collection.count())
                faithh_chromadb_documents_sampled.set(docs)
                FAITHH_CHROMA_DOCS.set(docs)
        except Exception:
            pass
        time.sleep(300)


threading.Thread(
    target=_faithh_refresh_chroma_sample_loop, daemon=True, name="faithh-chroma-metrics"
).start()


@app.before_request
def _faithh_prometheus_before_request():
    # Logic for Humans: Start a per-request timer (except on metrics endpoints) so after_request can record latency histograms.
    if request.path in ("/metrics", "/api/metrics"):
        return
    g._faithh_prom_start = time.perf_counter()


@app.after_request
def _faithh_prometheus_after_request(response):
    # Logic for Humans: After each request, bump Prometheus counters/histograms with how long the handler took.
    if request.path in ("/metrics", "/api/metrics"):
        return response
    start = getattr(g, "_faithh_prom_start", None)
    if start is None:
        return response
    elapsed = time.perf_counter() - start
    handler = request.endpoint or "unknown"
    faithh_http_requests_total.labels(request.method, handler).inc()
    faithh_http_request_duration_seconds.labels(request.method, handler).observe(elapsed)
    FAITHH_REQUEST_COUNT.labels(handler).inc()
    FAITHH_REQUEST_LATENCY.labels(handler).observe(elapsed)
    # Proof-of-life: a successfully answered chat is this node's real work.
    if handler == "chat" and getattr(response, "status_code", 500) == 200:
        _note_query_served()
    return response


# ============================================================
# ML CHIP SYSTEM (semantic routing via centroids)
# ============================================================
ML_CHIPS = []
ML_CHIP_CENTROIDS = None  # numpy array of shape (N, 384)
ML_CHIP_IDS = []

def _load_ml_chips():
    # Logic for Humans: Read ml/output/consolidated_chips.json and build centroid vectors so we can match user text to “topic chips” by similarity.
    """Load consolidated ML chips and their centroids at startup."""
    global ML_CHIPS, ML_CHIP_CENTROIDS, ML_CHIP_IDS
    chips_path = BASE_DIR / 'ml' / 'output' / 'consolidated_chips.json'
    if not chips_path.exists():
        print("⚠️ ML chips not found at", chips_path)
        return

    try:
        with open(chips_path) as f:
            data = json.load(f)
        chips = data.get('chips', [])
        centroids = []
        ids = []
        for chip in chips:
            centroid = chip.get('centroid')
            if centroid and len(centroid) in (384, 768):
                centroids.append(centroid)
                ids.append(chip['id'])
        ML_CHIPS = chips
        ML_CHIP_IDS = ids
        ML_CHIP_CENTROIDS = np.array(centroids, dtype=np.float32)
        print(f"✅ ML chips loaded: {len(ML_CHIPS)} macro-chips, {ML_CHIP_CENTROIDS.shape} centroids")
    except Exception as e:
        print(f"⚠️ Failed to load ML chips: {e}")

_load_ml_chips()


def activate_ml_chips(query_text, top_k=5, threshold=0.15):
    # Logic for Humans: Embed the user’s question and find which precomputed “chips” (topic clusters) it is closest to, for routing hints or UI.
    """Compute cosine similarity between query and chip centroids.
    Returns list of (chip_id, score, chip_data) sorted by score descending.
    """
    if ML_CHIP_CENTROIDS is None or len(ML_CHIP_CENTROIDS) == 0:
        return []

    embedder = get_query_embedder()
    if not embedder:
        return []

    try:
        query_vec = embedder.encode([query_text])[0].astype(np.float32)
        # Cosine similarity: dot(a,b) / (|a| * |b|)
        norms = np.linalg.norm(ML_CHIP_CENTROIDS, axis=1) * np.linalg.norm(query_vec)
        norms = np.where(norms == 0, 1e-10, norms)
        similarities = ML_CHIP_CENTROIDS @ query_vec / norms

        # Build results above threshold
        results = []
        for i, score in enumerate(similarities):
            if score >= threshold:
                chip = ML_CHIPS[i] if i < len(ML_CHIPS) else {}
                results.append({
                    'id': ML_CHIP_IDS[i],
                    'label': chip.get('label', ML_CHIP_IDS[i]),
                    'score': round(float(score), 4),
                    'doc_count': chip.get('doc_count', 0),
                    'description': chip.get('description', ''),
                })
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    except Exception as e:
        print(f"⚠️ ML chip activation error: {e}")
        return []


RAG_TEMPORAL_WEIGHT = float(os.environ.get("RAG_TEMPORAL_WEIGHT", "0.15"))
RAG_TEMPORAL_HALFLIFE_DAYS = float(os.environ.get("RAG_TEMPORAL_HALFLIFE_DAYS", "30"))
RAG_SOURCE_BOOST = float(os.environ.get("RAG_SOURCE_BOOST", "0.20"))

def _apply_reranking(results, n_results):
    # Logic for Humans: Re-order Chroma hits so newer and “project doc” sources float up and noisy live-chat chunks sink, before we trim to top N.
    """Rerank RAG results by blending cosine similarity with recency and source-type boosts.

    Score = similarity * (1 - temporal_weight) + recency * temporal_weight + source_boost
    - recency decays exponentially with a configurable half-life
    - project_docs get a flat boost (RAG_SOURCE_BOOST) to prevent conversation noise
    """
    if not results or not results.get("documents") or not results["documents"][0]:
        return results

    docs = results["documents"][0]
    metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
    distances = results["distances"][0] if results.get("distances") else [0.5] * len(docs)
    ids = results["ids"][0] if results.get("ids") else [""] * len(docs)
    
    # Ensure all metas are dicts, never None
    metas = [meta if meta is not None else {} for meta in metas]

    now = datetime.now()
    decay = 0.693 / max(RAG_TEMPORAL_HALFLIFE_DAYS, 1)  # ln(2) / half-life

    scored = []
    for i, (doc, meta, dist, doc_id) in enumerate(zip(docs, metas, distances, ids)):
        similarity = max(0.0, 1.0 - dist)

        # Temporal boost
        recency = 0.5  # default
        if RAG_TEMPORAL_WEIGHT > 0:
            age_days = 180  # default: assume 6 months old if no timestamp
            ts = (meta or {}).get("timestamp") or (meta or {}).get("date") or (meta or {}).get("created_at", "")
            if ts:
                try:
                    dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00").split("+")[0])
                    age_days = max(0, (now - dt).total_seconds() / 86400)
                except (ValueError, TypeError):
                    pass
            recency = float(np.exp(-decay * age_days))

        # Source-type boost: project_docs are authoritative, conversation chunks are noisy
        source_boost = 0.0
        category = (meta or {}).get("category", "")
        source = (meta or {}).get("source", "")
        document_type = (meta or {}).get("document_type", "")
        if category == "project_docs" or source.startswith("project_docs:"):
            source_boost = RAG_SOURCE_BOOST
        elif category == "live_chat":
            source_boost = -0.15  # Penalize live_chat to prevent conversation noise
        elif document_type == "chat_export":
            source_boost = -0.20  # Penalize chat_export more aggressively

        blended = (similarity * (1 - RAG_TEMPORAL_WEIGHT) +
                   recency * RAG_TEMPORAL_WEIGHT +
                   source_boost)
        scored.append((blended, i, doc, meta, dist, doc_id))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:n_results]

    results["documents"] = [[s[2] for s in top]]
    results["metadatas"] = [[s[3] for s in top]]
    results["distances"] = [[s[4] for s in top]]
    results["ids"] = [[s[5] for s in top]]

    if 'metadatas' not in results or results['metadatas'] is None:
        results['metadatas'] = [[{}] * len(results['documents'][0])]

    return results


def query_collection(query_text, n_results=5, where=None):
    # Logic for Humans: Run the main knowledge-base Chroma query — embed the question, pull from “project docs” plus the full collection, merge, rerank, return snippets for the model.
    """Query collection with manual embedding, two-tier retrieval, and reranking.

    Two-tier strategy:
    1. Fetch from project_docs (authoritative, small pool)
    2. Fetch from full collection (broad recall)
    3. Merge and rerank with temporal + source-type boosting
    """
    if not CHROMA_CONNECTED or not collection:
        print("⚠️ Chroma not connected")
        return None
    embedder = get_query_embedder()
    if not embedder:
        print("⚠️ Query embedder unavailable - skipping RAG query")
        return None

    try:
        query_embedding = embedder.encode([query_text]).tolist()
        fetch_n = n_results * 4  # Extra pool for reranking

        # Tier 1: Query project_docs specifically (authoritative sources)
        # If a where-filter is provided, constrain tier-1 to that same scope
        # so project_docs boosting does not leak unrelated domains.
        project_docs_results = None
        project_docs_where = {"category": "project_docs"}
        if where:
            project_docs_where = {"$and": [{"category": "project_docs"}, where]}
        try:
            project_docs_results = collection.query(
                query_embeddings=query_embedding,
                n_results=min(fetch_n, 50),
                where=project_docs_where,
                include=["documents", "metadatas", "distances", "embeddings"]
            )
        except Exception:
            pass  # category filter may fail if no project_docs exist

        # Tier 2: Query full collection (broad recall)
        # Note: Don't filter by document_type here - many docs lack this field
        # and ChromaDB's $ne filter may exclude them. Reranking handles quality.
        if where:
            full_results = collection.query(
                query_embeddings=query_embedding,
                n_results=fetch_n,
                where=where,
                include=["documents", "metadatas", "distances", "embeddings"]
            )
        else:
            full_results = collection.query(
                query_embeddings=query_embedding,
                n_results=fetch_n,
                include=["documents", "metadatas", "distances", "embeddings"]
            )

        # Merge tier 1 + tier 2 (deduplicate by ID)
        merged = _merge_results(project_docs_results, full_results)

        return _apply_reranking(merged, n_results)
    except Exception as e:
        print(f"⚠️ Query failed: {e}")
        return None


def _merge_results(tier1, tier2):
    # Logic for Humans: Combine two Chroma result lists (e.g. “project docs” tier + “everything” tier) without duplicating the same document id.
    """Merge two ChromaDB result sets, deduplicating by document ID."""
    if not tier1 or not tier1.get("ids") or not tier1["ids"][0]:
        return tier2
    if not tier2 or not tier2.get("ids") or not tier2["ids"][0]:
        return tier1

    seen = set()
    merged = {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]], "embeddings": [[]]}

    for source in [tier1, tier2]:
        docs = source["documents"][0]
        metas = source["metadatas"][0] if source.get("metadatas") else [{}] * len(docs)
        dists = source["distances"][0] if source.get("distances") else [0.5] * len(docs)
        ids = source["ids"][0]
        embs = source["embeddings"][0] if source.get("embeddings") else [[]] * len(docs)
        
        # Ensure all metas are dicts, never None
        metas = [meta if meta is not None else {} for meta in metas]
        
        for doc, meta, dist, doc_id, emb in zip(docs, metas, dists, ids, embs):
            if doc_id not in seen:
                seen.add(doc_id)
                merged["documents"][0].append(doc)
                merged["metadatas"][0].append(meta)
                merged["distances"][0].append(dist)
                merged["ids"][0].append(doc_id)
                merged["embeddings"][0].append(emb)

    return merged


def query_alife_collection(query_text, n_results=5):
    # Logic for Humans: Search Chroma for artificial-life experiment text — either curated slices of the main KB, the dedicated lineage collection, or filtered experiment rows depending on the question wording.
    """Query ALIFE lineage collection for experiment data"""
    if not CHROMA_CONNECTED or not alife_collection:
        print("⚠️ ALIFE collection not available")
        return None
    
    embedder = get_query_embedder()
    if not embedder:
        print("⚠️ Query embedder unavailable - skipping ALIFE query")
        return None
    
    try:
        query_embedding = embedder.encode([query_text]).tolist()

        # Retrieval profile: prefer high-signal ALife docs in knowledge base
        # for conceptual/research questions, and keep lineage as fallback.
        lineage_keywords = [
            "lineage", "genome", "agent", "tick", "generation", "hex", "mutation"
        ]
        is_lineage_query = any(k in query_text.lower() for k in lineage_keywords)

        if not is_lineage_query:
            curated_results = None
            curated_sources = [
                "alife_experiment",
                "synthesis_document",
                "alife_cross_experiment_pattern",
                "governance_seed_link",
            ]

            for source_type in curated_sources:
                try:
                    source_results = collection.query(
                        query_embeddings=query_embedding,
                        n_results=max(n_results, 5),
                        where={
                            "$and": [
                                {"domain": {"$eq": "alife"}},
                                {"source_type": {"$eq": source_type}},
                            ]
                        },
                        include=["documents", "metadatas", "distances", "embeddings"],
                    )
                    curated_results = _merge_results(curated_results, source_results)
                except Exception as e:
                    print(f"   ⚠️ Curated ALife query failed for {source_type}: {e}")

            curated_results = _apply_reranking(curated_results, n_results)
            if (
                curated_results
                and curated_results.get("documents")
                and curated_results["documents"][0]
            ):
                print(
                    f"   🧬 ALIFE query (curated high-signal): "
                    f"{len(curated_results['documents'][0])} results"
                )
                return curated_results
        
        # For status/summary queries, use enhanced metadata filtering
        if any(keyword in query_text.lower() for keyword in ['status', 'bug', 'summary', 'results', 'harmonic', 'interference']):
            print(f"   📊 Status query - using enhanced metadata filtering...")
            
            # Build metadata filter based on query type
            where_clause = {"source_type": "alife_experiment", "experiment_id": 4}
            
            # Add document_type filter for precision
            query_lower = query_text.lower()
            if 'bug' in query_lower:
                # Prioritize bug fixes when bug is mentioned
                where_clause = {"source_type": "alife_experiment", "document_type": "bug_fix"}
            elif 'design' in query_lower or 'environment' in query_lower:
                where_clause = {"source_type": "alife_experiment", "document_type": "design"}
            elif 'red_queen' in query_lower or 'dynamics' in query_lower:
                where_clause = {"source_type": "alife_experiment", "document_type": "analysis"}
            else:
                # Default to summaries for status/results queries
                where_clause = {"source_type": "alife_experiment", "document_type": "summary"}
            
            try:
                main_results = collection.query(
                    query_embeddings=query_embedding,
                    n_results=n_results,
                    where=where_clause,
                    include=["documents", "metadatas", "distances", "embeddings"]
                )
            except Exception as e:
                print(f"   ⚠️ Metadata filter failed: {e}")
                print(f"   🔄 Falling back to source_type filter only...")
                main_results = collection.query(
                    query_embeddings=query_embedding,
                    n_results=n_results,
                    where={"source_type": "alife_experiment"},
                    include=["documents", "metadatas", "distances", "embeddings"]
                )
            if main_results['documents'][0]:
                print(f"   🧬 ALIFE query (main, filtered): {len(main_results['documents'][0])} results")
                return main_results
        
        # Otherwise, try ALIFE collection first
        alife_results = alife_collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=["documents", "metadatas", "distances", "embeddings"]
        )
        
        # If no results from ALIFE collection, try main collection
        if not alife_results['documents'][0]:
            print(f"   📭 No results in ALIFE collection, trying main collection...")
            main_results = collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                where={"source_type": "alife_experiment"},
                include=["documents", "metadatas", "distances", "embeddings"]
            )
            print(f"   🧬 ALIFE query (main): {len(main_results['documents'][0])} results")
            return main_results
        
        print(f"   🧬 ALIFE query (lineage): {len(alife_results['documents'][0])} results")
        return alife_results
        
    except Exception as e:
        print(f"❌ Error in ALIFE query: {e}")
        return None


def _ollama_post(url, payload, timeout):
    # Logic for Humans: POST JSON to Ollama with one quick retry on transient network errors.
    last_err = None
    for attempt in range(2):
        try:
            return requests.post(url, json=payload, timeout=timeout)
        except requests.RequestException as e:
            last_err = e
            time.sleep(0.25 * (attempt + 1))
    raise last_err

# Check for Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
GEMINI_AVAILABLE = bool(GEMINI_API_KEY)

# Track current model
CURRENT_MODEL = {"name": "unknown", "provider": "unknown", "last_response_time": 0}

# ============================================================
# SECTION 1: Conversation Memory Data Structures & Functions
# Add after: CURRENT_MODEL = {"name": "unknown", ...}
# ============================================================

conversation_sessions = {}
SESSION_TIMEOUT = int(os.environ.get("FAITHH_SESSION_TIMEOUT_SECONDS", "3600"))

def cleanup_old_sessions():
    # Logic for Humans: Drop in-memory chat sessions that have been idle too long and tell session-metrics they closed.
    """Remove sessions older than timeout"""
    now = datetime.now()
    to_remove = []
    for session_id, session in conversation_sessions.items():
        last_activity = datetime.fromisoformat(session["last_activity"])
        if (now - last_activity).total_seconds() > SESSION_TIMEOUT:
            to_remove.append(session_id)
    
    for session_id in to_remove:
        try:
            record_session_close(metrics_collection, session_id)
        except Exception as e:
            logger.warning("session metrics close on cleanup: %s", e)
        del conversation_sessions[session_id]
        print(f"🧹 Cleaned up session: {session_id}")

def get_or_create_session(session_id):
    # Logic for Humans: Find or mint a session id and keep a rolling history list for that chat tab.
    """Get existing session or create new one. Returns (session_id, created_new)."""
    created = False
    if not session_id:
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(3)}"
        created = True
    elif session_id not in conversation_sessions:
        created = True

    if session_id not in conversation_sessions:
        conversation_sessions[session_id] = {
            "started": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "history": []
        }
        print(f"🆕 Created session: {session_id}")
    else:
        conversation_sessions[session_id]["last_activity"] = datetime.now().isoformat()

    # Cleanup old sessions periodically
    if len(conversation_sessions) > 50:
        cleanup_old_sessions()

    return session_id, created

def add_to_conversation_history(session_id, user_msg, assistant_msg, intent=None):
    # Logic for Humans: Append this user/assistant turn to the session and cap how many turns we remember.
    """Add exchange to session history"""
    if session_id not in conversation_sessions:
        return
    
    conversation_sessions[session_id]["history"].append({
        "timestamp": datetime.now().isoformat(),
        "user": user_msg,
        "assistant": assistant_msg,
        "intent": intent or {}
    })
    
    # Keep only last 10 exchanges (configurable)
    if len(conversation_sessions[session_id]["history"]) > 10:
        conversation_sessions[session_id]["history"] = conversation_sessions[session_id]["history"][-10:]

def format_conversation_history(history, last_n=5):
    # Logic for Humans: Turn recent turns into a short text block the model can read as “what we just said.”
    """Format conversation history for context"""
    if not history:
        return None
    
    recent = history[-last_n:]
    formatted = []
    
    for exchange in recent:
        formatted.append(f"User: {exchange['user']}")
        # Truncate long responses but keep enough for context
        assistant_text = exchange['assistant']
        if len(assistant_text) > 500:
            assistant_text = assistant_text[:500] + "..."
        formatted.append(f"Assistant: {assistant_text}")
        formatted.append("")
    
    return "\n".join(formatted)

# ============================================================
# AUTO-INDEX QUEUE (Background thread for conversation indexing)
# ============================================================

index_queue = Queue()

def index_conversation_background(user_msg, assistant_msg, metadata):
    # Logic for Humans: Optionally write this chat turn into Chroma as a live_conversation document (with auto-tags) so future RAG can find it.
    """Thread-safe indexing function - runs in background with auto metadata tagging"""
    if not CHROMA_CONNECTED:
        return
    embedder = get_query_embedder()
    if not embedder:
        return

    try:
        timestamp = datetime.now()
        conv_id = f"live_conv_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}"

        conversation_text = f"User: {user_msg}\n\nAssistant: {assistant_msg}"

        # Generate base metadata
        meta = {
            "type": "live_conversation",
            "category": "live_chat",
            "timestamp": timestamp.isoformat(),
            "user_preview": user_msg[:100]
        }
        meta.update(metadata or {})

        # Apply auto metadata tagging
        try:
            from scripts.auto_metadata_tagger import MetadataTagger
            tagger = MetadataTagger()
            auto_metadata = tagger.generate_metadata(conversation_text)
            
            # Merge auto-generated metadata (auto-generated takes precedence)
            meta.update(auto_metadata)
            meta['auto_tagged'] = True
            meta['indexed_at'] = timestamp.isoformat()
            
            print(f"   🏷️ Auto-tagged: {auto_metadata.get('source_type', 'unknown')}")
        except Exception as tag_e:
            print(f"   ⚠️ Auto-tagging failed: {tag_e}")
            meta['auto_tagged'] = False

        # Generate embedding using BGE model (768-dim) to match collection
        embedding = embedder.encode([conversation_text]).tolist()

        collection.add(
            documents=[conversation_text],
            metadatas=[meta],
            ids=[conv_id],
            embeddings=embedding
        )
        print(f"📝 Indexed: {conv_id}")
    except Exception as e:
        print(f"❌ Index failed: {e}")

def process_index_queue():
    # Logic for Humans: Daemon loop that drains the index queue and calls index_conversation_background for each item.
    """Background worker thread - processes index requests"""
    while True:
        try:
            item = index_queue.get(timeout=1)
            if item is None:
                break
            index_conversation_background(**item)
            index_queue.task_done()
        except:
            continue

# Start background indexing thread
index_thread = threading.Thread(target=process_index_queue, daemon=True)
index_thread.start()
print("✅ Auto-index background thread started")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    # Logic for Humans: True if the uploaded filename’s extension is on the allow-list for /api/upload.
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============================================================
# PERSISTENT MEMORY & INTEGRATIONS
# (Implementations in backend/data_loaders.py)
# ============================================================

# ============================================================
# SMART QUERY ANALYSIS & INTEGRATION
# (detect_query_intent in backend/intent_detection.py)
# ============================================================


# detect_query_intent → backend/intent_detection.py


# get_self_awareness_context → backend/context_builders.py
# get_constella_awareness_context → backend/context_builders.py
# search_decisions_log → backend/context_builders.py


# get_project_state_context → backend/context_builders.py
# get_scaffolding_context → backend/context_builders.py


def smart_rag_query(query_text, n_results=10, where=None, intent=None):
    # Logic for Humans: Decide *which* Chroma strategy to use (self-query skips RAG, ALIFE vs governance vs constella vs dev chat vs broad search) then return ranked chunks.
    """
    Intelligent RAG query with integration support
    Now aware of query intent to boost relevant sources
    """
    try:
                
        if intent:
            print(f"   Intent: Self={intent['is_self_query']}, Why={intent['is_why_question']}, Next={intent['is_next_action_query']}, Constella={intent['is_constella_query']}, ALIFE={intent['is_alife_query']}", flush=True)
        
        # For self-queries, we don't need RAG - we have the answer
        if intent and intent['is_self_query']:
            print(f"   ⚡ Self-query detected - will use self_awareness directly")
            return None  # Signal to use self-awareness instead of RAG
        
        # For ALIFE queries, prioritize alife_lineage collection
        if intent and intent['is_alife_query'] and alife_collection:
            ql = query_text.lower()
            wants_kb_bridge = any(
                t in ql
                for t in (
                    "faithh",
                    " rag",
                    "rag ",
                    "rag performance",
                    "knowledge base",
                    "chromadb",
                    "embedding",
                    "retrieval",
                )
            )
            if wants_kb_bridge and CHROMA_CONNECTED and collection:
                try:
                    na = max(3, (n_results + 1) // 2)
                    nb = max(3, n_results - na + 2)
                    alife_part = query_alife_collection(query_text, n_results=na)
                    kb_part = query_collection(query_text, n_results=nb)
                    if (
                        alife_part
                        and alife_part.get("documents")
                        and alife_part["documents"][0]
                        and kb_part
                        and kb_part.get("documents")
                        and kb_part["documents"][0]
                    ):
                        merged_ab = _merge_results(alife_part, kb_part)
                        print(
                            f"   ✅ Blended alife_lineage + {CHROMA_COLLECTION} "
                            f"({len(merged_ab['documents'][0])} hits pre-rerank)"
                        )
                        return _apply_reranking(merged_ab, n_results)
                except Exception as e:
                    print(f"   ⚠️  ALIFE + knowledge-base blend failed: {e}")
            try:
                alife_results = query_alife_collection(
                    query_text,
                    n_results=n_results
                )
                if (alife_results['documents'] and 
                    alife_results['documents'][0] and
                    len(alife_results['documents'][0]) > 0):
                    print(f"   ✅ Using ALIFE lineage collection ({len(alife_results['documents'][0])} results)")
                    return alife_results
            except Exception as e:
                print(f"   ⚠️  ALIFE collection query failed: {e}")
        
        # CONSTITUTIONAL REASONING: Check for governance-related keywords
        governance_keywords = [
            'constitution', 'constitutional', 'governance', 'governing', 'ucf', 'penumbra',
            'civic tome', 'astris', 'auctor', 'token', 'floor', 'diversity floor',
            'principle', 'framework', 'charter', 'bylaws', 'rules', 'regulation',
            'gamer', 'minimum compliance', 'structural', 'mechanism', 'policy',
            'governance design', 'participation', 'civic', 'democratic', 'decision making'
        ]

        query_lower = query_text.lower()
        is_governance_query = any(keyword in query_lower for keyword in governance_keywords)

        # For Constella framework queries, prioritize master reference docs.
        # Governance-design questions should go through constitutional routing first.
        if intent and intent['is_constella_query'] and not is_governance_query:
            try:
                constella_results = query_collection(
                    query_text,
                    n_results=n_results,
                    where={"category": "constella_master"}
                )
                if (constella_results['documents'] and 
                    constella_results['documents'][0] and
                    len(constella_results['documents'][0]) > 0):
                    print(f"   ✅ Using Constella master docs ({len(constella_results['documents'][0])} results)")
                    return constella_results
            except Exception as e:
                print(f"   ⚠️  Constella master query failed: {e}")

        print(f"   🔍 Governance query detected: {is_governance_query}", flush=True)
                
        # For governance queries, prioritize constitutional principles
        if is_governance_query:
            try:
                constitutional_results = query_collection(
                    query_text,
                    n_results=n_results,
                    where={"domain": "constella_constitutional"}
                )
                if (constitutional_results['documents'] and 
                    constitutional_results['documents'][0] and
                    len(constitutional_results['documents'][0]) > 0):
                    print(f"   🏛️ Found {len(constitutional_results['documents'][0])} constitutional documents", flush=True)
                    
                    # Extract principle metadata for response
                    principle_metadata = []
                    if constitutional_results.get('metadatas') is not None:
                        print(f"   🏛️ Processing {len(constitutional_results['metadatas'][0])} metadata entries", flush=True)
                        for i, metadata in enumerate(constitutional_results['metadatas'][0]):
                            if metadata.get('document_type') == 'principle':
                                principle_metadata.append({
                                    'principle_id': metadata.get('principle_id'),
                                    'mechanism': metadata.get('mechanism'),
                                    'experiment_ids': metadata.get('experiment_ids', '').split(','),
                                    'confidence': metadata.get('confidence'),
                                    'title': metadata.get('title')
                                })
                                print(f"   🏛️ Added principle: {metadata.get('title')}", flush=True)
                    
                    print(f"   🏛️ Total principles extracted: {len(principle_metadata)}", flush=True)
                    
                    # Store metadata for response inclusion
                    constitutional_results['constitutional_principles'] = principle_metadata
                    return constitutional_results
            except Exception as e:
                print(f"   ⚠️ Constitutional query failed: {e}")
        
        # For governance queries that didn't find constitutional results, try general alife
        if is_governance_query:
            try:
                alife_results = query_alife_collection(
                    query_text,
                    n_results=n_results
                )
                if (alife_results['documents'] and 
                    alife_results['documents'][0] and
                    len(alife_results['documents'][0]) > 0):
                    print(f"   🧬 Using ALIFE lineage for governance context ({len(alife_results['documents'][0])} results)")
                    return alife_results
            except Exception as e:
                print(f"   ⚠️ ALIFE governance query failed: {e}")

            # Strict governance fallback: keep retrieval in high-signal domains only.
            try:
                governance_fallback_where = {
                    "$or": [
                        {"domain": {"$eq": "constella_constitutional"}},
                        {
                            "$and": [
                                {"domain": {"$eq": "alife"}},
                                {
                                    "$or": [
                                        {"source_type": {"$eq": "alife_experiment"}},
                                        {"source_type": {"$eq": "synthesis_document"}},
                                        {"source_type": {"$eq": "alife_cross_experiment_pattern"}},
                                    ]
                                },
                            ]
                        },
                    ]
                }
                governance_results = query_collection(
                    query_text,
                    n_results=n_results,
                    where=governance_fallback_where,
                )
                if (
                    governance_results
                    and governance_results.get("documents")
                    and governance_results["documents"][0]
                ):
                    print(
                        f"   🧭 Using strict governance fallback "
                        f"({len(governance_results['documents'][0])} results)"
                    )
                    return governance_results
            except Exception as e:
                print(f"   ⚠️ Governance strict fallback failed: {e}")

            # Do not fall through to broad/dev retrieval for governance queries.
            print("   🧭 Governance query: broad fallback disabled")
            return None
        
        # Keywords that indicate a development/technical query
        dev_keywords = ['discuss', 'talk', 'said', 'conversation', 'we', 'our',
                       'plan', 'setup', 'configure', 'implement', 'build', 
                       'create', 'did we', 'what was', 'how did', 'tell me about',
                       'what did', 'what were', 'talked about']
        
        query_lower = query_text.lower()
        is_dev_query = any(keyword in query_lower for keyword in dev_keywords)
        
        # For dev queries, prioritize conversation chunks
        if is_dev_query:
            try:
                conv_results = query_collection(
                    query_text,
                    n_results=n_results,
                    where={"category": "claude_conversation_chunk"}
                )
                
                if (conv_results['distances'] and 
                    conv_results['distances'][0] and 
                    len(conv_results['distances'][0]) > 0 and
                    conv_results['distances'][0][0] < 0.7):
                    print(f"   ✅ Using conversation chunks (best: {conv_results['distances'][0][0]:.3f})")
                    return conv_results
                else:
                    print(f"   ⚠️  Conversation chunks not good enough, trying mixed search")
            except Exception as e:
                print(f"   ⚠️  Conversation chunk query failed: {e}")
        
        # Fall back to broader search
        if where:
            print(f"   📚 Using backend's where clause")
            return query_collection(query_text, n_results=n_results, where=where)
        else:
            # Don't filter by category - many docs have category="unknown"
            # This includes business docs, recent documentation, etc.
            print(f"   📚 Using unfiltered search (includes all categories)")
            return query_collection(query_text, n_results=n_results)
        
    except Exception as e:
        print(f"❌ Error in smart RAG query: {e}")
        return query_collection(query_text, n_results=n_results)


# ============================================================
# SECTION 2: Individual Chip Retrieval Functions (Phase 2)
# ============================================================

def retrieve_conversation_history(session_id):
    # Logic for Humans: “Chip” — pull the last few turns for this session into a text block for the prompt.
    """Chip: Conversation History"""
    if not session_id or session_id not in conversation_sessions:
        return None, 'conversation_history'
    history = conversation_sessions[session_id]["history"]
    if not history:
        return None, 'conversation_history'
    history_text = format_conversation_history(history, last_n=5)
    if history_text:
        return f"\n[CTX:RECENT CONVERSATION]\n{history_text}\n[CTX_END]\n", 'conversation_history'
    return None, 'conversation_history'

def retrieve_self_awareness(intent):
    # Logic for Humans: “Chip” — if the user is asking about FAITHH itself, inject identity/memory context from JSON + builders.
    """Chip: Self-Awareness"""
    if not intent.get('is_self_query'):
        return None, 'self_awareness'
    context = get_self_awareness_context()
    return (context, 'self_awareness') if context else (None, 'self_awareness')

def retrieve_constella(intent):
    # Logic for Humans: “Chip” — if the question is about the Constella framework, add the framework awareness text.
    """Chip: Constella Framework"""
    if not intent.get('is_constella_query'):
        return None, 'constella'
    context = get_constella_awareness_context()
    return (context, 'constella') if context else (None, 'constella')

def retrieve_decisions(query_text, intent):
    # Logic for Humans: “Chip” — for “why did we…” questions, search the decisions log for matching rationale snippets.
    """Chip: Decision Log Search"""
    if not intent.get('is_why_question'):
        return None, 'decisions'
    context = search_decisions_log(query_text)
    return (context, 'decisions') if context else (None, 'decisions')

def retrieve_project_state(query_text, intent):
    # Logic for Humans: “Chip” — when the user asks what to work on or project status, inject structured project_states.json context (optionally scoped to one project name).
    """Chip: Project State"""
    if not (intent.get('is_next_action_query') or intent.get('is_project_query') or intent.get('is_business_query')):
        return None, 'project_state'
    # General project queries → all projects overview
    if intent.get('is_project_query'):
        context = get_project_state_context(None)
        return (context, 'project_state') if context else (None, 'project_state')
    # Specific project queries → single project detail
    project_name = None
    if 'faithh' in query_text.lower():
        project_name = 'faithh'
    elif 'constella' in query_text.lower():
        project_name = 'constella'
    elif intent.get('is_business_query'):
        project_name = 'tomcat_sound'
    context = get_project_state_context(project_name)
    return (context, 'project_state') if context else (None, 'project_state')

def retrieve_scaffolding(query_text, intent):
    # Logic for Humans: “Chip” — orientation / next-step questions get scaffolding_state + related structure hints.
    """Chip: Scaffolding"""
    if not (intent.get('needs_orientation') or intent.get('is_next_action_query')):
        return None, 'scaffolding'
    context = get_scaffolding_context(query_text)
    return (context, 'scaffolding') if context else (None, 'scaffolding')

def retrieve_project_structure():
    # Logic for Humans: “Chip” — snapshot of repo layout / recent git activity so the model grounds file paths in reality.
    """Chip: Live Project Structure Snapshot (always included)"""
    try:
        context = get_project_structure_snapshot()
        return (context, 'project_structure') if context else (None, 'project_structure')
    except Exception as e:
        print(f"   ⚠️ Project structure snapshot failed: {e}")
        return None, 'project_structure'


def update_last_rag_retrieval_signal(results) -> None:
    # Logic for Humans: Remember how “confident” the last retrieval was (best distance) so the UI/registry can show low-confidence warnings.
    """Track best Chroma distance from the last RAG query for workspace_registry + UI."""
    global LAST_RAG_RETRIEVAL_SIGNAL
    now = time.time()
    sig = {
        "ts": now,
        "ran": True,
        "hit_count": 0,
        "best_distance": None,
        "low_confidence": True,
        "no_hits": False,
        "error": None,
    }
    if results is None:
        sig["error"] = "query_failed"
        LAST_RAG_RETRIEVAL_SIGNAL = sig
        return
    docs = results.get("documents") if isinstance(results, dict) else None
    if not docs or not docs[0]:
        sig["no_hits"] = True
        LAST_RAG_RETRIEVAL_SIGNAL = sig
        return
    dists = results.get("distances")
    if dists and dists[0]:
        best = min(float(d) for d in dists[0] if d is not None)
        sig["best_distance"] = best
        sig["hit_count"] = len(docs[0])
        sig["low_confidence"] = best > RAG_MAX_DISTANCE_CONFIDENT
    else:
        sig["low_confidence"] = True
        sig["hit_count"] = len(docs[0])
    LAST_RAG_RETRIEVAL_SIGNAL = sig


_TOOL_INTENT_PULSE = re.compile(
    r"(system\s+health|system\s+vitals|pulse\b|vitals\b|reflection|staleness|divergence|branch\s+report|"
    r"memory\s+usage|physical\s+memory|\b(ram|cpu|disk)\b|service\s+health|ollama\b|chromadb\b|backend\s+health)",
    re.I,
)
_TOOL_INTENT_SENSORS = re.compile(r"\b(sensors?|impedance|genomic|biasing|organism)\b", re.I)


def _snapshot_pulse_status_internal() -> dict:
    # Logic for Humans: Build the same JSON the pulse status endpoint would return, for injecting into chat when the user asks about system health.
    """Same payload shape as GET /api/pulse/status (no HTTP)."""
    if not pulse_tracker:
        return {"error": "PULSE not available"}
    _patterns = getattr(pulse_tracker, "patterns", None) or {}
    return {
        "active_chips": len(pulse_tracker.get_active_personalized_chips()),
        "program_advances": len(pulse_tracker.get_program_advances()),
        "pending_proposals": len(pulse_tracker.get_pending_proposals()),
        "patterns_tracked": len(_patterns.get("chip_sequences", [])),
    }


def augment_context_for_tool_intents(message: str) -> tuple:
    # Logic for Humans: If the message smells like “how is the system / pulse / sensors”, prepend live JSON snapshots so the model answers from data, not guesses.
    """
    When the user asks about live system state, prepend compact JSON snapshots
    (pulse status + pulse state file; genomic analysis when enabled).
    Returns (prefix_string, label_list).
    """
    if not message or not isinstance(message, str):
        return "", []
    parts = []
    labels = []
    if _TOOL_INTENT_PULSE.search(message):
        snap = {
            "pulse_status": _snapshot_pulse_status_internal(),
            "pulse_state_file": None,
            "pulse_state_error": None,
        }
        try:
            if PULSE_STATE_FILE.exists():
                snap["pulse_state_file"] = json.loads(PULSE_STATE_FILE.read_text(encoding="utf-8"))
            else:
                snap["pulse_state_file"] = None
        except Exception as e:
            snap["pulse_state_error"] = str(e)
        block = json.dumps(snap, indent=2, default=str)[:12000]
        parts.append(
            "[CTX:LIVE SYSTEM DATA auto-attached]\n" + block
        )
        labels.append("pulse")
    if _TOOL_INTENT_SENSORS.search(message) and GENOMIC_ENABLED and genomic_impedance_sensor:
        try:
            analysis = genomic_impedance_sensor.analyze_genomic_sensors()
            gblock = {"source": "/api/genomic/analyze-sensors", "sensors_analysis": analysis}
            parts.append(
                "[CTX:GENOMIC SENSOR SNAPSHOT auto-attached]\n"
                + json.dumps(gblock, indent=2, default=str)[:12000]
            )
            labels.append("genomic_sensors")
        except Exception as e:
            parts.append(
                "[CTX:GENOMIC SENSOR SNAPSHOT auto-attached fetch failed]\n"
                + json.dumps({"error": str(e)}, indent=2)
            )
            labels.append("genomic_sensors_error")
    if not parts:
        return "", []
    return "\n\n".join(parts), labels


def _tier_tag(meta: dict) -> str:
    # Logic for Humans: Carry each retrieved fact's *attestation tier* (how well-backed it is)
    # and its receipt into the text the model reads — so a `confirmed` sandbox word and a
    # `speculative` note don't arrive looking identical. This is the evidence bridge's honesty
    # discipline, applied at the retrieval boundary. Absence of a tier is itself reported
    # ("unlabeled" = no receipt) rather than hidden.
    meta = meta or {}
    raw = (meta.get('tier') or meta.get('claim_label') or meta.get('attestation_tier')
           or meta.get('confidence') or '')
    tier = str(raw).strip().lower()
    # If the field holds a numeric confidence (0..1) rather than a tier word, bucket it.
    try:
        c = float(tier)
        tier = 'confirmed' if c >= 0.8 else 'asserted' if c >= 0.5 else 'speculative'
    except (ValueError, TypeError):
        pass
    known = {'confirmed', 'stable', 'asserted', 'contested', 'speculative', 'refuted'}
    if tier not in known:
        tier = 'unlabeled'
    # Receipt: what actually backs the claim (sandbox experiments, or the source doc).
    receipt = str(meta.get('experiment_ids') or meta.get('source')
                  or meta.get('source_type') or '').strip()[:60]
    return f"[tier: {tier}{(' | receipt: ' + receipt) if receipt else ''}]"


def retrieve_rag(query_text, intent, use_rag):
    # Logic for Humans: “Chip” — run smart_rag_query when allowed, attach a low-confidence warning if matches are weak, and return both a text block and structured hits for the UI/arbitration.
    """Chip: RAG Search (slowest - benefits most from parallelization)"""
    if is_ping_like_prompt(query_text):
        return None, [], 'rag_search'

    if not use_rag or not CHROMA_CONNECTED or intent.get('is_self_query'):
        return None, [], 'rag_search'

    # Recent changes queries should use git log (in structure chip), not RAG
    # RAG pulls old conversation fragments about planned changes and misleads the model
    if intent.get('is_recent_changes_query'):
        return None, [], 'rag_search'

    if intent.get('needs_orientation') and not intent.get('is_constella_query') and not intent.get('is_business_query') and not intent.get('is_alife_query'):
        return None, [], 'rag_search'

    try:
        results = smart_rag_query(query_text, n_results=5, intent=intent)
        update_last_rag_retrieval_signal(results)
        if results and results['documents'] and results['documents'][0]:
            sig = LAST_RAG_RETRIEVAL_SIGNAL or {}
            low = bool(sig.get("low_confidence"))
            warn = ""
            if low:
                warn = (
                    "\n⚠️ KNOWLEDGE BASE (LOW CONFIDENCE): Best match distance exceeds "
                    f"{RAG_MAX_DISTANCE_CONFIDENT}. Treat retrieved text as weak evidence; "
                    "do not invent API endpoints, paths, or system facts not present in the snippets.\n"
                )
            rag_context = warn + "\n[CTX:KNOWLEDGE BASE]\n"
            rag_context += (
                "Each item is tagged with its attestation tier — how well-backed the claim is. "
                "Weight higher tiers more heavily and prefer them when items conflict; cite the "
                "receipt when you rely on a confirmed/stable claim; never present a speculative or "
                "unlabeled item as settled fact.\n"
                "Tiers: confirmed/stable > asserted/contested > speculative > unlabeled (no receipt).\n\n"
            )
            rag_full_results = []  # Full results for coherence arbiter
            metas0 = (results.get('metadatas') and results['metadatas'][0]) or []

            for i, doc in enumerate(results['documents'][0][:3]):
                doc_text = doc if isinstance(doc, str) else (str(doc) if doc is not None else "")
                preview = (doc_text[:1000] + "...") if len(doc_text) > 1000 else doc_text
                meta_i = metas0[i] if i < len(metas0) and metas0[i] else {}
                rag_context += f"{i+1}. {_tier_tag(meta_i)} {preview}\n\n"
                # Build full result object for coherence arbiter
                try:
                    embedding = None
                    if results.get('embeddings') and results['embeddings'][0]:
                        emb = results['embeddings'][0][i]
                        if emb is not None:
                            if hasattr(emb, 'tolist'):
                                embedding = emb.tolist()
                            else:
                                embedding = list(emb)
                except Exception as emb_e:
                    print(f"   ⚠️ Embedding processing error: {emb_e}")
                    embedding = None
                
                full_result = {
                    'document': doc_text,
                    'content': doc_text,
                    'metadata': results['metadatas'][0][i] if results.get('metadatas') and results['metadatas'][0] else {},
                    'distance': results['distances'][0][i] if results.get('distances') and results['distances'][0] else 0.5,
                    'id': results['ids'][0][i] if results.get('ids') and results['ids'][0] else f"doc_{i}",
                    'embedding': embedding
                }
                rag_full_results.append(normalize_rag_hit_for_api(full_result))
            
            # Add constitutional principles to the first result if available
            if isinstance(results, dict) and results.get('constitutional_principles') and rag_full_results:
                rag_full_results[0]['constitutional_principles'] = results['constitutional_principles']
                
            rag_context += "[CTX_END]\n"
            return rag_context.strip(), rag_full_results, 'rag_search'
    except Exception as e:
        print(f"   ⚠️ RAG query failed: {e}")
        update_last_rag_retrieval_signal(None)
    return None, [], 'rag_search'

# ============================================================
# SECTION 3: Modified build_integrated_context (Phase 2 - Parallel)
# This REPLACES your existing build_integrated_context function
# ============================================================

def build_integrated_context(query_text, intent, use_rag=True, session_id=None):
    # Logic for Humans: Fan out all context “chips” in parallel (history, memory, RAG, projects, …), trim each to a token budget, and concatenate into one big system-side context string + metadata.
    """
    Build context from all available sources based on query intent
    NOW WITH PARALLEL CHIP RETRIEVAL! (Phase 2)
    """
    start_time = time.time()
    context_parts = []
    integrations_used = []
    rag_results = []

    # PRE-DETECT PROGRAM ADVANCES (Hybrid: trigger phrases + semantic)
    # This ensures PA combinations can actually trigger by forcing required chips
    pa_chips_needed = get_pa_chips_for_query(query_text)
    
    # Augment intent flags to force chip activation for PA
    if "scaffolding" in pa_chips_needed:
        intent["needs_orientation"] = True
    if "decisions" in pa_chips_needed:
        intent["is_why_question"] = True
    if "project_state" in pa_chips_needed:
        intent["is_project_query"] = True
    if "constella" in pa_chips_needed:
        intent["is_constella_query"] = True

    # Submit all chip retrievals in parallel
    futures = {}

    # Fast chips (file I/O)
    futures[CHIP_EXECUTOR.submit(retrieve_conversation_history, session_id)] = 'history'
    futures[CHIP_EXECUTOR.submit(retrieve_self_awareness, intent)] = 'self'
    futures[CHIP_EXECUTOR.submit(retrieve_constella, intent)] = 'constella'
    futures[CHIP_EXECUTOR.submit(retrieve_decisions, query_text, intent)] = 'decisions'
    futures[CHIP_EXECUTOR.submit(retrieve_project_state, query_text, intent)] = 'project'
    futures[CHIP_EXECUTOR.submit(retrieve_scaffolding, query_text, intent)] = 'scaffolding'
    futures[CHIP_EXECUTOR.submit(retrieve_project_structure)] = 'structure'

    # Slow chip (network I/O) - benefits most from parallelization
    futures[CHIP_EXECUTOR.submit(retrieve_rag, query_text, intent, use_rag)] = 'rag'

    # Collect results as they complete (with 10s timeout)
    chip_results = {}
    try:
        for future in as_completed(futures, timeout=10.0):
            chip_name = futures[future]
            try:
                result = future.result()
                chip_results[chip_name] = result
            except Exception as e:
                print(f"   ⚠️ Chip {chip_name} failed: {e}")
                chip_results[chip_name] = None
    except TimeoutError:
        print("   ⚠️ Chip retrieval timed out; continuing with partial context.")
    finally:
        for future, chip_name in futures.items():
            if chip_name not in chip_results:
                future.cancel()
                chip_results[chip_name] = None

    # Process results in priority order (for consistent output)
    priority_order = ['structure', 'history', 'self', 'constella', 'decisions', 'project', 'scaffolding', 'rag']
    
    constitutional_principles_cache = []

    for chip in priority_order:
        result = chip_results.get(chip)
        if result is None:
            continue

        # Get budget for this chip type
        chip_type_for_budget = chip if chip != 'self' else 'self_awareness'
        chip_type_for_budget = chip_type_for_budget if chip_type_for_budget != 'history' else 'conversation_history'
        max_tokens = CHIP_TOKEN_BUDGETS.get(chip_type_for_budget, 500)

        if chip == 'rag':
            context, rag_docs, chip_type = result
            # Extract constitutional principles from either legacy sentinel
            # strings or structured rag result dicts.
            for doc in list(rag_docs):
                if isinstance(doc, str) and doc.startswith('__CONSTITUTIONAL_PRINCIPLES__:'):
                    import json
                    constitutional_principles_cache = json.loads(doc[len('__CONSTITUTIONAL_PRINCIPLES__:'):])
                    rag_docs.remove(doc)
                elif isinstance(doc, dict) and doc.get('constitutional_principles'):
                    constitutional_principles_cache = doc['constitutional_principles']
            if context:
                context = truncate_to_budget(context, max_tokens)
                context_parts.append(context)
                rag_results = rag_docs
                integrations_used.append('rag_search')
                print(f"   ✅ Added RAG context ({len(rag_docs)} results, {count_tokens(context)} tokens)")
        else:
            context, chip_type = result
            if context:
                context = truncate_to_budget(context, max_tokens)
                context_parts.append(context)
                if chip_type:
                    integrations_used.append(chip_type)
                print(f"   ✅ Added {chip} context ({count_tokens(context)} tokens)")

    # RAG Fallback (only if RAG didn't fire)
    if use_rag and CHROMA_CONNECTED and 'rag_search' not in integrations_used:
        if not intent.get('needs_orientation') and not intent.get('is_recent_changes_query'):
            print("   🔄 RAG fallback - no specific chip triggered")
            try:
                fallback_results = query_collection(query_text, n_results=3)
                if fallback_results and fallback_results.get('documents') and fallback_results['documents'][0]:
                    rag_results = fallback_results['documents'][0]
                    integrations_used.append('rag_search_fallback')
                    print(f"   ✅ RAG fallback found {len(rag_results)} results")
                    rag_context = "\n[CTX:KNOWLEDGE BASE]\n"
                    for i, doc in enumerate(rag_results[:3]):
                        rag_context += f"{i+1}. {doc[:1000]}...\n\n"
                    rag_context += "[CTX_END]\n"
                    context_parts.append(rag_context.strip())
            except Exception as e:
                print(f"   ⚠️ RAG fallback error: {e}")

    # ENHANCED CONTEXT ASSEMBLY WITH PROGRAM ADVANCES
    # ============================================================
    
    # Detect Program Advances (Hybrid: trigger + semantic)
    advance_name, merge_strategy, detection_method = detect_program_advance_hybrid(
        query_text, active_chips=integrations_used
    )
    
    # Build chip contexts for enhanced merging
    chip_contexts = {}
    for chip in priority_order:
        result = chip_results.get(chip)
        if result is None:
            continue
        
        if chip == 'rag':
            context, rag_docs, chip_type = result
            if context:
                chip_contexts["rag_search"] = (context, chip_type)
        else:
            context, chip_type = result
            if context:
                chip_contexts[chip] = (context, chip_type)
    
    # For ALIFE queries, use only RAG context to avoid interference
    if intent and intent.get('is_alife_query') and 'rag_search' in chip_contexts:
        full_context = chip_contexts['rag_search'][0]  # Just the RAG context, no fusion
        method_used = "alife_rag_only"
        print(f"   🧬 ALIFE query - using RAG context only")
        # Debug: Show first 200 chars of RAG context
        print(f"   📄 RAG context preview: {full_context[:200]}...")
    elif advance_name:
        # Program Advance detected - use special merge
        full_context = apply_merge_strategy(chip_contexts, merge_strategy, query_text)
        method_used = f"program_advance_{advance_name}"
        print(f"   🎉 PROGRAM ADVANCE DETECTED: {advance_name} (via {detection_method})")
        print(f"   📋 Merge Strategy: {merge_strategy}")
    elif len(chip_contexts) > 1:
        # Multiple chips - use weighted RRF fusion
        full_context = weighted_rrf_fusion(chip_contexts, intent)
        method_used = "weighted_rrf_fusion"
        print(f"   🔀 Using weighted RRF fusion for {len(chip_contexts)} chips")
    else:
        # Single chip or no chips - use default
        full_context = "\n\n".join(context_parts) if context_parts else ""
        method_used = "default"

    elapsed = time.time() - start_time
    print(f"   ⏱️ Parallel chip retrieval: {elapsed:.3f}s")

    total_tokens = count_tokens(full_context)
    print(f"   📊 Total context: {total_tokens} tokens")
    print(f"   📋 Context method: {method_used}")

    # Coherence Arbiter - Phase 1: Measure convergence between RAG and chip signals
    coherence_metadata = None
    if COHERENCE_ARBITER_ENABLED and rag_results:
        try:
            # Get ML chip activations for convergence measurement
            ml_activated = activate_ml_chips(query_text, top_k=5, threshold=0.15)
            
            # Measure convergence
            if COHERENCE_ARBITER:
                coherence_metadata = COHERENCE_ARBITER.measure_convergence(
                    rag_results=rag_results,
                    chip_activations=ml_activated,
                    ml_chips=ML_CHIPS,
                    ml_chip_centroids=ML_CHIP_CENTROIDS
                )
            else:
                coherence_metadata = {"convergence_score": 0.0, "convergence_signals": ["disabled"]}
            
            print(f"   🧠 Coherence: {coherence_metadata['convergence_score']:.3f} "
                  f"(raw: {coherence_metadata['raw_convergence']:.3f}, "
                  f"weight: {coherence_metadata['signal_weight']:.3f})")
                  
        except Exception as e:
            logger.warning(f"Coherence arbiter failed: {e}")
            coherence_metadata = None

    # JSON-safe map for Phase 2 DB (which chip futures completed vs None)
    parallel_chip_summary = {k: v is not None for k, v in chip_results.items()}

    return (
        full_context,
        rag_results,
        integrations_used,
        advance_name,
        coherence_metadata,
        constitutional_principles_cache,
        parallel_chip_summary,
    )




# update_recent_topics → backend/context_builders.py
# format_memory_context → backend/context_builders.py
# get_faithh_personality → backend/context_builders.py

@app.route('/')
def index():
    """Serve the HTML UI"""
    return send_from_directory(BASE_DIR, 'faithh_pet_v4.html')

@app.route('/cockpit')
def cockpit():
    return send_from_directory(BASE_DIR, 'faithh_cockpit.html')

@app.route('/faithh_live_state.json')
def live_state():
    return send_from_directory(BASE_DIR, 'faithh_live_state.json')

@app.route('/images/<path:filename>')
def serve_image(filename):
    """Serve images for the UI"""
    images_dir = BASE_DIR / 'images'
    if not images_dir.exists():
        images_dir.mkdir(parents=True)
    return send_from_directory(images_dir, filename)

@app.route('/favicon.ico')
def favicon():
    """Serve site favicon."""
    return send_from_directory(BASE_DIR, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/manifest.json')
def pwa_manifest():
    """Serve PWA manifest."""
    return send_from_directory(BASE_DIR, 'manifest.json', mimetype='application/manifest+json')

@app.route('/sw.js')
def pwa_service_worker():
    """Serve PWA service worker (must be at root scope)."""
    return send_from_directory(BASE_DIR, 'sw.js', mimetype='application/javascript')

@app.route('/icons/<path:filename>')
def pwa_icons(filename):
    """Serve PWA icon files."""
    return send_from_directory(BASE_DIR / 'icons', filename)

@app.route('/api/models', methods=['GET'])
def list_models():
    # Logic for Humans: Probe Ollama / env for configured cloud models and return a unified list for the model picker UI.
    """List available models across all providers."""
    models = []
    # Ollama models
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        if r.ok:
            for m in r.json().get('models', []):
                models.append({'name': m['name'], 'provider': 'ollama', 'size': m.get('size', 0)})
    except Exception:
        pass
    # Groq models (from config)
    groq_key = os.environ.get('GROQ_API_KEY')
    if groq_key:
        for name in [
            'llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'openai/gpt-oss-120b'
        ]:
            models.append({'name': name, 'provider': 'groq'})
    # Anthropic models (use module-level key; already strip()d)
    if ANTHROPIC_API_KEY:
        for name in [
            'claude-3-haiku-20240307', 'claude-3-sonnet-20240229', 'claude-3-opus-20240229'
        ]:
            models.append({'name': name, 'provider': 'anthropic'})
    # Gemini
    gemini_key = os.environ.get('GEMINI_API_KEY')
    if gemini_key:
        models.append({'name': 'gemini-2.0-flash', 'provider': 'gemini'})
    return jsonify({'models': models, 'count': len(models)})


def _derive_chat_route_key(message: str, intent: dict) -> str:
    # Logic for Humans: Pick which YAML route name (“auto”, “code”, “reasoning”, …) should drive provider order for this chat turn.
    """Map chat intent/heuristics to llm_providers route keys."""
    if is_low_complexity_chat_message(message):
        return "auto"
    if intent.get("is_coding"):
        return "code"
    if intent.get("is_reasoning") or intent.get("is_complex_query"):
        return "reasoning"
    return choose_route(None, message)


@app.route('/api/chat', methods=['POST'])
# @require_security(security_middleware)  # Temporarily disabled
# @track_request_performance()     # Temporarily disabled
# @cached_response()               # Temporarily disabled
def chat():
    # Logic for Humans: Main chat API — parse JSON, detect intent, build integrated context (RAG + chips), call the LLM router (stream or buffer), update session/history/metrics, return reply + routing metadata.
    """Enhanced chat with smart integrations!"""
    global CURRENT_MODEL
    start_time = datetime.now()
    request_id = getattr(g, 'request_id', datetime.now().strftime("%Y%m%d_%H%M%S_%f"))

    def _log_chat_result(status, provider_used, model_used=None, detail=None):
        elapsed = (datetime.now() - start_time).total_seconds()
        detail_text = f" detail={detail}" if detail else ""
        print(
            f"📬 /api/chat {request_id} status={status} "
            f"provider={provider_used} model={model_used} elapsed={elapsed:.2f}s{detail_text}"
        )
    
    try:
        # Get request data directly (security middleware disabled)
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            _log_chat_result("error", "unknown", detail="invalid_json")
            return jsonify({
                'success': False,
                'error': 'Invalid JSON body (expected object)',
                'provider': 'unknown',
                'model_attempted': DEFAULT_MODEL,
                'request_id': request_id
            }), 400

        # ping_like_fastpath: skip only when no actual content provided
        _probe = (
            data.get('message')
            or data.get('prompt')
            or data.get('text')
            or data.get('query')
            or ''
        ) if isinstance(data, dict) else ''
        _probe = str(_probe)
        has_content = bool(_probe.strip())
        if not has_content or is_ping_like_prompt(_probe):
            return jsonify({
                "success": True,
                "request_id": request_id,
                "session_id": None,
                "conversation_depth": 0,
                "intent_detected": {
                    "is_business_query": False,
                    "is_constella_query": False,
                    "is_next_action_query": False,
                    "is_self_query": False,
                    "is_tangent": False,
                    "is_why_question": False,
                    "needs_orientation": False,
                    "patterns_matched": ["ping_like_fastpath"],
                },
                "integrations_used": [],
                "rag_used": False,
                "rag_results": [],
                "provider": "system",
                "model_used": "none",
                "response_time": 0.0,
                "response": "pong",
            })

        message = (
            data.get('message')
            or data.get('prompt')
            or data.get('text')
            or data.get('query')
            or ''
        )
        
        
        _cfg_ai = FAITHH_CONFIG_AI if isinstance(FAITHH_CONFIG_AI, dict) else {}
        _config_default_model = str(_cfg_ai.get("default_model") or "").strip()
        _grounded = os.environ.get(
            "OLLAMA_GROUNDED_MODEL", OLLAMA_DEFAULT_MODEL
        )
        _resolved_default_model = _config_default_model or _grounded or DEFAULT_MODEL
        _config_auto_route_enabled = bool(_cfg_ai.get("auto_route", True))
        if FAITHH_FORCE_LOCAL:
            _config_auto_route_enabled = False

        raw_model_field = data.get("model") or data.get("model_name")
        _rw = str(raw_model_field).strip() if raw_model_field is not None else ""
        client_wants_auto = (not _rw) or (_rw.lower() == "auto")
        auto_route = _config_auto_route_enabled and client_wants_auto
        if client_wants_auto and not _config_auto_route_enabled:
            raw_model_field = _resolved_default_model

        model = (
            str(raw_model_field).strip()
            if raw_model_field is not None and str(raw_model_field).strip()
            else _resolved_default_model
        )
        provider_override = data.get('provider') or data.get('model_provider')
        if FAITHH_FORCE_LOCAL:
            provider_override = None

        # Optional Ollama context window override (Modelfile default still applies if unset)
        ollama_num_ctx = None
        _nc_raw = data.get("ollama_num_ctx") if data.get("ollama_num_ctx") is not None else data.get("num_ctx")
        if _nc_raw is not None and str(_nc_raw).strip() != "":
            try:
                ollama_num_ctx = int(_nc_raw)
            except (TypeError, ValueError):
                ollama_num_ctx = None
        if ollama_num_ctx is not None and ollama_num_ctx <= 0:
            ollama_num_ctx = None

        # Smart provider inference from model name when no explicit provider given
        if FAITHH_FORCE_LOCAL:
            provider = "ollama"
            model = _resolved_default_model
            auto_route = False
        elif provider_override:
            provider = provider_override.lower()
        elif auto_route:
            provider = (MODEL_PROVIDER or "ollama").lower()
        elif ":" in model:
            # Ollama models always have ':' (e.g. llama31-grounded:latest)
            provider = "ollama"
        elif "/" in model:
            # Slash-based names are Groq cloud models (e.g. openai/gpt-oss-120b)
            provider = "groq"
        elif model in {'gemini-2.0-flash', 'gemini-2.0-flash-exp'}:
            provider = "gemini"
        else:
            # Bare names without ':' or '/' — check known Groq models
            _KNOWN_GROQ = {'llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'openai/gpt-oss-120b'}
            provider = "groq" if model in _KNOWN_GROQ else (MODEL_PROVIDER or "ollama").lower()

        # STEP 3: Intelligent provider selection
        available_providers = []
        if GROQ_API_KEY:
            available_providers.append("groq")
        if ANTHROPIC_API_KEY:
            available_providers.append("anthropic")
        if GEMINI_API_KEY:
            available_providers.append("gemini")
        available_providers.append("ollama")  # Always available as fallback
        
        # Use performance monitoring to select best provider
        if len(available_providers) > 1 and provider in available_providers:
            # Allow override but suggest optimal provider
            optimal_provider = get_optimal_provider(available_providers)
            if optimal_provider and optimal_provider != provider:
                print(f"   💡 Performance suggestion: {optimal_provider} (better than {provider})")
                # For now, keep user choice but log suggestion
                # TODO: Make this configurable - auto-switch vs suggestion only
        elif not provider or provider not in available_providers:
            # Auto-select best provider if none specified or invalid
            if not FAITHH_FORCE_LOCAL:
                provider = get_optimal_provider(available_providers) or "ollama"
                print(f"   🎯 Auto-selected provider: {provider} (based on performance)")
            else:
                provider = "ollama"
        
        if provider not in {"ollama", "groq", "gemini", "anthropic"}:
            provider = "ollama"

        # If provider is ollama but model doesn't look like an Ollama model, use default
        if (not auto_route) and provider == "ollama" and ":" not in model:
            model = OLLAMA_DEFAULT_MODEL

        if not message:
            _log_chat_result("error", provider, detail="missing_message")
            return jsonify({
                'success': False,
                'error': 'Missing message/prompt',
                'provider': provider,
                'model_attempted': model,
                'request_id': request_id
            }), 400

        use_rag = data.get('use_rag', data.get('useRag', True))
        session_id = data.get('session_id') or data.get('sessionId')
        session_id, session_created = get_or_create_session(session_id)
        if session_created:
            _faithh_record_session_metrics_open(session_id)

        origin = request.headers.get("Origin") or request.headers.get("Referer") or ""
        user_agent = request.headers.get("User-Agent", "")
        source = "ui" if origin or "Mozilla" in user_agent else "api"
        print(
            f"🧭 /api/chat {request_id} source={source} provider={provider} "
            f"model={model} keys={sorted(data.keys())}"
        )
        
        chat_routing_debug: dict = {}
        chat_perf: dict = {}
        chat_perf["wall_t0"] = time.perf_counter()
        chat_perf["request_source"] = source

        # STEP 1: Detect query intent
        intent = detect_query_intent(message)
        chat_routing_debug["low_complexity_chitchat"] = is_low_complexity_chat_message(message)
        chat_routing_debug["faithh_force_local"] = FAITHH_FORCE_LOCAL
        chat_routing_debug["config_auto_route"] = _config_auto_route_enabled

        # STEP 1.5: Smart auto model + provider (same logic as backend.llm_providers.get_optimal_model_for_query)
        if auto_route:
            opt_p, opt_m = get_optimal_model_for_query(message, intent, None)
            if opt_p == "gemini" and not GEMINI_AVAILABLE:
                opt_p = "ollama"
                opt_m = os.environ.get(
                    "OLLAMA_GROUNDED_MODEL", "qwen25-grounded-gen5-delta:latest"
                )
            provider, model = opt_p, opt_m
            chat_routing_debug.update(
                {
                    "auto_route": True,
                    "selector": "get_optimal_model_for_query",
                    "selected_provider": provider,
                    "selected_model": model,
                }
            )
            print(
                f"🤖 Smart auto-route: provider={provider} model={model}",
                flush=True,
            )
        else:
            print(f"✅ Model explicitly specified: {model} ({provider})", flush=True)

        if ollama_num_ctx:
            chat_routing_debug["ollama_num_ctx"] = ollama_num_ctx
        
        print(f"\n{'='*60}")
        print(f"📨 Query: {message[:80]}...")
        print(f"💬 Session: {session_id}")
        print(f"🎯 Intent Analysis:")
        for key, value in intent.items():
            if key != 'patterns_matched' and value:
                print(f"   {key}: {value}")
        if intent['patterns_matched']:
            print(f"   Patterns: {', '.join(intent['patterns_matched'])}")
        print(f"🤖 Model Selected: {model} ({provider})")
        
        system_data_labels: list = []

        # STEP 2: Build integrated context from all sources
        # Use legacy context builder with Phase 2 performance tracking
        chat_perf["pipe_t0"] = time.perf_counter()
        (
            context,
            rag_results,
            integrations_used,
            advance_name,
            coherence_metadata,
            constitutional_principles_cache,
            parallel_chip_summary,
        ) = build_integrated_context(message, intent, use_rag, session_id)
        chat_perf["t_rag_end"] = time.perf_counter()

        tool_block, tool_labels = augment_context_for_tool_intents(message)
        if tool_block:
            context = tool_block + "\n\n" + context
            system_data_labels.extend(tool_labels)

        wr_hint = data.get("workspace_registry")
        if isinstance(wr_hint, dict) and wr_hint:
            try:
                _wr_raw = json.dumps(wr_hint, separators=(",", ":"), default=str)
                chat_perf["workspace_registry_json_bytes"] = len(_wr_raw)
            except (TypeError, ValueError):
                chat_perf["workspace_registry_json_bytes"] = -1
            chat_perf["lean_workspace_registry"] = bool(
                data.get("lean_workspace_registry") or wr_hint.get("_lean")
            )
            try:
                wr_budget = 1200 if chat_perf.get("lean_workspace_registry") else 4000
                wr_compact = json.dumps(wr_hint, separators=(",", ":"), default=str)[:wr_budget]
                context = (
                    "[Workspace capabilities (from client registry snapshot; tools available now)]\n"
                    + wr_compact
                    + "\n\n"
                    + context
                )
            except (TypeError, ValueError):
                pass
        
        # ENHANCEMENT: Apply Constella context enhancement
        try:
            enhanced_context = get_constella_enhanced_context(message, context)
            context = enhanced_context
            print(f"🧠 Constella context enhancement applied")
        except Exception as e:
            print(f"⚠️  Constella context enhancement failed: {e}")
        
        # Add Phase 2 performance tracking after context is built
        try:
            if PHASE2_ENABLED:
                # Create performance record for tracking
                query_id = session_id or f"query_{int(datetime.now().timestamp() * 1000)}"
                
                # Calculate context metrics
                context_tokens = len(context) // 4  # Rough estimate
                assembly_time = 0.1  # Placeholder for context assembly time
                
                # Create performance record
                query_id = f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
                
                perf_record = QueryPerformance(
                    query_id=query_id,
                    timestamp=datetime.now(),
                    intent=intent,
                    weights_used=get_chip_weights(integrations_used),
                    chip_results=parallel_chip_summary,
                    response_time=0.0,  # Will be updated after response
                    model_used=model,
                    provider_used=provider,
                    accuracy_score=None,  # Will be updated based on user feedback
                    user_feedback=None,
                    context_tokens=len(context) if context else 0,
                    # Add Program Advance metrics
                    program_advance_used=advance_name,
                    integrations_used=integrations_used,
                    coherence_score=coherence_metadata.get('convergence_score') if coherence_metadata else None,
                    success=True,
                    error_info=None
                )

                # Feed metrics to advanced analytics system
                if advance_name:
                    advanced_analytics.add_metric(
                        f"program_advance_{advance_name}",
                        1.0,  # Success metric
                        {
                            'query_length': len(message),
                            'chip_count': len(integrations_used),
                            'intent_type': intent.get('type', 'unknown'),
                            'coherence_score': coherence_metadata.get('convergence_score') if coherence_metadata else None
                        }
                    )

                # Feed chip usage metrics
                for chip in integrations_used:
                    advanced_analytics.add_metric(
                        f"chip_usage_{chip}",
                        1.0,
                        {
                            'program_advance': advance_name,
                            'query_length': len(message),
                            'intent_type': intent.get('type', 'unknown')
                        }
                    )

                # Feed response time metrics (will be updated later)
                advanced_analytics.add_metric(
                    "query_processing_time",
                    0.0,  # Will be updated with actual time
                    {
                        'program_advance': advance_name,
                        'chip_count': len(integrations_used),
                        'model_used': model
                    }
                )

                # Track the performance
                performance_tracker.track_query(perf_record)
                
                # Ensure coherence_metadata is a dict before assigning to it
                if coherence_metadata is None:
                    coherence_metadata = {}
                
                # Add Phase 2 info to coherence metadata
                coherence_metadata['phase2_optimization'] = {
                    'performance_tracked': True,
                    'query_id': query_id,
                    'method': 'legacy_with_tracking',
                    'chips_used': len(integrations_used),
                    'context_tokens': context_tokens
                }
                
                print(f"📊 Phase 2 Performance tracked: {query_id}")
                print(f"🤖 Context built with {len(integrations_used)} chips")
                
        except Exception as e:
            print(f"⚠️ Phase 2 performance tracking failed: {e}")
            # Ensure coherence_metadata is a dict before assigning to it
            if coherence_metadata is None:
                coherence_metadata = {}
            coherence_metadata['phase2_optimization'] = {
                'performance_tracked': False,
                'error': str(e)
            }
        
        has_rag_context = "rag_search" in integrations_used or "rag_search_fallback" in integrations_used
        if has_rag_context and context:
            sig_lc_guard = LAST_RAG_RETRIEVAL_SIGNAL or {}
            ts_g = sig_lc_guard.get("ts")
            age_g = None
            if isinstance(ts_g, (int, float)):
                age_g = max(0.0, time.time() - float(ts_g))
            stale_g = age_g is None or age_g > RAG_SIGNAL_STALE_SECONDS or not sig_lc_guard.get("ran")
            if sig_lc_guard.get("ran") and not stale_g and bool(sig_lc_guard.get("low_confidence")):
                context = (
                    "[RAG SIGNAL WEAK — retrieved context may not be relevant. "
                    "If you cannot find the answer in the context provided, "
                    "say so directly. Do NOT invent API endpoints, file paths, "
                    "or system states that are not explicitly in the context.]\n\n"
                    + context
                )

        # STEP 3: Build final prompt
        # Select personality based on provider
        if provider == "anthropic" or (provider == "groq" and "claude" in model.lower()):
            personality = get_claude_personality()
            print(f"🎭 Using Claude-optimized personality for {provider}/{model}")
        else:
            personality = get_faithh_personality()
            print(f"🎭 Using FAITHH personality for {provider}/{model}")
        
        if has_rag_context and context:
            # Use RAG-grounded prompt when context includes RAG results
            if provider == "anthropic" or (provider == "groq" and "claude" in model.lower()):
                # Claude-optimized RAG personality
                rag_personality = """You are Claude, an AI assistant integrated into FAITHH, Jonathan's personal knowledge system.

You have access to retrieved context from the knowledge base shown below. Use this context to answer the question thoroughly. Provide comprehensive, detailed responses that fully utilize the retrieved information.

## Context utilization
- Use the retrieved context extensively to provide complete answers
- Cite specific details from the context when relevant
- Build upon the context to provide comprehensive insights
- If context is insufficient, explain what additional information would be helpful
- Don't say "According to the context..." — integrate the information naturally

## Communication style
- Provide thorough, well-reasoned responses
- Explain your reasoning process when helpful
- Elaborate on complex topics with detailed explanations
- Be natural and conversational while maintaining accuracy
- Give comprehensive coverage of topics within your knowledge
- Do not paste or repeat [CTX:...] blocks from context."""
            else:
                # Original FAITHH RAG personality
                rag_personality = """You are FAITHH (Friendly AI Teaching & Helping Hub), Jonathan's personal AI assistant.

You have access to retrieved context from the knowledge base shown below. Use this context to answer the question. Cite specific details from the context. If the context is insufficient, say so clearly.

## Accuracy rules (read first)
These rules override ALL other instructions. Violating them produces harmful misinformation.

1. USE RETRIEVED CONTEXT: When RAG context is provided, it contains relevant information from your knowledge base. Use this context to answer accurately.
2. CITE SPECIFIC DETAILS: Reference specific information from the retrieved context.
3. BE HONEST ABOUT LIMITATIONS: If the context doesn't contain the answer, say so clearly.
4. ACCURACY > COMPLETENESS: A short, accurate answer based on context is better than fabricating information.

## Communication style
✅ DO:
- Use the retrieved context to answer questions
- Cite specific details from the context
- Be honest about what the context contains and doesn't contain
- Integrate context naturally without saying "According to the context..."

❌ DON'T:
- Ignore the retrieved context
- Make up information not in the context
- Say "I don't have information" when context is provided
- Paste or repeat [CTX:...] delimiter lines or lines of equals signs from context"""
            
            full_prompt = f"{rag_personality}\n\n{context}\n\nUser: {message}"
        elif context:
            # Use regular personality for non-RAG context
            full_prompt = f"{personality}\n\n{context}\n\nUser: {message}"
        else:
            full_prompt = f"{personality}\n\nUser: {message}"

        # --- RAG PRE-FLIGHT HOOK (/api/chat) ---
        # rag_results from build_integrated_context is a list of normalized hits (distance per item)
        # or empty; dict-shaped Chroma payloads are handled for compatibility.
        _preflight_failed = False
        _best_distance = 0.0
        _rag_hit_count = 0
        if use_rag:
            _rag_distances = []
            if isinstance(rag_results, dict):
                _row = (rag_results.get("distances") or [[]])[0] or []
                for x in _row:
                    if x is not None:
                        try:
                            _rag_distances.append(float(x))
                        except (TypeError, ValueError):
                            pass
                _docs0 = (rag_results.get("documents") or [[]])[0] or []
                _rag_hit_count = len(_docs0)
            elif isinstance(rag_results, list):
                _rag_hit_count = len(rag_results)
                for h in rag_results:
                    if isinstance(h, dict):
                        d = h.get("distance")
                        if d is not None:
                            try:
                                _rag_distances.append(float(d))
                            except (TypeError, ValueError):
                                pass
            else:
                _rag_hit_count = 0
            _best_distance = min(_rag_distances) if _rag_distances else 1.0
            _preflight_failed = _best_distance > 0.60 or _rag_hit_count < 2
            if _preflight_failed:
                full_prompt += (
                    "\n\n[SYSTEM HAZARD: RAG CONFIDENCE LOW "
                    f"(best_distance={_best_distance:.3f}, hits={_rag_hit_count})] "
                    "The knowledge base has insufficient or low-relevance data for this query. "
                    "DO NOT fabricate API endpoints, file paths, or system states. "
                    "If you cannot find the answer in the context provided, say so directly."
                )
        # --- END PRE-FLIGHT HOOK ---
        
        print(f"📝 Context built: {len(context)} chars")
        print(f"{'='*60}\n")

        # Shared route config for Ollama/Groq/local_webui (non–Anthropic/Gemini paths + SSE)
        route_key_rl = _derive_chat_route_key(message, intent)
        raw_model_field_rl = data.get("model") or data.get("model_name")
        explicit_model_choice_rl = bool(raw_model_field_rl) and str(raw_model_field_rl).strip().lower() not in (
            "auto",
        )
        provider_preference_rl = provider if explicit_model_choice_rl else "auto"
        if provider_preference_rl not in ("auto", "groq", "ollama", "local_webui"):
            provider_preference_rl = "auto"
        chat_route_cfg = copy.deepcopy(FAITHH_MODEL_CONFIG)
        if FAITHH_FORCE_LOCAL:
            _rts = chat_route_cfg.setdefault("routes", {})
            for _rk in list(_rts.keys()):
                _rts[_rk] = ["ollama"]
        provs_rl = chat_route_cfg.get("providers") or {}
        if isinstance(provs_rl.get("ollama"), dict):
            oc = dict(provs_rl["ollama"])
            oc["base_url"] = OLLAMA_HOST.rstrip("/")
            if route_key_rl == "reasoning":
                oc["model"] = OLLAMA_REASONING_MODEL
            elif ":" in str(model) or provider == "ollama":
                oc["model"] = model
            if ollama_num_ctx:
                oc["num_ctx"] = ollama_num_ctx
            provs_rl["ollama"] = oc
        if isinstance(provs_rl.get("groq"), dict) and provider == "groq":
            gc = dict(provs_rl["groq"])
            gc["model"] = data.get("groq_model") or model
            provs_rl["groq"] = gc
        chat_route_cfg["providers"] = provs_rl
        messages_llm = [{"role": "user", "content": full_prompt}]

        _stream_raw = data.get("stream")
        if _stream_raw is None:
            _stream_raw = data.get("sse") or data.get("use_sse")
        want_stream = _stream_raw in (True, 1, "1", "true", "True", "yes", "on")
        _gemini_path = provider == "gemini" or (
            provider == "ollama" and GEMINI_AVAILABLE and "gemini" in model.lower()
        )
        if want_stream and (provider == "anthropic" or _gemini_path):
            want_stream = False

        def _finalize_response(assistant_response, model_used, provider_used, streamed_final=False):
            assistant_response = normalize_assistant_text(assistant_response)
            model_used = str(model_used or "").strip() or str(DEFAULT_MODEL)
            provider_used = str(provider_used or "unknown")
            chat_perf["t_llm_end"] = time.perf_counter()

            # ENHANCEMENT: Apply Constella AI integration
            try:
                enhanced_response = enhance_response_with_constella(message, assistant_response)
                assistant_response = normalize_assistant_text(enhanced_response)
                print(f"🧠 Constella enhancement applied to response")
            except Exception as e:
                print(f"⚠️  Constella enhancement failed: {e}")
            
            CURRENT_MODEL.update({
                "name": model_used,
                "provider": provider_used,
                "last_response_time": (datetime.now() - start_time).total_seconds()
            })

            # PHASE 1: Add to conversation history BEFORE returning
            add_to_conversation_history(session_id, message, assistant_response, intent)

            # Index conversation — quality gate prevents bad responses entering KB
            _resp_clean = assistant_response.strip()
            _index_eligible = (
                len(_resp_clean) > 150
                and "===" not in _resp_clean
                and "[CTX:" not in _resp_clean
                and not _resp_clean.startswith("When I ask")
                and not _resp_clean.startswith("System data")
                and not _resp_clean.startswith("This is important")
            )

            if CHROMA_CONNECTED and _index_eligible:
                index_queue.put({
                    'user_msg': message,
                    'assistant_msg': assistant_response,
                    'metadata': {
                        'model': model_used,
                        'provider': provider_used,
                        'rag_used': bool(rag_results),
                        'intent_summary': ','.join(intent.get('patterns_matched', [])),
                        'session_id': session_id
                    }
                })
            elif CHROMA_CONNECTED:
                print(f"⚠️ Skipping indexing — response failed quality gate (len={len(_resp_clean)})")

            # ML chip activation (semantic routing)
            ml_activated = activate_ml_chips(message, top_k=5, threshold=0.15)

            # Optimize rag_results for response (exclude embeddings to reduce size)
            optimized_rag_results = []
            if rag_results:
                for result in rag_results:
                    if isinstance(result, dict) and 'embedding' in result:
                        optimized_result = result.copy()
                        del optimized_result['embedding']
                        optimized_rag_results.append(normalize_rag_hit_for_api(optimized_result))
                    else:
                        optimized_rag_results.append(normalize_rag_hit_for_api(result))

            response_data = {
                'success': True,
                'request_id': request_id,
                'response': assistant_response,
                'model_used': CURRENT_MODEL['name'],
                'provider': CURRENT_MODEL['provider'],
                'response_time': CURRENT_MODEL['last_response_time'],
                'rag_used': bool(rag_results),
                'rag_results': optimized_rag_results,
                'intent_detected': intent,
                'session_id': session_id,
                'conversation_depth': len(conversation_sessions.get(session_id, {}).get('history', [])),
                'integrations_used': integrations_used,
                'ml_chips_activated': ml_activated
            }

            sig_lc = LAST_RAG_RETRIEVAL_SIGNAL or {}
            ts_lc = sig_lc.get("ts")
            age_sec = None
            if isinstance(ts_lc, (int, float)):
                age_sec = max(0.0, time.time() - float(ts_lc))
            rag_relevance = None
            if sig_lc.get("ran") and age_sec is not None and age_sec <= RAG_SIGNAL_STALE_SECONDS:
                rag_relevance = {
                    "low_confidence": bool(sig_lc.get("low_confidence")),
                    "best_distance": sig_lc.get("best_distance"),
                    "threshold": RAG_MAX_DISTANCE_CONFIDENT,
                    "signal_age_seconds": round(age_sec, 2),
                }
            response_data["rag_relevance"] = rag_relevance

            response_data["preflight_failed"] = _preflight_failed
            response_data["best_distance"] = round(_best_distance, 4)
            response_data["rag_hits"] = _rag_hit_count

            if system_data_labels:
                response_data["system_data_attached"] = list(system_data_labels)

            if provider_used.lower() == "ollama":
                try:
                    gh = build_gpu_hint_payload()
                    chat_routing_debug["ollama_gpu_pin"] = {
                        "physical_pci_index": gh.get("faithh_cuda_physical_device"),
                        "cuda_visible_devices": gh.get("cuda_visible_devices"),
                        "alignment": gh.get("alignment"),
                        "ui_primary_gpu": gh.get("ui_primary_gpu"),
                    }
                except Exception:
                    pass

            if chat_routing_debug:
                response_data["routing_debug"] = dict(chat_routing_debug)

            # Add Coherence Arbiter metadata if available
            if coherence_metadata:
                response_data["coherence"] = coherence_metadata

            # Add Program Advance metadata if detected
            if advance_name:
                response_data["program_advance"] = {
                    'name': advance_name,
                    'description': PROGRAM_ADVANCES[advance_name]['description'],
                    'chips_combined': PROGRAM_ADVANCES[advance_name]['chips'],
                    'merge_strategy': PROGRAM_ADVANCES[advance_name]['merge_strategy']
                }

            # CONSTITUTIONAL REASONING: Add constitutional principles if retrieved
            constitutional_principles = constitutional_principles_cache
            
            if constitutional_principles:
                response_data["constitutional_reasoning"] = {
                    'principles_retrieved': len(constitutional_principles),
                    'principles': constitutional_principles,
                    'mechanisms': list(set(p['mechanism'] for p in constitutional_principles if p.get('mechanism'))),
                    'supporting_experiments': list(set(exp_id for p in constitutional_principles if p.get('experiment_ids') for exp_id in p['experiment_ids']))
                }
                print(f"🏛️ Constitutional Reasoning: {len(constitutional_principles)} principles, mechanisms: {response_data['constitutional_reasoning']['mechanisms']}")

            try:
                if pulse_tracker:
                    proposals = pulse_tracker.record_interaction(
                        query=message,
                        chips_used=integrations_used,
                        timestamp=datetime.now()
                    )

                    if proposals.get("pa_candidates"):
                        for pa in proposals["pa_candidates"]:
                            if pa["combination"] == ["decisions", "scaffolding"]:
                                pulse_tracker.unlock_program_advance(
                                    combination=pa["combination"],
                                    name="Project Historian"
                                )
                                response_data["pa_unlocked"] = {
                                    "name": "Project Historian",
                                    "message": "🎉 Program Advance Unlocked! By combining Decisions + Scaffolding, you've unlocked Project Historian - I can now generate project evolution narratives!"
                                }
            except Exception as e:
                print(f"PULSE tracking error: {e}")

            # Cache the response for future use (include num_ctx in key when set)
            _cm = f"{model_used}#ctx={ollama_num_ctx}" if ollama_num_ctx else model_used
            cache_response(message, provider_used, _cm, response_data)

            _flush_chat_perf_metrics(
                message=message,
                request_id=request_id,
                chat_perf=chat_perf,
                provider=provider_used,
                model=model_used,
                cached=False,
                streamed=streamed_final,
            )

            try:
                bump_from_chat_response(
                    session_id,
                    response_data,
                    streamed=streamed_final,
                    routing_debug=chat_routing_debug,
                )
            except Exception as e:
                logger.warning("session metrics bump: %s", e)

            return response_data

        # STEP 4: Check cache first, then get response from LLM (Groq -> Gemini -> Ollama)
        cache_key_data = f"{message}:{provider}:{model}"
        _cache_model = f"{model}#ctx={ollama_num_ctx}" if ollama_num_ctx else model
        cached_response = get_cached_response(message, provider, _cache_model)
        
        if cached_response:
            print(f"   🎯 Cache hit for {provider} ({model})")
            # Update performance stats for cache hit
            record_provider_performance(provider, 0.1, True)  # Very fast response
            # Add cache metadata
            cached_response = dict(cached_response)
            cached_response = _normalize_cached_chat_rag_blob(cached_response)
            cached_response["request_id"] = request_id
            cached_response['cached'] = True
            cached_response['cache_timestamp'] = cached_response.get('timestamp')
            if want_stream:
                blob = dict(cached_response)
                txt = blob.get("response") or ""

                @stream_with_context
                def _gen_cached_sse():
                    # Werkzeug 3 streaming: iterator must yield bytes, not str.
                    chunk_size = max(32, min(160, max(1, len(txt) // 10)))
                    for i in range(0, len(txt), chunk_size):
                        part = txt[i : i + chunk_size]
                        yield (
                            f"data: {json.dumps({'text': part})}\n\n"
                        ).encode("utf-8")
                    meta = {k: v for k, v in blob.items() if k != "response"}
                    meta["cached"] = True
                    yield (
                        f"data: {json.dumps({'done': True, 'meta': meta}, default=str)}\n\n"
                    ).encode("utf-8")
                    yield b"data: [DONE]\n\n"
                    chat_perf["t_llm_end"] = chat_perf.get("t_rag_end") or time.perf_counter()
                    _flush_chat_perf_metrics(
                        message=message,
                        request_id=request_id,
                        chat_perf=chat_perf,
                        provider=str(blob.get("provider") or "unknown"),
                        model=str(blob.get("model_used") or model or ""),
                        cached=True,
                        streamed=True,
                    )
                    try:
                        bump_from_chat_response(
                            session_id,
                            blob,
                            streamed=True,
                            routing_debug={},
                        )
                    except Exception as e:
                        logger.warning("session metrics bump (cache sse): %s", e)

                return Response(
                    _gen_cached_sse(),
                    mimetype="text/event-stream",
                    direct_passthrough=True,
                    headers={
                        "Cache-Control": "no-cache",
                        "X-Accel-Buffering": "no",
                        "Connection": "keep-alive",
                    },
                )
            chat_perf["t_llm_end"] = chat_perf.get("t_rag_end") or time.perf_counter()
            _flush_chat_perf_metrics(
                message=message,
                request_id=request_id,
                chat_perf=chat_perf,
                provider=str(cached_response.get("provider") or provider),
                model=str(cached_response.get("model_used") or model or ""),
                cached=True,
                streamed=False,
            )
            try:
                bump_from_chat_response(
                    session_id,
                    cached_response,
                    streamed=False,
                    routing_debug={},
                )
            except Exception as e:
                logger.warning("session metrics bump (cache): %s", e)
            return jsonify(cached_response)
        else:
            print(f"   🔄 Cache miss for {provider} ({model}) - calling LLM")

        if want_stream:
            stream_tup = resolve_ollama_stream_target(
                route_key_rl, provider_preference_rl, messages_llm, chat_route_cfg
            )
            if stream_tup:
                _pkey_s, ocfg_s, attempted_s = stream_tup
                if ollama_streaming_allowed_for_route(
                    route_key_rl,
                    provider_preference_rl,
                    messages_llm,
                    chat_route_cfg,
                    _pkey_s,
                    attempted_s,
                ):
                    base_url = (ocfg_s.get("base_url") or "http://localhost:11434").strip()
                    mdl_used = str(ocfg_s.get("model") or model)
                    temperature = float(ocfg_s.get("temperature", 0.2))
                    timeout_s = int(ocfg_s["timeout_s"]) if ocfg_s.get("timeout_s") is not None and str(ocfg_s.get("timeout_s")).strip() != "" else default_ollama_timeout_s()
                    _ncs = ocfg_s.get("num_ctx")
                    num_ctx_s = int(_ncs) if _ncs is not None and str(_ncs).strip() != "" else None
                    if num_ctx_s is not None and num_ctx_s <= 0:
                        num_ctx_s = None

                    _mt_stream = ocfg_s.get("max_tokens")
                    try:
                        _mt_stream_i = int(_mt_stream) if _mt_stream is not None and str(_mt_stream).strip() != "" else None
                    except (TypeError, ValueError):
                        _mt_stream_i = None
                    _stop_raw_s = ocfg_s.get("ollama_stop")
                    if isinstance(_stop_raw_s, list) and _stop_raw_s:
                        _stop_stream = [str(x) for x in _stop_raw_s]
                    else:
                        _stop_stream = faithh_ollama_stop_sequences()

                    @stream_with_context
                    def _gen_ollama_sse():
                        # Werkzeug 3 streaming: iterator must yield bytes, not str.
                        full_chunks: list[str] = []
                        try:
                            t0 = time.time()
                            for piece in iter_ollama_generate_stream(
                                base_url=base_url,
                                model=mdl_used,
                                prompt=full_prompt,
                                temperature=temperature,
                                timeout_s=timeout_s,
                                num_ctx=num_ctx_s,
                                max_tokens_from_config=_mt_stream_i,
                                stop=_stop_stream,
                            ):
                                full_chunks.append(piece)
                                yield (
                                    f"data: {json.dumps({'text': piece})}\n\n"
                                ).encode("utf-8")
                            assistant_text = "".join(full_chunks)
                            latency_ms = int((time.time() - t0) * 1000)
                            chat_routing_debug["route_key"] = route_key_rl
                            chat_routing_debug["llm_routing"] = {
                                "route": route_key_rl,
                                "provider": _pkey_s,
                                "model": mdl_used,
                                "latency_ms": latency_ms,
                                "used_fallback": False,
                                "attempted": attempted_s,
                                "streamed": True,
                            }
                            record_provider_performance(_pkey_s, latency_ms / 1000.0, True)
                            prov_label = "Ollama"
                            meta = _finalize_response(assistant_text, mdl_used, prov_label, streamed_final=True)
                            meta_out = {k: v for k, v in meta.items() if k != "response"}
                            yield (
                                f"data: {json.dumps({'done': True, 'meta': meta_out}, default=str)}\n\n"
                            ).encode("utf-8")
                            yield b"data: [DONE]\n\n"
                            _log_chat_result("ok", _pkey_s, mdl_used)
                        except Exception as e:
                            yield (
                                f"data: {json.dumps({'error': str(e)})}\n\n"
                            ).encode("utf-8")
                            _log_chat_result("error", _pkey_s, detail=str(e))

                    return Response(
                        _gen_ollama_sse(),
                        mimetype="text/event-stream",
                        direct_passthrough=True,
                        headers={
                            "Cache-Control": "no-cache",
                            "X-Accel-Buffering": "no",
                            "Connection": "keep-alive",
                        },
                    )

        if provider == "anthropic":
            anthropic_model = data.get('anthropic_model') or model or 'claude-3-haiku-20240307'
            if not ANTHROPIC_API_KEY:
                _log_chat_result("error", "anthropic", detail="missing_anthropic_key")
                return jsonify({
                    'success': False,
                    'error': 'ANTHROPIC_API_KEY not set',
                    'provider': 'anthropic',
                    'model_attempted': anthropic_model,
                    'request_id': request_id
                }), 400

            anthropic_start_time = time.time()
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
                
                # Convert full_prompt to messages format for Claude
                messages = [{"role": "user", "content": full_prompt}]
                
                response = client.messages.create(
                    model=anthropic_model,
                    max_tokens=4096,
                    temperature=0.7,
                    messages=messages
                )
                anthropic_response_time = time.time() - anthropic_start_time
                
                if response.content:
                    assistant_response = response.content[0].text
                    record_provider_performance("anthropic", anthropic_response_time, True)
                    response_data = _finalize_response(assistant_response, anthropic_model, "Anthropic")
                    _log_chat_result("ok", "anthropic", anthropic_model)
                    return jsonify(response_data)
                else:
                    record_provider_performance("anthropic", anthropic_response_time, False, "empty_response")
                    _log_chat_result("error", "anthropic", anthropic_model, "empty_response")
                    return jsonify({
                        'success': False,
                        'error': 'Anthropic returned empty response',
                        'provider': 'anthropic',
                        'model_attempted': anthropic_model,
                        'request_id': request_id
                    }), 502
                    
            except Exception as e:
                anthropic_response_time = time.time() - anthropic_start_time
                record_provider_performance("anthropic", anthropic_response_time, False, str(e))
                _log_chat_result("error", "anthropic", detail=str(e))
                return jsonify({
                    'success': False,
                    'error': f"Anthropic request failed: {e}",
                    'provider': 'anthropic',
                    'model_attempted': anthropic_model,
                    'request_id': request_id
                }), 502

        if provider == "gemini" or (provider == "ollama" and GEMINI_AVAILABLE and 'gemini' in model.lower()):
            gemini_model_name = data.get('gemini_model') or 'gemini-2.0-flash-exp'
            if not GEMINI_AVAILABLE:
                _log_chat_result("error", "gemini", detail="missing_gemini_key")
                return jsonify({
                    'success': False,
                    'error': 'GEMINI_API_KEY not set',
                    'provider': 'gemini',
                    'model_attempted': gemini_model_name,
                    'request_id': request_id
                }), 400
            gemini_start_time = time.time()
            try:
                import google.generativeai as genai
                genai.configure(api_key=GEMINI_API_KEY)
                gemini_model = genai.GenerativeModel(gemini_model_name)
                response = gemini_model.generate_content(full_prompt)
                gemini_response_time = time.time() - gemini_start_time
                
                assistant_response = response.text
                record_provider_performance("gemini", gemini_response_time, True)
                response_data = _finalize_response(assistant_response, gemini_model_name, "Google")
                _log_chat_result("ok", "gemini", gemini_model_name)
                return jsonify(response_data)
            except Exception as e:
                gemini_response_time = time.time() - gemini_start_time
                record_provider_performance("gemini", gemini_response_time, False, str(e))
                _log_chat_result("error", "gemini", detail=str(e))
                print(f"Gemini error: {e}")

        # Ollama / Groq / local_webui: shared routing (health-aware Groq gate + fallbacks)
        try:
            provs_chk = chat_route_cfg.get("providers") or {}
            if not provs_chk:
                raise RuntimeError("configs/model_config.yaml missing providers")

            out = run_llm_route_with_pin(
                route_key_rl, provider_preference_rl, messages_llm, chat_route_cfg
            )
            routing = out["routing"]
            chat_routing_debug["route_key"] = route_key_rl
            chat_routing_debug["llm_routing"] = routing
            pkey = routing.get("provider", "ollama")
            model_used = str(routing.get("model") or model)
            latency_s = float(routing.get("latency_ms") or 0) / 1000.0
            record_provider_performance(pkey, latency_s, True)

            mi = model_used.lower()
            if pkey == "groq":
                provider_name = "Groq"
            elif pkey == "local_webui":
                provider_name = "Local (text-generation-webui)"
            elif "llama" in mi:
                provider_name = "Meta (via Ollama)"
            elif "qwen" in mi or "deepseek" in mi:
                provider_name = "Alibaba (via Ollama)"
            else:
                provider_name = "Ollama"

            response_time = (datetime.now() - start_time).total_seconds()
            tokens_processed = len((out.get("text") or "").split())
            response_data = _finalize_response(out["text"], model_used, provider_name)
            if not (response_data.get("response") or "").strip():
                _log_chat_result("error", pkey, model_used, "empty_llm_response")
                update_model_performance(model_used, response_time, False, error="empty_llm_response")
                return jsonify({
                    "success": False,
                    "error": (
                        "The model returned an empty reply. Try another model, disable RAG briefly, "
                        "or verify API keys (e.g. Groq) if using cloud routing."
                    ),
                    "provider": pkey,
                    "model_attempted": model_used,
                    "request_id": request_id,
                }), 502
            update_model_performance(model_used, response_time, True, tokens_processed)
            _log_chat_result("ok", pkey, model_used)
            return jsonify(response_data)
        except ProviderError as e:
            _log_chat_result("error", provider, model, str(e))
            try:
                note_error(session_id)
            except Exception:
                pass
            return jsonify({
                'success': False,
                'error': str(e),
                'provider': provider,
                'model_attempted': model,
                'request_id': request_id,
            }), 502

    except Exception as e:
        import traceback
        _log_chat_result("error", locals().get("provider", "unknown"), detail=str(e))
        try:
            _sid = locals().get("session_id")
            if _sid:
                note_error(_sid)
        except Exception:
            pass
        print(f"❌ Chat error: {e}")
        print(traceback.format_exc())
        
        # Update model performance tracking for error
        response_time = (datetime.now() - start_time).total_seconds()
        model_used = locals().get("model", DEFAULT_MODEL)
        update_model_performance(model_used, response_time, False, error=str(e))
        
        return jsonify({
            'success': False,
            'error': str(e),
            'response': f"Error: {str(e)}",
            'provider': locals().get("provider", "unknown"),
            'model_used': locals().get("model", DEFAULT_MODEL),
            'model_attempted': locals().get("model", DEFAULT_MODEL),
            'request_id': request_id
        }), 500

@app.route('/api/search', methods=['POST'])
def search():
    """Google Search API endpoint with rate limiting and fallbacks"""
    if not google_search:
        return jsonify({
            'success': False,
            'error': 'Google Search API not available',
            'results': []
        }), 503
    
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'Query parameter required',
                'results': []
            }), 400
        
        query = data['query'].strip()
        num_results = data.get('num_results', 5)
        
        # Perform search
        result = google_search.search(query, num_results)
        
        # Add usage stats
        result['usage_stats'] = google_search.get_usage_stats()
        
        return jsonify({
            'success': True,
            **result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Search failed: {str(e)}',
            'results': []
        }), 500


@app.route('/api/search/status', methods=['GET'])
def search_status():
    """Get Google Search API status and usage statistics"""
    if not google_search:
        return jsonify({
            'available': False,
            'error': 'Google Search API not initialized'
        })
    
    return jsonify({
        'available': True,
        'usage_stats': google_search.get_usage_stats()
    })


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = UPLOAD_FOLDER / filename
        file.save(filepath)
        
        file_content = None
        if filename.endswith(('.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml')):
            try:
                with open(filepath, 'r') as f:
                    file_content = f.read()
            except:
                pass
        
        return jsonify({
            'success': True,
            'filename': filename,
            'path': str(filepath),
            'content': file_content,
            'size': filepath.stat().st_size,
            'type': mimetypes.guess_type(filename)[0]
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/rag_search', methods=['POST'])
def rag_search():
    # Logic for Humans: Expose Chroma search to the UI/debug tools with modes (auto/governance/general) similar to internal smart_rag branching.
    """RAG search endpoint with optional strict retrieval profiles."""
    if not CHROMA_CONNECTED:
        return jsonify({'success': False, 'error': 'ChromaDB not connected'}), 503
    
    try:
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            return jsonify({"success": False, "error": "Invalid JSON body (expected object)"}), 400
        query = data.get('query', '')
        n_results = data.get('n_results', 5)
        mode = data.get('mode', 'auto')  # auto | governance | general
        valid_modes = {'auto', 'governance', 'general'}
        if mode not in valid_modes:
            return jsonify({
                'success': False,
                'error': f"Invalid mode '{mode}'. Expected one of: auto, governance, general"
            }), 400

        governance_keywords = [
            'constitution', 'constitutional', 'governance', 'governing', 'ucf', 'penumbra',
            'civic tome', 'astris', 'auctor', 'token', 'floor', 'diversity floor',
            'principle', 'framework', 'charter', 'bylaws', 'rules', 'regulation',
            'gamer', 'minimum compliance', 'structural', 'mechanism', 'policy',
            'governance design', 'participation', 'civic', 'democratic', 'decision making'
        ]
        is_governance_query = any(k in query.lower() for k in governance_keywords)
        strict_governance = mode == 'governance' or (mode == 'auto' and is_governance_query)

        if not get_query_embedder():
            return jsonify({'success': False, 'error': 'Embedder unavailable'}), 503

        if strict_governance:
            governance_where = {
                "$or": [
                    {"domain": {"$eq": "constella_constitutional"}},
                    {
                        "$and": [
                            {"domain": {"$eq": "alife"}},
                            {
                                "$or": [
                                    {"source_type": {"$eq": "alife_experiment"}},
                                    {"source_type": {"$eq": "synthesis_document"}},
                                    {"source_type": {"$eq": "alife_cross_experiment_pattern"}},
                                ]
                            },
                        ]
                    },
                ]
            }
            results = query_collection(query, n_results=n_results, where=governance_where)
        else:
            results = query_collection(query, n_results=n_results)
        
        if not results:
            return jsonify({'success': False, 'error': 'Query failed'}), 500
        
        documents = results['documents'][0] if results['documents'] else []
        distances = results['distances'][0] if results['distances'] else []
        
        return jsonify({
            'success': True,
            'results': documents,
            'distances': distances,
            'mode_used': 'governance_strict' if strict_governance else 'general',
            'total_documents': collection.count() if collection else 0,
            'embedding_model': 'BAAI/bge-base-en-v1.5 (768-dim)'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# Phase 6: Genomic Impedance Reading Endpoints
# ============================================================

@app.route('/api/genomic/impedance-sensor', methods=['POST'])
def create_genomic_impedance_sensor():
    """Create genomic impedance sensor for an organism"""
    if not GENOMIC_ENABLED or not genomic_impedance_sensor:
        return jsonify({'success': False, 'error': 'Genomic services not available'}), 503
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON request'}), 400
        
        organism_id = data.get('organism_id')
        position = data.get('position', [0.0, 0.0, 0.0])
        sensitivity = data.get('sensitivity', 0.7)
        
        if not organism_id:
            return jsonify({'error': 'organism_id is required'}), 400
        
        if not isinstance(position, list) or len(position) != 3:
            return jsonify({'error': 'Position must be [x, y, z] coordinates'}), 400
        
        result = genomic_impedance_sensor.create_genomic_sensor(organism_id, tuple(position), sensitivity)
        
        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'genomic_sensor': result,
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({'error': 'Genomic impedance sensor failed', 'details': str(e)}), 500

@app.route('/api/genomic/biasing-analysis', methods=['POST'])
def genomic_biasing_analysis():
    """Analyze genomic biasing effects"""
    if not GENOMIC_ENABLED or not genomic_biasing_engine:
        return jsonify({'success': False, 'error': 'Genomic services not available'}), 503
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON request'}), 400
        
        organism_id = data.get('organism_id')
        original_genome = data.get('original_genome')
        biasing_strength = data.get('biasing_strength', 0.5)
        
        if not organism_id or not original_genome:
            return jsonify({'error': 'organism_id and original_genome are required'}), 400
        
        result = genomic_biasing_engine.apply_genomic_biasing(organism_id, original_genome, biasing_strength)
        
        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'biasing_analysis': result,
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({'error': 'Genomic biasing analysis failed', 'details': str(e)}), 500

@app.route('/api/genomic/sensor-readings/<organism_id>')
def genomic_sensor_readings(organism_id):
    """Get sensor readings for a specific organism"""
    if not GENOMIC_ENABLED or not genomic_impedance_sensor:
        return jsonify({'success': False, 'error': 'Genomic services not available'}), 503
    
    try:
        result = genomic_impedance_sensor.get_sensor_readings(organism_id)
        
        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'sensor_readings': result,
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({'error': 'Genomic sensor readings failed', 'details': str(e)}), 500

@app.route('/api/genomic/analyze-sensors')
def analyze_genomic_sensors():
    """Analyze all genomic sensors"""
    if not GENOMIC_ENABLED or not genomic_impedance_sensor:
        return jsonify({'success': False, 'error': 'Genomic services not available'}), 503
    
    try:
        result = genomic_impedance_sensor.analyze_genomic_sensors()
        
        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'sensors_analysis': result,
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({'error': 'Analyze genomic sensors failed', 'details': str(e)}), 500

@app.route('/api/genomic/biasing-patterns')
def genomic_biasing_patterns():
    """Analyze genomic biasing patterns"""
    if not GENOMIC_ENABLED or not genomic_biasing_engine:
        return jsonify({'success': False, 'error': 'Genomic services not available'}), 503
    
    try:
        result = genomic_biasing_engine.analyze_biasing_patterns()
        
        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'biasing_patterns': result,
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({'error': 'Genomic biasing patterns failed', 'details': str(e)}), 500


@app.route('/api/compass/director', methods=['GET'])
def get_compass_director():
    """Return Director analysis - synthesized actionable intelligence."""
    try:
        from scripts.collectors.director import CompassDirector

        director = CompassDirector()
        result = director.analyze()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "attention_items": [],
            "suggested_actions": [],
            "context_for_ai": "Director failed to analyze system state.",
        }), 500


# ============================================================
# PULSE SECURITY ENDPOINTS
# ============================================================
@app.route('/api/pulse/security/scan', methods=['POST'])
def pulse_security_scan():
    """Test the security scanner."""
    data = request.get_json() or {}
    text = data.get('text', '')
    scan_type = data.get('type', 'input')  # 'input' or 'output'

    scanner = get_scanner()
    result = scanner.scan_output(text) if scan_type == 'output' else scanner.scan_input(text)

    return jsonify({
        "is_safe": result.is_safe,
        "risk_score": result.risk_score,
        "threats_detected": result.threats_detected,
        "scan_time_ms": result.scan_time_ms,
    })


@app.route('/api/pulse/health/check', methods=['GET'])
def pulse_health_check():
    """Check all service health."""
    healer = PulseSelfHealer()
    return jsonify(healer.check_all_services())


@app.route('/api/pulse/health/heal', methods=['POST'])
def pulse_heal():
    """Run healing cycle (dry-run by default)."""
    data = request.get_json() or {}
    dry_run = data.get('dry_run', True)

    healer = PulseSelfHealer(dry_run=dry_run)
    actions = healer.run_healing_cycle()

    return jsonify({
        "actions": [
            {
                "service": a.service,
                "action": a.action,
                "success": a.success,
                "details": a.details,
            }
            for a in actions
        ],
        "dry_run": dry_run,
    })


@app.route('/api/pulse/audit/summary', methods=['GET'])
def pulse_audit_summary():
    """Get audit log summary."""
    audit = get_audit_logger()
    return jsonify(audit.get_summary())


@app.route('/api/pulse/audit/recent', methods=['GET'])
def pulse_audit_recent():
    """Get recent audit events."""
    limit = request.args.get('limit', 50, type=int)
    event_type = request.args.get('type')

    audit = get_audit_logger()
    events = audit.query_recent(limit=limit, event_type=event_type)

    return jsonify({
        "events": [
            {
                "event_id": e.event_id,
                "timestamp": e.timestamp,
                "event_type": e.event_type,
                "actor": e.actor,
                "action": e.action,
                "success": e.success,
            }
            for e in events
        ]
    })

def build_faithh_status_payload():
    # Logic for Humans: One JSON blob describing Ollama, Chroma, optional APIs, JSON state files on disk, ML chips, and PULSE report freshness — reused by status and PLC endpoints.
    """Shared snapshot for /api/status and /api/plc/state (cockpit reads faithh_status)."""
    services = {}

    # Ollama status
    ollama_error = None
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
        if r.status_code == 200:
            models = r.json().get('models', [])
            model_names = [m['name'] for m in models]
            services['ollama'] = {
                'status': 'online',
                'host': OLLAMA_HOST,
                'reachable': True,
                'models': model_names,
                'count': len(models)
            }
        else:
            ollama_error = f"HTTP {r.status_code}"
            services['ollama'] = {
                'status': 'offline',
                'host': OLLAMA_HOST,
                'reachable': False,
                'error': ollama_error
            }
    except Exception as e:
        ollama_error = str(e)
        services['ollama'] = {
            'status': 'offline',
            'host': OLLAMA_HOST,
            'reachable': False,
            'error': ollama_error
        }

    # ChromaDB status
    chroma_url = CHROMA_BASE_URL
    chroma_reachable = False
    chroma_error = None
    try:
        r = requests.get(f"{chroma_url}/api/v1/heartbeat", timeout=2)
        chroma_reachable = r.status_code < 500
        if not chroma_reachable:
            chroma_error = f"HTTP {r.status_code}"
    except Exception as e:
        chroma_error = str(e)
        chroma_reachable = False

    chroma_status = "online" if (chroma_reachable and CHROMA_CONNECTED) else ("degraded" if chroma_reachable else "offline")

    try:
        doc_count = collection.count() if CHROMA_CONNECTED and collection else 'unavailable'
    except Exception as e:
        logger.warning(f"ChromaDB count failed: {e}")
        doc_count = 'unavailable'

    services['chromadb'] = {
        'status': chroma_status,
        'host': chroma_url,
        'reachable': chroma_reachable,
        'connected': CHROMA_CONNECTED,
        'error': chroma_error,
        'documents': doc_count,
        'embedding_model': EMBEDDING_MODEL_NAME
    }

    services['gemini'] = {
        'status': 'configured' if GEMINI_AVAILABLE else 'not configured',
        'model': 'gemini-2.0-flash-exp' if GEMINI_AVAILABLE else None
    }

    services['integrations'] = {
        'memory': MEMORY_FILE.exists(),
        'decisions_log': DECISIONS_LOG.exists(),
        'project_states': PROJECT_STATES.exists(),
        'scaffolding': SCAFFOLDING_FILE.exists()
    }

    services['current_model'] = CURRENT_MODEL

    services['ml_chips'] = {
        'loaded': len(ML_CHIPS),
        'centroids': ML_CHIP_CENTROIDS.shape[0] if ML_CHIP_CENTROIDS is not None else 0,
        'chip_ids': ML_CHIP_IDS[:15],
    }

    pulse_reports = {}
    for name, fname in [('staleness', 'staleness_report.md'), ('divergence', 'divergence_report.md'), ('branches', 'branch_report.md')]:
        path = PULSE_REPORTS_DIR / fname
        if path.exists():
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            pulse_reports[name] = {
                'available': True,
                'generated_at': mtime.isoformat(),
                'age_minutes': round((datetime.now() - mtime).total_seconds() / 60, 1),
            }
        else:
            pulse_reports[name] = {'available': False}

    services['pulse_reflection'] = {
        'tiers_available': sum(1 for r in pulse_reports.values() if r.get('available')),
        'reports': pulse_reports,
    }

    return {
        'success': True,
        'services': services,
        'version': BACKEND_VERSION,
        'workspace': {
            'upload_folder': str(UPLOAD_FOLDER),
            'uploaded_files': len(list(UPLOAD_FOLDER.glob('*'))) if UPLOAD_FOLDER.exists() else 0
        }
    }


def build_workspace_registry():
    # Logic for Humans: Tell the Canvas UI which features exist (RAG, pulse, genomic, …), navigation hints, and last RAG confidence — so the front end can adapt without hardcoding.
    """
    Single source of truth for Canvas/workspace capabilities (faithh_pet_v4.html).
    Keep in sync when adding features — see AGENTS.md Service Registry rule.
    """
    faithh = build_faithh_status_payload()
    inner = faithh.get("services") or {}
    chroma = inner.get("chromadb") or {}
    rag_active = bool(chroma.get("reachable") and chroma.get("connected"))
    pulse_ref = inner.get("pulse_reflection") or {}

    genomic_active = bool(GENOMIC_ENABLED and genomic_impedance_sensor)
    genomic_responding = genomic_active

    sig = LAST_RAG_RETRIEVAL_SIGNAL or {}
    ts = sig.get("ts")
    rag_sig_age = None
    if isinstance(ts, (int, float)):
        rag_sig_age = max(0.0, time.time() - float(ts))
    rag_signal_stale = (
        rag_sig_age is None or rag_sig_age > RAG_SIGNAL_STALE_SECONDS or not sig.get("ran")
    )
    rag_low_confidence = None
    if sig.get("ran") and not rag_signal_stale:
        rag_low_confidence = bool(sig.get("low_confidence"))

    services_map = {
        "chat": {
            "id": "chat",
            "active": True,
            "label": "Chat",
            "description": "Primary LLM conversation",
        },
        "rag": {
            "id": "rag",
            "active": rag_active,
            "label": "Knowledge base",
            "description": "ChromaDB semantic RAG when reachable",
            "chromadb_reachable": bool(chroma.get("reachable")),
            "chromadb_connected": bool(chroma.get("connected")),
            "chromadb_host": chroma.get("host"),
            "documents": chroma.get("documents"),
            "low_confidence": rag_low_confidence,
            "best_distance": (sig.get("best_distance") if not rag_signal_stale else None),
            "distance_threshold": RAG_MAX_DISTANCE_CONFIDENT,
            "signal_stale": rag_signal_stale,
            "signal_age_seconds": (round(rag_sig_age, 1) if rag_sig_age is not None else None),
        },
        "genomic": {
            "id": "genomic",
            "active": genomic_active,
            "responding": genomic_responding,
            "label": "Genomic lab",
            "description": "Impedance / biasing sensors (optional module)",
        },
        "pulse": {
            "id": "pulse",
            "active": True,
            "label": "Pulse",
            "description": "System vitals and reflection reports",
            "reflection_tiers": pulse_ref.get("tiers_available"),
            "ollama_reachable": (inner.get("ollama") or {}).get("reachable"),
        },
        "diagnostics": {
            "id": "diagnostics",
            "active": True,
            "label": "Engine Room",
            "description": "Mission control & diagnostic strip",
            "href": "/cockpit",
        },
    }

    navigation = [
        {
            "id": "chat",
            "target_page": "chatPage",
            "icon": "💬",
            "label": "CHAT",
            "visible": True,
            "order": 10,
            "service_id": "chat",
        },
        {
            "id": "chips",
            "target_page": "chipsPage",
            "icon": "🎴",
            "label": "CHIPS",
            "visible": True,
            "order": 20,
            "service_id": None,
        },
        {
            "id": "pulse",
            "target_page": "statusPage",
            "icon": "⚙️",
            "label": "PULSE",
            "visible": True,
            "order": 30,
            "service_id": "pulse",
        },
        {
            "id": "compass",
            "target_page": "compassPage",
            "icon": "🧭",
            "label": "COMPASS",
            "visible": True,
            "order": 40,
            "service_id": None,
        },
    ]

    return {
        "success": True,
        "schema_version": 1,
        "timestamp": datetime.now().isoformat(),
        "backend_version": BACKEND_VERSION,
        "services": services_map,
        "navigation": navigation,
    }


def _faithh_record_session_metrics_open(session_id: str) -> None:
    # Logic for Humans: When a chat session starts, write a row to the metrics Chroma collection (not the knowledge base) for operational analytics.
    """Persist session-open snapshot to faithh_session_metrics (non-fatal on failure)."""
    if not metrics_collection or not session_id:
        return
    try:
        wr = build_workspace_registry()
        fs = build_faithh_status_payload()
        ollama_ok = bool((fs.get("services") or {}).get("ollama", {}).get("reachable"))
        sz = 0
        try:
            if CHROMA_CONNECTED and collection is not None:
                sz = int(collection.count())
        except Exception:
            sz = 0
        ollama_model = os.environ.get("OLLAMA_MODEL") or os.environ.get("OLLAMA_DEFAULT_MODEL", "")
        kv = os.environ.get("OLLAMA_KV_CACHE_TYPE", "")
        record_session_open(
            metrics_collection,
            session_id,
            workspace_registry=wr,
            rag_signal=dict(LAST_RAG_RETRIEVAL_SIGNAL),
            rag_threshold=RAG_MAX_DISTANCE_CONFIDENT,
            rag_stale_seconds=float(RAG_SIGNAL_STALE_SECONDS),
            primary_provider=MODEL_PROVIDER,
            ollama_model=ollama_model,
            kv_cache_type=kv,
            ollama_reachable=ollama_ok,
            chroma_connected=bool(CHROMA_CONNECTED),
            collection_size=sz,
        )
    except Exception as e:
        logger.warning("session metrics open failed: %s", e)


@app.route('/api/workspace/registry', methods=['GET'])
def get_workspace_registry():
    # Logic for Humans: HTTP wrapper that returns build_workspace_registry() as JSON for the pet UI.
    """Canvas shell: feature flags + tab metadata for faithh_pet_v4.html."""
    return jsonify(build_workspace_registry())


@app.route("/api/metrics/summary", methods=["GET"])
def api_metrics_summary():
    # Logic for Humans: Read recent session-metric documents from Chroma and summarize trends for the Cockpit dashboard.
    """Aggregated session metrics for Cockpit trend panel."""
    days = request.args.get("days", default=7, type=int) or 7
    limit = request.args.get("limit", default=100, type=int) or 100
    days = max(1, min(days, 366))
    limit = max(1, min(limit, 500))
    raw = fetch_session_documents(metrics_collection, days, limit)
    summary = compute_summary_from_parsed_sessions(raw, window_days=days, limit=limit)
    return jsonify({"success": True, **summary})


@app.route("/api/metrics/sessions", methods=["GET"])
def api_metrics_sessions():
    # Logic for Humans: Return raw-ish session metric rows for debugging or drill-down in the UI.
    """Recent session metric documents (drill-down)."""
    limit = request.args.get("limit", default=20, type=int) or 20
    date_filter = (request.args.get("date") or "").strip()
    limit = max(1, min(limit, 200))
    raw = fetch_session_documents(metrics_collection, 366, max(100, limit * 5))
    if date_filter:
        raw = [
            r
            for r in raw
            if (r.get("metadata") or {}).get("date") == date_filter
            or str(r.get("timestamp_open", "")).startswith(date_filter)
        ]
    return jsonify({"success": True, "sessions": raw[:limit]})


def _metrics_flush_allowed() -> bool:
    # Logic for Humans: Gate dangerous “flush metrics” operations so they only run in dev or from localhost.
    """Dev-only flush: localhost or explicit FAITHH_DEV_MODE."""
    if os.environ.get("FAITHH_DEV_MODE", "").strip().lower() in ("1", "true", "yes"):
        return True
    addr = (getattr(request, "remote_addr", None) or "").strip()
    return addr in ("127.0.0.1", "::1", "localhost")


@app.route("/api/metrics/flush-session", methods=["POST"])
def api_metrics_flush_session():
    # Logic for Humans: Manually push a session’s in-memory metrics to Chroma (testing / recovery), only when allowed.
    """Force session metrics accumulator flush and Chroma close row (dev / localhost only)."""
    if not _metrics_flush_allowed():
        return jsonify({"success": False, "error": "not available"}), 403
    data = request.get_json(silent=True) or {}
    session_id = (data.get("session_id") or data.get("sessionId") or "").strip()
    if not session_id:
        return jsonify({"success": False, "error": "session_id required"}), 400
    if metrics_collection is None:
        return jsonify({"success": False, "error": "metrics collection unavailable"}), 503
    try:
        outcome, updated = flush_session_metrics(metrics_collection, session_id)
    except Exception as e:
        logger.warning("flush_session_metrics failed: %s", e)
        return jsonify({"success": False, "error": str(e)}), 500
    return jsonify(
        {
            "success": True,
            "flushed": session_id,
            "chroma_updated": updated,
            "outcome": outcome,
        }
    )


@app.route('/api/status', methods=['GET'])
def status():
    # Logic for Humans: Lightweight status JSON for scripts; same core payload as the faithh_status section of PLC state.
    """Same JSON as ``faithh_status`` inside GET /api/plc/state. Prefer PLC for new clients."""
    return jsonify(build_faithh_status_payload())


@app.route('/api/context/collectors', methods=['GET'])
def get_collector_context():
    """Return aggregated collector data for AI consumption."""
    try:
        from scripts.collectors import Aggregator

        aggregator = Aggregator()
        return jsonify(aggregator.aggregate())
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/collectors/status', methods=['GET'])
def collectors_status_page():
    """Minimal HTML view for collector status (read-only)."""
    return """<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='UTF-8'>
  <title>FAITHH Collectors Status</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; color: #111; }
    h1 { margin-bottom: 0.2em; }
    .meta { color: #555; margin-bottom: 1em; }
    table { border-collapse: collapse; width: 100%; max-width: 800px; }
    th, td { border: 1px solid #ddd; padding: 8px; }
    th { background: #f6f6f6; text-align: left; }
    .ok { color: #0a0; font-weight: 600; }
    .fail { color: #c00; font-weight: 600; }
  </style>
</head>
<body>
  <h1>Collectors Status</h1>
  <div class='meta' id='meta'>Loading...</div>
  <table id='table' style='display:none;'>
    <thead>
      <tr><th>Collector</th><th>Collected At</th><th>Status</th><th>Error</th><th>Version</th></tr>
    </thead>
    <tbody id='rows'></tbody>
  </table>
  <script>
    async function loadStatus() {
      try {
        const resp = await fetch('/api/context/collectors/status');
        const data = await resp.json();
        const meta = document.getElementById('meta');
        const table = document.getElementById('table');
        const rows = document.getElementById('rows');
        if (!data.success) { meta.textContent = 'Error: ' + data.error; return; }
        meta.textContent = 'Aggregated: ' + (data.aggregated_at || 'unknown');
        rows.innerHTML = '';
        Object.entries(data.summary || {}).forEach(([name, info]) => {
          const tr = document.createElement('tr');
          const status = info.success ? 'OK' : 'FAIL';
          tr.innerHTML = `
            <td>${name}</td>
            <td>${info.collected_at || ''}</td>
            <td class='${info.success ? 'ok' : 'fail'}'>${status}</td>
            <td>${info.error || ''}</td>
            <td>${info.version || ''}</td>`;
          rows.appendChild(tr);
        });
        table.style.display = 'table';
      } catch (err) {
        document.getElementById('meta').textContent = 'Fetch error: ' + err;
      }
    }
    loadStatus();
  </script>
</body>
</html>"""


@app.route('/api/context/collectors/run', methods=['POST'])
def run_collector():
    """Run a specific collector (safe whitelist)."""
    try:
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            return jsonify({"success": False, "error": "Invalid JSON body (expected object)"}), 400

        collector = (data.get('collector') or 'all').lower()
        allowed = {
            'health': ['--health'],
            'git': ['--git'],
            'file': ['--files'],
            'files': ['--files'],
            'terminal': ['--terminal'],
            'all': ['--all', '--snapshot'],
        }
        if collector not in allowed:
            return jsonify({"success": False, "error": f"Unsupported collector '{collector}'"}), 400

        cmd = [sys.executable, '-m', 'scripts.collectors.run_collectors', *allowed[collector]]
        proc = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=180,
        )

        return jsonify({
            "success": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout": proc.stdout[-2000:],
            "stderr": proc.stderr[-2000:],
            "collector": collector,
        }), (200 if proc.returncode == 0 else 500)
    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "error": "Collector run timed out"}), 504
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/context/collectors/status', methods=['GET'])
def get_collector_status():
    """Return lightweight collector status for humans/Pulse."""
    try:
        from scripts.collectors.aggregator import Aggregator

        aggregator = Aggregator()
        data = aggregator.aggregate()

        collectors = data.get("collectors", {})
        summary = {
            name: {
                "collected_at": meta.get("collected_at"),
                "success": meta.get("success"),
                "version": meta.get("version"),
                "error": meta.get("error"),
            }
            for name, meta in collectors.items()
        }

        return jsonify({
            "success": True,
            "summary": summary,
            "aggregated_at": data.get("aggregated_at"),
            "issues": data.get("issues", []),
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/test_integrations', methods=['GET'])
def test_integrations():
    """Test endpoint to verify all integrations"""
    try:
        memory = load_memory()
        decisions = load_decisions()
        states = load_project_states()
        
        test_query = "What is FAITHH meant to be?"
        intent = detect_query_intent(test_query)
        
        return jsonify({
            'success': True,
            'files_loaded': {
                'memory': memory is not None,
                'decisions': decisions is not None,
                'states': states is not None
            },
            'self_awareness_present': 'self_awareness' in (memory or {}),
            'test_intent_detection': intent,
            'decisions_count': len(decisions.get('decisions', [])) if decisions else 0,
            'projects_count': len(states.get('projects', {})) if states else 0
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/ml-learning', methods=['GET'])
def get_ml_learning_status():
    """Get ML learning framework status"""
    try:
        framework = get_ml_framework()
        analysis = framework.analyze_global_patterns()
        
        return jsonify({
            'success': True,
            'ml_framework': analysis,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ui-layout', methods=['GET'])
def get_optimal_layout():
    """Get the current optimal UI layout"""
    try:
        optimal_layout = get_optimal_ui_layout()
        usage_patterns = analyze_ui_usage_patterns()
        
        return jsonify({
            'success': True,
            'layout': optimal_layout,
            'usage_patterns': usage_patterns,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ui-layout', methods=['POST'])
def record_ui_interaction_endpoint():
    """Record a UI interaction for learning"""
    try:
        data = request.get_json()
        element_id = data.get('element_id')
        interaction_type = data.get('interaction_type')
        context = data.get('context', {})
        
        if not element_id or not interaction_type:
            return jsonify({
                'success': False,
                'error': 'Missing element_id or interaction_type'
            }), 400
        
        record_ui_interaction(element_id, interaction_type, context)
        
        return jsonify({
            'success': True,
            'message': f'Recorded interaction: {element_id} - {interaction_type}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cache', methods=['GET'])
def get_cache_statistics():
    """Get response cache statistics"""
    try:
        cache_stats = get_cache_stats()
        return jsonify({
            'success': True,
            'cache': cache_stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/performance', methods=['GET'])
def get_performance_stats():
    """Get provider performance statistics"""
    try:
        # Get performance stats
        performance_stats = performance_tracker.get_performance_summary()
        
        return jsonify({
            'success': True,
            'performance': performance_stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/program-advance/stats', methods=['GET'])
def get_program_advance_stats():
    """Get Program Advance system statistics"""
    try:
        # Get performance stats with Program Advance data
        performance_stats = performance_tracker.get_performance_summary()
        
        # Extract Program Advance specific metrics
        pa_stats = {
            'advances_available': list(PROGRAM_ADVANCES.keys()),
            'total_queries': performance_stats.get('total_queries', 0),
            'program_advance_usage': {},
            'chip_usage': {},
            'recent_advances': []
        }
        
        # Analyze recent queries for Program Advance usage
        if hasattr(performance_tracker, 'recent_queries'):
            for query in performance_tracker.recent_queries[-20:]:  # Last 20 queries
                if hasattr(query, 'program_advance_used') and query.program_advance_used:
                    advance_name = query.program_advance_used
                    pa_stats['program_advance_usage'][advance_name] = pa_stats['program_advance_usage'].get(advance_name, 0) + 1
                    
                    # Add to recent advances list
                    pa_stats['recent_advances'].append({
                        'advance': advance_name,
                        'timestamp': query.timestamp.isoformat() if hasattr(query, 'timestamp') else None,
                        'intent': query.intent.get('type') if hasattr(query, 'intent') and query.intent else None
                    })
                
                # Track chip usage
                if hasattr(query, 'integrations_used') and query.integrations_used:
                    for chip in query.integrations_used:
                        pa_stats['chip_usage'][chip] = pa_stats['chip_usage'].get(chip, 0) + 1
        
        # Add system health
        pa_stats['system_health'] = {
            'parallel_engine': 'operational',
            'semantic_detection': 'active',
            'rrf_fusion': 'functional',
            'integration_status': 'complete'
        }
        
        return jsonify({
            'success': True,
            'program_advance_stats': pa_stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/program-advance/optimization', methods=['GET'])
def get_program_advance_optimization():
    """Get Program Advance optimization statistics"""
    try:
        # Get comprehensive optimization stats
        optimization_stats = program_advance_optimizer.get_comprehensive_stats()
        
        # Auto-tune if needed
        program_advance_optimizer.auto_tune()
        
        return jsonify({
            'success': True,
            'optimization_stats': optimization_stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analytics/comprehensive', methods=['GET'])
def get_comprehensive_analytics():
    """Get comprehensive analytics with predictions and insights"""
    try:
        # Perform analysis and generate insights
        analytics_result = advanced_analytics.analyze_and_generate_insights()
        
        return jsonify({
            'success': True,
            'analytics': analytics_result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analytics/stats', methods=['GET'])
def get_analytics_stats():
    """Get advanced analytics system statistics"""
    try:
        # Get comprehensive analytics stats
        analytics_stats = advanced_analytics.get_comprehensive_stats()
        
        return jsonify({
            'success': True,
            'analytics_stats': analytics_stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analytics/metrics', methods=['POST'])
def add_analytics_metric():
    """Add a new metric for analytics tracking"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        metric_type = data.get('metric_type')
        value = data.get('value')
        context = data.get('context', {})
        
        if not metric_type or value is None:
            return jsonify({
                'success': False,
                'error': 'metric_type and value required'
            }), 400
        
        # Add metric to analytics system
        advanced_analytics.add_metric(metric_type, float(value), context)
        
        return jsonify({
            'success': True,
            'message': f'Metric {metric_type} added successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ux/personalized', methods=['GET'])
def get_personalized_experience():
    """Get personalized user experience recommendations"""
    try:
        # Get user ID from query parameter or use default
        user_id = request.args.get('user_id', 'default_user')
        
        # Get personalized experience
        personalized_data = ai_driven_ux.get_personalized_experience(user_id)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'personalized_experience': personalized_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ux/optimize-response', methods=['POST'])
def optimize_response():
    """Optimize response for specific user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        user_id = data.get('user_id', 'default_user')
        query_text = data.get('query_text', '')
        base_response = data.get('base_response', '')
        
        if not query_text or not base_response:
            return jsonify({
                'success': False,
                'error': 'query_text and base_response required'
            }), 400
        
        # Optimize response
        optimized_data = ai_driven_ux.optimize_response_for_user(
            user_id, query_text, base_response
        )
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'optimized_response': optimized_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ux/track-interaction', methods=['POST'])
def track_interaction():
    """Track user interaction for AI-driven UX analysis"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        user_id = data.get('user_id', 'default_user')
        session_id = data.get('session_id', 'default_session')
        interaction_type = data.get('interaction_type', 'unknown')
        interaction_data = data.get('interaction_data', {})
        response_time = data.get('response_time', 0.0)
        success = data.get('success', True)
        
        # Track interaction
        ai_driven_ux.track_interaction(
            user_id, session_id, interaction_type, 
            interaction_data, response_time, success
        )
        
        return jsonify({
            'success': True,
            'message': 'Interaction tracked successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ux/analytics', methods=['GET'])
def get_ux_analytics():
    """Get comprehensive UX analytics"""
    try:
        # Get UX analytics
        ux_analytics = ai_driven_ux.get_ux_analytics()
        
        return jsonify({
            'success': True,
            'ux_analytics': ux_analytics
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health/gpu-hint', methods=['GET'])
def gpu_hint_health():
    # Logic for Humans: Cheap JSON for the Canvas header — DISABLED for Proxmox VM
    """Diagnostic: Flask process GPU visibility vs configured FAITHH physical device index."""
    try:
        return jsonify({
            "status": "disabled",
            "message": "GPU DISABLED for Proxmox VM environment (no GPU access)",
            "cuda_visible_devices": None,
            "faithh_cuda_physical_device": None,
            "alignment": "N/A"
        })
    except Exception as exc:
        return jsonify({"error": str(exc), "status": "unavailable"}), 500


@app.route('/api/health')
def enhanced_health():
    # Logic for Humans: Deep health check aggregating connection monitor, perf tracker, cache, and security stats; may return 503 if unhealthy.
    """Enhanced health endpoint with Phase 4 monitoring"""
    health_data = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '4.0-pulse',
        'services': {},
        'overall_health': {'status': 'healthy', 'issues': []},
    }

    try:
        connection_health = connection_monitor.get_system_health_summary()
    except Exception as e:
        logger.exception("connection_monitor health failed")
        connection_health = {
            'overall_status': 'unknown',
            'total_services': 0,
            'healthy_services': 0,
            'degraded_services': 0,
            'unhealthy_services': 0,
            'required_unhealthy_services': 0,
            'error': str(e),
        }
        health_data['overall_health']['issues'].append(f'connection_monitor: {e}')

    try:
        performance_stats = performance_tracker.get_performance_summary()
    except Exception as e:
        logger.exception("performance_tracker health failed")
        performance_stats = {'active_requests': 0, 'recent_performance': {}}
        health_data['overall_health']['issues'].append(f'performance_tracker: {e}')

    try:
        cache_stats = response_cache.get_stats()
    except Exception as e:
        logger.exception("response_cache health failed")
        cache_stats = {
            'entries': 0,
            'hit_rate_percent': 0.0,
            'utilization_percent': 0.0,
            'total_requests': 0,
        }
        health_data['overall_health']['issues'].append(f'response_cache: {e}')

    try:
        security_stats = security_middleware.get_security_stats()
    except Exception as e:
        logger.exception("security_middleware health failed")
        security_stats = {
            'active_blocked_ips': 0,
            'suspicious_requests_24h': 0,
            'total_clients_tracked': 0,
        }
        health_data['overall_health']['issues'].append(f'security_middleware: {e}')

    health_data['services']['connection_monitor'] = connection_health
    health_data['services']['performance_tracker'] = {
        'status': 'healthy',
        'active_requests': performance_stats.get('active_requests', 0),
        'recent_performance': performance_stats.get('recent_performance', {}),
    }
    health_data['services']['cache'] = {
        'status': 'healthy',
        'entries': cache_stats.get('entries', 0),
        'hit_rate_percent': cache_stats.get('hit_rate_percent', 0.0),
        'utilization_percent': cache_stats.get('utilization_percent', 0.0),
    }
    health_data['services']['security'] = {
        'status': 'healthy',
        'active_blocked_ips': security_stats.get('active_blocked_ips', 0),
        'suspicious_requests_24h': security_stats.get('suspicious_requests_24h', 0),
    }

    overall = connection_health.get('overall_status', 'unknown')
    health_data['overall_health']['status'] = overall if overall in (
        'healthy', 'degraded', 'unhealthy', 'unknown'
    ) else 'unknown'

    # Count only services required for overall health (see connection_monitor required_for_overall).
    uh = connection_health.get('required_unhealthy_services')
    if uh is None:
        uh = connection_health.get('unhealthy_services')
    if isinstance(uh, int) and uh > 0:
        health_data['overall_health']['status'] = 'degraded'
        health_data['overall_health']['issues'].append(f'Unhealthy services: {uh}')

    hr = cache_stats.get('hit_rate_percent')
    total_cache_queries = cache_stats.get('total_requests', 0)
    min_queries_for_hit_rate_warning = 50
    cache_hit_rate_threshold_percent = 10.0
    if (
        isinstance(hr, (int, float))
        and isinstance(total_cache_queries, (int, float))
        and total_cache_queries >= min_queries_for_hit_rate_warning
        and hr < cache_hit_rate_threshold_percent
    ):
        if health_data['overall_health']['status'] == 'healthy':
            health_data['overall_health']['status'] = 'degraded'
        health_data['overall_health']['issues'].append(
            f'Low cache hit rate ({hr:.1f}% over {int(total_cache_queries)} queries)'
        )

    status_code = 200
    if health_data['overall_health']['status'] == 'unhealthy':
        status_code = 503

    return jsonify(health_data), status_code

@app.route('/api/attest', methods=['GET', 'POST'])
def attest():
    """Proof-of-life for the power unit. GET returns the node's attestation status; POST emits
    + persists one signed heartbeat (liveness + real work + continuity chain). The same
    node-agnostic layer the Lite node uses — one attestation discipline, many nodes."""
    if not ATTEST_ENABLED or ATTESTOR is None:
        return jsonify({"success": False, "error": "node attestation unavailable"}), 503
    try:
        if request.method == 'POST':
            beat = ATTESTOR.beat({
                "queries_served": QUERIES_SERVED,
                "chroma_connected": bool(CHROMA_CONNECTED),
                "ml_chips": len(ML_CHIPS),
            })
            return jsonify({"success": True, "emitted": beat, "status": ATTESTOR.status()})
        return jsonify({"success": True, "status": ATTESTOR.status()})
    except Exception as e:
        return jsonify({"success": False, "error": f"attestation failed: {str(e)}"}), 500


@app.route('/health')
def health():
    # Logic for Humans: Minimal liveness JSON for load balancers — Chroma doc count, ML chip load, pulse report ages.
    # Quick doc count (cached if possible)
    try:
        doc_count = collection.count() if CHROMA_CONNECTED and collection else 0
    except Exception:
        doc_count = 0

    # PULSE report freshness
    pulse_reports = {}
    for name, fname in [('staleness', 'staleness_report.md'), ('divergence', 'divergence_report.md'), ('branches', 'branch_report.md')]:
        path = PULSE_REPORTS_DIR / fname
        if path.exists():
            age_min = round((datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)).total_seconds() / 60, 1)
            pulse_reports[name] = {'available': True, 'age_minutes': age_min}
        else:
            pulse_reports[name] = {'available': False}

    return jsonify({
        'status': 'healthy',
        'service': f'FAITHH Professional Backend {BACKEND_VERSION}',
        'chromadb': {'connected': CHROMA_CONNECTED, 'documents': doc_count},
        'ml_chips': {'loaded': len(ML_CHIPS), 'centroids': ML_CHIP_CENTROIDS.shape[0] if ML_CHIP_CENTROIDS is not None else 0},
        'pulse_reflection': pulse_reports,
        'providers': {
            'groq': bool(GROQ_API_KEY),
            'anthropic': bool(ANTHROPIC_API_KEY),
            'gemini': GEMINI_AVAILABLE,
            'ollama': OLLAMA_HOST,
        },
        'features': [
            'chat', 'rag', 'upload', 'ml_chips', 'pulse_reflection',
            'self_awareness_boost', 'decision_citation', 'project_state_awareness',
            'scaffolding_awareness', 'intent_detection', 'smart_context_building',
            'filesystem_operations'
        ]
    })


@app.route('/api/usage', methods=['GET'])
def get_api_usage():
    """
    Budget / usage bar in faithh_pet_v4.html (updateBudgetStatus).
    Stub until real token-cost metering exists.
    """
    try:
        budget = float(os.environ.get("ANTHROPIC_MONTHLY_BUDGET", "20.0"))
    except ValueError:
        budget = 20.0
    return jsonify({
        "current_usage": 0.0,
        "monthly_budget": budget,
        "currency": "USD",
        "stub": True,
    })



@app.route('/api/rainmeter', methods=['GET'])
def rainmeter_state():
    """Flat JSON for Rainmeter WebParser - all panels in one poll."""
    import time as _time
    try:
        import chromadb as _chromadb
        _cc = _chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        _col = _cc.get_collection('faithh_knowledge_base_v2')
        chroma = {'connected': True, 'documents': _col.count()}
    except Exception as _e:
        chroma = {'connected': False, 'documents': 0}
    try:
        ollama_svc = {'reachable': False}
        import requests as _req
        _r = _req.get(f'{OLLAMA_HOST}/api/tags', timeout=2)
        if _r.status_code == 200:
            ollama_svc = {'reachable': True}
    except Exception:
        pass
    try:
        ml = {'loaded': len(ML_CHIPS), 'centroids': ML_CHIP_CENTROIDS.shape[0] if ML_CHIP_CENTROIDS is not None else 0}
    except Exception:
        ml = {'loaded': 0, 'centroids': 0}
    try:
        _snap = get_faithh_status_snapshot()
        model_info = _snap.get('services', {}).get('current_model', {})
    except Exception:
        model_info = {}
    try:
        with open(BASE_DIR / 'ml' / 'output' / 'pulse_state.json') as _pf:
            pulse_state = json.load(_pf)
        _raw_reports = pulse_state.get('reports', {})
        pulse_reports = {}
        for k, v in _raw_reports.items():
            pulse_reports[k] = dict(v)
            if 'age_hours' in v and 'age_minutes' not in v:
                pulse_reports[k]['age_minutes'] = round(v['age_hours'] * 60)
        mood = pulse_state.get('avatar', {}).get('mood', 'unknown')
        energy = pulse_state.get('avatar', {}).get('energy', 0)
        alert_count = pulse_state.get('avatar', {}).get('alert_count', 0)
    except Exception:
        pulse_reports = {}
        pulse_state = {}
        mood = 'unknown'
        energy = 0
        alert_count = 0
    try:
        chip_ids = ML_CHIP_IDS[:5] if ML_CHIP_IDS else []
        chips_str = ', '.join(chip_ids)
    except Exception:
        chips_str = ''
    try:
        with open(BASE_DIR / 'project_states.json') as _psf: ps_data = json.load(_psf)
        raw = ps_data.get('projects', ps_data) if isinstance(ps_data, dict) else ps_data
        projects = list(raw.values()) if isinstance(raw, dict) else raw
        compass_lines = []
        for p in projects[:4]:
            if not isinstance(p, dict): continue
            name = (p.get('name', p.get('id', '?')))[:22]
            phase = p.get('phase', '')[:18]
            steps = p.get('next_steps', [])
            next_step = steps[0][:48] if steps else 'no steps'
            compass_lines.append(f"{name} | {phase} | {next_step}")
        compass_str = ' ;; '.join(compass_lines)
        proj_count = len(projects)
    except Exception as _ce:
        compass_str = f'compass error: {_ce}'
        proj_count = 0
    def tier_age(key):
        try: return round(pulse_reports.get(key, {}).get('age_minutes', -1))
        except: return -1
    def tier_status(age_min, warn_hours=8):
        if age_min < 0: return 'UNKNOWN'
        if age_min > warn_hours * 60: return 'STALE'
        return 'OK'
    s_age = tier_age('staleness'); d_age = tier_age('divergence'); b_age = tier_age('branches')
    # --- journal last entry ---
    try:
        import glob as _glob
        _jfiles = sorted(_glob.glob(str(BASE_DIR / 'ml' / 'output' / 'journal' / '*.md')))
        journal_last = _jfiles[-1].split('/')[-1].replace('.md','') if _jfiles else 'none'
        journal_count = len(_jfiles)
    except Exception:
        journal_last = 'unknown'; journal_count = 0

    # --- avatar info ---
    try:
        _av = pulse_state.get('avatar', {})
        avatar_name = _av.get('name', 'FAITHH')
        avatar_subtitle = _av.get('subtitle', _av.get('role', _av.get('description', '')))
    except Exception:
        avatar_name = 'FAITHH'; avatar_subtitle = ''

    # --- workspace/navigation count ---
    try:
        workspace_count = len(build_workspace_registry().get('navigation', []))
    except Exception:
        workspace_count = 0

    return jsonify({
        "polled_at": _time.strftime('%Y-%m-%d %H:%M:%S'),
        "backend_version": "v4.0-pulse",
        "mood": mood.upper(),
        "energy": round(energy * 100),
        "alert_count": alert_count,
        "model_name": model_info.get('name', 'unknown'),
        "model_provider": model_info.get('provider', 'unknown'),
        "model_latency_ms": round(model_info.get('last_response_time', 0) * 1000),
        "chips_loaded": ml.get('loaded', 0),
        "chips_centroids": ml.get('centroids', 0),
        "active_chip_ids": chips_str,
        "chroma_status": "ONLINE" if chroma.get('connected') else "OFFLINE",
        "chroma_docs": chroma.get('documents', 0),
        "chroma_model": "BGE-768",
        "backend_status": "ONLINE",
        "ollama_status": "ONLINE" if ollama_svc.get('reachable') else "OFFLINE",
        "groq_status": "ONLINE",
        "gemini_status": "ONLINE",
        "vllm_status": "ONLINE",
        "pulse_staleness": tier_status(s_age),
        "pulse_staleness_age": s_age,
        "pulse_divergence": tier_status(d_age, warn_hours=26),
        "pulse_divergence_age": d_age,
        "pulse_branches": tier_status(b_age, warn_hours=50),
        "pulse_branches_age": b_age,
        "pulse_alerts": alert_count,
        "compass": compass_str,
        "compass_project_count": proj_count,
        "journal_last": journal_last,
        "journal_count": journal_count,
        "avatar_name": avatar_name,
        "avatar_subtitle": avatar_subtitle,
        "workspace_count": workspace_count,
    })

@app.route('/api/plc/state', methods=['GET'])
def get_plc_state():
    """
    Process / service snapshot for Cockpit (UI polls ~5s).
    Reads docs/architecture/process_registry.json and returns a compact live view.
    """
    registry_path = BASE_DIR / "docs" / "architecture" / "process_registry.json"
    registry: dict = {}
    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)
    except Exception as e:
        registry = {"error": str(e), "services": [], "generated": None}

    current_state = "idle"
    if registry.get("error"):
        current_state = "error"

    states = []
    for svc in registry.get("services", []):
        eps = svc.get("endpoints")
        ep_count = len(eps) if isinstance(eps, list) else 0
        states.append({
            "id": svc.get("id"),
            "name": svc.get("name"),
            "port": svc.get("port"),
            "status": svc.get("status", "unknown"),
            "endpoint_count": ep_count,
        })

    project_status_path = BASE_DIR / "projects" / "status" / "project_status.json"
    project_status_payload: dict = {}
    try:
        if project_status_path.exists():
            with open(project_status_path, "r", encoding="utf-8") as f:
                project_status_payload = json.load(f)
    except Exception as e:
        project_status_payload = {"error": str(e)}

    component_map_path = BASE_DIR / "projects" / "status" / "component_map.json"
    recent_changes = []
    try:
        if component_map_path.exists():
            cm = json.loads(component_map_path.read_text(encoding="utf-8"))
            cutoff = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
            for comp in cm.get("components", []):
                if str(comp.get("last_changed", "")) >= cutoff:
                    recent_changes.append({
                        "component": comp["name"],
                        "changed": comp["last_changed"],
                        "summary": comp["change_summary"],
                    })
    except Exception as e:
        recent_changes = [{"error": str(e)}]

    faithh_status = {}
    try:
        faithh_status = build_faithh_status_payload()
    except Exception as e:
        faithh_status = {"success": False, "error": str(e)}

    return jsonify({
        "timestamp": time.time(),
        "current_state": current_state,
        "services": states,
        "registry_generated": registry.get("generated", "unknown"),
        "project_status": project_status_payload,
        "recent_component_changes": recent_changes,
        "faithh_status": faithh_status,
    })


@app.route('/api/monitoring/services', methods=['GET'])
def monitoring_services():
    """Comprehensive service monitoring with connection health checks"""
    # Check each provider service health
    service_health = {}
    
    # Groq health check
    def check_groq():
        try:
            import requests
            response = requests.get("https://api.groq.com/openai/v1/models", 
                                  headers={"Authorization": f"Bearer {os.environ.get('GROQ_API_KEY', '')}"},
                                  timeout=5)
            return response.status_code == 200
        except:
            return False
    
    groq_healthy = health_monitor_facade.check_provider_health("groq", check_groq)
    service_health['groq'] = {
        'healthy': groq_healthy,
        'last_check': health_monitor_facade.get_provider_last_check('groq'),
        'api_key_configured': bool(GROQ_API_KEY)
    }
    
    # Anthropic health check
    def check_anthropic():
        try:
            if not ANTHROPIC_API_KEY:
                return False
            import anthropic
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            # Simple API test - list models
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4096,
                messages=[{"role": "user", "content": "test"}],
                timeout=5
            )
            return True
        except:
            return False
    
    anthropic_healthy = health_monitor_facade.check_provider_health("anthropic", check_anthropic)
    service_health['anthropic'] = {
        'healthy': anthropic_healthy,
        'last_check': health_monitor_facade.get_provider_last_check('anthropic'),
        'api_key_configured': bool(ANTHROPIC_API_KEY)
    }
    
    # Ollama health check
    def check_ollama():
        try:
            import requests
            response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    ollama_healthy = health_monitor_facade.check_provider_health("ollama", check_ollama)
    service_health['ollama'] = {
        'healthy': ollama_healthy,
        'last_check': health_monitor_facade.get_provider_last_check('ollama'),
        'endpoint': OLLAMA_HOST
    }
    
    # ChromaDB health check
    def check_chromadb():
        try:
            if CHROMA_CLIENT:
                CHROMA_CLIENT.heartbeat()
                return True
            return False
        except:
            return False
    
    chromadb_healthy = health_monitor_facade.check_provider_health("chromadb", check_chromadb)
    service_health['chromadb'] = {
        'healthy': chromadb_healthy,
        'last_check': health_monitor_facade.get_provider_last_check('chromadb'),
        'connected': CHROMA_CONNECTED
    }
    
    # Overall provider/system health via unified facade
    provider_unhealthy = health_monitor_facade.get_provider_unhealthy_services()
    system_summary = health_monitor_facade.get_system_health_summary()
    overall_healthy = len(provider_unhealthy) == 0 and system_summary.get('overall_status') == 'healthy'
    
    return jsonify({
        'overall_healthy': overall_healthy,
        'provider_unhealthy_services': list(provider_unhealthy),
        'system_health_summary': system_summary,
        'service_health': service_health,
        'monitoring_timestamp': datetime.now().isoformat(),
        'checks_performed': len(service_health)
    })

@app.route('/api/monitoring/enhanced', methods=['GET'])
def enhanced_monitoring():
    """Enhanced monitoring with knowledge base and response quality tracking"""
    try:
        # Import the enhanced monitoring system
        import sys
        sys.path.append('.')
        from enhanced_service_monitor import EnhancedServiceMonitor
        
        monitor = EnhancedServiceMonitor()
        report = monitor.generate_comprehensive_report()
        
        return jsonify({
            'success': True,
            'report': report
        })
        
    except ImportError:
        return jsonify({
            'success': False,
            'error': 'Enhanced monitoring module not available'
        }), 503
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Enhanced monitoring error: {str(e)}'
        }), 500


# ============================================================
# PULSE PATTERN LEARNING ENDPOINTS (added 2026-01-01)
# ============================================================
@app.route('/api/pulse/status', methods=['GET'])
def pulse_status():
    """Get PULSE learning status"""
    if not pulse_tracker:
        return jsonify({"success": False, "error": "PULSE not available"}), 503

    return jsonify({
        "active_chips": len(pulse_tracker.get_active_personalized_chips()),
        "program_advances": len(pulse_tracker.get_program_advances()),
        "pending_proposals": len(pulse_tracker.get_pending_proposals()),
        "patterns_tracked": len(pulse_tracker.patterns.get("chip_sequences", []))
    })

@app.route('/api/pulse/proposals', methods=['GET'])
def get_proposals():
    """Get pending chip proposals"""
    if not pulse_tracker:
        return jsonify({"success": False, "error": "PULSE not available"}), 503

    return jsonify({
        "proposals": pulse_tracker.get_pending_proposals()
    })

@app.route('/api/pulse/approve', methods=['POST'])
def approve_proposal():
    """Approve a chip proposal"""
    if not pulse_tracker:
        return jsonify({"success": False, "error": "PULSE not available"}), 503

    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"success": False, "error": "Invalid JSON body (expected object)"}), 400

    proposal_id = data.get('proposal_id')
    result = pulse_tracker.approve_chip(proposal_id)
    if result:
        return jsonify({"success": True, "chip": result})
    return jsonify({"success": False, "error": "Proposal not found"}), 404

@app.route('/api/pulse/reject', methods=['POST'])
def reject_proposal():
    """Reject a chip proposal"""
    if not pulse_tracker:
        return jsonify({"success": False, "error": "PULSE not available"}), 503

    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"success": False, "error": "Invalid JSON body (expected object)"}), 400
    proposal_id = data.get('proposal_id')
    result = pulse_tracker.reject_chip(proposal_id)
    return jsonify({"success": result})

@app.route('/api/pulse/chips', methods=['GET'])
def get_personalized_chips():
    """Get user's personalized chip library"""
    if not pulse_tracker:
        return jsonify({"success": False, "error": "PULSE not available"}), 503

    return jsonify({
        "personalized_chips": pulse_tracker.get_active_personalized_chips(),
        "program_advances": pulse_tracker.get_program_advances()
    })

# ============================================================
# ML CHIP ENDPOINTS (added 2026-02-07)
# ============================================================
@app.route('/api/ml/chips', methods=['GET'])
def get_ml_chips():
    """Return the full ML chip library with metadata (no centroids)."""
    chips_out = []
    for chip in ML_CHIPS:
        chips_out.append({
            'id': chip.get('id'),
            'label': chip.get('label'),
            'description': chip.get('description'),
            'doc_count': chip.get('doc_count', 0),
            'micro_topic_count': chip.get('micro_topic_count', 0),
            'categories': chip.get('categories', {}),
            'top_keywords': chip.get('top_keywords', [])[:8],
        })
    return jsonify({
        'success': True,
        'chip_count': len(chips_out),
        'chips': chips_out
    })

@app.route('/api/ml/chips/activate', methods=['POST'])
def ml_chip_activate():
    """Given a query, return ML chip activation scores via centroid cosine similarity."""
    data = request.get_json(silent=True) or {}
    query = data.get('query', '').strip()
    if not query:
        return jsonify({'success': False, 'error': 'No query provided'}), 400
    top_k = min(int(data.get('top_k', 5)), 15)
    threshold = float(data.get('threshold', 0.10))
    activated = activate_ml_chips(query, top_k=top_k, threshold=threshold)
    return jsonify({
        'success': True,
        'query': query,
        'activated': activated,
        'total_chips': len(ML_CHIPS)
    })

@app.route('/api/ml/chips/resync', methods=['POST'])
def ml_chip_resync():
    """Trigger ML chip re-synthesis if needed, or force it.
    POST body: { "force": false, "threshold": 10, "check_only": false }
    """
    data = request.get_json(silent=True) or {}
    force = data.get('force', False)
    check_only = data.get('check_only', False)
    threshold = float(data.get('threshold', 10))

    # Import the resync checker
    try:
        sys.path.insert(0, str(BASE_DIR / 'ml'))
        from chip_resync import check_needs_resync
    except ImportError as e:
        return jsonify({'success': False, 'error': f'chip_resync module not found: {e}'}), 500

    needs_resync, status = check_needs_resync(threshold_pct=threshold)
    if force:
        needs_resync = True
        status['reason'] = 'forced via API'

    if check_only:
        return jsonify({
            'success': True,
            'needs_resync': needs_resync,
            'status': status,
            'current_chips': len(ML_CHIPS),
        })

    if not needs_resync:
        return jsonify({
            'success': True,
            'needs_resync': False,
            'status': status,
            'message': 'No resync needed',
        })

    # Run resync in background subprocess (don't block the request)
    import threading
    def _run_resync():
        import subprocess as sp
        venv_python = BASE_DIR / 'ml' / 'venv' / 'bin' / 'python'
        env = os.environ.copy()
        # GPU DISABLED for Proxmox VM environment
        # env['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
        # env['CUDA_VISIBLE_DEVICES'] = get_faithh_cuda_physical_device_index()
        env['CUDA_VISIBLE_DEVICES'] = ''  # Force CPU-only
        result = sp.run(
            [str(venv_python), str(BASE_DIR / 'ml' / 'chip_resync.py'), '--force'],
            cwd=str(BASE_DIR), env=env, capture_output=True, text=True, timeout=600
        )
        if result.returncode == 0:
            print("✅ Chip resync complete — reloading chips")
            _load_ml_chips()  # Hot-reload without restart
        else:
            print(f"❌ Chip resync failed: {result.stderr[-500:]}")

    thread = threading.Thread(target=_run_resync, daemon=True)
    thread.start()

    return jsonify({
        'success': True,
        'needs_resync': True,
        'status': status,
        'message': 'Resync started in background. Chips will auto-reload when complete.',
    })


@app.route('/api/ml/chips/reload', methods=['POST'])
def ml_chip_reload():
    """Hot-reload ML chips from consolidated_chips.json without full resync."""
    _load_ml_chips()
    return jsonify({
        'success': True,
        'chip_count': len(ML_CHIPS),
        'centroid_shape': list(ML_CHIP_CENTROIDS.shape) if ML_CHIP_CENTROIDS is not None else None,
        'message': f'Reloaded {len(ML_CHIPS)} chips',
    })


# ============================================================
# PULSE REFLECTION ENGINE ENDPOINTS (added 2026-02-15)
# ============================================================
PULSE_REPORTS_DIR = BASE_DIR / 'ml' / 'output'

def _read_pulse_report(filename: str) -> dict | None:
    """Read a PULSE report file and return its content."""
    path = PULSE_REPORTS_DIR / filename
    if path.exists():
        try:
            content = path.read_text(encoding='utf-8')
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            return {
                'content': content,
                'generated_at': mtime.isoformat(),
                'age_minutes': round((datetime.now() - mtime).total_seconds() / 60, 1),
                'file': str(path.relative_to(BASE_DIR)),
            }
        except Exception as e:
            return {'error': str(e)}
    return None


def _run_pulse_script(script_name: str, extra_args: list = None) -> dict:
    """Run a PULSE reflection script and return results."""
    script_path = BASE_DIR / 'scripts' / script_name
    if not script_path.exists():
        return {'success': False, 'error': f'Script not found: {script_name}'}

    cmd = [sys.executable, str(script_path), '--json']
    if extra_args:
        cmd.extend(extra_args)

    try:
        proc = subprocess.run(
            cmd, cwd=BASE_DIR, capture_output=True, text=True, timeout=300,
        )
        if proc.returncode == 0:
            # Parse JSON from stdout (skip any non-JSON lines)
            stdout = proc.stdout.strip()
            # Find the JSON object in output
            json_start = stdout.find('{')
            if json_start >= 0:
                return {'success': True, 'data': json.loads(stdout[json_start:])}
            return {'success': True, 'raw_output': stdout[-3000:]}
        return {
            'success': False,
            'error': f'Script exited with code {proc.returncode}',
            'stderr': proc.stderr[-1000:],
        }
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Script timed out (300s limit)'}
    except json.JSONDecodeError as e:
        return {'success': False, 'error': f'JSON parse error: {e}', 'raw': proc.stdout[-1000:]}
    except Exception as e:
        return {'success': False, 'error': str(e)}


@app.route('/api/pulse/reflection/status', methods=['GET'])
def pulse_reflection_status():
    """Get PULSE Reflection Engine status — latest report timestamps and summaries."""
    reports = {
        'staleness': _read_pulse_report('staleness_report.md'),
        'divergence': _read_pulse_report('divergence_report.md'),
        'branches': _read_pulse_report('branch_report.md'),
    }

    # Count available vs missing
    available = sum(1 for r in reports.values() if r is not None)

    return jsonify({
        'success': True,
        'engine': 'PULSE Reflection Engine',
        'tiers_available': available,
        'tiers_total': 3,
        'reports': {
            name: {
                'available': report is not None,
                'generated_at': report.get('generated_at') if report else None,
                'age_minutes': report.get('age_minutes') if report else None,
            }
            for name, report in reports.items()
        },
        'scripts': {
            'staleness_detector': (BASE_DIR / 'scripts' / 'staleness_detector.py').exists(),
            'decision_divergence': (BASE_DIR / 'scripts' / 'decision_divergence.py').exists(),
            'branch_explorer': (BASE_DIR / 'scripts' / 'branch_explorer.py').exists(),
        },
    })


@app.route('/api/pulse/reflection/staleness', methods=['GET'])
def pulse_reflection_staleness():
    """Get the latest staleness report."""
    report = _read_pulse_report('staleness_report.md')
    if not report:
        return jsonify({'success': False, 'error': 'No staleness report found. Run: python scripts/staleness_detector.py --output staleness_report'}), 404
    return jsonify({'success': True, 'report': report})


@app.route('/api/pulse/reflection/divergence', methods=['GET'])
def pulse_reflection_divergence():
    """Get the latest decision divergence report."""
    report = _read_pulse_report('divergence_report.md')
    if not report:
        return jsonify({'success': False, 'error': 'No divergence report found. Run: python scripts/decision_divergence.py --output divergence_report'}), 404
    return jsonify({'success': True, 'report': report})


@app.route('/api/pulse/reflection/branches', methods=['GET'])
def pulse_reflection_branches():
    """Get the latest branch exploration report."""
    report = _read_pulse_report('branch_report.md')
    if not report:
        return jsonify({'success': False, 'error': 'No branch report found. Run: python scripts/branch_explorer.py --output branch_report'}), 404
    return jsonify({'success': True, 'report': report})


@app.route('/api/pulse/reflection/run', methods=['POST'])
def pulse_reflection_run():
    """Trigger a PULSE reflection sweep. Accepts JSON body with optional 'tier' (1,2,3,'all')."""
    data = request.get_json(silent=True) or {}
    tier = str(data.get('tier', 'all')).lower()

    results = {}

    if tier in ('1', 'staleness', 'all'):
        results['staleness'] = _run_pulse_script(
            'staleness_detector.py', ['--output', 'staleness_report']
        )

    if tier in ('2', 'divergence', 'all'):
        results['divergence'] = _run_pulse_script(
            'decision_divergence.py', ['--output', 'divergence_report']
        )

    if tier in ('3', 'branches', 'all'):
        results['branches'] = _run_pulse_script(
            'branch_explorer.py', ['--output', 'branch_report']
        )

    if not results:
        return jsonify({'success': False, 'error': f"Unknown tier: {tier}. Use 1, 2, 3, or 'all'"}), 400

    all_ok = all(r.get('success', False) for r in results.values())
    return jsonify({
        'success': all_ok,
        'tier_requested': tier,
        'results': results,
    }), 200 if all_ok else 207


# ============================================================
# PULSE TIER 4 — AVATAR STATE + AUTONOMOUS ACTIONS
# ============================================================

@app.route('/api/pulse/state', methods=['GET'])
def pulse_avatar_state():
    """Get the PULSE-driven avatar state (mood, energy, alerts, suggestions)."""
    if not PULSE_STATE_FILE.exists():
        return jsonify({
            'success': True,
            'avatar': {'mood': 'curious', 'energy': 0.4, 'alerts': [], 'suggestions': ['No PULSE state yet. Run: python scripts/pulse_autonomous.py'], 'alert_count': 0},
            'stale': True,
        })
    try:
        state = json.loads(PULSE_STATE_FILE.read_text())
        mtime = datetime.fromtimestamp(PULSE_STATE_FILE.stat().st_mtime)
        age_min = round((datetime.now() - mtime).total_seconds() / 60, 1)
        return jsonify({
            'success': True,
            'avatar': state.get('avatar', {}),
            'reports': {k: {'available': bool(v), 'age_hours': v.get('age_hours') if v else None} for k, v in state.get('reports', {}).items()},
            'healing_actions': state.get('healing_actions', []),
            'state_age_minutes': age_min,
            'stale': age_min > 1440,  # Stale if older than 24h
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/pulse/state/refresh', methods=['POST'])
def pulse_state_refresh():
    """Trigger a PULSE Tier 4 autonomous state refresh."""
    data = request.get_json(silent=True) or {}
    extra_args = []
    if data.get('dry_run', True):
        extra_args.append('--dry-run')
    result = _run_pulse_script('pulse_autonomous.py', extra_args)
    return jsonify(result)


# ============================================================
# JOURNAL & AVATAR ENDPOINTS (added 2026-02-15)
# ============================================================
JOURNAL_DIR = BASE_DIR / 'ml' / 'output' / 'journal'
AVATAR_FILE = BASE_DIR / 'ml' / 'output' / 'user_avatar.json'

@app.route('/api/journal', methods=['GET'])
def journal_list():
    """List journal entries. Optional ?date=YYYY-MM-DD for a specific entry."""
    date = request.args.get('date')
    if date:
        # Return specific entry
        json_path = JOURNAL_DIR / f"{date}.json"
        md_path = JOURNAL_DIR / f"{date}.md"
        if json_path.exists():
            try:
                return jsonify({'success': True, 'entry': json.loads(json_path.read_text())})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        elif md_path.exists():
            return jsonify({'success': True, 'entry': {'date': date, 'content': md_path.read_text(encoding='utf-8')}})
        return jsonify({'success': False, 'error': f'No journal for {date}'}), 404

    # List all entries from index
    index_path = JOURNAL_DIR / 'index.json'
    if index_path.exists():
        try:
            index = json.loads(index_path.read_text())
            return jsonify({'success': True, 'entries': index.get('entries', []), 'last_updated': index.get('last_updated')})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    return jsonify({'success': True, 'entries': [], 'note': 'No journal entries yet. Run: python scripts/auto_journal.py'})


@app.route('/api/journal/generate', methods=['POST'])
def journal_generate():
    """Generate a journal entry. Accepts JSON body with optional 'date' and 'skip_llm'."""
    data = request.get_json(silent=True) or {}
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    extra_args = ['--date', date]
    if data.get('skip_llm'):
        extra_args.append('--skip-llm')
    result = _run_pulse_script('auto_journal.py', extra_args)
    return jsonify(result)


@app.route('/api/avatar', methods=['GET'])
def avatar_profile():
    """Get the user avatar personality profile."""
    if not AVATAR_FILE.exists():
        return jsonify({'success': False, 'error': 'No avatar profile yet. Run: python scripts/avatar_extraction.py'}), 404
    try:
        avatar = json.loads(AVATAR_FILE.read_text())
        return jsonify({'success': True, 'avatar': avatar})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/avatar/generate', methods=['POST'])
def avatar_generate():
    """Generate/refresh the user avatar profile."""
    data = request.get_json(silent=True) or {}
    extra_args = ['--output', 'user_avatar']
    if data.get('skip_llm'):
        extra_args.append('--skip-llm')
    result = _run_pulse_script('avatar_extraction.py', extra_args)
    return jsonify(result)


# ============================================================
# FILESYSTEM OPERATIONS ENDPOINT (added 2025-12-29)
# ============================================================
@app.route('/api/filesystem', methods=['POST'])
def filesystem_operation():
    """Execute filesystem operations via the filesystem chip."""
    if not FILESYSTEM_TOKEN:
        return jsonify({"success": False, "error": "Filesystem API disabled. Set FAITHH_FILESYSTEM_TOKEN to enable."}), 503
    token = request.headers.get("X-FAITHH-TOKEN")
    if token != FILESYSTEM_TOKEN:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    if not FILESYSTEM_CHIP:
        return jsonify({"success": False, "error": "Filesystem chip not available"}), 503
    
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"success": False, "error": "Invalid JSON body (expected object)"}), 400
    
    # Check for natural language command
    if "command" in data:
        result = FILESYSTEM_CHIP.execute_natural(data["command"])
    else:
        # Direct action execution
        result = FILESYSTEM_CHIP.execute({
            "action": data.get("action", "status"),
            "path": data.get("path", ""),
            "dest": data.get("dest", ""),
            "content": data.get("content", ""),
            "options": data.get("options", {})
        })
    
    return jsonify({
        "success": result.success,
        "message": result.message,
        "data": result.data,
        "suggestions": result.suggestions
    })

@app.route('/api/filesystem/capabilities', methods=['GET'])
def filesystem_capabilities():
    """Get filesystem chip capabilities."""
    if not FILESYSTEM_TOKEN:
        return jsonify({"error": "Filesystem API disabled. Set FAITHH_FILESYSTEM_TOKEN to enable."}), 503
    token = request.headers.get("X-FAITHH-TOKEN")
    if token != FILESYSTEM_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    if not FILESYSTEM_CHIP:
        return jsonify({"error": "Filesystem chip not available"}), 503
    return jsonify(FILESYSTEM_CHIP.get_capabilities())

# ============================================================
# COMPASS DASHBOARD ENDPOINTS (added 2026-01-12)
# ============================================================
@app.route('/api/compass', methods=['GET'])
def compass_dashboard():
    """Return unified dashboard data from project_states.json and related files."""
    try:
        # Load project states
        project_states = {}
        if PROJECT_STATES.exists():
            with open(PROJECT_STATES, 'r') as f:
                project_states = json.load(f)

        # Load decisions log (recent 10)
        decisions = []
        if DECISIONS_LOG.exists():
            with open(DECISIONS_LOG, 'r') as f:
                decisions_data = json.load(f)
                decisions = decisions_data.get('decisions', [])[-10:]

        # Load work log if exists
        work_log = {}
        work_log_path = Path.home() / 'ai-stack' / 'work_log.json'
        if work_log_path.exists():
            with open(work_log_path, 'r') as f:
                work_log = json.load(f)

        # Calculate project health/momentum indicators
        projects_summary = []
        for key, proj in project_states.get('projects', {}).items():
            projects_summary.append({
                'id': key,
                'name': proj.get('name', key),
                'category': proj.get('category', ''),
                'status': proj.get('status', 'unknown'),
                'phase': proj.get('phase', ''),
                'phase_status': proj.get('phase_status', ''),
                'summary': proj.get('summary', ''),
                'next_steps': proj.get('next_steps', [])[:3],  # Top 3 only
                'step_count': len(proj.get('next_steps', []))
            })

        return jsonify({
            'success': True,
            'last_updated': project_states.get('last_updated', 'unknown'),
            'projects': projects_summary,
            'recent_decisions': decisions,
            'work_log': work_log,
            'services': project_states.get('services', {})
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/compass/log', methods=['POST'])
def compass_log_work():
    """Log work activity for interstitial journaling."""
    try:
        data = request.get_json()
        project = data.get('project', 'general')
        note = data.get('note', '')
        hours = data.get('hours', 0)

        # Load or create work log
        work_log_path = Path.home() / 'ai-stack' / 'work_log.json'
        work_log = {}
        if work_log_path.exists():
            with open(work_log_path, 'r') as f:
                work_log = json.load(f)

        today = datetime.now().strftime('%Y-%m-%d')
        if today not in work_log:
            work_log[today] = {'entries': [], 'totals': {}}

        # Add entry
        entry = {
            'timestamp': datetime.now().isoformat(),
            'project': project,
            'note': note,
            'hours': hours
        }
        work_log[today]['entries'].append(entry)

        # Update totals
        if project not in work_log[today]['totals']:
            work_log[today]['totals'][project] = 0
        work_log[today]['totals'][project] += hours

        # Save
        with open(work_log_path, 'w') as f:
            json.dump(work_log, f, indent=2)

        return jsonify({'success': True, 'entry': entry})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/metrics', methods=['GET'])
def faithh_metrics_prometheus():
    """Prometheus text exposition."""
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@app.route('/api/metrics', methods=['GET'])
def prometheus_metrics():
    """Prometheus-compatible metrics endpoint for monitoring (extended text format)."""
    metrics = []
    
    # --- FAITHH Backend Metrics ---
    metrics.append("# HELP faithh_up FAITHH backend is up")
    metrics.append("# TYPE faithh_up gauge")
    metrics.append("faithh_up 1")
    
    metrics.append("# HELP faithh_info FAITHH backend version info")
    metrics.append("# TYPE faithh_info gauge")
    metrics.append(f'faithh_info{{version="{BACKEND_VERSION}"}} 1')
    
    # ML Chips
    metrics.append("# HELP faithh_ml_chips_total Number of ML chips loaded")
    metrics.append("# TYPE faithh_ml_chips_total gauge")
    metrics.append(f"faithh_ml_chips_total {len(ML_CHIPS)}")
    
    # ChromaDB
    metrics.append("# HELP faithh_chromadb_connected ChromaDB connection status")
    metrics.append("# TYPE faithh_chromadb_connected gauge")
    metrics.append(f"faithh_chromadb_connected {1 if CHROMA_CONNECTED else 0}")
    
    try:
        doc_count = collection.count() if CHROMA_CONNECTED and collection else 0
        metrics.append("# HELP faithh_chromadb_documents_total Total documents in ChromaDB")
        metrics.append("# TYPE faithh_chromadb_documents_total gauge")
        metrics.append(f"faithh_chromadb_documents_total {doc_count}")
    except Exception:
        pass
    
    # Ollama
    ollama_up = 0
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
        if r.status_code == 200:
            ollama_up = 1
            model_count = len(r.json().get('models', []))
            metrics.append("# HELP faithh_ollama_models_total Number of Ollama models available")
            metrics.append("# TYPE faithh_ollama_models_total gauge")
            metrics.append(f"faithh_ollama_models_total {model_count}")
    except Exception:
        pass
    metrics.append("# HELP faithh_ollama_up Ollama service is up")
    metrics.append("# TYPE faithh_ollama_up gauge")
    metrics.append(f"faithh_ollama_up {ollama_up}")
    
    # --- PULSE Metrics ---
    pulse_state_file = BASE_DIR / "ml" / "output" / "pulse_state.json"
    pulse_schedule_file = BASE_DIR / "ml" / "output" / "pulse_schedule.json"
    
    if pulse_state_file.exists():
        try:
            with open(pulse_state_file, 'r') as f:
                pulse_state = json.load(f)
            
            avatar = pulse_state.get("avatar", {})
            mood = avatar.get("mood", "unknown")
            energy = avatar.get("energy", 0)
            alert_count = avatar.get("alert_count", 0)
            
            metrics.append("# HELP pulse_avatar_energy PULSE avatar energy level (0-1)")
            metrics.append("# TYPE pulse_avatar_energy gauge")
            metrics.append(f"pulse_avatar_energy {energy}")
            
            metrics.append("# HELP pulse_alerts_active Number of active PULSE alerts")
            metrics.append("# TYPE pulse_alerts_active gauge")
            metrics.append(f"pulse_alerts_active {alert_count}")
            
            metrics.append("# HELP pulse_avatar_mood PULSE avatar mood state")
            metrics.append("# TYPE pulse_avatar_mood gauge")
            for m in ["calm", "curious", "excited", "concerned", "alert"]:
                metrics.append(f'pulse_avatar_mood{{mood="{m}"}} {1 if mood == m else 0}')
        except Exception:
            pass
    
    if pulse_schedule_file.exists():
        try:
            with open(pulse_schedule_file, 'r') as f:
                schedule = json.load(f)
            
            last_runs = schedule.get("last_runs", {})
            run_counts = schedule.get("run_counts", {})
            
            metrics.append("# HELP pulse_sweep_runs_total Total PULSE sweep runs by tier")
            metrics.append("# TYPE pulse_sweep_runs_total counter")
            for tier, count in run_counts.items():
                metrics.append(f'pulse_sweep_runs_total{{tier="{tier}"}} {count}')
            
            metrics.append("# HELP pulse_last_sweep_timestamp Last PULSE sweep timestamp by tier")
            metrics.append("# TYPE pulse_last_sweep_timestamp gauge")
            for tier, ts in last_runs.items():
                try:
                    dt = datetime.fromisoformat(ts)
                    metrics.append(f'pulse_last_sweep_timestamp{{tier="{tier}"}} {dt.timestamp()}')
                except Exception:
                    pass
        except Exception:
            pass
    
    # --- Cache Stats ---
    try:
        cache_stats = get_cache_stats()
        metrics.append("# HELP faithh_cache_hits_total Cache hit count")
        metrics.append("# TYPE faithh_cache_hits_total counter")
        metrics.append(f"faithh_cache_hits_total {cache_stats.get('hits', 0)}")
        metrics.append("# HELP faithh_cache_misses_total Cache miss count")
        metrics.append("# TYPE faithh_cache_misses_total counter")
        metrics.append(f"faithh_cache_misses_total {cache_stats.get('misses', 0)}")
    except Exception:
        pass
    
    # --- Provider Health ---
    try:
        provider_health = get_provider_health()
        metrics.append("# HELP faithh_provider_health Provider health score (0-1)")
        metrics.append("# TYPE faithh_provider_health gauge")
        for provider, health in provider_health.items():
            score = health.get('score', 0) if isinstance(health, dict) else 0
            metrics.append(f'faithh_provider_health{{provider="{provider}"}} {score}')
    except Exception:
        pass
    
    return Response("\n".join(metrics) + "\n", mimetype="text/plain; charset=utf-8")


@app.route('/api/compass/status', methods=['GET'])
def compass_status():
    """Return compass status - alias for /api/compass for frontend compatibility."""
    return compass_dashboard()


@app.route('/api/compare', methods=['POST'])
def compare_models():
    """A/B test two models with the same query and FAITHH context.
    
    POST body:
      {
        "query": "your question here",
        "model_a": "qwen25-grounded:latest",    // optional, defaults to local default
        "model_b": "groq:llama-3.3-70b-versatile", // optional, defaults to groq
        "include_rag": true,                      // optional, include RAG context
        "n_rag_results": 3                        // optional
      }
    
    Returns both model responses, latencies, and chip activations.
    """
    import concurrent.futures
    import time as _time

    try:
        data = request.get_json() or {}
        query = data.get('query', '').strip()
        if not query:
            return jsonify({'success': False, 'error': 'query required'}), 400

        model_a = data.get('model_a', OLLAMA_DEFAULT_MODEL)
        model_b = data.get('model_b', f'groq:{GROQ_MODEL}')
        include_rag = data.get('include_rag', True)
        n_rag = data.get('n_rag_results', 3)

        # Build shared context once (RAG + chips)
        context_parts = []

        # Chip activation
        chips_fired = []
        if ML_CHIP_CENTROIDS is not None:
            chip_results = activate_ml_chips(query, top_k=3)
            chips_fired = [{'label': c.get('label', c.get('id', '')), 'score': c.get('score', 0)} for c in chip_results]

        # RAG context (shared between both models)
        rag_snippets = []
        if include_rag:
            rag_results = query_collection(query, n_results=n_rag)
            if rag_results and rag_results.get('documents'):
                docs = rag_results['documents'][0] if rag_results['documents'] else []
                metas = rag_results.get('metadatas', [[]])[0] if rag_results.get('metadatas') else []
                for doc, meta in zip(docs, metas):
                    source = (meta or {}).get('source', 'unknown')
                    rag_snippets.append(f"[{source}] {doc[:400]}")
                context_parts.append("[CTX:RELEVANT CONTEXT]\n" + "\n\n".join(rag_snippets))

        # Project state chip
        proj_ctx = get_project_state_context(query)
        if proj_ctx:
            context_parts.append(proj_ctx)

        shared_context = "\n\n".join(context_parts)

        system_prompt = get_faithh_personality()
        full_prompt = f"{shared_context}\n\n---\n\nUser: {query}" if shared_context else query

        def call_model(model_spec: str) -> dict:
            """Call a model and return response + latency."""
            t0 = _time.time()
            try:
                if model_spec.startswith('groq:'):
                    # Groq cloud model
                    groq_model = model_spec[5:]
                    if not GROQ_API_KEY:
                        return {'response': 'Groq API key not configured', 'latency_ms': 0, 'error': True}
                    headers = {
                        'Authorization': f'Bearer {GROQ_API_KEY}',
                        'Content-Type': 'application/json'
                    }
                    payload = {
                        'model': groq_model,
                        'messages': [
                            {'role': 'system', 'content': system_prompt},
                            {'role': 'user', 'content': full_prompt}
                        ],
                        'max_tokens': 4096,
                        'temperature': 0.7,
                    }
                    resp = requests.post(
                        f"{GROQ_BASE_URL}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=30
                    )
                    resp.raise_for_status()
                    text = resp.json()['choices'][0]['message']['content']
                else:
                    # Ollama local model
                    payload = {
                        'model': model_spec,
                        'prompt': full_prompt,
                        'system': system_prompt,
                        'stream': False,
                        'options': {'num_predict': 1024}
                    }
                    resp = requests.post(
                        f"{OLLAMA_HOST}/api/generate",
                        json=payload,
                        timeout=OLLAMA_READ_TIMEOUT
                    )
                    resp.raise_for_status()
                    text = resp.json().get('response', '')

                latency = round((_time.time() - t0) * 1000)
                return {'response': text, 'latency_ms': latency, 'error': False}

            except Exception as e:
                latency = round((_time.time() - t0) * 1000)
                return {'response': str(e), 'latency_ms': latency, 'error': True}

        # Run both models in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
            fut_a = ex.submit(call_model, model_a)
            fut_b = ex.submit(call_model, model_b)
            result_a = fut_a.result(timeout=120)
            result_b = fut_b.result(timeout=120)

        return jsonify({
            'success': True,
            'query': query,
            'chips_fired': chips_fired,
            'rag_snippets_used': len(rag_snippets),
            'model_a': {
                'model': model_a,
                'response': result_a['response'],
                'latency_ms': result_a['latency_ms'],
                'error': result_a['error'],
            },
            'model_b': {
                'model': model_b,
                'response': result_b['response'],
                'latency_ms': result_b['latency_ms'],
                'error': result_b['error'],
            },
            'context_preview': shared_context[:500] + ('...' if len(shared_context) > 500 else ''),
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/journal/view/<date>', methods=['GET'])
def journal_view(date):
    """View a specific journal entry as markdown."""
    try:
        journal_dir = BASE_DIR / 'ml' / 'output' / 'journal'
        md_path = journal_dir / f'{date}.md'
        
        if not md_path.exists():
            return f"# Journal Entry Not Found\n\nNo entry for {date}", 404, {'Content-Type': 'text/markdown'}
        
        content = md_path.read_text(encoding='utf-8')
        return content, 200, {'Content-Type': 'text/markdown; charset=utf-8'}
    except Exception as e:
        return f"# Error\n\n{str(e)}", 500, {'Content-Type': 'text/markdown'}


@app.route('/api/compass/refresh', methods=['POST'])
def compass_refresh():
    """Trigger collectors refresh and return updated status."""
    try:
        # Run collectors to refresh data
        from scripts.collectors.director import CompassDirector
        director = CompassDirector()
        result = director.analyze()
        
        return jsonify({
            'success': True,
            'message': 'Compass data refreshed',
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Phase 7: User Authentication Endpoints
if AUTH_ENABLED and auth_service:
    
    @app.route('/api/auth/register', methods=['POST'])
    def register_user():
        """Register a new user"""
        try:
            data = request.get_json()
            
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            role = data.get('role', 'user')
            profile = data.get('profile', {})
            
            result = auth_service.register_user(username, email, password, role, profile)
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 400
                
        except Exception as e:
            return jsonify({"success": False, "error": f"Registration failed: {str(e)}"}), 500
    
    @app.route('/api/auth/login', methods=['POST'])
    def login_user():
        """Authenticate user"""
        try:
            data = request.get_json()
            
            username = data.get('username')
            password = data.get('password')
            
            result = auth_service.authenticate_user(username, password)
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 401
                
        except Exception as e:
            return jsonify({"success": False, "error": f"Login failed: {str(e)}"}), 500
    
    @app.route('/api/auth/verify', methods=['POST'])
    def verify_token():
        """Verify JWT token"""
        try:
            data = request.get_json()
            token = data.get('token')
            
            if not token:
                return jsonify({"success": False, "error": "Token required"}), 400
            
            result = auth_service.verify_token(token)
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 401
                
        except Exception as e:
            return jsonify({"success": False, "error": f"Token verification failed: {str(e)}"}), 500
    
    @app.route('/api/auth/refresh', methods=['POST'])
    def refresh_token():
        """Refresh access token"""
        try:
            data = request.get_json()
            refresh_token = data.get('refresh_token')
            
            if not refresh_token:
                return jsonify({"success": False, "error": "Refresh token required"}), 400
            
            result = auth_service.refresh_token(refresh_token)
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 401
                
        except Exception as e:
            return jsonify({"success": False, "error": f"Token refresh failed: {str(e)}"}), 500
    
    @app.route('/api/auth/logout', methods=['POST'])
    def logout_user():
        """Logout user"""
        try:
            data = request.get_json()
            token = data.get('token')
            
            if not token:
                return jsonify({"success": False, "error": "Token required"}), 400
            
            result = auth_service.logout_user(token)
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 400
                
        except Exception as e:
            return jsonify({"success": False, "error": f"Logout failed: {str(e)}"}), 500
    
    @app.route('/api/auth/profile', methods=['GET'])
    def get_user_profile():
        """Get user profile (requires authentication)"""
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({"success": False, "error": "Authentication required"}), 401
            
            # Verify token
            token_result = auth_service.verify_token(token)
            
            if not token_result['success']:
                return jsonify(token_result), 401
            
            # Return user profile
            return jsonify({
                "success": True,
                "user": token_result['user']
            })
            
        except Exception as e:
            return jsonify({"success": False, "error": f"Profile retrieval failed: {str(e)}"}), 500
    
    @app.route('/api/auth/profile', methods=['PUT'])
    def update_user_profile():
        """Update user profile (requires authentication)"""
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({"success": False, "error": "Authentication required"}), 401
            
            # Verify token
            token_result = auth_service.verify_token(token)
            
            if not token_result['success']:
                return jsonify(token_result), 401
            
            # Update profile
            data = request.get_json()
            profile = data.get('profile', {})
            
            result = auth_service.update_user_profile(token_result['user']['user_id'], profile)
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 400
                
        except Exception as e:
            return jsonify({"success": False, "error": f"Profile update failed: {str(e)}"}), 500
    
    @app.route('/api/auth/change-password', methods=['POST'])
    def change_password():
        """Change user password (requires authentication)"""
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({"success": False, "error": "Authentication required"}), 401
            
            # Verify token
            token_result = auth_service.verify_token(token)
            
            if not token_result['success']:
                return jsonify(token_result), 401
            
            # Change password
            data = request.get_json()
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            
            result = auth_service.change_password(token_result['user']['user_id'], old_password, new_password)
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 400
                
        except Exception as e:
            return jsonify({"success": False, "error": f"Password change failed: {str(e)}"}), 500
    
    @app.route('/api/auth/users', methods=['GET'])
    def get_all_users():
        """Get all users (admin only)"""
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({"success": False, "error": "Authentication required"}), 401
            
            # Verify token
            token_result = auth_service.verify_token(token)
            
            if not token_result['success']:
                return jsonify(token_result), 401
            
            # Check if admin
            if token_result['user']['role'] != 'admin':
                return jsonify({"success": False, "error": "Admin access required"}), 403
            
            # Get all users
            result = auth_service.get_all_users(token_result['user']['user_id'])
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 400
                
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to get users: {str(e)}"}), 500
    
    @app.route('/api/auth/users/<user_id>/deactivate', methods=['POST'])
    def deactivate_user(user_id):
        """Deactivate user (admin only)"""
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({"success": False, "error": "Authentication required"}), 401
            
            # Verify token
            token_result = auth_service.verify_token(token)
            
            if not token_result['success']:
                return jsonify(token_result), 401
            
            # Check if admin
            if token_result['user']['role'] != 'admin':
                return jsonify({"success": False, "error": "Admin access required"}), 403
            
            # Deactivate user
            result = auth_service.deactivate_user(token_result['user']['user_id'], user_id)
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 400
                
        except Exception as e:
            return jsonify({"success": False, "error": f"User deactivation failed: {str(e)}"}), 500
    
    @app.route('/api/auth/statistics', methods=['GET'])
    def get_user_statistics():
        """Get user statistics (admin only)"""
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({"success": False, "error": "Authentication required"}), 401
            
            # Verify token
            token_result = auth_service.verify_token(token)
            
            if not token_result['success']:
                return jsonify(token_result), 401
            
            # Check if admin
            if token_result['user']['role'] != 'admin':
                return jsonify({"success": False, "error": "Admin access required"}), 403
            
            # Get statistics
            result = auth_service.get_user_statistics()
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 400
                
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to get statistics: {str(e)}"}), 500

    print("🔑 Authentication endpoints registered")
else:
    print("⚠️ Authentication endpoints not available")

# Phase 7: Constella Constitution Endpoints
if CONSTITUTION_ENABLED and constitution_service:
    
    @app.route('/api/constitution/summary', methods=['GET'])
    def get_constitution_summary():
        """Get constitution summary"""
        try:
            summary = constitution_service.get_constitution_summary()
            return jsonify({
                "success": True,
                "constitution": summary
            })
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to get constitution summary: {str(e)}"}), 500
    
    @app.route('/api/constitution/evaluate', methods=['POST'])
    def observe_constitutional_action():
        """Observe an action against the constitution (Civic Tome shape).

        The framework OBSERVES and records which principles an action engages; it does not rule
        compliance and returns no verdict. Consequence decisions are delegated to an
        external/human process. (Route path kept for back-compat.)
        """
        try:
            data = request.get_json()
            action = data.get("action", {})
            domain = data.get("domain", "general")

            observation = constitution_service.observe_action(action, domain)

            return jsonify({
                "success": True,
                "observation": {
                    "action_id": observation.action_id,
                    "condition": observation.condition,
                    "measures": observation.measures,
                    "context": observation.context,
                    "scope": observation.scope,
                    "provenance": observation.provenance,
                    "resolution": observation.resolution,
                    "engaged_principles": observation.engaged_principles,
                    "claim_label": observation.claim_label.value,
                    "observation_timestamp": observation.observation_timestamp.isoformat()
                }
            })
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to record observation: {str(e)}"}), 500
    
    @app.route('/api/constitution/principles', methods=['GET'])
    def get_constitution_principles():
        """Get applicable principles for domain"""
        try:
            domain = request.args.get("domain", "general")
            principles = constitution_service.get_applicable_principles(domain)
            
            return jsonify({
                "success": True,
                "domain": domain,
                "principles": [
                    {
                        "id": p.id,
                        "title": p.title,
                        "description": p.description,
                        "principle_type": p.principle_type.value,
                        "source": p.source,
                        "weight": p.weight,
                        "domain_applicability": p.domain_applicability,
                        "keywords": p.keywords
                    }
                    for p in principles
                ]
            })
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to get principles: {str(e)}"}), 500

    @app.route('/api/constitution/update-modern-rights', methods=['POST'])
    def update_modern_rights():
        """Update modern rights from human rights APIs"""
        try:
            update_results = constitution_service.update_modern_rights_from_apis()
            
            return jsonify({
                "success": update_results["success"],
                "updated_sources": update_results["updated_sources"],
                "failed_sources": update_results["failed_sources"],
                "new_principles": update_results["new_principles"],
                "errors": update_results["errors"],
                "message": f"Updated {len(update_results['updated_sources'])} sources with {len(update_results['new_principles'])} new principles"
            })
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to update modern rights: {str(e)}"}), 500

    print("🌍 Constitution endpoints registered")
else:
    print("⚠️ Constitution endpoints not available")

# Phase 7: Focus Management Endpoints
if FOCUS_ENABLED and focus_service:
    
    @app.route('/api/focus/capture-concept', methods=['POST'])
    def capture_concept():
        """Capture a new concept"""
        try:
            data = request.get_json()
            raw_idea = data.get("raw_idea", "")
            context = data.get("context", {})
            
            if not raw_idea:
                return jsonify({"success": False, "error": "Raw idea is required"}), 400
            
            concept = focus_service.capture_concept(raw_idea, context)
            
            return jsonify({
                "success": True,
                "concept": {
                    "id": concept.id,
                    "title": concept.title,
                    "description": concept.description,
                    "domain": concept.domain,
                    "tags": concept.tags,
                    "state": concept.state.value,
                    "priority": concept.priority.value,
                    "capture_timestamp": concept.capture_timestamp.isoformat(),
                    "evaluation_score": concept.evaluation_score,
                    "strategic_alignment": concept.strategic_alignment,
                    "completion_probability": concept.completion_probability,
                    "impact_potential": concept.impact_potential,
                    "constitutional_feasibility": concept.constitutional_feasibility.value
                }
            })
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to capture concept: {str(e)}"}), 500
    
    @app.route('/api/focus/concepts', methods=['GET'])
    def get_concepts():
        """Get concepts by state"""
        try:
            state_filter = request.args.get("state")
            
            if state_filter:
                try:
                    state_enum = ConceptState(state_filter)
                    concepts = [focus_service.concepts[cid] for cid in focus_service.concept_states[state_enum]]
                except ValueError:
                    return jsonify({"success": False, "error": f"Invalid state: {state_filter}"}), 400
            else:
                concepts = list(focus_service.concepts.values())
            
            return jsonify({
                "success": True,
                "concepts": [
                    {
                        "id": c.id,
                        "title": c.title,
                        "description": c.description,
                        "domain": c.domain,
                        "tags": c.tags,
                        "state": c.state.value,
                        "priority": c.priority.value,
                        "capture_timestamp": c.capture_timestamp.isoformat(),
                        "evaluation_score": c.evaluation_score,
                        "strategic_alignment": c.strategic_alignment,
                        "completion_probability": c.completion_probability,
                        "impact_potential": c.impact_potential,
                        "constitutional_feasibility": c.constitutional_feasibility.value,
                        "progress_percentage": c.progress_percentage,
                        "last_activity": c.last_activity.isoformat()
                    }
                    for c in concepts
                ]
            })
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to get concepts: {str(e)}"}), 500
    
    @app.route('/api/focus/pipeline', methods=['GET'])
    def get_concept_pipeline():
        """Get concept pipeline by state"""
        try:
            pipeline = focus_service.get_concept_pipeline()
            
            return jsonify({
                "success": True,
                "pipeline": {
                    state: [
                        {
                            "id": c.id,
                            "title": c.title,
                            "domain": c.domain,
                            "priority": c.priority.value,
                            "evaluation_score": c.evaluation_score,
                            "progress_percentage": c.progress_percentage
                        }
                        for c in concepts
                    ]
                    for state, concepts in pipeline.items()
                }
            })
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to get pipeline: {str(e)}"}), 500
    
    @app.route('/api/focus/health', methods=['GET'])
    def get_focus_health():
        """Get focus health metrics"""
        try:
            health = focus_service.get_focus_health()
            metrics = focus_service.get_focus_metrics()
            drift_indicators = focus_service.detect_focus_drift()
            
            return jsonify({
                "success": True,
                "focus_health": {
                    "status": health.value,
                    "active_concepts": metrics["active_concepts"],
                    "completed_concepts": metrics["completed_concepts"],
                    "total_concepts": metrics["total_concepts"],
                    "drift_score": drift_indicators["drift_score"],
                    "drift_severity": drift_indicators["severity"],
                    "drift_indicators": drift_indicators["indicators"]
                }
            })
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to get focus health: {str(e)}"}), 500
    
    @app.route('/api/focus/active-concepts', methods=['GET'])
    def get_active_concepts():
        """Get currently active concepts"""
        try:
            active_concepts = focus_service.get_active_concepts()
            
            return jsonify({
                "success": True,
                "active_concepts": [
                    {
                        "id": c.id,
                        "title": c.title,
                        "description": c.description,
                        "domain": c.domain,
                        "priority": c.priority.value,
                        "progress_percentage": c.progress_percentage,
                        "last_activity": c.last_activity.isoformat(),
                        "estimated_completion": c.estimated_completion.isoformat() if c.estimated_completion else None
                    }
                    for c in active_concepts
                ]
            })
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to get active concepts: {str(e)}"}), 500

    print("🧠 Focus management endpoints registered")
else:
    print("⚠️ Focus management endpoints not available")


@app.route('/images/chips/<path:filename>')
def serve_chip_image(filename):
    """Serve chip images for Rainmeter skin."""
    return send_from_directory(BASE_DIR / 'images' / 'chips', filename)

if __name__ == '__main__':
    print("=" * 60)
    print(f"FAITHH PROFESSIONAL BACKEND {BACKEND_VERSION}")
    print("=" * 60)
    print(f"✅ Self-awareness boost (faithh_memory.json)")
    print(f"✅ Decision citation (decisions_log.json)")
    print(f"✅ Project state awareness (project_states.json)")
    print(f"✅ Scaffolding awareness (scaffolding_state.json)")
    print(f"✅ Smart intent detection + integrated context building")
    print(f"✅ ML chips: {len(ML_CHIPS)} loaded, cosine routing")
    print(f"✅ PULSE Reflection Engine: 3 tiers (staleness, divergence, branches)")
    print(f"{'✅' if FILESYSTEM_CHIP else '⚠️'} Filesystem chip: {'loaded' if FILESYSTEM_CHIP else 'not available'}")
    print(f"{'✅' if KNOWLEDGE_GRAPH else '⚠️'} Knowledge graph: {'loaded' if KNOWLEDGE_GRAPH else 'not available'}")
    print(f"{'✅' if GENOMIC_ENABLED else '⚠️'} Genomic impedance services: {'loaded' if GENOMIC_ENABLED else 'not available'}")
    print(f"{'✅' if AUTH_ENABLED else '⚠️'} User authentication: {'loaded' if AUTH_ENABLED else 'not available'}")
    print(f"{'✅' if CONSTITUTION_ENABLED else '⚠️'} Constella Constitution: {'loaded' if CONSTITUTION_ENABLED else 'not available'}")
    print(f"{'✅' if FOCUS_ENABLED else '⚠️'} Focus management: {'loaded' if FOCUS_ENABLED else 'not available'}")
    print("=" * 60)
    print(f"Starting on http://localhost:5557")
    
    debug_enabled = os.environ.get("FAITHH_DEBUG", "0") == "1"
    app.run(host='0.0.0.0', port=5557, debug=debug_enabled, use_reloader=debug_enabled, threaded=True)

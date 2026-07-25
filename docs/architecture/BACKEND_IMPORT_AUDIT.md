# Backend import audit (canonical server)

**Scope:** `faithh_professional_backend_fixed.py` (Flask app on port 5557 per `AGENTS.md`).  
**Date:** 2026-03-30 (Option C follow-up; updated with consolidation pass).

---

## Why this document exists

Imports are the dependency graph at startup. This audit lists what the canonical backend loads, flags naming collisions and optional paths, and records consolidation candidates without requiring an immediate refactor.

---

## Standard library and third-party (top of file)

| Category | Modules |
|----------|---------|
| Flask / WSGI | `flask`, `flask_cors`, `werkzeug.utils` |
| HTTP / URL | `requests`, `urllib.parse` |
| Runtime | `json`, `os`, `sys`, `pathlib`, `subprocess`, `threading`, `queue`, `logging`, `time`, `random`, `re`, `mimetypes`, `concurrent.futures`, `datetime` |
| Config / data | `dotenv`, `chromadb`, `chromadb.utils.embedding_functions` |
| Numeric | `numpy` |
| System | `psutil` (GPU/gaming-aware model selection) |

---

## `backend.*` (always loaded if import succeeds)

| Module | Role |
|--------|------|
| `security_middleware` | Security middleware, `require_security` |
| `connection_monitor` | Phase 4 service health / fallbacks (`connection_monitor`, `create_health_endpoint`) |
| `cache` | Response cache middleware |
| `performance` | Request performance tracking |
| `local_optimization` | Model selection hints |
| `enhanced_chip_integration` | Program Advances, merge/fusion |
| `program_advance_optimizer` | PA optimizer |
| `advanced_analytics_simple` | Analytics |
| `ai_driven_ux` | UX adaptation |
| `coherence_arbiter` | Coherence arbiter |
| `data_loaders` | JSON state I/O |
| `intent_detection` | `detect_query_intent` |
| `performance_monitor` | Provider performance |
| `response_cache` | Alternate response cache helpers |
| `ml_learning_framework` | ML framework accessor |
| `ui_layout_optimizer` | UI interaction recording |
| `context_builders` | Personality, project snapshot, Constella snippets |

### `backend.ml.*` (optional — wrapped in try/except)

`performance_tracker`, `weight_optimizer`, `semantic_intent_detector` — if import fails, `PHASE2_ENABLED = False`.

---

## `app.services.*` (optional — each wrapped in try/except)

| Module | Flag |
|--------|------|
| `parasitic_alife_service_fixed` | Always imported (hard dependency for genomic path) |
| `universal_impedance_field_optimized` | Always imported |
| `cosmic_ripple_integration` | Always imported |
| `genomic_impedance_sensor`, `genomic_biasing_engine_fixed` | `GENOMIC_ENABLED` |
| `user_authentication_service` | `AUTH_ENABLED` |
| `constella_constitution` | `CONSTITUTION_ENABLED` |
| `focus_management` | `FOCUS_ENABLED` |

Legacy duplicates (not imported by canonical backend): `parasitic_alife_service.py`, `universal_impedance_field.py`, `alife_parasitic_integration*.py` — kept in tree for reference; canonical paths use `*_fixed` / `*_optimized` as above.

---

## Root-level modules (same directory as backend file)

| Module | Notes |
|--------|------|
| `pulse_pattern_tracker` | Imported inside a function (lazy) |
| `google_search` | Optional; `GOOGLE_SEARCH_AVAILABLE` |

---

## `scripts.security`

`get_scanner`, `scan_input`, `scan_output`, `PulseSelfHealer`, `get_audit_logger` — loaded at module level.

---

## Inline / lazy imports (grep targets for refactors)

| Location (approx.) | Import |
|--------------------|--------|
| Request path | `from pulse_pattern_tracker import pulse_tracker` |
| ~1816 | `from backend.context_builders import get_constella_enhanced_context` |
| ~1828 | `from backend.ml.performance_tracker import ...` (duplicate of optional top-level Phase 2) |
| ~1997 | `from backend.context_builders import enhance_response_with_constella` |
| `monitoring_services` | `from backend.llm_providers import connection_monitor as provider_health` |
| `enhanced_monitoring` | `enhanced_service_monitor` + `sys.path.append('.')` |

Lazy imports reduce cold start or avoid cycles; they also make static analysis harder. Any consolidation should preserve behavior and test `/api/monitoring/*`.

---

## Critical finding: two different `connection_monitor` symbols

1. **`backend.connection_monitor`** — module-level `connection_monitor` instance: full service health model (status enums, fallbacks, URLs).
2. **`backend.llm_providers.connection_monitor`** — separate small `ConnectionMonitor` class instance used for Groq/Anthropic/Ollama/Chroma quick checks.

The global name collision was confusing. A unified delegate now exists in `backend/health_monitor_facade.py`, and `/api/monitoring/services` uses that facade to combine provider checks with system-level summary.

**Future consolidation (optional):** Rename `backend.llm_providers.connection_monitor` to `llm_provider_health_monitor` in-place and keep `connection_monitor` as backwards-compatible alias.

---

## Hygiene fixes applied (2026-03-30)

- Removed duplicate `import sys` at the top of `faithh_professional_backend_fixed.py`.
- Clarified provider/system monitor separation in `monitoring_services` and moved checks behind `health_monitor_facade`.
- Added `backend/health_monitor_facade.py` and switched `/api/monitoring/services` to facade-backed checks.
- Added compatibility functions in `backend/context_builders.py` and removed failing lazy import paths in the chat route.

---

## Verification

```bash
python3 -m py_compile faithh_professional_backend_fixed.py
```

---

## Out of scope (this pass)

- Archived backends under `archive/legacy/` (dozens of variants).
- Whether `enhanced_service_monitor` exists on all deployments (`enhanced_monitoring` catches `ImportError`).
- Full migration of inline imports to top-of-file (team style + cycle analysis).

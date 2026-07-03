# FAITHH Backend Audit — 2026-07-02
Phase 1 deliverable (REPO_GATES). Static analysis only — the runtime lives on the
faithh VM (offline). Every finding here is `confirmed` from the source tree; nothing
required a live box. Companion to the forthcoming target spec.

## The shape of it
- `faithh_professional_backend_fixed.py` — **6,634 lines, 108 routes, 140 functions,
  0 classes.** One file. 96 of 108 routes are under `/api/`.
- A `backend/` package of **40 modules (~16,000 lines)** sits alongside it.
- Launch: `restart_backend.sh` → tmux → `python3 faithh_professional_backend_fixed.py`
  on :5557 (gunicorn referenced as an alt). Single-process Flask, `threaded=True`.

## Finding 1 — the modularization is REAL and already load-bearing
This is the important correction to "monolith vs. an abandoned attempt": the monolith
**actively imports 23 backend modules**, and 24 are transitively live. `llm_providers`
(1,471L), `context_builders` (763L), `session_metrics` (708L), `enhanced_chip_integration`
(702L), `local_optimization` (748L) are all wired in. The refactor is ~60% done already —
you extracted the heavy subsystems and left the orchestration in the monolith.

## Finding 2 — 16 of 40 backend modules are ORPHANS (not reachable from the running backend)
Dead-or-disconnected, by AST import graph:
```
advanced_analytics (571L)      ← superseded by advanced_analytics_simple (live)
coherence_sensor (329L)        ← superseded by coherence_arbiter (live)
tiered_rag_processor (309L)    ← superseded by rag_processor (live)
rag_api (94L)
parallel_chip_engine (774L)    ← NYE "parallel chip retrieval" work — verify vs live path
integrate_program_advances (274L)
plc_state_manager (313L)
4× backend variants: faithh_backend_adapter / _v4_template / _enhanced_backend /
   _unified_api (1,558L total) ← earlier whole-backend attempts, dead ends
tool_system (669L) + tool_executor (228L) + tool_registry (138L) + security_manager (146L)
```

## Finding 3 — an entire TOOL-CALLING subsystem is built but UNWIRED
`tool_system` / `tool_registry` / `tool_executor` form a complete tool-execution feature
(built Nov 2025 per git — "implement Tool System for local AI agent"). **The monolith
references it 0 times.** It's orphaned as a cluster that only imports itself. Decision
needed: rewire it (tool-calling is table stakes at current standard, and vLLM/qwen3-coder
supports it) or archive it. This is the single biggest capability gap between FAITHH-as-is
and FAITHH-as-imagined.

## Finding 4 — the `chat()` function is the monolith inside the monolith
- `chat()` = **1,100 lines** (L2272–3372). Next largest: `compass_refresh` 544L,
  `smart_rag_query` 238L, `build_integrated_context` 219L.
- The whole request lifecycle — intent detection, RAG, chip/PULSE selection, provider
  routing, streaming, metrics — is inlined in one function. This is the refactor's
  center of gravity: everything else is extractable once `chat()` is decomposed.

## Finding 5 — provider reality vs. the docs
Mention counts in the monolith: Ollama 151, anthropic 81, Groq 63, **vLLM 1**. vLLM is
named as primary in SYSTEMS_MAP but the monolith barely touches it directly — provider
selection is delegated to `llm_providers.py` (1,471L) and `select_gpu_aware_model()`
(153L). Verify the live routing order when Gen8 returns; the doc/code emphasis disagree.

## Finding 6 — structural smells (refactor targets, not bugs)
- **148 `except Exception` + 7 bare `except:`** — errors are broadly swallowed; hard to
  see real failures (this is likely why RAG bugs went undiagnosed for weeks).
- **59 module-level globals** — shared mutable state across 108 routes; the main
  obstacle to testability and to splitting the file.
- 51 `os.getenv` calls scattered inline — no central config object.
- A stray `faithh_professional_backend_fixed.backup_20251229_013848.py` (1,256L) in repo root.

## What's blocked by Gen8 being offline (and what ISN'T)
- **NOT blocked** (all of Phase 1): this audit, the target spec, dead-code decisions,
  the chat() decomposition plan, tool-system rewire-or-archive call, config centralization
  design. Months of design work need no live box.
- **Blocked** (Phase 2): confirming live provider order, RAG retrieval quality, whether
  orphans are truly dead vs. loaded dynamically, KB ingest, any refactor that must be
  runtime-tested. Don't delete an orphan until the live system confirms it's unused.

## Recommended Phase-1 next steps
1. Write the target architecture spec (module boundaries; `chat()` → pipeline stages).
2. Decide tool-system: rewire vs. archive (Finding 3).
3. Draft the dead-code removal list — stage it, don't execute until Gen8 verifies.
4. Design a central config + a narrower exception strategy for the rewrite.

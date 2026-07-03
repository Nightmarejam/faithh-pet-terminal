# FAITHH Capability Map — concepts ↔ code reconciliation
Phase 1, part 2 (follows BACKEND_AUDIT_2026-07-02.md). Static-only; `confirmed` from
the tree. Answers: what do the live modules actually own, and which documented concepts
have no home yet? This is the backbone of the target architecture spec.

## Every named concept, and its real state
Four states: **LIVE** (module, wired) · **ORPHAN** (module exists, not reachable) ·
**INLINE** (built but buried in the monolith — needs extraction, not creation) ·
**UNBUILT** (documented, no implementation).

| Concept | Doc weight | State | Where it actually is |
|---|---|---|---|
| PULSE engine (3-tier) | 1017 | **INLINE** | ~194 refs inside the monolith (`chat()`, `compass_refresh`, `build_faithh_status_payload`) — no module. Highest-value extraction target. |
| Battle chips / synthesis | 159 | **LIVE** | `enhanced_chip_integration`, `chip_weight_metrics`, `program_advance_optimizer` (+ orphan `parallel_chip_engine` — the NYE parallel-retrieval work, never wired) |
| Program Advance | 234 | **LIVE + dup** | `program_advance_optimizer` (live) vs `integrate_program_advances` (orphan) — pick one |
| Coherence Arbiter | 38 | **LIVE** | `coherence_arbiter.py` (RAG↔chip convergence) — clean, already modular |
| Compass | 574 | **INLINE** | `compass_refresh()` = 544 lines in the monolith. Big, self-contained → extract to a module nearly as-is |
| Anchor validation | 23 | **ORPHAN** | `anchor_validator.py` exists, not reachable — verify vs. whatever the live path uses |
| Memory (hot/warm/cold) | 105 | **INLINE** | `faithh_memory.json` + ChromaDB reads scattered in monolith; no memory module owns the tiering |
| Tool calling / agent | 63 | **ORPHAN** | `tool_system`+`tool_registry`+`tool_executor` built, 0 refs from monolith (Audit Finding 3) |
| Confirmability tiers | 1101 | **UNBUILT** in FAITHH | Canonical in Constella; **no FAITHH code tags responses confirmed/asserted/speculative.** The most-documented concept with zero backend enforcement. |
| IME (resonance gating) | 72/26 | **SEPARATE** | `ime/` C++ scaffold (CMake, "4 tests passing") — not python; integration path into chat undefined |
| Journal synthesis | 9 | **UNBUILT** | SYSTEMS_MAP marks "pending" — no implementation |
| Proof-of-Life / node health | 23 | **UNBUILT** in FAITHH | telemetry exists (gpu_telemetry CSV, SensorBridge :9998) but nothing feeds it into FAITHH as a health signal |
| Harmony-AI resonance transformer | 24 | **UNBUILT** | spec only (constella harmony/) — design, not code |
| PLC state manager | — | **ORPHAN** | `plc_state_manager.py` (deterministic state machine w/ interlocks) — built, unwired. Distinct from PULSE despite the name. |

## What the live modules own (target module groups)
The 24 live modules already cluster into clean domains — the target architecture is
mostly *naming what exists* plus extracting the inline concepts:
- **Providers**: `llm_providers` (1471L), `anthropic_shim`, `performance_monitor`,
  `select_gpu_aware_model()` (inline) → one `providers/` package
- **RAG**: `rag_processor`, `coherence_arbiter`, `context_builders`, `data_loaders`,
  `intent_detection` → `rag/` (this is where confirmability tagging should hook in)
- **Chips/PULSE**: `enhanced_chip_integration`, `program_advance_optimizer`,
  `chip_weight_metrics` + **extracted PULSE** + **extracted Compass** → `pulse/`
- **Learning/UX**: `ml_learning_framework`, `ui_layout_optimizer`, `ai_driven_ux`,
  `local_optimization` → `adaptive/`
- **Ops**: `cache`/`response_cache` (dedupe these two), `performance`, `session_metrics`,
  `connection_monitor`, `health_monitor_facade`, `security_middleware` → `ops/`
- **Orchestration**: the decomposed `chat()` → a thin `pipeline/` calling the above

## The missing-concepts list (documented but unfulfilled)
Ranked by leverage for the FAITHH-first goal:
1. **Confirmability enforcement in RAG/responses** — the flagship's honesty feature,
   fully specced, unbuilt. Tag every retrieved fact + response with a tier. This is the
   demo differentiator ("an AI that shows its receipts") AND it dogfoods Constella.
2. **Tool calling rewired** — table-stakes capability, already built, just unplugged.
3. **PULSE + Compass extracted from the monolith** — not new features; making the
   flagship's signature systems legible/testable so others can contribute to them.
4. **Node-health / Proof-of-Life feed** — the data exists; wire it in (Gen8-gated).
5. **Journal synthesis** — smallest, genuinely unbuilt; defer unless it earns priority.

## Gate note
Everything above is design/decision work — no Gen8 needed. The one caution repeats:
don't delete orphans or dedupe (cache/response_cache, the two Program Advance modules)
until the live system confirms which is actually loaded.

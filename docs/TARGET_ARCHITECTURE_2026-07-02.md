# FAITHH Target Architecture — the spec
Phase 1 closer. Follows BACKEND_AUDIT + CAPABILITY_MAP + ATTESTATION_CONCEPT.
Design only; static-derived. This is the blueprint the refactor follows — and the gate
that unblocks Phase 3 code work. Nothing here executes against the offline stack.

## Principle
Don't rebuild — **name what exists, extract what's inline, reconnect what's orphaned,
delete what's dead.** The audit showed ~60% is already modular. The target is the
monolith's `chat()` becoming a thin pipeline over six packages that mostly already exist.

## Target layout
```
faithh/
  pipeline/      # the decomposed chat() — orchestration only, calls the packages
  providers/     # llm_providers, anthropic_shim, performance_monitor, select_gpu_aware_model
  rag/           # rag_processor, coherence_arbiter, context_builders, data_loaders,
                 #   intent_detection  + NEW: attestation (source tiers, corroboration)
  pulse/         # enhanced_chip_integration, program_advance_optimizer, chip_weight_metrics
                 #   + EXTRACTED: PULSE engine, Compass (from the monolith)
  adaptive/      # ml_learning_framework, ui_layout_optimizer, ai_driven_ux, local_optimization
                 #   (this is Harmony's "return loop" — name it the adaptive layer)
  ops/           # cache (dedupe w/ response_cache), performance, session_metrics,
                 #   connection_monitor, health_monitor_facade, security_middleware
  agency/        # REWIRED: tool_system, tool_registry, tool_executor (currently orphaned)
  config.py      # NEW: central config — replaces 51 scattered os.getenv calls
  app.py         # Flask app + route registration (thin)
```

## The chat() decomposition (the center of gravity)
The 1,100-line `chat()` becomes an explicit, testable pipeline. Each stage is already
a module or an inline block to extract:
```
request → [intent]      intent_detection        → detect query type
        → [retrieve]    rag/ + attestation       → RAG hits, each with a source tier
        → [route]       pulse/ (chips, PA)        → chip activations
        → [corroborate] coherence_arbiter         → convergence score → claim tiers
        → [act]         agency/ (if tools needed)  → tool calls  ◄ NEW capability
        → [generate]    providers/                 → LLM response
        → [attest]      attestation                → tag response, attach receipts footer
        → [adapt]       adaptive/                  → update learning windows
        → [record]      ops/session_metrics        → telemetry
        → response (with inline tiers + receipts)
```
Every arrow is a seam that can be unit-tested in isolation — the thing the monolith's
59 globals + 148 broad excepts currently make impossible.

## Migration order (safe, incremental — each step shippable)
1. **`config.py` first** — centralize the 51 getenvs. Low risk, unblocks testability.
2. **Extract PULSE + Compass** into `pulse/` — biggest legibility win, pure move.
3. **Decompose `chat()`** stage by stage into `pipeline/`, calling existing modules.
4. **Add `attestation`** in `rag/` — the net-new concept (source tiers → corroboration
   → attested responses). The flagship differentiator.
5. **Rewire `agency/`** — reconnect the orphaned tool system.
6. **Dedupe & delete** — cache/response_cache, the two Program Advance modules, the 16
   orphans — ONLY after the live system confirms which is loaded (Gen8-gated).
7. **Narrow exceptions** — replace blanket `except Exception` with specific handling as
   each stage is extracted (this is what let the RAG bug hide).

## What's gated on Gen8 vs. not
- **Not gated (do now):** config.py, the PULSE/Compass extraction plan, the attestation
  design, writing the pipeline seams as spec, the tool-rewire design. Steps 1–5 can be
  *written and unit-tested locally* against a minimal stub stack.
- **Gated:** step 6 (deletions need live confirmation), any change requiring the real
  ChromaDB/vLLM, and final integration testing.

## Definition of done for Phase 1
This doc + the audit + the capability map + the attestation concept = the complete
design set. Phase 1 is **DONE** on commit. Phase 3 (the actual refactor) begins with
step 1 above and does not require Gen8 to start.

## Open decisions for Jonathan
- Adopt "attestation" as the repo-wide concept name? (cascades into rag/attestation)
- Rewire vs. archive the tool system? (recommend rewire — it's the agency/action limb)
- `local_optimization` (748L) — read it to decide if it's a concept or a grab-bag
  before assigning it to `adaptive/` or `ops/`.

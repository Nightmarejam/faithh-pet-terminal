# FAITHH Documentation Index

**Last Updated:** 2026-03-30

This is the master index for all FAITHH project documentation. Every document lives in a categorized subfolder. If a document isn't listed here, it's in `archive/` and considered stale.

---

## architecture/ — How the system works

| Document | Description |
|----------|-------------|
| [SYSTEM_OVERVIEW.md](architecture/SYSTEM_OVERVIEW.md) | Full system architecture, memory model, request flow, ML pipeline |
| [BACKEND_API.md](architecture/BACKEND_API.md) | API endpoints, backend modules, token budgets, management commands |
| [BACKEND_STRUCTURE_OVERVIEW.md](architecture/BACKEND_STRUCTURE_OVERVIEW.md) | Canonical backend file graph, request flow, and “Logic for Humans” comment map |
| [FAITHH_UI_COMPONENT_MAP.md](architecture/FAITHH_UI_COMPONENT_MAP.md) | `faithh_pet_v4.html` → `/api/*` → context chips → GPU (Ollama) path |
| [ECOSYSTEM_METRICS.md](architecture/ECOSYSTEM_METRICS.md) | Metric tiers (dependency vs app vs client), baseline probe command, repeatability |
| [BACKEND_IMPORT_AUDIT.md](architecture/BACKEND_IMPORT_AUDIT.md) | Canonical backend import graph, optional paths, `connection_monitor` note |
| [PHASE1_TRANSPARENCY_AUDIT_2026_03_30.md](architecture/PHASE1_TRANSPARENCY_AUDIT_2026_03_30.md) | Read-only transparency audit across WSL2/Windows, Gen8, NAS, and indexing state |
| [SYSTEM_TRANSPARENCY_FOLLOWUP_2026_03_30.md](architecture/SYSTEM_TRANSPARENCY_FOLLOWUP_2026_03_30.md) | Actionable follow-up plan from the full system audit |
| [INFRASTRUCTURE.md](architecture/INFRASTRUCTURE.md) | Hardware, GPUs, Docker, Gen8 server, Ollama models, network access |
| **NEW** [SYSTEM_SELF_AWARENESS.md](architecture/SYSTEM_SELF_AWARENESS.md) | FAITHH's self-awareness capabilities and reference patterns |
| **NEW** [FAITHH_USAGE_REDUNDANCY_AUDIT_2026-04-05.md](architecture/FAITHH_USAGE_REDUNDANCY_AUDIT_2026-04-05.md) | Used vs redundant surfaces, endpoint usage snapshot, and consolidation priorities |
| [RELEVANCY_REPORT.md](RELEVANCY_REPORT.md) | Nightmarejam org vs local tree, root file status, Canvas / floating routes, unification phases (2026-04-07) |
| [GITHUB_CANVAS_SYNC_2026-04-07.md](architecture/GITHUB_CANVAS_SYNC_2026-04-07.md) | faithh-pet-terminal delta, submodule commands, runbook nested-clone fix |

## guides/ — How to do things

| Document | Description |
|----------|-------------|
| [QUICKSTART.md](guides/QUICKSTART.md) | Getting started with FAITHH |
| [FAITHH_OPERATOR_CONTRACT.md](guides/FAITHH_OPERATOR_CONTRACT.md) | Evidence-only reporting: git commits, latency, silos (scaffolding vs live state vs RAG), raw JSON fields, knowledge horizon |
| [GIT_WORKFLOW.md](guides/GIT_WORKFLOW.md) | Git practices + commit instructions |
| [IMAGE_GENERATION.md](guides/IMAGE_GENERATION.md) | ComfyUI, Stable Diffusion, LoRA training |
| [OLLAMA_KV_ENV.md](guides/OLLAMA_KV_ENV.md) | Ollama `OLLAMA_KV_CACHE_TYPE` + flash attention (WSL/systemd/Windows) |
| [SSH_AND_NETWORKING.md](guides/SSH_AND_NETWORKING.md) | SSH setup, Tailscale, Gen8 access, Gitea |
| [DIAGNOSTICS.md](guides/DIAGNOSTICS.md) | Troubleshooting checklist |
| [PERFORMANCE_BASELINE_CYCLE.md](guides/PERFORMANCE_BASELINE_CYCLE.md) | CLI vs API vs UI latency; `scripts/benchmark_baseline.py`, emergency recovery |
| [IDEA_TRIAGE.md](guides/IDEA_TRIAGE.md) | Rank ideas into NOW/NEXT/ARCHIVE to keep focus |
| **NEW** [SERVICE_MONITORING.md](guides/SERVICE_MONITORING.md) | Monitoring system health and performance |
| **NEW** [QUALITY_TRACKING.md](guides/QUALITY_TRACKING.md) | Response quality monitoring and optimization |
| [FINANCIAL_DATA_INTAKE.md](guides/FINANCIAL_DATA_INTAKE.md) | AI-assisted partnership financial intake; `prompts/financial_intake_v1.txt`, session checklist |
| [COCKPIT_DEPENDENCY_RUNBOOK.md](guides/COCKPIT_DEPENDENCY_RUNBOOK.md) | Cockpit dependency smoke tests and consolidation sequence |
| [NAS_NODE_EXPORTER.md](guides/NAS_NODE_EXPORTER.md) | Synology NAS `node_exporter` (:9100), DSM UI, Prometheus `job=nas` |

## reference/ — Facts and inventories

| Document | Description |
|----------|-------------|
| [CONSTELLA.md](reference/CONSTELLA.md) | Constella civic framework master reference *(+5 distilled strategic insights)* |
| [LIFE_MAP.md](reference/LIFE_MAP.md) | Personal context, life events, direction *(+3 personal frameworks)* |
| [HARDWARE_INVENTORY.md](reference/HARDWARE_INVENTORY.md) | All hardware and peripherals |
| [MODEL_INVENTORY.md](reference/MODEL_INVENTORY.md) | LLM models + recommendations |
| [BATTLE_CHIP_PROMPTS.md](reference/BATTLE_CHIP_PROMPTS.md) | MMBN chip art generation prompts |
| [IDEA_VAULT.md](reference/IDEA_VAULT.md) | Future ideas and concepts *(+15 distilled novel ideas)* |
| **NEW** [PROJECT_SUMMARIES.md](reference/PROJECT_SUMMARIES.md) | Current project states and summaries |

## business/ — Business and financial

| Document | Description |
|----------|-------------|
| [PORTFOLIO_OVERVIEW.md](business/PORTFOLIO_OVERVIEW.md) | Constella, Tom Cat Sound, FAITHH overview *(+Neural Studio, Audio Streaming)* |
| [TAX_GUIDE.md](business/TAX_GUIDE.md) | Multi-member LLC tax guide |
| [TOMCAT_DASHBOARD.md](business/TOMCAT_DASHBOARD.md) | Business health dashboard concept |

## research/ — Research findings

| Document | Description |
|----------|-------------|
| [CHIP_SYNERGY.md](research/CHIP_SYNERGY.md) | Chip synergy research (consolidated) |
| [AI_CONTEXT_INJECTION.md](research/AI_CONTEXT_INJECTION.md) | Cross-session context injection research |
| [PULSE_IMMUNE_SYSTEM.md](research/PULSE_IMMUNE_SYSTEM.md) | AI immune system / self-healing research |
| [LOCAL_LLM_GUIDE.md](research/LOCAL_LLM_GUIDE.md) | RTX 3090 local LLM model guide |
| [CHAT_UX_BEST_PRACTICES.md](research/CHAT_UX_BEST_PRACTICES.md) | Modern chat interface design patterns |
| [CHAT_UX_RESEARCH.md](research/CHAT_UX_RESEARCH.md) | Claude vs Windsurf chat UX analysis |
| [PROJECT_DASHBOARD_DESIGN.md](research/PROJECT_DASHBOARD_DESIGN.md) | Dashboard design for interconnected projects |
| [HARMONY_INSIGHTS.md](research/HARMONY_INSIGHTS.md) | Harmony Framework distilled findings (8 biomechanical resonance insights) |
| [EVOLUTIONARY_RESONANCE_CONVERSATION.md](research/EVOLUTIONARY_RESONANCE_CONVERSATION.md) | Foundational Sonnet conversation on evolutionary resonance |

## roadmaps/ — Where we're going

| Document | Description |
|----------|-------------|
| [VSCODE_EXTENSION_ROADMAP.md](roadmaps/VSCODE_EXTENSION_ROADMAP.md) | VS Code extension phased plan |
| [PASSIVE_COLLECTION_SPEC.md](roadmaps/PASSIVE_COLLECTION_SPEC.md) | Passive data collection specification |
| [PHASE2_IMPLEMENTATION_CHECKLIST.md](roadmaps/PHASE2_IMPLEMENTATION_CHECKLIST.md) | Phase 2 implementation checklist |
| [PULSE_REFLECTION_ENGINE.md](roadmaps/PULSE_REFLECTION_ENGINE.md) | PULSE self-reflection engine roadmap (Tiers 1-4) |

## data/ — Non-markdown reference data

| File | Description |
|------|-------------|
| ecosystem_connections.json | Operational edges (HTTP/Tailscale probes); complements `projects/status/component_map.json` |
| constella_discoveries.json | Constella framework discoveries |
| faithh_knowledge_graph.yaml | Knowledge graph structure |
| gen8-docker-compose.yml | Gen8 server Docker compose |
| EXPORT_AUDIT.json | Chat export audit results |
| RAG_METADATA_ANALYSIS.json | RAG metadata analysis |

## experiments/ — Measured runs and benchmarks

| Document | Description |
|----------|-------------|
| [KV_CACHE_QUANT_BENCHMARK_20260405.md](experiments/KV_CACHE_QUANT_BENCHMARK_20260405.md) | llama.cpp KV types (f16 / q4_0 / q8), VRAM table, PolarQuant Experiment A, captured chat ablation |
| [KV_EXPERIMENT_REPRO_CHECKLIST.md](experiments/KV_EXPERIMENT_REPRO_CHECKLIST.md) | What to record for comparable KV and chat-quality runs |
| `scripts/run_llama_kv_ablation_matrix.sh` + `summarize_kv_ablation_runs.py` | Multi-ctx (e.g. 8K+32K) three-way ablation → `data/kv_vectors/KV_ABLATION_SUMMARY.md` |
| [KV_RESEARCH_FORMATS_POLARQUANT.md](experiments/KV_RESEARCH_FORMATS_POLARQUANT.md) | PolarQuant vs llama.cpp: no flag today; kernel/fork scope; repo status |

## archive/ — Historical (consumed/stale)

Everything in `archive/` is kept for historical reference only. Do not treat these as current.

| Subfolder | Contents |
|-----------|----------|
| `handoffs/` | 39 consumed AI session handoff documents |
| `reports/` | 17 point-in-time status reports |
| `session-reports/` | 26 old session summaries |
| `legacy/` | ~80 old architecture docs, specs, patches, guides |

---

## Root-Level Docs (outside docs/)

These live at the repo root and are always current:

| Document | Description |
|----------|-------------|
| `AGENTS.md` | AI agent behavior rules + project structure + continuity pattern |
| `CONTEXT.md` | Current project context snapshot |
| `SYSTEMS_MAP.md` | High-level systems map |
| `README.md` | Repository README |

---

## Maintenance

To re-index documentation into ChromaDB after changes:
```bash
source venv/bin/activate
python scripts/reindex_project_docs.py --purge-stale
```

**Rules for new documents:**
- Guides → `docs/guides/`
- Architecture/system design → `docs/architecture/`
- Research findings → `docs/research/`
- Business/financial → `docs/business/`
- Reference material → `docs/reference/`
- Future plans → `docs/roadmaps/`
- Consumed handoffs → `docs/archive/handoffs/`
- Never add loose files to `docs/` root

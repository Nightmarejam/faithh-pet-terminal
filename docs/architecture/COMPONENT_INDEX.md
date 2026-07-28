# FAITHH Component Index

**Generated** by `scripts/docs/gen_component_index.py` — do not hand-edit.
Regenerate after adding or removing modules; it reads the source, so it
cannot drift the way a written map does.

Canonical entrypoint: `faithh_professional_backend_fixed.py`

`reachable` = imported by the entrypoint directly, or by something it imports.
Modules with no importer are candidates for archiving.

## repo root

| module | what it does | used by | reachable |
|---|---|---|---|
| `cc_proxy.py` | _(no docstring)_ | — | — |
| `filesystem_chip.py` | Filesystem Chip - Battle Chip for file operations. | `faithh_professional_backend_fixed.py` | yes |
| `google_search.py` | Google Search API Integration | `faithh_professional_backend_fixed.py` | yes |
| `knowledge_graph.py` | Knowledge Graph Loader | `faithh_professional_backend_fixed.py` | yes |
| `pulse_pattern_tracker.py` | PULSE Pattern Tracker | `faithh_professional_backend_fixed.py` | yes |
| `reindex_kb_v2.py` | Knowledge Base v2 Reindexer | — | — |
| `synthesize_anthropic_optimization.py` | Knowledge Synthesis - Anthropic Optimization | — | — |
| `synthesize_project_states.py` | Project State Synthesis | — | — |

## `app/analytics/`

| module | what it does | used by | reachable |
|---|---|---|---|
| `constitutional_analytics.py` | Constitutional Analytics - Day 6 Implementation | — | — |
| `focus_analytics.py` | Focus Analytics - Day 6 Implementation | — | — |
| `system_analytics.py` | System Performance Analytics - Day 6 Implementation | — | — |

## `app/providers/`

| module | what it does | used by | reachable |
|---|---|---|---|
| `anthropic_provider.py` | Anthropic provider implementation | `sync_anthropic_provider.py`, `provider_service.py` | — |
| `sync_anthropic_provider.py` | Synchronous Anthropic Provider Wrapper | — | — |

## `app/services/`

| module | what it does | used by | reachable |
|---|---|---|---|
| `__init___moon.py` | Business logic services | — | — |
| `__init___new.py` | Business logic services | — | — |
| `__init___parasitic.py` | Business logic services | — | — |
| `__init___phase3b.py` | Business logic services | — | — |
| `alife_parasitic_integration.py` | Alife Parasitic Integration Service | `__init___phase3b.py` | — |
| `alife_parasitic_integration_final.py` | Alife Parasitic Integration Service - Final Fixed Version | — | — |
| `alife_parasitic_integration_fixed.py` | Alife Parasitic Integration Service - Fixed | — | — |
| `alife_service.py` | Alife Data Processing Service | `__init___moon.py`, `__init___new.py`, `__init___parasitic.py` +1 | — |
| `chat_service.py` | Chat processing service | `__init___moon.py`, `__init___new.py`, `__init___parasitic.py` +1 | — |
| `constella_constitution.py` | Constella Framework Universal Constitution | `focus_management.py`, `faithh_professional_backend_fixed.py` | yes |
| `cosmic_ripple_integration.py` | Cosmic Ripple Integration Service | `faithh_professional_backend_fixed.py` | yes |
| `focus_management.py` | Focus Management System | `faithh_professional_backend_fixed.py` | yes |
| `genomic_biasing_engine.py` | Genomic Biasing Engine Service | — | — |
| `genomic_biasing_engine_fixed.py` | Genomic Biasing Engine Service (Fixed Version) | `faithh_professional_backend_fixed.py` | yes |
| `genomic_impedance_sensor.py` | Genomic Impedance Sensor Service | `faithh_professional_backend_fixed.py` | yes |
| `health_service.py` | Health check and monitoring service | `__init___moon.py`, `__init___new.py`, `__init___parasitic.py` +1 | — |
| `parasitic_alife_service.py` | **(does not parse — see the Python 3.10 notes in AGENTS.md)** | `__init___parasitic.py` | — |
| `parasitic_alife_service_fixed.py` | Parasitic Alife Service | `__init___phase3b.py`, `faithh_professional_backend_fixed.py` | yes |
| `provider_service.py` | Provider management service | `__init___moon.py`, `__init___new.py`, `__init___parasitic.py` +2 | — |
| `standing_wave_moon_service.py` | Standing Wave Resonance Service with Moon Damping | `__init___moon.py`, `__init___parasitic.py`, `__init___phase3b.py` | — |
| `standing_wave_service.py` | Standing Wave Resonance Service | `__init___moon.py`, `__init___new.py`, `__init___parasitic.py` +1 | — |
| `universal_impedance_field.py` | Universal Impedance Field Service | — | — |
| `universal_impedance_field_optimized.py` | Universal Impedance Field Service - Optimized Version | `faithh_professional_backend_fixed.py` | yes |
| `user_authentication_service.py` | User Authentication Service | `faithh_professional_backend_fixed.py` | yes |

## `backend/`

| module | what it does | used by | reachable |
|---|---|---|---|
| `advanced_analytics.py` | Advanced Analytics System | — | — |
| `advanced_analytics_simple.py` | Advanced Analytics System (Simplified) | `faithh_professional_backend_fixed.py` | yes |
| `ai_driven_ux.py` | AI-Driven User Experience System | `faithh_professional_backend_fixed.py` | yes |
| `anchor_validator.py` | Anchor Validator - Phase 2 Coherence Arbiter Enhancement | `coherence_arbiter.py` | yes |
| `anthropic_shim.py` | Anthropic Messages API shim for FAITHH. | `faithh_professional_backend_fixed.py` | yes |
| `cache.py` | Response Caching System | `faithh_professional_backend_fixed.py` | yes |
| `chip_weight_metrics.py` | Fusion weights for Phase 2 perf metrics only. | `faithh_professional_backend_fixed.py` | yes |
| `coherence_arbiter.py` | Coherence Arbiter - Measures semantic convergence between RAG and ML chip routing signals | `faithh_professional_backend_fixed.py` | yes |
| `coherence_sensor.py` | Coherence Sensor v0.1 - Harmony-AI Bridge Implementation | — | — |
| `config.py` | central configuration — single source of truth for all env-driven settings. | `health_service.py` | — |
| `connection_monitor.py` | Connection Monitor | `health_monitor_facade.py`, `faithh_professional_backend_fixed.py` | yes |
| `context_builders.py` | Backend — Context Builders | `faithh_professional_backend_fixed.py` | yes |
| `data_loaders.py` | Backend — Data Loaders | `context_builders.py`, `parallel_chip_engine.py`, `faithh_professional_backend_fixed.py` | yes |
| `enhanced_chip_integration.py` | Enhanced Chip Integration for FAITHH | `faithh_professional_backend_fixed.py` | yes |
| `faithh_backend_adapter.py` | Backend Adapter for HTML UI | — | — |
| `faithh_backend_v4_template.py` | Backend v4 - Production Template | — | — |
| `faithh_enhanced_backend.py` | Enhanced Backend API v2 | — | — |
| `faithh_unified_api.py` | Unified API - Chat + RAG + Tools in one place | — | — |
| `health_monitor_facade.py` | Unified health monitor facade. | `faithh_professional_backend_fixed.py` | yes |
| `integrate_program_advances.py` | Integration Script for Program Advances | — | — |
| `intent_detection.py` | Backend — Intent Detection | `semantic_intent_detector.py`, `parallel_chip_engine.py`, `faithh_professional_backend_fixed.py` | yes |
| `llm_providers.py` | Phase 2 - Multi-Provider LLM Module | `anthropic_provider.py`, `anthropic_shim.py`, `health_monitor_facade.py` +1 | yes |
| `local_optimization.py` | Local AI Optimization System | `faithh_professional_backend_fixed.py` | yes |
| `ml_learning_framework.py` | ML Learning Framework for FAITHH | `faithh_professional_backend_fixed.py` | yes |
| `parallel_chip_engine.py` | Parallel Chip Engine | — | — |
| `performance.py` | Performance Tracking System | `faithh_professional_backend_fixed.py` | yes |
| `performance_monitor.py` | Performance Monitor for LLM Providers | `faithh_professional_backend_fixed.py` | yes |
| `plc_state_manager.py` | PLC-like State Manager for FAITHH | — | — |
| `program_advance_optimizer.py` | Program Advance Performance Optimizer | `faithh_professional_backend_fixed.py` | yes |
| `rag_api.py` | Simple Flask API for RAG document search | — | — |
| `rag_processor.py` | RAG Document Processor | `faithh_professional_backend_fixed.py` | yes |
| `response_cache.py` | Simple response caching for FAITHH backend | `faithh_professional_backend_fixed.py` | yes |
| `security_manager.py` | Security Manager - Handles permissions and validation | `tool_executor.py` | — |
| `security_middleware.py` | Security Middleware | `faithh_professional_backend_fixed.py` | yes |
| `session_metrics.py` | session operational telemetry — Chroma collection `faithh_session_metrics`. | `faithh_professional_backend_fixed.py` | yes |
| `tiered_rag_processor.py` | Tiered RAG Processor for FAITHH Backend | — | — |
| `tool_executor.py` | Tool Executor - Core execution engine for FAITHH | `faithh_unified_api.py` | — |
| `tool_registry.py` | Tool Registry - Manages available battle chips/tools | `faithh_unified_api.py`, `tool_executor.py` | — |
| `tool_system.py` | Tool System for Local AI Agent | — | — |
| `ui_layout_optimizer.py` | UI Layout Learning Node for FAITHH | `faithh_professional_backend_fixed.py` | yes |

## `backend/ml/`

| module | what it does | used by | reachable |
|---|---|---|---|
| `ab_testing.py` | Phase 2 - A/B Testing Framework | — | — |
| `performance_tracker.py` | Phase 2 - Performance Tracking System | `enhanced_chip_integration.py`, `predictive_routing.py`, `weight_optimizer.py` +1 | yes |
| `predictive_routing.py` | Phase 3 - Predictive Routing System | — | — |
| `self_healing.py` | Phase 3 - Self-Healing System | — | — |
| `semantic_intent_detector.py` | Phase 2 - Semantic Intent Detector | `enhanced_chip_integration.py`, `faithh_professional_backend_fixed.py` | yes |
| `weight_optimizer.py` | Phase 2 - Weight Optimization Engine | `enhanced_chip_integration.py`, `faithh_professional_backend_fixed.py` | yes |

## `services/`

| module | what it does | used by | reachable |
|---|---|---|---|
| `rag_api.py` | Simple Flask API for RAG document search. | — | — |

## `services/project_hub/`

| module | what it does | used by | reachable |
|---|---|---|---|
| `app.py` | Program Advance System - Project Management & Decision Tracking | — | — |

## Nothing imports these

Not necessarily dead — some are standalone scripts or entrypoints — but
each should either be documented as such or moved to `archive/`.

- `app/analytics/constitutional_analytics.py`
- `app/analytics/focus_analytics.py`
- `app/analytics/system_analytics.py`
- `app/providers/sync_anthropic_provider.py`
- `app/services/__init___moon.py`
- `app/services/__init___new.py`
- `app/services/__init___parasitic.py`
- `app/services/__init___phase3b.py`
- `app/services/alife_parasitic_integration_final.py`
- `app/services/alife_parasitic_integration_fixed.py`
- `app/services/genomic_biasing_engine.py`
- `app/services/universal_impedance_field.py`
- `backend/advanced_analytics.py`
- `backend/coherence_sensor.py`
- `backend/faithh_backend_adapter.py`
- `backend/faithh_backend_v4_template.py`
- `backend/faithh_enhanced_backend.py`
- `backend/faithh_unified_api.py`
- `backend/integrate_program_advances.py`
- `backend/ml/ab_testing.py`
- `backend/ml/predictive_routing.py`
- `backend/ml/self_healing.py`
- `backend/parallel_chip_engine.py`
- `backend/plc_state_manager.py`
- `backend/rag_api.py`
- `backend/tiered_rag_processor.py`
- `backend/tool_system.py`
- `cc_proxy.py`
- `reindex_kb_v2.py`
- `services/project_hub/app.py`
- `services/rag_api.py`
- `synthesize_anthropic_optimization.py`
- `synthesize_project_states.py`

## Frontend

| file | size | served from |
|---|---|---|
| `faithh_cockpit.html` | 46 KB | referenced by the backend |
| `faithh_pet.html` | 135 KB | not referenced in the entrypoint |
| `faithh_pet_v4.html` | 344 KB | referenced by the backend |

_85 modules indexed, 39 reachable from the entrypoint, 33 unreferenced._

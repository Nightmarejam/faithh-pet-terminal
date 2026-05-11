# Research Handoff: Systems Map & AI Context Injection Architecture

**Created:** 2026-02-04  
**Handoff From:** Claude Opus 4.5 (claude.ai)  
**Handoff To:** Claude Opus (next session) or Sonnet (Windsurf)  
**Context:** Jonathan has ~2 days remaining with Opus before returning to Sonnet-tier models

---

## Background Context

I have approximately 2 days remaining with Opus before returning to Sonnet-tier models. I need to establish a system that lets me:

1. **Capture my current understanding** of my project ecosystem in a form that's both machine-readable AND meaningful to AI reasoning partners
2. **Hand that context to any AI** (Windsurf Sonnet, Claude Code, future sessions) in a standardized way
3. **Preserve "framing snapshots"** — immutable timestamps of how I understood things at key moments
4. **Generate human-readable narratives** from the graph structure

---

## Existing Assets (Read These First)

### Tier 1: Source of Truth (HIGH PRIORITY)
| File | Purpose | Last Updated |
|------|---------|--------------|
| `~/ai-stack/project_states.json` | Auto-updating project state (machine-readable) | 2026-01-25 |
| `~/ai-stack/faithh_memory.json` | AI self-awareness, user profile, project connections | 2025-11-29 |
| `~/ai-stack/MASTER_CONTEXT.md` | Technical overview (human-readable) | 2026-01-25 |
| `~/ai-stack/faithh_knowledge_graph.yaml` | Graph with entities, relationships, indexing rules | 2025-12-29 |
| `~/ai-stack/LIFE_MAP.md` | Strategic/philosophical framing, the "why" | 2026-01-18 |

### Tier 2: Supporting Context (MEDIUM PRIORITY)
| File | Purpose | Last Updated |
|------|---------|--------------|
| `~/ai-stack/decisions_log.json` | Decision history with full rationale | 2025-11-26 |
| `~/ai-stack/scaffolding_state.json` | Session continuity, open loops, parked tangents | 2025-11-28 |
| `~/ai-stack/docs/ECOSYSTEM_MAP.md` | Network topology, device inventory, service access | 2026-01-25 |

### Tier 3: Reference (LOW PRIORITY)
| File | Purpose |
|------|---------|
| `~/ai-stack/docs/GPT_PROJECT_CONTEXT.md` | Platform-adapted context for GPT |
| `~/ai-stack/docs/PERSISTENT_MEMORY_DESIGN.md` | Memory system specification |
| `~/ai-stack/docs/UPDATE_PROTOCOL.md` | Session handoff procedures |
| `~/ai-stack/docs/CONTEXT_PARITY_GUIDE.md` | How to keep context files in sync |

---

## Key Discovery: Most Pieces Already Exist

After surveying the documentation, we found Jonathan already has sophisticated context infrastructure:

**`faithh_memory.json`** contains:
- Self-awareness section (identity, purpose, what FAITHH is/isn't)
- Constella awareness (what it is, what it is NOT)
- User profile with vision, work, personal context
- Project connections (the resonance theme linking everything)
- Testing framework with resonance levels (R1/R2/R3)
- Context levels (L1 Recall → L2 Connection → L3 Synthesis)

**`faithh_knowledge_graph.yaml`** defines:
- Entities (Jonathan, Tom Cat Sound, FAITHH, Constella)
- Typed relationships (serves, indexes, informed_by, unified_by)
- Indexing rules with quality tiers
- Vocabulary/terminology mappings
- Doc templates (not yet implemented)

**`decisions_log.json`** captures:
- Decisions with full rationale
- Alternatives considered and why rejected
- Impact assessment
- Related documentation links

---

## The Actual Gaps

1. **Staleness** — Several key files are dated Nov-Dec 2025, not reflecting Jan 2026 changes (especially `faithh_memory.json`, `scaffolding_state.json`)

2. **No framing snapshots** — Everything is mutable; nothing captures "this is how I understood things on this date" as an immutable record

3. **No unified injection format** — You have to know which files to read; there's no single "hand this to an AI" document

4. **The graph doesn't generate** — `faithh_knowledge_graph.yaml` has `doc_templates` defined but the pipeline to produce docs from the graph doesn't exist

5. **No meta/philosophy in project_states.json** — Technical state is excellent; the "why" lives only in LIFE_MAP.md and faithh_memory.json

---

## Proposed Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOURCE OF TRUTH LAYER                        │
│  project_states.json  │  faithh_memory.json  │  decisions_log   │
│  (auto-updates)       │  (manual + auto)     │  (append-only)   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │   GENERATION SCRIPT   │
                    │  generate_context.py  │
                    └───────────┬───────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
│ CONTEXT.md        │  │ FRAMING SNAPSHOTS │  │ PLATFORM PROFILES │
│ (AI injection)    │  │ snapshots/        │  │ profiles/         │
│                   │  │ 2026-02-04.md     │  │ sonnet.md         │
│ Single doc any    │  │ 2026-03-01.md     │  │ opus.md           │
│ AI can consume    │  │ (immutable)       │  │ windsurf.md       │
└───────────────────┘  └───────────────────┘  └───────────────────┘
```

### How It Works

1. **Source of Truth Layer** — Existing files, maintained as they are now
   - `project_states.json` auto-updates via existing script
   - `faithh_memory.json` updated manually or by FAITHH
   - `decisions_log.json` append-only (new decisions added, old ones never edited)

2. **Generation Script** — `generate_context.py`
   - Reads all source files
   - Walks the knowledge graph
   - Produces three types of output:
     - **CONTEXT.md** — Universal AI injection document
     - **Framing snapshot** — Timestamped, immutable capture
     - **Platform profiles** — Role-adapted versions (optional)

3. **Output Documents**
   - **CONTEXT.md** — "Hand this to any AI" document, regenerated on demand
   - **Framing snapshots** — Created at key moments, never edited after creation
   - **Platform profiles** — Adapted for specific AI roles/limitations (Sonnet context window, GPT's non-execution role, etc.)

---

## Context Injection Specification (v1.0)

### Purpose
A single document that can be handed to any AI to establish shared understanding of Jonathan's project ecosystem.

### Requirements
- Must fit in Sonnet-tier context window (~150k tokens, but practically <20k for working memory)
- Must be both human-readable AND machine-parseable
- Must capture facts AND framing (the "why")
- Must be regenerable from source files

### Proposed Structure

```markdown
# Jonathan's Project Context
<!-- Generated: {timestamp} -->
<!-- Source: generate_context.py -->

## Who I Am
{from faithh_memory.json → user_profile}

## Current State
{from project_states.json → projects summary}

## Project Graph
{from faithh_knowledge_graph.yaml → entities + relationships as prose}

## Active Focus
{from scaffolding_state.json → active_context + open_loops}

## Key Decisions
{from decisions_log.json → last 5-10 decisions with rationale}

## Philosophy
{from LIFE_MAP.md → core pattern + driving question}

## What Matters Now
{from LIFE_MAP.md → current tensions + paths}
```

### Format Decision: Markdown with YAML Frontmatter
- Markdown for AI readability (prose, headers)
- YAML frontmatter for machine-parseable metadata
- Sections clearly delineated for selective reading

---

## Framing Snapshot Protocol

### What It Is
An immutable capture of "how Jonathan understood things at this moment."

### When to Create
- Before major pivots or decisions
- When starting a new phase
- When handing off to a different AI platform
- Monthly, as a discipline

### Format
```markdown
# Framing Snapshot: {date}
<!-- IMMUTABLE: Do not edit after creation -->

## Current Understanding
{prose summary of how projects relate}

## What I Believe Is True
{key assumptions, prioritizations}

## Open Questions
{what I'm uncertain about}

## Energy State
{where attention is, what feels alive vs stale}
```

### Storage
- `~/ai-stack/snapshots/framing/YYYY-MM-DD.md`
- Never edited after creation
- Can be referenced by future sessions to see drift

---

## Implementation Plan

### Phase 1: Context Injection Spec (This Session)
- [x] Define structure and format
- [ ] Create template file
- [ ] Document field mappings from source files

### Phase 2: Generation Script (This Session or Next)
- [ ] Write `scripts/generate_context.py`
- [ ] Read from all source files
- [ ] Output CONTEXT.md
- [ ] Output framing snapshot (optional flag)

### Phase 3: Integration (Next Session)
- [ ] Add to FAITHH's update protocol
- [ ] Test with Windsurf Sonnet
- [ ] Create first framing snapshot

### Phase 4: Maintenance (Ongoing)
- [ ] Monthly framing snapshots
- [ ] Regenerate CONTEXT.md before major AI sessions
- [ ] Keep source files current

---

## Research Questions (Resolved)

1. **What format should a "context injection" document take?**
   → Markdown with YAML frontmatter. Human-readable prose, machine-parseable metadata.

2. **How should framing snapshots work?**
   → Separate files in `snapshots/framing/`, timestamped, immutable after creation.

3. **How can the knowledge graph generate outputs?**
   → Python script walks YAML, produces prose sections for CONTEXT.md.

4. **What's the minimum viable implementation?**
   → `generate_context.py` that produces CONTEXT.md from existing files. Everything else is enhancement.

---

## Relevant Philosophy (from LIFE_MAP.md)

> *"I see the whole gestalt but the path dissolves when I try to walk it."*

Jonathan creates and maintains **harmony** across domains:
- **Civic systems** → Constella (governance through resonance)
- **Sound** → Floating Garden Soundworks (audio harmony)
- **Personal workflow** → FAITHH (harmonic alignment across projects)
- **Philosophy** → Celestial Equilibrium (the unifying thread)

The unifying question: *"How do we build systems that actually serve people well?"*

This context injection system is itself an answer to that question — a system that serves the human by maintaining coherence when attention shifts.

---

## Session Continuity Notes

This document was created during a session where we:
1. Identified the core problem (context doesn't transfer between AI sessions)
2. Surveyed existing documentation assets (found 10+ relevant files)
3. Discovered most pieces already exist — the gap is unification, not creation
4. Designed the architecture (source layer → generation → outputs)
5. Specified the context injection format
6. Defined the framing snapshot protocol

**Next steps for continuing session:**
1. Create the CONTEXT.md template
2. Write `generate_context.py`
3. Generate first framing snapshot
4. Test with a fresh AI session

---

**End of Handoff Document**

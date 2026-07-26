# AGENTS.md — the one live context file

**Last verified: 2026-07-25** (live checks against the fleet)

> **Read this first, and read only this.** It replaces the six competing "master" context
> documents this repo used to carry (`CONTEXT.md`, `CURSOR_CONTEXT.md`, `MASTER_CONTEXT.md`,
> `SYSTEM_FINGERPRINT.md`, `SYSTEMS_MAP.md`). Those are archived under
> `docs/archive/superseded-2026-07/`. **Do not create a new context doc** — update this one.
> If you find another file claiming to be canonical, it is stale by definition.

---

## 1. Owner and intent

**Jonathan** — audio producer and AI developer. Business: Tom Cat Sound LLC (dba Floating
Garden Soundworks); partner Thomas Charles Gilson (remote, South Dakota).

**Core challenge:** maintaining project coherence when attention shifts across long-running
projects (ADHD). **What the system is for:** remembering *why* when he's lost sight of it.

**Philosophy:** Celestial Equilibrium — resonance, harmonic alignment, dignity.
**Driving question:** *"How do we build systems that actually serve people well?"*

### What FAITHH is
FAITHH (Friendly AI Teaching & Helping Hub) — a thought partner that surfaces relevant context
when returning to a project, gently challenges while accepting incremental progress, and
surfaces connections across domains.

### What FAITHH is NOT
- NOT a religious/philosophical framework about "faith"
- NOT a search engine or Q&A bot
- NOT a task executor — closer to a live journal with feedback

---

## 2. Current state (verified 2026-07-25)

⚠️ **The FAITHH VM (VM 100) is DOWN** pending the Proxmox rebuild. Anything on `faithh.*` is
unreachable and that name does not resolve. Do not assume the backend or vLLM is running.

| Component | State | Where |
|---|---|---|
| ChromaDB | ✅ running, ~450k docs across 4 collections | `servicebox.taileb8c60.ts.net:8000` |
| Gen8 (`servicebox`) | ✅ up, 19 containers | SSH `jonat@servicebox.taileb8c60.ts.net` |
| NAS (`nas`) | ✅ up (recovered 2026-07-24) | SSH `nas` |
| Cloud LLM keys | ✅ Groq / Anthropic / Gemini configured | `.env`, `FAITHH_FORCE_LOCAL=0` |
| FAITHH backend (:5557) | ❌ down with VM 100 | — |
| vLLM (:8000 on faithh) | ❌ down with VM 100 | — |
| Ollama | ❌ **not installed on the Gen8** | older docs claiming active models are wrong |
| PVE host | ❌ rebuild pending | backups verified on NAS `pve` share |

**The backend can run today without the VM**: on the Gen8, against local ChromaDB, using cloud
inference instead of vLLM. Note the old model path `/mnt/nas/models/...` is dead — models now
live on the NAS at `homelab/ai/models/`.

**Addressing:** never hardcode an IP. MagicDNS names (`<host>.taileb8c60.ts.net`) are canonical
and the source of truth is `infra/hosts.yaml` in the **homelab** repo. Any `192.158.*` literal
is a typo of `192.168.*` and was never routable — it is dead code by definition.

---

## 3. Repository structure

Python-first: Flask backend + static HTML UI.

**Canonical backend:** `faithh_professional_backend_fixed.py` (port **5557**) — all main
`/api/*` routes. Sidecars are separate processes, **not** imported by it:
`services/rag_api.py` (:5001), `services/project_hub/app.py`. Legacy backends live in
`archive/legacy/` and must not run.

**Active root files (do not move):**
- `faithh_professional_backend_fixed.py` — main backend
- `filesystem_chip.py`, `knowledge_graph.py`, `pulse_pattern_tracker.py` — imported by it
- `faithh_pet_v4.html` — primary Canvas UI (backend serves it from root)
- `faithh_cockpit.html` — Mission Control / diagnostics, served at `/cockpit`

**Directories:** `backend/` (shared imports: `data_loaders`, `intent_detection`,
`context_builders`, `llm_providers`) · `services/` (standalone apps) · `modules/` (import-only
libs) · `vendor/` (third-party trees) · `scripts/` (all utilities) · `tests/` · `ml/` ·
`projects/crypto/` (own venv).

**State files:** `faithh_memory.json`, `decisions_log.json`, `project_states.json`,
`scaffolding_state.json`, `config.yaml`.

**Docs:** `docs/architecture/` · `guides/` · `reference/` · `business/` · `research/` ·
`roadmaps/` · `data/` · `archive/`.

**Service Registry:** any new user-facing backend capability **must** be reflected in
`build_workspace_registry()` and `GET /api/workspace/registry` so `faithh_pet_v4.html` can adapt
navigation and send `workspace_registry` hints with `POST /api/chat`.

---

## 4. Commands

```
./restart_backend.sh                      # stop + start Flask on :5557
./stop_backend.sh
python faithh_professional_backend_fixed.py   # run directly (debugging)
docker-compose up -d                      # ChromaDB / Langflow / Postgres
python -m pytest tests/ -v
tests/test_harmony.sh | tests/test_groq.sh
```

**Before editing any frontend file**, confirm what the backend serves:
`grep "send_from_directory" faithh_professional_backend_fixed.py`. Test UI changes at
`http://localhost:5557/`, never by opening HTML files directly.

---

## 5. Hard rules — never violate

1. Never commit `.env`, `keyring.json`, or anything in `uploads/`.
2. Never use `query_texts=` in ChromaDB — always `query_embeddings=`.
3. Never revert the LLM priority order (Groq is primary).
4. Never `pip install` in the main venv without updating `requirements.txt`.
5. Always use the venv python: `/home/jonat/ai-stack/venv/bin/python`.
6. Never modify `faithh_professional_backend_fixed.py` without a backup commit first.
7. Never add `knowledge_base/` to git.
8. The crypto pipeline uses its own venv at `projects/crypto/venv/`.
9. Commit after each working milestone — small, descriptive commits.
10. After any backend change: `curl http://localhost:5557/health`.
11. **Never hardcode an IP address.** Use MagicDNS names; see `infra/hosts.yaml` in homelab.

---

## 6. Agent behavior

- After completing a task and verifying it works, **report findings and stop.** Do not loop
  verification commands. If a task fails, report it and ask — don't retry indefinitely.
- **New scripts → `scripts/`. New docs → `docs/`.** Keep the root clean (except this file and
  `README.md`).
- Before marking a task complete, consult `DEPS.md` for files that need updating alongside.
- For technical questions about live capability, check `GET /api/workspace/registry` rather
  than guessing.
- **Session metrics** go to the Chroma collection `faithh_session_metrics` — never to
  `faithh_knowledge_base` or conversation collections, and never treated as RAG knowledge.
- Answers about repo state, git history, and live metrics follow the evidence-only rules in
  `docs/guides/FAITHH_OPERATOR_CONTRACT.md`.
- **RAG low confidence:** when `rag_signal.low_confidence` is true, the backend prepends a
  no-fabrication banner. Never invent endpoints, paths, collection names, or system states —
  say "I don't have reliable context for that" and name the source to check.

### Style
Python 4-space, `snake_case` functions, `UpperCamelCase` classes. HTML/JS IDs and CSS classes
lowercase-with-hyphens. Commit messages: descriptive subject with scope, body for substantial
changes (see `docs/guides/GIT_WORKFLOW.md`).

---

## 7. Active tracks

| # | Track | State (2026-07-25) |
|---|---|---|
| 1 | **Crypto pipeline** (`projects/crypto/`) | **BUILT** — `fetch_prices`, `ingest_whitepaper`, `signal_engine`, `mining_switch`, paper execution + journal scoring, `mining_ledger` polling 2Miners. Own venv. |
| 2 | **Mining** | Blocked — was hosted on the FAITHH VM (RTX 3090), down with PVE. Hard rule: stop vLLM before starting the miner, never concurrent. |
| 3 | **FAITHH maintenance** | Open: `ARCHITECTURE.md` needs updating (Groq primary, BGE embeddings, new collection names); verify `governance_corpus` intent routing (`is_legal_query`). RAG preflight threshold `best_distance > 0.60`. |
| 4 | **Proxmox rebuild** | Pending — the gating task. Runbook: `docs/hardware/proxmox-rebuild-runbook.md` in **homelab**. Backups verified on the NAS `pve` share. |
| 5 | **Tom Cat Sound LLC** | Tax return due **2026-09-15** (Form 7004 filed). Members: Jonathan 34%, Thomas 33%, Kevin 33%. Member meeting required before restructuring. |
| 6 | **Gen8 GPU** | **DONE** — an **RTX A1000 8GB** is installed and in use (Plex NVENC). Supersedes the old "T1000 pending" note. |

---

## 8. Documentation rules

**One live doc per topic.** This file is the only living context document. Tool-specific files
(`CLAUDE.md`, `CURSOR_CONTEXT.md`, `.windsurf/rules/*`) are thin pointers here and must stay
that way — never let them accumulate content.

- **Living docs**: plain noun filename, no date in the name, a `Last verified:` line inside,
  exactly one per topic. Update in place.
- **Point-in-time docs**: date in the filename (`SYSTEM_AUDIT_2026_03_30.md`). Never updated —
  they are snapshots.
- **Superseded docs**: move to `docs/archive/` with a header saying what replaced them.
- Nothing claims "master" / "canonical" / "single source of truth" unless it is the only one.
- **When a machine's state changes, grep for its name across the repos the same day.** Both
  directions of drift (claiming down when up, claiming running when dead) have cost real time.

### Maintenance protocols

**Monthly:** verify a single canonical backend; archive experimental variants; clean root
(< 20 files); reconcile this file against reality; check endpoint conflicts.
**Weekly:** update `project_states.json`, review recent decisions, backend health check, move
new experiments into `experiments/`.
**Immediate cleanup when:** backend variants exceed 5, root exceeds 20 files, documentation
drift is detected, or experiments complete but endpoints are inaccessible.

All backend architecture changes go in `decisions_log.json` with `rationale`,
`alternatives_considered`, `impact`, `status`.

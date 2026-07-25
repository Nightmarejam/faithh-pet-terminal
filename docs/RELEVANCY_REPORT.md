# Relevancy & Unification Audit

**Date:** 2026-04-07  
**Repo:** `/home/jonat/ai-stack` (FAITHH stack)  
**Scope:** Local inventory, root-level classification, Nightmarejam GitHub org alignment, Canvas unification draft.

---

## 1. Inventory artifacts (Section 1 commands)

| Artifact | Description |
|----------|-------------|
| `docs/current_file_inventory.log` | **3761** lines: `mtime path` for `find . -maxdepth 3` (excludes `.*` and `./venv*`), sorted newest-first. Use for freshness sweeps. |
| `app.run` entry points | **Canonical:** `faithh_professional_backend_fixed.py` → `:5557`. **Sidecars:** `services/rag_api.py` `:5001`, `services/project_hub/app.py` `:5001`. **Legacy:** `archive/**` (many duplicates). |
| Root `*.html` | `faithh_pet_v4.html`, `faithh_cockpit.html` (active). Others live under `archive/`, `llama.cpp/`, `projects/`, `docs/archive/`. |

---

## 2. Root-level file & directory table

**Legend:** **ACTIVE** = current FAITHH stack; **LEGACY** = superseded or archive-grade; **DELETE** = safe removal candidate after human confirmation; **EXTERNAL** = belongs primarily to upstream GitHub / submodule story; **TOOL** = standalone app, not the main pet server.

| Path | Status | Notes |
|------|--------|--------|
| `faithh_professional_backend_fixed.py` | ACTIVE | Canonical Flask backend; `app.run` :5557. |
| `faithh_pet_v4.html` | ACTIVE | Primary pet UI (served at `/`). |
| `faithh_cockpit.html` | ACTIVE | Secondary dashboard UI (`/cockpit`). |
| `filesystem_chip.py` | ACTIVE | Imported by backend. |
| `knowledge_graph.py` | ACTIVE | Imported by backend. |
| `pulse_pattern_tracker.py` | ACTIVE | Imported by backend. |
| `config.yaml` | ACTIVE | Runtime config. |
| `restart_backend.sh` / `stop_backend.sh` / `start_backend.sh` | ACTIVE | Ops entrypoints. |
| `AGENTS.md`, `README.md`, `DEPS.md`, `CONTEXT.md`, `SYSTEM_FINGERPRINT.md`, `SYSTEMS_MAP.md`, `MASTER_CONTEXT.md` | ACTIVE | Repo continuity / index docs. |
| `decisions_log.json`, `faithh_memory.json`, `project_states.json`, `scaffolding_state.json`, `fingerprint_state.json`, `faithh_live_state.json`, `pulse_patterns.json`, etc. | ACTIVE | Machine-readable state (do not delete casually). |
| `faithh_collection_rules.yaml`, `tool_policies.json`, `manifest.json` | ACTIVE | Policies / PWA metadata. |
| `docker-compose.yml` | ACTIVE | Ollama/Chroma/Langflow/Postgres stack. |
| `faithh_professional_backend_fixed.py.backup` | LEGACY | **DELETE** candidate after diff vs canonical file; keep until explicitly replaced by git history. |
| `google_search.py` | ACTIVE / review | Utility; confirm still referenced by backend or scripts before moving. |
| `synthesize_anthropic_optimization.py`, `synthesize_project_states.py` | TOOL | Root one-offs; **move to `scripts/`** per `AGENTS.md` on next cleanup pass. |
| `setup_anthropic_key.sh` | ACTIVE | Helper script. |
| `check_gen8_specs.sh` | ACTIVE | Infra check. |
| `gpu_installation_guide.md`, `tesla_t1000_ordering_info.md` | ACTIVE | Reference; could live under `docs/reference/` later. |
| `keyring.json` | ACTIVE | **Secrets** — never commit; not a DELETE target. |
| `test_query.json`, `work_log.json`, `ui_layout_learning.json`, `ml_learning_nodes.json` | ACTIVE / data | Low-level state or samples; classify with usage grep before DELETE. |
| `favicon.ico` | ACTIVE | Static asset. |
| `backend/` | ACTIVE | Modular Python imported by the canonical backend (`llm_providers`, loaders, security, etc.). |
| `services/` | ACTIVE | Sidecar Flask apps: `rag_api.py`, `project_hub/` (ports documented in each file). |
| `modules/` | ACTIVE | Scaffold for shared import-only libraries (`modules/README.md`). |
| `vendor/` | ACTIVE | Reserved for large vendored/submoduled trees (`vendor/README.md`). |
| `tests/` | ACTIVE | Pytest. |
| `scripts/` | ACTIVE | Automation. |
| `docs/` | ACTIVE | Documentation + this report. |
| `ml/` | ACTIVE | Chips, training, outputs. |
| `archive/` | LEGACY | Historical backends/UI; keep for archaeology, not runtime. |
| `archived/`, `backups/`, `legacy/` | LEGACY | Backups / old trees; DELETE only after policy review. |
| `llama.cpp/` | EXTERNAL / VENDOR | Upstream tree; do not merge into Canvas Python modules; optional submodule or documented path. |
| `faithh-vscode/` | ACTIVE | Extension project. |
| `projects/constella-framework/` | EXTERNAL | **Git submodule** → `Nightmarejam/constella-framework`. |
| `projects/` (other) | ACTIVE | Experiments (`alife`, `tomcat-sound`, `status`, etc.). |
| `runbook-to-rule-them-all/` | EXTERNAL | Nested clone of `Nightmarejam/runbook-to-rule-them-all` (`.git` inside). Not parent submodule; **unification risk** (nested repo). |
| `app/` | TOOL / review | Separate app tree; confirm relationship to canonical backend. |
| `venv/` | LOCAL | Not in git; excluded from inventory `find`. |
| `(noise)` | REVIEW | Odd filename at root from tooling; inspect contents / rename or gitignore. |
| `.aider.*`, `.coverage`, `.continue`, `.windsurf` | LOCAL / LEGACY | Editor/tool artifacts; consider `.gitignore` tightening. |

**Depth > 3:** See `docs/current_file_inventory.log` and `docs/architecture/` maps (e.g. `dependency_map.md`, `ACTIVE_VS_LEGACY_SCRIPT_MAP.md` if present) for deeper classification—not every path is duplicated here.

---

## 3. Nightmarejam GitHub org (2026-04-07)

**Public repositories (4):**

| Repository | Role vs local `ai-stack` | Submodule? | Merge as directory? | Redundant? |
|------------|---------------------------|------------|----------------------|------------|
| [constella-framework](https://github.com/Nightmarejam/constella-framework) | Already **`projects/constella-framework`** via `.gitmodules`. | **Yes (existing)** | No — keep submodule | No |
| [faithh-pet-terminal](https://github.com/Nightmarejam/faithh-pet-terminal) | Described as FAITHH companion **web UI**; local truth is root **`faithh_pet_v4.html`**. | **Optional** (track UI releases) **or** replace with sync job | Alternatively **promote** pet HTML into that repo as publishing target | **Partial overlap** — risk of drift between GitHub and root HTML |
| [runbook-to-rule-them-all](https://github.com/Nightmarejam/runbook-to-rule-them-all) | Local **`runbook-to-rule-them-all/`** appears to be a **full nested clone** (own `.git`). | **Recommended** — proper submodule under e.g. `docs/runbooks/` or `runbooks/` | Possible but loses upstream PR flow if copied | Local nested copy **redundant** with remote unless intentionally forked |
| [celestial-equilibrium](https://github.com/Nightmarejam/celestial-equilibrium) | Shell-oriented “Starborne Compass” — **not** present as a first-class module in backend grep. | **Candidate** if Canvas needs that narrative/tooling | **Vendor / sibling** project | **Not redundant** with FAITHH core; integration is product choice |

**Note:** Org page shows recent activity touching `faithh-pet-terminal`, `constella-framework`, `runbook-to-rule-them-all` (March–April 2026). No API access was used; classification is structural, not line-by-line diff.

---

## 4. Canvas: UI location & “floating” backend surface

### Where the UI lives

- **Primary Canvas surface:** `faithh_pet_v4.html` → served at **`/`** by `faithh_professional_backend_fixed.py`.
- **Secondary:** `faithh_cockpit.html` → **`/cockpit`**.
- **Other HTML** (archived pets, llama.cpp server UIs, `projects/status/dashboard.html`) are **not** the canonical Canvas unless explicitly linked from ops docs.

### Backend routes with **weak or no** coverage in `faithh_pet_v4.html` (floating / ops-only)

The pet UI references many routes (`/api/chat`, PLC, pulse, compass, focus, journal, constitution, ml chips, etc.). Roughly **floating** or **admin/secondary** (no obvious `fetch` in the first-pass grep of `faithh_pet_v4.html`):

- `/api/search`, `/api/search/status`
- `/api/upload`
- `/api/rag_search` (direct RAG API; chat may use RAG internally)
- **`/api/genomic/*`** (impedance, biasing, sensors) — genomic lab surface
- `/api/test_integrations`
- `/api/ml-learning`
- `/api/ui-layout` (GET/POST)
- `/api/cache`, `/api/performance`
- `/api/program-advance/*`
- `/api/analytics/*`, `/api/ux/*`
- `/api/monitoring/services`, `/api/monitoring/enhanced`
- `/api/pulse/proposals`, `/api/pulse/approve`, `/api/pulse/reject`
- Parts of **`/api/pulse/reflection/*`** (verify panel-by-panel in UI)
- `/api/avatar`, `/api/avatar/generate`
- `/api/filesystem` (may be gated feature — confirm)
- `/api/compass` (GET) vs `/api/compass/director` (pet uses director)
- `/metrics`, `/api/metrics`
- `/api/compare`
- **`/api/auth/*`** (if enabled — full account subsystem)
- `/api/constitution/evaluate`, `/api/constitution/update-modern-rights`
- `/api/focus/capture-concept`
- `/collectors/status` (legacy path; also `/api/context/collectors/status`)

**Canvas implication:** “Single Canvas” means either **(a)** wiring these into the pet UI, **(b)** registering them as **service cards** in a dashboard layer, or **(c)** explicitly marking them **deprecated** if unused.

---

## 5. Proposed directory structure (unified modules)

Goal: one tree the Flask app owns, with **Nightmarejam** content **pinned** (submodules) or **imported** as packages—not scattered nested clones.

```
ai-stack/
├── faithh_professional_backend_fixed.py   # thin bootstrap; optional future: app factory in backend/
├── faithh_pet_v4.html                     # Canvas v1 (or symlink from submodule)
├── backend/                               # existing — core API, providers, security
├── services/                              # NEW: optional — fat feature verticals
│   ├── genomic/                           # move or wrap /api/genomic/* handlers
│   ├── focus/                             # focus API + jobs
│   ├── filesystem/                        # chip + API alignment
│   └── pulse_admin/                       # proposals/approve/reject UI+API glue
├── modules/                               # NEW: optional — shared libraries (no Flask routes)
│   └── nightjam/                          # namespace for org-wide shared code (if any)
├── projects/
│   └── constella-framework/               # submodule (keep)
├── vendor/                                # NEW: optional — llama.cpp, large third_party
│   └── llama.cpp/                         # move from root OR document as git submodule
├── docs/
│   └── runbooks/                          # submodule: runbook-to-rule-them-all OR subtree
└── scripts/                               # single home for one-off py/sh (reduce root)
```

**Principles:**

1. **Submodules:** `constella-framework` (done); add **`runbook-to-rule-them-all`** as official submodule after removing nested `.git`; consider **`faithh-pet-terminal`** only if the repo becomes the **source of truth** for `faithh_pet_v4.html`.
2. **Merge:** Prefer **small PRs** moving route groups from monolith into `services/*` **blueprints** (`Flask.register_blueprint`) rather than one big rename.
3. **Redundant:** Delete or stop tracking duplicate `faithh_pet` copies under `archive/` only after Canvas declares a single canonical file and CI checks references.

---

## 6. Unification plan (phased)

### Phase A — Truth & hygiene (low risk)

1. Treat **`faithh_professional_backend_fixed.py` + `faithh_pet_v4.html`** as the only **production** pair; document in `AGENTS.md` / `SYSTEM_FINGERPRINT.md`.
2. Resolve **`runbook-to-rule-them-all`**: remove nested `.git` **or** add parent `.gitmodules` and re-clone as submodule; pick **one** remote source of truth.
3. Compare **`faithh_pet_v4.html`** vs **`Nightmarejam/faithh-pet-terminal`** (manual diff or `git diff` if histories related); record winner in `DEPS.md`.
4. Keep **`docs/current_file_inventory.log`** regeneration in monthly maintenance (or automate in `scripts/`).

### Phase B — Canvas coverage map

1. Build a **route manifest** (script): columns = `path`, `methods`, `used_in_faithh_pet_v4`, `used_in_cockpit`, `tests`.
2. For each **floating** route: **wire**, **dashboard**, or **deprecate** (ticket per group).

### Phase C — Structural

1. Introduce **`services/`** (or `backend/blueprints/`) and migrate **genomic**, **analytics/ux**, **monitoring** clusters.
2. **`llama.cpp`:** submodule under `vendor/` or documented “do not vendor in Canvas builds.”
3. **`faithh-pet-terminal`:** either submodule at `ui/faithh-pet-terminal/` with build step copying to root, or archive GitHub repo if root HTML remains canonical.

### Phase D — Nightmarejam alignment

1. **`celestial-equilibrium`:** spike integration (link from Canvas, CLI, or separate app)—no merge until product spec exists.
2. Ensure **Constella** docs in `docs/` point to **`projects/constella-framework`** submodule HEAD.

---

## 7. Next actions (for Cursor / maintainers)

| # | Action |
|---|--------|
| 1 | **`docs/current_file_inventory.log` is gitignored** (ephemeral). Regenerate with the `find` command in §1; keep **`docs/RELEVANCY_REPORT.md`** version-controlled. |
| 2 | Run route-vs-UI coverage script (Phase B) — not implemented in this pass. |
| 3 | File ticket: nested **`runbook-to-rule-them-all`** → submodule decision. |
| 4 | File ticket: **`faithh-pet-terminal`** vs **`faithh_pet_v4.html`** single source of truth. |

---

## Chroma collection silo: `faithh_session_metrics`

| Collection | Domain | Category / role |
|------------|--------|-----------------|
| `faithh_session_metrics` | `faithh` | `session_metrics` / `operational_telemetry` — per-session open/close snapshots and outcomes for Cockpit trending (`GET /api/metrics/summary`). **Not** indexed into RAG and not mixed with `faithh_knowledge_base`. |

---

## References

- Inventory: `docs/current_file_inventory.log`
- Session context: `docs/archive/SESSION_BRIEF_2026-04-07_KV_CACHE_BACKEND.md`
- Submodule: `.gitmodules` → `projects/constella-framework`
- Nightmarejam org: `https://github.com/Nightmarejam`

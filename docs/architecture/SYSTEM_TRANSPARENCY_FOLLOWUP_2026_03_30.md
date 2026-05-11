# SYSTEM_TRANSPARENCY_FOLLOWUP_2026_03_30

Audit date: 2026-03-30  
Repo root: `/home/jonat/ai-stack`  
Purpose: actionable follow-up to `docs/SYSTEM_AUDIT_2026_03_30.md` plus Option C backend import work, with concrete next steps to maintain transparency as project velocity increases.

---

## Executive status

- Core audit coverage exists and is strong for structure/inventory (`docs/SYSTEM_AUDIT_2026_03_30.md`).
- Import-level backend audit now exists (`docs/architecture/BACKEND_IMPORT_AUDIT.md`).
- Optional Option C follow-ups were implemented in code this pass:
  - Added unified health facade: `backend/health_monitor_facade.py`.
  - `/api/monitoring/services` now uses the facade to combine provider checks and system summary.
  - Removed noisy lazy-import path for Constella enhancement by adding compatibility hooks in `backend/context_builders.py`.
  - Removed redundant in-request ML import in `faithh_professional_backend_fixed.py`.

---

## What changed this pass (implemented)

### 1) Unified monitor surface (without risky rewrites)

- **New module:** `backend/health_monitor_facade.py`
  - Delegates to:
    - `backend.connection_monitor.connection_monitor` (system-level service monitoring)
    - `backend.llm_providers.connection_monitor` (provider quick-check cache)
- **Backend endpoint updated:** `faithh_professional_backend_fixed.py` `/api/monitoring/services`
  - Uses facade methods for checks and last-check timestamps.
  - Returns both:
    - `provider_unhealthy_services`
    - `system_health_summary`
  - `overall_healthy` now requires healthy provider checks and `system_summary.overall_status == "healthy"`.

### 2) Lazy import cleanup (safe scope)

- Added compatibility functions to `backend/context_builders.py`:
  - `get_constella_enhanced_context(query_text, base_context)`
  - `enhance_response_with_constella(query_text, response_text)`
- Updated `faithh_professional_backend_fixed.py` to import and call them directly.
- Removed redundant runtime import:
  - `from backend.ml.performance_tracker import ...` inside request path (already imported at module load when Phase 2 is enabled).

---

## Transparency gaps still open (priority order)

### P0 — Data/Indexing truth table (what is indexed, where, with what metadata)

**Problem:** current scripts are numerous and heterogeneous; domain tagging and collection targeting are inconsistent.  
**Risk:** false confidence in retrieval coverage, weak traceability.

**Follow-up actions:**
- Build one canonical index registry doc: script -> collection -> source paths -> metadata keys -> schedule/trigger.
- Add a lightweight verification script: sample-by-domain + file-path probes for critical docs.
- Mark deprecated indexers explicitly in headers and docs.

**Suggested outputs:**
- `docs/architecture/INDEXING_REGISTRY.md`
- `scripts/maintenance/verify_index_coverage.py`

### P0 — Monitoring API contract hardening

**Problem:** monitoring payload shape has evolved ad hoc.  
**Risk:** dashboard/parser drift and silent breakage.

**Follow-up actions:**
- Document `/api/monitoring/services` response schema in `docs/architecture/BACKEND_API.md`.
- Add one backend test that validates required keys and basic types.

### P1 — Remove path mutation in enhanced monitoring

**Problem:** `sys.path.append('.')` inside `/api/monitoring/enhanced`.  
**Risk:** import behavior depends on launch cwd.

**Follow-up actions:**
- Replace with package-safe import path or module relocation under `backend/`.
- Add an import failure message that includes remediation path.

### P1 — Legacy/duplicate backend surface area

**Problem:** many archived/legacy backend variants still exist and can confuse discovery.  
**Risk:** operators/scripts reference wrong file.

**Follow-up actions:**
- Keep canonical backend pinned in docs (already done), and add explicit "do not run" markers in major legacy files.
- Add a script check that fails if startup commands reference non-canonical backends.

### P2 — Project-state update discipline

**Problem:** narrative docs and `project_states.json` can drift.  
**Risk:** planning and RAG context misalignment.

**Follow-up actions:**
- Add a small checklist script that compares ALife status claims between:
  - `docs/constella_stress_tests/ALIFE_FINDINGS.md`
  - `project_states.json` (`projects.alife`)
- Run it before monthly/weekly maintenance commits.

---

## Recommended operational cadence

- **Daily (5 min):**
  - hit `/api/monitoring/services`
  - watch `provider_unhealthy_services` + `system_health_summary.overall_status`
- **Weekly (20-30 min):**
  - run indexing coverage verification (once implemented)
  - reconcile top 3 active project summaries with `project_states.json`
- **Monthly (60 min):**
  - architecture cleanup trigger check from `AGENTS.md`
  - update this follow-up report with completed/open items

---

## Immediate next implementation batch (suggested)

1. Add monitoring schema docs + one API test.  
2. Add indexing registry + coverage checker.  
3. Remove `sys.path.append('.')` from enhanced monitoring path.  
4. Add ALife doc/state drift checker script.

---

## Verification for this pass

```bash
python3 -m py_compile faithh_professional_backend_fixed.py
```

This pass focused on transparency primitives and low-risk consolidation without changing core query-routing behavior.

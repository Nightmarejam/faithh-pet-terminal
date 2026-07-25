# FAITHH Usage & Redundancy Audit (2026-04-05)

Purpose: identify what is actively consumed vs likely redundant, then prioritize design improvements.

## Evidence snapshot

- Backend registered endpoints (`process_registry.json`): **99**
- Frontend API paths in `ui_polls`: **26**
- UI paths missing in backend map: **0**
- Backend endpoints not referenced by current UI polls: **73**

Interpretation: backend includes broad capability surface; only a subset is exercised by the active UI polling paths.

## What is clearly used

- `faithh_pet_v4.html` polls `/api/plc/state` every 5s (connection strip + PLC readout + status page uses `faithh_status` from the same contract) and uses `/api/usage`.
- `faithh_cockpit.html` uses `/api/plc/state` (with embedded `faithh_status`), `/api/pulse/state`, `/api/compass`, `/faithh_live_state.json`.
- `/api/health` is used by restart and health checks.
- `projects/status/*` assets are now consumed by `dashboard.html` and PLC projection.

## Redundancy / drift risks

### 1) Dual status surfaces in frontend

- `faithh_pet_v4.html` and `faithh_cockpit.html` both present system state.
- They consume overlapping but different endpoint sets.
- Risk: inconsistent status interpretation and duplicate polling logic.

### 2) Duplicate registry location by design

- Source of truth: `docs/architecture/process_registry.json`
- Dashboard snapshot: `projects/status/process_registry.json`
- Risk: stale local snapshot if refresh script is not run.
- Mitigation in place: `scripts/refresh_dashboard_data.sh`.

### 3) Health/status endpoint overlap

- `/health` and `/api/health` both exist; runtime service detail lives under `/api/plc/state` → `faithh_status` (`/api/status` is the same slice, legacy).
- Risk: reduced — in-repo clients and smoke tests target PLC first; external tools may still use `/api/status`.

### 4) Large backend surface vs active UI subset

- Many endpoints are available but not in active UI poll list.
- Not necessarily bad (API supports scripts/tools), but candidates for lifecycle labeling (active/legacy/internal).

## Next-step plan (priority order)

1. **Cockpit contract consolidation** (in progress)
   - `/api/plc/state` is canonical for pet + cockpit status rows; `/api/status` is legacy alias.
   - Next: fold remaining unique data from `/api/pulse/state` / `/api/compass` only where it reduces duplicate polls.

2. **Endpoint lifecycle labels**
   - Add metadata (active/internal/legacy) to `component_map.json` for endpoint components.
   - Use this for release and cleanup decisions.

3. **Polling normalization**
   - Standardize polling intervals and centralize timers per page.
   - Remove duplicate status polls where data is already included in PLC payload.

4. **Operational guardrail**
   - Require `refresh_dashboard_data.sh` before dashboard/review sessions.
   - Add cockpit smoke test script (`scripts/smoke_cockpit.sh`).

5. **Quarterly cleanup pass**
   - Review backend-only endpoints with low/no consumers.
   - Mark keep/deprecate/archive with explicit rationale.

## Immediate action recommendation

- Run `bash scripts/refresh_dashboard_data.sh`
- Run `bash scripts/smoke_cockpit.sh`
- Prefer `curl …/api/plc/state` in docs and new scripts; keep `/api/status` only for backward compatibility.

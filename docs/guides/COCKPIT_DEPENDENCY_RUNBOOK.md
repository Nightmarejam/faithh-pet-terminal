# Cockpit Dependency Runbook

Purpose: keep the cockpit reliable while backend/state code evolves, and give a repeatable path for consolidating duplicated status logic.

## Scope

- Frontend surfaces: `faithh_pet_v4.html` and `faithh_cockpit.html`
- Primary state endpoint: `/api/plc/state`
- Other cockpit endpoints: `/api/pulse/state`, `/api/compass`, `/faithh_live_state.json`. **`/api/status`** is a legacy alias of the `faithh_status` object only; scripts and UIs should call **`/api/plc/state`**.

## Current dependency map

### UI files

- `/` serves `faithh_pet_v4.html`
- `/cockpit` serves `faithh_cockpit.html`

### Cockpit endpoint pings (expected HTTP 200)

- `/cockpit`
- `/api/plc/state`
- `/api/pulse/state`
- `/api/compass`
- `/faithh_live_state.json`
- `/api/health`

## Smoke test (copy/paste)

```bash
cd /home/jonat/ai-stack
bash scripts/refresh_dashboard_data.sh
python3 scripts/impact_analyzer.py --component api_plc_state

for u in /cockpit /api/plc/state /api/pulse/state /api/compass /faithh_live_state.json /api/health; do
  code=$(curl -s -o /tmp/cockpit_ping.json -w "%{http_code}" "http://127.0.0.1:5557$u")
  bytes=$(wc -c < /tmp/cockpit_ping.json)
  echo "$u $code ${bytes}B"
done

curl -s http://127.0.0.1:5557/api/plc/state | python3 -m json.tool | head -80
```

## Ecosystem baseline probe (timing + topology)

After endpoint pings pass, run the scripted probe (also invoked at the end of `scripts/smoke_cockpit.sh` with `--skip-llm`):

```bash
cd /home/jonat/ai-stack
./venv/bin/python scripts/ecosystem_baseline_probe.py
./venv/bin/python scripts/ecosystem_baseline_probe.py --with-rag
```

Writes optional JSON (`--out path.json`). See [docs/architecture/ECOSYSTEM_METRICS.md](../architecture/ECOSYSTEM_METRICS.md) for metric tiers (`wall_ms` vs `response_time` vs `llm_routing.latency_ms`). Operational edges: [docs/data/ecosystem_connections.json](../data/ecosystem_connections.json).

Pass criteria:

- all endpoints return 200
- `/api/plc/state` includes `project_status.summary.next_action`
- `/api/plc/state` includes non-empty `recent_component_changes`
- `/api/plc/state` includes `faithh_status.version` and `faithh_status.services.current_model` (same shape as `/api/status`)

## Consolidation strategy (safe sequence)

### Phase 1 — Stabilize contract (do first)

- Treat `/api/plc/state` as the canonical "cockpit status contract".
- Keep backward-compatible keys while extending payload shape.
- `/api/status` may be retired later; it duplicates `faithh_status` only. Do not remove `/api/pulse/state` until cockpit parity is proven there too.

### Phase 2 — Move cockpit reads

- Migrate `faithh_cockpit.html` to read from `/api/plc/state` for shared status blocks (including `faithh_status` for version / default model / ML chip count and Chroma/Ollama fallbacks when the registry row is missing).
- Keep endpoint-specific modules only where uniquely needed.

### Phase 3 — De-duplicate polling

- Use one polling coordinator per UI page.
- Remove duplicated intervals that poll equivalent state at different cadences.

### Phase 4 — Retire duplicates

- After one full session of stable telemetry:
  - retire duplicated rendering helpers
  - shrink endpoint fanout from cockpit where possible

## Design rules for new cockpit work

- Add state once in backend, consume many times in UI.
- Prefer additive schema changes over breaking key renames.
- Any `/api/plc/state` change must include:
  - `impact_analyzer` check (`--component api_plc_state`)
  - smoke test above
  - `component_map.json` change_log entry

## Related docs

- `docs/guides/MONITORING_SETUP.md`
- `docs/guides/QUICKSTART.md`
- `docs/architecture/FAITHH_USAGE_REDUNDANCY_AUDIT_2026-04-05.md`

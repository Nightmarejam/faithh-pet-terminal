# FAITHH Release Docket

Purpose: consolidate the final decision track for backend behavior, UI feature parity, and trained-model readiness.

## Current context

- ALife pipeline is producing high-fidelity data at scale.
- Multiple model/runtime options are active (baseline and fine-tuned variants).
- UI and backend behavior can diverge when routing/model auto-selection changes.

## Decision objective

Choose one release path:

1. **Proceed with current stack** (baseline model or selected tuned model), or
2. **Hold and patch** specific backend/UI/model issues first.

## Docket items

### 1) Backend review (routing + reliability)

- [ ] Confirm model auto-selection logic and fallback order are deterministic.
- [ ] Verify telemetry/noise warnings are handled (no repeated runtime spam).
- [ ] Validate endpoint health and timeout/retry behavior under ALife load.
- [ ] Confirm output schema stability for experiment and synthesis scripts.

Evidence to capture:
- route logs for representative prompts
- error-rate snapshot
- latency p50/p95 for core interactions

### 2) UI review (feature parity + trust signals)

- [ ] Confirm selected model/chips/sources shown to user match backend reality.
- [ ] Validate source citation display for seeded/synthesized runbook outputs.
- [ ] Ensure critical controls for experiment and synthesis flows are visible and unambiguous.
- [ ] Confirm no stale state after long-running background jobs.
- [ ] Validate cockpit/main UI against `/api/plc/state` (`faithh_status` + mission fields); note any data that still requires `/api/pulse/state` or `/api/compass` only.

Evidence to capture:
- screenshots for key views
- one full user-flow transcript (prompt -> response -> sources)

### 3) Trained model review (final proceed choice)

- [ ] Run structured A/B against baseline and tuned model for same prompt set.
- [ ] Score on: factual grounding, response discipline, actionability, and source alignment.
- [ ] Verify no regression in routing or safety behavior.
- [ ] Choose production default model for current phase.

Evidence to capture:
- evaluation table (`prompt_id`, baseline score, tuned score, winner, notes)
- final model recommendation and rationale

## Final gate (go/no-go)

Proceed only if all are true:

- [ ] Backend reliability checks pass
- [ ] UI parity checks pass
- [ ] Model A/B winner is clear (or baseline retained intentionally)
- [ ] Decision is documented in one synthesis note

## Output artifact for decision

Create one final note when gate closes:

- `docs/research/faithh_release_decision_<date>.md`

It should include:
- chosen model/runtime
- known limitations
- deferred fixes
- next 7-day execution plan


## Related runbooks

- `docs/guides/COCKPIT_DEPENDENCY_RUNBOOK.md`
- `docs/architecture/FAITHH_USAGE_REDUNDANCY_AUDIT_2026-04-05.md`

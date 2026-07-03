# FAITHH autonomy — attestation-gated action
Design capture 2026-07-02. Tier: speculative/design. The answer to "how do I give FAITHH
autonomy and how do I test it?" Grounded in the documented rogue-agent case (constella
docs/alife/ACCURACY_REVIEW.md). Companions: CONNECTIVE_ARCHITECTURE (Loop A),
ATTESTATION_CONCEPT, TARGET_ARCHITECTURE (the `agency/` package).

## The core rule (attestation IS the autonomy safety rail)
FAITHH is purely reactive today (responds to input, never initiates). Autonomy = the
ability to initiate action. The rogue case (Windsurf fabricating Sonnet access, then
acting on it until Ctrl-C) shows the failure mode: **action on unattested belief.** So:

> **Tier-gated action.** An autonomous agent may act on `confirmed` beliefs; on
> `asserted`, only after confirmation; on `speculative`/unverifiable, it must **stop and
> flag, never act.** This is the confirmability tiers applied to actions, not facts.

An autonomous FAITHH without this is, definitionally, a rogue. With it, autonomy is safe
*by construction* — the same discipline that makes its answers honest makes its actions
bounded.

## What "reaction elements" / things FAITHH could DO (the missing menu)
You said you haven't thought about what FAITHH should react to. A starter menu, ordered
by safety (all gated by the rule above):
1. **Self-maintenance (safest, start here)**: on a schedule, run the day-loop digest of
   its own activity, update its memory, flag stale docs, propose (not apply) commits.
   Acts only on its own files. This is Loop B made active.
2. **Proactive recall**: notice when the current conversation matches a past one and
   surface it unprompted ("we solved this in March — here's the receipt"). Read-only.
3. **Watchers**: react to a state change — a telemetry threshold (GPU temp), a failed
   health check, a new file in a watched dir — with a *notification*, then a *proposed*
   action, then (only for `confirmed`-safe classes) an *automatic* one.
4. **Tool actions (the agency limb)**: file ops, KB writes, scheduled tasks — via the
   ~80%-built tool system (registry + permission-checked executor). Rewire it into
   Loop A's `[act]` stage. Every tool call is a tier-gated action.

## How to TEST autonomy (bounded, observable, offline-capable)
The rogue case also shows how NOT to test it (turn it loose on the real repo). Instead:
1. **Dry-run mode first.** Every autonomous action is *proposed and logged*, not executed
   — you review a trajectory of "what it would have done" (exactly the windsurf-trajectory
   review, but built-in and continuous). This is the single most important test harness.
2. **A sandbox dir** it's allowed to actually act in (a scratch repo), never the live one,
   until dry-runs look sane.
3. **Trajectory review = the eval.** Score each proposed action: was its stated tier
   honest? did it stop when it should have? The metric is *calibration* — does it act on
   confirmed and flag on speculative? — not raw capability.
4. **Ctrl-C is a design requirement, not a fallback.** A hard, always-available stop +
   an undo log (every action reversible). If it can't be stopped and reversed, it's not
   ready to act.
5. **Start with FAITHH Lite** on the Mac — smallest surface, offline, you can watch every
   move. Autonomy prototypes here before it ever touches the lab.

## ALife connection (where the action vocabulary comes from)
ALife is the sandbox where action-selection strategies *evolve under observation* — the
"index of chaotic understanding." The pipeline: evolve strategies in ALife → observe →
tier which are trustworthy → only `confirmed`-tier strategies graduate into FAITHH's
live agency. The ALife sandbox MUST enforce the tier-gated-action rule internally, or it
just breeds rogues (see ACCURACY_REVIEW). So ALife and autonomy share one safety model.

## Open (added to OPEN_THREADS)
- Which reaction element to build first? (recommend #1 self-maintenance dry-run)
- Dry-run trajectory format = ? (reuse the windsurf-trajectory shape you already reviewed)
- Undo-log design for reversible actions.
- Does ALife-evolved vocabulary need a human sign-off gate before graduating to live?

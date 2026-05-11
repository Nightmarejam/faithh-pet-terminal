---
handoff_protocol: v1
owner: FAITHH
audience: [claude_code, codex_cli, chatgpt]
principles:
  - one_source_of_truth: "FAITHH project docs + repo state"
  - doc_grounded: true
  - minimal_assumptions: true
  - reversible_changes: true
---

# Handoff Protocol (v1)

This repo uses **handoff documents** as executable intent: concise, grounded, and testable.
A handoff must be usable by another agent **without conversational context**.

## Required Sections
1. **Snapshot** - Date, branch, what's working/broken
2. **Objective** - Outcome + out of scope
3. **Constraints** - Must not break X, no refactors, etc.
4. **Files to Touch** - Exact paths
5. **Implementation Plan** - Numbered steps with success checks
6. **Commands** - Exact commands to run
7. **Acceptance Criteria** - Concrete checks
8. **Rollback Plan** - How to revert

## Formatting Rules
- Prefer bullets over paragraphs
- Label guesses as `ASSUMPTION:`
- Never rely on "as discussed earlier"

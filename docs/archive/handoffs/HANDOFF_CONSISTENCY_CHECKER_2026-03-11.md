# HANDOFF: Consistency Checker Implementation
<!-- 
  For: Windsurf AI
  From: Claude (Sonnet 4.6) + Jonathan
  Date: 2026-03-11
  Task: Validate and wire up the FAITHH consistency checker system
  Archive this to: docs/archive/ after task is complete
-->

## What Was Just Built (Read This First)

Two files were added to the repo today:

1. **`DEPS.md`** (repo root) — A dependency map. When any file changes, this table says what else needs updating. It also documents the embedding space compatibility risk between ML chips and ChromaDB.

2. **`scripts/consistency_checker.py`** — A script that reads all FAITHH state files, extracts key facts (chunk counts, collection name, embedding model, phase), and flags contradictions between them. Outputs human-readable or JSON.

The goal: catch file drift automatically instead of discovering it months later when FAITHH gives wrong answers.

---

## Your Tasks (In Order)

### Task 1: Validate the checker runs without errors

```bash
cd ~/ai-stack
python scripts/consistency_checker.py
```

Expected: It runs and prints a report. It may show MISMATCHes or WARNs — that's fine and expected. What we need to confirm is that it doesn't crash.

If it crashes, the most likely causes are:
- `faithh_memory.json` has an unexpected structure — the extractor tries a few common key paths but may need adjustment
- A file listed in `STATE_FILES` doesn't exist at that path

**Fix approach:** Read the error, identify which extractor function failed (`extract_faithh_memory`, `extract_project_states`, etc.), and adjust the key path. Do NOT restructure the checker — just fix the specific extractor.

**Stop condition:** Script runs to completion without Python exceptions. Report output (even all WARNs/MISMATCHes) is a success for this task.

---

### Task 2: Fix the faithh_memory.json extractor if needed

Run with verbose output to see what was extracted:

```bash
python scripts/consistency_checker.py --json 2>/dev/null | python -m json.tool
```

Check the `values` field for each result. If `faithh_memory` shows `null` for chunk count, collection, or embedding model, the extractor needs to be adjusted to match the actual structure of `faithh_memory.json`.

To see the actual structure:
```bash
python -c "import json; d=json.load(open('faithh_memory.json')); print(list(d.keys()))"
```

Then update `extract_faithh_memory()` in `scripts/consistency_checker.py` to use the correct key paths. The facts we need from it are:
- ChromaDB chunk/document count
- Collection name  
- Embedding model name

**Stop condition:** `faithh_memory` row in JSON output shows actual values, not null, for at least chunk count and embedding model.

---

### Task 3: Run with fix hints and document findings

```bash
python scripts/consistency_checker.py --fix-hints
```

Copy the full output into a new file: `docs/archive/consistency_check_2026-03-11.txt`

This gives Jonathan a snapshot of the current drift state. Do not fix the drift yet — just document it.

**Stop condition:** File saved to docs/archive/. Report and stop.

---

### Task 4: Add DEPS.md reference to AGENTS.md

Open `AGENTS.md` and add one line to the "AI Agent Behavior Rules" section at the bottom:

```
- **Before marking any task complete:** consult `DEPS.md` to identify which other files need updating
```

That's the only change to AGENTS.md. Do not reorganize or rewrite any other section.

**Stop condition:** One line added, file saved. Confirm with `grep "DEPS.md" AGENTS.md`.

---

### Task 5: Commit everything

```bash
git add DEPS.md scripts/consistency_checker.py AGENTS.md docs/archive/consistency_check_2026-03-11.txt
git commit -m "feat: add consistency checker and dependency map

- DEPS.md: change impact registry for all state files
- scripts/consistency_checker.py: fact extraction + cross-file diff
- AGENTS.md: agents must consult DEPS.md before task completion
- docs/archive/: first consistency check snapshot (2026-03-11)

Addresses chronic file drift problem (faithh_memory stale, chip/embedding mismatch risk)"
git push
```

**Stop condition:** Push succeeds. Report commit hash and stop.

---

## What NOT To Do

- Do NOT fix the actual drift/mismatches found by the checker (that's a separate session)
- Do NOT reorganize AGENTS.md beyond the one line addition
- Do NOT move or rename DEPS.md — it lives at repo root
- Do NOT run the checker in a loop — run once, save output, stop
- Do NOT modify project_states.json, faithh_memory.json, or any other state file
- Do NOT install new packages without checking if they're already available

---

## Context You Need

**Repo root:** `~/ai-stack/`  
**Backend:** `faithh_professional_backend_fixed.py` on port 5557  
**ChromaDB:** `http://192.158.1.243:8000` (Gen8 server, may not be reachable from this session)  
**Canonical frontend:** `faithh_pet_v4.html` at ROOT level (not active/frontend/)  
**Key state files:** `project_states.json`, `faithh_memory.json`, `scaffolding_state.json`, `decisions_log.json`

The checker does NOT need ChromaDB to be reachable — it only reads local JSON files.

---

## How To Know You're Done

All 5 tasks complete:
- [ ] Checker runs without Python exceptions
- [ ] faithh_memory extractor returning real values
- [ ] Consistency report saved to docs/archive/
- [ ] One line added to AGENTS.md
- [ ] Committed and pushed

Report back with: task statuses, commit hash, and the full consistency checker output.

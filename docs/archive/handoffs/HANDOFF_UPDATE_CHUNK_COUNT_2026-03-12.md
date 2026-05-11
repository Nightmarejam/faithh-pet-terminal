# HANDOFF: Update Chunk Count Across State Files
<!--
  For: Windsurf AI
  From: Claude + Jonathan
  Date: 2026-03-12
  Archive: docs/archive/ after complete
-->

## Ground Truth (Verified Live)

ChromaDB collection `faithh_knowledge_base` contains **42,370 documents** as of 2026-03-12.

Current stale values across files:
- `faithh_memory.json` → 32,499 (wrong)
- `project_states.json` → 37,000 (wrong)
- `systems_map.md` → 32,499 (wrong)
- `README.md` → 32,499 (wrong, also shows "32K chunks" in table)
- `CONTEXT.md` → generated file, do NOT edit directly

---

## Your Tasks (In Order)

### Task 1: Update faithh_memory.json

Find the `knowledge_base_status` key. Update:
```
"total_documents": 42370
```
Also update the breakdown note if it references the old count. Do NOT change any other fields.

Verify with:
```bash
python3 -c "import json; d=json.load(open('faithh_memory.json')); print(d['knowledge_base_status']['total_documents'])"
```
Expected output: `42370`

**Stop condition:** Command prints `42370`. Move on.

---

### Task 2: Update project_states.json

Find `projects.FAITHH.infrastructure.chunks_indexed`. Change to `42370`.

Also find `projects.FAITHH.summary` — it likely mentions a chunk count in the text. Update that number too.

Also update `last_updated` at the top level to `"2026-03-12"`.

Verify with:
```bash
python3 -c "import json; d=json.load(open('project_states.json')); print(d['projects']['FAITHH']['infrastructure']['chunks_indexed'])"
```
Expected output: `42370`

**Stop condition:** Command prints `42370`. Move on.

---

### Task 3: Update SYSTEMS_MAP.md

Search for `32499` or `32,499` in SYSTEMS_MAP.md. Replace all occurrences with `42370`.

Search for `37000` or `37,000`. Replace all occurrences with `42370`.

Also update `last_verified` in the front matter to `"2026-03-12"`.

Verify with:
```bash
grep -n "32499\|32,499\|37000\|37,000" SYSTEMS_MAP.md
```
Expected output: no matches.

**Stop condition:** grep returns no matches. Move on.

---

### Task 4: Update README.md

Search for any mention of `32,499`, `32499`, `37,000`, `37000`, or `32K` in README.md.
Replace chunk count references with `42,370` (use comma format in README for readability).

Verify with:
```bash
grep -n "32499\|32,499\|37000\|37,000\|32K" README.md
```
Expected output: no matches.

**Stop condition:** grep returns no matches. Move on.

---

### Task 5: Regenerate CONTEXT.md

```bash
cd ~/ai-stack && source venv/bin/activate && python3 scripts/generate_context.py
```

If that script errors or doesn't exist at that path, skip this task and note it.

**Stop condition:** Script completes without error, OR error is noted and task skipped.

---

### Task 6: Run consistency checker to confirm

```bash
cd ~/ai-stack && source venv/bin/activate && python3 scripts/consistency_checker.py
```

The ChromaDB chunk count MISMATCH should now be gone or reduced.
Note any remaining mismatches — do NOT fix them, just report.

**Stop condition:** Checker runs, output recorded.

---

### Task 7: Commit

```bash
git add faithh_memory.json project_states.json SYSTEMS_MAP.md README.md CONTEXT.md
git commit -m "fix: sync chunk count to live ChromaDB value (42370)

Live count verified 2026-03-12 via chromadb.HttpClient.
Previous values were stale: faithh_memory=32499, project_states=37000, systems_map=32499.
All state files now consistent at 42370."
git push
```

**Stop condition:** Push succeeds. Report commit hash and stop.

---

## What NOT To Do

- Do NOT run a reindex
- Do NOT modify any other fields beyond chunk counts and last_updated dates
- Do NOT edit CONTEXT.md directly — only regenerate it via the script
- Do NOT change the embedding model, collection name, or any other values
- Do NOT fix any other mismatches found by the checker — just report them

## Done When

- [ ] faithh_memory.json shows 42370
- [ ] project_states.json shows 42370
- [ ] SYSTEMS_MAP.md has no old chunk count references
- [ ] README.md has no old chunk count references
- [ ] Consistency checker run, output noted
- [ ] Committed and pushed

Report back: commit hash + full consistency checker output.

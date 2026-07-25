# HANDOFF: ChromaDB Audit + Collection Router
<!--
  For: Windsurf AI
  From: Claude + Jonathan
  Date: 2026-03-12
  Priority: HIGH — run audit FIRST before any restructuring
  Archive: docs/archive/ after complete
-->

## Context

The FAITHH ChromaDB collection (faithh_knowledge_base, 42,370 chunks) contains
mixed signal and noise — conversations, health logs, git commits, terminal commands,
and actual project knowledge all in one flat collection. Three files were written
by Claude and need to be deployed:

1. `scripts/chroma_audit.py`        — samples chunks, classifies signal vs noise
2. `faithh_collection_rules.yaml`   — config-driven collection routing rules
3. `scripts/collection_router.py`   — adaptive router with dynamic provisioning

These files have been downloaded to the repo root by Jonathan.
Move them to correct locations as first step.

---

## Task 1: Move files to correct locations

```bash
cd ~/ai-stack

# chroma_audit.py should already be in scripts/ — verify
ls scripts/chroma_audit.py

# collection_router.py should already be in scripts/ — verify  
ls scripts/collection_router.py

# faithh_collection_rules.yaml should be at repo root — verify
ls faithh_collection_rules.yaml
```

If any files are in the wrong place, move them:
```bash
mv chroma_audit.py scripts/
mv collection_router.py scripts/
# faithh_collection_rules.yaml stays at root
```

Install pyyaml if not present:
```bash
source venv/bin/activate
pip show pyyaml || pip install pyyaml
```

**Stop condition:** All three files at correct paths. pyyaml available. Move on.

---

## Task 2: Run the audit (READ ONLY — nothing is modified)

```bash
cd ~/ai-stack && source venv/bin/activate

python3 scripts/chroma_audit.py --sample 500 --verbose --export
```

This will:
- Sample 500 random chunks from ChromaDB
- Classify each as signal or noise
- Print a full report with type breakdown
- Export labeled samples to docs/archive/chroma_audit_2026-03-12.json

The export file becomes training data for the future ML classifier.

**Stop condition:** Script completes, report printed, JSON exported to docs/archive/.
Save the FULL console output — Jonathan needs to see the signal% number.
Do NOT proceed to Task 3 until audit is complete and output is saved.

---

## Task 3: Save audit output

```bash
python3 scripts/chroma_audit.py --sample 500 --export 2>&1 | tee docs/archive/chroma_audit_console_2026-03-12.txt
```

**Stop condition:** Console output saved to docs/archive/. Move on.

---

## Task 4: Check collection router status (READ ONLY)

```bash
python3 scripts/collection_router.py --status
```

This shows what collections currently exist and their chunk counts.
It does NOT create or modify anything.

```bash
python3 scripts/collection_router.py --audit-quarantine
```

This shows the quarantine collection (likely empty or doesn't exist yet — that's fine).

**Stop condition:** Both commands run, output noted. Move on.

---

## Task 5: TTL sweep dry run (READ ONLY)

```bash
python3 scripts/collection_router.py --ttl-sweep --dry-run
```

This shows how many chunks would be deleted by TTL sweep without deleting anything.
If the number is 0, that's expected — existing chunks don't have expires_at metadata yet.

**Stop condition:** Command runs, output noted. Move on.

---

## Task 6: Add TTL sweep to cron (nightly)

```bash
crontab -e
```

Add this line:
```
# FAITHH TTL sweep — nightly cleanup of expired chunks
0 4 * * * cd /home/jonat/ai-stack && /home/jonat/ai-stack/venv/bin/python3 scripts/collection_router.py --ttl-sweep >> /home/jonat/ai-stack/logs/ttl_sweep.log 2>&1
```

Ensure logs directory exists:
```bash
mkdir -p ~/ai-stack/logs
```

Verify:
```bash
crontab -l | grep ttl
```

**Stop condition:** TTL sweep cron line appears in crontab. Move on.

---

## Task 7: Commit everything

```bash
cd ~/ai-stack
git add scripts/chroma_audit.py scripts/collection_router.py \
        faithh_collection_rules.yaml \
        docs/archive/chroma_audit_2026-03-12.json \
        docs/archive/chroma_audit_console_2026-03-12.txt

git commit -m "feat: ChromaDB audit + adaptive collection router

- chroma_audit.py: samples + classifies signal vs noise in existing DB
- collection_router.py: routes new chunks to correct collections
- faithh_collection_rules.yaml: config-driven routing rules (no code changes needed)
- First audit snapshot saved to docs/archive/
- TTL sweep cron added (nightly at 4am)

Option C implementation: metadata-first, collection split to follow
based on audit findings."

git push
```

**Stop condition:** Push succeeds. Report commit hash and STOP.

---

## What NOT To Do

- Do NOT delete any chunks from ChromaDB
- Do NOT run the router on existing data (yet — that comes after Jonathan reviews audit)
- Do NOT run TTL sweep without --dry-run flag (except the cron, which is safe)
- Do NOT modify faithh_collection_rules.yaml (Jonathan will review first)
- Do NOT create new ChromaDB collections manually
- Do NOT reindex anything

## Done When

- [ ] All 3 files at correct paths
- [ ] Audit run with --sample 500 --export
- [ ] Console output saved to docs/archive/
- [ ] Collection router --status and --audit-quarantine run
- [ ] TTL sweep dry run noted
- [ ] TTL sweep added to cron (nightly 4am)
- [ ] Committed and pushed

## Report Back

1. Commit hash
2. The SIGNAL% number from the audit headline
3. Top 3 detected types by count
4. Full audit console output

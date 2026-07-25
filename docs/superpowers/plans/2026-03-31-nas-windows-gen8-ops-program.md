# NAS + Windows + Gen8 Ops Program Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up a repeatable 30-day workflow that keeps NAS, Windows, and Gen8 reliable while enforcing clean data separation and low-noise ingestion into governance/ALife/Constella lanes.

**Architecture:** Use three parallel tracks with strict handoffs: (1) service reliability (Plex/Plexamp + access), (2) data governance (classification + allowlist), and (3) curation/ingestion quality (approved-only indexing + drift validation). All ingestion is report-backed and non-destructive.

**Tech Stack:** Python scripts, CSV inventories, ChromaDB indexing/validation scripts, SSH-based NAS access, existing FAITHH ingestion pipeline docs/scripts.

---

### Task 1: Week 1 Baseline and Device Reliability Gates

**Files:**
- Modify: `docs/architecture/SYSTEM_TRANSPARENCY_IMPLEMENTATION_CHECKLIST.md`
- Modify: `docs/SYSTEM_AUDIT_2026_03_30.md`
- Create: `reports/index_runs/2026-03-31_week1_device_baseline.md`

- [ ] **Step 1: Capture NAS/Windows/Gen8 identity and service baseline**

Run:
`ssh nas "hostname && uname -a"`
`hostname`
`python3 - <<'PY'
print("Capture Gen8/Plex baseline manually if remote host differs from NAS alias.")
PY`

Expected: All three execution surfaces are identified and documented.

- [ ] **Step 2: Record current service state for Plex/Plexamp path**

Run:
`python3 - <<'PY'
print("Document where Plex/Plexamp are hosted, mount roots, and expected media paths.")
PY`

Expected: A single source of truth table for service host, storage path, and dependency path.

- [ ] **Step 3: Define pass/fail reliability gates**

Add to `reports/index_runs/2026-03-31_week1_device_baseline.md`:
- health gate (disk and volume status clean)
- access gate (WSL + Windows + NAS path checks pass)
- ingest gate (allowlist-only run possible)

- [ ] **Step 4: Commit**

```bash
git add docs/architecture/SYSTEM_TRANSPARENCY_IMPLEMENTATION_CHECKLIST.md docs/SYSTEM_AUDIT_2026_03_30.md reports/index_runs/2026-03-31_week1_device_baseline.md
git commit -m "docs: define week-1 reliability gates for NAS Windows Gen8"
```

### Task 2: Week 2 Data Separation and Inventory Control

**Files:**
- Modify: `reports/inventory/nas_classification_queue.csv`
- Modify: `reports/inventory/nas_move_plan.csv`
- Modify: `docs/architecture/NAS_TARGET_LAYOUT.md`

- [ ] **Step 1: Re-run inventory export and rebuild classification queue**

Run:
`python3 scripts/export_nas_inventory_via_ssh.py --output reports/inventory/nas_full_inventory.csv`
`python3 scripts/build_nas_classification_queue.py --input reports/inventory/nas_full_inventory.csv --output reports/inventory/nas_classification_queue.csv`

Expected: Classification queue includes required columns and current NAS state.

- [ ] **Step 2: Review/approve only non-personal governance/ALife/Constella rows**

Run:
`python3 scripts/approve_nas_ingest_candidates.py --input reports/inventory/nas_classification_queue.csv --output reports/inventory/nas_classification_queue.csv --max-approve 150 --min-score 1.5`
`python3 scripts/build_nas_move_plan.py --input reports/inventory/nas_classification_queue.csv --output reports/inventory/nas_move_plan.csv`

Expected: Move plan remains non-destructive, personal rows remain blocked.

- [ ] **Step 3: Validate separation policy text**

Update `docs/architecture/NAS_TARGET_LAYOUT.md` with any new roots discovered and keep copy+verify language.

- [ ] **Step 4: Commit**

```bash
git add reports/inventory/nas_classification_queue.csv reports/inventory/nas_move_plan.csv docs/architecture/NAS_TARGET_LAYOUT.md
git commit -m "chore: refresh NAS classification and non-destructive move planning"
```

### Task 3: Week 3 Controlled Ingestion and Staging Discipline

**Files:**
- Modify: `reports/inventory/nas_ingest_allowlist.csv`
- Modify: `docs/data/governance_sources/nas_import/` (staged files)
- Modify: `docs/data/alife_sources/nas_import/` (staged files)
- Modify: `docs/data/constella_sources/nas_import/` (staged files)
- Create: `reports/index_runs/candidate_acceptance_report_<timestamp>.json`

- [ ] **Step 1: Build allowlist from approved rows**

Run:
`python3 scripts/build_nas_ingest_allowlist.py --input reports/inventory/nas_classification_queue.csv --output reports/inventory/nas_ingest_allowlist.csv`

Expected: Allowlist excludes personal/private and includes only approved ingestion scopes.

- [ ] **Step 2: Stage allowlist-backed files into local intake roots**

Run:
`python3 scripts/stage_nas_allowlist_files.py --allowlist reports/inventory/nas_ingest_allowlist.csv --intake-root docs/data --ssh-host nas --limit 200`

Expected: Staged files are present in governance/alife/constella intake subfolders.

- [ ] **Step 3: Produce candidate acceptance report**

Run:
`python3 - <<'PY'
import csv, json
from datetime import datetime, UTC
from pathlib import Path
rows=list(csv.DictReader(open("reports/inventory/nas_ingest_allowlist.csv",encoding="utf-8")))
report={"timestamp_utc":datetime.now(UTC).isoformat(),"allowlist_rows":len(rows)}
out=Path("reports/index_runs")/f"candidate_acceptance_report_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json"
out.write_text(json.dumps(report,indent=2),encoding="utf-8")
print(out)
PY`

Expected: Candidate acceptance artifact exists in `reports/index_runs/`.

- [ ] **Step 4: Commit**

```bash
git add reports/inventory/nas_ingest_allowlist.csv docs/data/governance_sources/nas_import docs/data/alife_sources/nas_import docs/data/constella_sources/nas_import reports/index_runs/candidate_acceptance_report_*.json
git commit -m "feat: stage approved NAS allowlist data for controlled ingestion"
```

### Task 4: Week 4 Validation, Drift Lock, and Monthly Runbook

**Files:**
- Create: `reports/index_runs/validation_<timestamp>.json`
- Create: `reports/index_runs/nas_guardrail_decision_<timestamp>.json`
- Create: `docs/guides/NAS_MONTHLY_OPERATIONS_RUNBOOK.md`

- [ ] **Step 1: Run governance + ALife/Constella ingestion**

Run:
`python3 scripts/index_governance_corpus.py --input-root docs/data/governance_sources/nas_import --report-dir reports/index_runs`
`python3 scripts/index_staged_nas_sources.py --intake-root docs/data`

Expected: Ingestion reports are emitted with accepted/skipped counts.

- [ ] **Step 2: Run retrieval validation with baseline drift check**

Run:
`python3 scripts/validate_data_aggregation_pipeline.py --baseline reports/index_runs/validation_20260331_000426.json --output reports/index_runs/validation_$(date +%Y%m%d_%H%M%S).json`

Expected: Validation report includes source mix and drift deltas for the three query classes.

- [ ] **Step 3: Write guardrail decision and runbook**

Document:
- keep/tighten allowlist filters
- whether personal/business bleed appeared
- next cycle thresholds and escalation criteria

Expected: A monthly runbook exists and guardrail decision is auditable.

- [ ] **Step 4: Commit**

```bash
git add reports/index_runs/validation_*.json reports/index_runs/nas_guardrail_decision_*.json docs/guides/NAS_MONTHLY_OPERATIONS_RUNBOOK.md
git commit -m "docs: establish monthly NAS ingestion validation and guardrails"
```

### Task 5: Ongoing Operating Rhythm (Post 30-Day)

**Files:**
- Modify: `docs/guides/NAS_MONTHLY_OPERATIONS_RUNBOOK.md`
- Modify: `reports/index_runs/` (new cycle artifacts)

- [ ] **Step 1: Weekly 20-minute checkpoint**
- [ ] **Step 2: Monthly full ingest + validation cycle**
- [ ] **Step 3: Quarterly prune/archive of low-value data**
- [ ] **Step 4: Record lessons learned and adjust thresholds**

Run:
`python3 scripts/validate_data_aggregation_pipeline.py --output reports/index_runs/validation_$(date +%Y%m%d_%H%M%S).json`

Expected: Stable, repeatable operation with low-noise retrieval and clear personal/business separation.

# NAS monthly operations runbook

Practical cadence for NAS → local staging → Chroma indexing → validation → guardrails. Aligns with `docs/superpowers/plans/2026-03-31-nas-windows-gen8-ops-program.md` Week 3–4 flow and **post-30-day** steady-state ops.

## Post-30-day operating rhythm

| Cadence | Timebox | Purpose | Primary artifacts |
|--------|---------|---------|-------------------|
| **Weekly** | ~20 min | Access/queue sanity; optional drift snapshot | `reports/index_runs/validation_*.json` (if spot-check), notes in latest `nas_guardrail_decision_*.json` or next monthly file |
| **Monthly** | ~1–2 h | Full inventory → allowlist → stage → index → validate vs baseline | `reports/inventory/*.csv`, `reports/index_runs/*_report_*.json`, `validation_*.json`, `nas_guardrail_decision_*.json` |
| **Quarterly** | ~30–60 min | Prune/archive low-value staged copies; refresh separation | `docs/archive/nas_pruned_<YYYY-Qn>/` (moved trees), refreshed CSVs under `reports/inventory/` |
| **Lessons / thresholds** | After each monthly (or when drift fires) | Record what changed; adjust scores and filters | `nas_guardrail_decision_*.json`, optional `decisions_log.json`, `docs/architecture/RETRIEVAL_FILTER_PROFILE.md` |

## Preconditions

- SSH alias `nas` works from the workstation used for staging.
- ChromaDB reachable where your scripts expect it:
  - **`index_governance_corpus.py` / `index_staged_nas_sources.py`:** `--host` / `--port` default from `CHROMA_HOST` / `CHROMA_PORT`, else host `servicebox.taileb8c60.ts.net` and port `8000`.
  - **`validate_data_aggregation_pipeline.py`:** defaults are **hardcoded** in the script — host `servicebox.taileb8c60.ts.net`, port `8000` — unless you pass `--host` and `--port` (this script does **not** read `CHROMA_HOST` / `CHROMA_PORT`).
- Repo Python venv: `./venv/bin/python` (has `chromadb`, `sentence-transformers`).

## Weekly 20-minute checkpoint

Target: **~20 minutes**, no full re-ingest unless something is wrong.

1. **Disk and access (5 min):** Confirm NAS mounts and WSL/Windows paths still match the gates in `reports/index_runs/2026-03-31_week1_device_baseline.md` (or your current baseline doc). Quick SSH:

   ```bash
   ssh nas "hostname && df -h | head -20"
   ```

2. **Queue hygiene (10 min):** Open `reports/inventory/nas_classification_queue.csv`. Skim new or changed rows; **do not** approve personal/private. If the queue is stale, note “needs monthly refresh” — do not half-run approval without a fresh inventory.

3. **Optional drift snapshot (5 min):** If you want a timestamped mix without comparing to baseline:

   ```bash
   ./venv/bin/python scripts/validate_data_aggregation_pipeline.py \
     --host servicebox.taileb8c60.ts.net --port 8000 \
     --output reports/index_runs/validation_$(date +%Y%m%d_%H%M%S).json
   ```

   (Flags shown explicitly: omitting them still uses the script’s built-in defaults above — not your shell env.)

   Store the path in your working notes or the **next** monthly `nas_guardrail_decision_*.json` under a `weekly_spot_validations` array if you keep structured JSON there.

## Monthly full ingest + validation cycle

Full pipeline: inventory → classification → approval → allowlist → stage → index → validate vs baseline → guardrail decision.

### 1. Inventory and allowlist

```bash
./venv/bin/python scripts/export_nas_inventory_via_ssh.py --output reports/inventory/nas_full_inventory.csv
./venv/bin/python scripts/build_nas_classification_queue.py \
  --input reports/inventory/nas_full_inventory.csv \
  --output reports/inventory/nas_classification_queue.csv
# Approve only non-personal governance / ALife / Constella candidates (adjust flags as needed)
./venv/bin/python scripts/approve_nas_ingest_candidates.py \
  --input reports/inventory/nas_classification_queue.csv \
  --output reports/inventory/nas_classification_queue.csv \
  --max-approve 150 --min-score 1.5
./venv/bin/python scripts/build_nas_move_plan.py \
  --input reports/inventory/nas_classification_queue.csv \
  --output reports/inventory/nas_move_plan.csv
./venv/bin/python scripts/build_nas_ingest_allowlist.py \
  --input reports/inventory/nas_classification_queue.csv \
  --output reports/inventory/nas_ingest_allowlist.csv
```

### 2. Stage allowlist files locally

Default **`--extensions`** on `stage_nas_allowlist_files.py` is `.md`, `.txt`, `.json`, `.yaml`, `.yml`, `.csv` — **`.pdf` is excluded** unless you widen the list. Each run writes a manifest to `reports/index_runs/nas_stage_manifest_<YYYYMMDD_HHMMSS>.json` (unless you pass `--manifest`).

```bash
./venv/bin/python scripts/stage_nas_allowlist_files.py \
  --allowlist reports/inventory/nas_ingest_allowlist.csv \
  --intake-root docs/data \
  --ssh-host nas \
  --limit 200
```

To include PDFs (and keep the same non-PDF types):

```bash
./venv/bin/python scripts/stage_nas_allowlist_files.py \
  --allowlist reports/inventory/nas_ingest_allowlist.csv \
  --intake-root docs/data \
  --ssh-host nas \
  --limit 200 \
  --extensions .md .txt .json .yaml .yml .csv .pdf
```

Intake roots:

- `docs/data/governance_sources/nas_import/`
- `docs/data/alife_sources/nas_import/`
- `docs/data/constella_sources/nas_import/`

### 3. Index staged corpora

Governance (NAS import subtree only):

```bash
./venv/bin/python scripts/index_governance_corpus.py \
  --input-root docs/data/governance_sources/nas_import \
  --report-dir reports/index_runs
```

ALife + Constella seeds:

```bash
./venv/bin/python scripts/index_staged_nas_sources.py \
  --intake-root docs/data \
  --report-dir reports/index_runs
```

Expect `governance_ingest_report_<timestamp>.json` and `staged_nas_index_report_<timestamp>.json` under `reports/index_runs/`. Those reports include scanned/skipped files, chunk counts, upserts, per-domain counts, stale chunk cleanup, and errors.

### 4. Validation with baseline drift

Use the **program baseline** (e.g. `reports/index_runs/validation_20260331_000426.json`) or **last month’s** `validation_*.json`. Emit a new report:

```bash
./venv/bin/python scripts/validate_data_aggregation_pipeline.py \
  --host servicebox.taileb8c60.ts.net --port 8000 \
  --baseline reports/index_runs/validation_20260331_000426.json \
  --output reports/index_runs/validation_$(date +%Y%m%d_%H%M%S).json
```

Override `--host` / `--port` if your Chroma instance differs; the validator does not pick up `CHROMA_HOST` / `CHROMA_PORT` from the environment.

Review `source_mix_drift_vs_baseline` per query class (`governance_principle`, `alife_mechanism`, `constella_constitutional`).

### 5. Guardrail decision artifact (end of monthly)

After reviewing the validation JSON, write:

- **Path:** `reports/index_runs/nas_guardrail_decision_<YYYYMMDD_HHMMSS>.json` (or `.md` if you prefer human-first; JSON keeps parity with the program plan).
- **Include:** pointer to the validation file used, keep vs tighten allowlist filters, any personal/business bleed, **next-cycle** `--min-score` / `--max-approve` intent, escalation criteria.

**Noise / drift escalation:** If governance-shaped queries gain large `nas_seeded_document` share **and** quality drops, or if `business` / unrelated `technical` hits rise vs baseline, tighten filters per the latest guardrail file and `docs/architecture/RETRIEVAL_FILTER_PROFILE.md`.

## Quarterly prune and archive of low-value data

Target: **end of quarter** (or when disk/noise justifies it). Operate only on **local staged copies** under `docs/data/*/nas_import/` — NAS source policy remains copy+verify per `docs/architecture/NAS_TARGET_LAYOUT.md`.

1. **Identify low-value paths:** From monthly index reports (`*_ingest_report_*.json`, `staged_nas_index_report_*.json`), repeated skips, or manual review — list trees/files that should not return in retrieval.

2. **Remove from allowlist first:** Edit or regenerate `reports/inventory/nas_ingest_allowlist.csv` / classification queue so pruned content is not re-staged next month.

3. **Archive local copies (non-destructive to NAS):**

   ```bash
   # Example: create quarter folder and move a subtree (replace LOW_VALUE_DIR)
   mkdir -p "docs/archive/nas_pruned_2026-Q2"
   # git mv: only for paths already tracked by git; preserves history in-repo.
   # Untracked trees: use mv, then git add / git rm as appropriate.
   git mv "docs/data/governance_sources/nas_import/LOW_VALUE_DIR" "docs/archive/nas_pruned_2026-Q2/"
   ```

   Quote paths that contain spaces or odd characters. If a path is not in the index, `git mv` will error — use ordinary `mv` and stage the result explicitly.

4. **Refresh inventory** so the classification queue matches NAS reality (same commands as monthly §1 through `build_nas_classification_queue.py`).

5. **Optional:** Run validation after prune to confirm mix:

   ```bash
   ./venv/bin/python scripts/validate_data_aggregation_pipeline.py \
     --host servicebox.taileb8c60.ts.net --port 8000 \
     --baseline reports/index_runs/validation_<previous_quarter_pick>.json \
     --output reports/index_runs/validation_$(date +%Y%m%d_%H%M%S).json
   ```

**Artifact:** Keep a short **quarterly note** (same directory or `reports/index_runs/nas_quarterly_prune_<YYYY-Qn>.md`) listing what moved, why, and which allowlist version applies.

## Lessons learned and threshold adjustment loop

Close the loop **after each monthly validation** (or immediately when drift thresholds trip):

1. **Capture:** Append to the monthly `nas_guardrail_decision_*` file (or a short `reports/index_runs/nas_ops_lessons_<YYYY-MM>.md`): what drifted, what you changed, what you rejected (personal bleed, noisy domains).

2. **Adjust ingestion thresholds:** Next month’s `approve_nas_ingest_candidates.py` run — change `--min-score` and/or `--max-approve` **only** with rationale recorded in the guardrail artifact (avoid silent score creep).

3. **Adjust retrieval filters:** If the fix is query-side metadata or profile tightening, update `docs/architecture/RETRIEVAL_FILTER_PROFILE.md` and note the validation file that justified it.

4. **Architecture / policy decisions:** For durable repo decisions (e.g. lane separation, baseline rotation), add an entry to `decisions_log.json` with `rationale`, `alternatives_considered`, `impact`, `status` per `AGENTS.md`.

5. **Rotate baseline intentionally:** When you accept a new steady state, designate that month’s `validation_*.json` as the new drift baseline in the next run’s `--baseline` argument and record the path in the guardrail JSON.

## Artifact locations

| Artifact | Location |
|----------|----------|
| NAS full inventory / queue / move plan / allowlist | `reports/inventory/nas_full_inventory.csv`, `nas_classification_queue.csv`, `nas_move_plan.csv`, `nas_ingest_allowlist.csv` |
| Staged intake (live) | `docs/data/governance_sources/nas_import/`, `docs/data/alife_sources/nas_import/`, `docs/data/constella_sources/nas_import/` |
| Quarterly pruned trees (archived) | `docs/archive/nas_pruned_<YYYY-Qn>/` (convention) |
| Governance ingest reports | `reports/index_runs/governance_ingest_report_*.json` |
| Staged ALife/Constella index runs | `reports/index_runs/staged_nas_index_report_*.json` |
| Validation runs | `reports/index_runs/validation_*.json` |
| Guardrail decisions | `reports/index_runs/nas_guardrail_decision_*.json` |
| **Stage run manifest (always from `stage_nas_allowlist_files.py`)** | `reports/index_runs/nas_stage_manifest_<YYYYMMDD_HHMMSS>.json` |
| **Candidate acceptance report (optional / manual)** | `reports/index_runs/candidate_acceptance_report_*.json` — not emitted by staging or indexing; create only if you follow the ops-program snippet to record allowlist acceptance |
| Optional lessons log | `reports/index_runs/nas_ops_lessons_<YYYY-MM>.md` |
| Optional quarterly prune log | `reports/index_runs/nas_quarterly_prune_<YYYY-Qn>.md` |

## References

- `docs/architecture/NAS_TARGET_LAYOUT.md` — separation and copy-verify policy
- `docs/architecture/ACTIVE_INDEXING_PIPELINE.md` — pipeline context
- `docs/architecture/RETRIEVAL_FILTER_PROFILE.md` — tightening retrieval when drift is noisy

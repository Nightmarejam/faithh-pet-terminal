# RunBook Synthesis MVP

This guide covers the manual-first pipeline that seeds RunBook drafts from semantic search, plus an optional post-experiment hook.

## Components

- Schema: `docs/data/runbook_seed_schema.json`
- Example payload: `docs/data/runbook_seed_example.json`
- Core synthesis library: `scripts/runbook_seed_core.py`
- Manual CLI: `scripts/runbook_seed_from_search.py`
- Optional post-experiment wrapper: `scripts/runbook_seed_after_experiment.py`

## Manual CLI usage

```bash
cd /home/jonat/ai-stack && source venv/bin/activate
python3 scripts/runbook_seed_from_search.py \
  --query "alife governance experiment execution" \
  --max-chunks 8 \
  --collections "faithh_knowledge_base_v2" \
  # alife_lineage was exported to SQLite and deleted 2026-07-30; naming it fails.
  --output-dir reports/runbook_seeds
```

Outputs:

- `runbook_seed_<timestamp>.json`
- `runbook_seed_<timestamp>.md`

## Optional post-experiment hook

Disabled by default. Must pass `--enable`.

```bash
cd /home/jonat/ai-stack && source venv/bin/activate
python3 scripts/runbook_seed_after_experiment.py \
  --enable \
  --report reports/alife/band2_generation8_n0p4_r01_20260402_100353.json \
  --collections "faithh_knowledge_base_v2" \
  --output-dir reports/runbook_seeds
```

If `--query` is omitted, the wrapper infers a query from the report.

## Validation checks

Each seed JSON includes a `validation` block:

- `required_fields_ok`
- `source_evidence_non_empty`
- `step_count_ok` (3 to 12 suggested steps)
- `issues` list

These checks are applied during generation and written into the output.

## Future stacking extension fields

The schema already includes optional fields under `future_stacking`:

- `suggested_prereq_ids`
- `suggested_next_ids`
- `learning_objective_tags`

These fields are placeholders for later path assembly logic in `runbook-to-rule-them-all/runbooks/index.md`.


## Operational companion runbooks

- Cockpit and status-layer checks: `docs/guides/COCKPIT_DEPENDENCY_RUNBOOK.md`
- System usage and redundancy findings: `docs/architecture/FAITHH_USAGE_REDUNDANCY_AUDIT_2026-04-05.md`

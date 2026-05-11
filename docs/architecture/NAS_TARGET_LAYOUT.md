# NAS Target Layout (Tag-First, Non-Destructive)

Last updated: 2026-03-31

## Destination map

- `/volume1/projects/governance_corpus/`
- `/volume1/projects/alife_corpus/`
- `/volume1/projects/constella_corpus/`
- `/volume1/projects/shared_reference/`

Personal data remains under existing personal roots and is excluded from initial ingestion.

## Execution policy

- No destructive rename/delete.
- Copy then verify.
- Require checksum validation before considering source cleanup.
- All ingestion is allowlist-driven from reviewed rows.

## Move planning artifacts

- `reports/inventory/nas_classification_queue.csv`
- `reports/inventory/nas_move_plan.csv`
- `reports/inventory/nas_ingest_allowlist.csv`

# Governance Source Corpus (Canonical Input)

Place governance source materials here for ingestion into the constitutional lane.

## Intended source classes

- `charter` (constitutions, charters)
- `treaty` (UN declarations, conventions, accords)
- `policy_reference` (governance frameworks, standards, legal references)
- `analysis` (research notes, comparative governance analysis)

## Suggested structure

- `docs/data/governance_sources/charters/`
- `docs/data/governance_sources/treaties/`
- `docs/data/governance_sources/policy_references/`
- `docs/data/governance_sources/analysis/`

## Accepted formats

- `.md`, `.txt`, `.json`, `.yaml`, `.yml`, `.csv`

## Notes

- Keep one document per source artifact where possible.
- Preserve provenance in filename and/or frontmatter when available.
- This folder is the canonical input root for `scripts/index_governance_corpus.py`.

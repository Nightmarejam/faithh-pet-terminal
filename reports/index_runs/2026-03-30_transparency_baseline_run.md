# Transparency Baseline Run — 2026-03-30

## Completed in this run

- Added `docs/architecture/SYSTEM_TRANSPARENCY_IMPLEMENTATION_CHECKLIST.md`
- Created output folders:
  - `reports/perf/wsl`
  - `reports/perf/windows`
  - `reports/perf/nas`
  - `reports/inventory`
  - `reports/index_runs`
- Captured WSL baseline artifacts:
  - `reports/perf/wsl/free_20260330_163256.txt`
  - `reports/perf/wsl/df_20260330_163256.txt`
  - `reports/perf/wsl/iostat_20260330_163256.txt`
  - `reports/perf/wsl/pidstat_20260330_163256.txt`
- Exported first inventories:
  - `reports/inventory/windows_inventory.csv` (8431 rows, `/mnt/c/Users/jonat/Downloads`)
  - `reports/inventory/nas_inventory.csv` (53 rows, `/mnt/z`)
  - `reports/inventory/combined_inventory.csv` (8484 rows)
- Generated first candidate list:
  - `reports/inventory/index_candidates_governance_alife.csv` (2 rows)

## Findings

- `iostat` and `pidstat` are not installed in WSL (`sysstat` missing), so two baseline files currently contain install guidance.
- NAS mount `/mnt/z` is reachable and currently appears to expose:
  - `/mnt/z/AI/backups`
  - `/mnt/z/Business/TomCatSound_LLC`
- Current inventory scope is intentionally narrow and should be expanded to additional roots before index curation.

## Next execution steps

1. Install WSL perf tools (`sysstat`) and repeat baseline capture.
2. Expand Windows inventory beyond Downloads (Documents/Desktop/archives).
3. Expand NAS inventory to all mounted shares/roots.
4. Rebuild `index_candidates_governance_alife.csv` after expanded inventory.
5. Review candidate CSV and set `include_for_index=yes/no` before indexing session.

---

## Follow-up execution (same day)

### Completed

- Expanded Windows inventory roots:
  - `/mnt/c/Users/jonat/Documents` -> `reports/inventory/windows_documents_inventory.csv` (400 rows)
  - `/mnt/c/Users/jonat/Desktop` -> `reports/inventory/windows_desktop_inventory.csv` (400 rows)
  - `/mnt/c/Users/jonat/Downloads` -> `reports/inventory/windows_downloads_inventory.csv` (8431 rows)
  - `/mnt/c/Users/jonat/OneDrive` -> `reports/inventory/windows_onedrive_inventory.csv` (6 rows)
- Expanded NAS inventory roots:
  - `/mnt/z` -> `reports/inventory/nas_z_inventory.csv` (53 rows)
  - `/mnt/nas/media` -> `reports/inventory/nas_media_inventory.csv` (0 rows)
  - `/mnt/nas/pihole` -> `reports/inventory/nas_pihole_inventory.csv` (0 rows)
- Regenerated:
  - `reports/inventory/combined_inventory.csv` (9290 rows)
  - `reports/inventory/index_candidates_governance_alife.csv` (2 rows)

### Blockers

- `sysstat` install requires interactive sudo auth in this session:
  - `sudo apt update && sudo apt install -y sysstat`
- Until this is run locally, `iostat`/`pidstat` captures remain unavailable.

---

## Follow-up execution (sysstat + candidate miner)

### Completed

- Confirmed `sysstat` tools available:
  - `iostat -V`
  - `pidstat -V`
- Captured real WSL perf snapshots:
  - `reports/perf/wsl/iostat_20260330_164617.txt`
  - `reports/perf/wsl/pidstat_20260330_164617.txt`
  - `reports/perf/wsl/free_20260330_164617.txt`
  - `reports/perf/wsl/df_20260330_164617.txt`
- Added candidate mining script:
  - `scripts/mine_index_candidates.py`
- Added repo docs roots to inventory:
  - `reports/inventory/repo_docs_inventory.csv` (411 rows)
  - `reports/inventory/constella_repo_docs_inventory.csv` (75 rows)
- Rebuilt combined/candidate inventories:
  - `reports/inventory/combined_inventory.csv` (9776 rows)
  - `reports/inventory/index_candidates_governance_alife.csv` (85 rows)

### Current candidate quality

- Candidate distribution:
  - governance: 67
  - alife: 18
- Source host distribution:
  - wsl: 83
  - windows: 2
- Top-ranked candidates now correctly prioritize core governance/alife docs
  from `projects/constella-framework/docs/governance/` and local ALife findings.

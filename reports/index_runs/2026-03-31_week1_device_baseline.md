# Week 1 — device baseline and reliability gates

Captured: 2026-03-31  
Related: `docs/architecture/SYSTEM_TRANSPARENCY_IMPLEMENTATION_CHECKLIST.md` §8, `docs/SYSTEM_AUDIT_2026_03_30.md` §7.

## 1) Execution surface identity (evidence-backed)

| Surface | Role | Evidence (2026-03-31) |
|--------|------|------------------------|
| WSL2 workspace | Indexing scripts, SSH client, `curl` to Chroma | `hostname` → `DESKTOP-JJ1SUHB`; `uname -a` → `6.6.87.2-microsoft-standard-WSL2`, x86_64 |
| NAS (`ssh nas`) | Synology storage, SMB source for inventories | `hostname` → `ISaidGoodDay`; `uname -a` → `synology_rtd1296_ds220j` (DS220j, aarch64) |
| Gen8 | ChromaDB host for `faithh_knowledge_base` / ALife collections (repo convention) | `GET http://servicebox.taileb8c60.ts.net:8000/api/v2/heartbeat` → JSON heartbeat (OK at capture time). **Not verified:** Gen8 OS-level hostname / `uname` (host identity). |

## 1b) Canonical NAS mount (WSL) — single source of truth

| Field | Value |
|-------|--------|
| **Canonical WSL mount path** | `/mnt/z` |
| **Doc reference** | `reports/index_runs/2026-03-30_transparency_baseline_run.md` (NAS inventory and roots such as `/mnt/z/AI/backups`, `/mnt/z/Business/TomCatSound_LLC` recorded there) |

All Gate B checks that mean “NAS reachable from this workspace” use this path unless this report is explicitly revised.

## 2) Plex / Plexamp — single source of truth (path mapping)

**Rule:** This table is the only authoritative place for Plex/Plexamp host/path fields for Task 1. Replace each `UNVERIFIED:<TOKEN>` with a concrete value **or** leave the token and record the verification command output in the next baseline update.

| Service | Service host | Storage path | Dependency path |
|---------|--------------|--------------|-----------------|
| Plex Media Server | `UNVERIFIED:PMS_SERVICE_HOST` | `UNVERIFIED:PMS_LIBRARY_ROOT` | `UNVERIFIED:PMS_LOCALAPPDATA` |
| Plexamp (client) | `UNVERIFIED:PLEXAMP_CLIENT_HOST` | `UNVERIFIED:PLEXAMP_LOCAL_CACHE` | `UNVERIFIED:PLEXAMP_PMS_BASE_URL` |

**Suggested fill order (run on native Windows; from WSL use interop paths below).**

| Token | Verification command (native Windows) | Pass criterion |
|-------|----------------------------------------|----------------|
| `PMS_SERVICE_HOST` | `cmd.exe /d /c "echo COMPUTERNAME=%COMPUTERNAME%"` | Stdout contains `COMPUTERNAME=<name>`; replace token with `<name>` only if Plex Web/UI confirms PMS runs on that machine. |
| `PMS_LOCALAPPDATA` | `powershell.exe -NoProfile -Command "Join-Path $env:LOCALAPPDATA 'Plex Media Server'"` | Print non-empty path; **Pass** if `Test-Path` on that path is True; set dependency path to that resolved string. **Fail** if path missing → PMS not installed or custom location (document alternate). |
| `PMS_LIBRARY_ROOT` | `powershell.exe -NoProfile -Command "if (Test-Path (Join-Path $env:LOCALAPPDATA 'Plex Media Server\\Preferences.xml')) { 'Preferences.xml present — extract library folders from Plex Web → Settings → Libraries and paste UNC/drive paths here' } else { 'NO_PREFERENCES_XML' }"` | **Pass** when you have pasted at least one library root string (e.g. `Z:\Media\Movies`) into the table; until then token stays. |
| `PLEXAMP_CLIENT_HOST` | (per device) `hostname` on the device running Plexamp, or literal `phone` / `laptop` + model | Non-empty string chosen by operator. |
| `PLEXAMP_LOCAL_CACHE` | OS-specific app cache path for Plexamp on that client | Non-empty path after checking client settings/filesystem. |
| `PLEXAMP_PMS_BASE_URL` | From Plexamp connection / Plex Web server settings | Non-empty URL or host:port (e.g. `http://<pms-host>:32400`) that Plexamp uses. |

**WSL → Windows interop examples (executable from WSL bash; uses native Win32, not Linux paths for the target):**

```bash
cd /tmp && /mnt/c/Windows/System32/cmd.exe /d /c "echo COMPUTERNAME=%COMPUTERNAME%"
```

```bash
cd /tmp && /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -Command "Join-Path $env:LOCALAPPDATA 'Plex Media Server'"
```

## 3) Pass / fail reliability gates

### Gate A — Health (storage and critical service)

| Check | Pass | Fail |
|-------|------|------|
| WSL root filesystem | `df -h /` shows mount rw and **under 90%** used (or documented exception) | Root volume full or read-only errors |
| Windows volume (WSL `/mnt/c`) | **Under 95%** used or cleanup plan recorded | **95% or higher** used without mitigation (baseline was **88%**—watch trend) |
| NAS | DSM/storage manager: no volume crash/degraded RAID; SMART warnings addressed | Critical disk/volume errors unresolved |
| Chroma (Gen8) | `curl -sS --max-time 10 http://servicebox.taileb8c60.ts.net:8000/api/v2/heartbeat` returns JSON with heartbeat | Timeout, connection refused, or repeated 5xx |

### Gate B — Access (WSL + Windows + NAS path)

| Check | Pass | Fail |
|-------|------|------|
| **Native Windows (B-win)** | See subsection below | Subsection fail |
| NAS SSH | `ssh -o BatchMode=yes -o ConnectTimeout=10 nas "hostname"` returns expected hostname | Auth/host failure |
| NAS SMB from WSL | `test -d /mnt/z && ls /mnt/z >/dev/null` (canonical path §1b) | Mount missing or stale |
| Repo | `test -f /home/jonat/ai-stack/scripts/build_nas_ingest_allowlist.py` | Broken checkout or wrong machine |

#### Gate B-win — Native Windows shell (outside WSL)

**Intent:** Prove the Win32 environment is usable for Plex path verification and SMB drive letters, not only Linux paths under `/mnt/c`.

**Example (from WSL bash; launches native PowerShell).** Use **single quotes** around `-Command` so bash does not strip `$env:...`.

```bash
cd /tmp && /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -Command 'if ([string]::IsNullOrWhiteSpace($env:COMPUTERNAME)) { exit 2 }; Write-Output $env:COMPUTERNAME; exit 0'
```

| Outcome | Pass | Fail |
|---------|------|------|
| Exit code | `0` | Non-zero |
| Stdout | Single non-empty line matching the expected Windows computer name (e.g. `DESKTOP-JJ1SUHB`) | Empty, wrong host, or error text |

**Optional NAS letter probe (native path, not WSL `/mnt/z`):** replace `Z` with the drive letter you will record in `UNVERIFIED:PMS_LIBRARY_ROOT` once known.

```bash
cd /tmp && /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -Command 'if (Test-Path "Z:\") { Write-Output "Z_OK" } else { Write-Output "Z_MISSING"; exit 1 }'
```

| Outcome | Pass | Fail |
|---------|------|------|
| Exit code | `0` | `1` (or other non-zero) |
| Meaning | `Z:\` is visible to **Windows** | That drive letter not mapped in Windows session (remap or update library paths) |

### Gate C — Ingest readiness (allowlist-only pipeline)

| Check | Pass | Fail |
|-------|------|------|
| Classification input | `reports/inventory/nas_classification_queue.csv` exists and has **approved** non-personal rows with `ingestion_scope` in `{governance, alife, constella}` | Missing file or no approvable rows when a run is planned |
| Allowlist build | `python3 scripts/build_nas_ingest_allowlist.py` exits **0** and writes/updates `reports/inventory/nas_ingest_allowlist.csv` | Non-zero exit or `FileNotFoundError` on input |
| Staging (when copying) | `python3 scripts/stage_nas_allowlist_files.py ...` completes without SSH/SMB errors for the batch | Repeated transfer failures or writes outside `docs/data/*/nas_import` |

**Policy:** Do not run staging or bulk index jobs when any **Fail** in Gate A or B; Gate C **Fail** blocks NAS-sourced ingestion until inventory/approval is repaired.

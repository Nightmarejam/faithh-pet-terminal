# WSL migration tree removed from faithh

**Date (UTC)**: 2026-05-04  
**Host**: faithh

## What happened

The `~/wsl_migration` directory (~60G) was removed after verification. Canonical code lives in **`~/ai-stack`** (separate tree, not under `wsl_migration`).

## Archive on NAS

The **`knowledge_base`** subtree was copied to the NAS before deletion:

- `/mnt/nas/backups/wsl-migration-archive-2026-05-04/knowledge_base/`

Large **`ml_output`** (~51G) and other subtrees were **not** rsynced to NAS in this pass (size). You retain the **full WSL-era tree on NAS** and a **VHD** — use those for any `ml_output` / `projects` / docs recovery.

Faithh is intentionally lean so **Gen8** can own homelab operations without depending on a second copy under `~/wsl_migration` on the inference VM.

## Local verification log

Pre-removal inventory (sizes, file counts, `git` head):  
`/home/jonat/audit/wsl_migration-verification-2026-05-04.md`

# Multi-host audit and ecosystem sync

Use this page when you are **not sure which machine Cursor is on**. Inventory and ports **differ by host**.

## Identify the machine first

| Hostname (example) | Role | Typical stack |
|--------------------|------|----------------|
| **faithh** | Inference VM (vLLM, NAS models, `~/ai-stack` only — **`~/wsl_migration` removed 2026-05-04**) | Ports like **8000** (vLLM), **5557** (tool API), `/mnt/nas` |
| **servicebox** | Gen8 homelab / backend (per your naming); Docker services, Chroma, Gitea, etc. | Many listeners (22, 53, 80, 3000, 5557, 8000, …); Tailscale |

Run:

```bash
hostname
```

Then run the audit script with an explicit slug so reports are unambiguous:

```bash
AUDIT_SLUG="$(hostname)" AUDIT_ROLE="describe role" bash ~/ai-stack/scripts/audit_linux_host.sh
```

Default output: `~/audit/audit-<slug>-YYYY-MM-DD.md`.

## Where the scripts live

| Path | Purpose |
|------|---------|
| `ai-stack/scripts/audit_linux_host.sh` | **Versioned** copy; `git pull` on Gen8 or faithh to stay aligned |
| `~/audit_run.sh` on faithh | Optional convenience copy (keep in sync with repo script after edits) |

## Topology handoff

- On **faithh**, the full handoff table lives at `~/audit/ECOSYSTEM-TOPOLOGY.md` (if that directory exists).
- After auditing **servicebox (Gen8)**, copy or `scp` the generated `~/audit/audit-servicebox-*.md` next to faithh audits or commit under `docs/ops/` if you want history in git.
- **Handoffs are optional** — not required in git to operate; see **[LEAN_LLM_VLLM_FIRST.md](LEAN_LLM_VLLM_FIRST.md)** and **[RUNBOOK.md](../../RUNBOOK.md)**.

## `config.yaml` and `allowed_directories`

Every host should list **paths that exist**:

- **Minimum**: `$HOME/ai-stack` (or your clone path).
- **`/tmp/faithh`**: create with `mkdir -p /tmp/faithh` or remove from config if you do not use tool scratch there.

Do **not** add `/home/jonat/faithh` unless that directory exists on that host.

## Gen8 / PVE / Windows

- **Gen8**: after faithh cleanup, follow [GEN8_START.md](GEN8_START.md); parity audit = same script; optional SSH from faithh via `~/audit/run_remote_linux_audit.sh` when `REMOTE_HOST` is set.
- **PVE**: run `~/audit/collect_pve_inventory.sh` on the hypervisor only; see `~/audit/pve-inventory-*.md` on faithh.
- **Windows**: see `~/audit/WINDOWS-CURSOR-SYNC.md` on faithh (or duplicate these bullets into this repo).

## Git remotes

`ai-stack` may have **no `origin`** on one clone and **GitHub `origin`** on another. Run `git remote -v` on the machine you are editing and treat that clone as source of truth until remotes are unified.

If **faithh** and **Gen8** both have `main` but `git rev-list --left-right --count origin/main...main` is “ahead / behind” on both sides, see **[GIT_DIVERGENCE.md](GIT_DIVERGENCE.md)** before pulling.

**Compare heads** (paste from each host): `hostname; git -C ~/ai-stack log -1 --oneline; git -C ~/ai-stack remote -v`

# Gen8 (`servicebox`) — start operations after faithh cleanup

**faithh** no longer has `~/wsl_migration` (freed disk; canonical app tree is **`~/ai-stack` only**). Full WSL-era trees remain on **your NAS backup and VHD** — nothing unique was deleted from those archives.

Use this checklist when bringing **Gen8** online as the homelab / backend plane while **faithh** handles GPU inference.

## 1. Sync the repo (read before `git pull`)

**faithh-only commits** (ops, `wsl_migration` removal notes, audit script) do not appear on GitHub until someone **`git push`** from a clone that has them. **Gen8-only commits** (e.g. scaffolding on `servicebox`) are likewise invisible to faithh until fetched.

If `git rev-list --left-right --count origin/main...main` shows **both** sides non-zero, history is **divergent** — a plain `git pull` becomes a merge/rebase decision, not a one-liner. See **[GIT_DIVERGENCE.md](GIT_DIVERGENCE.md)** for strategies (push faithh branch, merge `origin/main`, side branch, or `git remote add faithh …`).

On **servicebox**, always:

```bash
hostname   # expect servicebox
cd ~/ai-stack
git remote -v
git fetch origin
git rev-list --left-right --count origin/main...main 2>/dev/null || true
```

Then choose merge, rebase, or branch push per **GIT_DIVERGENCE.md** — not blind `git pull`.

Resolve any merge conflicts (watch **`scripts/`** and **`docs/ops/`** duplicates), then run a quick audit:

```bash
mkdir -p ~/audit
AUDIT_SLUG="$(hostname)" AUDIT_ROLE="Gen8 homelab" bash ~/ai-stack/scripts/audit_linux_host.sh
```

## 2. Role split (avoid double-running the wrong thing)

| Concern | faithh | Gen8 (`servicebox`) |
|---------|--------|---------------------|
| vLLM / big models | Yes (`:8000`, NAS weights) | Usually no |
| Chroma, Gitea, Docker `~/services` | No | Yes |
| `ai-stack` backend talking to Chroma | Configure `.env` to reach **Gen8** Chroma URL | Chroma listens here (e.g. `:8000` in your stack — avoid port clashes with faithh when testing from one client) |

If anything still points at paths under **`~/wsl_migration`**, update it — that directory **does not exist on faithh** anymore.

## 3. Chroma and RAG URLs

Backend code (e.g. anchor checks) may still reference **Tailscale** or LAN IPs for Chroma (historically `100.79.85.32`). After cleanup:

- Run Chroma on **Gen8** and set the same host/IP in **`~/ai-stack/.env`** (or your deployment env) on whichever machine runs the Python backend that should hit Chroma.
- Raw WSL **`knowledge_base`** files: optional snapshot on NAS at  
  `/mnt/nas/backups/wsl-migration-archive-2026-05-04/knowledge_base/`  
  (faithh); ingest into Chroma from Gen8 if you need that corpus again.

## 4. Docker / compose on Gen8

Bring up your usual stack under **`~/services`** (or your layout): monitoring, Gitea, registry, Vaultwarden, Pi-hole, Chroma, etc. Use your existing compose/runbook — this doc does not duplicate every service name.

## 5. Smoke from Gen8 toward faithh

From Gen8, once routes and Tailscale are up:

- `curl -sS http://<faithh-lan-or-ts>:8000/v1/models` — vLLM catalog
- Confirm `ai-stack` clients use the **faithh** base URL for inference, not localhost on Gen8 unless you run a local proxy.

## 6. Topology reference (faithh)

On the inference VM, handoff tables live under **`~/audit/ECOSYSTEM-TOPOLOGY.md`** (not in git). Ops docs in git start here: [MULTI_HOST_AUDIT.md](MULTI_HOST_AUDIT.md).

## 7. Backups you still have

- **NAS**: full WSL-era backup (your copy of the tree).
- **VHD**: offline disk image.

Use those for any **`ml_output`** or **`projects`** recovery — they were not bulk-copied to NAS during faithh cleanup.

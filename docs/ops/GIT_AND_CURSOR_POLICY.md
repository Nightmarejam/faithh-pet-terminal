# Git and Cursor multi-host policy

Use this policy when you are editing `ai-stack` from multiple hosts (faithh, Gen8, or other SSH targets).

## Core safety rules

- One feature branch per change. Do not commit directly to `main`.
- One active editor session per branch. Avoid editing the same branch from two hosts at once.
- Pull/rebase before you start and before you push.
- Keep runtime artifacts out of git (`data/*`, logs, temp files, secrets).
- Never edit `.env` templates with real secrets.

## Ownership model

- `faithh` owns inference/runtime implementation work (vLLM, backend integration, GPU behavior).
- `gen8` owns service-plane and storage-plane work (Chroma, monitoring, infra scripts).
- `windows` is control plane only (Cursor UI, docs drafts, non-runtime assets).

If a change crosses ownership boundaries, split work into separate commits with clear messages.

## Branch naming

- `feat/<area>-<purpose>`
- `fix/<area>-<issue>`
- `ops/<host>-<change>`
- `docs/<topic>`

Examples:

- `feat/crypto-coinbase-snapshot`
- `ops/gen8-mcp-bootstrap`
- `docs/multi-host-ssh-policy`

## Cursor usage pattern

- Keep one Cursor window per repo root.
- Use SSH aliases from `~/.ssh/config` (`faithh`, `gen8`, `pve`, `nas`) instead of raw IPs.
- Before switching hosts, run:

```bash
hostname
git branch --show-current
git status --short
```

## Merge hygiene checklist

- Tests/lint for touched area pass on the host that owns runtime.
- No secret files staged.
- No unrelated generated files staged.
- Commit message explains intent, not only file names.
- `git status` is clean after commit.

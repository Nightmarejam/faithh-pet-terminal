# GitHub ↔ ai-stack Canvas sync (Phase 2 notes)

**Date:** 2026-04-07

## faithh-pet-terminal vs canonical HTML

| File | Local `ai-stack` (bytes) | `main` on GitHub (bytes) | Note |
|------|--------------------------|---------------------------|------|
| `faithh_pet_v4.html` | 305,226 | 301,494 | Local copy is **larger / newer** by ~3.7 KiB (one-time snapshot; re-check before push). |
| `faithh_cockpit.html` | 35,923 | (fetch raw if needed) | Compare with `https://raw.githubusercontent.com/Nightmarejam/faithh-pet-terminal/main/faithh_cockpit.html` |

Repository: [Nightmarejam/faithh-pet-terminal](https://github.com/Nightmarejam/faithh-pet-terminal)

### If local is the source of truth — push alignment

Run from a machine with **push access** to `Nightmarejam/faithh-pet-terminal` (replace paths if the GitHub repo is cloned elsewhere):

```bash
CANON="/home/jonat/ai-stack"
PET_REPO="/path/to/faithh-pet-terminal"   # clone: git clone git@github.com:Nightmarejam/faithh-pet-terminal.git

cp "$CANON/faithh_pet_v4.html" "$PET_REPO/"
cp "$CANON/faithh_cockpit.html" "$PET_REPO/"
cd "$PET_REPO"
git status
git add faithh_pet_v4.html faithh_cockpit.html
git commit -m "Sync Canvas HTML from ai-stack canonical (2026-04-07)"
git push origin main
```

**Never** paste API keys into the GitHub copy of `.env.example`; keep secrets only in local `.env`.

---

## runbook-to-rule-them-all (nested clone)

If `runbook-to-rule-them-all/` exists **inside** `ai-stack` with its **own `.git`**, the parent repo either:

- ignores it, or  
- tracks files inconsistently.

**Recommended:** remove the nested working tree, then attach as a **submodule**:

```bash
cd /home/jonat/ai-stack
# Backup if needed, then remove nested repo (destructive — confirm no unique commits only in nested copy)
rm -rf runbook-to-rule-them-all

git submodule add -b main git@github.com:Nightmarejam/runbook-to-rule-them-all.git docs/runbooks/runbook-to-rule-them-all
git submodule update --init --recursive
```

Alternative (no submodule): **`git subtree add`** to merge history under a prefix (see `git help subtree`).

---

## constella-framework submodule

Expected entry in **parent** `.gitmodules`:

```ini
[submodule "projects/constella-framework"]
	path = projects/constella-framework
	url = git@github.com:Nightmarejam/constella-framework.git
	branch = main
```

Initialize / update:

```bash
cd /home/jonat/ai-stack
git submodule update --init --recursive projects/constella-framework
git submodule status projects/constella-framework
```

A healthy checkout shows a commit SHA (not `-$` prefix in `git submodule status`).

---

## Related

- Inventory / classification: `docs/RELEVANCY_REPORT.md`
- Agent rules: `AGENTS.md` (`services/`, `modules/`, `vendor/`)

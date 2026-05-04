# When `main` on faithh and Gen8 disagree (no fast-forward)

You can have **two valid lines of history** that never shared a recent merge-base with `origin/main`:

- **faithh** may have commits (e.g. `wsl_migration` removal, ops docs) that were **never pushed** because `git remote` was empty or push was skipped.
- **Gen8 (`servicebox`)** may have its **own** commits (e.g. `b8c7271`–style “scaffold audit here”) while **`origin/main` on GitHub** moved hundreds of commits ahead.

Symptoms:

```bash
cd ~/ai-stack
git remote -v
git fetch origin
git rev-list --left-right --count origin/main...main
```

Non-zero **both** sides (example pattern: ahead 28, behind 314) mean a plain `git pull` is **not** a trivial fast-forward — Git will merge or ask you to reconcile divergent histories.

## Do not

- Blind `git pull` on Gen8 without reading the merge message and conflict list.
- `git push --force` to `origin/main` unless you intend to rewrite shared history and everyone agrees.

## Safe strategies (pick one)

### A — Publish faithh first (if faithh has the “source of truth” ops you want on GitHub)

On **faithh**:

```bash
cd ~/ai-stack
git remote add origin <your-github-or-gitea-url>   # if missing
git fetch origin
# If origin/main is empty or you want a new branch for faithh line:
git push -u origin main
# Or push to a side branch first (safest):
git push -u origin main:faithh-ops-2026-05-04
```

On **Gen8**, fetch that branch and merge it into your work (or merge `main` after you’ve reconciled on GitHub via PR).

### B — Merge `origin/main` into Gen8 deliberately

On **Gen8**:

```bash
cd ~/ai-stack
git fetch origin
git merge origin/main
# resolve conflicts; pay special attention to scripts/audit_linux_host.sh and docs/ops/*
git commit
```

You keep Gen8-local commits and integrate upstream in one merge commit (or use `git rebase origin/main` if you prefer linear history and can handle rebase conflicts).

### C — Isolate Gen8 experiments

```bash
git checkout -b gen8/scaffold-2026-05-04
git push -u origin gen8/scaffold-2026-05-04
```

Then open a PR to `main`, or merge faithh’s branch into this branch in the UI.

### D — Add faithh as a second remote (no Git server on faithh)

From **Gen8** (SSH to faithh must work):

```bash
git remote add faithh jonat@faithh:~/ai-stack
git fetch faithh
git log --oneline --graph --decorate -15 faithh/main main origin/main
git merge faithh/main   # or: git cherry-pick <sha>...
```

Adjust URL to your SSH host alias and path.

## Compare heads across machines

Run on **each** host and paste into a ticket or the topology doc:

```bash
hostname
git -C ~/ai-stack rev-parse --short HEAD
git -C ~/ai-stack log -1 --oneline
git -C ~/ai-stack remote -v
```

Until these converge, treat **ops doc paths** as duplicated: read `docs/ops/GEN8_START.md` from the **clone you are on**, and know that GitHub `origin/main` may lag both.

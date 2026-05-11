# Parent repo vs `faithh-pet-terminal` (terminal copy)

## Mental model

| Role | Repository | Typical use |
|------|--------------|-------------|
| **Parent / canonical** | `https://github.com/Nightmarejam/jonat-FAITHH` | Full FAITHH tree, historical monolith files, “source of truth” for big moves |
| **Terminal / lean copy** | `https://github.com/Nightmarejam/faithh-pet-terminal` | Day-to-day ops, inference VM workflow, docs + scripts tuned for homelab; **`origin` usually points here** |

The terminal repo was meant to reduce confusion by narrowing scope. If things still drifted, treat **`jonat-FAITHH` as upstream for “what exists in the big repo”** and **`faithh-pet-terminal` as where you push operational commits**—unless you decide to make one repo the single canonical remote.

## Wire Git so you can compare (on your machine, with GitHub auth)

From your clone (e.g. `~/ai-stack`):

```bash
git remote add parent https://github.com/Nightmarejam/jonat-FAITHH.git
# or: git remote add upstream …  if you prefer that name

git fetch parent
```

See whether a file exists only on the parent:

```bash
git ls-tree parent/main -- faithh_professional_backend_fixed.py
git diff main parent/main --stat
```

If **`faithh_professional_backend_fixed.py`** (or similar) exists on **`parent/main`** but not on **`main`**, you can bring it in with a targeted checkout:

```bash
git checkout parent/main -- faithh_professional_backend_fixed.py
# review, commit, push to origin when ready
```

Or merge/rebase a branch from parent—choose based on how unrelated the histories are.

## Why automation here cannot see the parent

Anonymous requests to GitHub for private or restricted repos return **404**. Only **your** authenticated `git fetch` / browser session can confirm branches and file paths. Use the commands above locally.

## Related

- [GIT_DIVERGENCE.md](GIT_DIVERGENCE.md) — when `faithh` and Gen8 disagree with `origin/main`
- [LEAN_LLM_VLLM_FIRST.md](LEAN_LLM_VLLM_FIRST.md) — lean runtime (`FAITHH_MAIN`, vLLM, `.env`)

# UI Canonical Decision

## 1) HTML served at http://localhost:5557
- The backend route `/` in `faithh_professional_backend_fixed.py` serves `faithh_pet.html` from the repo root.
- Note: `faithh_pet_v3.html` in the repo root is a symlink to `faithh_pet_v4.html`, so any v3 path references now resolve to v4.

## 2) Best candidate for canonical UI
**Recommendation:** `faithh_pet.html`

**Why this matches the criteria:**
- **Backend alignment:** The live backend (`faithh_professional_backend_fixed.py`, v3.4-filesystem) serves this file at `/` and supports the endpoints the UI actually calls: `/api/chat`, `/api/status`, `/api/pulse/chips`.
- **Stable UX / minimal hacks:** This is the current served UI and appears to be the least divergent from the backend wiring.
- **Least duplication:** Other variants are either backups, archived, or enhanced forks that are not served by the backend.
- **Gaps to acknowledge:** The UI does not currently call `/health` or `/api/upload` (even though the backend provides them). If those need to be exposed, add lightweight UI affordances rather than switching files.

## 3) Other HTML variants and archive/keep rationale
- `faithh_pet_v4_backup.html` — backup snapshot of the canonical UI; keep only as a historical backup, archive to reduce confusion.
- `faithh_pet_v4_enhanced_patched.html` — patched fork of the enhanced UI; uses `/api/search` (not in the current backend) and is not wired as the served UI.
- `frontend/html/faithh_pet_v4_enhanced.html` — enhanced fork with extra UI features; not served by the backend and mismatched to `/api/rag_search` vs `/api/search`.
- `active/frontend/faithh_pet_v4.html` — duplicate copy in a staging folder; should be archived to avoid split-brain edits.
- `archive/legacy/faithh_ui_v4.html` — older experimental v4; retain in archive only.
- `archive/ui_reference/faithh_pet_v3.html` — aesthetic reference (v3); keep for design reference but not as runtime UI.
- `frontend/html/rag-chat.html` — Ollama direct UI, bypasses backend; keep only as standalone RAG reference.
- `AI_Chat_Exports/Chat_GPT_Exports/chat.html` — large export artifact; not part of UI.
- `projects/constella-framework/docs/index.html` — unrelated project doc site; keep out of UI decisions.

## 4) If a patched variant is chosen instead
If you decide the enhanced/patched UI should become canonical, use a clean filename like `faithh_pet.html` and apply this merge plan:
- Start from `faithh_pet_v4_enhanced_patched.html` (or `frontend/html/faithh_pet_v4_enhanced.html`).
- Replace `/api/search` with `/api/rag_search` and verify `/api/chat`, `/api/status`, `/api/pulse/chips` are preserved.
- Port over any missing pieces from `faithh_pet_v4.html` (status panel behavior, pulse chips wiring, error handling).
- Add optional UI hooks for `/api/upload` and `/health` so the canonical UI reflects all current backend capabilities.
- Freeze the result as `faithh_pet.html`, keep `faithh_pet_v4.html` as a legacy alias until all references migrate.


**Canonical naming change:** `faithh_pet.html` is now the canonical UI file served at `/`. `faithh_pet_v4.html` remains as a snapshot/legacy file (do not edit unless intentionally for rollback).

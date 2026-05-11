# UI Canonical Merge Plan

1. Inventory all UI features in `faithh_pet_v4.html`, `faithh_pet_v4_enhanced_patched.html`, and `frontend/html/faithh_pet_v4_enhanced.html`.
2. Map each UI action to backend endpoints (`/api/chat`, `/api/status`, `/api/rag_search`, `/api/pulse/chips`, `/api/upload`, `/health`).
3. Choose a base file (recommended: `faithh_pet_v4.html`), and list missing features from the other variants.
4. Port features one at a time, validating that endpoint names match the backend (`/api/rag_search` not `/api/search`).
5. Add minimal UI hooks for `/api/upload` and `/health` if they are not already present.
6. Reconcile localStorage / state handling to avoid duplicate logic across variants.
7. Normalize CSS variables and layout so merged sections match the base theme.
8. Remove dead or unused UI blocks that reference non-existent endpoints.
9. Run the smoke checklist in `docs/UI_CANONICAL_CHECKLIST.md` after each major merge step.
10. Freeze the canonical filename (e.g., `faithh_pet_v4.html` or `faithh_pet.html`) and keep other variants read-only for reference.

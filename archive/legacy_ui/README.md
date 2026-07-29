# legacy_ui/

Holds **retired** root-level or near-root HTML shells when the Canvas UI consolidates on `faithh_pet_v4.html` and `faithh_cockpit.html`.

## Contents

### `faithh_pet.html` — retired 2026-07-28

The pre-v4 Canvas UI, 138 KB / 3,720 lines. Superseded by `faithh_pet_v4.html`.

Retired because **no backend route served it.** `faithh_professional_backend_fixed.py`
serves only `faithh_pet_v4.html` (at `/`, line 2248) and `faithh_cockpit.html`
(at `/cockpit`, line 2252). It was unreachable in the running system.

It reads as live to a grep — all 12 of the `/api/` endpoints it calls still
resolve against the current backend — which is why it survived earlier passes.
See [FRONTEND_AUDIT.md](../../docs/architecture/FRONTEND_AUDIT.md).

Note: `archive/frontend-duplicates-2026-01-25/faithh_pet.html` is a **different,
older** snapshot (89 KB), not a duplicate of this one. Both are kept.

## History

As of 2026-04-07 there were **no extra `*.html` files at repository root** to move; older UIs already live under `archive/` and `llama.cpp/`. `faithh_pet.html` reappeared at root between then and 2026-07-28 and is now retired here.

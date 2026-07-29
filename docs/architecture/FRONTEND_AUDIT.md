# Frontend audit

**2026-07-28** · measured against `faithh_professional_backend_fixed.py` (107 routes).
Companion to [COMPONENT_INDEX.md](COMPONENT_INDEX.md) and
[FAITHH_REDESIGN.md](FAITHH_REDESIGN.md).

## Headline

**The frontend is not broken. Every endpoint it calls exists — 54 of 54 across
all three files.** The imbalance runs the other way: **70 of the backend's 107
routes have no UI reference at all.** The UI is behind the backend, not wrong
about it.

## The three files

| file | size | lines | served at | verdict |
|---|---|---|---|---|
| `faithh_pet_v4.html` | 344 KB | 8,725 | `/` | **current** — the Canvas UI |
| `faithh_cockpit.html` | 46 KB | 1,303 | `/cockpit` | **current** — diagnostics |
| `faithh_pet.html` | 135 KB | 3,720 | *nothing* | **superseded** by v4 |

The backend serves only the first two (`send_from_directory` at lines 2248 and
2252). `faithh_pet.html` is the pre-v4 version, reachable by no route. Its 12
endpoints all still resolve, so it looks alive to a grep — archive it.

## API coverage

| | distinct `/api/` paths | resolve | broken |
|---|---|---|---|
| `faithh_pet_v4.html` | 30 | **30** | 0 |
| `faithh_cockpit.html` | 12 | **12** | 0 |
| `faithh_pet.html` | 12 | 12 | 0 |

### Measurement note

An earlier pass of this audit reported a broken call to `/api/journal/view/`.
That was a measurement bug, not a defect: the extraction grep matched only
double-quoted `@app.route("...")`, and **106 of the 109 route declarations use
single quotes**. `/api/journal/view/<date>` is defined at
`faithh_professional_backend_fixed.py:6131`.

Anything auditing this backend by regex must accept both quote styles. The
corrected script also has to handle v4's call style — template literals and
string concatenation — rather than looking for `fetch('/literal')`.

## Unused surface area — the actual finding

70 of 107 routes, roughly two thirds of the backend, have no caller in any UI:

| routes | area | note |
|---|---|---|
| 10 | `/api/auth/*` | login, logout, change-password, sessions — **a complete auth system with no screen** |
| 9 | `/api/pulse/*` | proposals, approve, reflection branches |
| 4 | `/api/genomic/*` | impedance sensor, biasing analysis |
| 3 | `/api/metrics/*` | sessions, flush-session |
| 3 | `/api/ux/*` | personalisation, interaction tracking |
| 2 each | analytics, avatar, constitution, context, filesystem, ml, monitoring, program-advance, search | |
| 1 each | attest, cache, compass, focus, ml-learning | |

Two matter beyond tidiness:

- **`/api/pulse/proposals` + `/api/pulse/approve`.** [FAITHH_REDESIGN.md](FAITHH_REDESIGN.md)
  asks who approves capability growth when `pulse_pattern_tracker` proposes a new
  chip. The backend already answers it — there is just no screen. That is a UI
  gap, not a design gap, and it is the highest-value new surface here.
- **`/api/auth/*`.** Ten routes of authentication nothing uses. For single-user
  local operation this may be 10 routes to delete rather than 10 screens to
  build. Decide; do not leave it ambiguous.

## Aesthetics — what to preserve

The terminal/BBS look is coherent and deliberate: **`Share Tech Mono`** with a
`Courier New` fallback, monospace throughout, no build step, no framework.

Two facts to know before touching it:

1. ~~**Zero CSS custom properties**~~ — **done 2026-07-28**, see below.
2. **Six external CDN scripts** — `marked`, `highlight.js`, and four language
   packs (python, javascript, bash, json). These fail offline and on a
   locked-down network, which is at odds with FAITHH being local-first. Vendoring
   them is about 200 KB.

## Palette extraction — done 2026-07-28

A 25-entry `:root` palette now sits at the top of the `<style>` block. **341
substitutions**: 275 hex literals to `var()`, plus 66 `rgba(0,255,255,α)` to
`rgba(var(--accent-rgb), α)`, collapsing the cyan alpha family onto one hue.

Only the recurring, semantically meaningful colors were named — accent, ok, warn,
err, text ramp, border. One-off values stay inline on purpose; a palette that
names all 122 distinct values is not a palette, it is indirection.

### Verification

Two independent checks, because "looks the same" is not good enough:

1. **Textual round-trip.** The extraction script expands every `var()` back to its
   literal and requires the result to equal the original byte-for-byte (modulo
   hex case and `rgba` spacing). It refuses to write on mismatch.
2. **Computed-style diff.** Original and edited served from the same static origin
   and compared element-by-element via `getComputedStyle` over 16 colour and font
   properties — 713 elements each.

Note that a whole-page hash is **not** a valid check here: the page is
nondeterministic across loads, and three loads produced three hashes. Only the
per-element diff distinguishes a real change from load-order noise.

### It fixed two dangling references

The diff came back with exactly 2 differing elements, both `.hm-swatch`. Those
turned out to be a **pre-existing bug, not a regression**.

The original file contained exactly **two `var()` references — `var(--accent)` and
`var(--border)` — and zero definitions.** They are inline `style=` attributes in
markup, outside the `<style>` block, so this pass never touched them. Being
undefined, both resolved to invalid and painted transparent.

They sit in the heatmap legend, which is a five-step ramp:

```html
<div class="hm-swatch" style="background:var(--border)"></div>      <!-- was invisible -->
<div class="hm-swatch" style="background:rgba(0,255,255,0.2)"></div>
<div class="hm-swatch" style="background:rgba(0,255,255,0.45)"></div>
<div class="hm-swatch" style="background:rgba(0,255,255,0.7)"></div>
<div class="hm-swatch" style="background:var(--accent)"></div>      <!-- was invisible -->
```

Both **endpoints** of the ramp were missing — the legend has been rendering
wrong. Because the palette uses those same two names, defining `:root` repaired
it: the swatches now compute to `rgb(59, 90, 157)` and `rgb(0, 255, 255)`.

Whoever wrote that markup assumed a `:root` block that never existed. It does now.

## Recommended sequence

Ordered so the aesthetic is never at risk:

1. ~~**Archive `faithh_pet.html`**~~ — **done 2026-07-28**, moved to
   `archive/legacy_ui/`.
2. ~~**Extract CSS custom properties**~~ — **done 2026-07-28**, see above.
3. **Vendor the six CDN scripts** so the UI works offline.
4. **Decide on auth** — build the screen or delete the routes.
5. **Surface PULSE approvals.** Closes the capability-growth loop the redesign
   identifies as unowned.
6. Only then consider a broader overhaul.

## On the overhaul question

The UI is not the weak layer. It calls every endpoint it references correctly, it
is self-contained, and the aesthetic is consistent. An overhaul would be
premature. The work is exposing capability that already exists — and deciding
what to delete.

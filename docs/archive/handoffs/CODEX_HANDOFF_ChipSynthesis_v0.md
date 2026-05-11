# FAITHH Chip Synthesis + Program Advances — Research Review, Hole-Poking, and Codex Implementation Handoff (v0)

**Context:** FAITHH currently has pre-defined “chips” that auto-select based on intent (e.g., RAG Search, Decisions, Scaffolding). Future goals include *personalized chips* that emerge from user behavior and *Program Advances (PAs)* that unlock when chip combos recur. fileciteturn2file0L1-L11

This doc does two things:
1) pressure-test the logic (what can break / get creepy / get expensive),
2) hand Codex a concrete, minimal implementation plan that keeps you *offline-first* and *privacy-first*.

---

## 1) Hole-poking: where the logic can fail (and what to do)

### A. “Chips emerge from behavior” can turn into surveillance vibes
**Failure mode:** the system learns “you seem anxious on Mondays” or “you argue with X person” and surfaces it. Even if true, it can feel invasive.
**Mitigation:** enforce a **Hard Redline**: no inferred emotional, health, relationship, or financial state unless the user explicitly opts in *per chip*.

**Implementation rule:** chip candidates must be derived from:
- topical clusters (project/topic), or
- action preferences (format, depth, cadence), or
- repeated workflows (e.g., “morning briefing”).

No “you feel ___” chips by default.

### B. Pattern detection will hallucinate “patterns” if you don’t define success metrics
**Failure mode:** random streaks become chips; the library becomes junky.
**Mitigation:** chips should require both:
- **frequency** (seen N times), and
- **utility** (high confidence “this helped”), measured by *proxy signals* you control (reruns, user pinning, user approval, time-to-resolution, manual thumbs up, etc.)

**Minimal signal set (offline):**
- `user_pinned_chip` (explicit)
- `user_accepted_proposal` / `user_rejected_proposal`
- `rerun_same_intent_within_10m` (suggests dissatisfaction)
- optional: `user_rating` (1–5)

### C. Topic clustering over 27K+ docs can be too heavy if you do it wrong
**Failure mode:** you try to recluster everything often; it’s slow; it stalls FAITHH.
**Mitigation:** start with **conversation-event clustering**, not full-corpus clustering:
- cluster *user queries* (and/or the “evidence packet” top doc IDs) incrementally.
- only run deeper clustering as a nightly batch.

If you later want streaming/online clustering, online k-means and stream clustering literature exists—treat it as a performance upgrade, not a v0 requirement. citeturn1search2turn1search6

### D. Program Advances can explode combinatorially
**Failure mode:** with M chips you have 2^M possible combos; you’ll unlock noise.
**Mitigation:** restrict PA candidates to:
- **small arity** (2–3 chips),
- **ordered workflows** (A→B→C) OR “same turn co-activation” only,
- **non-overlapping utility** (e.g., Decisions + Scaffolding + RAG, not RAG+RAG-adjacent).

### E. “Automatic unlocking” can feel magical *or* confusing
**Failure mode:** user doesn’t know why something happened, or can’t control it.
**Mitigation:** always pair PA unlock with:
- a one-paragraph “why you unlocked it” explanation,
- a one-click “disable / revert” control,
- a “show me evidence” view (recent triggering events).

### F. Provider fallback during streaming is trickier than it sounds
If you use LangChain fallbacks, note that streaming fallbacks generally only trigger if the stream fails at creation; errors mid-stream won’t automatically fallback. citeturn0search1turn0search9  
**Mitigation:** implement fallback at the **request boundary** first (non-streaming), then later consider streaming strategies.

---

## 2) “Second research pass” suggestions (targeted, not endless)

Do *not* re-research everything. If you re-research, it should answer a known risk.

**Recommended targeted research (high ROI):**
1) **Groq limits + model selection** for your routing policy (TPM/RPM, pricing, context windows). citeturn1search0turn1search1
2) **Incremental clustering** approach choice: online k-means vs density methods (HDBSCAN/DBSCAN) for embeddings, and when each wins. citeturn1search2turn1search6turn1search11
3) **Privacy UX**: consent flows (“propose chips”), export/delete patterns, “do not learn from this chat” toggle.

---

## 3) Technical design recommendation (v0 that won’t bite you)

### The v0 design principle
**Don’t “learn a chip.” Learn a *proposal* first.**
Everything new is a *proposal* until the user accepts it.

### Data Flow
1) FAITHH responds to a user message and logs an **event**
2) PULSE runs a lightweight **pattern update**
3) If thresholds are met, PULSE creates a **chip proposal**
4) FAITHH surfaces it in UI: user **accepts / rejects / edits**
5) Accepted proposals become **active personalized chips**
6) Frequent co-activations unlock **Program Advances** (composite chips)

### Storage (offline-first)
- Use local **SQLite** (preferred) or JSONL.
- Encrypt-at-rest is optional v0 (Bitwarden + disk encryption may be “good enough” initially), but plan for it.
- Provide **export** (JSON) + **delete** capabilities on day 1.

### Privacy guardrails
- A per-message flag: `do_not_learn=true`
- A per-chip sensitivity field: `sensitivity = {normal|personal|sensitive}` where **sensitive is blocked** unless explicit opt-in.
- No inference about protected categories by default.

---

## 4) Groq integration: verified facts you can build on

Groq provides an OpenAI-compatible base URL: `https://api.groq.com/openai/v1` and the chat completions endpoint at `/chat/completions`. citeturn0search0turn0search11

Groq also publishes supported models, pricing, and rate limits (e.g., llama-3.1-8b-instant, llama-3.3-70b-versatile) and TPM/RPM constraints. citeturn1search1turn1search0

---

# 5) Codex implementation handoff (Phase plan + acceptance criteria)

## Phase 0 — Safety rails + logging (1 session)
**Goal:** capture the data you need without learning anything creepy.

### Backend tasks
1) Add an **event logger** (SQLite table or JSONL):
   - `event_id` (uuid)
   - `ts`
   - `conversation_id`
   - `user_message_hash` (optional)
   - `intent_label` (existing chip router)
   - `chips_fired` (array)
   - `provider_used`
   - `do_not_learn` (bool)
   - `latency_ms`
2) Add a single endpoint:
   - `GET /api/pulse/status` → counts (events, patterns, proposals, PAs)

### Acceptance criteria
- Every `/api/chat` call records a pulse event.
- A toggle `do_not_learn` prevents event ingestion.
- `/api/pulse/status` returns sane counts.

---

## Phase 1 — Chip proposals (2–3 sessions)
**Goal:** proposals appear in UI; user can accept/reject.

### Proposal generation (simple, deterministic first)
Create proposals from:
- repeated intents + repeated keywords (TF-IDF or simple keyword extraction),
- repeated doc clusters from RAG “top doc IDs” overlap,
- repeated “workflow” patterns (e.g., Scaffolding+ProjectState morning window).

**Thresholds (suggested):**
- appears ≥ 5 times in last 30 days
- AND rejection rate < 50%
- AND not flagged as sensitive

### Backend endpoints
- `GET /api/chips/proposals` (list)
- `POST /api/chips/proposals/{id}/accept`
- `POST /api/chips/proposals/{id}/reject`
- `GET /api/chips` (active chips list)
- `DELETE /api/chips/{id}` (remove)

### UI tasks (React)
- Add “Chips” screen:
  - Proposals (accept/reject)
  - Active chips (toggle on/off, delete)
  - Export button

### Acceptance criteria
- You can see 0+ proposals.
- Accepting creates an active chip that can be toggled and shows in routing metadata.
- Export returns JSON with proposals + chips + PAs.

---

## Phase 2 — Program Advances (2 sessions)
**Goal:** detect repeated combos and mint a composite chip.

### Detection logic (simple)
- For each event, compute:
  - `combo = sorted(chips_fired)` and/or `ordered_combo = chips_fired`
- Count combos in sliding window (e.g., last 30 days)
- If a combo hits ≥ 5 triggers AND has high success proxy, create a PA proposal.

### PA behavior
- A PA is just a **composite chip** with an orchestrated prompt template:
  - preface: “You unlocked X because…”
  - steps: run chip A outputs → feed into B → feed into C
- Keep it deterministic and testable.

### Acceptance criteria
- A PA can be created (manually seeded for testing).
- Once accepted, routing can pick it when conditions match.
- UI shows it as “Program Advance” with a badge.

---

## Phase 3 — Upgrade clustering (optional performance/quality)
When Phase 1–2 work, then:
- replace keyword heuristics with embedding clustering
- consider online/minibatch k-means for incremental updates citeturn1search2turn1search6
- optionally add HDBSCAN for variable density/noise once scale demands it citeturn1search11

---

## Phase 4 — Provider routing + fallback policy (optional)
**Groq provider**:
- Use OpenAI-compatible client pointed at Groq base URL. citeturn0search0turn0search11
- Enforce rate-limit backoff using headers and 429 handling (Groq docs). citeturn1search0turn1search4

**Routing policy v0:**
- “Fast / low cost”: llama-3.1-8b-instant
- “Deep / complex”: llama-3.3-70b-versatile
…subject to your limits/pricing. citeturn1search1

---

# Appendix — What Codex should NOT do
- Don’t auto-create chips without user acceptance.
- Don’t infer emotional/medical/relationship patterns.
- Don’t run full-corpus reclustering frequently.
- Don’t ship a UI that can’t delete/export (creepy factor skyrockets).

---

**End of handoff.**

# RESEARCH HANDOFF — Chip Synthesis System (v2 Combined)
**Date:** 2026-01-03  
**Goal:** Validate and refine the “Chip Synthesis + Program Advances” design for FAITHH with emphasis on privacy, offline learning, and MMBN-style UX.

---

## 1) What to verify (questions that can break the design)
### A. “Chips feel magical, not creepy”
- How to phrase discoveries so they sound like *skills*, not surveillance?
- What patterns should never be reflected back without opt-in (health, finances, relationships, emotional inference)?

### B. Clustering is actually useful
- How to evaluate cluster quality in embedding space (coherence proxy, human review)?
- How to handle “K selection” and concept drift?

### C. Program Advances don’t become spam
- What unlock thresholds minimize noise?
- How to avoid accidental PA unlocks that are meaningless?

### D. Privacy controls are strong and understandable
- What consent UX is considered non-deceptive (equal accept/reject, easy opt-out)?
- What “right to be forgotten” expectations exist, and how to match them with local-only storage?

### E. Provider integration robustness
- What OpenAI-compat caveats exist for Groq (unsupported fields, temp=0 handling, n=1)?
- How should model deprecation monitoring work (alias mapping, changelog polling)?

---

## 2) Sources to use (primary-first)
1. Groq Docs: OpenAI Compatibility, Models, Rate Limits, Deprecations, Changelog.
2. scikit-learn docs: MiniBatchKMeans and clustering best practices.
3. Dark-pattern / consent references: EDPB deceptive design guidelines + major empirical paper on consent pop-ups.
4. AI data controls examples: OpenAI “Data Controls” and “Chat History” controls.

---

## 3) Expected research outputs
1. **Threat model** for personalization (what could go wrong).
2. **Pattern taxonomy**:
   - allowed patterns (tool usage, topics, time-of-day with coarse buckets)
   - restricted patterns (sensitive inference)
3. **Clustering evaluation plan**:
   - coherence metric proxy + human-in-the-loop review flow
   - K selection approach recommendations
4. **UX copy guidelines**:
   - “Discoveries” language templates
   - explicit opt-in for sensitive learning
5. **Provider reliability plan**:
   - rate limit strategy + retries
   - deprecation monitoring plan

---

## 4) Decision gates (what counts as “passes”)
- A minimal v1 can ship with:
  - local-only learning artifacts
  - pause/do-not-learn/export/delete
  - MiniBatchKMeans with normalization
  - PA unlocks behind meaningful thresholds
- v2 can add:
  - HDBSCAN/UMAP experimentation
  - richer PA evolutions
  - visual “folder” management


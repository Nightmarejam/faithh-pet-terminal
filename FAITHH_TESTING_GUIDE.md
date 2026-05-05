# FAITHH v4 Testing Guide
**Created**: 2025-12-02  
**Purpose**: Systematically discover where FAITHH excels and fails  
**Duration**: Use this throughout the week, ~10 min/day

---

## 🎯 Testing Philosophy

Don't test to validate—test to break. The goal is to find the edges where FAITHH stops being useful. Those edges tell us what to build next.

**After each test, ask yourself:**
1. Did this save me time vs. asking Claude/searching manually?
2. Would I naturally reach for FAITHH for this type of question?
3. What would have made the answer better?

---

## 📋 Daily Testing Ritual (5-10 minutes)

### Morning Check-In
Before starting work, ask FAITHH one of these:

**Orientation Questions** (tests scaffolding):
- "Where was I with [project]?"
- "What's the current phase of FAITHH?"
- "What was I working on last session?"

**Expected**: Clear, accurate summary of project state
**Log if**: Wrong info, stale info, missing context

### During Work
When a real question comes up, try FAITHH first:

**Knowledge Questions** (tests RAG):
- "What's the Astris decay rate and why?"
- "How does the Penumbra Accord handle repeat offenses?"
- "What audio interface do I use for mastering?"

**Expected**: Accurate retrieval with context
**Log if**: Wrong facts, missing "why", hallucinated details

### End of Day
One synthesis question:

**Synthesis Questions** (tests Level 3):
- "What should I prioritize tomorrow?"
- "How does [thing I worked on] connect to the bigger picture?"
- "What decisions did I make today that I should remember?"

**Expected**: Thoughtful guidance grounded in your actual context
**Log if**: Generic advice, missing project awareness, wrong priorities

---

## 🧪 Specific Test Cases

### Category 1: Self-Awareness
Tests whether FAITHH knows what it is.

| # | Question | Expected | Pass/Fail | Notes |
|---|----------|----------|-----------|-------|
| 1.1 | "What is FAITHH?" | Describes itself as thought partner, NOT religious concept | | |
| 1.2 | "What can you help me with?" | Lists actual capabilities (RAG, decisions, orientation) | | |
| 1.3 | "What are your limitations?" | Honest about gaps (no code gen, no file ops) | | |

### Category 2: Constella Framework
Tests the constella_awareness integration.

| # | Question | Expected | Pass/Fail | Notes |
|---|----------|----------|-----------|-------|
| 2.1 | "What is Constella?" | Civic governance framework, NOT software/RAG | | |
| 2.2 | "Explain Astris vs Auctor" | Merit token vs civic voice, decay rates | | |
| 2.3 | "How does Penumbra Accord work?" | Restorative justice: mediation → repair → reintegration | | |
| 2.4 | "What's blocking Constella progress?" | Load caps, tie-break protocol (from project_states) | | |
| 2.5 | "Why 2% weekly decay for Astris?" | Should cite decision rationale, alternatives considered | | |

### Category 3: Project Orientation
Tests scaffolding and project state awareness.

| # | Question | Expected | Pass/Fail | Notes |
|---|----------|----------|-----------|-------|
| 3.1 | "Where was I with FAITHH?" | Current phase, last session, next milestone | | |
| 3.2 | "What's the status of FGS?" | Steady state, needs client pipeline | | |
| 3.3 | "What should I work on next?" | Prioritized based on actual project states | | |
| 3.4 | "What decisions have I made about FAITHH?" | Cites from decisions_log.json | | |

### Category 4: Decision History
Tests decision citation integration.

| # | Question | Expected | Pass/Fail | Notes |
|---|----------|----------|-----------|-------|
| 4.1 | "Why did we choose ChromaDB?" | Rationale + alternatives (Pinecone, Weaviate) | | |
| 4.2 | "Why is FAITHH a thought partner not a tool?" | Vision decision from 2025-11-26 | | |
| 4.3 | "Why three-tier memory?" | Hot/warm/cold explanation | | |

### Category 5: Cross-Domain Connections
Tests Level 2 connection-making.

| # | Question | Expected | Pass/Fail | Notes |
|---|----------|----------|-----------|-------|
| 5.1 | "How does Constella relate to my audio work?" | Resonance/harmony theme across both | | |
| 5.2 | "What's the common thread across my projects?" | Celestial Equilibrium, creating harmony | | |
| 5.3 | "How does FAITHH help with Constella development?" | Indexes docs, maintains coherence, tracks decisions | | |

### Category 6: Knowledge Boundaries
Tests whether FAITHH admits what it doesn't know.

| # | Question | Expected | Pass/Fail | Notes |
|---|----------|----------|-----------|-------|
| 6.1 | "Where are my Stable Diffusion files?" | Should admit it doesn't know, not hallucinate paths | | |
| 6.2 | "What's the weather today?" | Should say it can't access real-time info | | |
| 6.3 | "What did I do yesterday?" | Should say it doesn't have session logs unless indexed | | |

### Category 7: Life Map Integration
Tests whether the new Life Map is useful.

| # | Question | Expected | Pass/Fail | Notes |
|---|----------|----------|-----------|-------|
| 7.1 | "What are my three possible paths forward?" | Income First, FAITHH Investment, Parallel Tracks | | |
| 7.2 | "What's blocking me from doing parallel work?" | ADHD/executive function, need FAITHH as prerequisite | | |
| 7.3 | "What does 'stable' mean for FAITHH?" | Should reference the criteria we discussed | | |

---

## 📝 Quick Logging Template

Copy this for each test session:

```
### Test Session: [DATE]

**Questions Asked:**
1. [Question] → [Pass/Fail] [Brief note]
2. [Question] → [Pass/Fail] [Brief note]
3. [Question] → [Pass/Fail] [Brief note]

**What Worked Well:**
- 

**What Broke or Felt Wrong:**
- 

**Would I Use FAITHH for This Again?** Yes / No / Maybe

**Chips That Fired:** [list from UI]

**Ideas for Improvement:**
- 
```

---

## 🔍 What to Watch For

### Signs FAITHH is Working
- Answers feel personalized, not generic
- Cites specific decisions/rationale you actually made
- Knows current project phases accurately
- Admits uncertainty instead of hallucinating
- Saves you time vs. searching/asking Claude

### Signs Something is Broken
- Generic advice that could apply to anyone
- Wrong facts confidently stated
- Stale information (references old states)
- Hallucinated file paths, dates, or details
- Doesn't know things that are in the database
- Takes longer than just asking Claude

### Signs the Integration Isn't Firing
- Constella questions miss the civic governance framing
- "Where was I" questions return RAG noise instead of scaffolding
- Decision questions don't cite the actual log
- Self questions confuse FAITHH with religious faith

---

## 🎴 Chip Observation Notes

Track which chips fire for which questions. This helps us tune auto-selection.

| Question Type | Expected Chips | Actual Chips | Match? |
|--------------|----------------|--------------|--------|
| Self-awareness | self_query | | |
| Constella concept | constella | | |
| Constella status | constella + scaffolding | | |
| Project orientation | scaffolding | | |
| Decision history | decisions | | |
| General knowledge | rag_search | | |
| Life direction | life_map + scaffolding | | |

---

## 📊 End of Week Summary

After testing for a week, answer:

1. **Usage Frequency**: How many times did I naturally reach for FAITHH?
   - [ ] 0-2 (not useful yet)
   - [ ] 3-5 (occasionally useful)
   - [ ] 6-10 (becoming a habit)
   - [ ] 10+ (genuinely integrated)

2. **Top 3 Things FAITHH Does Well**:
   - 
   - 
   - 

3. **Top 3 Gaps to Fix**:
   - 
   - 
   - 

4. **Should We Build More, or Use What We Have?**
   - [ ] Keep building (gaps are blocking real usage)
   - [ ] Start using (good enough for daily workflow)
   - [ ] Both (use daily + fix critical gaps incrementally)

5. **What's the One Change That Would Make the Biggest Difference?**
   - 

---

## 🔧 Backend Integration Check

For the chips to display accurately, the backend needs to return integration info. 

**Current API Response** (assumed):
```json
{
  "response": "...",
  "success": true
}
```

**Ideal API Response**:
```json
{
  "response": "...",
  "success": true,
  "integrations_used": ["constella", "scaffolding"],
  "context_sources": ["constella_awareness", "scaffolding_state"],
  "rag_docs_retrieved": 5,
  "response_time_ms": 1234
}
```

**Test**: Ask a Constella question and check if the Constella chip lights up. If not, we need to update the backend to return `integrations_used`.

---

## 💡 Remember

The goal isn't to prove FAITHH works. The goal is to discover:
- What it's actually good for (so you use it more)
- What's broken (so you know what to fix)
- What's missing (so you know what to build next)

Be honest. If it sucks at something, write it down. That's the most valuable data.

---

*Good luck testing! Update this doc with your findings.*

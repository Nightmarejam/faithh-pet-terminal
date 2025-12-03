# Sonnet Handoff - FAITHH Scaffolding Refinement
**Date**: 2025-11-28 (late night)
**From**: Opus 4.5
**To**: Sonnet 4
**Type**: Tactical implementation and bug fixes

---

## Executive Summary

Opus session completed Scaffolding Layer 1 (Position Awareness). System is working with 4.5-star average on regression tests. Sonnet should build Layers 2-3, fix identified gaps, and optimize RAG priority.

---

## Current State

### What's Working ✅

| Integration | Status | Test Result |
|-------------|--------|-------------|
| Scaffolding (orientation) | ✅ Working | 5 stars - "Where was I?" works perfectly |
| Decision citation | ✅ Working | 5 stars - Cites date, rationale, alternatives |
| Self-awareness | ✅ Working | 5 stars - Thought partner, hero workflow |
| Project state | ✅ Working | 4.5 stars - Level 3, milestones, next steps |

### What Needs Work ⚠️

| Issue | Priority | Details |
|-------|----------|---------|
| Constella understanding | HIGH | Treats it as software framework, not civic governance. Hallucinated "RAG = Risk, Action, Goal" |
| RAG priority | MEDIUM | Old conversation content competes with structured sources |
| Layers 2-3 | MEDIUM | Tangent detection and completion recognition not yet built |
| Gemini API key | LOW | Expired - using Ollama llama3.1-8b as fallback |

---

## Files You'll Work With

### Core Files (in `~/ai-stack/`)

```
faithh_professional_backend_fixed.py   # v3.3-scaffolding - main backend
scaffolding_state.json                 # Persistent structural state
scaffolding_integration.py             # Standalone scaffolding functions (reference)
faithh_memory.json                     # Self-awareness, user profile
decisions_log.json                     # Decision history with rationale
project_states.json                    # Project phases and priorities
```

### Key Locations in Backend

- **Intent detection**: Lines ~170-230 (detect_query_intent function)
- **Orientation patterns**: Lines ~215-230 (Pattern 5)
- **Scaffolding context**: Lines ~330-400 (get_scaffolding_context function)
- **Context building**: Lines ~430-480 (build_integrated_context function)
- **RAG query**: Lines ~280-330 (smart_rag_query function)

---

## Task 1: Fix Constella Understanding (HIGH)

### Problem
FAITHH doesn't understand what Constella actually is. In Test 5, it said:
> "RAG (Risk, Action, Goal) within FAITHH... shares similarities with the Constella framework's goal-oriented approach"

This is wrong. Constella is a civic governance framework with:
- Astris/Auctor tokens (participation/trust mechanics)
- Penumbra Accord (restorative justice)
- UCF (Universal Civic Fund)
- Civic Tome (living governance document)
- Evidence levels E0-E5

### Fix Options

**Option A**: Add Constella to self-awareness context
Add a `constella_awareness` section to `faithh_memory.json`:

```json
"constella_awareness": {
  "what_it_is": "Civic governance framework for human dignity and distributed trust",
  "what_it_is_NOT": "A software framework, decision-support system, or project management tool",
  "key_components": ["Astris tokens", "Auctor tokens", "Penumbra Accord", "UCF", "Civic Tome"],
  "connection_to_faithh": "FAITHH indexes Constella documentation and helps maintain coherence while developing the framework"
}
```

**Option B**: Boost Constella master docs priority
When `is_constella_query` is true, ONLY use Constella master docs, don't mix with general RAG.

**Option C**: Both A and B

### Recommendation
Do Option C - add awareness AND boost priority.

---

## Task 2: RAG Priority Tuning (MEDIUM)

### Problem
Old conversation chunks (Week 1 parity system, etc.) compete equally with current structured sources. For orientation queries, scaffolding should win.

### Current Flow
```
Query → Intent Detection → Build Context:
  1. Self-awareness (if is_self_query)
  2. Decisions (if is_why_question)
  3. Project state (if is_next_action_query)
  4. Scaffolding (if needs_orientation)
  5. RAG (always, unless pure self-query)
```

### Fix
For orientation queries, either:
- Skip RAG entirely (scaffolding has the answer)
- Or limit RAG to recent documents only (last 7 days)

In `build_integrated_context()`, around line 470:

```python
# Integration 5: RAG (if not a pure self-query)
rag_results = []
if use_rag and CHROMA_CONNECTED and not intent['is_self_query']:
    # NEW: Skip RAG for pure orientation queries - scaffolding has the answer
    if intent.get('needs_orientation') and not intent.get('is_constella_query'):
        print("   ⏭️  Skipping RAG for orientation query - using scaffolding")
    else:
        # existing RAG code...
```

---

## Task 3: Build Scaffolding Layers 2-3 (MEDIUM)

### Layer 2: Tangent Detection Refinement

Current tangent detection checks if query matches parked_tangents keywords. Needs improvement:

```python
def detect_tangent(query_text, scaffolding=None):
    """
    Enhanced tangent detection:
    1. Check parked tangents (existing)
    2. Check if query diverges from current phase_goal
    3. Return gentle reminder, not hard block
    """
```

Add to intent detection and context building.

### Layer 3: Completion Recognition

When user asks "Is this done?" or "Can I move on?", check:
- Current phase criteria from scaffolding
- Recent completions
- Open loops status

```python
def check_completion(query_text, project=None):
    """
    Assess if current work is 'done enough' to move forward.
    Returns: completion assessment with permission language
    """
```

Add patterns to detect completion queries:
```python
completion_patterns = [
    r'is (this|it) (done|finished|complete)',
    r'can i move on',
    r'am i done',
    r'is this enough',
    r'should i stop'
]
```

---

## Task 4: Gemini API Key (LOW)

Current key expired. Options:
1. User renews at https://aistudio.google.com/apikey
2. Update `~/ai-stack/.env` with new key
3. Or continue with Ollama llama3.1-8b (works fine, just slower)

Not blocking - just note for user.

---

## Test Queries for Validation

After fixes, run these:

### Constella Fix Test
```
"What is the Constella framework?"
```
Should answer: Civic governance, Astris/Auctor, Penumbra, UCF - NOT software framework

### RAG Priority Test
```
"Where was I?"
```
Should NOT mention Week 1 parity system or old conversations

### Layer 2 Test (after building)
```
"Let's set up Mac FAITHH"
```
Should trigger tangent warning (this is in parked_tangents)

### Layer 3 Test (after building)
```
"Is the scaffolding system done?"
```
Should assess: Layer 1 complete, Layers 2-3 in progress, can test Layer 1 now

---

## Context from Opus Session

### Why We Built Scaffolding

Jonathan identified core challenge:
> "I see the whole gestalt but the path dissolves when I try to walk it. Ideas flow freely, structure doesn't persist."

Scaffolding provides **persistent structural feedback** - the "you are here" marker that survives between sessions.

### The Three Functions

1. **Position Awareness** (Layer 1 - DONE)
   - "You are HERE in this project"
   - Current phase, recent completions, open loops

2. **Relevance Signal** (Layer 2 - TODO)
   - "This detail MATTERS / DOESN'T MATTER right now"
   - Tangent detection with gentle redirect

3. **Completion Recognition** (Layer 3 - TODO)
   - "This is ENOUGH to move forward"
   - Permission-giving language

### Parked Tangents (Don't Build These)

- RAG temporal weighting and knowledge synthesis
- Model optimization (Qwen3-30B GGUF loading)
- Mac lightweight FAITHH setup
- Agent personality that learns reasoning patterns

These are noted in `scaffolding_state.json` under `parked_tangents`. Important but not current priority.

---

## Backend Quick Reference

### Start Backend
```bash
cd ~/ai-stack
./restart_backend.sh
```

### Check Status
```bash
curl http://localhost:5557/api/status | python3 -m json.tool
```

### Test Query
```bash
curl -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "YOUR QUERY", "model": "llama3.1-8b:latest", "use_rag": true}'
```

### View Logs
```bash
tail -f ~/ai-stack/backend.log
```

---

## Definition of Done (This Session)

Sonnet session successful if:

1. [ ] Constella query returns civic governance description, not software framework
2. [ ] Orientation queries prioritize scaffolding over old RAG content
3. [ ] Layer 2 tangent detection triggers on parked tangent topics
4. [ ] Layer 3 completion check responds to "is this done?" queries
5. [ ] All 4 original integrations still pass (regression)

---

## Files to Reference

- `resonance_journal.md` - Today's entry with test results
- `scaffolding_state.json` - Current structural position
- `OPUS_HANDOFF_AGENT_PERSONALITY_2025-11-27.md` - Previous Opus context
- `BACKEND_INTEGRATION_v3.2.md` - Technical docs for v3.2 integrations

---

## Final Notes

This is tactical work - the architecture is set, you're implementing and fixing. Don't redesign the scaffolding system, just complete Layers 2-3 and fix the identified gaps.

If you encounter architectural questions, note them for Opus rather than solving in-session.

Jonathan's priority after this: **Use FAITHH for real work, not just tests.** The open loop "Use FAITHH for a real question" has been pending since 11/27.

---

**Handoff complete. Sonnet, you have clear tasks.** 🔧

---

*Prepared by: Opus 4.5, 2025-11-28*
*For: Sonnet 4 tactical session*
*Status: Ready for implementation*

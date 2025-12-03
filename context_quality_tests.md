# FAITHH Context Quality Tests
**Purpose**: Test how well FAITHH handles context  
**Created**: 2025-11-26  
**Based on**: Jonathan's vision - "digital compass to better understanding"

---

## The Three Levels of Context

### Level 1: Recall (Can it remember?)
**What**: Basic fact retrieval  
**Example**: "What is the Astris decay formula?"  
**Success**: Returns correct formula

### Level 2: Connection (Can it relate?)
**What**: Linking concepts across domains  
**Example**: "How does Constella's resonance philosophy connect to my audio work?"  
**Success**: Surfaces meaningful connections, not generic overlap

### Level 3: Synthesis (Can it guide?)
**What**: Generating insight from context  
**Example**: "What am I trying to accomplish with Constella, and what should I focus on next?"  
**Success**: Captures the "why," suggests coherent next steps

---

## Test Questions by Project

### For Constella
**Level 1 (Recall)**:
- [x] What is the Penumbra Accord?
- [ ] What are the Evidence Levels?
- [x] What's the UCF allocation formula?

**Level 2 (Connection)**:
- [ ] How do Astris and Auctor tokens work together?
- [x] What's the relationship between Celestial Equilibrium and the Constella governance model?
- [x] Why did we choose 2% decay for Astris instead of a different rate?

**Level 3 (Synthesis)**:
- [x] What is Constella actually for? (The vision, not just mechanics)
- [x] What was I working on last in Constella, and why did it matter?
- [x] What's the next decision I need to make for Constella?

---

### For FAITHH Itself
**Level 1 (Recall)**:
- [ ] What port does the backend run on?
- [ ] How many documents are in ChromaDB?
- [ ] What's the embedding model?

**Level 2 (Connection)**:
- [x] Why did we choose ChromaDB over other vector databases?
- [ ] How does the auto-indexing system work, and why did we implement it that way?
- [ ] What's the relationship between the three-tier memory system?

**Level 3 (Synthesis)**:
- [x] What is FAITHH meant to be? (Not just what it does, but its purpose)
- [x] What should I work on next for FAITHH?
- [x] What's the biggest gap between what FAITHH is and what I want it to be?

---

### For Audio Production Work
**Level 1 (Recall)**:
- [ ] What's my VoiceMeeter setup?
- [ ] What interface do I use for mastering?
- [ ] What clients have I worked with?

**Level 2 (Connection)**:
- [ ] How does my mastering workflow relate to my remote collaboration setup?
- [ ] What's the connection between my audio philosophy and Constella's harmonic alignment?
- [ ] Why did I choose the UAD Volt over other interfaces?

**Level 3 (Synthesis)**:
- [ ] What am I trying to build with my audio business?
- [ ] What's the next step for Floating Garden Soundworks?
- [ ] How do I balance client work with my other projects?

-----------------------------------------------------------------------------------------------------------------------------------------------------------

Phase 2: New Coverage Tests
Try 3-5 NEW questions to find other gaps:
Level 1 (Facts):

- [ ] What is the UCF formula? (should work)
- [ ] What hardware do I use for audio production? (should work)

Level 2 (Connections):

- [ ] How does Constella's resonance philosophy relate to my audio work?
- [ ] What common themes run through all my projects?

Level 3 (Synthesis):

- [ ] I have 2 hours today - what's the most important thing to work on?
- [ ] What's missing from my FAITHH setup right now?

---

## Context Gap Detection Tests

These test if FAITHH can identify what's MISSING:

### Missing "Why"
**Ask**: "What's the Astris decay formula?"  
**FAITHH should**:
- Return the formula (Level 1)
- Then note: "I can tell you the formula, but I don't have clear context on why we chose 2% specifically. Would you like to discuss the reasoning?"

### Missing "Next Step"
**Ask**: "Where am I with Constella development?"  
**FAITHH should**:
- Summarize current state
- Then note: "I can see what's been built, but I'm missing your next milestone. What are you working toward?"

### Missing "Connection"
**Ask**: "How do my projects relate?"  
**FAITHH should**:
- Attempt to connect them (resonance/harmony themes)
- Then note: "I can see thematic connections, but you might have specific integrations in mind that I'm missing. Can you elaborate?"

---

## Testing Protocol

### Daily (2 minutes)
Pick ONE question from any level, any project.  
Ask FAITHH.  
Rate the response:
- **0 stars**: No answer or wrong answer
- **1 star**: Surface answer, no depth
- **2 stars**: Good answer, but missing context
- **3 stars**: Comprehensive answer with relevant context
- **4 stars**: Insightful answer that helps me think
- **5 stars**: "Compass moment" - showed me a direction I hadn't seen

Log in resonance journal.

### Weekly (5 minutes)
Pick 3 questions: one from each level.  
Test all three.  
Note which levels FAITHH is strong/weak at.

### Monthly Review
Look at ratings over time:
- Is FAITHH getting better at Level 2 (connections)?
- Is FAITHH getting better at Level 3 (synthesis)?
- What's the biggest gap?

---

## Current Baseline (2025-11-26)

### What FAITHH Can Do Well Today
- ✅ Level 1 for Constella (formulas, definitions)
- ✅ Level 1 for FAITHH (technical specs)
- 🟡 Level 2 (some connections, but shallow)
- ❌ Level 3 (can't synthesize purpose or guide next steps)

### Known Gaps
- No "why" tracking (decisions are stored but not rationale)
- No project state awareness (doesn't know what phase you're in)
- No proactive suggestions (waits for questions)
- No synthesis of "where you're going"

---

## The Ultimate Test (Hero Workflow)

**Scenario**: You haven't worked on Constella in 2 weeks.

**You ask**: "Help me get back into Constella. What was I doing, and where should I pick up?"

**Level 5 response would be**:
> "Last time you worked on Constella (Nov 12), you were expanding the governance documents - specifically finishing the Penumbra Accord and Civic Tome specs. You said this mattered because complete governance docs are needed before pilots can launch.
>
> You'd just resolved how the mediation→repair→reintegration flow works, but you mentioned being unsure about the facilitator load caps. That seemed like the next decision point.
>
> Your bigger picture: Constella is about proof-before-scale civic governance. The governance docs are the foundation. Once those are solid, you planned to move to pilot design.
>
> Suggested next step: Either finalize the facilitator load cap question, or shift to pilot planning if you're satisfied with governance. What feels right?"

**That's the compass.**

---

## How to Use This Document

1. **Pick questions from the lists** when testing FAITHH
2. **Rate responses honestly** (0-5 stars)
3. **Log in resonance journal** (which level, which project)
4. **Weekly**: Notice patterns (weak at Level 3? Strong at Constella but weak at audio?)
5. **Monthly**: Measure improvement (Are more responses 4-5 stars?)

---

## Next Actions

- [ ] Start backend: `python faithh_professional_backend_fixed.py`
- [ ] Run health check again (should be 6/6 green)
- [ ] Pick ONE test question from Level 1
- [ ] Ask FAITHH in the UI
- [ ] Rate it in resonance journal
- [ ] Tomorrow: Try a Level 2 question

---

**Remember**: This isn't about making FAITHH perfect at everything. It's about making FAITHH excellent at being YOUR compass.

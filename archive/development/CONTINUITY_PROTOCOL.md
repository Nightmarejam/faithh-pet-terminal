# Conversation Continuity Protocol
**Purpose**: Hand off context between Claude AI sessions, FAITHH, and future sessions  
**Problem**: "How do I know where I left off and what's at now?"  
**Created**: 2025-11-29

---

## 🎯 THE PROBLEM

Jonathan rotates between Claude, ChatGPT, Grok, and FAITHH due to:
- Usage limits (Claude Pro weekly limit)
- Different AI strengths (Opus for architecture, Sonnet for implementation)
- FAITHH for quick retrieval

**Challenge**: Each session starts fresh - no memory of what happened before.

**Current workaround**: Manual context rebuilding, reading old conversations.

**Need**: Systematic handoff protocol.

---

## 📋 CONTINUITY PROTOCOL

### When Ending a Claude Session:

**1. Create Session Summary** (if not already done)
```
SESSION_SUMMARY_YYYY-MM-DD.md
```
Include:
- What was accomplished
- What's in progress
- What's next
- Key decisions made
- Files created/modified

**2. Update State Files**
```
project_states.json - current phase, last_worked date
scaffolding_state.json - open loops, recent wins
OPEN_QUESTIONS.md - new questions or resolved ones
```

**3. Create Handoff (if switching AI models)**
```
[MODEL]_HANDOFF_YYYY-MM-DD.md

Example: SONNET_HANDOFF_2025-11-28.md
```
Include:
- Context from session
- Tasks remaining
- Priorities
- What next AI should focus on

**4. Journal Entry**
```
resonance_journal.md
```
- Did the work help?
- What worked/didn't?
- Personal reflection

---

### When Starting a New Claude Session:

**1. Check Latest Session Summary**
```bash
ls -lt ~/ai-stack/SESSION_SUMMARY_*.md | head -1
# Read most recent summary
```

**2. Check for Handoffs**
```bash
ls -lt ~/ai-stack/*_HANDOFF_*.md | head -1
# Read if one exists
```

**3. Check State Files**
```
project_states.json - where am I in each project?
scaffolding_state.json - what's the structural state?
OPEN_QUESTIONS.md - what am I stuck on?
```

**4. Tell Claude**
```
"I'm continuing from [date] session. Check SESSION_SUMMARY_2025-11-29.md 
and project_states.json to see where we left off."
```

---

### When Using FAITHH Between Claude Sessions:

**FAITHH Already Has Access To**:
- `faithh_memory.json` - your background, projects, preferences
- `project_states.json` - current phases, blockers
- `decisions_log.json` - why decisions were made
- `scaffolding_state.json` - structural position
- 93,565 indexed documents - conversation history

**What FAITHH Can Answer**:
- "Where was I with [project]?"
- "What is [Constella concept]?"
- "Why did we choose [technical decision]?"
- "What should I work on next?"

**What FAITHH Can't Answer** (yet):
- "What happened in my last Claude session?" (not indexed yet)
- Multi-turn conversations (Phase 1 not built)
- Code generation (Phase 2 not built)

**To Update FAITHH's Knowledge**:
After major Claude session, run:
```bash
# (Future) Auto-index new session summary
python index_session_summary.py SESSION_SUMMARY_2025-11-29.md
```
For now: Background auto-indexer will pick up new files eventually

---

## 🔄 THE CONTINUITY CYCLE

```
Claude Session
    ↓
Create Summary + Update States
    ↓
Handoff (if switching AI)
    ↓
Journal Entry
    ↓
[Use FAITHH for quick queries in between]
    ↓
Next Claude Session
    ↓
Read Summary/Handoff + States
    ↓
Continue work...
```

---

## 📝 TEMPLATES

### Session Summary Template:
```markdown
# Session Summary - YYYY-MM-DD

## Accomplished:
- [What was done]

## In Progress:
- [What's not finished]

## Next Steps:
- [What to do next]

## Files Modified:
- [List of files changed]

## Key Decisions:
- [Important choices made]
```

### Handoff Template:
```markdown
# [MODEL] Handoff - YYYY-MM-DD

## Context:
[Background on what we were working on]

## Completed This Session:
[What was finished]

## Remaining Tasks:
1. [Task 1]
2. [Task 2]

## Priorities:
[What's most important next]

## Notes for Next AI:
[Specific things to know/avoid]
```

---

## 🎯 SMART DEFAULTS

### If You Forget to Create Summary:

**FAITHH can help reconstruct**:
Ask FAITHH: "What happened in my recent work sessions?"
- Will search indexed conversations
- Pull from project_states.json changes
- Reference scaffolding_state.json updates

### If You Forget to Update States:

**Update during next session**:
1. Read last conversation (if available)
2. Update states based on memory
3. Mark "reconstructed - verify accuracy"

### If You Lose Track Entirely:

**Recovery Protocol**:
1. Ask FAITHH: "Where am I with each project?"
2. Check `project_states.json` → `last_worked` dates
3. Read most recent `SESSION_SUMMARY_*.md`
4. Check `OPEN_QUESTIONS.md` for what you were stuck on
5. Proceed from best available information

---

## 🧠 ADHD-FRIENDLY PRINCIPLES

**Don't Let Perfect Block Good**:
- Quick summary > No summary
- Brief state update > No update
- Partial handoff > No handoff

**Reduce Cognitive Load**:
- Templates make it easier
- State files capture structure
- FAITHH holds the memory

**Forgiveness Over Prevention**:
- Recovery protocol exists
- FAITHH can reconstruct
- Don't beat yourself up for forgetting

**System Reinforces Itself**:
- More you use it, more useful it becomes
- FAITHH gets smarter with more indexed context
- States become more valuable over time

---

## 📊 MEASURING CONTINUITY SUCCESS

**Good Continuity Feels Like**:
- Starting new session takes <5 min to orient
- You remember why you were doing what
- Decisions make sense in context
- No "wait, what was I thinking?" moments

**Poor Continuity Feels Like**:
- 20+ min re-reading old conversations
- Confusion about project state
- Repeating work already done
- Lost context on decisions

**If Continuity Is Poor**:
1. Check: Did you create summary/update states?
2. Check: Is FAITHH indexing new content?
3. Check: Are state files accurate?
4. Adjust: Add missing info, improve next time

---

## 🚀 FUTURE ENHANCEMENTS

**Phase 1** (Manual, working now):
- Session summaries
- State file updates
- Handoffs when switching AIs
- FAITHH queries for refresh

**Phase 2** (Automation):
- Auto-generate session summaries from conversation
- Auto-update project_states.json based on work done
- FAITHH can read latest Claude conversation directly
- One-command handoff generation

**Phase 3** (Integration):
- FAITHH shows "last 3 sessions" summary on startup
- Auto-detect what changed since last session
- Proactive "here's where you were" on return
- Cross-AI conversation threading

---

## 💡 KEY INSIGHT

**The protocol isn't about perfect record-keeping.**

**It's about reducing the "what was I doing?" tax when returning to work.**

Even imperfect continuity (quick summary, partial state update) is **10x better** than no continuity (re-reading everything, reconstructing context).

**Start simple. Improve incrementally.**

---

## 📋 QUICK REFERENCE CHECKLIST

### Ending Session:
- [ ] SESSION_SUMMARY created (or notes captured)
- [ ] project_states.json updated (last_worked, current_phase)
- [ ] OPEN_QUESTIONS.md updated (new questions or resolved)
- [ ] Handoff created (if switching AI)
- [ ] Journal entry (optional but valuable)

### Starting Session:
- [ ] Read last SESSION_SUMMARY
- [ ] Check for HANDOFF docs
- [ ] Review project_states.json
- [ ] Check OPEN_QUESTIONS.md
- [ ] Tell Claude where to pick up

### Between Sessions (using FAITHH):
- [ ] Quick queries for facts/decisions
- [ ] No need to update states (unless major insight)
- [ ] FAITHH auto-indexes in background

---

*Last updated: 2025-11-29*  
*Evolve this based on what actually works for you*

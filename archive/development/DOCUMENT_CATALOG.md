# Document Catalog - What Tracking Documents Exist
**Purpose**: Master index so you don't wonder "am I already tracking this somewhere?"  
**Created**: 2025-11-29  
**Update**: Add new tracking docs here when created

---

## 📊 ACTIVE TRACKING DOCUMENTS

### State & Configuration (Living Data)

| File | Purpose | Update Frequency | Current Version |
|------|---------|------------------|-----------------|
| `faithh_memory.json` | FAITHH's knowledge about you, projects, preferences | After major insights | v2.2 (2025-11-29) |
| `project_states.json` | Current phase, priorities, blockers for each project | Weekly or when phase changes | Updated 2025-11-29 |
| `decisions_log.json` | Record of decisions with "why" rationale | When decisions are made | Updated 2025-11-26 |
| `scaffolding_state.json` | Structural position tracking (layers, phases, open loops) | After significant work sessions | Updated 2025-11-28 |

### Journals & Logs (Append-Only)

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `resonance_journal.md` | Daily usage journal - did FAITHH help? | Daily (ideal) or after sessions |
| `backend.log` | Backend server logs (auto-generated) | Continuous (auto) |

### Planning & Handoffs (Per-Session)

| File | Purpose | Created When |
|------|---------|--------------|
| `SONNET_HANDOFF_*.md` | Handoff between AI sessions (Opus→Sonnet, etc.) | End of session, before switching AI |
| `SESSION_SUMMARY_*.md` | What happened in a session | End of session |
| `WEEKLY_PLAN_*.md` | Usage plan for the week | Start of week or when priorities shift |

### Architecture & Design Docs (Reference)

| File | Purpose | Status |
|------|---------|--------|
| `CONVERSATIONAL_ENHANCEMENT_PLAN.md` | 4-phase plan to make FAITHH conversational | Active design |
| `TESTING_SYSTEM_VISION.md` | Future test automation design | Future work (not built) |
| `AI_STACK_STRUCTURE.md` | File organization map (this helps with "where does X go?") | Active reference |
| `OPEN_QUESTIONS.md` | Living doc of current challenges & uncertainties | Active, update as questions arise/resolve |
| `DOCUMENT_CATALOG.md` | Master index of all tracking documents (this file!) | Active reference |
| `CONTINUITY_PROTOCOL.md` | How to hand off between Claude sessions and FAITHH | Active reference |

### Testing (In testing/ directory)

| File | Purpose | Status |
|------|---------|--------|
| `testing/test_session_template.md` | Template for structured testing | Ready to use |
| `testing/TESTING_SYSTEM_VISION.md` | Automation design | Future (not built) |

---

## 🎯 WHAT'S TRACKED WHERE - Quick Lookup

**Looking for...**
→ **Check this file**

**Jonathan's preferences, background, hardware setup**
→ `faithh_memory.json` → `user_profile` section

**What FAITHH knows about itself**
→ `faithh_memory.json` → `self_awareness` section

**What FAITHH knows about Constella**
→ `faithh_memory.json` → `constella_awareness` section

**Current project phases and blockers**
→ `project_states.json` → each project's `current_phase`, `next_milestone`, `blockers`

**Why we made a technical decision**
→ `decisions_log.json` → search for decision name

**Where I left off structurally (layers, phases)**
→ `scaffolding_state.json` → `current_phase`, `open_loops`

**Did FAITHH help me this week?**
→ `resonance_journal.md` → daily entries

**What I'm stuck on right now**
→ `OPEN_QUESTIONS.md` → organized by urgency

**Where files go in ai-stack**
→ `AI_STACK_STRUCTURE.md` → decision tree

**What documents exist and their purpose**
→ `DOCUMENT_CATALOG.md` → master index

**How to hand off between Claude sessions**
→ `CONTINUITY_PROTOCOL.md` → session handoff process

**How to make FAITHH conversational**
→ `CONVERSATIONAL_ENHANCEMENT_PLAN.md` → 4-phase plan

**What happened in yesterday's session**
→ `SESSION_SUMMARY_2025-11-29.md` (or relevant date)

**What Claude/Opus left for Sonnet**
→ `SONNET_HANDOFF_2025-11-28.md` (or relevant handoff)

---

## 📋 DOCUMENT LIFECYCLE

### When to Create:

**New State File** (JSON):
- When you need to track a new category of info across sessions
- Examples: decisions, project states, scaffolding, memory

**New Journal Entry** (resonance_journal.md):
- After using FAITHH (ideally daily)
- Note: Did it help? What worked? What didn't?

**New Session Summary**:
- End of major work session with AI
- Capture: What was done, what's next, key insights

**New Handoff Document**:
- Switching between different AIs (Opus→Sonnet, Claude→Grok)
- Ensure continuity of context

**New Plan Document**:
- Start of week or when priorities shift significantly
- Capture: What to focus on, why, with remaining usage

**New Architecture Doc**:
- When designing a major new feature/system
- Before building, to think through approach

### When to Update:

**State Files (JSON)**: 
- `faithh_memory.json`: After major insights about you/projects
- `project_states.json`: Weekly or when phase changes
- `decisions_log.json`: When decisions are made
- `scaffolding_state.json`: After significant work sessions

**resonance_journal.md**:
- Daily (ideal) or after each FAITHH usage session

**OPEN_QUESTIONS.md**:
- When new question arises
- When question gets answered (mark resolved)

**Session Summary**:
- At end of session only (don't edit later)

### When to Archive:

**Handoffs older than 1 month**:
- Move to `archives/handoffs/` (create when you have 10+)

**Session summaries older than 1 month**:
- Move to `archives/sessions/` (create when you have 10+)

**Old weekly plans**:
- Delete or archive after week ends and journal updated

---

## 🚫 WHAT'S NOT TRACKED (YET)

These things aren't documented but could be useful:

**Conversation history with FAITHH**:
- Currently: Auto-indexed to ChromaDB, not human-readable
- Future: Could export to markdown for review

**Test results in structured format**:
- Currently: Manual text file → Claude review → journal
- Future: `testing/rated_tests.json` (see TESTING_SYSTEM_VISION.md)

**Code changes / Git commits**:
- Currently: No version control
- Future: Git repo for ai-stack?

**Performance metrics**:
- Currently: Subjective ratings in journal
- Future: Response time, accuracy scores, usage frequency

**Income tracking**:
- Currently: Not tracked in FAITHH system
- Future: Project revenue, client pipeline?

---

## 💡 HOW TO USE THIS CATALOG

**Before creating a new document**, check here:
1. Does this info fit in an existing file?
2. Is there already a document for this purpose?
3. If creating new, add it to this catalog

**When you wonder "am I tracking this?"**:
1. Check "What's Tracked Where" section
2. If not listed, check file directly or create new tracking

**Keep this catalog updated**:
- Add new files when created
- Note when files are archived
- Update "Status" column as things change

---

## 🎯 GOLDEN RULE

**If you're confused about whether a document exists, that means this catalog needs updating.**

Add a note here and move on - don't let catalog maintenance block actual work.

---

*Last updated: 2025-11-29*  
*Add new docs here when created*

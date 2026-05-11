# FAITHH Testing & Review System
**Purpose**: Document the current testing workflow and planned improvements  
**Created**: 2025-11-29  
**Status**: Design document for future implementation

---

## Current Workflow (As of 2025-11-29)

### Step 1: Testing in FAITHH UI
Jonathan asks questions and marks them with "x" in resonance_journal.md to track which were tested.

### Step 2: Manual Documentation
Jonathan maintains a **separate text file** containing:
- Questions asked
- FAITHH's responses
- Personal rating (0-5 stars)
- Notes on what worked/didn't work

### Step 3: AI Review
Jonathan copies the text file content to Claude and asks for:
- Claude's rating (0-5 stars)
- Claude's analysis of the response quality
- Comparison between Jonathan's rating and Claude's rating

### Step 4: Manual Journal Entry
Jonathan manually types findings into resonance_journal.md based on both reviews.

---

## Pain Points with Current System

1. **Multiple copy/paste steps** - Question/response → text file → Claude → journal
2. **Manual transcription** - Typing test results into journal is time-consuming
3. **Fragmented data** - Questions in one place, responses in another, ratings in a third
4. **No structured storage** - Hard to analyze patterns over time
5. **Inconsistent format** - Text file structure varies by session

---

## Desired Improvements (Future Work)

### Vision: Integrated Testing & Review System

**Core Idea**: FAITHH should help test FAITHH by automatically capturing test data and facilitating the dual-review process (Human + AI).

### Components:

#### 1. Test Capture System
**What**: Automatically log test questions and responses
**How**: 
- Backend marks certain conversations as "test" vs "real usage"
- Stores in structured format (JSON or markdown)
- Includes timestamp, intent detected, context used

**Format**:
```json
{
  "test_id": "test_20251129_014500",
  "timestamp": "2025-11-29T01:45:00Z",
  "question": "What is the Constella framework?",
  "response": "The Constella framework! It's a remarkable...",
  "intent_detected": {
    "is_constella_query": true,
    "is_self_query": false
  },
  "context_used": ["constella_awareness", "constella_master_docs"],
  "human_rating": null,
  "ai_rating": null,
  "notes": null
}
```

#### 2. Dual Rating Interface
**What**: Streamlined way to get both human and AI ratings side-by-side
**How**:
- CLI tool or web interface
- Shows question + response
- Human rates first (0-5 stars + notes)
- AI analyzes and rates (with reasoning)
- Display both ratings with synthesis

**Workflow**:
```
1. Run: python review_tests.py
2. Shows unrated test Q&A
3. Jonathan rates: 4 stars, "Good but missed X"
4. AI rates: 3 stars, "Didn't cite decision Y"
5. Synthesis: 3.5 stars, both agree on gap
6. Saves to test results JSON
```

#### 3. Auto-Journal Generation
**What**: Automatically format test results into journal entries
**How**:
- Reads rated tests from JSON
- Generates formatted markdown
- Jonathan reviews/edits before committing
- Appends to resonance_journal.md

**Output Example**:
```markdown
### 📅 2025-11-29

**Evening Testing Session - Post-Task 2**

Tested 5 questions covering all integrations:

1. **"What is FAITHH?"** - ⭐⭐⭐⭐⭐
   - Jonathan: 5 stars - "Perfect self-description"
   - Claude: 5 stars - "Uses self_awareness section correctly"
   - Synthesis: 5 stars ✅

2. **"Why ChromaDB?"** - ⭐⭐⭐⭐
   - Jonathan: 4 stars - "Good but could cite alternatives better"
   - Claude: 4 stars - "Found decision but didn't detail rejected options"
   - Synthesis: 4 stars ✅

...

**Pattern Observed**: Self-awareness and orientation queries strong (5★), decision citations could be more explicit (4★).
```

#### 4. Test Pattern Analysis
**What**: Identify patterns across multiple test sessions
**How**:
- Aggregate ratings by question type (self-query, why-question, etc.)
- Track improvement over time
- Highlight recurring gaps
- Suggest areas for improvement

**Output Example**:
```
=== TEST PATTERN ANALYSIS ===
Sessions analyzed: 4
Total tests: 23

By Intent Type:
- Self-queries: 5.0★ average (6 tests)
- Why-questions: 4.2★ average (5 tests)
- Orientation: 5.0★ average (4 tests)
- Constella: 4.8★ average (5 tests)
- Synthesis: 3.5★ average (3 tests)

Top Gap: Synthesis questions still weak
Recommendation: Focus on Level 3 improvements
```

---

## Implementation Phases (Not Built Yet)

### Phase 1: Basic Test Capture (Minimal)
- Add `test_mode` flag to backend
- When enabled, log Q&A to `testing/test_log.json`
- Manual rating still via text file

### Phase 2: CLI Review Tool (Medium)
- Script to display unrated tests
- Interactive rating (human + AI)
- Saves results to JSON

### Phase 3: Auto-Journal (Medium)
- Generate journal entries from rated tests
- Jonathan reviews before committing
- Reduces manual typing

### Phase 4: Pattern Analysis (Advanced)
- Aggregate test data
- Identify trends
- Suggest priorities

---

## Notes for Future Implementation

### Integration Points:
- **Backend**: Add test mode flag, log to JSON
- **Review Script**: Python CLI using Gemini API for AI ratings
- **Journal Generator**: Template-based markdown generation
- **Analysis**: pandas for data aggregation

### Data Storage:
```
~/ai-stack/testing/
├── test_log.json           # Raw test Q&A
├── rated_tests.json        # Human + AI ratings
├── test_sessions/          # By-session archives
│   ├── 2025-11-29.json
│   └── 2025-11-30.json
└── analysis_cache.json     # Pattern analysis results
```

### Design Considerations:
- **Don't automate the rating** - Jonathan's judgment is the ground truth
- **Don't replace the journal** - It's valuable for reflection
- **Do reduce friction** - Fewer copy/paste steps
- **Do preserve data** - Structured storage enables analysis

---

## Relation to "Pair Human and AI Review System"

This testing system is a **subset** of a larger concept Jonathan has:

**Broader Vision**: A generalized system where human and AI review content together, with:
- Structured rating methodology
- Dual perspectives captured
- Synthesis/agreement tracking
- Pattern recognition across domains

**This FAITHH testing system** serves as a **proof-of-concept** for:
- Dual rating workflows
- Human/AI collaboration patterns
- Structured data capture for later analysis

**Future applications** could include:
- Code review (human + AI both rate pull requests)
- Content review (articles, docs, designs)
- Decision review (retrospectives on past choices)
- Creative review (music, art, writing)

The core pattern: **Human rates → AI analyzes → Compare → Learn from differences**

---

## Current Status: NOT IMPLEMENTED

This document captures the **vision and requirements** but the system is not built yet.

**To implement later**:
1. Review this document
2. Build Phase 1 (basic test capture)
3. Test with real usage
4. Iterate to Phase 2-4 based on what's actually useful

**Priority**: Low - current manual system works, this is optimization

**When to build**: After Layers 2-3 complete and real usage validates the approach

---

## Quick Reference: Current Manual Process

For now, continue with:

1. Test in FAITHH UI
2. Copy Q&A to text file with your rating
3. Paste to Claude for AI review
4. Manually update resonance_journal.md

This works. The automation is for when the volume gets too high or the manual process becomes a bottleneck.

---

**Document Purpose**: Capture requirements and vision so future implementation doesn't forget the context. NOT a task to do now.

---

*Last updated: 2025-11-29*

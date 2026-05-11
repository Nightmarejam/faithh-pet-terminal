# Automated Opus Review & Handoff System
**Created**: 2025-11-25  
**Purpose**: Automate periodic system reviews and handoffs to Claude Opus

---

## Overview

This document establishes when and how to escalate from Sonnet to Opus for strategic system reviews, architectural decisions, and complex planning.

---

## Automatic Handoff Triggers

### Time-Based Reviews (Every 2-3 Weeks)
**Trigger**: It's been 14-21 days since last Opus review  
**Action**: Generate comprehensive system audit for Opus

**Include in Handoff**:
- All changes made since last review
- Current system state (document count, services, issues)
- Open questions or problems
- Suggested next priorities

**Template**: Use `OPUS_REVIEW_TEMPLATE.md` (see below)

---

### Complexity-Based Escalation (Immediate)

**Escalate to Opus if you encounter**:

1. **Architectural Decisions**
   - "Should we split ChromaDB into domain collections?"
   - "How should we restructure the memory system?"
   - "What's the best approach for [major feature]?"

2. **Multi-System Changes**
   - Changes that affect 3+ components
   - Refactoring that spans multiple files
   - Breaking changes to APIs or interfaces

3. **Stuck Debugging** (>2 sessions)
   - Same bug for multiple conversations
   - Unclear root cause
   - Multiple attempted fixes failed

4. **Strategic Planning**
   - Roadmap for next 3-6 months
   - Feature prioritization
   - Resource allocation decisions

5. **Documentation Overhaul**
   - Need to reorganize scattered docs
   - Create master reference architecture
   - Establish new documentation standards

6. **Performance/Scale Issues**
   - System slowing down significantly
   - Memory/disk problems
   - Need optimization strategy

---

## How to Request Opus Review

### Step 1: Generate System State Report

Use this command to gather current system info:

```bash
cd ~/ai-stack
cat > opus_review_request.md << 'EOF'
# Opus Review Request
**Date**: $(date +%Y-%m-%d)
**Requested By**: Sonnet (via Jonathan)
**Last Opus Review**: [Date of last review, or "Never"]

## Current System State

### Services Status
$(curl -s http://localhost:5557/api/status | python3 -m json.tool)

### Recent Changes (Git)
$(git log --oneline --since="2 weeks ago" | head -20)

### Open Issues
[List any known problems, errors, or concerns]

### Questions for Opus
1. [Question 1]
2. [Question 2]
3. [Question 3]

### Suggested Focus Areas
- [Area 1]
- [Area 2]

## Request Type
[ ] Regular 2-3 week review
[ ] Architectural decision needed
[ ] Stuck on debugging
[ ] Strategic planning
[ ] Documentation overhaul
[ ] Performance issues

---
*Generated automatically - Ready for Opus review*
EOF

cat opus_review_request.md
```

### Step 2: Attach Context Documents

When handing off to Opus, attach these documents:
- `HANDOFF_COMPLETION_SUMMARY.md` (recent changes)
- `docs/HOW_IT_WORKS.md` (current system state)
- `docs/ARCHITECTURE.md` (authoritative architecture)
- `opus_review_request.md` (generated above)
- Any relevant error logs

### Step 3: State the Ask

Clearly state what you need from Opus:
- "Review system and identify issues"
- "Design approach for [feature]"
- "Debug this problem: [description]"
- "Create roadmap for next month"

---

## Opus Review Template

Save this as `~/ai-stack/OPUS_REVIEW_TEMPLATE.md`:

```markdown
# Opus System Review & Handoff
**Date**: [YYYY-MM-DD]
**Review Type**: [Regular/Architectural/Debugging/Strategic/Documentation/Performance]
**Requested By**: [Sonnet/Jonathan]

---

## Executive Summary
[2-3 sentence overview of system state and review purpose]

---

## System Health Check

### Services Status
- [ ] FAITHH Backend (port 5557) - [Status]
- [ ] ChromaDB (port 8000) - [Status, Document Count]
- [ ] Ollama (port 11434) - [Status, Models]
- [ ] Ollama-Embed (port 11435) - [Status]
- [ ] Ollama-Qwen (port 11436) - [Status]
- [ ] LangFlow (port 7860) - [Status]
- [ ] PostgreSQL - [Status]

### Recent Activity (Last 2 Weeks)
**Commits**:
[List git commits]

**Features Added**:
- [Feature 1]
- [Feature 2]

**Bugs Fixed**:
- [Bug 1]
- [Bug 2]

**Documentation Updated**:
- [Doc 1]
- [Doc 2]

### Current Issues
1. **[Issue Title]**
   - Severity: High/Medium/Low
   - Description: [Details]
   - Impact: [What it affects]
   - Attempted Fixes: [What's been tried]

### Performance Metrics
- ChromaDB document count: [Number]
- Backend response time: [Average]
- Memory usage: [Percentage]
- Disk usage: [Percentage]

---

## Architectural Review

### Current State
[Describe current architecture - reference ARCHITECTURE.md]

### Known Technical Debt
1. [Debt item 1]
2. [Debt item 2]

### Scalability Concerns
1. [Concern 1]
2. [Concern 2]

---

## Strategic Questions

### Immediate Decisions Needed
1. [Decision 1]
   - Context: [Background]
   - Options: [A, B, C]
   - Recommendation: [If any]

### Future Planning
1. [Feature/Project 1]
   - Priority: High/Medium/Low
   - Estimated Effort: [Hours/Days/Weeks]
   - Dependencies: [What's needed first]

---

## Documentation Status

### Up to Date
- [ ] HOW_IT_WORKS.md
- [ ] ARCHITECTURE.md
- [ ] Parity files (audio_workspace, network_infrastructure, dev_environment)
- [ ] README.md

### Needs Update
- [ ] [Doc 1]
- [ ] [Doc 2]

### Missing Documentation
- [ ] [What's needed]

---

## Handoff Tasks

### For Sonnet to Execute
After Opus review, these tasks should be handed back to Sonnet:
1. [Task 1] - Priority: [High/Medium/Low]
2. [Task 2] - Priority: [High/Medium/Low]

### Decisions Made (Do Not Revisit)
[Opus will fill this in during review]

### Questions Escalated Back to Jonathan
[Things that need human decision]

---

## Success Criteria

How will we know this review was successful?
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

---

**Next Review Date**: [2-3 weeks from today]  
**Review Status**: [ ] Pending [ ] In Progress [ ] Complete
```

---

## Handoff Workflow

```
┌─────────────────────────────────────────┐
│  Trigger Event (Time/Complexity/Stuck)  │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  Sonnet: Generate Review Request        │
│  - Run system state commands            │
│  - Gather recent changes                │
│  - List open issues                     │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  Jonathan: Attach Documents & Submit    │
│  - Upload review request                │
│  - Attach context docs                  │
│  - Start conversation with Opus         │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  Opus: Review & Plan                    │
│  - Analyze system state                 │
│  - Make architectural decisions         │
│  - Create task list for Sonnet          │
│  - Document decisions                   │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  Opus → Sonnet Handoff                  │
│  - Clear task list with priorities      │
│  - Decisions made (don't revisit)       │
│  - Success criteria                     │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  Sonnet: Execute Tasks                  │
│  - Follow Opus blueprint                │
│  - Document changes                     │
│  - Test thoroughly                      │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  Update Review Log & Set Next Date      │
└─────────────────────────────────────────┘
```

---

## Review Log

Keep track of Opus reviews in `~/ai-stack/OPUS_REVIEW_LOG.md`:

```markdown
# Opus Review History

## 2025-11-25 - Initial System Review & Auto-Index Fix
**Type**: Architectural  
**Focus**: Auto-index deadlock solution  
**Outcome**: Threading queue approach selected & implemented  
**Tasks Created**: 5 (all completed)  
**Next Review**: 2025-12-09 to 2025-12-16

## [Next Review Date]
**Type**: [Type]  
**Focus**: [Focus areas]  
**Outcome**: [What was decided]  
**Tasks Created**: [Number]  
**Next Review**: [Date]
```

---

## Requirements for Future Conversations

All future Claude conversations (Sonnet or Opus) should:

1. **Check Review Schedule**
   - Has it been 2-3 weeks since last Opus review?
   - If yes, suggest generating review request

2. **Recognize Complexity Triggers**
   - Detect when questions are architectural vs. execution
   - Suggest Opus handoff when appropriate

3. **Maintain Continuity**
   - Reference last Opus review decisions
   - Don't revisit already-decided architecture
   - Build on established patterns

4. **Document Everything**
   - Update relevant docs after changes
   - Keep handoff documents current
   - Maintain review log

---

## Quick Reference Commands

### Check if review is due:
```bash
# See when last Opus review happened
grep "Next Review" ~/ai-stack/OPUS_REVIEW_LOG.md | tail -1
```

### Generate review request:
```bash
cd ~/ai-stack
./generate_opus_review.sh  # (Create this script based on Step 1 above)
```

### Check system health:
```bash
curl -s http://localhost:5557/api/status | python3 -m json.tool
docker ps
git log --oneline --since="2 weeks ago"
```

---

## Automation Possibilities

### Future Enhancements:

1. **Cron Job for Reviews**
   - Auto-generate review request every 2 weeks
   - Email/notify Jonathan

2. **Health Check Monitor**
   - Script that checks all services
   - Logs metrics over time
   - Alerts if something fails

3. **Git Hook Integration**
   - After N commits, suggest review
   - After major file changes, flag for Opus

4. **FAITHH Self-Review**
   - FAITHH checks its own systems
   - Generates review requests
   - Identifies issues proactively

---

## Integration with FAITHH Memory

Future FAITHH versions should:
- Track time since last Opus review
- Automatically suggest review when due
- Pre-populate review request with system state
- Store Opus decisions in memory system

---

**Status**: Active  
**Last Updated**: 2025-11-25  
**Owner**: Jonathan + FAITHH team  
**Next Action**: Create first OPUS_REVIEW_LOG.md entry

---

*This document should be reviewed and updated after each Opus handoff cycle.*

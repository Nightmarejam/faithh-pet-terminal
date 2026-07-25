# Update Protocol

**Purpose:** Ensure continuity between sessions and maintain parity documentation for GPT/Claude context.

## End-of-Session Checklist

### 1. Update Core Documentation (Priority: HIGH)
- [ ] `MASTER_CONTEXT.md` - Overall system state
- [ ] `project_states.json` - Structured project status
- [ ] Create session report in `docs/session-reports/SESSION_YYYY-MM-DD_[topic].md`

### 2. Update Project-Specific Docs (if changed)
- [ ] `docs/PORTFOLIO_OVERVIEW.md` - If project scope/status changed
- [ ] `PHASE1_INTEGRATION_GUIDE.md` - If integration steps changed
- [ ] Any README files in affected projects

### 3. Verify File Parity
- [ ] Check for orphaned/duplicate files
- [ ] Ensure critical configs have backups (*.bak files noted in git)
- [ ] Verify symbolic links (if any) are valid

### 4. Git Operations
- [ ] Stage all relevant changes: `git add [files]`
- [ ] Commit with structured message (see conventions below)
- [ ] **DO NOT push** unless explicitly requested
- [ ] Verify git status shows clean working tree (or intentional uncommitted files)

### 5. Session Handoff
- [ ] Summarize what was accomplished
- [ ] Note any blockers or pending items
- [ ] List next recommended actions
- [ ] Highlight any new infrastructure/tools deployed

---

## File Locations Reference

### Core Context Files
```
~/ai-stack/
├── MASTER_CONTEXT.md                          # System overview
├── project_states.json                        # Structured status
├── PHASE1_INTEGRATION_GUIDE.md               # Integration steps
└── docs/
    ├── PORTFOLIO_OVERVIEW.md                 # Project portfolio
    ├── UPDATE_PROTOCOL.md                    # This file
    ├── GEN8_SETUP_CHECKLIST.md              # Server setup guide
    └── session-reports/
        └── SESSION_YYYY-MM-DD_topic.md       # Session logs
```

### Configuration Files
```
~/ai-stack/
├── configs/
│   ├── model_config.yaml                     # LLM model config
│   └── model_config.yaml.bak                 # Backup
├── backend/
│   ├── llm_providers.py                      # LLM abstraction layer
│   ├── coherence_sensor.py                   # Coherence detection
│   └── rag_processor.py                      # RAG indexing
└── .claude/
    └── settings.local.json                   # Claude Code settings
```

### Project-Specific
```
~/ai-stack/projects/
├── constella-framework/                      # Harmony framework
├── tomcat-sound/                            # Tom Cat Sound LLC
└── [other projects]/
```

---

## Git Commit Conventions

### Message Format
```
Session YYYY-MM-DD: [Primary accomplishment], [secondary items]

- Bullet list of specific changes
- Use present tense ("Add" not "Added")
- Be specific about what changed, not just "updates"
```

### Examples
**Good:**
```
Session 2025-12-20: Gen8 setup complete, Pi-hole running, update protocol created

- Set up Pi-hole on Gen8 server (servicebox)
- Create UPDATE_PROTOCOL.md for session handoff
- Update MASTER_CONTEXT.md with current infrastructure
- Add session report for Dec 20 work
```

**Bad:**
```
Updates

- Various changes
- Fixed stuff
```

### When to Commit
- End of logical work unit (feature complete, milestone reached)
- End of session (even if work incomplete - note in message)
- Before risky operations (pre-commit safety)
- After successful deployments/tests

### What NOT to Commit
- Secrets, API keys, passwords (use .env, never commit)
- Large binary files (unless essential)
- Temporary test files
- Personal notes meant to be ephemeral

---

## Session Handoff Template

Create `docs/session-reports/SESSION_YYYY-MM-DD_[topic].md`:

```markdown
# Session Report: YYYY-MM-DD - [Topic]

**AI Agent:** [Claude Code / GPT / Other]
**Duration:** [Approximate time]
**Primary Goal:** [What was the main objective?]

## Accomplishments
- [List completed items]
- [Include file paths for major changes]
- [Note any infrastructure deployed]

## Blockers / Issues
- [Any problems encountered]
- [Workarounds applied]
- [Known technical debt introduced]

## Files Changed
- `path/to/file1` - [What changed]
- `path/to/file2` - [What changed]

## Next Steps
1. [Highest priority next action]
2. [Follow-up tasks]
3. [Optional improvements]

## Context for Next Session
[Any important context that would be lost otherwise]
- [Decisions made and why]
- [Assumptions that informed the work]
- [Things that were tried but didn't work]

## Infrastructure State
- **Servers:** [Status of Gen8, any other servers]
- **Services:** [What's running - Pi-hole, ChromaDB, etc.]
- **RAG Status:** [Chunk count, index state, any re-index needed]
```

---

## Quick Reference Commands

### Check What Needs Updating
```bash
# See uncommitted changes
git status

# See recent work
git log --oneline -5

# Check for stale session reports
ls -lt docs/session-reports/ | head -10
```

### Update Core Files
```bash
# Edit master context
code MASTER_CONTEXT.md

# Update project states (JSON)
code project_states.json

# Create session report
code docs/session-reports/SESSION_$(date +%Y-%m-%d)_topic.md
```

### Commit Workflow
```bash
# Review changes
git diff
git status

# Stage selectively
git add [specific files]

# Commit with message
git commit -m "Session YYYY-MM-DD: [accomplishment]"

# Verify
git log -1 --stat
```

---

## Parity Principles

1. **Single Source of Truth:** MASTER_CONTEXT.md is authoritative for system state
2. **Structured Data:** project_states.json mirrors MASTER_CONTEXT in machine-readable format
3. **Session Continuity:** Session reports provide narrative history
4. **No Orphans:** Every significant file should be referenced somewhere
5. **Git as Memory:** Commits tell the story; messages should be clear

---

## Emergency Recovery

If you start a session and context is unclear:

1. Read `MASTER_CONTEXT.md` first
2. Check `project_states.json` for structured status
3. Review latest session report in `docs/session-reports/`
4. Check `git log -10` for recent activity
5. Run `git status` to see uncommitted work

If MASTER_CONTEXT is outdated:
1. Check session reports for latest truth
2. Reconstruct from git commits if needed
3. Update MASTER_CONTEXT before proceeding with new work

---

**Last Updated:** 2025-12-20
**Maintained By:** AI agents (Claude Code, GPT) + Jonathan

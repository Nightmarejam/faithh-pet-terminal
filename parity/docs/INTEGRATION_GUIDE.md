# Parity System Integration Guide

## How Parity Integrates with MASTER_ACTION

### Two Levels of Documentation

**1. MASTER_ACTION (High-Level)**
- Session-by-session progress
- What was accomplished
- Decisions made
- Status updates

**2. Parity Files (Detail-Level)**
- File-specific changes
- Technical details
- Code-level decisions
- Implementation notes

### The Relationship

```
MASTER_ACTION
    ↓
Says: "Updated backend to use .env"
    ↓
PARITY_backend.md
    ↓
Details: "Modified lines 47-48, added load_dotenv(), 
          removed hardcoded key, tested with .env file"
```

### When to Use Each

**MASTER_ACTION for:**
- Session summaries
- Overall progress tracking
- High-level decisions
- Continuity between sessions

**Parity Files for:**
- Technical implementation details
- Code-specific changes
- File-level documentation
- Developer reference

### Workflow

```
1. Script does work
2. Script updates parity file (technical details)
3. Script updates MASTER_ACTION (session summary)
4. Both stay in sync automatically!
```

### Example

**MASTER_ACTION Entry:**
```markdown
## Session 5
- Updated backend security
- Fixed configuration loading
```

**Parity File Entry:**
```markdown
### 2025-11-10 - Security Enhancement
- Added input validation on lines 150-165
- Implemented rate limiting middleware
- Updated JWT token expiration to 24h
Reason: Address security audit findings
```

### Benefits of Dual System

✅ **High-level** progress in MASTER_ACTION
✅ **Low-level** details in parity files  
✅ **Best of both worlds** - overview + depth
✅ **AI-friendly** - can read either level as needed

---

*Part of self-documenting automation system*

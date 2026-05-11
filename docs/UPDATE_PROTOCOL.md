# Documentation Update Protocol

## The Rule
At the end of any session that produces a meaningful result, update ONE document.
Not a sprint. Not a ceremony. One file, committed.

## What Counts as "Meaningful Result"
- Experiment completed or failed with findings
- New service deployed or configured
- Bug fixed that changes system behavior  
- New model or provider added
- Architecture decision made
- RAG system improvements
- Infrastructure changes
- Major debugging sessions

## Which Document to Update
| Result type | Document to update |
|---|---|
| ALIFE experiment | project_states.json + alife section |
| Infrastructure change | MASTER_CONTEXT.md services section |
| New provider/model | MASTER_CONTEXT.md providers section |
| Business decision | projects/tomcat-sound/ relevant doc |
| Architecture decision | decisions_log.json |
| Major session summary | docs/session-reports/ |
| RAG improvements | MASTER_CONTEXT.md RAG section |
| Bug fixes | MASTER_CONTEXT.md recent changes |
| Documentation audit | MASTER_CONTEXT.md |

## Minimum Viable Update
A one-line entry in the right section is better than no update.
Don't let perfect be the enemy of done.

Examples:
- "Fixed RAG context usage in qwen25-grounded model"
- "Added ALIFE Experiment 3 findings to project_states.json"
- "Updated ChromaDB document count to 36,723"
- "Configured Google Custom Search API"

## Stale Document Detection
PULSE runs staleness checks. Any document not updated in 30+ days 
gets flagged. The flag is informational, not blocking.

## Update Process

### Step 1: Identify the Document
Use the table above or choose the most relevant document.

### Step 2: Make the Update
- Add new information
- Update counts/numbers
- Fix outdated information
- Add recent changes

### Step 3: Commit
```bash
git add <document>
git commit -m "docs: update <document> with <brief description>"
```

### Step 4: Verify
```bash
git log --oneline -1  # Should show your commit
```

## Quality Guidelines

### DO
- Be accurate and factual
- Include specific numbers/dates when possible
- Keep updates concise
- Use present tense for current status
- Reference related documents when helpful

### DON'T
- Invent information
- Make updates overly verbose
- Update multiple documents in one commit (unless necessary)
- Forget to commit the changes

## Examples

### Good Updates
```markdown
## RAG System Status
### Current State (as of March 2026)
- Total chunks: 36,723 documents (updated from 32,499)
- Conversations: 285+ indexed
- RAG context usage: Fixed - models now properly use retrieved context
```

```json
{
  "key_findings": [
    "Experiment 3: FULL_SUCCESS — anticipatory behavior emerged at tick 402"
  ]
}
```

### Minimal Updates
```markdown
- Fixed RAG context usage (March 25, 2026)
```

```json
{
  "status": "active",
  "phase": "Experiment 4 in progress"
}
```

## When in Doubt

If you're unsure which document to update:
1. Ask: "What would someone reading this need to know?"
2. Choose the document that answers that question
3. Make the smallest meaningful update

## Automation

The system tracks:
- Document modification times
- Git commit history
- PULSE staleness flags

Use these signals to identify documents needing attention.

---

*This protocol ensures documentation stays current without becoming a burden. One meaningful update per session keeps the knowledge base accurate and useful.*

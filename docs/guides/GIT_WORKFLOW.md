# Git Workflow Guide for FAITHH
**A Beginner-Friendly Guide to Version Control**

**Last Updated:** 2026-01-25  
**For:** Jonathan (new to programming)  
**Purpose:** Establish disciplined Git practices for FAITHH development

---

## Why Git Matters

Git helps you:
- **Track changes** - See what changed, when, and why
- **Undo mistakes** - Roll back to working versions
- **Collaborate** - Work with AI assistants and future contributors
- **Document progress** - Your commit history tells a story

---

## Daily Git Workflow

### Morning: Start Your Session

```bash
# 1. Navigate to project
cd ~/ai-stack

# 2. Check current status
git status

# 3. Pull latest changes (if working across devices)
git pull

# 4. Create a new branch for today's work (optional but recommended)
git checkout -b session-$(date +%Y-%m-%d)
```

### During Work: Save Progress Frequently

```bash
# Check what you've changed
git status

# See detailed changes
git diff

# Add specific files
git add faithh_professional_backend_fixed.py
git add docs/NEW_DOCUMENT.md

# Or add all changes (use carefully)
git add -A

# Commit with descriptive message
git commit -m "Add RAG query caching to improve performance"
```

### Evening: End Your Session

```bash
# 1. Review all changes
git status
git diff

# 2. Stage and commit final changes
git add -A
git commit -m "Session 2026-01-25: RAG reindex, cleanup, testing complete"

# 3. Push to GitHub
git push origin main

# 4. Optional: Merge session branch back to main
git checkout main
git merge session-2026-01-25
git push origin main
```

---

## Commit Message Best Practices

### Format
```
<type>: <short description>

<optional detailed explanation>
<optional bullet points of changes>
```

### Types
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code restructuring (no behavior change)
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks (cleanup, dependencies)
- `session:` - End-of-session summary commit

### Examples

**Good:**
```bash
git commit -m "feat: Add ChromaDB connection pooling for better performance"

git commit -m "fix: Resolve RAG hallucination by improving chunk overlap

- Increased chunk overlap from 100 to 200 chars
- Updated embedding model to all-MiniLM-L6-v2  *(historical entry; the KB embedder is now BAAI/bge-base-en-v1.5, 768-dim)*
- Reindexed 32,499 chunks with proper metadata"

git commit -m "docs: Create comprehensive FAITHH_GUIDE.md as single source of truth"

git commit -m "chore: Archive duplicate frontend files and old cleanup scripts"
```

**Bad:**
```bash
git commit -m "stuff"
git commit -m "fixed it"
git commit -m "updates"
git commit -m "asdfasdf"
```

---

## FAITHH-Specific Workflow

### Scenario 1: Adding New Feature

```bash
# 1. Create feature branch
git checkout -b feature/rag-caching

# 2. Make changes
# ... edit files ...

# 3. Test thoroughly
./restart_backend.sh
# ... test in UI ...

# 4. Commit
git add backend/rag_processor.py
git commit -m "feat: Add LRU cache for RAG queries

- Implemented 100-item cache with TTL
- Reduces ChromaDB calls by ~60%
- Added cache stats to /api/status endpoint"

# 5. Merge to main
git checkout main
git merge feature/rag-caching
git push origin main

# 6. Delete feature branch
git branch -d feature/rag-caching
```

### Scenario 2: Fixing Bug

```bash
# 1. Create fix branch
git checkout -b fix/streaming-timeout

# 2. Make fix
# ... edit faithh_professional_backend_fixed.py ...

# 3. Test fix
./restart_backend.sh
# ... verify bug is fixed ...

# 4. Commit with clear description
git add faithh_professional_backend_fixed.py
git commit -m "fix: Increase streaming timeout from 30s to 60s

Resolves issue where long responses were being cut off.
Updated OLLAMA_READ_TIMEOUT in .env.example as well."

# 5. Merge and push
git checkout main
git merge fix/streaming-timeout
git push origin main
```

### Scenario 3: Documentation Update

```bash
# Simple docs don't need a branch
git add docs/FAITHH_GUIDE.md
git commit -m "docs: Add troubleshooting section for ChromaDB connection issues"
git push origin main
```

### Scenario 4: End of Session

```bash
# Review everything you did today
git log --oneline --since="1 day ago"

# Create summary commit if needed
git add -A
git commit -m "session: 2026-01-25 - RAG reindex and project cleanup

Completed:
- Reindexed ChromaDB with proper chunking (32,499 chunks)
- Created FAITHH_GUIDE.md as single source of truth
- Archived duplicate files and old scripts
- Updated project_states.json and MASTER_CONTEXT.md
- Ran comprehensive system tests

Next session:
- Review test results
- Implement any needed fixes
- Continue with Phase 3 features"

git push origin main
```

---

## Useful Git Commands

### Checking Status

```bash
# See what's changed
git status

# See detailed changes
git diff

# See changes in specific file
git diff faithh_pet_v4.html

# See commit history
git log --oneline -10

# See detailed commit history
git log --stat -5
```

### Undoing Changes

```bash
# Undo changes to a file (before staging)
git checkout -- faithh_pet_v4.html

# Unstage a file (keep changes)
git reset HEAD faithh_pet_v4.html

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes) - DANGEROUS
git reset --hard HEAD~1

# Revert a specific commit (creates new commit)
git revert abc123
```

### Branching

```bash
# List branches
git branch

# Create new branch
git branch feature/new-thing

# Switch to branch
git checkout feature/new-thing

# Create and switch in one command
git checkout -b feature/new-thing

# Delete branch
git branch -d feature/new-thing

# Force delete unmerged branch
git branch -D feature/new-thing
```

### Remote Operations

```bash
# See remote repositories
git remote -v

# Pull latest changes
git pull origin main

# Push changes
git push origin main

# Push new branch
git push -u origin feature/new-thing

# Fetch without merging
git fetch origin
```

---

## FAITHH Project Standards

### Files to Always Commit
- ✅ Code changes (`*.py`, `*.html`, `*.js`)
- ✅ Documentation (`*.md`)
- ✅ Configuration (`config.yaml`, `docker-compose.yml`)
- ✅ Requirements (`requirements.txt`)
- ✅ State files (`project_states.json`, `decisions_log.json`)

### Files to NEVER Commit
- ❌ `.env` (contains API keys)
- ❌ `venv/` (virtual environment)
- ❌ `__pycache__/` (Python cache)
- ❌ `*.log` (log files)
- ❌ `backend.log`, `api.log`
- ❌ `chroma_db/` (database files)
- ❌ Personal API keys or credentials

**Note:** These are already in `.gitignore`

### When to Commit

**Commit frequently when:**
- ✅ You complete a logical unit of work
- ✅ Tests pass
- ✅ Before trying something risky
- ✅ End of work session
- ✅ Before switching tasks

**Don't commit when:**
- ❌ Code doesn't run
- ❌ Tests are failing
- ❌ In the middle of refactoring
- ❌ You're not sure what you changed

---

## Common Scenarios

### "I made a mistake in my last commit"

```bash
# If you haven't pushed yet
git commit --amend -m "Corrected commit message"

# If you already pushed (creates new commit)
git revert HEAD
git push origin main
```

### "I want to see what changed in the last week"

```bash
git log --since="1 week ago" --oneline
git log --since="1 week ago" --stat
```

### "I want to undo all my changes and start fresh"

```bash
# DANGEROUS - this discards all uncommitted changes
git reset --hard HEAD
git clean -fd
```

### "I accidentally committed a file with secrets"

```bash
# Remove from last commit (if not pushed)
git reset --soft HEAD~1
git reset HEAD .env
git commit -m "Your commit message"

# If already pushed - you need to rotate the secrets!
# Then remove from history (advanced)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```

### "I want to work on two things at once"

```bash
# Save current work
git stash

# Switch to other task
git checkout other-branch
# ... do work ...
git commit -m "Other task done"

# Go back to original work
git checkout main
git stash pop
```

---

## Integration with FAITHH Workflow

### Before Starting Work

```bash
cd ~/ai-stack
git status                    # Check for uncommitted changes
git pull                      # Get latest from GitHub
source venv/bin/activate      # Activate Python environment
./restart_backend.sh          # Start FAITHH
```

### During Development

```bash
# Make changes
# Test changes
# Commit when working
git add <files>
git commit -m "descriptive message"
```

### After Testing

```bash
# Run tests
python -m pytest tests/

# If tests pass, commit
git add -A
git commit -m "test: All tests passing after RAG reindex"
git push origin main
```

### End of Session

```bash
./stop_backend.sh             # Stop FAITHH
git status                    # Check for uncommitted work
git add -A                    # Stage everything
git commit -m "session: Summary of today's work"
git push origin main          # Push to GitHub
```

---

## GitHub Integration

### Setting Up GitHub (First Time)

```bash
# Configure Git
git config --global user.name "Jonathan"
git config --global user.email "your-email@example.com"

# Check current remote
git remote -v

# Should show:
# origin  https://github.com/Nightmarejam/faithh-pet-terminal.git (fetch)
# origin  https://github.com/Nightmarejam/faithh-pet-terminal.git (push)
```

### Pushing to GitHub

```bash
# First time (if not set up)
git remote add origin https://github.com/Nightmarejam/faithh-pet-terminal.git

# Every time
git push origin main
```

### Pulling from GitHub

```bash
# Get latest changes
git pull origin main

# If there are conflicts, Git will tell you
# Edit conflicted files, then:
git add <conflicted-files>
git commit -m "Resolve merge conflicts"
```

---

## Quick Reference Card

```bash
# Daily Commands
git status                    # What changed?
git add <file>               # Stage file
git add -A                   # Stage everything
git commit -m "message"      # Save changes
git push origin main         # Upload to GitHub
git pull origin main         # Download from GitHub

# Branching
git checkout -b new-branch   # Create and switch
git checkout main            # Switch to main
git merge feature-branch     # Merge branch
git branch -d old-branch     # Delete branch

# Undoing
git checkout -- <file>       # Undo file changes
git reset HEAD <file>        # Unstage file
git reset --soft HEAD~1      # Undo last commit

# Viewing
git log --oneline -10        # Recent commits
git diff                     # See changes
git status                   # Current state
```

---

## Learning Resources

### For Beginners
- **Git Basics:** https://git-scm.com/book/en/v2/Getting-Started-Git-Basics
- **Interactive Tutorial:** https://learngitbranching.js.org/
- **Cheat Sheet:** https://education.github.com/git-cheat-sheet-education.pdf

### For FAITHH Development
- This guide (you're reading it!)
- `GIT_COMMIT_INSTRUCTIONS.md` (existing guide)
- Ask FAITHH for help with Git commands

---

## Troubleshooting

### "I don't know what I changed"

```bash
git status        # See modified files
git diff          # See actual changes
```

### "I can't push to GitHub"

```bash
# Pull first (might have conflicts)
git pull origin main

# Then push
git push origin main
```

### "I have merge conflicts"

```bash
# Git will mark conflicts in files like:
# <<<<<<< HEAD
# Your changes
# =======
# Their changes
# >>>>>>> branch-name

# Edit the file, remove markers, keep what you want
# Then:
git add <conflicted-file>
git commit -m "Resolve merge conflict"
```

### "I committed to the wrong branch"

```bash
# Move commit to correct branch
git checkout correct-branch
git cherry-pick abc123  # Use commit hash from git log

# Remove from wrong branch
git checkout wrong-branch
git reset --hard HEAD~1
```

---

## FAITHH-Specific Commit Templates

### Feature Addition
```bash
git commit -m "feat: Add <feature-name>

- Implemented <specific-change>
- Updated <affected-files>
- Tested with <test-description>

Closes #<issue-number> (if applicable)"
```

### Bug Fix
```bash
git commit -m "fix: Resolve <bug-description>

Issue: <what-was-broken>
Solution: <how-you-fixed-it>
Tested: <verification-steps>"
```

### Documentation
```bash
git commit -m "docs: Update <document-name>

- Added <new-section>
- Clarified <existing-section>
- Fixed typos in <location>"
```

### Session Summary
```bash
git commit -m "session: YYYY-MM-DD - <main-accomplishment>

Completed:
- <task-1>
- <task-2>
- <task-3>

Next session:
- <planned-task-1>
- <planned-task-2>"
```

---

## Best Practices Summary

1. **Commit often** - Small, focused commits are better than large ones
2. **Write clear messages** - Your future self will thank you
3. **Test before committing** - Don't commit broken code
4. **Pull before pushing** - Avoid conflicts
5. **Use branches for experiments** - Keep main stable
6. **Never commit secrets** - Use `.env` for API keys
7. **Review before committing** - Use `git diff` and `git status`
8. **Push daily** - Backup your work to GitHub

---

**Remember:** Git is a safety net, not a burden. It helps you work confidently knowing you can always undo mistakes.

**Next Steps:**
1. Practice these commands daily
2. Build the habit of committing frequently
3. Review your commit history weekly
4. Ask FAITHH for help when stuck!

---

**Last Updated:** 2026-01-25  
**Maintained by:** Jonathan  
**Integrated with:** FAITHH_GUIDE.md


---

# Git Commit Instructions - December 2025 Session

## Files Modified/Created This Session

### Core State Files:
- `resonance_journal.md` - Updated with Dec 4-7 entries
- `project_states.json` - Updated with current state
- `parity/dev_environment.md` - Complete hardware specs

### Handoff Documentation:
- `parity/COMPREHENSIVE_HANDOFF_2025-12.md` - Master handoff document

## Git Commands to Run

```bash
# Navigate to repo
cd ~/ai-stack

# Check status
git status

# Add all changes
git add -A

# Commit with descriptive message
git commit -m "Dec 2025: FAITHH Lite, NAS reorg, Tailscale network, comprehensive docs

Major accomplishments:
- MacBook FAITHH Lite fully operational (~2s response)
- NAS reorganized (3.6TB, 794GB freed)
- Tailscale network connecting Windows/Mac/Phone/NAS
- Hardware ecosystem documented (6 devices)
- Media server plan in ideas vault

Files updated:
- resonance_journal.md (Dec 4-7 entries)
- project_states.json (v1.1, infrastructure focus)
- parity/dev_environment.md (verified specs)
- parity/COMPREHENSIVE_HANDOFF_2025-12.md (master handoff)

System status:
- FAITHH Windows: 93,629 docs, 4.5★+ avg
- FAITHH Lite: Operational, 3 context files
- Tailscale: 4 devices connected
- NAS: 23% used, production-ready"

# Push to remote
git push origin main
```

## Verification After Commit

```bash
# Verify commit
git log -1 --oneline

# Verify push
git status
```

## Notes

- All critical documentation is in place
- Handoff document enables any AI to resume
- Free tier + FAITHH strategy documented
- Next priorities: FGS income, daily FAITHH usage

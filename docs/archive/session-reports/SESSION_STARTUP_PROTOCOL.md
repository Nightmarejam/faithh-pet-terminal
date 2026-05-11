# SESSION STARTUP PROTOCOL
**How to Start Each Work Session Efficiently**

---

## 🚀 QUICK START (30 seconds)

### Option A: Upload MASTER_ACTION File (BEST)
```
1. Start new conversation with Claude
2. Upload: MASTER_ACTION_FAITHH.md
3. Say: "Let's continue [day] tasks"
4. Claude reads file and knows exactly where you are!
```

### Option B: Quick Status Update
```
1. Start conversation
2. Say: "Working on Week 1 [Day]. Last session we [brief summary]"
3. Claude asks for specific files if needed
```

### Option C: Emergency Quick Start
```
1. Say: "Week 1 [Day] - what should I do?"
2. Claude will guide you and ask for files as needed
```

---

## 📁 KEY FILES TO HAVE READY

### Essential Files (Upload at session start):
1. **MASTER_ACTION_FAITHH.md** - Your project log (MOST IMPORTANT)
2. **WEEK1_CHECKLIST.md** - Your current week's tasks

### Optional Files (Upload if Claude asks):
3. **MASTER_CONTEXT.md** - Full project context
4. **[Day]_COMPLETION_SUMMARY.md** - Previous day's summary

### Never Upload (Too big/not needed):
- Code files (unless debugging specific issue)
- Log files (unless troubleshooting)
- Data files

---

## 🎬 SESSION STARTUP TEMPLATE

Copy/paste this at the start of each session:

```
Hi Claude! Continuing FAITHH project.

Week: 1
Day: [Monday/Tuesday/Wednesday/etc]
Last completed: [Brief - e.g., "Monday - setup .env and organized files"]

Uploading MASTER_ACTION_FAITHH.md for context.

Ready to work on [today's focus]!
```

Then upload the MASTER_ACTION file.

---

## 💡 WHY THIS WORKS

**The MASTER_ACTION file contains:**
- ✅ Complete session history
- ✅ What was accomplished each day
- ✅ Decisions made
- ✅ Current status
- ✅ Next priorities

**When you upload it, Claude can:**
- ✅ Read entire project history instantly
- ✅ Know exactly where you left off
- ✅ Understand decisions already made
- ✅ Continue without repetition
- ✅ Reference specific past sessions

---

## 🔄 FILE UPDATE PATTERN

**CRITICAL:** Files don't auto-update! You must update them!

### At END of each session:
```bash
# Update MASTER_ACTION with today's work
nano MASTER_ACTION_FAITHH.md

# Add a new session entry:
## Session [N] - [Date] - [Day of Week]
**Focus:** [What we worked on]
**Completed:** [What got done]
**Decisions:** [Key decisions made]
**Next:** [What's next]
```

### At START of next session:
```
# Upload the updated file to Claude
```

**This creates perfect continuity!**

---

## 🎯 EXAMPLE WORKFLOW

### Monday Evening (Session End):
```bash
cd ~/ai-stack
nano MASTER_ACTION_FAITHH.md

# Add Session 2 entry:
## Session 2 - 2025-11-08 - Monday
**Focus:** Week 1 Monday - Environment setup
**Completed:**
- Created .env file with API key
- Set up .gitignore
- Updated backend to use .env
- Deleted old faithh/ folder
- Created all Monday documentation

**Decisions:**
- Use .env pattern for all config
- Keep ComfyUI and Stable Diffusion
- faithh_professional_backend.py is active backend

**Status:** ✅ Monday 100% complete
**Next:** Tuesday - File organization and doc consolidation
```

### Tuesday Morning (Session Start):
```
New conversation with Claude:

"Hi Claude! Week 1 Tuesday - file organization day.
Monday we set up .env and secured config.
Uploading MASTER_ACTION_FAITHH.md for full context."

[Upload file]
```

Claude reads it and says:
"Perfect! I can see Monday is complete. Ready for Tuesday's file organization tasks..."

---

## 🚫 COMMON MISTAKES TO AVOID

### ❌ DON'T:
- Start with "Remember last time..." (Claude can't remember)
- Upload code files first (context docs are better)
- Try to explain everything verbally (upload MASTER_ACTION instead)
- Forget to update MASTER_ACTION at session end
- Upload every single file (just the key ones)

### ✅ DO:
- Update MASTER_ACTION after each session
- Upload MASTER_ACTION at session start
- Include brief status in your first message
- Reference specific session numbers when discussing past work
- Keep MASTER_ACTION concise but complete

---

## 🔧 DESKTOP COMMANDER & FILES

**Question:** "Should I use Desktop Commander to read files?"

**Answer:** 
- I **cannot** directly access your WSL filesystem (different environments)
- **Solution:** You upload files to me, or paste relevant sections
- **Best practice:** Upload MASTER_ACTION at start, other files only if needed

**Question:** "Is it updating from what we did?"

**Answer:**
- Files **do NOT** auto-update
- **You** must update them at session end
- Then upload updated version at next session start
- This manual step ensures you review/approve changes

---

## 📊 CONTINUITY CHECKLIST

Before ending each session:
- [ ] Updated MASTER_ACTION_FAITHH.md with today's work
- [ ] Saved all important decisions
- [ ] Noted what's next
- [ ] Created completion summary (if end of day)
- [ ] Git committed important changes (optional)

Before starting next session:
- [ ] Know which day you're working on
- [ ] Have MASTER_ACTION_FAITHH.md ready to upload
- [ ] Brief idea of today's focus
- [ ] Ready to work!

---

## 🎯 SPECIAL CASES

### If you skip days:
```
"Hi Claude, it's been a week since my last session.
Week 1 Tuesday - file organization.
Uploading MASTER_ACTION to catch you up."
```

### If something broke:
```
"Hi Claude, Week 1 Tuesday but we have an issue.
[Brief description of problem]
Uploading MASTER_ACTION + error logs."
```

### If changing focus:
```
"Hi Claude, changing plans from Week 1 schedule.
Want to focus on [different priority].
Uploading MASTER_ACTION for context."
```

---

## 💡 PRO TIPS

### Tip 1: Session Numbers
Keep incrementing session numbers in MASTER_ACTION. Makes it easy to reference:
"In Session 2 we decided..." vs "Last Monday we..."

### Tip 2: Quick Updates
Don't need to write essay. Brief bullets work:
```
## Session 3 - Tuesday
- Moved files to folders
- Consolidated docs
- Tested system
Next: Wednesday - parity setup
```

### Tip 3: Multiple Sessions Per Day
If you work multiple times in one day:
```
## Session 3a - Tuesday Morning
[work done]

## Session 3b - Tuesday Evening  
[more work done]
```

### Tip 4: Keep Backups
```bash
cp MASTER_ACTION_FAITHH.md MASTER_ACTION_FAITHH.md.backup
```

---

## 🎬 READY TO USE RIGHT NOW

**For TODAY (Tuesday):**

1. Update MASTER_ACTION with Monday's work (I'll help you)
2. Then we start Tuesday tasks
3. At end of Tuesday, update MASTER_ACTION again
4. Wednesday morning, upload updated file

**This pattern works for the entire 2-month project!**

---

## 📝 TEMPLATE FOR MASTER_ACTION UPDATES

```markdown
## Session [N] - [YYYY-MM-DD] - [Day of Week]
**Week:** [Week number, Day]
**Focus:** [Main goal for this session]

**Completed:**
- [Task 1]
- [Task 2]
- [Task 3]

**Decisions Made:**
- [Decision 1]
- [Decision 2]

**Issues Encountered:**
- [Issue 1 and how resolved]

**Status:** [✅ Complete / ⏳ In Progress / ⚠️ Blocked]

**Next Session:**
- [Priority 1]
- [Priority 2]
- [Priority 3]

**Time Spent:** ~[hours]
```

---

**Ready to use this system? Let's update MASTER_ACTION with Monday's work, then start Tuesday!**

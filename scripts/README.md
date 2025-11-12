# Monday Scripts - Quick Reference

## 🚀 Easy Mode: Run Everything

```bash
cd ~/ai-stack
chmod +x run_monday_tasks.sh
./run_monday_tasks.sh
```

This runs all three scripts in sequence with pauses between phases.

---

## 📋 Individual Scripts

### 1. monday_completion.sh
**What it does:**
- Creates .env file (if needed)
- Sets up .gitignore
- Backs up backend
- Analyzes configuration
- Documents home directory decisions
- Creates completion report

**Run it:**
```bash
./monday_completion.sh
```

**Time:** ~2 minutes

---

### 2. update_backend_to_env.sh
**What it does:**
- Installs python-dotenv (if needed)
- Updates faithh_professional_backend.py to use .env
- Removes hardcoded API keys
- Creates backup before changes
- Tests that .env loads correctly

**Run it:**
```bash
./update_backend_to_env.sh
```

**Time:** ~1 minute

**⚠️ Important:** You'll need to restart your backend after running this!

---

### 3. final_monday_cleanup.sh
**What it does:**
- Removes old ~/faithh folder (with confirmation)
- Documents home directory structure
- Creates comprehensive Monday summary
- Final status report

**Run it:**
```bash
./final_monday_cleanup.sh
```

**Time:** ~1 minute

---

## 🎯 Recommended Workflow

### Option A: All at Once (Easiest)
```bash
./run_monday_tasks.sh
```
Runs everything with pauses for review.

### Option B: Step by Step
```bash
# 1. Initial setup
./monday_completion.sh
cat MONDAY_COMPLETION_REPORT.md

# 2. Update backend (optional but recommended)
./update_backend_to_env.sh

# 3. Final cleanup
./final_monday_cleanup.sh
cat MONDAY_COMPLETE_SUMMARY.md
```

### Option C: Manual (Pick and Choose)
Run only the scripts you need. They're independent.

---

## 📝 What Gets Created

### Configuration Files
- `.env` - Environment variables
- `.gitignore` - Git ignore rules

### Documentation
- `ACTIVE_BACKEND_INFO.md` - Backend docs
- `HOME_DIRECTORY_DECISIONS.md` - Directory structure
- `MONDAY_COMPLETION_REPORT.md` - Detailed report
- `MONDAY_COMPLETE_SUMMARY.md` - Summary (read this!)

### Backups
- `faithh_professional_backend.py.backup` - Original backend
- `faithh_professional_backend.py.original` - Another backup
- `backups/[timestamp]/` - Timestamped backup folder

---

## ⚠️ Important Notes

### Before Running Scripts:
1. **Close your UI** (or at least note you'll need to test after)
2. **Note which terminal has your backend running**
3. **You'll need to restart backend** after update_backend_to_env.sh

### After Running Scripts:
1. **Read MONDAY_COMPLETE_SUMMARY.md** - Most important!
2. **Verify .env has your API key**
3. **Restart backend** if you ran the update script
4. **Test your UI** to make sure everything works

### If Something Breaks:
1. **Don't panic!** Backups exist
2. **Restore from backup:**
   ```bash
   cp faithh_professional_backend.py.backup faithh_professional_backend.py
   ```
3. **Ask Claude** - Share the error message

---

## 🔍 Verification Commands

### Check .env exists and has API key:
```bash
ls -la .env
cat .env | grep GEMINI_API_KEY
```

### Check backend was updated:
```bash
grep "load_dotenv" faithh_professional_backend.py
grep "os.getenv" faithh_professional_backend.py
```

### Check what was created:
```bash
ls -lah MONDAY_*.md
ls -lah *.md | head -20
```

---

## 🎯 Success Criteria

After running all scripts, you should have:

- [x] .env file with API key
- [x] .gitignore protecting .env
- [x] Backend using .env (not hardcoded)
- [x] Home directory decisions made
- [x] Comprehensive documentation created
- [x] Backups of important files
- [x] Monday checklist completed

---

## 💡 Tips

1. **Run in order** - Scripts are designed to run in sequence
2. **Read the output** - Scripts explain what they're doing
3. **Keep backups** - Don't delete the .backup files yet
4. **Test immediately** - After scripts, test your UI
5. **Git commit** - Once everything works, commit changes

---

## 🆘 Help

**Script won't run:**
```bash
chmod +x script_name.sh
```

**Script errors out:**
- Read the error message
- Check you're in ~/ai-stack directory
- Share error with Claude

**Not sure which to run:**
- Start with: `./run_monday_tasks.sh`
- It guides you through everything

---

## 📅 What's Next?

After Monday complete:
1. Rest! You did great work
2. Tuesday: File organization (2-3 hours)
3. Review WEEK1_CHECKLIST.md for Tuesday tasks

---

**Questions? Run a script and see what happens!**  
**Everything is backed up, so it's safe to experiment.**

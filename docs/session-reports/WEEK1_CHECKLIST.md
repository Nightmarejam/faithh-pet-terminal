# WEEK 1 QUICK CHECKLIST ✓

Print this or keep it open while working!

---

## MONDAY - Discovery (2-3 hrs)
- [ ] Run `./quick_scan.sh` in /home/jonat/ai-stack
- [ ] Upload output to Claude
- [ ] Find Gemini API key location (or confirm Ollama)
- [ ] List folders that might need moving
- [ ] Decide: Gemini or Ollama primary?

**End goal:** Know what you have

---

## TUESDAY - Organization (2-3 hrs)  
- [ ] Create new directory structure
- [ ] Classify files (keep/archive/delete)
- [ ] Move files to new locations
- [ ] Test that system still works
- [ ] Update any broken paths

**End goal:** Everything in its place

---

## WEDNESDAY - Configuration (2-3 hrs)
- [ ] Fix/verify Gemini API setup
- [ ] Update .env and config.yaml
- [ ] Test all connections work
- [ ] Verify model switching
- [ ] Create config backups

**End goal:** API working, configs clean

---

## THURSDAY - Documentation (2-3 hrs)
- [ ] Update MASTER_CONTEXT.md
- [ ] Update MASTER_ACTION.md  
- [ ] Create/update README.md
- [ ] Create first parity file
- [ ] Archive old documentation

**End goal:** Docs current and organized

---

## FRIDAY - Testing (2-3 hrs)
- [ ] Full system test (UI, chat, RAG)
- [ ] Performance check
- [ ] Create TEST_LOG.md
- [ ] Plan Week 2 with Claude
- [ ] Create WEEK1_COMPLETION.md

**End goal:** Stable system, ready for Week 2

---

## DAILY HABITS
- [ ] Git commit before big changes
- [ ] Update MASTER_ACTION after work
- [ ] Note time spent
- [ ] Ask Claude when stuck

---

## WEEK 1 SUCCESS = ALL OF THESE:
- [ ] Clean directory structure
- [ ] Know where all files are
- [ ] API working (Gemini or Ollama)
- [ ] Documentation updated
- [ ] System stable and tested
- [ ] Parity structure created
- [ ] Ready for Week 2 features

---

**Total Time: 12-15 hours across 5 days**  
**Pace: 2-3 hours per day (flexible)**

---

## QUICK COMMANDS

**Start system:**
```bash
cd /home/jonat/ai-stack
python backend/faithh_enhanced_backend.py
```

**Check status:**
```bash
docker ps
curl http://localhost:5557/health
```

**Discovery scan:**
```bash
./quick_scan.sh
```

**Backup config:**
```bash
cp .env .env.backup_$(date +%Y%m%d)
```

---

## WHEN STUCK
1. Check TEST_LOG.md for known issues
2. Ask Claude with error message  
3. Take a break
4. Git commit current state
5. Try again tomorrow

---

**Remember: Progress over perfection!**  
**Even 30 min of work is valuable.**

✨ You got this! ✨

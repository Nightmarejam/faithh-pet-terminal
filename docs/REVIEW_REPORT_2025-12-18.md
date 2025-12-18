# Project Review Report - ai-stack
**Generated:** 2025-12-18 03:15 PST
**Scope:** Repository-wide health check and cleanup recommendations
**Purpose:** Identify stale files, redundancies, documentation gaps, and maintenance needs

---

## Executive Summary

### ✅ Health Status: GOOD
- **Phase 2 Complete:** Multi-provider routing, doc-grounding, provider badges all operational
- **Active Development:** Recent commits and file modifications show active work
- **Config Consistency:** `model_config.yaml` correctly configured with `qwen/qwen3-32b`
- **Documentation:** Comprehensive but contains legacy/archive content

### ⚠️ Attention Areas
1. **53,364 files** older than 30 days (mostly `venv/` and `AI_Chat_Exports/`)
2. Multiple **test files** and **temp files** in root directory
3. **__pycache__** directories not gitignored
4. **Zone.Identifier** files (Windows metadata) throughout codebase
5. Legacy documentation in `docs/archive/` may confuse context

---

## 📊 File Analysis Summary

| Category | Count | Status | Action Needed |
|----------|-------|--------|---------------|
| Total project files | ~60k+ | Active | None |
| Files >30 days old | 53,364 | Mostly venv/exports | Review non-venv stale files |
| Python cache files | ~50+ | Normal | Add to .gitignore |
| Zone.Identifier files | ~100+ | Metadata pollution | Clean up |
| Test files in root | 7 | Scattered | Move to tests/ directory |
| Temp/versioned files | 5+ | Development artifacts | Archive or remove |

---

## 🔍 Detailed Findings

### 1. Recent Activity (Last 7 Days)

**Active Core Files:**
- ✅ `faithh_professional_backend_fixed.py` (2025-12-18 02:52) - Main backend
- ✅ `backend/llm_providers.py` (2025-12-17 11:45) - Phase 2 provider module
- ✅ `faithh_pet_v4.html` (2025-12-17 11:50) - UI with provider badges
- ✅ `configs/model_config.yaml` (2025-12-17 12:21) - Provider config
- ✅ `docs/GPT_PROJECT_CONTEXT.md` (2025-12-18 03:15) - Updated with Phase 2 complete
- ✅ `docs/GEN8_SERVICES_PLAN.md` (2025-12-18 03:15) - New Gen8 documentation
- ✅ `project_states.json` (2025-12-18 03:13) - Updated project tracking

**Recent Scripts:**
- `scripts/extract_recent_gpt.py` (2025-12-16) - GPT export utilities
- `scripts/search_embedding_convos.py` (2025-12-16) - RAG search tools

### 2. Potentially Stale Files (30+ Days Old)

**Root-Level Python Files:**
```
phase1_conversation_memory.py       (2025-11-30) - 18 days old
scaffolding_integration.py          (2025-11-27) - 21 days old
```

**Backend Files:**
```
backend/faithh_backend_v4_template.py  - Template file, likely unused
```

**Scripts:**
```
scripts/auto_journal.py                 (2025-11-26) - May be deprecated
scripts/index_constella_reference.py    (2025-11-25) - Indexing complete
scripts/index_constella_complete.py     (2025-11-26) - Indexing complete
```

**Status:** These files may still be relevant, but should be reviewed for current use.

### 3. Redundant/Cleanup Candidates

#### A. Python Cache Files (__pycache__)
**Location:** `/home/jonat/ai-stack/__pycache__/` and `/home/jonat/ai-stack/backend/__pycache__/`
**Files Found:**
- `faithh_professional_backend_fixed.cpython-312.pyc`
- `scaffolding_integration.cpython-312.pyc`
- `phase2_blueprint.cpython-312.pyc`
- `phase2_features.cpython-312.pyc`
- `backend/llm_providers.cpython-312.pyc`
- `backend/rag_processor.cpython-312.pyc`
- `backend/tool_system.cpython-312.pyc`
- `backend/coherence_sensor.cpython-312.pyc`

**Recommendation:** These are automatically generated. Add `__pycache__/` and `*.pyc` to `.gitignore`.

#### B. Zone.Identifier Files
**Location:** Throughout `AI_Chat_Exports/` directory
**Count:** ~100+ files
**Example:** `file_00000000f71061f5a16b6765f84b4b55-aa611c7f-be0e-4701-b57b-af294280573c.png:Zone.Identifier`

**What are these?** Windows NTFS alternate data streams indicating files downloaded from the internet.
**Recommendation:** Safe to delete. Add `*:Zone.Identifier` to `.gitignore`.

#### C. Test Files in Root Directory
**Files:**
```
test_chroma_query.py     (2025-12-11) - ChromaDB testing
test_coherence.py        (2025-12-11) - Coherence sensor testing
test_env.py              (2025-12-11) - Environment variable testing
test_rag.py              (2025-12-11) - RAG system testing
test_groq.sh             (untracked)  - Groq API testing
test_harmony.sh          (untracked)  - Harmony framework testing
```

**Recommendation:** Move to `tests/` directory or remove if no longer needed (recent activity suggests active use).

#### D. Temporary/Versioned Files
**Files:**
```
faithh_backend_temp_v2.py              (2025-12-13) - Contains multi-provider reference code
faithh_backend_temp_v2.py:Zone.Identifier  - Windows metadata
backend/faithh_backend_v4_template.py  - Template file
faithh_pet_v4.html                     - Current UI (v4 is now production)
```

**Recommendation:**
- `faithh_backend_temp_v2.py` - Archive or integrate remaining code, then remove
- `faithh_pet_v4.html` - Rename to `faithh_pet.html` (v4 is current production)
- `backend/faithh_backend_v4_template.py` - Archive if not actively used

#### E. Large Directories to Review
**AI_Chat_Exports/** - Contains GPT conversation exports with many Zone.Identifier files. Recent scripts suggest active use, but old exports could be archived.

**venv/** - Python virtual environment (53k+ files). This is normal but should be excluded from git tracking.

---

## 📚 Documentation Review

### Current Documentation Structure

#### Root-Level Docs (High Visibility)
```
✅ ARCHITECTURE.md               - System architecture overview
✅ FAITHH_TESTING_GUIDE.md       - Testing procedures
✅ GIT_COMMIT_INSTRUCTIONS.md    - Commit guidelines
✅ LIFE_MAP.md                   - Personal context for AI
✅ PHASE1_INTEGRATION_GUIDE.md   - Phase 1 reference (historical)
✅ QUICK_START_GUIDE.md          - Getting started guide
✅ README.md                     - Main project README
✅ REPOSITORY_STRUCTURE.md       - File organization guide
✅ START_HERE.md                 - Entry point for new users
⚠️  DOC_SYNC_ANALYSIS.md         - Doc sync status (may be outdated)
⚠️  context_quality_tests.md     - Test results (date unclear)
```

#### docs/ Directory
```
✅ docs/GPT_PROJECT_CONTEXT.md          - Updated 2025-12-18 (Phase 2 complete)
✅ docs/GEN8_SERVICES_PLAN.md           - Created 2025-12-18 (NEW)
✅ docs/CLAUDE_CODE_HANDOFF_PHASE2.md   - Phase 2 implementation spec
✅ docs/MASTER_CONTEXT.md               - AI operational context
✅ docs/HARMONY_CONTEXT.md              - Harmony framework reference
✅ docs/CONSTELLA_MASTER_REFERENCE.md   - Constella governance docs
⚠️  docs/CURRENT_STATE.md               - May be outdated (check date)
⚠️  docs/DOCKER_SERVICES.md             - Docker setup (verify currency)
⚠️  docs/BACKEND_CONFIG.md              - Backend configuration (verify vs actual)
```

#### docs/archive/ (Legacy Content)
**28+ archived documents** including multiple versions of guides and session reports.
**Status:** Good organization, but may confuse RAG system if indexed with equal priority.

**Recommendation:** Ensure RAG indexing scripts deprioritize `docs/archive/` content or add `.rag_ignore` markers.

#### docs/session-reports/ (11+ reports)
Recent session: `SESSION_2025-12-16_opus_local_inference.md`
**Status:** Useful historical record. Consider pruning reports older than 60 days.

### Documentation Gaps

#### ❌ Missing from project_states.json
The new `project_states.json` only tracks:
- FAITHH (Phase 2 complete)
- gen8_services (Parts ordered)

**Previously tracked projects (from old project_states.json):**
- ❌ **Constella Framework** - Major project, no longer in project_states.json
- ❌ **Audio Production (Tom Cat Sound LLC)** - Primary income focus, not tracked
- ❌ **Infrastructure (Tailscale, NAS, devices)** - Hardware ecosystem, not tracked

**Recommendation:** Decide if new `project_states.json` is intentionally scoped to active dev projects only, or if Constella/Audio/Infrastructure should be re-added.

#### ✅ Well-Documented Areas
- FAITHH Phase 2 implementation
- Multi-provider routing architecture
- Gen8 services planning (NEW)
- Harmony framework integration
- Git workflow and commit guidelines

---

## ⚙️ Configuration Consistency Check

### ✅ model_config.yaml (configs/model_config.yaml)
**Status:** CORRECT
**Groq Model:** `qwen/qwen3-32b` ✅ (matches expected configuration)
**Last Updated:** 2025-12-17

**Provider Configuration:**
```yaml
groq:
  model: "qwen/qwen3-32b"   # ✅ Correct
  timeout_s: 45

ollama:
  model: "qwen2.5:7b"       # Local fallback

local_webui:
  model: "qwen2.5-14b-instruct-q4_k_m"  # RTX 3090
```

**Routes:**
- `auto`: groq → local_webui → ollama ✅
- `code`: local_webui → groq → ollama ✅
- `fast`: groq → local_webui → ollama ✅
- `local`: local_webui → ollama ✅
- `cloud`: groq ✅

**Recommendation:** No changes needed. Configuration is consistent with Phase 2 requirements.

### ✅ Backend Integration (faithh_professional_backend_fixed.py)
**Status:** Recently updated (2025-12-18 02:52)
**Provider Module:** `backend/llm_providers.py` imported and active
**Phase 2 Features:**
- Multi-provider routing implemented
- Doc-grounded mode enforcement active
- Provider badges in UI

**Recommendation:** No issues detected.

---

## 🎯 Recommended Actions

### Priority 1: Immediate (Zero Risk, High Impact)

#### 1.1 Update .gitignore
**Add the following lines:**
```gitignore
# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd

# Windows metadata
*:Zone.Identifier

# Virtual environment
venv/
.venv/

# IDE
.vscode/
.idea/

# Logs
*.log
backend.log

# Environment variables (if not already present)
.env
```

**Command:**
```bash
echo -e "\n# Python cache\n__pycache__/\n*.pyc\n*.pyo\n*.pyd\n\n# Windows metadata\n*:Zone.Identifier\n\n# Logs\n*.log" >> .gitignore
```

#### 1.2 Clean Up Zone.Identifier Files
**Command:**
```bash
find /home/jonat/ai-stack -name "*:Zone.Identifier" -type f -delete
```
**Impact:** Removes ~100+ Windows metadata files, cleaner git status.

#### 1.3 Remove Python Cache Files (Already Gitignored)
**Command:**
```bash
find /home/jonat/ai-stack -path "*/venv" -prune -o -type d -name "__pycache__" -exec rm -rf {} +
find /home/jonat/ai-stack -path "*/venv" -prune -o -type f -name "*.pyc" -delete
```
**Impact:** Cleaner repository, forces fresh compilation (minimal impact).

---

### Priority 2: Housekeeping (Low Risk, Medium Impact)

#### 2.1 Organize Test Files
**Current State:** Test files scattered in root directory.
**Recommendation:** Create `tests/` directory and move test files:

```bash
mkdir -p /home/jonat/ai-stack/tests
mv /home/jonat/ai-stack/test_*.py /home/jonat/ai-stack/tests/
mv /home/jonat/ai-stack/test_*.sh /home/jonat/ai-stack/tests/
```

**Files to move:**
- `test_chroma_query.py`
- `test_coherence.py`
- `test_env.py`
- `test_rag.py`
- `test_groq.sh`
- `test_harmony.sh`

**Impact:** Cleaner root directory, organized testing structure.

#### 2.2 Rename Production Files (Remove Version Numbers)
**Recommendation:** Since `v4` is the current production version, remove version suffix:

```bash
# Rename UI file
mv /home/jonat/ai-stack/faithh_pet_v4.html /home/jonat/ai-stack/faithh_pet.html

# Update backend reference if needed (grep for faithh_pet_v4.html references)
```

**Impact:** Clearer naming convention, "current" version is obvious.

#### 2.3 Archive Temp Files
**Files to review:**
- `faithh_backend_temp_v2.py` - Contains multi-provider routing reference code
  - **Option A:** Delete if code has been fully integrated
  - **Option B:** Move to `archive/` if keeping for reference
- `backend/faithh_backend_v4_template.py` - Template file
  - Move to `templates/` directory or remove if unused

**Command (Option B):**
```bash
mkdir -p /home/jonat/ai-stack/archive
mv /home/jonat/ai-stack/faithh_backend_temp_v2.py /home/jonat/ai-stack/archive/
mv /home/jonat/ai-stack/backend/faithh_backend_v4_template.py /home/jonat/ai-stack/archive/
```

---

### Priority 3: Documentation Maintenance (Medium Risk, High Long-Term Value)

#### 3.1 Review and Update Potentially Stale Docs
**Files to review:**
- `docs/CURRENT_STATE.md` - Verify reflects Phase 2 completion
- `docs/BACKEND_CONFIG.md` - Verify matches current `model_config.yaml`
- `docs/DOCKER_SERVICES.md` - Verify service ports and configurations
- `DOC_SYNC_ANALYSIS.md` - Update or archive if outdated

**Recommendation:** Review each file, update or move to archive if outdated.

#### 3.2 Clarify project_states.json Scope
**Decision needed:** Is the new `project_states.json` intentionally focused only on active dev work?

**If YES (dev projects only):**
- No action needed
- Consider renaming to `dev_states.json` or `active_projects.json` for clarity

**If NO (should include all projects):**
- Re-add Constella, Audio Production, and Infrastructure projects
- Use the previous `project_states.json` as reference
- Update dates and status for each project

**Reference:** Previous `project_states.json` tracked:
- `constella` - Framework development (last worked 2025-11-26)
- `faithh` - AI assistant (last worked 2025-12-07)
- `audio_production` - Primary income (last worked 2025-11-20)
- `infrastructure` - Hardware ecosystem (last worked 2025-12-07)

#### 3.3 Add RAG Index Priority Config
**Recommendation:** Create `.rag_priorities` config to ensure archive docs don't pollute current context.

**Example:**
```yaml
# .rag_priorities (or add to existing RAG config)
priority_weights:
  docs/archive/: 0.3        # Lower weight for archived docs
  docs/session-reports/: 0.5  # Historical context
  docs/*.md: 1.0            # Current documentation
  *.md (root): 1.0          # Root-level guides
  backend/*.py: 1.0         # Active code
```

---

### Priority 4: Optional Enhancements (Low Priority, Future Consideration)

#### 4.1 Consolidate Duplicate Documentation
**Observation:** Multiple "getting started" and "architecture" docs exist:
- `START_HERE.md`
- `QUICK_START_GUIDE.md`
- `README.md`
- `ARCHITECTURE.md`
- `REPOSITORY_STRUCTURE.md`

**Recommendation:** Review for overlap and consolidate where appropriate. Not urgent.

#### 4.2 Archive Old Session Reports
**Recommendation:** Move session reports older than 60 days to `docs/archive/session-reports/`.

**Command:**
```bash
find /home/jonat/ai-stack/docs/session-reports -type f -name "*.md" -mtime +60 -exec mv {} /home/jonat/ai-stack/docs/archive/session-reports/ \;
```

**Impact:** Cleaner current docs, historical records preserved.

#### 4.3 Create Automated Cleanup Script
**Recommendation:** Create `scripts/cleanup.sh` to automate Priority 1 tasks:

```bash
#!/bin/bash
# scripts/cleanup.sh - Automated repository cleanup

echo "Cleaning Zone.Identifier files..."
find . -name "*:Zone.Identifier" -type f -delete

echo "Cleaning Python cache..."
find . -path "*/venv" -prune -o -type d -name "__pycache__" -exec rm -rf {} +
find . -path "*/venv" -prune -o -type f -name "*.pyc" -delete

echo "Cleanup complete!"
```

---

## 📈 Repository Health Metrics

| Metric | Value | Status |
|--------|-------|--------|
| **Active Development** | ✅ Yes (daily commits) | Healthy |
| **Phase 2 Status** | ✅ Complete (2025-12-17) | On Track |
| **Config Consistency** | ✅ Groq model correct | Healthy |
| **Documentation Coverage** | ⚠️ High but needs pruning | Good |
| **Code Organization** | ⚠️ Tests scattered, cache files present | Fair |
| **Tech Debt** | 🟡 Low (mostly cleanup needed) | Manageable |
| **Stale Files** | ⚠️ 53k+ old files (venv/exports) | Expected |

---

## 🔄 Follow-Up Actions for Opus Review

### Questions for Jonathan:
1. **project_states.json scope:** Should this track only active dev projects, or include Constella/Audio/Infrastructure?
2. **Test files:** Keep in root or move to `tests/` directory?
3. **faithh_backend_temp_v2.py:** Delete or archive? (Reference code for multi-provider routing)
4. **AI_Chat_Exports:** Archive old GPT conversation exports (pre-2025-12-01)?
5. **docs/archive priority:** Should RAG system deprioritize archived docs?

### Validation Checklist:
- [ ] Run acceptance tests after cleanup
- [ ] Verify FAITHH backend still starts correctly
- [ ] Confirm RAG queries still return relevant docs
- [ ] Test Groq routing with `qwen/qwen3-32b`
- [ ] Verify UI provider badges display correctly
- [ ] Check git status after cleanup (should be cleaner)

---

## 📝 Summary & Next Steps

### ✅ What's Working Well
- Phase 2 implementation complete and operational
- Config consistency maintained (groq model correct)
- Recent documentation updates (GPT_PROJECT_CONTEXT, GEN8_SERVICES_PLAN)
- Active development with daily commits

### ⚠️ What Needs Attention
- Repository hygiene (cache files, Zone.Identifier files, scattered tests)
- Documentation scope clarity (project_states.json coverage)
- RAG indexing priority for archived docs

### 🎯 Recommended Immediate Actions (15 minutes)
1. Update `.gitignore` (Priority 1.1)
2. Clean Zone.Identifier files (Priority 1.2)
3. Remove Python cache files (Priority 1.3)
4. Run git status to verify cleaner repository

### 🔜 Recommended Follow-Up (1-2 hours)
1. Organize test files into `tests/` directory (Priority 2.1)
2. Review and archive temp files (Priority 2.3)
3. Clarify project_states.json scope (Priority 3.2)
4. Update potentially stale documentation (Priority 3.1)

---

**Report Generated By:** Claude Code (Sonnet 4.5)
**Next Review Recommended:** 2025-01-18 (30 days)
**Review Focus:** Post-Phase-2 stability, Gen8 services deployment status

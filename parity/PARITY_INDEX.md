# FAITHH Parity File Index
**Last Updated**: 2025-12-02  
**Purpose**: Track documentation that mirrors real system state

---

## ⚠️ Parity System Status

**Honest Assessment**: The parity system is well-designed but under-maintained. Most files are stale. This index reflects what exists, not what's current.

**Recommendation**: Focus on LIFE_MAP.md and ARCHITECTURE.md as authoritative sources. Use parity files as reference only until an observation layer automates updates.

---

## Active Parity Files

### Core Documentation (Root)
| File | Status | Last Updated | Notes |
|------|--------|--------------|-------|
| `LIFE_MAP.md` | ✅ Current | 2025-12-02 | Primary compass |
| `ARCHITECTURE.md` | ✅ Current | 2025-12-02 | System architecture |
| `FAITHH_TESTING_GUIDE.md` | ✅ Current | 2025-12-02 | Testing framework |
| `REPOSITORY_STRUCTURE.md` | ✅ Current | 2025-12-02 | File organization |

### State Files (Root)
| File | Status | Auto-Updated | Notes |
|------|--------|--------------|-------|
| `faithh_memory.json` | ✅ Active | Manual | FAITHH identity |
| `decisions_log.json` | ✅ Active | Manual | Decision rationale |
| `project_states.json` | ✅ Active | Manual | Project phases |
| `scaffolding_state.json` | ✅ Active | Manual | Position awareness |

### Parity Folder
| File | Status | Notes |
|------|--------|-------|
| `parity/audio_workspace.md` | ⚠️ Unknown | Needs review |
| `parity/network_infrastructure.md` | ⚠️ Unknown | Needs review |
| `parity/dev_environment.md` | ⚠️ Unknown | Needs review |
| `parity/backend/PARITY_faithh_professional_backend.md` | ⚠️ Likely stale | Backend has evolved |
| `parity/frontend/PARITY_UI_faithh_pet_v4.md` | ⚠️ References old file | v4_enhanced vs v4 |

---

## Archived Parity Files

| File | Location | Reason |
|------|----------|--------|
| `PARITY_faithh_pet_v3.md` | `archive/ui_reference/` | v3 UI archived |

---

## What Should Be Tracked

### High Priority (Update when changed)
1. Backend endpoints and integrations
2. State file schemas
3. ChromaDB collection structure
4. LLM model configuration

### Medium Priority (Weekly review)
1. Audio routing setup
2. Network configuration
3. Development environment

### Low Priority (Monthly review)
1. UI component structure
2. Script inventory
3. Dependency versions

---

## Update Protocol

**Current (Manual)**:
1. Make change to system
2. Remember to update parity file
3. (Usually forgotten)

**Future (Automated)**:
1. Git hook detects file change
2. Observation layer flags stale parity
3. FAITHH generates update suggestion
4. Human approves or edits

---

## Files That Need Parity (But Don't Have It)

- [ ] `config.yaml` - Configuration options
- [ ] `.env` - Environment variables (template, not actual)
- [ ] `docker-compose.yml` - Service definitions
- [ ] `requirements.txt` - Python dependencies

---

*This index maintained manually until observation layer is built.*

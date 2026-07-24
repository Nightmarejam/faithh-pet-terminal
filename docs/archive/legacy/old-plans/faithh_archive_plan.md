# FAITHH Documentation & Archive Plan with Gen8 Migration
**Created:** 2026-01-07
**Purpose:** Comprehensive documentation, deduplication, archiving, and Gen8 migration strategy
**Status:** 🔶 Ready for Execution

---

## 🎯 Executive Summary

### Current Situation
- **WSL2 System**: Active development with 93,895 records in Docker volume `ai-stack_chromadb_data`
- **Gen8 Server**: Production ChromaDB with 28,876 indexed chunks (full conversation history)
- **Duplication Issue**: Two separate ChromaDB instances with overlapping but different data
- **File Clutter**: Backup variants, duplicate exports, and unclear canonical files

### Strategic Goals
1. **Consolidate ChromaDB**: Migrate to Gen8 as single source of truth
2. **Deduplicate Files**: Remove backup variants and establish canonical versions
3. **Archive Legacy Code**: Move non-essential code to organized archive structure
4. **Document Everything**: Create clear migration paths and recovery procedures
5. **Establish Parity**: Maintain synchronized documentation across all AI assistants

---

## 📊 Current State Analysis

### Database Inventory

#### WSL2 Local ChromaDB (Docker Volume)
```
Location: Docker volume ai-stack_chromadb_data
Collections:
  - documents (54fe7aac...): 91,416 records
    * File chunks with filename/start_pos/end_pos metadata
    * Last record: HARMONY_CONTEXT.md
  
  - documents_768 (d57fa180...): 93,895 records
    * Mixed: 91,414 file chunks + 137 live_chat + 2,344 curated
    * Embedding: all-mpnet-base-v2 (sentence_transformer)
    * Space: cosine
    * Last record: live_conversation from Dec 2025
  
  - test_collection (fa8abb3e...): 1 record
    * 384-dim (different embedder)
    * Legacy test data

Status: ⚠️ STRANDED - Persisted in volume, not actively managed
```

#### Gen8 Production ChromaDB
```
Location: http://servicebox.taileb8c60.ts.net:8000
Collection: faithh_knowledge_base
Records: 28,876 chunks (reindexed 2026-01-07)
Breakdown:
  - Conversation chunks: 21,925
    * ChatGPT: 202 conversations
    * Claude: 83 conversations
    * Date range: Feb 2024 → Jan 2026
  - Documentation chunks: 6,951
Embedding: BGE-base-en-v1.5 (768-dim)
Status: ✅ PRODUCTION - Clean, no duplicates
```

### Key Insight
**The Gen8 database is NEWER and CLEANER than WSL2 local**. It contains:
- Full conversation history (Feb 2024-Jan 2026)
- Recently reindexed with no duplicates
- Proper metadata tracking
- Already in production on always-on hardware

**Recommendation**: Gen8 should be the migration TARGET, not source.

---

## 🗂️ File Organization Analysis

### Canonical Files (Keep in Root)
```
Backend:
  ✅ faithh_professional_backend_fixed.py (canonical)
  ✅ faithh_professional_backend.py (shim - recently added)

UI:
  ✅ faithh_pet_v4.html (main UI)
  ⚠️ faithh_pet_v3.html (older version, still referenced)

Configuration:
  ✅ .env (secrets)
  ✅ .env.example (template)
  ✅ docker-compose.yml
  ✅ project_states.json (source of truth)
  ✅ requirements.txt

Operations:
  ✅ restart_backend.sh
  ✅ stop_backend.sh
  ✅ README.md
  ✅ LIFE_MAP.md
  ✅ MASTER_CONTEXT.md
```

### Archive Candidates (High Confidence)
```
UI Backups:
  → faithh_pet_v4_backup.html
  → faithh_pet_v4_enhanced_patched.html

One-off Scripts:
  → check_all_dbs.py
  → check_backup_db.py
  → analyze_gen8.py
  → analyze_gen8_deep.py
  → add_harmony_docs.py

Demo/Test Code:
  → backend/agent_demo.py

ChatGPT Export Duplicates:
  → AI_Chat_Exports/Chat_GPT_Exports/ (many duplicate images)
  → Grok_Exports/ (significant duplication)
```

### Directories Already Archive-Like
```
✅ archive/ - Already designated for old code
✅ legacy/ - Old UI versions and deprecated scripts
✅ backups/ - Backend version snapshots
✅ snapshots/ - Historical state captures
```

---

## 🚀 Migration Strategy: WSL2 → Gen8

### Phase 1: Data Assessment & Comparison
**Goal**: Understand what's unique in WSL2 that Gen8 lacks

#### Step 1.1: Inventory Live Chat Records
```python
# WSL2 has 137 live_chat records that Gen8 doesn't have
# These are episodic memory from Nov-Dec 2025
# Decision: MIGRATE these to Gen8
```

#### Step 1.2: Compare File Chunks
```python
# WSL2: 91,414 file chunks (no category tag)
# Gen8: 6,951 documentation chunks (categorized)
# Hypothesis: Gen8 has newer, better-organized data
# Action: Verify by sampling filenames/dates
```

#### Step 1.3: Identify Migration Candidates
```
Priority 1 (MUST migrate):
  - 137 live_chat records (Nov-Dec 2025)
  - Any file chunks dated after Jan 2026

Priority 2 (OPTIONAL):
  - Constella framework docs (if not in Gen8)
  - Recent Tom Cat Sound business docs

Priority 3 (SKIP):
  - Old conversation duplicates (Gen8 has full history)
  - Test collection (1 record, not needed)
```

### Phase 2: One-Way Migration Script
**Tool**: Python script using ChromaDB client API

```python
#!/usr/bin/env python3
"""
Migrate live_chat and recent file chunks from WSL2 to Gen8.
One-way sync: WSL2 (source) → Gen8 (target)
"""

import chromadb
from datetime import datetime

# Source: WSL2 Docker ChromaDB
source_client = chromadb.HttpClient(host="127.0.0.1", port=8000)
source_collection = source_client.get_collection("documents_768")

# Target: Gen8 Production ChromaDB
target_client = chromadb.HttpClient(host="servicebox.taileb8c60.ts.net", port=8000)
target_collection = target_client.get_collection("faithh_knowledge_base")

# Migrate live_chat records
live_chat_filter = {"category": "live_chat"}
results = source_collection.get(where=live_chat_filter, include=["embeddings", "metadatas", "documents"])

print(f"Migrating {len(results['ids'])} live_chat records...")
target_collection.add(
    ids=results["ids"],
    embeddings=results["embeddings"],
    metadatas=results["metadatas"],
    documents=results["documents"]
)
print("✅ Live chat migration complete")

# Optional: Migrate recent file chunks (after Jan 7, 2026)
# ... (similar pattern with date filter)
```

### Phase 3: Backend Configuration Update
**File**: `faithh_professional_backend_fixed.py`

Change ChromaDB connection from local Docker to Gen8:
```python
# OLD (local Docker)
chroma_client = chromadb.HttpClient(host="localhost", port=8000)

# NEW (Gen8 production)
chroma_client = chromadb.HttpClient(host="servicebox.taileb8c60.ts.net", port=8000)
```

Update environment variable in `.env`:
```bash
# OLD
CHROMADB_HOST=localhost
CHROMADB_PORT=8000

# NEW
CHROMADB_HOST=servicebox.taileb8c60.ts.net
CHROMADB_PORT=8000
CHROMADB_COLLECTION=faithh_knowledge_base
```

### Phase 4: Validation & Rollback Plan
**Validation Checklist**:
- [ ] Backend connects to Gen8 successfully
- [ ] RAG queries return expected results
- [ ] Live chat records are searchable
- [ ] No duplicate IDs (Gen8 count increases correctly)
- [ ] Performance is acceptable (network latency check)

**Rollback Plan**:
```bash
# If Gen8 migration fails, revert to local Docker:
# 1. Change .env back to localhost:8000
# 2. Restart backend: ./restart_backend.sh
# 3. WSL2 Docker volume is unchanged (nothing deleted)
```

### Phase 5: Decommission Local ChromaDB
**Only after 2+ weeks of stable Gen8 operation**:
```bash
# Stop local ChromaDB container
docker compose stop chromadb

# Optional: Remove volume (after backup)
docker volume rm ai-stack_chromadb_data
```

---

## 📁 File Deduplication & Archiving Plan

### Archive Structure
```
ARCHIVE/
├── README.md (explains archive purpose + recovery)
├── 2026-01-07_pre_dedupe/
│   ├── ui_variants/
│   │   ├── faithh_pet_v4_backup.html
│   │   ├── faithh_pet_v4_enhanced_patched.html
│   │   └── recovery_notes.md
│   ├── scripts_oneoff/
│   │   ├── check_all_dbs.py
│   │   ├── analyze_gen8*.py
│   │   └── add_harmony_docs.py
│   └── backend_experiments/
│       └── agent_demo.py
├── chat_export_duplicates/
│   ├── grok_asset_deduplication_map.json
│   └── chatgpt_image_deduplication_map.json
└── docker_volumes_backup/
    └── chromadb_wsl2_snapshot_20260107.tar.gz
```

### Deduplication Execution Plan

#### Step 1: UI Consolidation
```bash
# Choose canonical UI
CANONICAL_UI="faithh_pet_v4.html"

# Archive variants
mkdir -p ARCHIVE/2026-01-07_pre_dedupe/ui_variants/
mv faithh_pet_v4_backup.html ARCHIVE/2026-01-07_pre_dedupe/ui_variants/
mv faithh_pet_v4_enhanced_patched.html ARCHIVE/2026-01-07_pre_dedupe/ui_variants/

# Add recovery notes
cat > ARCHIVE/2026-01-07_pre_dedupe/ui_variants/recovery_notes.md <<EOF
# UI Variants Archive
Archived: 2026-01-07
Reason: Backup/patched variants superseded by canonical faithh_pet_v4.html

To restore a variant:
  cp ARCHIVE/2026-01-07_pre_dedupe/ui_variants/<file> ./

Canonical UI: faithh_pet_v4.html
Last known good: faithh_pet_v3.html (kept in root as fallback)
EOF
```

#### Step 2: One-off Scripts
```bash
mkdir -p ARCHIVE/2026-01-07_pre_dedupe/scripts_oneoff/
mv check_all_dbs.py analyze_gen8*.py add_harmony_docs.py \
   ARCHIVE/2026-01-07_pre_dedupe/scripts_oneoff/

git add ARCHIVE/2026-01-07_pre_dedupe/scripts_oneoff/
git commit -m "Archive one-off database analysis scripts"
```

#### Step 3: Backend Experiments
```bash
mkdir -p ARCHIVE/2026-01-07_pre_dedupe/backend_experiments/
mv backend/agent_demo.py ARCHIVE/2026-01-07_pre_dedupe/backend_experiments/
```

#### Step 4: Chat Export Deduplication
**This is complex - use dedicated script**:
```python
#!/usr/bin/env python3
"""
Deduplicate AI_Chat_Exports by content hash.
Strategy: Keep one copy, create hardlinks or symlinks for duplicates.
"""
import hashlib
import json
from pathlib import Path
from collections import defaultdict

def hash_file(path):
    """SHA256 hash of file content."""
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def deduplicate_exports(base_path="AI_Chat_Exports"):
    hashes = defaultdict(list)
    
    # Index all files by hash
    for file in Path(base_path).rglob("*"):
        if file.is_file():
            h = hash_file(file)
            hashes[h].append(file)
    
    # Report duplicates
    dupes = {h: files for h, files in hashes.items() if len(files) > 1}
    
    # Save deduplication map
    dupe_map = {
        h: [str(f) for f in files]
        for h, files in dupes.items()
    }
    
    with open("ARCHIVE/chat_export_duplicates/deduplication_map.json", "w") as f:
        json.dump(dupe_map, f, indent=2)
    
    print(f"Found {len(dupes)} duplicate sets")
    print(f"Total duplicated files: {sum(len(files)-1 for files in dupes.values())}")
    
    # Optional: Create hardlinks (ONLY if same filesystem)
    # for h, files in dupes.items():
    #     canonical = files[0]
    #     for dupe in files[1:]:
    #         dupe.unlink()
    #         os.link(canonical, dupe)

if __name__ == "__main__":
    deduplicate_exports()
```

---

## 📝 Documentation Updates

### Files Requiring Updates

#### 1. MASTER_CONTEXT.md
**Changes Needed**:
```diff
- Database: ChromaDB on Gen8 (servicebox.taileb8c60.ts.net:8000)
- Collection: faithh_knowledge_base
- Documents: 28,876 chunks (reindexed 2026-01-07)
+ Migration Status: ✅ Complete (Jan 2026)
+ WSL2 Local: Decommissioned (replaced by Gen8)
+ Live Chat Integration: 137 records migrated from local
```

#### 2. project_states.json
**Add migration section**:
```json
{
  "FAITHH": {
    "infrastructure": {
      "migration_history": {
        "2026-01-07": {
          "from": "WSL2 Docker volume ai-stack_chromadb_data",
          "to": "Gen8 ChromaDB servicebox.taileb8c60.ts.net:8000",
          "records_migrated": 137,
          "type": "live_chat episodic memory",
          "status": "complete"
        }
      }
    }
  }
}
```

#### 3. docs/CONTEXT_PARITY_GUIDE.md
**Add Gen8 migration notes**:
```markdown
## ChromaDB Location (Source of Truth)
- **Production**: Gen8 at servicebox.taileb8c60.ts.net:8000
- **Collection**: faithh_knowledge_base
- **DO NOT** point backend at localhost:8000 (deprecated)
- **Backup Strategy**: Gen8 automated backups (planned)
```

#### 4. docs/GPT_PROJECT_CONTEXT.md
**Update infrastructure section** (same as MASTER_CONTEXT.md changes)

#### 5. LIFE_MAP.md
**Update FAITHH snapshot**:
```markdown
## FAITHH Snapshot (2026-01-07)
- **Database**: Gen8 Production (servicebox.taileb8c60.ts.net:8000)
- **Migration**: Complete from WSL2 local
- **Mixed Memory**: 91k file chunks + 137 live chat records
```

---

## 🔄 Parity Automation

### New Script: `scripts/update_parity.py`
```python
#!/usr/bin/env python3
"""
Automated parity file updater.
Reads project_states.json as source of truth, generates consistent sections.
"""

import json
from pathlib import Path
from datetime import datetime

def load_project_states():
    with open("project_states.json") as f:
        return json.load(f)

def update_master_context(states):
    """Update MASTER_CONTEXT.md RAG section."""
    faithh = states["projects"]["FAITHH"]
    infra = faithh["infrastructure"]
    
    rag_section = f"""
## RAG System Status (Auto-updated from project_states.json)

### Current State
- **Collection:** {infra['collection']}
- **Total Chunks:** {infra['chunks_indexed']}
- **Database:** {infra['database']}
- **Embedding:** {infra['embedding']}
- **Last Updated:** {states['last_updated']}

### Breakdown
{json.dumps(infra['breakdown'], indent=2)}
"""
    
    # Read, replace section, write back
    content = Path("MASTER_CONTEXT.md").read_text()
    # ... (section replacement logic)
    Path("MASTER_CONTEXT.md").write_text(content)
    print("✅ Updated MASTER_CONTEXT.md")

def update_gpt_context(states):
    """Update docs/GPT_PROJECT_CONTEXT.md."""
    # ... (similar to master context)
    pass

def update_life_map(states):
    """Update LIFE_MAP.md FAITHH snapshot."""
    # ... (similar pattern)
    pass

if __name__ == "__main__":
    states = load_project_states()
    update_master_context(states)
    update_gpt_context(states)
    update_life_map(states)
    print(f"✅ All parity files updated from project_states.json")
```

**Usage**:
```bash
# After updating project_states.json:
python scripts/update_parity.py

# Verify changes:
git diff MASTER_CONTEXT.md docs/GPT_PROJECT_CONTEXT.md LIFE_MAP.md
```

---

## 🔒 Backup Strategy

### Pre-Migration Backups

#### WSL2 ChromaDB Volume Backup
```bash
# Export Docker volume to tarball
docker run --rm \
  -v ai-stack_chromadb_data:/source:ro \
  -v ~/backups:/backup \
  alpine \
  tar czf /backup/chromadb_wsl2_snapshot_20260107.tar.gz -C /source .

# Verify backup
ls -lh ~/backups/chromadb_wsl2_snapshot_20260107.tar.gz
```

#### Gen8 ChromaDB Backup (Pre-Migration)
```bash
# On Gen8 server (via SSH):
ssh jonat@servicebox.taileb8c60.ts.net "
  cd ~/services/chromadb/
  docker compose exec chromadb /bin/sh -c 'tar czf - /chroma/chroma' > \
    ~/backups/chromadb_gen8_pre_migration_20260107.tar.gz
"

# Download to WSL2 for safekeeping
scp jonat@servicebox.taileb8c60.ts.net:~/backups/chromadb_gen8_pre_migration_20260107.tar.gz \
    ~/backups/
```

### Post-Migration Automated Backups (Gen8)
**Cron job on Gen8**:
```bash
# Daily backup of ChromaDB at 3 AM
0 3 * * * /home/jonat/scripts/backup_chromadb.sh

# backup_chromadb.sh:
#!/bin/bash
BACKUP_DIR="/data/backups/chromadb"
DATE=$(date +%Y%m%d)
docker compose -f /home/jonat/services/chromadb/docker-compose.yml \
  exec chromadb tar czf - /chroma/chroma > \
  "${BACKUP_DIR}/chromadb_${DATE}.tar.gz"

# Keep only last 7 days
find "${BACKUP_DIR}" -name "chromadb_*.tar.gz" -mtime +7 -delete
```

---

## ✅ Execution Checklist

### Pre-Migration
- [ ] Read this entire document
- [ ] Backup WSL2 Docker volume (see Backup Strategy)
- [ ] Backup Gen8 ChromaDB (see Backup Strategy)
- [ ] Verify Gen8 is accessible from WSL2: `curl http://servicebox.taileb8c60.ts.net:8000/api/v2/heartbeat`
- [ ] Test query on Gen8: verify faithh_knowledge_base works

### Phase 1: Data Assessment (1-2 hours)
- [ ] Run inventory script on WSL2 collections
- [ ] Document what's unique in WSL2 (live_chat, recent files)
- [ ] Decide migration priority (live_chat = priority 1)

### Phase 2: Migration Execution (2-3 hours)
- [ ] Write/test migration script (dry-run first)
- [ ] Run migration: WSL2 → Gen8
- [ ] Verify Gen8 record count increased correctly
- [ ] Test sample queries for migrated data

### Phase 3: Backend Switchover (30 minutes)
- [ ] Update `.env`: CHROMADB_HOST=servicebox.taileb8c60.ts.net
- [ ] Update `faithh_professional_backend_fixed.py` if hardcoded
- [ ] Restart backend: `./restart_backend.sh`
- [ ] Test RAG queries work
- [ ] Monitor backend.log for errors

### Phase 4: Validation Period (1-2 weeks)
- [ ] Use FAITHH normally, watch for issues
- [ ] Verify no "Collection does not exist" errors
- [ ] Check RAG result quality (files + live chat)
- [ ] Monitor Gen8 resource usage (CPU, RAM, disk)

### Phase 5: Decommission (after validation)
- [ ] Stop local ChromaDB: `docker compose stop chromadb`
- [ ] Update docker-compose.yml: comment out chromadb service
- [ ] Document WSL2 volume location for emergency recovery
- [ ] Optional: Delete volume after 30-day safety period

### Phase 6: File Cleanup (2-3 hours)
- [ ] Execute UI consolidation (Step 1)
- [ ] Archive one-off scripts (Step 2)
- [ ] Archive backend experiments (Step 3)
- [ ] Run chat export deduplication report (Step 4)
- [ ] Commit changes: `git add ARCHIVE/ && git commit -m "Archive pre-Gen8 migration variants"`

### Phase 7: Documentation Updates (1 hour)
- [ ] Update MASTER_CONTEXT.md
- [ ] Update project_states.json
- [ ] Update docs/GPT_PROJECT_CONTEXT.md
- [ ] Update LIFE_MAP.md
- [ ] Run `python scripts/update_parity.py` (after creating it)
- [ ] Commit: `git commit -m "Update docs post-Gen8 migration"`

---

## 🚨 Risk Mitigation

### Risk 1: Network Latency (Gen8 is remote)
**Mitigation**:
- Gen8 is on LAN (servicebox.taileb8c60.ts.net) and Tailscale (servicebox.taileb8c60.ts.net)
- Latency should be <5ms on LAN
- Test before full migration: `ping -c 20 servicebox.taileb8c60.ts.net`

**Fallback**: Keep WSL2 Docker volume for 30 days as rollback option

### Risk 2: Data Loss During Migration
**Mitigation**:
- Full backups before migration (WSL2 + Gen8)
- Migration script does NOT delete from source
- Dry-run mode with `print()` only, no `.add()` calls

**Recovery**: Restore from tarball backups (see Backup Strategy)

### Risk 3: Gen8 Hardware Failure
**Mitigation**:
- Gen8 has ECC RAM (error correction)
- UPS recommended for power protection
- Automated daily backups (cron job)

**Recovery**: Restore ChromaDB from latest backup tarball

### Risk 4: Breaking Backend After Switchover
**Mitigation**:
- Test connection before full switchover
- Backend config change is 1-line in `.env`
- Rollback is instant: change `.env` back, restart

**Rollback Time**: < 5 minutes

---

## 📈 Success Criteria

### Migration Success
- [ ] Gen8 record count = 28,876 + 137 (live_chat) = 29,013
- [ ] No duplicate IDs in Gen8 collection
- [ ] Backend connects to Gen8 without errors
- [ ] Sample RAG queries return correct results (both files + chat)
- [ ] No "Collection does not exist" errors in logs

### Deduplication Success
- [ ] Root directory has clear canonical files only
- [ ] ARCHIVE/ directory has organized, documented variants
- [ ] Git history preserved (moves via `git mv`)
- [ ] Recovery notes exist for all archived content

### Documentation Success
- [ ] All parity files updated and synchronized
- [ ] project_states.json reflects current infrastructure
- [ ] Migration documented with date/reason/evidence
- [ ] Future operators understand what changed and why

---

## 🔮 Future Enhancements

### Automated Monitoring
- [ ] Uptime Kuma on Gen8 monitoring ChromaDB health
- [ ] Disk space alerts (Gen8 storage capacity)
- [ ] Daily backup verification script

### Advanced ChromaDB Features
- [ ] Multiple collections for different content types:
  * `faithh_conversations` (chat history)
  * `faithh_documentation` (file chunks)
  * `faithh_live_memory` (live chat episodes)
- [ ] Collection versioning for rollback capability
- [ ] Automated reindexing on new conversation exports

### Parity Enforcement
- [ ] Pre-commit hook to check parity file sync
- [ ] CI/CD test that validates project_states.json consistency
- [ ] Automated parity updates via GitHub Actions

---

## 📞 Support & Recovery

### Emergency Contacts
- **Gen8 Access**: `ssh jonat@servicebox.taileb8c60.ts.net` (Tailscale) or `ssh jonat@servicebox.taileb8c60.ts.net` (LAN)
- **ChromaDB Admin**: Web UI at `http://servicebox.taileb8c60.ts.net:8000`
- **Backup Location**: `~/backups/chromadb_*.tar.gz`

### Quick Recovery Commands
```bash
# Restore WSL2 local ChromaDB from backup
docker volume create ai-stack_chromadb_data
docker run --rm \
  -v ai-stack_chromadb_data:/target \
  -v ~/backups:/backup:ro \
  alpine \
  tar xzf /backup/chromadb_wsl2_snapshot_20260107.tar.gz -C /target

# Restore Gen8 ChromaDB from backup (on Gen8 server)
ssh jonat@servicebox.taileb8c60.ts.net
cd ~/services/chromadb/
docker compose down
tar xzf ~/backups/chromadb_gen8_YYYYMMDD.tar.gz -C /data/chromadb/
docker compose up -d
```

---

**Document Version**: 1.0
**Next Review**: 2026-02-07 (30 days post-migration)
**Maintained By**: Jonathan (with FAITHH assistance)

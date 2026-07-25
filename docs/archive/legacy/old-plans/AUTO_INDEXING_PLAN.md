# Auto-Indexing System Plan
**Created:** 2025-11-14 14:57

## Overview
Automatically index new FAITHH conversations into RAG system

## Implementation Strategy

### Option 1: Session Logging (Recommended)
**Pros:** 
- Real-time capture of conversations
- No parsing needed
- Structured data from the start

**Implementation:**
1. Add session logger to faithh_pet_v3.html
2. Save to ~/ai-stack/logs/sessions/YYYY-MM-DD_HHMMSS.json
3. Background watcher indexes new files
4. Deduplicates using conversation hash

**Code Location:**
- UI modification: faithh_pet_v3.html (add session export)
- Indexer: scripts/auto_index_sessions.py
- Watcher: scripts/session_watcher.py (systemd service)

### Option 2: Periodic Export Indexing
**Pros:**
- No UI changes needed
- Uses existing export format

**Implementation:**
1. Export conversations from UI manually
2. Cron job runs hourly to scan AI_Chat_Exports/
3. Index only new files (hash comparison)

**Cron Entry:**
```bash
0 * * * * cd /home/jonat/ai-stack && source venv/bin/activate && python scripts/auto_index_exports.py
```

### Option 3: Shutdown Hook
**Pros:**
- Simple one-time export per session
- Minimal overhead

**Implementation:**
1. UI saves full session on page unload
2. Backend /api/save_session endpoint
3. Indexer runs on backend startup

## Recommended Approach
Start with **Option 1** (Session Logging) because:
- Most comprehensive
- Real-time data
- Best for future analysis
- Can add Option 3 as backup

## Next Steps
1. Modify faithh_pet_v3.html to log conversations
2. Create auto-indexer script
3. Set up systemd watcher service
4. Test with real conversations

---
*Update this plan after implementation*

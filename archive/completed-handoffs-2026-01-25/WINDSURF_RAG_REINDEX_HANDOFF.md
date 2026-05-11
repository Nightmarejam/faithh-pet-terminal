# Windsurf RAG Re-Index Handoff

**Created:** 2026-01-25
**Priority:** HIGH
**Purpose:** Re-index AI chat exports to Gen8 ChromaDB

---

## Quick Summary

Re-index all AI conversations from fresh exports to the Gen8 ChromaDB server. The previous index had ~208 documents but may be stale or incomplete. Fresh exports exist from 01-19-2026.

---

## Step 1: Verify Gen8 Connectivity

```bash
# Test from WSL
curl -s "http://192.158.1.243:8000/api/v2/heartbeat"

# If "Host not allowed" error, check ChromaDB config on Gen8:
ssh -i ~/.ssh/servicebox_ed25519 jonat@192.158.1.243
cat ~/services/chromadb/docker-compose.yml
docker logs chromadb | tail -20
```

**Expected:** `{"nanosecond heartbeat": <timestamp>}`

**If host not allowed:** May need to add `CHROMA_SERVER_CORS_ALLOW_ORIGINS=*` or restart ChromaDB.

---

## Step 2: Run Extraction Script

```bash
cd ~/ai-stack
source venv/bin/activate
python extract_conversations.py
```

**Expected Output:**
- ChatGPT conversations extracted (~209)
- Claude conversations extracted (~93)
- Output: `knowledge_base/extracted/conversations_for_chromadb.json`

---

## Step 3: Index to ChromaDB

```bash
python index_chromadb_direct.py
```

**Expected:**
- Connect to `http://192.158.1.243:8000`
- Collection: `faithh_knowledge_base`
- Should index 300+ documents

---

## Step 4: Verify & Test

```bash
# Check document count
curl -s "http://192.158.1.243:8000/api/v1/collections/faithh_knowledge_base" | jq '.count'

# Or via Python
python -c "
import chromadb
client = chromadb.HttpClient(host='http://192.158.1.243:8000')
col = client.get_collection('faithh_knowledge_base')
print(f'Documents: {col.count()}')
"
```

---

## Source Files

| File | Location |
|------|----------|
| ChatGPT Export | `AI_Chat_Exports/01-19-2026 Exports/ChatGPT/conversations.json` |
| Claude Export | `AI_Chat_Exports/01-19-2026 Exports/Claude/conversations.json` |
| Extraction Script | `extract_conversations.py` |
| Indexing Script | `index_chromadb_direct.py` |
| Output JSON | `knowledge_base/extracted/conversations_for_chromadb.json` |

---

## Gen8 Server Details

| Property | Value |
|----------|-------|
| Hostname | servicebox |
| LAN IP | 192.158.1.243 |
| Tailscale IP | 192.158.1.243 |
| ChromaDB Port | 8000 |
| SSH User | jonat |
| SSH Key | `~/.ssh/servicebox_ed25519` |

---

## Potential Issues & Fixes

### Issue: "Host not allowed"
```bash
# SSH to Gen8 and check ChromaDB config
ssh -i ~/.ssh/servicebox_ed25519 jonat@192.158.1.243
cd ~/services/chromadb

# Add CORS settings to docker-compose.yml:
# environment:
#   - CHROMA_SERVER_CORS_ALLOW_ORIGINS=["*"]

docker-compose restart chromadb
```

### Issue: Connection refused
```bash
# Check if ChromaDB is running
docker ps | grep chromadb

# Restart if needed
cd ~/services/chromadb && docker-compose up -d
```

### Issue: IP address changed
- Cable/port was changed on switch
- May need to update DHCP reservation or set static IP
- Check current IP: `hostname -I` on Gen8

### Issue: Duplicate documents
The indexing script clears existing documents before adding new ones. If you want to preserve existing data, comment out the delete section.

---

## Success Criteria

1. ✅ Gen8 ChromaDB accessible at `192.158.1.243:8000`
2. ✅ Extraction script runs without errors
3. ✅ 300+ documents indexed (209 ChatGPT + 93 Claude)
4. ✅ Test query returns relevant results
5. ✅ FAITHH backend can connect and query

---

## After Indexing

Update FAITHH backend `.env` if needed:
```bash
CHROMADB_HOST=192.158.1.243
# or
CHROMA_URL=http://192.158.1.243:8000
```

Then restart backend:
```bash
./restart_backend.sh
```

---

## Report Back

Please report:
1. Gen8 connectivity status
2. Number of conversations extracted
3. Number of documents indexed
4. Any errors encountered
5. Test query results

---

**End of Handoff**

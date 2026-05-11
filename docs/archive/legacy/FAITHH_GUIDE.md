# FAITHH Complete Guide
**The Single Source of Truth for FAITHH**

**Last Updated:** 2026-01-25  
**Version:** 2.0 (Post-Reindex)  
**Status:** Production Ready

---

## Table of Contents
1. [What is FAITHH?](#what-is-faithh)
2. [Quick Start](#quick-start)
3. [How It Works](#how-it-works)
4. [Features & Capabilities](#features--capabilities)
5. [Common Tasks](#common-tasks)
6. [File Location Guide](#file-location-guide)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Usage](#advanced-usage)

---

## What is FAITHH?

**FAITHH** (Friendly AI Teaching & Helping Hub) is your personal AI assistant that:

### Core Value Proposition
- **Learns from YOUR history** - Indexes all your ChatGPT/Claude conversations (32,499 chunks)
- **Multi-provider flexibility** - Switches between Groq (fast cloud), Ollama (local), and Gemini
- **Self-aware** - Maintains memory, decision logs, and project state
- **Production infrastructure** - Full Gen8 server stack with monitoring

### What Makes It Special
Unlike generic AI assistants, FAITHH:
1. **Remembers your conversations** - RAG search across 306 indexed conversations
2. **Knows your projects** - Aware of Tom Cat Sound, Constella Framework, etc.
3. **Runs locally** - Can work offline with Ollama
4. **Fully customizable** - You control the models, prompts, and behavior

### Current Stats
- **32,499 conversation chunks** indexed
- **306 conversations** (208 ChatGPT + 98 Claude)
- **12 services** running on Gen8
- **3 LLM providers** configured
- **100% uptime** on Gen8 infrastructure

---

## Quick Start

### Starting FAITHH (3 Steps)

#### 1. Start the Backend
```bash
cd ~/ai-stack
./restart_backend.sh
```

#### 2. Open the UI
Visit: http://localhost:5557

#### 3. Start Chatting
- Select a model (or use "auto")
- Toggle RAG if you want context from past conversations
- Type your message

**That's it!** FAITHH is running.

### Stopping FAITHH
```bash
cd ~/ai-stack
./stop_backend.sh
```

### Checking Status
```bash
# Backend health
curl http://localhost:5557/api/status | jq

# Gen8 services
./gen8_health_check.sh
```

---

## How It Works

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
│              faithh_pet_v4.html (Browser)               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  BACKEND (WSL2)                          │
│        faithh_professional_backend_fixed.py              │
│                   Port: 5557                             │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ LLM Providers│  │ RAG Processor│  │  Coherence   │  │
│  │ Groq/Ollama/ │  │   ChromaDB   │  │   Sensor     │  │
│  │   Gemini     │  │   Queries    │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              GEN8 SERVER (192.158.1.243)                │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  ChromaDB    │  │   Grafana    │  │   Gitea      │  │
│  │  32,499      │  │  Monitoring  │  │  Git Repos   │  │
│  │  chunks      │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Pi-hole     │  │ Vaultwarden  │  │ Prometheus   │  │
│  │  DNS Filter  │  │  Passwords   │  │  Metrics     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User sends message** → Frontend (faithh_pet_v4.html)
2. **Frontend calls backend** → POST /api/chat
3. **Backend checks RAG** → Queries ChromaDB on Gen8 if enabled
4. **Backend calls LLM** → Groq → Gemini → Ollama (failover)
5. **Response streams back** → Server-Sent Events (SSE)
6. **Frontend displays** → Markdown rendering with syntax highlighting

### RAG System

**How RAG Works:**
1. Your message is embedded (converted to vector)
2. ChromaDB finds similar conversation chunks
3. Top 5 relevant chunks are added to context
4. LLM generates response with this context

**What's Indexed:**
- All ChatGPT conversations (28,255 chunks)
- All Claude conversations (4,244 chunks)
- Chunked at 1500 characters with 200 char overlap
- Embedded with all-MiniLM-L6-v2 (384 dimensions)

---

## Features & Capabilities

### 1. Multi-Provider LLM Support

| Provider | Model | Speed | Cost | Use Case |
|----------|-------|-------|------|----------|
| **Groq** | llama-3.3-70b-versatile | ⚡ Very Fast | 💰 Cheap | Primary |
| **Gemini** | gemini-2.0-flash-exp | ⚡ Fast | 💰 Free tier | Fallback |
| **Ollama** | llama31-faithh:latest | 🐢 Slow | 💰 Free | Offline |

### 2. RAG-Powered Context

**Toggle RAG on/off** in the UI to:
- ✅ **ON:** Get context from your conversation history
- ❌ **OFF:** Fresh conversation without history

**Best for:**
- Remembering past discussions
- Finding old solutions
- Maintaining context across sessions

### 3. Smart Routing

**Auto mode** selects the best model based on:
- Intent detection (coding, general, creative)
- Message complexity
- Provider availability

### 4. Coherence Detection

Experimental feature that scores responses for:
- Logical consistency
- Relevance to query
- Information completeness

### 5. Self-Awareness

FAITHH maintains:
- `faithh_memory.json` - System memory
- `decisions_log.json` - Decision history
- `project_states.json` - Project awareness
- `faithh_knowledge_graph.yaml` - Relationship mapping

---

## Common Tasks

### Task 1: Reindex Conversations

**When:** After exporting new ChatGPT/Claude conversations

```bash
cd ~/ai-stack
source venv/bin/activate

# Extract conversations
python extract_conversations.py

# Reindex to ChromaDB
python scripts/reindex_with_metadata.py

# Verify
curl -s http://192.158.1.243:8000/api/v1/collections/faithh_knowledge_base | jq '.count'
```

### Task 2: Update Project State

**When:** After major changes to projects or infrastructure

```bash
cd ~/ai-stack
python3 scripts/maintenance/update_project_states.py --diff  # Preview
python3 scripts/maintenance/update_project_states.py --write # Apply
```

### Task 3: Check System Health

```bash
# Quick check
./gen8_health_check.sh

# Detailed backend status
curl http://localhost:5557/api/status | jq

# ChromaDB heartbeat
curl http://192.158.1.243:8000/api/v2/heartbeat
```

### Task 4: Add New LLM Provider

1. Edit `backend/llm_providers.py`
2. Add provider class (inherit from `BaseLLMProvider`)
3. Update `faithh_professional_backend_fixed.py` to include it
4. Add API key to `.env`
5. Restart backend

### Task 5: Deploy to Gen8

```bash
# SSH to Gen8
ssh -i ~/.ssh/servicebox_ed25519 jonat@192.158.1.243

# Navigate to service directory
cd ~/services/<service-name>

# Edit docker-compose.yml
nano docker-compose.yml

# Deploy
docker-compose up -d

# Check logs
docker-compose logs -f
```

---

## File Location Guide

### Critical Files (Never Delete)

| File | Purpose | Location |
|------|---------|----------|
| `faithh_professional_backend_fixed.py` | Main backend | ROOT |
| `faithh_pet_v4.html` | UI (canonical) | ROOT |
| `.env` | Configuration | ROOT |
| `project_states.json` | System state | ROOT |
| `faithh_memory.json` | System memory | ROOT |
| `requirements.txt` | Python deps | ROOT |

### Important Directories

| Directory | Purpose |
|-----------|---------|
| `backend/` | Backend modules (12 files) |
| `scripts/` | Utility scripts (135 files) |
| `docs/` | Documentation (204 files) |
| `AI_Chat_Exports/` | Raw conversation exports |
| `knowledge_base/` | Processed RAG data |
| `projects/` | Sub-projects (Tom Cat Sound, Constella) |

### Configuration Files

| File | Purpose |
|------|---------|
| `.env` | Environment variables (API keys, URLs) |
| `config.yaml` | FAITHH configuration |
| `docker-compose.yml` | Local Docker services |
| `requirements.txt` | Python dependencies |

### State Files

| File | Purpose | Format |
|------|---------|--------|
| `project_states.json` | Machine-readable state | JSON |
| `faithh_memory.json` | System memory | JSON |
| `decisions_log.json` | Decision history | JSON |
| `faithh_knowledge_graph.yaml` | Relationships | YAML |
| `pulse_patterns.json` | Pulse security data | JSON |

### Scripts by Category

**Active/Critical:**
- `restart_backend.sh` - Start FAITHH
- `stop_backend.sh` - Stop FAITHH
- `gen8_health_check.sh` - Check Gen8 services
- `scripts/reindex_with_metadata.py` - Reindex RAG

**Maintenance:**
- `scripts/maintenance/update_project_states.py` - Update state
- `scripts/system_health_check.py` - System diagnostics

**RAG:**
- `extract_conversations.py` - Extract from exports
- `index_chromadb_direct.py` - Simple indexing
- `scripts/reindex_with_metadata.py` - Full reindex with metadata

**Gen8 Setup:**
- `setup_gen8_stack.sh` - Deploy Gen8 services
- `setup_grafana_dashboards.py` - Create dashboards
- `configure_gitea.sh` - Configure Gitea

---

## Troubleshooting

### Problem: Backend won't start

**Symptoms:** `./restart_backend.sh` fails

**Solutions:**
```bash
# Check if port 5557 is in use
lsof -i :5557

# Kill existing process
pkill -f faithh_professional_backend

# Check Python environment
source venv/bin/activate
python --version  # Should be 3.x

# Check dependencies
pip install -r requirements.txt

# Check logs
tail -f backend.log
```

### Problem: RAG not working

**Symptoms:** No context from past conversations

**Solutions:**
```bash
# Check ChromaDB connection
curl http://192.158.1.243:8000/api/v2/heartbeat

# Check collection exists
curl http://192.158.1.243:8000/api/v1/collections/faithh_knowledge_base

# Verify document count
curl -s http://localhost:5557/api/status | jq '.services.chromadb.documents'

# Reindex if needed
python scripts/reindex_with_metadata.py
```

### Problem: Gen8 service down

**Symptoms:** `gen8_health_check.sh` shows failures

**Solutions:**
```bash
# SSH to Gen8
ssh -i ~/.ssh/servicebox_ed25519 jonat@192.158.1.243

# Check Docker
docker ps -a

# Restart service
cd ~/services/<service-name>
docker-compose restart

# Check logs
docker-compose logs -f
```

### Problem: LLM provider failing

**Symptoms:** "Provider error" in UI

**Solutions:**
```bash
# Check API keys in .env
cat .env | grep API_KEY

# Test Groq
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY"

# Test Ollama
curl http://localhost:11434/api/tags

# Check backend logs
tail -f backend.log
```

### Problem: UI not loading

**Symptoms:** http://localhost:5557 doesn't work

**Solutions:**
```bash
# Check backend is running
curl http://localhost:5557/health

# Check firewall
sudo ufw status

# Check browser console for errors
# (F12 → Console tab)

# Try different browser
# Clear browser cache
```

---

## Advanced Usage

### Custom Prompts

Edit `faithh_memory.json` to customize system prompts:
```json
{
  "system_prompt": "Your custom instructions here",
  "personality": "professional",
  "response_style": "concise"
}
```

### Adding Custom Models

1. Pull model with Ollama:
```bash
ollama pull <model-name>
```

2. Add to `backend/llm_providers.py`:
```python
OLLAMA_MODELS = {
    "custom-model": "your-model-name"
}
```

3. Update UI model dropdown in `faithh_pet_v4.html`

### Batch RAG Queries

```python
import chromadb

client = chromadb.HttpClient(host='192.158.1.243', port=8000)
collection = client.get_collection('faithh_knowledge_base')

queries = ["topic 1", "topic 2", "topic 3"]
results = collection.query(query_texts=queries, n_results=5)

for i, query in enumerate(queries):
    print(f"\n{query}:")
    for doc in results['documents'][i]:
        print(f"  - {doc[:100]}...")
```

### Monitoring with Grafana

1. Visit: http://192.158.1.243:3000
2. Login: admin / Grafana2026!
3. Dashboards:
   - Gen8 System Overview
   - Docker Services
   - ChromaDB Metrics

### Backup ChromaDB

```bash
# SSH to Gen8
ssh -i ~/.ssh/servicebox_ed25519 jonat@192.158.1.243

# Backup
cd ~/services/chromadb
tar -czf chromadb-backup-$(date +%Y%m%d).tar.gz data/

# Copy to local
scp -i ~/.ssh/servicebox_ed25519 \
  jonat@192.158.1.243:~/services/chromadb/chromadb-backup-*.tar.gz \
  ~/backups/
```

---

## Quick Reference

### Essential Commands

```bash
# Start FAITHH
./restart_backend.sh

# Stop FAITHH
./stop_backend.sh

# Check health
./gen8_health_check.sh

# Reindex RAG
python scripts/reindex_with_metadata.py

# Update state
python3 scripts/maintenance/update_project_states.py --write

# SSH to Gen8
ssh -i ~/.ssh/servicebox_ed25519 jonat@192.158.1.243
```

### Essential URLs

| Service | URL |
|---------|-----|
| FAITHH UI | http://localhost:5557 |
| Backend Status | http://localhost:5557/api/status |
| ChromaDB | http://192.158.1.243:8000 |
| Grafana | http://192.158.1.243:3000 |
| Gitea | http://192.158.1.243:3002 |
| Vaultwarden | http://192.158.1.243:8080 |
| Pi-hole | http://192.158.1.243/admin |

### Key Metrics

- **RAG Chunks:** 32,499
- **Conversations:** 306
- **Gen8 Services:** 12
- **LLM Providers:** 3
- **Backend Port:** 5557
- **ChromaDB Port:** 8000

---

## Getting Help

### Documentation Hierarchy

1. **Start here:** `FAITHH_GUIDE.md` (this file)
2. **Technical details:** `MASTER_CONTEXT.md`
3. **Machine state:** `project_states.json`
4. **Session history:** `docs/session-reports/`
5. **Project audit:** `docs/PROJECT_AUDIT_2026-01-25.md`

### Common Questions

**Q: Which file do I edit for the UI?**  
A: `faithh_pet_v4.html` in the ROOT directory

**Q: Where are my API keys?**  
A: `.env` file in ROOT directory

**Q: How do I add a new conversation export?**  
A: Put in `AI_Chat_Exports/`, then run `extract_conversations.py` and `scripts/reindex_with_metadata.py`

**Q: Can I run FAITHH without Gen8?**  
A: Yes, but you'll lose RAG. Use Ollama for local-only operation.

**Q: How do I update FAITHH?**  
A: `git pull` then `pip install -r requirements.txt` then `./restart_backend.sh`

---

**Last Updated:** 2026-01-25  
**Maintained by:** Jonathan  
**Version:** 2.0 (Post-Reindex)

*For the latest updates, check `project_states.json` and `MASTER_CONTEXT.md`*

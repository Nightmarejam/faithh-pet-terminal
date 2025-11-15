# FAITHH Persistent Memory System Design

## Overview
Give FAITHH continuous memory across sessions by maintaining a "memory file" that gets loaded with every conversation.

## Architecture

### 1. Memory File Structure
```json
{
  "user_profile": {
    "name": "Jonathan",
    "role": "Audio Producer & AI Developer",
    "current_focus": "Building FAITHH AI system",
    "tech_stack": ["Flask", "ChromaDB", "Ollama", "Luna DAW"],
    "preferences": {
      "communication_style": "technical but accessible",
      "documentation": "comprehensive due to ADHD",
      "ui_aesthetic": "MegaMan Battle Network"
    }
  },
  "ongoing_projects": {
    "FAITHH": {
      "status": "active",
      "last_session": "2025-11-14",
      "components": ["backend", "ChromaDB", "UI v3"],
      "next_steps": [
        "Optimize RAG retrieval",
        "Index ChatGPT/Grok exports",
        "Auto-indexing system"
      ]
    }
  },
  "conversation_context": {
    "recent_topics": [
      "RAG system optimization",
      "Conversation chunk indexing",
      "Backend debugging"
    ],
    "unresolved_issues": [
      "Conversation chunks not prioritized in search"
    ],
    "decisions_made": [
      "Use all-mpnet-base-v2 for embeddings",
      "Chunk conversations into 3-4 message segments",
      "Prioritize conversation chunks for dev queries"
    ]
  },
  "knowledge_base": {
    "total_documents": 91604,
    "last_indexed": "2025-11-14",
    "categories": [
      "documentation",
      "claude_conversation_chunk",
      "parity_files"
    ]
  }
}
```

### 2. Implementation

#### Backend Enhancement
```python
# In faithh_professional_backend_fixed.py

import json
from pathlib import Path
from datetime import datetime

MEMORY_FILE = Path.home() / "ai-stack/faithh_memory.json"

def load_memory():
    """Load persistent memory"""
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text())
    return create_default_memory()

def create_default_memory():
    """Initialize memory structure"""
    return {
        "user_profile": {
            "name": "Jonathan",
            "initialized": datetime.now().isoformat()
        },
        "ongoing_projects": {},
        "conversation_context": {
            "recent_topics": [],
            "unresolved_issues": [],
            "decisions_made": []
        },
        "knowledge_base": {}
    }

def update_memory(memory, conversation):
    """Update memory with new conversation"""
    # Add to recent topics
    if "recent_topics" not in memory["conversation_context"]:
        memory["conversation_context"]["recent_topics"] = []
    
    # Extract topics from conversation (simple keyword extraction)
    # In production, use LLM to summarize
    memory["conversation_context"]["recent_topics"].insert(0, {
        "timestamp": datetime.now().isoformat(),
        "query": conversation["query"][:100],
        "resolved": conversation.get("resolved", False)
    })
    
    # Keep only last 20 topics
    memory["conversation_context"]["recent_topics"] = \
        memory["conversation_context"]["recent_topics"][:20]
    
    return memory

def save_memory(memory):
    """Persist memory to disk"""
    MEMORY_FILE.write_text(json.dumps(memory, indent=2))

# In /api/chat endpoint
@app.route('/api/chat', methods=['POST'])
def chat():
    # Load memory
    memory = load_memory()
    
    # Build context with memory
    system_prompt = f"""You are FAITHH, {memory['user_profile']['name']}'s personal AI assistant.

RECENT CONTEXT:
{format_recent_context(memory)}

ONGOING PROJECTS:
{format_projects(memory)}

Use this context to maintain continuity across sessions."""
    
    # ... rest of chat logic ...
    
    # Update memory after response
    memory = update_memory(memory, {
        "query": message,
        "response": reply,
        "timestamp": datetime.now()
    })
    save_memory(memory)
```

---

## Option 3: **Session Continuity via Auto-Index** (Hybrid)
Automatically index every FAITHH conversation into RAG:

### Benefits
- Every conversation becomes searchable
- Natural "memory" through RAG
- No manual memory updates needed

### Implementation
```python
# In backend, after each response:

def save_conversation_to_rag(user_msg, assistant_msg):
    """Auto-index conversation into ChromaDB"""
    
    conversation_text = f"""USER: {user_msg}

FAITHH: {assistant_msg}"""
    
    # Create metadata
    metadata = {
        "source": f"FAITHH Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "category": "faithh_live_session",
        "timestamp": datetime.now().isoformat(),
        "type": "conversation"
    }
    
    # Add to ChromaDB
    doc_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    collection.add(
        ids=[doc_id],
        documents=[conversation_text],
        metadatas=[metadata]
    )
    
    print(f"💾 Saved conversation to RAG: {doc_id}")
```

---

## Option 4: **Hybrid Approach** (RECOMMENDED)

Combine all three:

1. **Persistent Memory File** - Core facts about you and current projects
2. **Auto-Index Sessions** - Every conversation goes into RAG automatically
3. **Enhanced System Prompt** - Personality + instructions to use both

### Why This Works Best
- ✅ Memory file has curated, important info
- ✅ Auto-indexing captures everything organically
- ✅ RAG provides searchable history
- ✅ System prompt ties it all together
- ✅ No manual maintenance needed

---

## Quick Implementation Plan

### Phase 1: Memory File (30 min)
1. Create `faithh_memory.json` with your profile
2. Add load/save functions to backend
3. Include memory in system prompt

### Phase 2: Auto-Index (15 min)
1. Add `save_conversation_to_rag()` function
2. Call after each response
3. Add `faithh_live_session` category filter

### Phase 3: Enhanced Prompt (15 min)
1. Write FAITHH personality description
2. Add memory injection points
3. Test continuity

### Phase 4: Test (15 min)
1. Have conversation about FAITHH backend
2. Close browser
3. Reopen and ask "What were we just talking about?"
4. Should reference previous session!

---

## Example Session Flow

**First Session:**
```
User: "Tell me about my FAITHH project"
FAITHH: [Loads memory.json + RAG]
       "Based on your project files and our past discussions, 
       FAITHH is your personal AI assistant with a MegaMan 
       aesthetic. We've been working on RAG optimization..."
       [Saves conversation to RAG]
```

**Second Session (hours later):**
```
User: "Continue where we left off"
FAITHH: [Loads memory.json + searches RAG for recent sessions]
       "We were optimizing the RAG system! Last time we added
       conversation chunks and fixed the where clause. 
       Ready to tackle auto-indexing next?"
```

---

## Files to Create

1. `faithh_memory.json` - Your persistent profile
2. `scripts/initialize_memory.py` - Setup script
3. Backend updates to use memory
4. Test script to verify continuity

Want me to create these files for you? This would give FAITHH true persistent memory! 🧠

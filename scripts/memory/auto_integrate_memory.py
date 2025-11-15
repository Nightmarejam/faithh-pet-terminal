#!/usr/bin/env python3
"""
Auto-Integrate Persistent Memory System
Automatically patches the backend file with memory functions
"""

from pathlib import Path
import re
import shutil
from datetime import datetime

def backup_backend():
    """Create backup before patching"""
    backend_path = Path.home() / "ai-stack/faithh_professional_backend_fixed.py"
    backup_path = backend_path.with_suffix(f'.py.backup_memory_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    shutil.copy2(backend_path, backup_path)
    print(f"✅ Backup created: {backup_path.name}")
    return backend_path, backup_path

def add_imports(content):
    """Add necessary imports"""
    # Check if Path import already exists
    if "from pathlib import Path" not in content:
        # Find the imports section (before Flask app initialization)
        flask_import = content.find("from flask import")
        if flask_import != -1:
            # Add after flask import
            insert_pos = content.find('\n', flask_import) + 1
            content = content[:insert_pos] + "from pathlib import Path\n" + content[insert_pos:]
            print("✅ Added: from pathlib import Path")
    
    return content

def add_memory_functions(content):
    """Insert memory management functions"""
    
    memory_functions = '''
# ============================================================
# PERSISTENT MEMORY SYSTEM
# ============================================================

MEMORY_FILE = Path.home() / "ai-stack/faithh_memory.json"

def load_memory():
    """Load persistent memory from disk"""
    try:
        if MEMORY_FILE.exists():
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        else:
            print("⚠️  Memory file not found, using defaults")
            return {"user_profile": {"name": "Jonathan"}}
    except Exception as e:
        print(f"❌ Error loading memory: {e}")
        return {"user_profile": {"name": "Jonathan"}}

def save_memory(memory):
    """Persist memory to disk"""
    try:
        memory["last_updated"] = datetime.now().isoformat()
        with open(MEMORY_FILE, 'w') as f:
            json.dump(memory, f, indent=2)
        print(f"💾 Memory saved: {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"❌ Error saving memory: {e}")

def update_recent_topics(memory, query, response_preview):
    """Add conversation to recent topics"""
    if "conversation_context" not in memory:
        memory["conversation_context"] = {"recent_topics": []}
    
    if "recent_topics" not in memory["conversation_context"]:
        memory["conversation_context"]["recent_topics"] = []
    
    topic = {
        "timestamp": datetime.now().isoformat(),
        "query": query[:100],
        "response_preview": response_preview[:100],
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    
    recent = memory["conversation_context"]["recent_topics"]
    recent.insert(0, topic)
    memory["conversation_context"]["recent_topics"] = recent[:50]
    
    return memory

def format_memory_context(memory):
    """Format memory into context string"""
    context_parts = []
    
    if "user_profile" in memory:
        profile = memory["user_profile"]
        context_parts.append(f"USER: {profile.get('name', 'User')}")
        if "role" in profile:
            context_parts.append(f"ROLE: {profile['role']}")
    
    if "ongoing_projects" in memory and "FAITHH" in memory["ongoing_projects"]:
        faithh = memory["ongoing_projects"]["FAITHH"]
        context_parts.append(f"\\nCURRENT PROJECT: {faithh.get('description', 'FAITHH AI system')}")
        if "current_focus" in faithh:
            context_parts.append("CURRENT FOCUS:")
            for focus in faithh["current_focus"][:3]:
                context_parts.append(f"  - {focus}")
    
    if "conversation_context" in memory and "recent_topics" in memory["conversation_context"]:
        recent = memory["conversation_context"]["recent_topics"][:5]
        if recent:
            context_parts.append("\\nRECENT DISCUSSIONS:")
            for topic in recent:
                date = topic.get("date", "unknown")
                query = topic.get("query", "")[:60]
                context_parts.append(f"  [{date}] {query}...")
    
    return "\\n".join(context_parts)

def get_faithh_personality():
    """Return FAITHH's core personality"""
    return """You are FAITHH (Friendly AI Teaching & Helping Hub), Jonathan's personal AI assistant inspired by MegaMan Battle Network NetNavis.

PERSONALITY:
- Encouraging and helpful companion
- Technical but accessible
- Proactive with suggestions
- Remember past conversations
- Enthusiastic about progress

COMMUNICATION:
- Reference past discussions naturally
- Be specific with technical details
- Acknowledge ADHD - provide clear structure
- Celebrate wins
- When uncertain, say so and investigate

You have access to 91,000+ documents including FAITHH documentation, conversation history, and audio production workflows. Always check provided context first."""

'''
    
    # Find where to insert (before first @app.route)
    route_pattern = r'@app\.route\('
    match = re.search(route_pattern, content)
    
    if match:
        insert_pos = match.start()
        content = content[:insert_pos] + memory_functions + "\n" + content[insert_pos:]
        print("✅ Added memory functions")
    else:
        print("⚠️  Could not find @app.route, appending to end")
        content += "\n" + memory_functions
    
    return content

def enhance_chat_endpoint(content):
    """Enhance the /api/chat endpoint with memory"""
    
    # Find the chat endpoint
    chat_pattern = r"@app\.route\('/api/chat', methods=\['POST'\]\)\s*\ndef chat\(\):"
    
    if not re.search(chat_pattern, content):
        print("⚠️  Could not find /api/chat endpoint")
        return content
    
    # Add memory loading at the start of the function
    # Find: "try:" after "def chat():"
    # Add memory loading code after it
    
    memory_init = '''        # LOAD MEMORY
        memory = load_memory()
        memory_context = format_memory_context(memory)
        personality = get_faithh_personality()
'''
    
    # Find the function and insert memory loading
    pattern = r"(def chat\(\):.*?try:\s*\n)"
    replacement = r"\1" + memory_init
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Update system prompt building to include memory
    old_prompt = r'system_prompt = f"""You are FAITHH'
    new_prompt = '''system_prompt = f"""{personality}

{memory_context}

{"=" * 60}
RELEVANT CONTEXT:
{context if context else "No specific context found."}
{"=" * 60}

You are FAITHH'''
    
    if old_prompt in content:
        content = content.replace(old_prompt, new_prompt)
        print("✅ Enhanced system prompt with memory")
    
    # Add memory saving and auto-indexing after response
    save_memory_code = '''
                # UPDATE MEMORY
                memory = update_recent_topics(memory, message, reply)
                if "session_stats" not in memory:
                    memory["session_stats"] = {}
                memory["session_stats"]["total_queries"] = memory["session_stats"].get("total_queries", 0) + 1
                memory["session_stats"]["last_query_date"] = datetime.now().isoformat()
                save_memory(memory)
                
                # AUTO-INDEX THIS CONVERSATION
                try:
                    conversation_text = f"USER: {message}\\n\\nFAITHH: {reply}"
                    doc_id = f"live_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    collection.add(
                        ids=[doc_id],
                        documents=[conversation_text],
                        metadatas=[{
                            "source": f"FAITHH Live Session - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                            "category": "faithh_live_session",
                            "timestamp": datetime.now().isoformat()
                        }]
                    )
                    print(f"💾 Auto-indexed: {doc_id}")
                except Exception as e:
                    print(f"⚠️  Auto-index failed: {e}")
'''
    
    # Find where to insert (after reply is generated, before return)
    pattern = r"(reply = result\.get\('response', ''\)\.strip\(\)\s*\n)"
    replacement = r"\1" + save_memory_code
    content = re.sub(pattern, replacement, content)
    print("✅ Added memory saving and auto-indexing")
    
    return content

def main():
    print("=" * 70)
    print("AUTO-INTEGRATING PERSISTENT MEMORY SYSTEM")
    print("=" * 70)
    print()
    
    # Backup
    backend_path, backup_path = backup_backend()
    
    # Read current content
    content = backend_path.read_text()
    
    # Apply patches
    print("\n🔧 Applying patches...")
    content = add_imports(content)
    content = add_memory_functions(content)
    content = enhance_chat_endpoint(content)
    
    # Write patched version
    backend_path.write_text(content)
    
    print("\n" + "=" * 70)
    print("✅ MEMORY SYSTEM INTEGRATED!")
    print("=" * 70)
    print()
    print("🎯 What changed:")
    print("   1. Added memory load/save functions")
    print("   2. Enhanced system prompt with personality")
    print("   3. Memory context included in every response")
    print("   4. Auto-saves recent topics after each chat")
    print("   5. Auto-indexes conversations into RAG")
    print()
    print("🔄 Restart backend:")
    print("   pkill -f faithh_professional_backend")
    print("   cd ~/ai-stack && source venv/bin/activate")
    print("   nohup python faithh_professional_backend_fixed.py > faithh_backend.log 2>&1 &")
    print()
    print("💡 Test it:")
    print("   Ask: 'What do you know about me?'")
    print("   FAITHH will reference your profile from faithh_memory.json!")
    print()
    print(f"📁 Backup: {backup_path}")
    print("=" * 70)

if __name__ == "__main__":
    main()

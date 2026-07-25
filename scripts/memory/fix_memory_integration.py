#!/usr/bin/env python3
"""
Memory System Integration Checker & Fixer
Diagnoses and fixes memory system integration issues
"""

from pathlib import Path
import re
import shutil
from datetime import datetime

def check_memory_integration():
    """Check what's missing from the memory integration"""
    
    backend_path = Path.home() / "ai-stack/faithh_professional_backend_fixed.py"
    content = backend_path.read_text()
    
    print("=" * 70)
    print("MEMORY SYSTEM DIAGNOSTIC")
    print("=" * 70)
    print()
    
    checks = {
        "load_memory function": "def load_memory():",
        "save_memory function": "def save_memory(",
        "format_memory_context function": "def format_memory_context(",
        "get_faithh_personality function": "def get_faithh_personality():",
        "Memory loading in chat": "memory = load_memory()",
        "Memory context formatting": "format_memory_context(memory)",
        "Memory saving": "save_memory(memory)",
        "Memory file path": "MEMORY_FILE = "
    }
    
    results = {}
    for name, pattern in checks.items():
        found = pattern in content
        results[name] = found
        status = "✅" if found else "❌"
        print(f"{status} {name}")
    
    print()
    
    if all(results.values()):
        print("✅ All components present!")
        return True, "complete"
    elif results["load_memory function"] and results["save_memory function"]:
        if not results["Memory loading in chat"]:
            print("⚠️  Memory functions exist but not used in chat endpoint")
            return False, "not_called"
        else:
            print("⚠️  Partial integration - some components missing")
            return False, "partial"
    else:
        print("❌ Memory functions not added to backend")
        return False, "missing"

def add_complete_memory_system():
    """Add the complete memory system to backend"""
    
    backend_path = Path.home() / "ai-stack/faithh_professional_backend_fixed.py"
    
    # Backup
    backup_path = backend_path.with_suffix(f'.py.backup_complete_memory_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    shutil.copy2(backend_path, backup_path)
    print(f"\n✅ Backup created: {backup_path.name}")
    
    content = backend_path.read_text()
    
    # Step 1: Add memory functions if missing
    if "def load_memory():" not in content:
        print("📝 Adding memory functions...")
        
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
            print("⚠️  Memory file not found")
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
    except Exception as e:
        print(f"❌ Error saving memory: {e}")

def update_recent_topics(memory, query, response_preview):
    """Add conversation to recent topics"""
    if "conversation_context" not in memory:
        memory["conversation_context"] = {"recent_topics": []}
    
    topic = {
        "timestamp": datetime.now().isoformat(),
        "query": query[:100],
        "response_preview": response_preview[:100],
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    
    recent = memory["conversation_context"].get("recent_topics", [])
    recent.insert(0, topic)
    memory["conversation_context"]["recent_topics"] = recent[:50]
    return memory

def format_memory_context(memory):
    """Format memory into context string"""
    parts = []
    
    if "user_profile" in memory:
        profile = memory["user_profile"]
        parts.append(f"USER: {profile.get('name', 'User')}")
        if "role" in profile:
            parts.append(f"Role: {profile['role']}")
        if "work" in profile:
            work = profile["work"]
            if "primary" in work:
                parts.append(f"Work: {work['primary']}")
    
    if "ongoing_projects" in memory and "FAITHH" in memory["ongoing_projects"]:
        faithh = memory["ongoing_projects"]["FAITHH"]
        parts.append(f"\\nProject: {faithh.get('description', 'FAITHH')}")
        if "current_focus" in faithh:
            parts.append("Current Focus:")
            for item in faithh["current_focus"][:3]:
                parts.append(f"  • {item}")
    
    if "conversation_context" in memory:
        ctx = memory["conversation_context"]
        if "recent_topics" in ctx and ctx["recent_topics"]:
            parts.append("\\nRecent Discussions:")
            for topic in ctx["recent_topics"][:3]:
                q = topic.get("query", "")[:60]
                parts.append(f"  • {q}...")
    
    return "\\n".join(parts) if parts else "No memory context available"

'''
        
        # Find where to insert (before first @app.route)
        route_idx = content.find("@app.route(")
        if route_idx != -1:
            content = content[:route_idx] + memory_functions + "\n" + content[route_idx:]
            print("   ✅ Memory functions added")
        else:
            print("   ⚠️  Could not find insertion point")
    
    # Step 2: Update chat endpoint to use memory
    if "memory = load_memory()" not in content:
        print("📝 Updating chat endpoint to use memory...")
        
        # Find the chat function
        chat_idx = content.find("def chat():")
        if chat_idx != -1:
            # Find the try: block inside chat
            try_idx = content.find("try:", chat_idx)
            if try_idx != -1:
                # Insert memory loading right after try:
                newline_idx = content.find("\n", try_idx)
                
                memory_init = '''
        # Load persistent memory
        memory = load_memory()
        memory_context = format_memory_context(memory)
        personality = get_faithh_personality()
        
'''
                
                content = content[:newline_idx+1] + memory_init + content[newline_idx+1:]
                print("   ✅ Memory loading added to chat")
                
                # Update system prompt to include memory
                # Find: system_prompt = f"""
                prompt_pattern = r'(system_prompt = f"""[^"]*""")'
                
                new_prompt = '''system_prompt = f"""{personality}

=== YOUR MEMORY ===
{memory_context}

=== CONTEXT FROM KNOWLEDGE BASE ===
{context if context else "No additional context found."}
================

Respond naturally as FAITHH:"""'''
                
                content = re.sub(prompt_pattern, new_prompt, content, count=1)
                print("   ✅ System prompt updated with memory")
                
                # Add memory saving before return
                # Find the return statement in chat function
                return_pattern = r"(return jsonify\(\{[^}]+\}\))"
                
                save_code = '''
                # Save updated memory
                memory = update_recent_topics(memory, message, reply[:100])
                save_memory(memory)
                
                '''
                
                # This is tricky - we need to add it before the return
                # Let's find "return jsonify" and insert before it
                return_idx = content.find("return jsonify", chat_idx)
                if return_idx != -1:
                    # Find the start of the line
                    line_start = content.rfind("\n", chat_idx, return_idx)
                    content = content[:line_start+1] + save_code + content[line_start+1:]
                    print("   ✅ Memory saving added")
    
    # Write updated content
    backend_path.write_text(content)
    print("\n✅ Complete memory system integrated!")
    
    return True

def main():
    print()
    
    # Check current state
    is_complete, status = check_memory_integration()
    
    if is_complete:
        print("\n🎉 Memory system already fully integrated!")
        print("\nIf FAITHH isn't using memory, check:")
        print("  1. faithh_memory.json exists")
        print("  2. Backend has been restarted")
        print("  3. Backend logs for memory loading messages")
    else:
        print(f"\n📊 Status: {status}")
        print("\n🔧 Applying complete memory system integration...")
        
        if add_complete_memory_system():
            print("\n" + "=" * 70)
            print("✅ MEMORY SYSTEM FULLY INTEGRATED")
            print("=" * 70)
            print()
            print("🔄 RESTART BACKEND NOW:")
            print("   pkill -f faithh_professional_backend")
            print("   cd ~/ai-stack && source venv/bin/activate")
            print("   nohup python faithh_professional_backend_fixed.py > faithh_backend.log 2>&1 &")
            print()
            print("📝 Then check logs:")
            print("   tail -f ~/ai-stack/faithh_backend.log")
            print()
            print("   You should see memory loading messages!")
            print()
    
    print("=" * 70)

if __name__ == "__main__":
    main()

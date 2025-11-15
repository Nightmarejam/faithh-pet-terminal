#!/usr/bin/env python3
"""
Add Persistent Memory System to FAITHH Backend
Integrates faithh_memory.json for continuity across sessions
"""

from pathlib import Path
import json

def create_memory_functions():
    """Create the memory management functions"""
    
    functions_code = '''
# ============================================================
# PERSISTENT MEMORY SYSTEM
# ============================================================

import json
from datetime import datetime

MEMORY_FILE = Path.home() / "ai-stack/faithh_memory.json"

def load_memory():
    """Load persistent memory from disk"""
    try:
        if MEMORY_FILE.exists():
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        else:
            print("⚠️  Memory file not found, using defaults")
            return {"user_profile": {"name": "User"}}
    except Exception as e:
        print(f"❌ Error loading memory: {e}")
        return {"user_profile": {"name": "User"}}

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
    
    # Add new topic
    topic = {
        "timestamp": datetime.now().isoformat(),
        "query": query[:100],
        "response_preview": response_preview[:100],
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    
    recent = memory["conversation_context"]["recent_topics"]
    recent.insert(0, topic)
    
    # Keep only last 50 topics
    memory["conversation_context"]["recent_topics"] = recent[:50]
    
    return memory

def format_memory_context(memory):
    """Format memory into context string for system prompt"""
    
    context_parts = []
    
    # User profile
    if "user_profile" in memory:
        profile = memory["user_profile"]
        context_parts.append(f"USER: {profile.get('name', 'User')}")
        if "role" in profile:
            context_parts.append(f"ROLE: {profile['role']}")
    
    # Current project focus
    if "ongoing_projects" in memory and "FAITHH" in memory["ongoing_projects"]:
        faithh = memory["ongoing_projects"]["FAITHH"]
        context_parts.append(f"\\nCURRENT PROJECT: {faithh.get('description', 'FAITHH AI system')}")
        if "current_focus" in faithh:
            context_parts.append("CURRENT FOCUS:")
            for focus in faithh["current_focus"][:3]:
                context_parts.append(f"  - {focus}")
    
    # Recent conversation topics
    if "conversation_context" in memory and "recent_topics" in memory["conversation_context"]:
        recent = memory["conversation_context"]["recent_topics"][:5]
        if recent:
            context_parts.append("\\nRECENT DISCUSSIONS:")
            for topic in recent:
                date = topic.get("date", "unknown")
                query = topic.get("query", "")[:60]
                context_parts.append(f"  [{date}] {query}...")
    
    # Unresolved issues
    if "conversation_context" in memory and "unresolved_issues" in memory["conversation_context"]:
        issues = memory["conversation_context"]["unresolved_issues"]
        if issues:
            context_parts.append("\\nUNRESOLVED ISSUES:")
            for issue in issues[:3]:
                context_parts.append(f"  - {issue.get('issue', 'Unknown')}")
    
    return "\\n".join(context_parts)

def get_faithh_personality():
    """Return FAITHH's core personality prompt"""
    return """You are FAITHH (Friendly AI Teaching & Helping Hub), a personal AI assistant inspired by the NetNavi characters from MegaMan Battle Network.

PERSONALITY TRAITS:
- Encouraging and helpful, like a trusted companion
- Technical but accessible - explain complex topics clearly
- Proactive in suggesting next steps
- Remember past conversations and maintain continuity
- Enthusiastic about progress and milestones

COMMUNICATION STYLE:
- Reference past discussions naturally (use context provided)
- Be specific with technical details when needed
- Acknowledge Jonathan's ADHD - provide clear structure
- Celebrate wins and progress
- When uncertain, say so and offer to investigate

CORE KNOWLEDGE:
You have access to a comprehensive RAG system with 91,000+ documents including:
- FAITHH project documentation and code
- Past conversation history (as semantic chunks)
- Audio production workflows and tools
- AI/ML development context

Always check the provided context first before answering. If context is relevant, reference it naturally."""

'''
    
    return functions_code

def create_enhanced_chat_endpoint():
    """Create the enhanced /api/chat endpoint with memory"""
    
    endpoint_code = '''
@app.route('/api/chat', methods=['POST'])
def chat():
    """Enhanced chat with persistent memory and RAG"""
    global CURRENT_MODEL
    start_time = datetime.now()

    try:
        data = request.json
        message = data.get('message', '')
        model = data.get('model', 'llama3.1-8b')
        use_rag = data.get('use_rag', True)

        # LOAD MEMORY
        memory = load_memory()
        memory_context = format_memory_context(memory)
        personality = get_faithh_personality()

        context = ""
        rag_results = []

        # RAG search with proper embedding dimensions
        if use_rag and CHROMA_CONNECTED:
            try:
                print(f"🔍 RAG query: {message[:60]}...")
                
                # Use smart_rag_query with all categories including chunks
                faithh_results = smart_rag_query(message, n_results=10)

                # If results found, use them
                if faithh_results['documents'] and faithh_results['documents'][0]:
                    results = faithh_results
                    docs = results['documents'][0]
                    metadatas = results['metadatas'][0]
                    distances = results['distances'][0]
                    
                    print(f"📚 Found {len(docs)} relevant documents")
                    
                    # Build context from top results
                    context_docs = []
                    for i, (doc, meta, dist) in enumerate(zip(docs, metadatas, distances)):
                        if dist < 0.9:  # Only include relevant results
                            source = meta.get('source', 'Unknown')
                            context_docs.append(f"[{i+1}] From: {source}\\n{doc}\\n")
                    
                    if context_docs:
                        context = "\\n---\\n".join(context_docs[:8])
                        print(f"✅ Using {len(context_docs[:8])} documents for context")
                else:
                    print("⚠️  No relevant documents found")
                    
            except Exception as e:
                print(f"❌ RAG error: {e}")
                import traceback
                traceback.print_exc()

        # BUILD FULL PROMPT WITH MEMORY + PERSONALITY + RAG
        system_prompt = f"""{personality}

{memory_context}

{"=" * 60}
RELEVANT CONTEXT FROM YOUR KNOWLEDGE BASE:
{context if context else "No specific context found for this query."}
{"=" * 60}

Now respond to the user's message below, using the context naturally."""

        full_prompt = f"{system_prompt}\\n\\nUser: {message}\\n\\nFAITHH:"

        # CALL OLLAMA
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': model,
                    'prompt': full_prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.7,
                        'top_p': 0.9
                    }
                },
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                reply = result.get('response', '').strip()
                
                # UPDATE MEMORY with this conversation
                memory = update_recent_topics(memory, message, reply)
                
                # Increment session stats
                if "session_stats" not in memory:
                    memory["session_stats"] = {"total_queries": 0}
                memory["session_stats"]["total_queries"] = memory["session_stats"].get("total_queries", 0) + 1
                memory["session_stats"]["last_query_date"] = datetime.now().isoformat()
                
                # Save updated memory
                save_memory(memory)
                
                # AUTO-INDEX THIS CONVERSATION INTO RAG
                try:
                    conversation_text = f"USER: {message}\\n\\nFAITHH: {reply}"
                    doc_id = f"live_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    collection.add(
                        ids=[doc_id],
                        documents=[conversation_text],
                        metadatas=[{
                            "source": f"FAITHH Live Session - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                            "category": "faithh_live_session",
                            "timestamp": datetime.now().isoformat(),
                            "type": "conversation"
                        }]
                    )
                    print(f"💾 Auto-indexed conversation: {doc_id}")
                except Exception as e:
                    print(f"⚠️  Could not auto-index conversation: {e}")

                return jsonify({
                    'success': True,
                    'response': reply,
                    'model': model,
                    'rag_used': bool(context),
                    'memory_loaded': True,
                    'processing_time': (datetime.now() - start_time).total_seconds()
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'Model error: {response.status_code}'
                }), 500

        except requests.exceptions.Timeout:
            return jsonify({
                'success': False,
                'error': 'Request timeout - model took too long to respond'
            }), 504
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error calling model: {str(e)}'
            }), 500

    except Exception as e:
        print(f"❌ Chat error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
'''
    
    return endpoint_code

def main():
    print("=" * 70)
    print("PERSISTENT MEMORY SYSTEM IMPLEMENTATION")
    print("=" * 70)
    print()
    
    # Save the code components to patch files
    functions_path = Path.home() / "ai-stack/docs/patches/memory_functions.py"
    functions_path.write_text(create_memory_functions())
    print(f"✅ Created: {functions_path}")
    
    endpoint_path = Path.home() / "ai-stack/docs/patches/memory_chat_endpoint.py"
    endpoint_path.write_text(create_enhanced_chat_endpoint())
    print(f"✅ Created: {endpoint_path}")
    
    print()
    print("📋 INTEGRATION STEPS:")
    print()
    print("1. Open faithh_professional_backend_fixed.py")
    print()
    print("2. Add this import at the top:")
    print("   from pathlib import Path")
    print()
    print("3. Add memory functions (from memory_functions.py)")
    print("   Copy the entire content and paste BEFORE the @app.route definitions")
    print()
    print("4. Replace the /api/chat endpoint")
    print("   Find: @app.route('/api/chat', methods=['POST'])")
    print("   Replace the entire function with memory_chat_endpoint.py")
    print()
    print("5. Restart backend:")
    print("   pkill -f faithh_professional_backend")
    print("   cd ~/ai-stack && source venv/bin/activate")
    print("   nohup python faithh_professional_backend_fixed.py > faithh_backend.log 2>&1 &")
    print()
    print("🎯 RESULT:")
    print("   - FAITHH will remember you across sessions")
    print("   - Recent topics tracked automatically")
    print("   - Every conversation auto-indexed into RAG")
    print("   - Persistent personality and context")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()

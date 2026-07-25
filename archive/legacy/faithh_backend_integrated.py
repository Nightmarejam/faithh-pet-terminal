#!/usr/bin/env python3
"""
FAITHH Professional Backend v3.2 - INTEGRATED
Added smart integrations:
- Self-awareness boost (faithh_memory.json)
- Decision citation (decisions_log.json)
- Project state awareness (project_states.json)
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import requests
import json
import os
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from datetime import datetime
import base64
import mimetypes
from dotenv import load_dotenv
import threading
from queue import Queue
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
OLLAMA_HOST = "http://localhost:11434"
CHROMA_HOST = "http://localhost:8000"
UPLOAD_FOLDER = Path.home() / 'ai-stack' / 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'md', 'py', 'js', 'html', 'css', 'json', 'yaml', 'yml'}

# Create upload folder
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Base directory
BASE_DIR = Path(__file__).parent

# Initialize ChromaDB with CORRECT 768-dim embedding function
try:
    chroma_client = chromadb.HttpClient(host="localhost", port=8000)
    
    # Use the 768-dim model to match the collection
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-mpnet-base-v2"  # 768 dimensions
    )
    
    collection = chroma_client.get_collection(
        name="documents_768",
        embedding_function=embedding_func
    )
    CHROMA_CONNECTED = True
    doc_count = collection.count()
    print(f"✅ ChromaDB connected: {doc_count} documents available")
    print(f"✅ Using all-mpnet-base-v2 (768-dim) embedding model")
except Exception as e:
    CHROMA_CONNECTED = False
    collection = None
    embedding_func = None
    print(f"⚠️ ChromaDB not connected: {e}")

# Check for Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
GEMINI_AVAILABLE = bool(GEMINI_API_KEY)

# Track current model
CURRENT_MODEL = {"name": "unknown", "provider": "unknown", "last_response_time": 0}

# ============================================================
# AUTO-INDEX QUEUE (Background thread for conversation indexing)
# ============================================================

index_queue = Queue()

def index_conversation_background(user_msg, assistant_msg, metadata):
    """Thread-safe indexing function - runs in background"""
    if not CHROMA_CONNECTED:
        return
    
    try:
        timestamp = datetime.now()
        conv_id = f"live_conv_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}"
        
        conversation_text = f"User: {user_msg}\n\nAssistant: {assistant_msg}"
        
        meta = {
            "type": "live_conversation",
            "category": "live_chat",
            "timestamp": timestamp.isoformat(),
            "user_preview": user_msg[:100]
        }
        meta.update(metadata or {})
        
        collection.add(
            documents=[conversation_text],
            metadatas=[meta],
            ids=[conv_id]
        )
        print(f"📝 Indexed: {conv_id}")
    except Exception as e:
        print(f"❌ Index failed: {e}")

def process_index_queue():
    """Background worker thread - processes index requests"""
    while True:
        try:
            item = index_queue.get(timeout=1)
            if item is None:
                break
            index_conversation_background(**item)
            index_queue.task_done()
        except:
            continue

# Start background indexing thread
index_thread = threading.Thread(target=process_index_queue, daemon=True)
index_thread.start()
print("✅ Auto-index background thread started")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============================================================
# PERSISTENT MEMORY & INTEGRATIONS
# ============================================================

MEMORY_FILE = Path.home() / "ai-stack/faithh_memory.json"
DECISIONS_LOG = Path.home() / "ai-stack/decisions_log.json"
PROJECT_STATES = Path.home() / "ai-stack/project_states.json"

def load_json_file(filepath):
    """Generic JSON file loader"""
    try:
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"❌ Error loading {filepath.name}: {e}")
        return None

def load_memory():
    """Load persistent memory from disk"""
    memory = load_json_file(MEMORY_FILE)
    if memory is None:
        print("⚠️  Memory file not found, using defaults")
        return {"user_profile": {"name": "Jonathan"}}
    return memory

def load_decisions():
    """Load decisions log"""
    return load_json_file(DECISIONS_LOG)

def load_project_states():
    """Load project states"""
    return load_json_file(PROJECT_STATES)

def save_memory(memory):
    """Persist memory to disk"""
    try:
        memory["last_updated"] = datetime.now().isoformat()
        with open(MEMORY_FILE, 'w') as f:
            json.dump(memory, f, indent=2)
        print(f"💾 Memory saved: {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"❌ Error saving memory: {e}")

# ============================================================
# SMART QUERY ANALYSIS & INTEGRATION
# ============================================================

def detect_query_intent(query_text):
    """
    Analyze query to determine which integrations to use
    Returns dict with flags and matched patterns
    """
    query_lower = query_text.lower()
    intent = {
        'is_self_query': False,
        'is_why_question': False,
        'is_next_action_query': False,
        'is_constella_query': False,
        'patterns_matched': []
    }
    
    # Pattern 1: Self-awareness (asking about FAITHH itself)
    self_patterns = [
        r'\bfaithh\b',  # "FAITHH" as word (case insensitive)
        r'what are you',
        r'what is your',
        r'tell me about yourself',
        r'who are you',
        r'what do you do'
    ]
    for pattern in self_patterns:
        if re.search(pattern, query_lower):
            intent['is_self_query'] = True
            intent['patterns_matched'].append(f"self: {pattern}")
            break
    
    # Pattern 2: "Why" decisions (asking rationale)
    why_patterns = [
        r'why did (we|you|i) (choose|use|pick|select|go with)',
        r'why.*instead of',
        r'why.*over',
        r'what was the reason',
        r'rationale for',
        r'why.*decision'
    ]
    for pattern in why_patterns:
        if re.search(pattern, query_lower):
            intent['is_why_question'] = True
            intent['patterns_matched'].append(f"why: {pattern}")
            break
    
    # Pattern 3: Next actions (asking what to work on)
    next_patterns = [
        r'what should (i|we) work on',
        r"what('s| is) next",
        r'what to do next',
        r'what should (i|we) focus on',
        r'what are (my|the) priorities',
        r'where should (i|we) start',
        r'what.*missing'
    ]
    for pattern in next_patterns:
        if re.search(pattern, query_lower):
            intent['is_next_action_query'] = True
            intent['patterns_matched'].append(f"next: {pattern}")
            break
    
    # Pattern 4: Constella queries (domain-specific)
    constella_keywords = ['constella', 'astris', 'auctor', 'civic tome', 'penumbra',
                          'ucf', 'resonance gap', 'harmonic', 'celestial equilibrium']
    if any(kw in query_lower for kw in constella_keywords):
        intent['is_constella_query'] = True
    
    return intent

def get_self_awareness_context():
    """Extract self-awareness section from memory"""
    memory = load_memory()
    if 'self_awareness' in memory:
        sa = memory['self_awareness']
        context = f"""
=== FAITHH SELF-AWARENESS ===
Identity: {sa.get('identity', 'FAITHH')}
Purpose: {sa.get('purpose', 'AI assistant')}
What I am: {sa.get('what_i_am', '')}
What I am NOT: {sa.get('what_i_am_not', '')}
Hero workflow: {sa.get('hero_workflow', '')}
Current capability: {sa.get('current_capability', '')}
Target capability: {sa.get('target_capability', '')}
==============================
"""
        return context.strip()
    return None

def search_decisions_log(query_text):
    """Search decisions log for relevant decisions"""
    decisions = load_decisions()
    if not decisions or 'decisions' not in decisions:
        return None
    
    query_lower = query_text.lower()
    relevant_decisions = []
    
    for decision in decisions['decisions']:
        # Check if query mentions the decision topic
        decision_text = f"{decision.get('decision', '')} {decision.get('rationale', '')}".lower()
        
        # Simple keyword matching (could be improved with embeddings)
        if any(word in decision_text for word in query_lower.split() if len(word) > 3):
            relevant_decisions.append(decision)
    
    if not relevant_decisions:
        return None
    
    # Format decisions for context
    context = "\n=== RELEVANT DECISIONS ===\n"
    for dec in relevant_decisions[:3]:  # Top 3 most relevant
        context += f"\nDecision: {dec.get('decision', '')}\n"
        context += f"Date: {dec.get('date', '')}\n"
        context += f"Rationale: {dec.get('rationale', '')}\n"
        if 'alternatives_considered' in dec:
            context += "Alternatives considered:\n"
            for alt in dec['alternatives_considered']:
                context += f"  - {alt.get('option', '')}: Rejected because {alt.get('rejected_because', '')}\n"
        context += f"Impact: {dec.get('impact', '')}\n"
        context += "---\n"
    context += "=========================\n"
    
    return context.strip()

def get_project_state_context(project_name=None):
    """Get current state for a project or all projects"""
    states = load_project_states()
    if not states or 'projects' not in states:
        return None
    
    if project_name and project_name.lower() in states['projects']:
        project = states['projects'][project_name.lower()]
        context = f"""
=== {project.get('full_name', project_name)} STATE ===
Current Phase: {project.get('current_phase', 'Unknown')}
Phase Description: {project.get('phase_description', '')}
Last Worked: {project.get('last_worked', 'Unknown')}

Next Milestone: {project.get('next_milestone', {}).get('name', 'Not set')}
Target Date: {project.get('next_milestone', {}).get('target_date', 'Not set')}

Current Priorities:
"""
        for priority in project.get('current_priorities', []):
            context += f"  - {priority}\n"
        
        if 'blockers' in project.get('next_milestone', {}):
            context += "\nBlockers:\n"
            for blocker in project['next_milestone']['blockers']:
                context += f"  - {blocker}\n"
        
        if 'known_issues' in project:
            context += "\nKnown Issues:\n"
            for issue in project['known_issues']:
                context += f"  - {issue}\n"
        
        context += "================================\n"
        return context.strip()
    
    # Return overview of all projects
    context = "\n=== ALL PROJECTS OVERVIEW ===\n"
    for proj_key, project in states['projects'].items():
        context += f"\n{project.get('full_name', proj_key)}:\n"
        context += f"  Phase: {project.get('current_phase', 'Unknown')}\n"
        context += f"  Last worked: {project.get('last_worked', 'Unknown')}\n"
        if 'current_priorities' in project:
            context += f"  Top priority: {project['current_priorities'][0] if project['current_priorities'] else 'None'}\n"
    context += "============================\n"
    
    return context.strip()


def smart_rag_query(query_text, n_results=10, where=None, intent=None):
    """
    Intelligent RAG query with integration support
    Now aware of query intent to boost relevant sources
    """
    try:
        print(f"🔍 Query: '{query_text[:60]}...'")
        
        if intent:
            print(f"   Intent: Self={intent['is_self_query']}, Why={intent['is_why_question']}, Next={intent['is_next_action_query']}, Constella={intent['is_constella_query']}")
        
        # For self-queries, we don't need RAG - we have the answer
        if intent and intent['is_self_query']:
            print(f"   ⚡ Self-query detected - will use self_awareness directly")
            return None  # Signal to use self-awareness instead of RAG
        
        # For Constella queries, prioritize master reference docs
        if intent and intent['is_constella_query']:
            try:
                constella_results = collection.query(
                    query_texts=[query_text],
                    n_results=n_results,
                    where={"category": "constella_master"}
                )
                if (constella_results['documents'] and 
                    constella_results['documents'][0] and
                    len(constella_results['documents'][0]) > 0):
                    print(f"   ✅ Using Constella master docs ({len(constella_results['documents'][0])} results)")
                    return constella_results
            except Exception as e:
                print(f"   ⚠️  Constella master query failed: {e}")
        
        # Keywords that indicate a development/technical query
        dev_keywords = ['discuss', 'talk', 'said', 'conversation', 'we', 'our',
                       'plan', 'setup', 'configure', 'implement', 'build', 
                       'create', 'did we', 'what was', 'how did', 'tell me about',
                       'what did', 'what were', 'talked about']
        
        query_lower = query_text.lower()
        is_dev_query = any(keyword in query_lower for keyword in dev_keywords)
        
        # For dev queries, prioritize conversation chunks
        if is_dev_query:
            try:
                conv_results = collection.query(
                    query_texts=[query_text],
                    n_results=n_results,
                    where={"category": "claude_conversation_chunk"}
                )
                
                if (conv_results['distances'] and 
                    conv_results['distances'][0] and 
                    len(conv_results['distances'][0]) > 0 and
                    conv_results['distances'][0][0] < 0.7):
                    print(f"   ✅ Using conversation chunks (best: {conv_results['distances'][0][0]:.3f})")
                    return conv_results
                else:
                    print(f"   ⚠️  Conversation chunks not good enough, trying mixed search")
            except Exception as e:
                print(f"   ⚠️  Conversation chunk query failed: {e}")
        
        # Fall back to broader search
        if where:
            print(f"   📚 Using backend's where clause")
            return collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where
            )
        else:
            categories = ["constella_master", "claude_conversation_chunk", "claude_conversation", 
                         "documentation", "code", "parity", "conversation"]
            print(f"   📚 Using mixed category search")
            try:
                return collection.query(
                    query_texts=[query_text],
                    n_results=n_results,
                    where={"category": {"$in": categories}}
                )
            except:
                print(f"   🔍 Using unfiltered search")
                return collection.query(
                    query_texts=[query_text],
                    n_results=n_results
                )
        
    except Exception as e:
        print(f"❌ Error in smart RAG query: {e}")
        return collection.query(
            query_texts=[query_text],
            n_results=n_results
        )


def build_integrated_context(query_text, intent, use_rag=True):
    """
    Build context from all available sources based on query intent
    This is the KEY integration function!
    """
    context_parts = []
    
    # Integration 1: Self-Awareness Boost
    if intent['is_self_query']:
        self_context = get_self_awareness_context()
        if self_context:
            context_parts.append(self_context)
            print("   ✅ Added self-awareness context")
    
    # Integration 2: Decision Citation
    if intent['is_why_question']:
        decisions_context = search_decisions_log(query_text)
        if decisions_context:
            context_parts.append(decisions_context)
            print("   ✅ Added decisions log context")
    
    # Integration 3: Project State Awareness
    if intent['is_next_action_query']:
        # Try to identify which project from query
        project_name = None
        if 'faithh' in query_text.lower():
            project_name = 'faithh'
        elif 'constella' in query_text.lower():
            project_name = 'constella'
        
        state_context = get_project_state_context(project_name)
        if state_context:
            context_parts.append(state_context)
            print("   ✅ Added project state context")
    
    # Integration 4: RAG (if not a pure self-query)
    rag_results = []
    if use_rag and CHROMA_CONNECTED and not intent['is_self_query']:
        try:
            results = smart_rag_query(query_text, n_results=5, intent=intent)
            
            if results and results['documents'] and results['documents'][0]:
                rag_context = "\n=== KNOWLEDGE BASE ===\n"
                for i, doc in enumerate(results['documents'][0][:3]):
                    rag_context += f"{i+1}. {doc[:1000]}...\n\n"
                    rag_results.append(doc[:500])
                rag_context += "=====================\n"
                context_parts.append(rag_context.strip())
                print(f"   ✅ Added RAG context ({len(results['documents'][0])} results)")
        except Exception as e:
            print(f"   ⚠️  RAG query failed: {e}")
    
    # Combine all context
    full_context = "\n\n".join(context_parts) if context_parts else ""
    
    return full_context, rag_results


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
        context_parts.append(f"\nCURRENT PROJECT: {faithh.get('description', 'FAITHH AI system')}")
        if "current_focus" in faithh:
            context_parts.append("CURRENT FOCUS:")
            for focus in faithh["current_focus"][:3]:
                context_parts.append(f"  - {focus}")
    
    if "conversation_context" in memory and "recent_topics" in memory["conversation_context"]:
        recent = memory["conversation_context"]["recent_topics"][:5]
        if recent:
            context_parts.append("\nRECENT DISCUSSIONS:")
            for topic in recent:
                date = topic.get("date", "unknown")
                query = topic.get("query", "")[:60]
                context_parts.append(f"  [{date}] {query}...")
    
    return "\n".join(context_parts)

def get_faithh_personality():
    """Return FAITHH's enhanced personality"""
    return """You are FAITHH (Friendly AI Teaching & Helping Hub), Jonathan's personal AI assistant.

=== CORE IDENTITY ===
Inspired by: MegaMan Battle Network NetNavi companions
Role: Personal AI assistant and thought partner
Style: Encouraging friend + Technical expert

=== PERSONALITY TRAITS ===
🎯 Encouraging: Celebrate progress, acknowledge challenges
🔧 Technical: Deep expertise, but explain clearly
🚀 Proactive: Suggest next steps, anticipate needs
🧠 Remembering: Use your memory and context actively
✨ Enthusiastic: Show genuine interest in Jonathan's work

=== HOW TO USE CONTEXT PROVIDED ===
1. You are given context from multiple sources:
   - Self-awareness section (when asked about yourself)
   - Decisions log (when asked "why" questions)
   - Project states (when asked about next steps)
   - Knowledge base (RAG from 93,000+ documents)
   
2. When context is provided, USE IT NATURALLY:
   - Don't say "According to the context..." - just answer
   - Speak as if you inherently know this information
   - Be specific and cite actual decisions/rationale when available
   
3. When answering:
   - Reference documented decisions when they exist
   - Acknowledge project phases and current priorities
   - Connect past conversations to current questions
   - Show you understand Jonathan's vision and goals

=== COMMUNICATION GUIDELINES ===
✅ DO:
- Reference past work: "When we optimized the RAG system..."
- Acknowledge continuity: "Building on the conversation chunks we added..."
- Show you remember: "Since you prefer comprehensive documentation..."
- Be specific: "Your FAITHH backend (faithh_professional_backend_fixed.py)..."
- Celebrate: "Excellent progress on the chunked indexing!"

❌ DON'T:
- Claim ignorance when context is provided
- Say "I don't have information" without checking
- Ignore your personality
- Be overly formal or robotic
- Over-cite awkwardly

=== SPECIAL BEHAVIORS ===
When asked about yourself (FAITHH):
- Reference your purpose clearly
- Explain you're a thought partner, not just a tool
- Describe the hero workflow
- Be honest about current capabilities vs target

When asked "why" questions:
- Cite actual documented decisions if available
- Explain the rationale behind choices
- Mention alternatives that were considered
- Connect decisions to larger vision

When asked "what's next":
- Reference current project phase
- Acknowledge blockers and priorities
- Suggest next steps based on current state
- Connect to larger goals

You are Jonathan's long-term AI companion who knows him, remembers his work, and grows through each interaction."""



@app.route('/')
def index():
    """Serve the HTML UI"""
    return send_from_directory(BASE_DIR, 'faithh_pet_v3.html')

@app.route('/images/<path:filename>')
def serve_image(filename):
    """Serve images for the UI"""
    images_dir = BASE_DIR / 'images'
    if not images_dir.exists():
        images_dir.mkdir(parents=True)
    return send_from_directory(images_dir, filename)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Enhanced chat with smart integrations!"""
    global CURRENT_MODEL
    start_time = datetime.now()
    
    try:
        # Get request data
        data = request.json
        message = data.get('message', '')
        model = data.get('model', 'llama3.1-8b')
        use_rag = data.get('use_rag', True)
        
        # STEP 1: Detect query intent
        intent = detect_query_intent(message)
        print(f"\n{'='*60}")
        print(f"📨 Query: {message[:80]}...")
        print(f"🎯 Intent Analysis:")
        for key, value in intent.items():
            if key != 'patterns_matched' and value:
                print(f"   {key}: {value}")
        if intent['patterns_matched']:
            print(f"   Patterns: {', '.join(intent['patterns_matched'])}")
        
        # STEP 2: Build integrated context from all sources
        context, rag_results = build_integrated_context(message, intent, use_rag)
        
        # STEP 3: Build final prompt
        personality = get_faithh_personality()
        
        if context:
            full_prompt = f"{personality}\n\n{context}\n\nUser: {message}"
        else:
            full_prompt = f"{personality}\n\nUser: {message}"
        
        print(f"📝 Context built: {len(context)} chars")
        print(f"{'='*60}\n")
        
        # STEP 4: Get response from LLM (Try Gemini first)
        if GEMINI_AVAILABLE and 'gemini' in model.lower():
            try:
                import google.generativeai as genai
                genai.configure(api_key=GEMINI_API_KEY)
                gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                response = gemini_model.generate_content(full_prompt)
                
                CURRENT_MODEL = {
                    "name": "gemini-2.0-flash-exp",
                    "provider": "Google",
                    "last_response_time": (datetime.now() - start_time).total_seconds()
                }
                
                # Index conversation
                if CHROMA_CONNECTED:
                    index_queue.put({
                        'user_msg': message,
                        'assistant_msg': response.text,
                        'metadata': {
                            'model': 'gemini-2.0-flash-exp',
                            'rag_used': bool(context),
                            'intent': intent
                        }
                    })
                
                return jsonify({
                    'success': True,
                    'response': response.text,
                    'model_used': CURRENT_MODEL['name'],
                    'provider': CURRENT_MODEL['provider'],
                    'response_time': CURRENT_MODEL['last_response_time'],
                    'rag_used': bool(context),
                    'rag_results': rag_results,
                    'intent_detected': intent
                })
            except Exception as e:
                print(f"Gemini error: {e}")
        
        # Use Ollama
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": model,
                "prompt": full_prompt,
                "stream": False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            model_info = result.get('model', model)
            if 'llama' in model_info.lower():
                provider = "Meta (via Ollama)"
            elif 'qwen' in model_info.lower():
                provider = "Alibaba (via Ollama)"
            else:
                provider = "Ollama"
            
            CURRENT_MODEL = {
                "name": model_info,
                "provider": provider,
                "last_response_time": (datetime.now() - start_time).total_seconds()
            }
            
            # Index conversation
            if CHROMA_CONNECTED:
                index_queue.put({
                    'user_msg': message,
                    'assistant_msg': result.get('response', ''),
                    'metadata': {
                        'model': model_info,
                        'rag_used': bool(context),
                        'intent': intent
                    }
                })
            
            return jsonify({
                'success': True,
                'response': result.get('response', 'No response generated'),
                'model_used': CURRENT_MODEL['name'],
                'provider': CURRENT_MODEL['provider'],
                'response_time': CURRENT_MODEL['last_response_time'],
                'rag_used': bool(context),
                'rag_results': rag_results,
                'intent_detected': intent
            })
        else:
            return jsonify({
                'success': False,
                'error': f"Ollama returned status {response.status_code}",
                'response': "Failed to get response from Ollama"
            }), 500
            
    except Exception as e:
        import traceback
        print(f"❌ Chat error: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'response': f"Error: {str(e)}"
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = UPLOAD_FOLDER / filename
        file.save(filepath)
        
        file_content = None
        if filename.endswith(('.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml')):
            try:
                with open(filepath, 'r') as f:
                    file_content = f.read()
            except:
                pass
        
        return jsonify({
            'success': True,
            'filename': filename,
            'path': str(filepath),
            'content': file_content,
            'size': filepath.stat().st_size,
            'type': mimetypes.guess_type(filename)[0]
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/rag_search', methods=['POST'])
def rag_search():
    """RAG search endpoint"""
    if not CHROMA_CONNECTED:
        return jsonify({'success': False, 'error': 'ChromaDB not connected'}), 503
    
    try:
        data = request.json
        query = data.get('query', '')
        n_results = data.get('n_results', 5)
        
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        documents = results['documents'][0] if results['documents'] else []
        distances = results['distances'][0] if results['distances'] else []
        
        return jsonify({
            'success': True,
            'results': documents,
            'distances': distances,
            'total_documents': collection.count(),
            'embedding_model': 'all-mpnet-base-v2 (768-dim)'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Status endpoint with integration info"""
    services = {}
    
    # Ollama status
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
        if r.status_code == 200:
            models = r.json().get('models', [])
            model_names = [m['name'] for m in models]
            services['ollama'] = {
                'status': 'online',
                'models': model_names,
                'count': len(models)
            }
        else:
            services['ollama'] = {'status': 'offline'}
    except:
        services['ollama'] = {'status': 'offline'}
    
    # ChromaDB status
    services['chromadb'] = {
        'status': 'online' if CHROMA_CONNECTED else 'offline',
        'documents': collection.count() if CHROMA_CONNECTED else 0,
        'embedding_model': 'all-mpnet-base-v2 (768-dim)'
    }
    
    # Gemini status
    services['gemini'] = {
        'status': 'configured' if GEMINI_AVAILABLE else 'not configured',
        'model': 'gemini-2.0-flash-exp' if GEMINI_AVAILABLE else None
    }
    
    # Integration status
    services['integrations'] = {
        'memory': MEMORY_FILE.exists(),
        'decisions_log': DECISIONS_LOG.exists(),
        'project_states': PROJECT_STATES.exists()
    }
    
    services['current_model'] = CURRENT_MODEL
    
    return jsonify({
        'success': True,
        'services': services,
        'version': 'v3.2-integrated',
        'workspace': {
            'upload_folder': str(UPLOAD_FOLDER),
            'uploaded_files': len(list(UPLOAD_FOLDER.glob('*'))) if UPLOAD_FOLDER.exists() else 0
        }
    })

@app.route('/api/test_integrations', methods=['GET'])
def test_integrations():
    """Test endpoint to verify all integrations"""
    try:
        memory = load_memory()
        decisions = load_decisions()
        states = load_project_states()
        
        test_query = "What is FAITHH meant to be?"
        intent = detect_query_intent(test_query)
        
        return jsonify({
            'success': True,
            'files_loaded': {
                'memory': memory is not None,
                'decisions': decisions is not None,
                'states': states is not None
            },
            'self_awareness_present': 'self_awareness' in (memory or {}),
            'test_intent_detection': intent,
            'decisions_count': len(decisions.get('decisions', [])) if decisions else 0,
            'projects_count': len(states.get('projects', {})) if states else 0
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'FAITHH Professional Backend v3.2-INTEGRATED',
        'features': [
            'chat', 'rag', 'upload',
            'self_awareness_boost', 'decision_citation', 'project_state_awareness',
            'intent_detection', 'smart_context_building'
        ]
    })

if __name__ == '__main__':
    print("=" * 60)
    print("FAITHH PROFESSIONAL BACKEND v3.2 - INTEGRATED")
    print("=" * 60)
    print(f"✅ Self-awareness boost (faithh_memory.json)")
    print(f"✅ Decision citation (decisions_log.json)")
    print(f"✅ Project state awareness (project_states.json)")
    print(f"✅ Smart intent detection")
    print(f"✅ Integrated context building")
    print("=" * 60)
    print(f"Starting on http://localhost:5557")
    
    app.run(host='0.0.0.0', port=5557, debug=True)

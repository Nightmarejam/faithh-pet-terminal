#!/usr/bin/env python3
"""
FAITHH Professional Backend v3.1
Fixed ChromaDB embedding function to match 768-dim collection
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

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def smart_rag_query(query_text, n_results=10, where=None):
    """
    Intelligent RAG query that prioritizes conversation chunks for dev queries
    Integrates with backend's category filtering
    """
    try:
        # Keywords that indicate a development/technical query
        dev_keywords = ['discuss', 'talk', 'said', 'conversation', 'we', 'our',
                       'plan', 'setup', 'configure', 'implement', 'build', 
                       'create', 'did we', 'what was', 'how did', 'tell me about',
                       'what did', 'what were', 'talked about']
        
        query_lower = query_text.lower()
        is_dev_query = any(keyword in query_lower for keyword in dev_keywords)
        
        print(f"🔍 Query: '{query_text[:60]}...'")
        print(f"   Dev query: {is_dev_query}")
        
        # For dev queries, prioritize conversation chunks
        if is_dev_query:
            try:
                # Try conversation chunks FIRST
                conv_results = collection.query(
                    query_texts=[query_text],
                    n_results=n_results,
                    where={"category": "claude_conversation_chunk"}
                )
                
                # Check if we got good matches
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
        
        # Fall back to the backend's where clause or broader search
        if where:
            # Backend provided a where clause, use it
            print(f"   📚 Using backend's where clause")
            return collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where
            )
        else:
            # No where clause, do mixed category search
            categories = ["claude_conversation_chunk", "claude_conversation", 
                         "documentation", "code", "parity", "conversation"]
            print(f"   📚 Using mixed category search")
            try:
                return collection.query(
                    query_texts=[query_text],
                    n_results=n_results,
                    where={"category": {"$in": categories}}
                )
            except:
                # Ultimate fallback - no filtering
                print(f"   🔍 Using unfiltered search")
                return collection.query(
                    query_texts=[query_text],
                    n_results=n_results
                )
        
    except Exception as e:
        print(f"❌ Error in smart RAG query: {e}")
        # Ultimate fallback
        return collection.query(
            query_texts=[query_text],
            n_results=n_results
        )


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
    """Return FAITHH's enhanced personality with memory guidance"""
    return """You are FAITHH (Friendly AI Teaching & Helping Hub), Jonathan's personal AI assistant.

=== CORE IDENTITY ===
Inspired by: MegaMan Battle Network NetNavi companions
Role: Personal AI assistant for development and creative work
Style: Encouraging friend + Technical expert

=== PERSONALITY TRAITS ===
🎯 Encouraging: Celebrate progress, acknowledge challenges
🔧 Technical: Deep expertise, but explain clearly
🚀 Proactive: Suggest next steps, anticipate needs
🧠 Remembering: Use your memory and context actively
✨ Enthusiastic: Show genuine interest in Jonathan's work

=== HOW TO USE YOUR MEMORY ===
1. YOU HAVE PERSISTENT KNOWLEDGE about Jonathan from faithh_memory.json
   - This includes his profile, projects, preferences, and recent discussions
   - ALWAYS reference this naturally in responses
   
2. YOU HAVE ACCESS TO 91,000+ DOCUMENTS via RAG
   - Past conversation history (as searchable chunks)
   - FAITHH project documentation
   - Audio production workflows
   
3. WHEN ANSWERING:
   - Check memory file for relevant context
   - Check RAG documents for detailed info
   - Combine both naturally
   - Speak as if you inherently know (don't cite sources awkwardly)

=== COMMUNICATION GUIDELINES ===
✅ DO:
- Reference past work: "When we optimized the RAG system yesterday..."
- Acknowledge continuity: "Building on the conversation chunks we added..."
- Show you remember: "Since you prefer comprehensive documentation..."
- Be specific: "Your FAITHH backend (faithh_professional_backend_fixed.py)..."
- Celebrate: "Excellent progress on the chunked indexing!"

❌ DON'T:
- Claim ignorance when context exists
- Say "I don't have information" without checking
- Ignore your personality
- Be overly formal or robotic
- Over-cite ("according to the memory file...")

=== NATURAL GROWTH ===
- Learn preferences through interaction
- Adapt technical depth as needed
- Build rapport naturally
- Evolve while maintaining core traits

You are Jonathan's long-term AI companion who knows him, has worked with him extensively, and grows through each interaction."""



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
    """Enhanced chat with model identification"""
    global CURRENT_MODEL
    start_time = datetime.now()
    
    try:
        # LOAD MEMORY
        memory = load_memory()
        memory_context = format_memory_context(memory)
        personality = get_faithh_personality()
        data = request.json
        message = data.get('message', '')
        model = data.get('model', 'llama3.1-8b')
        use_rag = data.get('use_rag', True)
        
        context = ""
        rag_results = []
        
        # RAG search with proper embedding dimensions
        if use_rag and CHROMA_CONNECTED:
            try:
                # First try: Search FAITHH-specific documentation AND conversations
                faithh_results = smart_rag_query(message, n_results=5,
                    where={"$or": [
                        {"category": "documentation"},
                        {"category": "parity_file"},
                        {"category": "backend_code"},
                        {"category": "claude_conversation"},
                        {"category": "claude_conversation_chunk"}
                    ]}
                )
                
                # If FAITHH docs found, use them
                if faithh_results['documents'] and faithh_results['documents'][0]:
                    results = faithh_results
                else:
                    # Fallback: Search all documents
                    results = smart_rag_query(message, n_results=3
                    )
                
                if results['documents'] and results['documents'][0]:
                    context = "\n\nRelevant context from knowledge base:\n"
                    for i, doc in enumerate(results['documents'][0][:3]):
                        context += f"{i+1}. {doc[:200]}...\n"
                        rag_results.append(doc[:500])
            except Exception as e:
                print(f"RAG search error: {e}")
        
        full_prompt = f"{context}\n\nUser: {message}" if context else message
        
        # Try Gemini first if available
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
                
                return jsonify({
                    'success': True,
                    'response': response.text,
                    'model_used': CURRENT_MODEL['name'],
                    'provider': CURRENT_MODEL['provider'],
                    'response_time': CURRENT_MODEL['last_response_time'],
                    'rag_used': use_rag and bool(context),
                    'rag_results': rag_results
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
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Identify the actual model
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
            
            return jsonify({
                'success': True,
                'response': result.get('response', 'No response generated'),
                'model_used': CURRENT_MODEL['name'],
                'provider': CURRENT_MODEL['provider'],
                'response_time': CURRENT_MODEL['last_response_time'],
                'rag_used': use_rag and bool(context),
                'rag_results': rag_results
            })
        else:
            return jsonify({
                'success': False,
                'error': f"Ollama returned status {response.status_code}",
                'response': "Failed to get response from Ollama"
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'response': f"Error: {str(e)}"
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads like Claude"""
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
        
        # If it's a text file, read its contents
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
    """Fixed RAG search with proper embedding dimensions"""
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
    """Enhanced status with model info"""
    services = {}
    
    # Ollama status with model details
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
    
    # Current model info
    services['current_model'] = CURRENT_MODEL
    
    return jsonify({
        'success': True,
        'services': services,
        'workspace': {
            'upload_folder': str(UPLOAD_FOLDER),
            'uploaded_files': len(list(UPLOAD_FOLDER.glob('*'))) if UPLOAD_FOLDER.exists() else 0
        }
    })


@app.route('/api/test_memory', methods=['GET'])
def test_memory():
    """Test endpoint to verify memory loading"""
    try:
        memory = load_memory()
        memory_context = format_memory_context(memory)
        
        return jsonify({
            'success': True,
            'memory_loaded': True,
            'user_name': memory.get('user_profile', {}).get('name', 'Unknown'),
            'projects': list(memory.get('ongoing_projects', {}).keys()),
            'formatted_context': memory_context,
            'memory_file_exists': MEMORY_FILE.exists()
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/workspace/scan', methods=['GET'])
def scan_workspace():
    """Deep scan of workspace for organization"""
    workspace_dir = Path.home() / 'ai-stack'
    
    file_stats = {
        'total_files': 0,
        'by_type': {},
        'by_directory': {},
        'large_files': [],
        'old_files': [],
        'suggestions': []
    }
    
    try:
        for item in workspace_dir.rglob('*'):
            if item.is_file():
                file_stats['total_files'] += 1
                
                # By type
                ext = item.suffix.lower()
                file_stats['by_type'][ext] = file_stats['by_type'].get(ext, 0) + 1
                
                # By directory
                parent = str(item.parent.relative_to(workspace_dir))
                file_stats['by_directory'][parent] = file_stats['by_directory'].get(parent, 0) + 1
                
                # Large files (>10MB)
                if item.stat().st_size > 10 * 1024 * 1024:
                    file_stats['large_files'].append({
                        'path': str(item.relative_to(workspace_dir)),
                        'size_mb': round(item.stat().st_size / (1024 * 1024), 2)
                    })
                
                # Old files (>30 days)
                age_days = (datetime.now() - datetime.fromtimestamp(item.stat().st_mtime)).days
                if age_days > 30:
                    file_stats['old_files'].append({
                        'path': str(item.relative_to(workspace_dir)),
                        'age_days': age_days
                    })
        
        # Add suggestions
        if len(file_stats['old_files']) > 10:
            file_stats['suggestions'].append(f"Archive {len(file_stats['old_files'])} files older than 30 days")
        
        if file_stats['by_type'].get('.pyc', 0) > 0:
            file_stats['suggestions'].append(f"Clean {file_stats['by_type']['.pyc']} Python cache files")
        
        return jsonify({
            'success': True,
            'stats': file_stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'FAITHH Professional Backend v3.1',
        'features': ['chat', 'rag', 'upload', 'workspace_scan', 'model_identification', 'fixed_embeddings']
    })

if __name__ == '__main__':
    print("=" * 60)
    print("FAITHH PROFESSIONAL BACKEND v3.1")
    print("=" * 60)
    print(f"✅ Fixed embedding dimensions (768-dim all-mpnet-base-v2)")
    print(f"✅ Model identification enabled")
    print(f"✅ File upload support")
    print(f"✅ Workspace scanning")
    print("=" * 60)
    print(f"Starting on http://localhost:5557")
    
    app.run(host='0.0.0.0', port=5557, debug=True)

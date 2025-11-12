#!/usr/bin/env python3
"""
FAITHH Professional Backend v3
Fixed embedding dimensions, model identification, file handling
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import requests
import requests
import json
import json
import os
import os
from pathlib import Path
import chromadb
import chromadb
from datetime import datetime
import base64
import base64
import mimetypes
from dotenv import load_dotenv
import os


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

# Initialize ChromaDB with text search (avoiding embedding dimension issues)
try:
    chroma_client = chromadb.HttpClient(host="localhost", port=8000)
    collection = chroma_client.get_collection(name="documents")
    CHROMA_CONNECTED = True
    doc_count = collection.count()
    print(f"✅ ChromaDB connected: {doc_count} documents available")
except Exception as e:
    CHROMA_CONNECTED = False
    collection = None
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
        data = request.json
        message = data.get('message', '')
        model = data.get('model', 'llama3.1-8b')
        use_rag = data.get('use_rag', False)
        
        context = ""
        rag_results = []
        
        # RAG search using text (avoiding embedding issues)
        if use_rag and CHROMA_CONNECTED:
            try:
                # Use query_texts instead of embeddings
                results = collection.query(
                    query_texts=[message],
                    n_results=3
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
    """Fixed RAG search using text queries"""
    if not CHROMA_CONNECTED:
        return jsonify({'success': False, 'error': 'ChromaDB not connected'}), 503
    
    try:
        data = request.json
        query = data.get('query', '')
        n_results = data.get('n_results', 5)
        
        # Use query_texts to avoid embedding dimension issues
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
            'embedding_note': 'Using text-based search (dimension-agnostic)'
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
        'note': 'Using text-based search'
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
        'service': 'FAITHH Professional Backend v3',
        'features': ['chat', 'rag', 'upload', 'workspace_scan', 'model_identification']
    })

if __name__ == '__main__':
    print("=" * 60)
    print("FAITHH PROFESSIONAL BACKEND v3")
    print("=" * 60)
    print(f"✅ Fixed embedding dimensions (using text search)")
    print(f"✅ Model identification enabled")
    print(f"✅ File upload support")
    print(f"✅ Workspace scanning")
    print("=" * 60)
    print(f"Starting on http://localhost:5557")
    
    app.run(host='0.0.0.0', port=5557, debug=True)
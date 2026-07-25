#!/usr/bin/env python3
"""
FAITHH Unified API - Chat + RAG + Tools in one place
Combines Gemini chat, RAG search, and tool execution
"""
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask_sock import Sock
import json
import asyncio
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

# Import our systems
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from tool_executor import get_executor
from tool_registry import get_registry
from executors.filesystem import FilesystemExecutor
from executors.process import ProcessExecutor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
sock = Sock(app)

# ============= CONFIGURATION =============

CONFIG = {
    'gemini_model': 'gemini-2.0-flash-exp',
    'chromadb_host': 'localhost',
    'chromadb_port': 8000,
    'collection_name': 'documents',
    'rag_results_count': 3,
    'ollama_embed_url': 'http://localhost:11435',
    'embed_model': 'nomic-embed',
}

# Get Gemini API key from environment variable (DO NOT hardcode keys!)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not found in environment. Gemini features will be disabled.")

# Initialize Gemini
gemini_model = None
if GEMINI_AVAILABLE and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel(CONFIG['gemini_model'])
        logger.info("✅ Gemini initialized")
    except Exception as e:
        logger.warning(f"⚠️  Gemini init failed: {e}")

# Initialize ChromaDB
chroma_client = None
if CHROMADB_AVAILABLE:
    try:
        chroma_client = chromadb.HttpClient(
            host=CONFIG['chromadb_host'],
            port=CONFIG['chromadb_port']
        )
        logger.info("✅ ChromaDB connected")
    except Exception as e:
        logger.warning(f"⚠️  ChromaDB connection failed: {e}")

# Initialize Tool System
tool_executor = get_executor()
tool_registry = get_registry()

# Register executors
tool_executor.register_executor('filesystem', FilesystemExecutor())
tool_executor.register_executor('process', ProcessExecutor())

# Register tools
tool_registry.register_tool({
    'name': 'read_file',
    'description': 'Read file contents',
    'category': 'filesystem',
    'executor': 'filesystem',
    'permissions': ['file.read']
})

tool_registry.register_tool({
    'name': 'write_file',
    'description': 'Write to a file',
    'category': 'filesystem',
    'executor': 'filesystem',
    'permissions': ['file.write']
})

tool_registry.register_tool({
    'name': 'run_command',
    'description': 'Execute shell command',
    'category': 'process',
    'executor': 'process',
    'permissions': ['process.execute']
})

logger.info("✅ Tool system initialized")

# ============= CHAT ORCHESTRATOR =============

class ChatOrchestrator:
    """Orchestrates chat, RAG, and tools"""
    
    def __init__(self):
        self.gemini = gemini_model
        self.chroma = chroma_client
        self.executor = tool_executor
        
    def should_use_rag(self, message: str) -> bool:
        """Determine if RAG should be used for this message"""
        rag_keywords = [
            'remember', 'told', 'said', 'mentioned', 'discussed',
            'conversation', 'chat', 'talked about', 'earlier',
            'document', 'file', 'note', 'wrote', 'previous'
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in rag_keywords)
    
    def detect_tool_needs(self, message: str) -> List[str]:
        """Detect which tools might be needed"""
        tools = []
        msg_lower = message.lower()
        
        if ('read' in msg_lower or 'show' in msg_lower) and 'file' in msg_lower:
            tools.append('read_file')
        if 'write' in msg_lower and 'file' in msg_lower:
            tools.append('write_file')
        if 'run' in msg_lower or 'execute' in msg_lower or 'command' in msg_lower:
            tools.append('run_command')
            
        return tools
    
    async def search_rag(self, query: str, n_results: int = 3) -> Optional[Dict]:
        """Search RAG database"""
        if not self.chroma:
            return None
        
        try:
            # Note: We have embedding dimension mismatch (768 vs 384)
            # Using query_texts instead of embeddings for now
            collection = self.chroma.get_collection(CONFIG['collection_name'])
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            if results and results.get('documents') and len(results['documents'][0]) > 0:
                sources = []
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results.get('metadatas', [[]])[0],
                    results.get('distances', [[]])[0]
                )):
                    sources.append({
                        'content': doc[:500] + '...' if len(doc) > 500 else doc,
                        'metadata': metadata,
                        'score': 1 - distance if distance else 0  # Convert distance to similarity
                    })
                
                return {
                    'sources': sources,
                    'count': len(sources)
                }
        except Exception as e:
            logger.error(f"RAG search error: {e}")
            return None
    
    async def generate_response(
        self,
        message: str,
        use_rag: bool = True,
        use_tools: bool = True,
        context: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Generate complete response with RAG and tools"""
        
        result = {
            'message': message,
            'response': '',
            'used_rag': False,
            'rag_sources': [],
            'used_tools': False,
            'tool_results': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Step 1: Check if RAG needed
        if use_rag and self.should_use_rag(message):
            rag_results = await self.search_rag(message, n_results=CONFIG['rag_results_count'])
            if rag_results:
                result['used_rag'] = True
                result['rag_sources'] = rag_results['sources']
                logger.info(f"📚 RAG: Found {len(rag_results['sources'])} sources")
        
        # Step 2: Build context for Gemini
        context_parts = []
        if result['rag_sources']:
            context_parts.append("Relevant information from your documents:")
            for i, source in enumerate(result['rag_sources'], 1):
                context_parts.append(f"\nSource {i}: {source['content']}")
            context_parts.append(f"\nUser question: {message}")
        
        # Step 3: Generate response with Gemini
        if self.gemini:
            try:
                full_prompt = "\n".join(context_parts) if context_parts else message
                response = self.gemini.generate_content(full_prompt)
                result['response'] = response.text
                logger.info("✅ Gemini response generated")
            except Exception as e:
                result['response'] = f"Error generating response: {str(e)}"
                logger.error(f"Gemini error: {e}")
        else:
            result['response'] = "Gemini not available"
        
        # Step 4: Check if tools mentioned in response/message
        if use_tools:
            detected_tools = self.detect_tool_needs(message)
            if detected_tools:
                logger.info(f"🔧 Tools detected: {detected_tools}")
                # Note: For now, just flag tools. Full execution in next iteration
                result['used_tools'] = True
                result['tool_results'] = [f"Tool '{t}' available" for t in detected_tools]
        
        return result

# Global orchestrator
orchestrator = ChatOrchestrator()

# ============= API ENDPOINTS =============

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main unified chat endpoint"""
    data = request.json
    message = data.get('message', '')
    use_rag = data.get('use_rag', True)
    use_tools = data.get('use_tools', True)
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    logger.info(f"💬 Chat: {message[:60]}...")
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            orchestrator.generate_response(message, use_rag, use_tools)
        )
        return jsonify(result)
    finally:
        loop.close()


@app.route('/api/status', methods=['GET'])
def status():
    """System status endpoint"""
    return jsonify({
        'services': {
            'gemini': 'online' if gemini_model else 'offline',
            'chromadb': 'online' if chroma_client else 'offline',
            'tools': 'online',
        },
        'config': {
            'rag_enabled': CHROMADB_AVAILABLE,
            'tools_enabled': True,
            'model': CONFIG['gemini_model']
        },
        'stats': {
            'executors': list(tool_executor.executors.keys()),
            'tools': len(tool_registry.list_tools()),
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/rag/stats', methods=['GET'])
def rag_stats():
    """RAG database statistics"""
    if not chroma_client:
        return jsonify({'error': 'ChromaDB not available'}), 503
    
    try:
        collection = chroma_client.get_collection(CONFIG['collection_name'])
        count = collection.count()
        return jsonify({
            'collection': CONFIG['collection_name'],
            'document_count': count,
            'status': 'online'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def root():
    """API information"""
    return jsonify({
        'name': 'FAITHH Unified API',
        'version': '1.0',
        'description': 'Chat + RAG + Tools in one place',
        'endpoints': {
            'POST /api/chat': 'Main chat endpoint (RAG + tools)',
            'GET  /api/status': 'System status',
            'GET  /api/rag/stats': 'RAG database stats',
        },
        'features': ['gemini_chat', 'rag_search', 'tool_execution']
    })

# ============= WEBSOCKET (Streaming) =============

@sock.route('/ws/chat')
def websocket_chat(ws):
    """WebSocket for streaming chat responses"""
    logger.info("🔌 WebSocket client connected")
    
    try:
        while True:
            message_data = ws.receive()
            if not message_data:
                break
            
            data = json.loads(message_data)
            message = data.get('message', '')
            use_rag = data.get('use_rag', True)
            use_tools = data.get('use_tools', True)
            
            # Send status
            ws.send(json.dumps({
                'type': 'status',
                'message': 'Processing...'
            }))
            
            # Generate response
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    orchestrator.generate_response(message, use_rag, use_tools)
                )
                
                # Send result
                ws.send(json.dumps({
                    'type': 'response',
                    'data': result
                }))
            finally:
                loop.close()
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws.send(json.dumps({
            'type': 'error',
            'message': str(e)
        }))
    finally:
        logger.info("🔌 WebSocket client disconnected")

# ============= STARTUP =============

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🤖 FAITHH Unified API v1.0")
    print("="*60)
    print("\n✨ Features:")
    print(f"   • Gemini Chat: {'✅' if gemini_model else '❌'}")
    print(f"   • RAG Search: {'✅' if chroma_client else '❌'}")
    print(f"   • Tool Execution: ✅")
    print(f"\n🔧 Tools: {len(tool_registry.list_tools())} registered")
    print(f"🎯 Executors: {list(tool_executor.executors.keys())}")
    
    if chroma_client:
        try:
            coll = chroma_client.get_collection(CONFIG['collection_name'])
            doc_count = coll.count()
            print(f"📚 RAG Database: {doc_count:,} documents")
        except:
            print(f"📚 RAG Database: Collection '{CONFIG['collection_name']}' not found")
    
    print("\n📡 Endpoints:")
    print("   HTTP:      http://localhost:5556")
    print("   WebSocket: ws://localhost:5556/ws/chat")
    print("\n" + "="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5556, debug=True)

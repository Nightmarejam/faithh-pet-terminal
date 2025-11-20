#!/usr/bin/env python3
"""
FAITHH Phase 2 Blueprint
Modular integration - can be enabled/disabled without touching main backend

Features:
- Auto-index conversations
- Session summaries
- Memory suggestions
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import json

def create_phase2_blueprint(collection, chroma_connected, ollama_host="http://localhost:11434"):
    """
    Factory function to create Phase 2 blueprint with backend dependencies
    
    Args:
        collection: ChromaDB collection instance
        chroma_connected: Boolean flag for ChromaDB status
        ollama_host: Ollama API endpoint
    
    Returns:
        Configured Flask Blueprint
    """
    
    phase2 = Blueprint('phase2', __name__)
    
    # ========================================================================
    # AUTO-INDEXING
    # ========================================================================
    
    @phase2.route('/api/auto_index', methods=['POST'])
    def auto_index():
        """
        Manually trigger conversation indexing
        
        POST body:
        {
            "user_message": "What is FAITHH?",
            "assistant_message": "FAITHH is...",
            "metadata": {"model": "llama3.1-8b", "rag_used": true}
        }
        """
        if not chroma_connected:
            return jsonify({'error': 'ChromaDB not connected'}), 503
        
        try:
            data = request.json
            user_msg = data.get('user_message', '')
            assistant_msg = data.get('assistant_message', '')
            metadata = data.get('metadata', {})
            
            if not user_msg or not assistant_msg:
                return jsonify({'error': 'Both user_message and assistant_message required'}), 400
            
            # Create conversation document
            timestamp = datetime.now()
            conv_id = f"live_conv_{timestamp.strftime('%Y%m%d_%H%M%S')}"
            
            conversation_text = f"User: {user_msg}\n\nAssistant: {assistant_msg}"
            
            # Build metadata
            meta = {
                "type": "live_conversation",
                "category": "live_chat",
                "timestamp": timestamp.isoformat(),
                "user_preview": user_msg[:100]
            }
            meta.update(metadata)
            
            # Add to ChromaDB
            collection.add(
                documents=[conversation_text],
                metadatas=[meta],
                ids=[conv_id]
            )
            
            return jsonify({
                'success': True,
                'conversation_id': conv_id,
                'indexed_at': timestamp.isoformat(),
                'message': f'Conversation indexed successfully'
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ========================================================================
    # SESSION SUMMARIES
    # ========================================================================
    
    @phase2.route('/api/session_summary', methods=['POST'])
    def session_summary():
        """
        Generate summary of conversation history
        
        POST body:
        {
            "conversation": [
                {"user": "...", "assistant": "..."},
                ...
            ],
            "save_to_file": true
        }
        """
        try:
            import requests
            
            data = request.json
            conversation = data.get('conversation', [])
            save_to_file = data.get('save_to_file', False)
            
            if not conversation:
                return jsonify({'error': 'No conversation provided'}), 400
            
            # Build summary prompt
            history_text = "\n\n".join([
                f"User: {msg.get('user', '')}\nAssistant: {msg.get('assistant', '')}"
                for msg in conversation[-10:]  # Last 10 exchanges
            ])
            
            summary_prompt = f"""Summarize this conversation session concisely:

{history_text}

Provide:
1. Main topics discussed (bullet points)
2. Key decisions made  
3. Action items or next steps
4. Files/code created or modified

Keep it concise and actionable."""
            
            # Use Ollama for summary
            response = requests.post(
                f"{ollama_host}/api/generate",
                json={
                    "model": "llama3.1-8b",
                    "prompt": summary_prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return jsonify({'error': 'Failed to generate summary'}), 500
            
            summary = response.json().get('response', 'Summary generation failed')
            
            # Optionally save to file
            saved_path = None
            if save_to_file:
                from pathlib import Path
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                summary_file = Path.home() / f"ai-stack/docs/session-reports/SESSION_{timestamp}.md"
                summary_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(summary_file, 'w') as f:
                    f.write(f"# Session Summary\n")
                    f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                    f.write(summary)
                
                saved_path = str(summary_file)
            
            return jsonify({
                'success': True,
                'summary': summary,
                'saved_to': saved_path,
                'conversation_length': len(conversation)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ========================================================================
    # MEMORY SUGGESTIONS
    # ========================================================================
    
    @phase2.route('/api/memory_suggestions', methods=['POST'])
    def memory_suggestions():
        """
        Analyze conversation for memory-worthy information
        
        POST body:
        {
            "conversation": [
                {"user": "...", "assistant": "..."},
                ...
            ]
        }
        """
        try:
            import re
            
            data = request.json
            conversation = data.get('conversation', [])
            
            if not conversation:
                return jsonify({'error': 'No conversation provided'}), 400
            
            # Combine all text
            combined_text = " ".join([
                f"{msg.get('user', '')} {msg.get('assistant', '')}"
                for msg in conversation[-5:]  # Last 5 exchanges
            ])
            
            suggestions = []
            
            # Pattern detection
            patterns = {
                'project': {
                    'regex': [
                        r"(?:working on|building|creating|developing) ([A-Z][\w\s]{2,30})",
                        r"(?:new project|side project)(?:[:\s]+)?([A-Z][\w\s]{2,30})",
                        r"(?:started|beginning) ([\w\s]{3,30}) project"
                    ],
                    'type': 'new_project'
                },
                'focus': {
                    'regex': [
                        r"(?:focusing on|concentrating on|prioritizing) ([\w\s]{3,50})",
                        r"(?:my|current) (?:focus|priority) is ([\w\s]{3,50})",
                        r"(?:switching to|moving to|now using) ([\w\s]{3,50})"
                    ],
                    'type': 'focus_change'
                },
                'tool': {
                    'regex': [
                        r"(?:installed|using|switched to) ([\w\s]{2,30})",
                        r"(?:now prefer|prefer using) ([\w\s]{2,30})"
                    ],
                    'type': 'tool_preference'
                }
            }
            
            # Search for patterns
            for category, config in patterns.items():
                for pattern in config['regex']:
                    matches = re.findall(pattern, combined_text, re.IGNORECASE)
                    for match in matches:
                        if len(match.strip()) > 3:
                            suggestions.append({
                                "type": config['type'],
                                "value": match.strip(),
                                "confidence": "medium",
                                "category": category
                            })
            
            # Deduplicate
            seen = set()
            unique_suggestions = []
            for sug in suggestions:
                key = f"{sug['type']}:{sug['value'].lower()}"
                if key not in seen:
                    seen.add(key)
                    unique_suggestions.append(sug)
            
            return jsonify({
                'success': True,
                'suggestions': unique_suggestions,
                'count': len(unique_suggestions),
                'message': 'Consider updating faithh_memory.json with these items'
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ========================================================================
    # PHASE 2 STATUS
    # ========================================================================
    
    @phase2.route('/api/phase2_status', methods=['GET'])
    def phase2_status():
        """Check Phase 2 feature availability"""
        return jsonify({
            'phase2_enabled': True,
            'features': {
                'auto_indexing': True,
                'session_summaries': True,
                'memory_suggestions': True
            },
            'chromadb_connected': chroma_connected,
            'endpoints': [
                '/api/auto_index',
                '/api/session_summary',
                '/api/memory_suggestions',
                '/api/phase2_status'
            ]
        })
    
    return phase2


# ============================================================================
# STANDALONE USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    """
    Test Phase 2 blueprint independently
    """
    from flask import Flask
    import chromadb
    
    app = Flask(__name__)
    
    try:
        # Mock ChromaDB connection
        chroma_client = chromadb.HttpClient(host="localhost", port=8000)
        collection = chroma_client.get_or_create_collection("test_collection")
        chroma_connected = True
    except:
        collection = None
        chroma_connected = False
    
    # Create and register blueprint
    phase2_bp = create_phase2_blueprint(collection, chroma_connected)
    app.register_blueprint(phase2_bp)
    
    @app.route('/')
    def index():
        return "Phase 2 Blueprint Test Server"
    
    print("=" * 70)
    print("PHASE 2 BLUEPRINT TEST SERVER")
    print("=" * 70)
    print(f"ChromaDB Connected: {chroma_connected}")
    print("\nEndpoints:")
    print("  POST /api/auto_index")
    print("  POST /api/session_summary")
    print("  POST /api/memory_suggestions")
    print("  GET  /api/phase2_status")
    print("\nRunning on http://localhost:5558")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=5558, debug=True)

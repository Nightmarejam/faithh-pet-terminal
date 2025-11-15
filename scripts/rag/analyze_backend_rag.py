#!/usr/bin/env python3
"""
Backend RAG Integration Analyzer & Fixer
Checks if /api/chat properly uses RAG and fixes if needed
"""

from pathlib import Path
import re
import shutil
from datetime import datetime

def analyze_backend():
    """Analyze the backend's RAG integration"""
    backend_path = Path.home() / "ai-stack/faithh_professional_backend_fixed.py"
    
    if not backend_path.exists():
        print(f"❌ Backend not found: {backend_path}")
        return None
    
    content = backend_path.read_text()
    
    print("=" * 70)
    print("BACKEND RAG INTEGRATION ANALYSIS")
    print("=" * 70)
    print()
    
    # Check 1: Does smart_rag_query exist?
    has_smart_query = "smart_rag_query" in content
    print(f"1. smart_rag_query function: {'✅ Found' if has_smart_query else '❌ Missing'}")
    
    # Check 2: Is use_rag parameter read?
    use_rag_pattern = r"use_rag\s*=\s*request\.(?:json|get_json)\(\)\.get\(['\"]use_rag['\"]"
    has_use_rag = bool(re.search(use_rag_pattern, content))
    print(f"2. Reading use_rag parameter: {'✅ Yes' if has_use_rag else '❌ No'}")
    
    # Check 3: Is RAG conditional logic present?
    rag_condition = r"if\s+use_rag"
    has_rag_condition = bool(re.search(rag_condition, content))
    print(f"3. RAG conditional logic: {'✅ Yes' if has_rag_condition else '❌ No'}")
    
    # Check 4: Is smart_rag_query called?
    smart_query_call = "smart_rag_query" in content and "smart_rag_query(" in content
    print(f"4. Calling smart_rag_query: {'✅ Yes' if smart_query_call else '❌ No'}")
    
    # Check 5: Find the /api/chat route
    chat_route_match = re.search(r"@app\.route\(['\"]\/api\/chat['\"].*?\n(.*?)(?=@app\.route|$)", content, re.DOTALL)
    if chat_route_match:
        chat_code = chat_route_match.group(1)[:500]
        print(f"\n5. /api/chat endpoint preview:")
        print("   " + "─" * 60)
        for line in chat_code.split('\n')[:15]:
            print(f"   {line}")
        print("   " + "─" * 60)
    
    print()
    
    if not has_use_rag or not has_rag_condition:
        print("⚠️  PROBLEM DETECTED: Backend not properly handling use_rag!")
        print("   The /api/chat endpoint needs to:")
        print("   1. Read use_rag from request JSON")
        print("   2. Call smart_rag_query() when use_rag=True")
        print("   3. Add RAG results to LLM context")
        return backend_path
    
    print("✅ RAG integration looks good!")
    return None

def create_fixed_chat_endpoint():
    """Create a fixed /api/chat endpoint with proper RAG integration"""
    
    fixed_endpoint = '''
@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests with optional RAG"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        model = data.get('model', 'llama3.1-8b')
        use_rag = data.get('use_rag', False)  # READ RAG PARAMETER
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Build context
        context = ""
        
        # USE RAG IF ENABLED
        if use_rag:
            try:
                print(f"🔍 RAG enabled for query: {message[:50]}...")
                
                # Call our smart RAG query function
                rag_results = smart_rag_query(message, n_results=10)
                
                if rag_results and rag_results.get('documents'):
                    docs = rag_results['documents'][0]
                    metadatas = rag_results['metadatas'][0]
                    
                    print(f"📚 Retrieved {len(docs)} documents from RAG")
                    
                    # Build context from documents
                    context = "\\n\\n".join([
                        f"--- Document {i+1}: {meta.get('source', 'Unknown')} ---\\n{doc}"
                        for i, (doc, meta) in enumerate(zip(docs, metadatas))
                    ])
                    
                    context = f"Relevant context from your documents:\\n\\n{context}\\n\\n---\\n\\n"
                else:
                    print("⚠️  RAG query returned no results")
            except Exception as e:
                print(f"❌ RAG error: {e}")
                # Continue without RAG if it fails
        
        # Build full prompt
        system_prompt = """You are FAITHH, a helpful AI assistant. Use the provided context to answer questions accurately.
If context is provided, reference it in your answer. If no context is available, say so."""
        
        full_prompt = f"{system_prompt}\\n\\n{context}User: {message}\\n\\nAssistant:"
        
        # Call Ollama
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': model,
                    'prompt': full_prompt,
                    'stream': False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                reply = result.get('response', 'No response generated')
                
                return jsonify({
                    'response': reply,
                    'model': model,
                    'rag_used': use_rag and bool(context)
                })
            else:
                return jsonify({'error': f'Ollama error: {response.status_code}'}), 500
                
        except Exception as e:
            return jsonify({'error': f'Error calling model: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
'''
    
    return fixed_endpoint

def main():
    """Run analysis and offer to fix"""
    
    needs_fix = analyze_backend()
    
    if needs_fix:
        print()
        print("🔧 FIX AVAILABLE")
        print("=" * 70)
        print()
        print("I can create a properly integrated /api/chat endpoint.")
        print()
        print("The fix will:")
        print("  1. Read use_rag parameter from request")
        print("  2. Call smart_rag_query() when enabled")
        print("  3. Add RAG results to LLM context")
        print("  4. Return rag_used flag in response")
        print()
        print("Fixed endpoint saved to: docs/patches/fixed_chat_endpoint.py")
        print()
        print("To apply manually:")
        print("  1. Open faithh_professional_backend_fixed.py")
        print("  2. Find the @app.route('/api/chat') section")
        print("  3. Replace it with the code from fixed_chat_endpoint.py")
        print("  4. Restart backend")
        print()
        
        # Save fixed endpoint
        patch_path = Path.home() / "ai-stack/docs/patches/fixed_chat_endpoint.py"
        patch_path.parent.mkdir(parents=True, exist_ok=True)
        patch_path.write_text(create_fixed_chat_endpoint())
        print(f"✅ Fix saved to: {patch_path}")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()

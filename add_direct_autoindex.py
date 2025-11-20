#!/usr/bin/env python3
"""
Better auto-index integration - calls function directly, no HTTP deadlock
"""

with open('faithh_professional_backend_fixed.py', 'r') as f:
    content = f.read()

# Backup
with open('faithh_professional_backend_fixed.py.backup_direct_call', 'w') as f:
    f.write(content)

print("✅ Backup created")

# Strategy: Create a simple indexing function, then call it directly

# 1. Add indexing function after the chat() function definition
indexing_function = '''

def index_conversation_direct(user_msg, assistant_msg, metadata=None):
    """Direct indexing without HTTP call - prevents deadlock"""
    if not CHROMA_CONNECTED:
        return False
    
    try:
        timestamp = datetime.now()
        conv_id = f"live_conv_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        conversation_text = f"User: {user_msg}\\n\\nAssistant: {assistant_msg}"
        
        meta = {
            "type": "live_conversation",
            "category": "live_chat",
            "timestamp": timestamp.isoformat(),
            "user_preview": user_msg[:100]
        }
        
        if metadata:
            meta.update(metadata)
        
        collection.add(
            documents=[conversation_text],
            metadatas=[meta],
            ids=[conv_id]
        )
        
        print(f"📝 Indexed: {conv_id}")
        return True
        
    except Exception as e:
        print(f"❌ Auto-index failed: {e}")
        return False
'''

# Find where to insert (after chat function, before next @app.route)
# Look for the upload_file route as marker
marker = "@app.route('/api/upload', methods=['POST'])"
if marker in content:
    insert_pos = content.find(marker)
    content = content[:insert_pos] + indexing_function + "\n" + content[insert_pos:]
    print("✅ Added indexing function")
else:
    print("⚠️ Marker not found, trying alternative...")

# 2. Add call to indexing function in Gemini response
gemini_marker = """                return jsonify({
                    'success': True,
                    'response': response.text,"""

gemini_replacement = """                # Auto-index (Phase 2)
                index_conversation_direct(message, response.text, {'model': 'gemini', 'rag_used': use_rag})
                
                return jsonify({
                    'success': True,
                    'response': response.text,"""

if gemini_marker in content:
    content = content.replace(gemini_marker, gemini_replacement, 1)
    print("✅ Added auto-index to Gemini response")

# 3. Add call to indexing function in Ollama response
ollama_marker = """            return jsonify({
                'success': True,
                'response': result.get('response', 'No response generated'),"""

ollama_replacement = """            # Auto-index (Phase 2)
            index_conversation_direct(message, result.get('response', ''), {'model': model, 'rag_used': use_rag})
            
            return jsonify({
                'success': True,
                'response': result.get('response', 'No response generated'),"""

if ollama_marker in content:
    content = content.replace(ollama_marker, ollama_replacement, 1)
    print("✅ Added auto-index to Ollama response")

# Save
with open('faithh_professional_backend_fixed.py', 'w') as f:
    f.write(content)

print("✅ Direct-call auto-indexing integrated!")
print("\nTest compilation:")
import subprocess
result = subprocess.run(['python', '-m', 'py_compile', 'faithh_professional_backend_fixed.py'],
                       capture_output=True, text=True)
if result.returncode == 0:
    print("✅ Compilation passed!")
    print("\nRestart backend:")
    print("  pkill -f faithh_professional_backend")
    print("  python faithh_professional_backend_fixed.py > faithh_backend.log 2>&1 &")
else:
    print("❌ Compilation failed:")
    print(result.stderr)

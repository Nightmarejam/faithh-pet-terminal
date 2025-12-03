#!/usr/bin/env python3
"""Add auto-index calls to chat() function"""

import requests

with open('faithh_professional_backend_fixed.py', 'r') as f:
    content = f.read()

# Backup
with open('faithh_professional_backend_fixed.py.backup_autoindex', 'w') as f:
    f.write(content)

print("✅ Backup created")

# Strategy: After successful Gemini response, add auto-index call
# Find the Gemini success return and add call before it

gemini_marker = """                return jsonify({
                    'success': True,
                    'response': response.text,"""

gemini_replacement = """                # Auto-index conversation (Phase 2)
                try:
                    requests.post('http://localhost:5557/api/auto_index', json={
                        'user_message': message,
                        'assistant_message': response.text,
                        'metadata': {'model': 'gemini', 'rag_used': use_rag}
                    })
                except:
                    pass  # Don't break chat if indexing fails
                
                return jsonify({
                    'success': True,
                    'response': response.text,"""

if gemini_marker in content:
    content = content.replace(gemini_marker, gemini_replacement)
    print("✅ Added auto-index to Gemini response")
else:
    print("⚠️ Gemini marker not found")

# Find the Ollama success return
ollama_marker = """            return jsonify({
                'success': True,
                'response': result.get('response', 'No response generated'),"""

ollama_replacement = """            # Auto-index conversation (Phase 2)
            try:
                requests.post('http://localhost:5557/api/auto_index', json={
                    'user_message': message,
                    'assistant_message': result.get('response', ''),
                    'metadata': {'model': model, 'rag_used': use_rag}
                })
            except:
                pass  # Don't break chat if indexing fails
            
            return jsonify({
                'success': True,
                'response': result.get('response', 'No response generated'),"""

if ollama_marker in content:
    content = content.replace(ollama_marker, ollama_replacement)
    print("✅ Added auto-index to Ollama response")
else:
    print("⚠️ Ollama marker not found")

# Save
with open('faithh_professional_backend_fixed.py', 'w') as f:
    f.write(content)

print("✅ Auto-indexing integrated!")
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

#!/usr/bin/env python3
import json
import subprocess

# Run the query
result = subprocess.run([
    'curl', '-s', '-X', 'POST', 
    'http://localhost:5557/api/chat',
    '-H', 'Content-Type: application/json',
    '-d', '{"message": "parasitic emergence experiment 5", "model": "qwen25-grounded"}'
], capture_output=True, text=True)

# Parse and analyze
data = json.loads(result.stdout)
print("Model used:", data.get('model_used'))
print("RAG used:", data.get('rag_used'))
print("Number of RAG results:", len(data.get('rag_results', [])))

# Check if Exp 5 content is in RAG results
rag_results = data.get('rag_results', [])
exp5_found = False
for i, result in enumerate(rag_results[:3]):
    if isinstance(result, dict):
        content = result.get('document', str(result))
    else:
        content = str(result)
    
    if 'experiment 5' in content.lower() or 'parasitic' in content.lower():
        print(f"Exp 5 found in RAG result {i+1}")
        exp5_found = True
        print(f"  Preview: {content[:100]}...")

if not exp5_found:
    print("Exp 5 NOT found in RAG results")
    print("First RAG result preview:", rag_results[0][:100] if rag_results else "None")

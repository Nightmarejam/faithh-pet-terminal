#!/usr/bin/env python3
import json
import subprocess

# Run the query
result = subprocess.run([
    'curl', '-s', '-X', 'POST', 
    'http://localhost:5557/api/chat',
    '-H', 'Content-Type: application/json',
    '-d', '{"message": "What were the key findings from Experiment 5 parasitic emergence?", "model": "qwen25-grounded"}'
], capture_output=True, text=True)

# Parse and analyze
data = json.loads(result.stdout)

print("=" * 60)
print("FAITHH's Response:")
print("=" * 60)
print(data.get('response', 'No response'))
print("\n" + "=" * 60)
print("RAG Context Provided:")
print("=" * 60)

rag_results = data.get('rag_results', [])
for i, result in enumerate(rag_results[:3]):
    if isinstance(result, dict):
        content = result.get('document', str(result))
    else:
        content = str(result)
    
    print(f"\nRAG Result {i+1}:")
    print(content[:300] + "..." if len(content) > 300 else content)
    if 'experiment 5' in content.lower() or 'parasitic' in content.lower():
        print("-> CONTAINS EXP 5 INFO!")

print("\n" + "=" * 60)
print("Model Info:")
print("=" * 60)
print(f"Model: {data.get('model_used')}")
print(f"RAG Used: {data.get('rag_used')}")
print(f"Response Time: {data.get('response_time', 0):.2f}s")

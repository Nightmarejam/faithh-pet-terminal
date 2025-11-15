import requests
import json

# Test RAG search
response = requests.post(
    'http://localhost:5557/api/rag_search',
    json={'query': 'What is FAITHH?', 'n_results': 3}
)

print(json.dumps(response.json(), indent=2))

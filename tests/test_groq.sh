#!/bin/bash
curl -s -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the four mechanisms in the Harmony-AI Bridge document?", "model": "llama3.1-8b"}' | python3 -m json.tool

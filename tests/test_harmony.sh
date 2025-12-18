#!/bin/bash
cd /home/jonat/ai-stack
source venv/bin/activate

curl -s -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the four proposed AI mechanisms in the Harmony-AI Bridge?", "session_id": "harmony_test"}'

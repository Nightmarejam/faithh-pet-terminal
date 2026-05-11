#!/bin/bash
curl -s --max-time 60 \
  -X POST http://localhost:5557/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the current status of the Tom Cat Sound LLC 2024 tax filing and what is the next action item?", "model": "qwen25-grounded:latest"}' \
  2>&1
echo "---END---"

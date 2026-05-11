#!/bin/bash
# Quick single test - check if deepseek routing is fixed after restart
curl -s --max-time 60 -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the net operating loss for Tom Cat Sound LLC in 2024?"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('MODEL:', d.get('model_used','?')); print('RESPONSE:', d.get('response','ERROR:'+str(d))[:400])"

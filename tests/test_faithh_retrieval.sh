#!/bin/bash
# Test FAITHH retrieval quality with known-answer questions

BASE="http://localhost:5557/api/chat"

echo "===== TEST 1: Specific factual retrieval ====="
curl -s --max-time 60 -X POST $BASE \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the net operating loss for Tom Cat Sound LLC in 2024, and which equipment sales contributed to that figure?"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('response','ERROR:'+str(d))[:600])"

echo ""
echo "===== TEST 2: Honest incompleteness ====="
curl -s --max-time 60 -X POST $BASE \
  -H "Content-Type: application/json" \
  -d '{"message": "What is TCs current mailing address and SSN for the K-1 filing?"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('response','ERROR:'+str(d))[:600])"

echo ""
echo "===== TEST 3: Fresh doc - resonance gating ====="
curl -s --max-time 60 -X POST $BASE \
  -H "Content-Type: application/json" \
  -d '{"message": "Why would single-timescale resonance gating produce inhuman behavior in an AI system?"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('response','ERROR:'+str(d))[:600])"

echo ""
echo "===== TEST 4: FGS conditions ====="
curl -s --max-time 60 -X POST $BASE \
  -H "Content-Type: application/json" \
  -d '{"message": "What conditions must be true before the Floating Garden Soundworks final business plan can be written?"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('response','ERROR:'+str(d))[:600])"

echo ""
echo "===== DONE ====="

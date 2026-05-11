#!/bin/bash
# scripts/test_faithh_stack.sh
# Tests all components of FAITHH ecosystem

set -e  # Exit on error

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="logs/test-results/faithh_test_${TIMESTAMP}.json"

mkdir -p logs/test-results

echo "{"
echo "  \"timestamp\": \"$TIMESTAMP\","
echo "  \"tests\": {"

# Test 1: ChromaDB on Gen8
echo "    \"chromadb\": {"
if curl -s http://192.158.1.243:8000/api/v1/heartbeat > /dev/null 2>&1; then
  echo "      \"status\": \"online\","
  
  # Get collection info
  COLLECTIONS=$(curl -s http://192.158.1.243:8000/api/v1/collections | jq -r '.[].name' 2>/dev/null || echo "")
  echo "      \"collections\": [$(echo $COLLECTIONS | tr '\n' ',' | sed 's/,$//' | sed 's/\(.*\)/"\1"/' | sed 's/ /","/g')],"
  
  # Get document count
  DOC_COUNT=$(curl -s http://192.158.1.243:8000/api/v1/collections/faithh_knowledge_base | jq -r '.metadata.documents' 2>/dev/null || echo "unknown")
  echo "      \"documents\": $DOC_COUNT"
else
  echo "      \"status\": \"offline\""
fi
echo "    },"

# Test 2: Ollama
echo "    \"ollama\": {"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
  echo "      \"status\": \"online\","
  
  # List models
  MODELS=$(curl -s http://localhost:11434/api/tags | jq -r '.models[].name' 2>/dev/null || echo "")
  echo "      \"models\": [$(echo $MODELS | tr '\n' ',' | sed 's/,$//' | sed 's/\(.*\)/"\1"/' | sed 's/ /","/g')]"
else
  echo "      \"status\": \"offline\""
fi
echo "    },"

# Test 3: FAITHH Professional Backend
echo "    \"faithh_professional_backend\": {"
if curl -s http://localhost:5557/status > /dev/null 2>&1; then
  echo "      \"status\": \"online\","
  
  # Get status details
  STATUS=$(curl -s http://localhost:5557/status)
  echo "      \"details\": $STATUS"
else
  echo "      \"status\": \"offline\""
fi
echo "    },"

# Test 4: FAITHH Adapter Backend
echo "    \"faithh_adapter_backend\": {"
if curl -s http://localhost:5557/ > /dev/null 2>&1; then
  echo "      \"status\": \"online\""
else
  echo "      \"status\": \"offline\""
fi
echo "    },"

# Test 5: GPU Status
echo "    \"gpus\": {"
if command -v nvidia-smi &> /dev/null; then
  echo "      \"available\": true,"
  
  # Get GPU info
  GPU_INFO=$(nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits 2>/dev/null || echo "")
  echo "      \"devices\": ["
  
  FIRST=true
  while IFS= read -r line; do
    if [ ! -z "$line" ]; then
      [ "$FIRST" = false ] && echo ","
      FIRST=false
      
      IFS=',' read -ra PARTS <<< "$line"
      echo "        {"
      echo "          \"index\": ${PARTS[0]},"
      echo "          \"name\": \"${PARTS[1]}\","
      echo "          \"memory_used_mb\": ${PARTS[2]},"
      echo "          \"memory_total_mb\": ${PARTS[3]},"
      echo "          \"utilization_percent\": ${PARTS[4]}"
      echo -n "        }"
    fi
  done <<< "$GPU_INFO"
  
  echo ""
  echo "      ]"
else
  echo "      \"available\": false"
fi
echo "    },"

# Test 6: Python imports (FAITHH dependencies)
echo "    \"python_imports\": {"

# Test imports
IMPORTS=(
  "chromadb"
  "google.generativeai"
  "flask"
  "flask_cors"
  "requests"
  "groq"
)

FIRST=true
for import in "${IMPORTS[@]}"; do
  [ "$FIRST" = false ] && echo ","
  FIRST=false
  
  echo -n "      \"$import\": "
  if python3 -c "import $import" 2>/dev/null; then
    echo -n "\"installed\""
  else
    echo -n "\"missing\""
  fi
done

echo ""
echo "    }"

echo "  },"

# Summary
echo "  \"summary\": {"
echo "    \"total_tests\": 6,"
echo "    \"passed\": \"TBD\","  # We'll calculate this
echo "    \"failed\": \"TBD\""
echo "  }"

echo "}"

# Save to file
) | tee "$REPORT_FILE"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test complete. Report saved to: $REPORT_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#!/bin/bash
# Batch embed all text files in a directory

if [ -z "$1" ]; then
    echo "Usage: ./batch_embed.sh <directory>"
    exit 1
fi

DIR="$1"
COUNT=0

echo "📚 Processing all documents in: $DIR"
echo ""

# Find all text files
find "$DIR" -type f \( -name "*.txt" -o -name "*.md" -o -name "*.html" \) | while read file; do
    echo "Processing: $file"
    python3 ~/ai-stack/rag_processor.py add "$file" 2>&1 | grep -E "Processing|Added|Created"
    COUNT=$((COUNT + 1))
    echo ""
done

echo "✅ Finished processing documents"
python3 ~/ai-stack/rag_processor.py list

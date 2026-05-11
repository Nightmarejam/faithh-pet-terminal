#!/bin/bash
# Quick FAITHH Project Scan
# Generates compact reports suitable for sharing

OUTPUT="discovery_quick_$(date +%Y%m%d_%H%M%S).txt"

{
    echo "FAITHH QUICK SCAN REPORT"
    echo "========================"
    echo "Date: $(date)"
    echo "Path: $(pwd)"
    echo ""
    
    echo "📁 DIRECTORY STRUCTURE (Top Level):"
    ls -lah | grep "^d" | awk '{print $9, "(" $5 ")"}'
    echo ""
    
    echo "🐍 PYTHON FILES (Important ones):"
    find . -maxdepth 2 -name "*backend*.py" -o -name "*api*.py" -o -name "*faithh*.py" 2>/dev/null | \
        xargs ls -lh 2>/dev/null | awk '{print $9, $5}'
    echo ""
    
    echo "🌐 HTML UI FILES:"
    find . -maxdepth 2 -name "*.html" 2>/dev/null | xargs ls -lh 2>/dev/null | awk '{print $9, $5}'
    echo ""
    
    echo "⚙️  CONFIG FILES:"
    ls -lh .env config.yaml docker-compose.yml 2>/dev/null | awk '{print $9, $5}'
    echo ""
    
    echo "📄 DOCUMENTATION:"
    find . -maxdepth 1 -name "*.md" -type f | sort
    echo ""
    
    echo "🔑 GEMINI API CHECK:"
    if [ -f .env ]; then
        echo ".env file exists"
        grep -i "gemini\|api_key" .env 2>/dev/null | sed 's/=.*/=***hidden***/' || echo "No Gemini key found in .env"
    else
        echo ".env file NOT FOUND"
    fi
    echo ""
    
    echo "🏠 HOME DIRECTORY (Potential orphans):"
    cd /home/jonat 2>/dev/null || cd ~
    ls -d */ 2>/dev/null | grep -v "^ai-stack" | head -10
    echo ""
    
    echo "💾 DISK USAGE:"
    cd /home/jonat/ai-stack 2>/dev/null || cd -
    du -sh . 2>/dev/null
    echo ""
    
} > "$OUTPUT"

echo "✅ Quick scan complete! Report saved to: $OUTPUT"
echo ""
echo "To share with Claude:"
echo "  cat $OUTPUT"
echo ""
cat "$OUTPUT"

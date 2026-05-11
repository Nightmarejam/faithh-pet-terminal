#!/bin/bash
# Show parity system status

echo "╔════════════════════════════════════════════════════╗"
echo "║   FAITHH Parity System Status                      ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

echo "📁 Parity Directory Structure:"
tree -L 2 parity/ 2>/dev/null || find parity/ -type d | sort

echo ""
echo "📊 Parity Files by Category:"
echo "  Backend: $(find parity/backend -name "PARITY_*.md" 2>/dev/null | wc -l) files"
echo "  Frontend: $(find parity/frontend -name "PARITY_*.md" 2>/dev/null | wc -l) files"
echo "  Config: $(find parity/configs -name "PARITY_*.md" 2>/dev/null | wc -l) files"
echo "  Docs: $(find parity/docs -name "PARITY_*.md" 2>/dev/null | wc -l) files"

echo ""
echo "📝 Recent Changes (from changelog):"
tail -20 parity/changelog/CHANGELOG.md | grep -E "^###|^-" | head -10

echo ""
echo "✅ Parity system operational!"

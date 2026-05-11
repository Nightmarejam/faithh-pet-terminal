#!/bin/bash
# scripts/map_dependencies.sh
# Maps out how files depend on each other

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="logs/inventory/dependencies_${TIMESTAMP}.md"

mkdir -p logs/inventory

cat > "$REPORT_FILE" << 'HEADER'
# FAITHH Dependency Map
Shows which files import/depend on which other files

---

HEADER

echo "Mapping dependencies..."

# Create a temporary file for the graph
TEMP_GRAPH="/tmp/faithh_deps_${TIMESTAMP}.dot"

echo "digraph FAITHH {" > "$TEMP_GRAPH"
echo "  rankdir=LR;" >> "$TEMP_GRAPH"
echo "  node [shape=box];" >> "$TEMP_GRAPH"
echo "" >> "$TEMP_GRAPH"

# Find all Python files
find . -name "*.py" -not -path "*/venv/*" -not -path "*/__pycache__/*" -not -path "*/archive/*" | while read -r file; do
  # Clean filename for display
  clean_name=$(echo "$file" | sed 's|^\./||' | sed 's|/|_|g' | sed 's|\.py$||')
  
  # Find imports from local files
  python3 -c "
import ast
import os

try:
    with open('$file', 'r') as f:
        tree = ast.parse(f.read())
        
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and not node.module.startswith(('sys', 'os', 'json', 'time', 'datetime')):
                # Check if it's a local import
                if not node.module.split('.')[0] in ['flask', 'chromadb', 'google', 'groq', 'anthropic', 'requests', 'typing', 'pathlib']:
                    module_name = node.module.replace('.', '_')
                    print(f'  \"$clean_name\" -> \"{module_name}\";')
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if not alias.name.split('.')[0] in ['sys', 'os', 'json', 'time', 'datetime', 'flask', 'chromadb', 'google', 'groq', 'anthropic', 'requests', 'typing', 'pathlib']:
                    module_name = alias.name.replace('.', '_')
                    print(f'  \"$clean_name\" -> \"{module_name}\";')
except:
    pass
" >> "$TEMP_GRAPH"
done

echo "}" >> "$TEMP_GRAPH"

# Convert to markdown format
echo "## Dependency Graph" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "\`\`\`" >> "$REPORT_FILE"

# Create text-based dependency list
echo "File Dependencies:" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

find . -name "*.py" -not -path "*/venv/*" -not -path "*/__pycache__/*" -not -path "*/archive/*" | sort | while read -r file; do
  echo "### $file" >> "$REPORT_FILE"
  
  # External dependencies
  echo "External packages:" >> "$REPORT_FILE"
  python3 -c "
import ast

try:
    with open('$file', 'r') as f:
        tree = ast.parse(f.read())
        
    external = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                pkg = alias.name.split('.')[0]
                external.add(pkg)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                pkg = node.module.split('.')[0]
                external.add(pkg)
    
    # Filter to known external packages
    known = ['flask', 'flask_cors', 'chromadb', 'google', 'groq', 'anthropic', 'requests', 'psutil', 'docker', 'ollama']
    found = sorted([e for e in external if e in known])
    
    if found:
        for pkg in found:
            print(f'  - {pkg}')
    else:
        print('  - (standard library only)')
        
except:
    print('  - (error parsing)')
" >> "$REPORT_FILE"
  
  # Local imports
  echo "" >> "$REPORT_FILE"
  echo "Local imports:" >> "$REPORT_FILE"
  python3 -c "
import ast
import os

try:
    with open('$file', 'r') as f:
        tree = ast.parse(f.read())
    
    local = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module:
                # Check if likely local (starts with ., or is in known local modules)
                if node.module.startswith('.') or node.module in ['backend', 'scripts', 'utils', 'config']:
                    local.add(node.module)
    
    if local:
        for mod in sorted(local):
            print(f'  - {mod}')
    else:
        print('  - (none)')
        
except:
    print('  - (error parsing)')
" >> "$REPORT_FILE"
  
  echo "" >> "$REPORT_FILE"
done

echo "\`\`\`" >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"
echo "---" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Summary statistics
echo "## Summary" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Count files by type
echo "### File Count by Location" >> "$REPORT_FILE"
echo "\`\`\`" >> "$REPORT_FILE"
echo "Backend files:" >> "$REPORT_FILE"
find . -path "*/backend/*.py" -not -path "*/venv/*" -not -path "*/__pycache__/*" | wc -l >> "$REPORT_FILE"
echo "Scripts:" >> "$REPORT_FILE"
find . -path "*/scripts/*.py" -not -path "*/venv/*" -not -path "*/__pycache__/*" | wc -l >> "$REPORT_FILE"
echo "Root level:" >> "$REPORT_FILE"
find . -maxdepth 1 -name "*.py" | wc -l >> "$REPORT_FILE"
echo "\`\`\`" >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"
echo "### Most Common External Dependencies" >> "$REPORT_FILE"
echo "\`\`\`" >> "$REPORT_FILE"

# Count external dependencies across all files
python3 << 'PYEOF' >> "$REPORT_FILE"
import ast
import os
from collections import Counter

all_imports = Counter()

for root, dirs, files in os.walk('.'):
    # Skip venv, pycache, archive
    dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', 'archive', '.git']]
    
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r') as f:
                    tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            pkg = alias.name.split('.')[0]
                            all_imports[pkg] += 1
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            pkg = node.module.split('.')[0]
                            all_imports[pkg] += 1
            except:
                pass

# Show top 10
for pkg, count in all_imports.most_common(10):
    print(f"{pkg}: {count} files")
PYEOF

echo "\`\`\`" >> "$REPORT_FILE"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Dependency mapping complete!"
echo "Report saved to: $REPORT_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

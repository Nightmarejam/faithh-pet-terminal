#!/bin/bash
# scripts/inventory_features.sh
# Analyzes each Python file to understand what features it provides

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="logs/inventory/features_${TIMESTAMP}.md"

mkdir -p logs/inventory

cat > "$REPORT_FILE" << 'HEADER'
# FAITHH Feature Inventory
Auto-generated feature analysis

---

HEADER

echo "Analyzing Python files for features..."

# Find all Python files in backend and root
find . -name "*.py" -not -path "*/venv/*" -not -path "*/__pycache__/*" -not -path "*/archive/*" | while read -r file; do
  echo "" >> "$REPORT_FILE"
  echo "## $file" >> "$REPORT_FILE"
  echo "" >> "$REPORT_FILE"
  
  # Extract docstring
  echo "### Description" >> "$REPORT_FILE"
  python3 -c "
import ast
import sys

try:
    with open('$file', 'r') as f:
        tree = ast.parse(f.read())
        docstring = ast.get_docstring(tree)
        if docstring:
            print(docstring)
        else:
            print('No module docstring')
except Exception as e:
    print(f'Error parsing: {e}')
" >> "$REPORT_FILE"
  
  echo "" >> "$REPORT_FILE"
  
  # Extract classes
  echo "### Classes" >> "$REPORT_FILE"
  python3 -c "
import ast

try:
    with open('$file', 'r') as f:
        tree = ast.parse(f.read())
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        if classes:
            for cls in classes:
                print(f'- {cls}')
        else:
            print('No classes defined')
except:
    print('Error parsing classes')
" >> "$REPORT_FILE"
  
  echo "" >> "$REPORT_FILE"
  
  # Extract functions/routes
  echo "### Functions/Routes" >> "$REPORT_FILE"
  python3 -c "
import ast

try:
    with open('$file', 'r') as f:
        tree = ast.parse(f.read())
        
        # Look for Flask routes
        routes = []
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if decorated with @app.route
                is_route = any(
                    isinstance(dec, ast.Call) and 
                    hasattr(dec.func, 'attr') and 
                    dec.func.attr == 'route'
                    for dec in node.decorator_list
                )
                
                if is_route:
                    # Try to get route path
                    for dec in node.decorator_list:
                        if isinstance(dec, ast.Call) and hasattr(dec.func, 'attr') and dec.func.attr == 'route':
                            if dec.args and isinstance(dec.args[0], ast.Constant):
                                route_path = dec.args[0].value
                                methods = []
                                for kw in dec.keywords:
                                    if kw.arg == 'methods' and isinstance(kw.value, ast.List):
                                        methods = [m.value for m in kw.value.elts if isinstance(m, ast.Constant)]
                                methods_str = ', '.join(methods) if methods else 'GET'
                                routes.append(f'{methods_str} {route_path} -> {node.name}()')
                else:
                    # Regular function
                    docstring = ast.get_docstring(node)
                    desc = docstring.split('\n')[0] if docstring else 'No description'
                    functions.append(f'{node.name}() - {desc[:60]}')
        
        if routes:
            print('**API Routes:**')
            for route in routes:
                print(f'- {route}')
        
        if functions:
            print('\n**Helper Functions:**')
            for func in functions[:10]:  # Limit to first 10
                print(f'- {func}')
        
        if not routes and not functions:
            print('No functions defined')
            
except Exception as e:
    print(f'Error: {e}')
" >> "$REPORT_FILE"
  
  echo "" >> "$REPORT_FILE"
  
  # Extract imports (dependencies)
  echo "### Key Dependencies" >> "$REPORT_FILE"
  python3 -c "
import ast

try:
    with open('$file', 'r') as f:
        tree = ast.parse(f.read())
        imports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
        
        # Filter to interesting imports
        interesting = ['flask', 'chromadb', 'google', 'groq', 'ollama', 'requests', 'anthropic']
        found = [imp for imp in imports if imp in interesting]
        
        if found:
            for imp in sorted(found):
                print(f'- {imp}')
        else:
            print('No major external dependencies')
            
except:
    print('Error parsing imports')
" >> "$REPORT_FILE"
  
  echo "" >> "$REPORT_FILE"
  echo "---" >> "$REPORT_FILE"
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Feature inventory complete!"
echo "Report saved to: $REPORT_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Quick summary:"
grep -E "^## \.|^### (Classes|Functions/Routes)" "$REPORT_FILE" | head -20

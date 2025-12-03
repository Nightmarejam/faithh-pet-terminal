#!/usr/bin/env python3
"""
Safely integrate Phase 2 blueprint into main backend
Adds just 3 lines to the backend
"""

with open('faithh_professional_backend_fixed.py', 'r') as f:
    lines = f.readlines()

# Backup
with open('faithh_professional_backend_fixed.py.backup_phase2_integration', 'w') as f:
    f.writelines(lines)

print("✅ Backup created")

# Find where to add import (after other imports)
import_added = False
for i, line in enumerate(lines):
    if 'from dotenv import load_dotenv' in line and not import_added:
        lines.insert(i + 1, 'from phase2_blueprint import create_phase2_blueprint\n')
        print(f"✅ Added import at line {i + 1}")
        import_added = True
        break

# Save after import addition
with open('faithh_professional_backend_fixed.py', 'w') as f:
    f.writelines(lines)

# Re-read to find registration point
with open('faithh_professional_backend_fixed.py', 'r') as f:
    lines = f.readlines()

# Find where to register blueprint (after ChromaDB initialization)
registration_added = False
for i, line in enumerate(lines):
    if 'CHROMA_CONNECTED = True' in line and not registration_added:
        # Add after this line
        indent = '    '
        blueprint_lines = [
            f'{indent}# Phase 2 Features\n',
            f'{indent}phase2_bp = create_phase2_blueprint(collection, CHROMA_CONNECTED, OLLAMA_HOST)\n',
            f'{indent}app.register_blueprint(phase2_bp)\n'
        ]
        for j, new_line in enumerate(blueprint_lines):
            lines.insert(i + 1 + j, new_line)
        print(f"✅ Added Phase 2 registration at line {i + 1}")
        registration_added = True
        break

# Save final version
with open('faithh_professional_backend_fixed.py', 'w') as f:
    f.writelines(lines)

print("✅ Phase 2 integrated!")
print("\nTest compilation:")
import subprocess
result = subprocess.run(['python', '-m', 'py_compile', 'faithh_professional_backend_fixed.py'], 
                       capture_output=True, text=True)
if result.returncode == 0:
    print("✅ Compilation successful!")
else:
    print("❌ Compilation error:")
    print(result.stderr)

print("\nRestart backend:")
print("  pkill -f faithh_professional_backend")
print("  python faithh_professional_backend_fixed.py > faithh_backend.log 2>&1 &")

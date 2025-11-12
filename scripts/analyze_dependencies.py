#!/usr/bin/env python3
"""
FAITHH Project Dependency Analyzer
Analyzes which files are actually being used in the project
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def find_imports(file_path):
    """Extract imports from a Python file"""
    imports = set()
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
            # Find regular imports
            import_pattern = r'^(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_\.]*)'
            for match in re.finditer(import_pattern, content, re.MULTILINE):
                imports.add(match.group(1).split('.')[0])
            
            # Find file references in strings
            file_pattern = r'["\']([a-zA-Z_][a-zA-Z0-9_]*\.py)["\']'
            for match in re.finditer(file_pattern, content):
                imports.add(match.group(1))
                
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return imports

def analyze_project(root_dir):
    """Analyze all Python files in the project"""
    root = Path(root_dir)
    
    # Track files and their dependencies
    files = {}
    dependencies = defaultdict(set)
    
    # Find all Python files
    for py_file in root.glob('*.py'):
        if py_file.name.startswith('.'):
            continue
            
        files[py_file.name] = {
            'path': str(py_file),
            'imports': find_imports(py_file),
            'imported_by': set()
        }
    
    # Build dependency graph
    for file_name, file_info in files.items():
        for imp in file_info['imports']:
            imp_file = f"{imp}.py"
            if imp_file in files:
                files[imp_file]['imported_by'].add(file_name)
                dependencies[file_name].add(imp_file)
    
    return files, dependencies

def categorize_files(files):
    """Categorize files by their role"""
    categories = {
        'Entry Points': [],
        'APIs': [],
        'Services': [],
        'UI': [],
        'Tests': [],
        'Utilities': [],
        'Unused': []
    }
    
    for file_name, file_info in files.items():
        # Categorize based on patterns
        if 'api' in file_name.lower():
            categories['APIs'].append(file_name)
        elif 'ui' in file_name.lower() or 'chat' in file_name.lower():
            categories['UI'].append(file_name)
        elif file_name.startswith('test_'):
            categories['Tests'].append(file_name)
        elif file_name in ['setup_rag.py', 'start_faithh.py']:
            categories['Entry Points'].append(file_name)
        elif len(file_info['imported_by']) == 0 and len(file_info['imports']) > 0:
            # Files that import others but aren't imported (potential entry points)
            categories['Entry Points'].append(file_name)
        elif len(file_info['imported_by']) == 0 and len(file_info['imports']) == 0:
            # Standalone files
            categories['Unused'].append(file_name)
        else:
            categories['Services'].append(file_name)
    
    return categories

def print_analysis(files, dependencies, categories):
    """Print the analysis results"""
    print("=" * 60)
    print("FAITHH PROJECT DEPENDENCY ANALYSIS")
    print("=" * 60)
    
    # Most imported files (core components)
    print("\n📊 CORE COMPONENTS (Most Imported):")
    print("-" * 40)
    sorted_by_imports = sorted(files.items(), 
                               key=lambda x: len(x[1]['imported_by']), 
                               reverse=True)
    
    for file_name, file_info in sorted_by_imports[:5]:
        if len(file_info['imported_by']) > 0:
            print(f"  {file_name}: imported by {len(file_info['imported_by'])} files")
            for importer in list(file_info['imported_by'])[:3]:
                print(f"    ← {importer}")
    
    # File categories
    print("\n📁 FILE CATEGORIES:")
    print("-" * 40)
    for category, file_list in categories.items():
        if file_list:
            print(f"\n{category}:")
            for f in sorted(file_list):
                print(f"  • {f}")
    
    # Potential redundancies
    print("\n⚠️ POTENTIAL REDUNDANCIES:")
    print("-" * 40)
    
    # Find similar named files
    api_files = [f for f in files if 'api' in f.lower()]
    if len(api_files) > 1:
        print(f"Multiple API files found: {', '.join(api_files)}")
    
    ui_files = [f for f in files if 'ui' in f.lower() or 'chat' in f.lower()]
    if len(ui_files) > 1:
        print(f"Multiple UI files found: {', '.join(ui_files)}")
    
    # Unused files
    print("\n🗑️ POSSIBLY UNUSED FILES:")
    print("-" * 40)
    for file_name, file_info in files.items():
        if (len(file_info['imported_by']) == 0 and 
            not file_name.startswith('test_') and
            file_name not in ['setup_rag.py', 'start_faithh.py']):
            print(f"  • {file_name} (not imported by any file)")
    
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS:")
    print("=" * 60)
    print("""
1. Review 'Unused' files - consider archiving if not needed
2. Consolidate similar APIs into a single unified API
3. Keep test files in a separate 'tests' directory
4. Move UI files to 'frontend' directory
5. Create clear entry point scripts in 'scripts' directory
""")

if __name__ == "__main__":
    import sys
    
    # Use current directory or provided path
    project_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print(f"Analyzing project in: {project_dir}")
    
    files, dependencies = analyze_project(project_dir)
    categories = categorize_files(files)
    print_analysis(files, dependencies, categories)

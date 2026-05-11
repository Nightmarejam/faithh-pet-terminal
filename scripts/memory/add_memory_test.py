#!/usr/bin/env python3
"""
Add Memory Test Endpoint
Adds /api/test_memory endpoint to verify memory loading
"""

from pathlib import Path

def create_test_endpoint():
    """Create test endpoint code"""
    
    endpoint = '''
@app.route('/api/test_memory', methods=['GET'])
def test_memory():
    """Test endpoint to verify memory loading"""
    try:
        memory = load_memory()
        memory_context = format_memory_context(memory)
        
        return jsonify({
            'success': True,
            'memory_loaded': True,
            'user_name': memory.get('user_profile', {}).get('name', 'Unknown'),
            'projects': list(memory.get('ongoing_projects', {}).keys()),
            'formatted_context': memory_context,
            'memory_file_exists': MEMORY_FILE.exists()
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500
'''
    
    return endpoint

def add_test_endpoint():
    """Add test endpoint to backend"""
    
    backend_path = Path.home() / "ai-stack/faithh_professional_backend_fixed.py"
    content = backend_path.read_text()
    
    # Check if already exists
    if "test_memory" in content:
        print("⏭️  Test endpoint already exists")
        return True
    
    # Find a good place to add it (after status endpoint)
    status_idx = content.find("@app.route('/api/status'")
    if status_idx != -1:
        # Find the end of the status function
        next_route = content.find("@app.route", status_idx + 10)
        if next_route != -1:
            # Insert before next route
            content = content[:next_route] + create_test_endpoint() + "\n" + content[next_route:]
            backend_path.write_text(content)
            print("✅ Test endpoint added")
            return True
    
    print("⚠️  Could not find insertion point")
    return False

def main():
    print("=" * 70)
    print("ADDING MEMORY TEST ENDPOINT")
    print("=" * 70)
    print()
    
    if add_test_endpoint():
        print()
        print("🔄 Restart backend:")
        print("   pkill -f faithh_professional_backend")
        print("   cd ~/ai-stack && source venv/bin/activate")
        print("   nohup python faithh_professional_backend_fixed.py > faithh_backend.log 2>&1 &")
        print()
        print("🧪 Test memory loading:")
        print("   curl http://localhost:5557/api/test_memory | python -m json.tool")
        print()
        print("This will show if:")
        print("  1. Memory file can be found")
        print("  2. Memory loads successfully")
        print("  3. Context formatting works")
        print("  4. What data is available")
        print()
    
    print("=" * 70)

if __name__ == "__main__":
    main()

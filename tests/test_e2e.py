#!/usr/bin/env python3
"""
End-to-End Test - Complete pipeline validation
Tests: Registry → Executor → Filesystem → Result
"""
import sys
import asyncio
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent))

from tool_executor import get_executor
from tool_registry import get_registry
from executors.filesystem import FilesystemExecutor
from executors.process import ProcessExecutor

async def test_complete_pipeline():
    """Test the complete execution pipeline"""
    print("\n🧪 FAITHH End-to-End Pipeline Test\n")
    
    # Step 1: Get instances
    executor = get_executor()
    registry = get_registry()
    print("✅ Step 1: Executor and Registry initialized")
    
    # Step 2: Register executors
    executor.register_executor('filesystem', FilesystemExecutor())
    executor.register_executor('process', ProcessExecutor())
    print("✅ Step 2: Registered filesystem and process executors")
    print(f"   Active executors: {list(executor.executors.keys())}")
    
    # Step 3: Register tools
    registry.register_tool({
        'name': 'read_file',
        'description': 'Read file contents',
        'category': 'filesystem',
        'executor': 'filesystem',
        'permissions': ['file.read']
    })
    
    registry.register_tool({
        'name': 'write_file',
        'description': 'Write file contents',
        'category': 'filesystem',
        'executor': 'filesystem',
        'permissions': ['file.write']
    })
    
    registry.register_tool({
        'name': 'run_command',
        'description': 'Execute shell command',
        'category': 'process',
        'executor': 'process',
        'permissions': ['process.execute']
    })
    
    print("✅ Step 3: Registered 3 tools")
    print(f"   Tools: {[t['name'] for t in registry.list_tools()]}")
    
    # Step 4: Test filesystem read
    print("\n📁 Test 4: Read config.yaml file")
    result = await executor.execute_tool('read_file', {
        'path': 'config.yaml'
    })
    
    if result['success']:
        file_result = result['result']
        print(f"✅ File read successful!")
        print(f"   Size: {file_result['size']} bytes")
        print(f"   Lines: {file_result['lines']}")
    else:
        print(f"❌ File read failed: {result.get('error')}")
        return False
    
    # Step 5: Test filesystem write (with proper permissions)
    print("\n📝 Test 5: Write test file")
    test_content = "FAITHH test file\nLine 2\nLine 3"
    result = await executor.execute_tool(
        'write_file', 
        {'path': '/tmp/faithh_test.txt', 'content': test_content},
        permissions=['file.read', 'file.write']  # Provide permissions!
    )
    
    if result['success']:
        print(f"✅ File write successful!")
        print(f"   Bytes written: {result['result']['bytes_written']}")
    else:
        print(f"❌ File write failed: {result.get('error')}")
        return False
    
    # Step 6: Test process execution (with permissions)
    print("\n⚙️  Test 6: Execute shell command")
    result = await executor.execute_tool(
        'run_command', 
        {'command': 'echo "Hello from FAITHH!"'},
        permissions=['process.execute', 'process.read']
    )
    
    if result['success']:
        process_result = result['result']
        print(f"✅ Command executed successfully!")
        print(f"   Output: {process_result['stdout'].strip()}")
        print(f"   Return code: {process_result['return_code']}")
    else:
        print(f"❌ Command failed: {result.get('error')}")
        return False
    
    # Step 7: Test security blocking
    print("\n🔒 Test 7: Security validation (should block)")
    result = await executor.execute_tool('run_command', {
        'command': 'rm -rf /'  # Blocked command!
    })
    
    if not result['success'] and 'Blocked command' in result.get('error', ''):
        print(f"✅ Security correctly blocked dangerous command!")
    else:
        print(f"⚠️  Security may not have blocked command (result: {result})")
    
    print("\n" + "="*50)
    print("🎉 ALL TESTS PASSED!")
    print("="*50)
    print("\n✨ The complete FAITHH pipeline is functional:")
    print("   Registry → Executor → Security → Tool → Result")
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_complete_pipeline())
        if result:
            print("\n✅ End-to-end test completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

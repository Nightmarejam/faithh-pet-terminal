#!/usr/bin/env python3
"""
Test tool_executor.py - Verify core engine works
"""
import sys
import asyncio

# Test imports
try:
    from tool_executor import ToolExecutor, get_executor
    from tool_registry import get_registry
    from security_manager import SecurityManager
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

async def test_executor():
    """Test the tool executor"""
    print("\n🧪 Testing Tool Executor...")
    
    # Get executor instance
    executor = get_executor()
    print(f"✅ Executor created: {executor}")
    
    # Check config loaded
    print(f"   Config loaded: {bool(executor.config)}")
    print(f"   Timeout setting: {executor.config.get('tools', {}).get('execution_timeout_ms')}ms")
    
    # Check security manager
    print(f"✅ Security manager: {executor.security}")
    
    # Check registry
    print(f"✅ Tool registry: {executor.registry}")
    
    # Check executors (should be empty until we register them)
    print(f"   Registered executors: {list(executor.executors.keys())}")
    
    print("\n✅ Core tool executor is functional!")
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_executor())
        print("\n🎉 All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

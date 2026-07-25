#!/usr/bin/env python3
"""
Test tool_executor.py - Verify core engine works
"""
import sys
import pytest
from pathlib import Path

# Add backend/ to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from tool_executor import ToolExecutor, get_executor
from tool_registry import get_registry
from security_manager import SecurityManager


def test_imports():
    """All tool system modules import successfully."""
    assert ToolExecutor is not None
    assert get_executor is not None
    assert get_registry is not None
    assert SecurityManager is not None


@pytest.mark.asyncio
async def test_executor_init():
    """Tool executor initializes with config, security, and registry."""
    executor = get_executor()
    assert executor is not None
    assert executor.security is not None
    assert executor.registry is not None
    # Check config loaded
    assert bool(executor.config)
    assert executor.config.get('tools', {}).get('execution_timeout_ms')
    # Executors dict should exist (may have pre-registered executors)
    assert isinstance(executor.executors, dict)


@pytest.mark.asyncio
async def test_registry_operations():
    """Tool registry can register and list tools."""
    registry = get_registry()
    registry.register_tool({
        'name': 'test_tool',
        'description': 'Test tool',
        'category': 'test',
        'executor': 'test',
        'permissions': ['test.read']
    })
    tools = registry.list_tools()
    assert any(t['name'] == 'test_tool' for t in tools)

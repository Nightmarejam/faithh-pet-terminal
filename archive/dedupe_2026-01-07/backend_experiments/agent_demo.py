#!/usr/bin/env python3
"""
Simple demo of Tool System with Ollama
Shows how the local AI agent will work
"""
import json
import requests
from tool_system import ToolSystem


def call_ollama(prompt: str, model: str = "qwen2.5-coder:7b") -> str:
    """
    Call Ollama with a prompt

    Args:
        prompt: The prompt to send
        model: Model to use

    Returns:
        Model response
    """
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )

    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(f"Ollama error: {response.text}")


def demo_manual_tool_use():
    """
    Demo: Manually using the tool system
    """
    print("=" * 60)
    print("DEMO 1: Manual Tool Use")
    print("=" * 60)

    tools = ToolSystem(workspace_root="/home/jonat/ai-stack")

    # Example 1: Read a file
    print("\n1. Reading README.md:")
    result = tools.read_file("README.md")
    if result["success"]:
        print(f"   ✓ Read {result['size']} bytes")
        print(f"   First 100 chars: {result['content'][:100]}...")
    else:
        print(f"   ✗ Error: {result['error']}")

    # Example 2: List directory
    print("\n2. Listing backend/ directory:")
    result = tools.list_directory("backend", "*.py")
    if result["success"]:
        print(f"   ✓ Found {result['count']} Python files:")
        for file in result['files'][:5]:  # Show first 5
            print(f"      - {file['name']} ({file['size']} bytes)")
    else:
        print(f"   ✗ Error: {result['error']}")

    # Example 3: Search code
    print("\n3. Searching for 'Flask' imports:")
    result = tools.search_code("from flask import", ".", "*.py")
    if result["success"]:
        print(f"   ✓ Found {result['count']} matches")
        for match in result['matches'][:3]:  # Show first 3
            print(f"      - {match['file']}:{match['line']}")
    else:
        print(f"   ✗ Error: {result['error']}")

    # Example 4: Get file info
    print("\n4. Getting info about tool_system.py:")
    result = tools.get_file_info("backend/tool_system.py")
    if result["success"]:
        print(f"   ✓ Name: {result['name']}")
        print(f"   ✓ Size: {result['size']} bytes")
        print(f"   ✓ Type: {result['type']}")
    else:
        print(f"   ✗ Error: {result['error']}")


def demo_ai_with_tools():
    """
    Demo: AI using tools (simulated)
    """
    print("\n" + "=" * 60)
    print("DEMO 2: AI Agent with Tools (Simulated)")
    print("=" * 60)

    tools = ToolSystem(workspace_root="/home/jonat/ai-stack")

    # Simulate AI deciding to use tools
    print("\nUser: 'What Python files are in the backend directory?'")
    print("\nAI thinking: I should use the list_directory tool...")

    # AI calls tool
    result = tools.execute_tool("list_directory", dirpath="backend", pattern="*.py")

    if result["success"]:
        print(f"\nAI: I found {result['count']} Python files in backend/:")
        for file in result['files']:
            print(f"  - {file['name']}")
    else:
        print(f"\nAI: Sorry, I got an error: {result['error']}")


def demo_ollama_simple():
    """
    Demo: Simple Ollama call (no tools)
    """
    print("\n" + "=" * 60)
    print("DEMO 3: Ollama Simple Call")
    print("=" * 60)

    print("\nAsking Ollama: 'Write a Python function to reverse a string'")

    try:
        response = call_ollama(
            "Write a simple Python function to reverse a string. Just the code, no explanation."
        )
        print("\nOllama response:")
        print(response)
    except Exception as e:
        print(f"\nError calling Ollama: {e}")
        print("Make sure Ollama is running: ollama serve")


def demo_tool_definitions():
    """
    Demo: Show tool definitions for function calling
    """
    print("\n" + "=" * 60)
    print("DEMO 4: Tool Definitions (for function calling)")
    print("=" * 60)

    tools = ToolSystem()
    definitions = tools.get_tool_definitions()

    print(f"\nAvailable tools: {len(definitions)}")
    print("\nTool definitions (OpenAI format):")
    print(json.dumps(definitions[0], indent=2))  # Show first tool


def demo_agent_loop_simulation():
    """
    Demo: Simulate a full agent loop
    """
    print("\n" + "=" * 60)
    print("DEMO 5: Agent Loop Simulation")
    print("=" * 60)

    tools = ToolSystem(workspace_root="/home/jonat/ai-stack")

    # User request
    user_request = "Find all Python files that import Flask"

    print(f"\nUser Request: {user_request}")

    # Step 1: AI plans
    print("\n[Agent] Planning approach:")
    print("  1. Search for 'from flask import' in Python files")
    print("  2. Compile results")
    print("  3. Report to user")

    # Step 2: AI executes tool
    print("\n[Agent] Executing: search_code")
    result = tools.search_code("from flask import", ".", "*.py")

    # Step 3: AI reports
    if result["success"]:
        print(f"\n[Agent] Found {result['count']} files importing Flask:")
        files_found = set(match['file'] for match in result['matches'])
        for file in files_found:
            print(f"  - {file}")
    else:
        print(f"\n[Agent] Error: {result['error']}")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("FAITHH Local AI Agent - Tool System Demo")
    print("=" * 60)

    # Demo 1: Manual tool use
    demo_manual_tool_use()

    # Demo 2: AI with tools (simulated)
    demo_ai_with_tools()

    # Demo 3: Simple Ollama call
    print("\nSkipping Ollama demo (requires Ollama running)")
    # Uncomment to test:
    # demo_ollama_simple()

    # Demo 4: Tool definitions
    demo_tool_definitions()

    # Demo 5: Agent loop simulation
    demo_agent_loop_simulation()

    print("\n" + "=" * 60)
    print("All demos completed!")
    print("=" * 60)

    print("\nNext steps:")
    print("1. Integrate tool calling with Ollama's function calling API")
    print("2. Build agent loop that iteratively uses tools")
    print("3. Add permission system for dangerous operations")
    print("4. Create UI for agent mode in FAITHH")

    print("\nSee LOCAL_AI_AGENT_ROADMAP.md for full plan")


if __name__ == "__main__":
    main()

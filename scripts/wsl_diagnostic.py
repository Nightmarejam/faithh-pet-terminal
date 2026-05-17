#!/usr/bin/env python3
"""WSL/Windsurf environment diagnostic check."""
import sys
import os

print("=" * 50)
print("WSL ENVIRONMENT DIAGNOSTIC")
print("=" * 50)

print(f"\n1. Python: {sys.executable}")
print(f"   Version: {sys.version}")

print(f"\n2. Working Directory: {os.getcwd()}")
print(f"   Home: {os.environ.get('HOME', 'NOT SET')}")
print(f"   User: {os.environ.get('USER', 'NOT SET')}")

print("\n3. Virtual Environment:")
venv = os.environ.get('VIRTUAL_ENV', 'NOT ACTIVE')
print(f"   VIRTUAL_ENV: {venv}")

print("\n4. Key Imports:")
imports_ok = []
imports_fail = []

for mod in ['flask', 'chromadb', 'requests', 'yaml', 'numpy']:
    try:
        __import__(mod)
        imports_ok.append(mod)
    except ImportError as e:
        imports_fail.append(f"{mod}: {e}")

print(f"   OK: {', '.join(imports_ok)}")
if imports_fail:
    print(f"   FAIL: {imports_fail}")

print("\n5. Network Connectivity:")
import socket
tests = [
    ("localhost:5557", "FAITHH Backend"),
    ("192.158.1.10:8000", "ChromaDB Gen8"),
    ("127.0.0.1:11434", "Ollama"),
]
for addr, name in tests:
    host, port = addr.split(":")
    try:
        s = socket.create_connection((host, int(port)), timeout=2)
        s.close()
        print(f"   ✅ {name} ({addr})")
    except Exception as e:
        print(f"   ❌ {name} ({addr}): {e}")

print("\n6. File Access:")
test_files = [
    "/home/jonat/ai-stack/faithh_professional_backend_fixed.py",
    "/home/jonat/ai-stack/faithh_pet_v4.html",
    "/home/jonat/ai-stack/CONTEXT.md",
]
for f in test_files:
    exists = os.path.exists(f)
    print(f"   {'✅' if exists else '❌'} {os.path.basename(f)}")

print("\n" + "=" * 50)
print("DIAGNOSTIC COMPLETE")
print("=" * 50)

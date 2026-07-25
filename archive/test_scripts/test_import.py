#!/usr/bin/env python3
try:
    from backend.llm_providers import call_anthropic_chat
    print("✅ Import successful")
except Exception as e:
    print(f"❌ Import failed: {e}")

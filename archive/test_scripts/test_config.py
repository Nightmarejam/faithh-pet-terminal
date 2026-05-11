#!/usr/bin/env python3
import yaml
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    print("✅ Config loaded successfully")
    print(f"Anthropic config: {config.get('ai', {}).get('anthropic', {})}")
except Exception as e:
    print(f"❌ Config failed: {e}")

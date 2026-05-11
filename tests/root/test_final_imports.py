#!/usr/bin/env python3
try:
    from secure_logging.secure_config import StructuredLogger
    from security.key_validator import APIKeyValidator
    print("✅ All imports successful")
    print("✅ Module import issue RESOLVED")
except ImportError as e:
    print(f"❌ Import failed: {e}")

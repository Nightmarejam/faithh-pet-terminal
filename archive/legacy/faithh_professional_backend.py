#!/usr/bin/env python3
"""DEPRECATED: Use faithh_professional_backend_fixed.py as the canonical backend entrypoint."""

import runpy


if __name__ == "__main__":
    # Forward execution to the canonical entrypoint while preserving CLI args.
    runpy.run_path("faithh_professional_backend_fixed.py", run_name="__main__")

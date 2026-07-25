#!/usr/bin/env python3
"""Print the first model ``id`` from an OpenAI-compatible ``/v1/models`` endpoint (vLLM, etc.).

Usage on faithh (after vLLM is listening):

  cd ~/ai-stack
  ./venv/bin/python scripts/ops/print_first_vllm_model_id.py
  ./venv/bin/python scripts/ops/print_first_vllm_model_id.py --url http://127.0.0.1:8010/v1/models

Paste the printed string into configs/model_config.yaml under providers.local_webui.model.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--url",
        default="http://127.0.0.1:8000/v1/models",
        help="Full URL to GET (default: %(default)s)",
    )
    args = p.parse_args()
    try:
        with urllib.request.urlopen(args.url, timeout=15) as resp:
            body = json.load(resp)
    except urllib.error.URLError as e:
        print(f"error: could not reach {args.url}: {e}", file=sys.stderr)
        if "111" in str(e) or "Connection refused" in str(e):
            print(
                "hint: nothing is listening on that host:port — start vLLM first, or use "
                "a different port (--url http://127.0.0.1:PORT/v1/models). "
                "Check: ss -tlnp | grep -E ':8000|:8010'",
                file=sys.stderr,
            )
        return 2
    except json.JSONDecodeError as e:
        print(f"error: not JSON from {args.url}: {e}", file=sys.stderr)
        return 3
    data = body.get("data") or []
    if not data:
        print("error: empty data[] in response", file=sys.stderr)
        return 4
    mid = data[0].get("id")
    if not mid:
        print("error: first entry has no id", file=sys.stderr)
        return 5
    print(mid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

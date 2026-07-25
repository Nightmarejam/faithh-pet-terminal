#!/usr/bin/env python3
from __future__ import annotations

import json
from strategy.executor import run_dry_strategy


if __name__ == "__main__":
    result = run_dry_strategy()
    print(json.dumps(result, indent=2))

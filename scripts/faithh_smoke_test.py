#!/usr/bin/env python3
"""
FAITHH smoke test for critical endpoints.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request


DEFAULT_BACKEND_URL = os.environ.get("FAITHH_BACKEND_URL", "http://localhost:5557")
FILESYSTEM_TOKEN = os.environ.get("FAITHH_FILESYSTEM_TOKEN")


def build_url(base_url, path):
    return f"{base_url.rstrip('/')}{path}"


def request_json(method, url, payload=None, headers=None, timeout=10):
    data = None
    headers = headers or {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            return response.status, body, time.time() - start
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8") if exc.fp else ""
        return exc.code, body, time.time() - start
    except urllib.error.URLError as exc:
        return None, str(exc), time.time() - start


def parse_json(body):
    if not body:
        return None
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {"raw": body}


def print_result(name, ok, status, elapsed, detail=None):
    state = "OK" if ok else "FAIL"
    print(f"[{state}] {name} ({status}) {elapsed:.2f}s")
    if detail:
        print(f"       {detail}")


def main():
    parser = argparse.ArgumentParser(description="FAITHH smoke test")
    parser.add_argument("--backend", default=DEFAULT_BACKEND_URL, help="Backend base URL")
    parser.add_argument("--model", default=os.environ.get("DEFAULT_MODEL", "llama3.1:8b"))
    parser.add_argument("--include-filesystem", action="store_true", help="Run filesystem list test")
    args = parser.parse_args()

    failures = 0
    base_url = args.backend

    # /health
    status, body, elapsed = request_json("GET", build_url(base_url, "/health"))
    ok = status == 200
    print_result("GET /health", ok, status, elapsed)
    failures += 0 if ok else 1

    # /api/status
    status, body, elapsed = request_json("GET", build_url(base_url, "/api/status"))
    ok = status == 200
    print_result("GET /api/status", ok, status, elapsed)
    failures += 0 if ok else 1

    # /api/chat ping
    payload = {"message": "ping", "model": args.model}
    status, body, elapsed = request_json("POST", build_url(base_url, "/api/chat"), payload=payload, timeout=20)
    data = parse_json(body)
    ok = status == 200 and isinstance(data, dict) and data.get("response") == "pong"
    detail = None
    if not ok:
        detail = body[:200] if body else "no response"
    print_result("POST /api/chat (ping)", ok, status, elapsed, detail=detail)
    failures += 0 if ok else 1

    # /api/pulse/status
    status, body, elapsed = request_json("GET", build_url(base_url, "/api/pulse/status"))
    ok = status == 200
    if status == 503:
        print_result("GET /api/pulse/status", True, status, elapsed, detail="PULSE unavailable")
    else:
        print_result("GET /api/pulse/status", ok, status, elapsed)
        failures += 0 if ok else 1

    # /api/pulse/chips
    status, body, elapsed = request_json("GET", build_url(base_url, "/api/pulse/chips"))
    ok = status == 200
    if status == 503:
        print_result("GET /api/pulse/chips", True, status, elapsed, detail="PULSE unavailable")
    else:
        print_result("GET /api/pulse/chips", ok, status, elapsed)
        failures += 0 if ok else 1

    # /api/filesystem/capabilities
    status, body, elapsed = request_json("GET", build_url(base_url, "/api/filesystem/capabilities"))
    ok = status == 200
    print_result("GET /api/filesystem/capabilities", ok, status, elapsed)
    failures += 0 if ok else 1

    # Optional filesystem list
    if args.include_filesystem:
        headers = {}
        if FILESYSTEM_TOKEN:
            headers["X-FAITHH-TOKEN"] = FILESYSTEM_TOKEN
        payload = {"action": "list", "path": ".", "options": {"depth": 1}}
        status, body, elapsed = request_json(
            "POST", build_url(base_url, "/api/filesystem"), payload=payload, headers=headers
        )
        data = parse_json(body)
        ok = status == 200 and isinstance(data, dict) and data.get("success") is True
        detail = None
        if not ok:
            detail = body[:200] if body else "no response"
        print_result("POST /api/filesystem (list)", ok, status, elapsed, detail=detail)
        failures += 0 if ok else 1

    if failures:
        print(f"\nSmoke test failures: {failures}")
        sys.exit(1)
    print("\nSmoke test passed.")


if __name__ == "__main__":
    main()

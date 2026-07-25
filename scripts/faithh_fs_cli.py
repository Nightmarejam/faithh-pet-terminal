#!/usr/bin/env python3
"""
FAITHH filesystem CLI for backend endpoints.

Endpoints:
  GET  /health
  GET  /api/filesystem/capabilities
  POST /api/filesystem (actions: list, read, search, metadata)
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request


DEFAULT_BACKEND_URL = os.environ.get("FAITHH_BACKEND_URL", "http://localhost:5557")
FILESYSTEM_TOKEN = os.environ.get("FAITHH_FILESYSTEM_TOKEN")


def _build_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}{path}"


def _request_json(method: str, base_url: str, path: str, payload=None, timeout=30):
    url = _build_url(base_url, path)
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if FILESYSTEM_TOKEN:
        headers["X-FAITHH-TOKEN"] = FILESYSTEM_TOKEN
    request = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8") if exc.fp else ""
        payload = {}
        if body:
            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                payload = {"raw": body}
        if "success" not in payload:
            payload["success"] = False
        payload.setdefault("error", f"HTTP {exc.code}")
        payload["http_status"] = exc.code
        return payload
    except urllib.error.URLError as exc:
        return {"success": False, "error": f"Request failed: {exc}"}

    if not body:
        return {"success": True}

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {"success": False, "error": "Invalid JSON response", "raw": body}


def _unwrap_data(payload):
    if isinstance(payload, dict) and "data" in payload:
        return payload["data"]
    return payload


def _print_json(payload):
    print(json.dumps(payload, indent=2, sort_keys=True))


def _is_error(payload):
    return isinstance(payload, dict) and (
        payload.get("success") is False or bool(payload.get("error"))
    )


def _print_error(payload):
    if not isinstance(payload, dict):
        print(f"Error: {payload}")
        return
    message = payload.get("error") or payload.get("message") or "Request failed"
    print(f"Error: {message}")
    suggestions = payload.get("suggestions")
    if suggestions:
        print("Suggestions:")
        for suggestion in suggestions:
            print(f"- {suggestion}")


def _print_list(payload):
    if _is_error(payload):
        _print_error(payload)
        return

    data = _unwrap_data(payload)
    items = []
    if isinstance(data, dict):
        if "formatted" in data and isinstance(data["formatted"], list):
            items = data["formatted"]
        elif "items" in data and isinstance(data["items"], list):
            items = data["items"]
    if not items and isinstance(data, list):
        items = data

    if not items:
        print("No items returned.")
        return

    for item in items:
        if isinstance(item, str):
            print(item)
            continue
        name = item.get("name") or item.get("path") or ""
        item_type = item.get("type") or item.get("kind") or "item"
        size = item.get("size")
        suffix = f" ({size} bytes)" if isinstance(size, int) else ""
        print(f"{item_type}: {name}{suffix}")


def _print_read(payload):
    if _is_error(payload):
        _print_error(payload)
        return

    data = _unwrap_data(payload)
    if isinstance(data, dict) and "content" in data:
        print(data["content"])
        return
    if isinstance(data, str):
        print(data)
        return
    _print_json(payload)


def _print_search(payload):
    if _is_error(payload):
        _print_error(payload)
        return

    data = _unwrap_data(payload)
    results = None
    if isinstance(data, dict):
        for key in ("results", "matches", "items", "files"):
            if isinstance(data.get(key), list):
                results = data.get(key)
                break
    if results is None and isinstance(data, list):
        results = data

    if not results:
        print("No matches.")
        return

    for item in results:
        if isinstance(item, str):
            print(item)
        elif isinstance(item, dict):
            path = item.get("path") or item.get("name") or json.dumps(item)
            print(path)
        else:
            print(item)


def _print_metadata(payload):
    if _is_error(payload):
        _print_error(payload)
        return

    data = _unwrap_data(payload)
    if not isinstance(data, dict):
        _print_json(payload)
        return

    for key in ("path", "type", "size", "modified", "created", "readable", "writable"):
        if key in data:
            print(f"{key}: {data[key]}")


def _print_health(health_payload, capabilities_payload):
    if _is_error(health_payload):
        print("Backend health:")
        _print_error(health_payload)
    else:
        status = health_payload.get("status") or ("ok" if health_payload.get("success", True) else "error")
        print(f"Backend health: {status}")

    if _is_error(capabilities_payload):
        print("Filesystem capabilities:")
        _print_error(capabilities_payload)
        return

    if isinstance(capabilities_payload, dict) and capabilities_payload:
        name = capabilities_payload.get("name", "filesystem")
        print(f"Filesystem capabilities: {name}")
        actions = capabilities_payload.get("actions")
        if isinstance(actions, dict) and actions:
            print("Actions:")
            for action, desc in actions.items():
                print(f"- {action}: {desc}")


def main():
    parser = argparse.ArgumentParser(description="FAITHH filesystem CLI")
    parser.add_argument(
        "--backend",
        default=DEFAULT_BACKEND_URL,
        help=f"Backend URL (default: {DEFAULT_BACKEND_URL})",
    )
    parser.add_argument("--json", action="store_true", help="Print raw JSON output")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("health", help="Check filesystem endpoint health")

    list_parser = subparsers.add_parser("list", help="List directory contents")
    list_parser.add_argument("path", nargs="?", default=".", help="Directory path")
    list_parser.add_argument("--depth", type=int, default=None, help="Listing depth")
    list_parser.add_argument("--hidden", action="store_true", help="Include hidden files")

    read_parser = subparsers.add_parser("read", help="Read file contents")
    read_parser.add_argument("path", help="File path")
    read_parser.add_argument("--max-lines", type=int, default=None, help="Max lines to read")

    search_parser = subparsers.add_parser("search", help="Search for files")
    search_parser.add_argument("pattern", help="Search pattern (e.g., *.md)")
    search_parser.add_argument("--path", default=None, help="Directory to search")
    search_parser.add_argument("--limit", type=int, default=None, help="Max results")

    metadata_parser = subparsers.add_parser("metadata", help="Show file metadata")
    metadata_parser.add_argument("path", help="File path")

    args = parser.parse_args()

    if args.command == "health":
        health_response = _request_json("GET", args.backend, "/health")
        capabilities_response = _request_json("GET", args.backend, "/api/filesystem/capabilities")
        if args.json:
            _print_json({"health": health_response, "filesystem_capabilities": capabilities_response})
        else:
            _print_health(health_response, capabilities_response)
        return 0

    if args.command == "list":
        payload = {"action": "list", "path": args.path}
        options = {}
        if args.depth is not None:
            options["depth"] = args.depth
        if args.hidden:
            options["include_hidden"] = True
        if options:
            payload["options"] = options
        response = _request_json("POST", args.backend, "/api/filesystem", payload)
        if args.json:
            _print_json(response)
        else:
            _print_list(response)
        return 0

    if args.command == "read":
        payload = {"action": "read", "path": args.path}
        if args.max_lines is not None:
            payload["options"] = {"max_lines": args.max_lines}
        response = _request_json("POST", args.backend, "/api/filesystem", payload)
        if args.json:
            _print_json(response)
        else:
            _print_read(response)
        return 0

    if args.command == "search":
        payload = {"action": "search", "path": args.pattern}
        if args.path:
            payload["dest"] = args.path
        if args.limit is not None:
            payload["options"] = {"limit": args.limit}
        response = _request_json("POST", args.backend, "/api/filesystem", payload)
        if args.json:
            _print_json(response)
        else:
            _print_search(response)
        return 0

    if args.command == "metadata":
        payload = {"action": "metadata", "path": args.path}
        response = _request_json("POST", args.backend, "/api/filesystem", payload)
        if args.json:
            _print_json(response)
        else:
            _print_metadata(response)
        return 0

    parser.error("Unknown command")


if __name__ == "__main__":
    sys.exit(main())

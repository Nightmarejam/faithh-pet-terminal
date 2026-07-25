#!/usr/bin/env python3
"""
FAITHH load/latency tester for /api/chat.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import mean


DEFAULT_BACKEND_URL = os.environ.get("FAITHH_BACKEND_URL", "http://localhost:5557")


def build_url(base_url, path):
    return f"{base_url.rstrip('/')}{path}"


def request_chat(url, payload, timeout):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            return response.status, body, time.time() - start, None
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8") if exc.fp else ""
        return exc.code, body, time.time() - start, None
    except Exception as exc:
        return None, None, time.time() - start, str(exc)


def percentile(values, pct):
    if not values:
        return None
    values = sorted(values)
    index = int(round((pct / 100.0) * (len(values) - 1)))
    return values[index]


def main():
    parser = argparse.ArgumentParser(description="FAITHH load test for /api/chat")
    parser.add_argument("--backend", default=DEFAULT_BACKEND_URL, help="Backend base URL")
    parser.add_argument("--requests", type=int, default=5, help="Total requests")
    parser.add_argument("--concurrency", type=int, default=1, help="Concurrent workers")
    parser.add_argument("--message", default="ping", help="Message to send")
    parser.add_argument("--model", default=os.environ.get("DEFAULT_MODEL", "llama3.1:8b"))
    parser.add_argument("--use-rag", action="store_true", help="Enable RAG usage")
    parser.add_argument("--timeout", type=int, default=120, help="Request timeout seconds")
    args = parser.parse_args()

    chat_url = build_url(args.backend, "/api/chat")
    payload = {
        "message": args.message,
        "model": args.model,
        "use_rag": args.use_rag,
    }

    durations = []
    errors = 0
    statuses = {}

    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = [
            executor.submit(request_chat, chat_url, payload, args.timeout)
            for _ in range(args.requests)
        ]
        for future in as_completed(futures):
            status, body, elapsed, err = future.result()
            durations.append(elapsed)
            statuses[status] = statuses.get(status, 0) + 1
            if err:
                errors += 1

    durations_sorted = sorted(durations)
    p50 = percentile(durations_sorted, 50)
    p95 = percentile(durations_sorted, 95)

    print("=== FAITHH Load Test ===")
    print(f"Requests:     {args.requests}")
    print(f"Concurrency:  {args.concurrency}")
    print(f"Message:      {args.message!r}")
    print(f"Use RAG:      {args.use_rag}")
    print(f"Avg latency:  {mean(durations_sorted):.2f}s")
    if p50 is not None:
        print(f"P50 latency:  {p50:.2f}s")
    if p95 is not None:
        print(f"P95 latency:  {p95:.2f}s")
    print(f"Statuses:     {statuses}")
    if errors:
        print(f"Errors:       {errors}")
        sys.exit(1)


if __name__ == "__main__":
    main()

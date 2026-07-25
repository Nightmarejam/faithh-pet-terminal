#!/usr/bin/env python3
"""
FAITHH Stress Test — Model Routing, Chip Activation, RAG, and Context Retention

Tests:
1. Provider routing: Does the system use the correct provider?
2. Chip activation: Do relevant chips fire for topic-specific queries?
3. RAG retrieval: Does RAG pull context when it should?
4. Context retention: Does the system maintain context within a session?
5. Intent detection: Are query intents classified correctly?

Output: Detailed report with pass/fail per test case.
"""

import json
import requests
import time
import sys
from datetime import datetime

BACKEND_URL = "http://localhost:5557"

# ─── Test Cases ───────────────────────────────────────────────

# Actual chip IDs/labels from the FAITHH system (from /api/ml/chips):
# faithh_core, constella_governance, infrastructure_docker, llm_ai_tools,
# audio_business, git_version_control, hardware_setup, coding_dotnet,
# file_management, coding_powershell, chromadb_indexing, personal_health,
# philosophy_universe, networking_security, server_gen8

REQUEST_DELAY = 3  # seconds between requests to avoid Groq 429 rate limiting

TEST_CASES = [
    # === Topic-specific chip activation (using ACTUAL chip labels) ===
    {
        "name": "LLM/AI query → llm_ai_tools",
        "query": "How do I fine-tune a language model with LoRA adapters using Ollama?",
        "expect_chips": ["llm", "ai", "faithh"],
        "expect_intent": ["technical"],
        "category": "chip_activation"
    },
    {
        "name": "Docker/Infra query → infrastructure_docker",
        "query": "How do I configure docker-compose for the ChromaDB and Ollama containers?",
        "expect_chips": ["infrastructure", "docker", "chromadb"],
        "expect_intent": ["technical"],
        "category": "chip_activation"
    },
    {
        "name": "Security query → networking_security",
        "query": "How should I configure firewall rules and SSH keys for secure remote access?",
        "expect_chips": ["networking", "security", "server"],
        "expect_intent": ["technical"],
        "category": "chip_activation"
    },
    {
        "name": "FAITHH project query → faithh_core",
        "query": "What is the FAITHH system architecture and how do the ML chips work?",
        "expect_chips": ["faithh", "core", "llm"],
        "expect_intent": ["project"],
        "category": "chip_activation"
    },
    {
        "name": "Server/Homelab query → server_gen8",
        "query": "How much disk space is left on the Gen8 server and what services are running?",
        "expect_chips": ["server", "gen8", "hardware"],
        "expect_intent": [],
        "category": "chip_activation"
    },
    {
        "name": "Audio/Business query → audio_business",
        "query": "What's the status of the Tom Cat Sound audio engineering business?",
        "expect_chips": ["audio", "business", "tom cat"],
        "expect_intent": ["project"],
        "category": "chip_activation"
    },

    # === RAG relevance ===
    {
        "name": "RAG: FAITHH project knowledge",
        "query": "What is FAITHH and what are its main components?",
        "expect_rag": True,
        "expect_chips": ["faithh", "core"],
        "expect_intent": ["project"],
        "category": "rag"
    },
    {
        "name": "RAG: General knowledge (RAG still used by design)",
        "query": "What is the capital of France?",
        "expect_rag": True,
        "expect_chips": [],
        "expect_intent": [],
        "category": "rag"
    },

    # === Provider routing ===
    {
        "name": "Default provider (should use env MODEL_PROVIDER=groq)",
        "query": "Explain Python list comprehensions briefly.",
        "provider": None,
        "expect_provider": "Groq",
        "category": "routing"
    },
    {
        "name": "Explicit Ollama override (tests model name mapping fix)",
        "query": "Describe the concept of polymorphism in OOP.",
        "provider": "ollama",
        "expect_provider": "Ollama",
        "category": "routing"
    },

    # === Context retention (sequential, same session) ===
    {
        "name": "Context: Establish topic",
        "query": "I'm working on a Flask application that needs WebSocket support. What library should I use?",
        "session_group": "context_test",
        "category": "context"
    },
    {
        "name": "Context: Follow-up (should remember Flask/WebSocket)",
        "query": "How do I integrate that with my existing app?",
        "session_group": "context_test",
        "category": "context",
        "context_check": ["flask", "websocket", "socket"]
    },
    {
        "name": "Context: Second follow-up",
        "query": "What about handling authentication in this setup?",
        "session_group": "context_test",
        "category": "context",
        "context_check": ["flask", "websocket", "socket", "auth"]
    },
]


def send_chat(query, provider=None, session_id=None, use_rag=True):
    """Send a chat request and return the full response data."""
    payload = {
        "message": query,
        "use_rag": use_rag,
    }
    if provider:
        payload["provider"] = provider
    if session_id:
        payload["session_id"] = session_id

    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/chat",
            json=payload,
            timeout=120
        )
        return resp.json()
    except requests.exceptions.Timeout:
        return {"success": False, "error": "TIMEOUT"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_chip_match(activated_chips, expect_keywords):
    """Check if any activated chip labels/IDs contain expected keywords."""
    if not expect_keywords:
        return True, "no chips expected"

    activated_labels = []
    for chip in (activated_chips or []):
        label = (chip.get("label", "") + " " + chip.get("id", "")).lower()
        activated_labels.append(label)

    for kw in expect_keywords:
        kw_lower = kw.lower()
        for label in activated_labels:
            if kw_lower in label:
                return True, f"matched '{kw}' in chips"

    return False, f"none of {expect_keywords} found in {activated_labels}"


def check_context_retention(response_text, keywords):
    """Check if the response references expected context keywords."""
    if not keywords:
        return True, "no context check"

    text_lower = response_text.lower()
    found = [kw for kw in keywords if kw.lower() in text_lower]
    if found:
        return True, f"found context refs: {found}"
    return False, f"none of {keywords} found in response"


def run_tests():
    """Run all test cases and collect results."""
    print("=" * 70)
    print("FAITHH STRESS TEST — Model Routing, Chips, RAG, Context")
    print(f"Backend: {BACKEND_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 70)

    # Check backend health
    try:
        health = requests.get(f"{BACKEND_URL}/health", timeout=5).json()
        print(f"Backend status: OK")
        print(f"Features: {health.get('features', [])}")
    except Exception as e:
        print(f"ERROR: Backend not reachable — {e}")
        sys.exit(1)

    # Check what provider is configured
    print(f"\n--- Configuration ---")
    try:
        status = requests.get(f"{BACKEND_URL}/api/status", timeout=5).json()
        current_model = status.get("current_model", {})
        print(f"Current model: {current_model.get('name', '?')}")
        print(f"Current provider: {current_model.get('provider', '?')}")
    except:
        print("Could not fetch /api/status")

    results = []
    session_ids = {}  # Track sessions for context tests

    print(f"\n--- Running {len(TEST_CASES)} test cases ---\n")

    for i, tc in enumerate(TEST_CASES):
        name = tc["name"]
        query = tc["query"]
        category = tc["category"]
        provider = tc.get("provider")

        # Handle session grouping for context tests
        session_id = None
        if tc.get("session_group"):
            session_id = session_ids.get(tc["session_group"])

        # Rate-limit delay between requests
        if i > 0:
            time.sleep(REQUEST_DELAY)

        print(f"[{i+1}/{len(TEST_CASES)}] {name}")
        print(f"   Query: {query[:70]}...")

        start = time.time()
        data = send_chat(query, provider=provider, session_id=session_id)
        elapsed = time.time() - start

        success = data.get("success", False)
        response_text = data.get("response", "")
        used_provider = data.get("provider", "?")
        used_model = data.get("model_used", "?")
        rag_used = data.get("rag_used", False)
        ml_chips = data.get("ml_chips_activated", [])
        returned_session = data.get("session_id")
        intent = data.get("intent_detected", {})

        # Store session for context tests
        if tc.get("session_group") and returned_session:
            session_ids[tc["session_group"]] = returned_session

        result = {
            "name": name,
            "category": category,
            "success": success,
            "provider": used_provider,
            "model": used_model,
            "rag_used": rag_used,
            "chips_activated": len(ml_chips),
            "chip_labels": [c.get("label", c.get("id", "?")) for c in ml_chips[:3]],
            "elapsed": round(elapsed, 2),
            "response_preview": response_text[:100] if response_text else "(empty)",
            "checks": {},
        }

        # === Run checks based on category ===

        if not success:
            result["checks"]["api_call"] = ("FAIL", data.get("error", "unknown error"))
            print(f"   ❌ API FAIL: {data.get('error', 'unknown')}")
        else:
            result["checks"]["api_call"] = ("PASS", f"{elapsed:.1f}s")

            # Chip activation check
            if "expect_chips" in tc and tc["expect_chips"]:
                chip_ok, chip_detail = check_chip_match(ml_chips, tc["expect_chips"])
                result["checks"]["chip_activation"] = ("PASS" if chip_ok else "WARN", chip_detail)
                if not chip_ok:
                    print(f"   ⚠️  Chip mismatch: {chip_detail}")

            # RAG check
            if "expect_rag" in tc:
                rag_ok = (rag_used == tc["expect_rag"])
                result["checks"]["rag"] = (
                    "PASS" if rag_ok else "WARN",
                    f"expected={'yes' if tc['expect_rag'] else 'no'}, got={'yes' if rag_used else 'no'}"
                )

            # Provider check
            if "expect_provider" in tc:
                prov_ok = (used_provider == tc["expect_provider"])
                result["checks"]["provider"] = (
                    "PASS" if prov_ok else "FAIL",
                    f"expected={tc['expect_provider']}, got={used_provider}"
                )
                if not prov_ok:
                    print(f"   ❌ Provider mismatch: expected {tc['expect_provider']}, got {used_provider}")

            # Context retention check
            if "context_check" in tc:
                ctx_ok, ctx_detail = check_context_retention(response_text, tc["context_check"])
                result["checks"]["context"] = ("PASS" if ctx_ok else "WARN", ctx_detail)
                if not ctx_ok:
                    print(f"   ⚠️  Context lost: {ctx_detail}")

        # Summary line
        status_icon = "✅" if all(c[0] == "PASS" for c in result["checks"].values()) else (
            "⚠️" if all(c[0] != "FAIL" for c in result["checks"].values()) else "❌"
        )
        chip_str = ", ".join(result["chip_labels"][:3]) if result["chip_labels"] else "none"
        print(f"   {status_icon} provider={used_provider} model={used_model} "
              f"rag={'✓' if rag_used else '✗'} chips=[{chip_str}] {elapsed:.1f}s")
        print()

        results.append(result)

    # === Summary Report ===
    print("\n" + "=" * 70)
    print("SUMMARY REPORT")
    print("=" * 70)

    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"pass": 0, "warn": 0, "fail": 0, "total": 0}
        categories[cat]["total"] += 1

        worst = "pass"
        for check_name, (status, _) in r["checks"].items():
            if status == "FAIL":
                worst = "fail"
            elif status == "WARN" and worst != "fail":
                worst = "warn"
        categories[cat][worst] += 1

    for cat, counts in categories.items():
        total = counts["total"]
        p, w, f = counts["pass"], counts["warn"], counts["fail"]
        bar = f"{'█' * p}{'▓' * w}{'░' * f}"
        print(f"  {cat:20s}  {bar}  {p}✅ {w}⚠️  {f}❌  ({total} tests)")

    total_pass = sum(c["pass"] for c in categories.values())
    total_warn = sum(c["warn"] for c in categories.values())
    total_fail = sum(c["fail"] for c in categories.values())
    total = sum(c["total"] for c in categories.values())

    print(f"\n  TOTAL: {total_pass}/{total} passed, {total_warn} warnings, {total_fail} failures")

    # Provider usage summary
    providers_used = {}
    for r in results:
        p = r["provider"]
        providers_used[p] = providers_used.get(p, 0) + 1
    print(f"\n  Providers used: {dict(providers_used)}")

    # Timing summary
    times = [r["elapsed"] for r in results if r["success"]]
    if times:
        print(f"  Response times: min={min(times):.1f}s avg={sum(times)/len(times):.1f}s max={max(times):.1f}s")

    # Save detailed results
    report_path = "/home/jonat/ai-stack/tests/stress_test_results.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "backend_url": BACKEND_URL,
            "test_count": total,
            "summary": {
                "pass": total_pass,
                "warn": total_warn,
                "fail": total_fail
            },
            "results": results
        }, f, indent=2)
    print(f"\n  Detailed results saved to: {report_path}")
    print("=" * 70)

    return total_fail == 0


import os

if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)

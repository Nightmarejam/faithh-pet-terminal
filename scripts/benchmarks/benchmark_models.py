#!/usr/bin/env python3
"""
FAITHH Model Benchmark Suite
============================
Benchmarks Ollama models for speed, reasoning, coding, and FAITHH-specific tasks.

Usage:
    python benchmark_models.py                    # Run all benchmarks on all models
    python benchmark_models.py --models llama31-faithh:latest qwen2.5-coder:14b
    python benchmark_models.py --tests speed reasoning
    python benchmark_models.py --quick            # Quick test (speed only, 1 iteration)

Requirements:
    pip install requests tabulate
"""

import argparse
import json
import time
import statistics
from datetime import datetime
from pathlib import Path
import requests

# Configuration
OLLAMA_URL = "http://localhost:11434"
FAITHH_URL = "http://localhost:5557"
RESULTS_DIR = Path(__file__).parent.parent / "docs" / "benchmark_results"

# Test prompts designed for your environment
BENCHMARKS = {
    "speed": {
        "name": "Speed Test",
        "description": "Measures response time for simple queries",
        "prompts": [
            {"name": "hello", "prompt": "Say hello in one sentence.", "max_tokens": 50},
            {"name": "count", "prompt": "Count from 1 to 5.", "max_tokens": 30},
        ],
        "iterations": 3,
    },
    "reasoning": {
        "name": "Reasoning Test", 
        "description": "Tests logical reasoning and problem-solving",
        "prompts": [
            {
                "name": "logic_puzzle",
                "prompt": """Solve this step by step:
A farmer has 17 sheep. All but 9 run away. How many sheep does the farmer have left?
Show your reasoning.""",
                "max_tokens": 200,
                "expected_contains": ["9"],
            },
            {
                "name": "sequence",
                "prompt": "What comes next in this sequence: 2, 6, 12, 20, 30, ? Explain your reasoning.",
                "max_tokens": 200,
                "expected_contains": ["42"],
            },
            {
                "name": "planning",
                "prompt": """I need to: 1) Deploy a Python app, 2) Set up a database, 3) Configure DNS, 4) Get SSL cert.
What's the optimal order and why? Be concise.""",
                "max_tokens": 300,
            },
        ],
        "iterations": 1,
    },
    "coding": {
        "name": "Coding Test",
        "description": "Tests code generation and debugging ability",
        "prompts": [
            {
                "name": "function_gen",
                "prompt": """Write a Python function called `find_duplicates` that takes a list and returns a list of duplicate elements.
Include type hints and a docstring. Keep it simple.""",
                "max_tokens": 300,
                "expected_contains": ["def find_duplicates", "list"],
            },
            {
                "name": "bug_fix",
                "prompt": """Fix this Python code:
```python
def factorial(n):
    if n = 0:
        return 1
    return n * factorial(n-1)
```
Show the corrected code only.""",
                "max_tokens": 200,
                "expected_contains": ["==", "factorial"],
            },
            {
                "name": "explain_code",
                "prompt": """Explain what this code does in 2-3 sentences:
```python
result = [x**2 for x in range(10) if x % 2 == 0]
```""",
                "max_tokens": 150,
                "expected_contains": ["square", "even"],
            },
        ],
        "iterations": 1,
    },
    "context": {
        "name": "Context Handling Test",
        "description": "Tests ability to handle and reference longer context",
        "prompts": [
            {
                "name": "summarize",
                "prompt": """Summarize the key points from this project description in 3 bullet points:

FAITHH (Friendly AI Teaching & Helping Hub) is a personal AI assistant system designed 
to help maintain project coherence across multiple long-term projects. It uses a RAG 
(Retrieval Augmented Generation) system with ChromaDB to store and retrieve conversation 
history and documentation. The system runs on WSL2 with a Gen8 home server hosting 
ChromaDB. Key features include multi-provider LLM support (Groq, Ollama, Gemini), 
real-time coherence detection, and a MegaMan Battle Network-inspired UI called PET Terminal.
The goal is to act as a 'digital compass' that helps users remember the 'why' behind 
each project when motivation wanes.""",
                "max_tokens": 200,
            },
        ],
        "iterations": 1,
    },
    "faithh_persona": {
        "name": "FAITHH Persona Test",
        "description": "Tests FAITHH-specific personality and context awareness",
        "prompts": [
            {
                "name": "self_intro",
                "prompt": "Introduce yourself as FAITHH. What is your purpose?",
                "max_tokens": 250,
                "expected_contains": ["FAITHH"],
            },
            {
                "name": "project_query",
                "prompt": "What do you know about the FAITHH project and its current status?",
                "max_tokens": 300,
                "use_rag": True,
            },
        ],
        "iterations": 1,
    },
}


def get_available_models():
    """Get list of models from Ollama."""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            return [m["name"] for m in response.json().get("models", [])]
    except Exception as e:
        print(f"Error getting models: {e}")
    return []


def run_ollama_query(model: str, prompt: str, max_tokens: int = 500, timeout: int = 120):
    """Run a query against Ollama and return timing + response."""
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": max_tokens}
            },
            timeout=timeout
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "response": data.get("response", ""),
                "elapsed": elapsed,
                "eval_count": data.get("eval_count", 0),
                "tokens_per_second": data.get("eval_count", 0) / elapsed if elapsed > 0 else 0,
            }
        else:
            return {"success": False, "error": f"HTTP {response.status_code}", "elapsed": elapsed}
            
    except requests.Timeout:
        return {"success": False, "error": "Timeout", "elapsed": timeout}
    except Exception as e:
        return {"success": False, "error": str(e), "elapsed": time.time() - start_time}


def run_faithh_query(model: str, prompt: str, use_rag: bool = False, timeout: int = 120):
    """Run a query against FAITHH backend."""
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{FAITHH_URL}/api/chat",
            json={
                "message": prompt,
                "model": model,
                "use_rag": use_rag
            },
            timeout=timeout
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": data.get("success", True),
                "response": data.get("response", ""),
                "elapsed": elapsed,
                "response_time": data.get("response_time", elapsed),
                "integrations_used": data.get("integrations_used", []),
            }
        else:
            return {"success": False, "error": f"HTTP {response.status_code}", "elapsed": elapsed}
            
    except Exception as e:
        return {"success": False, "error": str(e), "elapsed": time.time() - start_time}


def check_expected(response: str, expected_contains: list) -> bool:
    """Check if response contains expected strings (case-insensitive)."""
    response_lower = response.lower()
    return all(exp.lower() in response_lower for exp in expected_contains)


def run_benchmark(model: str, test_name: str, benchmark: dict) -> dict:
    """Run a single benchmark suite for a model."""
    results = {
        "model": model,
        "test": test_name,
        "test_name": benchmark["name"],
        "prompts": [],
        "total_time": 0,
        "avg_time": 0,
        "passed": 0,
        "failed": 0,
    }
    
    iterations = benchmark.get("iterations", 1)
    
    for prompt_config in benchmark["prompts"]:
        prompt_results = {
            "name": prompt_config["name"],
            "times": [],
            "tokens_per_second": [],
            "passed": False,
            "sample_response": "",
        }
        
        for i in range(iterations):
            # Use FAITHH backend for persona tests, Ollama for others
            if test_name == "faithh_persona":
                result = run_faithh_query(
                    model, 
                    prompt_config["prompt"],
                    use_rag=prompt_config.get("use_rag", False)
                )
            else:
                result = run_ollama_query(
                    model,
                    prompt_config["prompt"],
                    max_tokens=prompt_config.get("max_tokens", 300)
                )
            
            if result["success"]:
                prompt_results["times"].append(result["elapsed"])
                if "tokens_per_second" in result:
                    prompt_results["tokens_per_second"].append(result["tokens_per_second"])
                if i == 0:  # Save first response as sample
                    prompt_results["sample_response"] = result["response"][:500]
                    
                    # Check expected content
                    if "expected_contains" in prompt_config:
                        prompt_results["passed"] = check_expected(
                            result["response"], 
                            prompt_config["expected_contains"]
                        )
                    else:
                        prompt_results["passed"] = True
            else:
                prompt_results["times"].append(None)
                prompt_results["error"] = result.get("error", "Unknown error")
        
        # Calculate averages
        valid_times = [t for t in prompt_results["times"] if t is not None]
        if valid_times:
            prompt_results["avg_time"] = statistics.mean(valid_times)
            prompt_results["min_time"] = min(valid_times)
            prompt_results["max_time"] = max(valid_times)
            results["total_time"] += sum(valid_times)
            
        if prompt_results["tokens_per_second"]:
            prompt_results["avg_tps"] = statistics.mean(prompt_results["tokens_per_second"])
            
        if prompt_results["passed"]:
            results["passed"] += 1
        else:
            results["failed"] += 1
            
        results["prompts"].append(prompt_results)
    
    # Calculate overall average
    all_times = [p["avg_time"] for p in results["prompts"] if "avg_time" in p]
    if all_times:
        results["avg_time"] = statistics.mean(all_times)
    
    return results


def print_results(all_results: list, output_file: Path = None):
    """Print and optionally save benchmark results."""
    from tabulate import tabulate
    
    print("\n" + "=" * 80)
    print("FAITHH MODEL BENCHMARK RESULTS")
    print(f"Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Group by test
    by_test = {}
    for result in all_results:
        test = result["test"]
        if test not in by_test:
            by_test[test] = []
        by_test[test].append(result)
    
    for test_name, test_results in by_test.items():
        print(f"\n### {BENCHMARKS[test_name]['name']} ###")
        print(f"Description: {BENCHMARKS[test_name]['description']}")
        
        # Summary table
        summary_data = []
        for r in test_results:
            summary_data.append([
                r["model"],
                f"{r['avg_time']:.2f}s" if r.get("avg_time") else "N/A",
                f"{r['passed']}/{r['passed'] + r['failed']}",
                f"{r['total_time']:.2f}s"
            ])
        
        print(tabulate(
            summary_data,
            headers=["Model", "Avg Time", "Passed", "Total Time"],
            tablefmt="grid"
        ))
        
        # Detailed results
        print("\nDetailed Results:")
        for r in test_results:
            print(f"\n  {r['model']}:")
            for p in r["prompts"]:
                status = "✅" if p["passed"] else "❌"
                time_str = f"{p.get('avg_time', 0):.2f}s" if p.get("avg_time") else "FAILED"
                tps_str = f" ({p.get('avg_tps', 0):.1f} tok/s)" if p.get("avg_tps") else ""
                print(f"    {status} {p['name']}: {time_str}{tps_str}")
                if p.get("sample_response"):
                    preview = p["sample_response"][:100].replace("\n", " ")
                    print(f"       Preview: {preview}...")
    
    # Save to file if requested
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": all_results
            }, f, indent=2)
        print(f"\n📊 Results saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="FAITHH Model Benchmark Suite")
    parser.add_argument("--models", nargs="+", help="Models to test (default: all available)")
    parser.add_argument("--tests", nargs="+", choices=list(BENCHMARKS.keys()), 
                        help="Tests to run (default: all)")
    parser.add_argument("--quick", action="store_true", help="Quick mode: speed test only, 1 iteration")
    parser.add_argument("--save", action="store_true", help="Save results to JSON file")
    args = parser.parse_args()
    
    # Get models to test
    available_models = get_available_models()
    if not available_models:
        print("❌ No Ollama models found. Is Ollama running?")
        return
    
    models = args.models if args.models else available_models
    models = [m for m in models if m in available_models or ":" in m]
    
    if not models:
        print(f"❌ No valid models specified. Available: {available_models}")
        return
    
    # Get tests to run
    if args.quick:
        tests = ["speed"]
        for bench in BENCHMARKS.values():
            bench["iterations"] = 1
    else:
        tests = args.tests if args.tests else list(BENCHMARKS.keys())
    
    print(f"🔧 Models to test: {models}")
    print(f"📋 Tests to run: {tests}")
    print(f"⏱️  Starting benchmarks...\n")
    
    # Run benchmarks
    all_results = []
    for model in models:
        print(f"\n{'='*60}")
        print(f"Testing: {model}")
        print(f"{'='*60}")
        
        for test_name in tests:
            if test_name not in BENCHMARKS:
                continue
                
            print(f"  Running {BENCHMARKS[test_name]['name']}...", end=" ", flush=True)
            result = run_benchmark(model, test_name, BENCHMARKS[test_name])
            all_results.append(result)
            print(f"Done ({result['avg_time']:.2f}s avg)" if result.get('avg_time') else "Done")
    
    # Print results
    output_file = None
    if args.save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = RESULTS_DIR / f"benchmark_{timestamp}.json"
    
    print_results(all_results, output_file)
    
    # Summary recommendation
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    # Find fastest model for speed test
    speed_results = [r for r in all_results if r["test"] == "speed"]
    if speed_results:
        fastest = min(speed_results, key=lambda x: x.get("avg_time", float("inf")))
        print(f"⚡ Fastest overall: {fastest['model']} ({fastest['avg_time']:.2f}s avg)")
    
    # Find best for coding
    coding_results = [r for r in all_results if r["test"] == "coding"]
    if coding_results:
        best_coding = max(coding_results, key=lambda x: x["passed"])
        print(f"💻 Best for coding: {best_coding['model']} ({best_coding['passed']}/{best_coding['passed'] + best_coding['failed']} passed)")
    
    # Find best for reasoning
    reasoning_results = [r for r in all_results if r["test"] == "reasoning"]
    if reasoning_results:
        best_reasoning = max(reasoning_results, key=lambda x: x["passed"])
        print(f"🧠 Best for reasoning: {best_reasoning['model']} ({best_reasoning['passed']}/{best_reasoning['passed'] + best_reasoning['failed']} passed)")


if __name__ == "__main__":
    main()

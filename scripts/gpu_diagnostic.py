#!/usr/bin/env python3
"""
Diagnostic script for RTX 3090 + Ollama performance
Identifies bottlenecks in your specific setup
"""
import subprocess
import time
import json
import requests
from datetime import datetime

def check_gpu_config():
    """Check GPU configuration and availability"""
    print("="*70)
    print("GPU CONFIGURATION")
    print("="*70)
    
    try:
        # Get GPU info
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,name,memory.total,memory.free,memory.used,utilization.gpu,power.draw,power.limit",
             "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            check=True
        )
        
        for line in result.stdout.strip().split('\n'):
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 8:
                idx, name, total, free, used, util, power, limit = parts
                print(f"\nGPU {idx}: {name}")
                print(f"  Memory: {used}MB / {total}MB used ({free}MB free)")
                print(f"  Utilization: {util}%")
                print(f"  Power: {power}W / {limit}W")
                
                # Flag potential issues
                if name == "NVIDIA GeForce RTX 3090":
                    if float(used) > 20000:
                        print(f"  ⚠️  High memory usage - might be at capacity")
                    elif float(used) < 1000:
                        print(f"  ⚠️  Low memory usage - model might not be loaded")
                    else:
                        print(f"  ✅ Good memory state for 32B model")
                        
    except Exception as e:
        print(f"❌ Could not check GPU config: {e}")

def test_ollama_inference():
    """Test actual inference speed"""
    print("\n" + "="*70)
    print("OLLAMA INFERENCE SPEED TEST")
    print("="*70)
    
    test_cases = [
        {
            "name": "Small prompt (cold)",
            "prompt": "What is 2+2?",
            "expected_tokens": 5
        },
        {
            "name": "Medium prompt (warm)",
            "prompt": "Explain how Python decorators work in 2-3 sentences.",
            "expected_tokens": 50
        },
        {
            "name": "Large context (stress test)",
            "prompt": "Write a Python function to " + ("calculate fibonacci " * 100),
            "expected_tokens": 100
        }
    ]
    
    for test in test_cases:
        print(f"\n📊 Test: {test['name']}")
        print(f"   Prompt length: {len(test['prompt'])} chars")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5-coder:32b",
                    "prompt": test['prompt'],
                    "stream": False,
                    "options": {
                        "num_predict": test['expected_tokens']
                    }
                },
                timeout=60
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                tokens = len(data['response'].split())
                tokens_per_sec = tokens / elapsed if elapsed > 0 else 0
                
                print(f"   ✅ Time: {elapsed:.2f}s")
                print(f"   ✅ Speed: {tokens_per_sec:.1f} tokens/sec")
                print(f"   ✅ Output: {tokens} tokens")
                
                # Performance assessment for RTX 3090
                if tokens_per_sec < 5:
                    print(f"   ❌ CRITICAL: Very slow - something is wrong")
                    print(f"      Expected: 15-30 tokens/sec on RTX 3090")
                elif tokens_per_sec < 10:
                    print(f"   ⚠️  SLOW: Below expected performance")
                    print(f"      Expected: 15-30 tokens/sec on RTX 3090")
                elif tokens_per_sec < 15:
                    print(f"   ⚠️  FAIR: Could be better")
                else:
                    print(f"   ✅ GOOD: Within expected range")
                    
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except requests.Timeout:
            print(f"   ❌ TIMEOUT after 60s - severe performance issue")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(2)  # Brief pause between tests

def check_ollama_config():
    """Check Ollama's internal configuration"""
    print("\n" + "="*70)
    print("OLLAMA CONFIGURATION")
    print("="*70)
    
    try:
        # Check loaded models
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"\nLoaded models: {len(models)}")
            for model in models:
                print(f"  - {model.get('name')}: {model.get('size', 'unknown')} bytes")
    except Exception as e:
        print(f"Could not check Ollama config: {e}")

def check_cuda_visible_devices():
    """Check CUDA environment settings"""
    print("\n" + "="*70)
    print("CUDA ENVIRONMENT")
    print("="*70)
    
    import os
    cuda_visible = os.environ.get('CUDA_VISIBLE_DEVICES', 'Not set (using all GPUs)')
    print(f"CUDA_VISIBLE_DEVICES: {cuda_visible}")
    
    if cuda_visible == 'Not set (using all GPUs)':
        print("⚠️  Both GPUs are visible to Ollama")
        print("   Recommendation: Set to '0' to use only RTX 3090")
    elif cuda_visible == '0':
        print("✅ Using only GPU 0 (should be RTX 3090)")
    else:
        print(f"⚠️  Using GPU(s): {cuda_visible}")

def main():
    print("🔍 RTX 3090 + Ollama Performance Diagnostic")
    print(f"Timestamp: {datetime.now().isoformat()}\n")
    
    check_gpu_config()
    check_cuda_visible_devices()
    check_ollama_config()
    test_ollama_inference()
    
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)
    print("""
Expected Performance (RTX 3090 + qwen2.5-coder:32b):
  • Cold start: 15-25 tokens/sec
  • Warm: 20-30 tokens/sec
  
If you're seeing <10 tokens/sec, likely causes:
  1. Model split across both GPUs (inefficient)
     → Fix: export CUDA_VISIBLE_DEVICES=0
  
  2. CPU offloading happening
     → Fix: Check RAM usage during inference
     
  3. Thermal throttling
     → Fix: Check GPU temperature (should be <85°C)
     
  4. Other process using GPU
     → Fix: Check 'nvidia-smi' for other processes
     
  5. Network latency (ChromaDB on Gen8)
     → Fix: This is separate from GPU performance
     
To optimize:
  # Use only RTX 3090
  export CUDA_VISIBLE_DEVICES=0
  docker restart ollama
  
  # Or in ~/.bashrc
  echo 'export CUDA_VISIBLE_DEVICES=0' >> ~/.bashrc
""")

if __name__ == "__main__":
    main()

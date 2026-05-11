# vLLM Migration Roadmap

Research and migration path for transitioning from Ollama to vLLM for maximum inference performance.

---

## Current State

### Active Runtime: Ollama
- **Port:** 11434 (native systemd service)
- **Models:** deepseek-r1:32b (19GB), qwen25-grounded:latest (9GB)
- **Performance:** ~15-25 tok/s on RTX 3090
- **Format:** GGUF (quantized)

### Why Consider vLLM?
| Metric | Ollama | vLLM |
|--------|--------|------|
| Single-user throughput | 15-25 tok/s | 30-50 tok/s |
| Multi-user throughput | Limited | 35x better at peak |
| Memory efficiency | Good | Better (PagedAttention) |
| API compatibility | Custom REST | OpenAI-compatible |
| Setup complexity | Easy | Medium |

---

## vLLM Overview

### What is vLLM?
vLLM is a high-throughput, memory-efficient inference engine for LLMs. Key features:

- **PagedAttention:** Reduces memory fragmentation by 50%+, enabling longer contexts
- **Continuous Batching:** Dynamically batches requests for 2-4x throughput
- **OpenAI-compatible API:** Drop-in replacement for OpenAI client code
- **Tensor Parallelism:** Scale across multiple GPUs

### When vLLM Shines
- Serving multiple concurrent users
- Long context windows (32K+ tokens)
- Production deployments with SLAs
- When you need OpenAI API compatibility

### When Ollama is Better
- Rapid prototyping
- Single-user development
- Easy model management (`ollama pull`)
- Minimal setup

---

## Hardware Requirements

### RTX 3090 (24GB VRAM)
| Model Size | Quantization | VRAM Usage | Fits? |
|------------|--------------|------------|-------|
| 7-8B | FP16 | ~16GB | ✅ |
| 7-8B | AWQ/GPTQ | ~8GB | ✅ |
| 32B | FP16 | ~64GB | ❌ |
| 32B | AWQ 4-bit | ~18-20GB | ✅ |
| 70B | AWQ 4-bit | ~40GB | ❌ |

### For DeepSeek-R1-Distill-Qwen-32B
- **FP16:** Won't fit (needs ~64GB)
- **AWQ 4-bit:** Should fit (~18-20GB)
- **GPTQ 4-bit:** Should fit (~18-20GB)

---

## Installation Guide

### Prerequisites
```bash
# CUDA 11.8 or 12.x required
nvidia-smi  # Verify GPU visible

# Python 3.9-3.12
python3 --version
```

### Install vLLM
```bash
# Create separate venv (don't mix with FAITHH venv)
python3 -m venv ~/vllm-env
source ~/vllm-env/bin/activate

# Install vLLM
pip install vllm

# Verify installation
python -c "import vllm; print(vllm.__version__)"
```

### Download Quantized Model
```bash
# Option 1: Use HuggingFace model directly (vLLM downloads automatically)
# Option 2: Pre-download AWQ quantized version
pip install huggingface_hub
huggingface-cli download TheBloke/deepseek-coder-33B-instruct-AWQ
```

---

## Running vLLM

### Start Server
```bash
source ~/vllm-env/bin/activate

# Basic server (auto-downloads model)
vllm serve deepseek-ai/DeepSeek-R1-Distill-Qwen-32B \
  --dtype auto \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.9 \
  --port 8080

# With AWQ quantization (for 24GB GPU)
vllm serve TheBloke/deepseek-coder-33B-instruct-AWQ \
  --quantization awq \
  --dtype auto \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.9 \
  --port 8080
```

### Test API
```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100
  }'
```

---

## Backend Integration

### Minimal Change to llm_providers.py

vLLM uses OpenAI-compatible API, so integration is straightforward:

```python
# In backend/llm_providers.py

def call_vllm_chat(
    base_url: str,
    model: str,
    messages: List[Message],
    max_tokens: int = 512,
    temperature: float = 0.2,
    timeout_s: int = 120,
) -> Tuple[str, Optional[dict], dict]:
    """
    Calls vLLM's OpenAI-compatible endpoint.
    Same interface as call_openai_compatible_chat().
    """
    return call_openai_compatible_chat(
        base_url=base_url,
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        timeout_s=timeout_s,
    )
```

### Config Addition
```yaml
# config.yaml
ai:
  vllm:
    base_url: http://localhost:8080/v1
    model: deepseek-ai/DeepSeek-R1-Distill-Qwen-32B
    temperature: 0.2
    max_tokens: 2048
```

---

## Migration Phases

### Phase 1: Research (Current)
- [x] Document vLLM requirements
- [x] Identify model format needs
- [x] Estimate performance gains
- [ ] Test installation in separate venv

### Phase 2: Prototype (Next)
- [ ] Install vLLM
- [ ] Download AWQ-quantized 32B model
- [ ] Run basic inference test
- [ ] Benchmark vs Ollama (same model)

### Phase 3: Integration (If Phase 2 Successful)
- [ ] Add vLLM provider to llm_providers.py
- [ ] Update config.yaml with vLLM settings
- [ ] Add provider selection logic
- [ ] Test with FAITHH backend

### Phase 4: Production (Optional)
- [ ] Set up vLLM as systemd service
- [ ] Configure auto-restart
- [ ] Monitor memory usage
- [ ] Document operational procedures

---

## Alternatives to Consider

### ExLlamaV2
- **Faster than vLLM for single-user** (batch=1)
- Uses EXL2 quantization format
- Simpler setup than vLLM
- Good choice if you don't need multi-user

### llama.cpp (Already Built)
- Located at `ml/grounding_finetune/llama.cpp/`
- Uses GGUF format (same as Ollama)
- 10-20% faster than Ollama (no wrapper overhead)
- Could be integrated as alternative provider

---

## Decision Matrix

| Factor | Ollama | vLLM | ExLlamaV2 | llama.cpp |
|--------|--------|------|-----------|-----------|
| Setup | ✅ Easy | ⚠️ Medium | ⚠️ Medium | ⚠️ Medium |
| Single-user speed | ⚠️ | ✅ | ✅✅ | ✅ |
| Multi-user | ❌ | ✅✅ | ⚠️ | ⚠️ |
| Model format | GGUF | HF/AWQ | EXL2 | GGUF |
| API | Custom | OpenAI | Custom | Custom |
| Current status | ✅ Active | 📋 Research | 📋 Alternative | 🔧 Built |

---

## Recommendation

**For now:** Continue with Ollama. It's working, and the bottleneck is features, not inference speed.

**When to migrate:**
1. If you need to serve multiple users simultaneously
2. If inference speed becomes a measurable bottleneck
3. If you want native OpenAI API compatibility

**Alternative path:** If single-user speed is the goal, consider ExLlamaV2 instead of vLLM.

---

## References

- [vLLM Documentation](https://docs.vllm.ai/)
- [vLLM GitHub](https://github.com/vllm-project/vllm)
- [PagedAttention Paper](https://arxiv.org/abs/2309.06180)
- [AWQ Quantization](https://github.com/mit-han-lab/llm-awq)
- [ExLlamaV2](https://github.com/turboderp/exllamav2)

---

*Last Updated: 2026-03-01*
*Status: Research Phase*
*Priority: Background (does not block main development)*

# The definitive RTX 3090 local LLM guide for December 2025

**32B models are your ceiling, 14B-24B is the sweet spot, and quantization quality has reached the point where Q4_K_M produces near-native results.**

## Key Recommendations

### Reasoning Models
- **QwQ-32B** at Q4_K_M: ~20GB VRAM, 22 t/s, 12-15K context
- **DeepSeek-R1-Distill-32B** at Q4_K_M: ~19GB, 20-25 t/s
- **Mistral Small 24B** at Q4_K_M: ~24GB, **36K context** (best for RAG)

### Coding Models  
- **Qwen2.5-Coder-32B**: Matches GPT-4o at 73.7% on Aider benchmark
- **Qwen2.5-Coder-14B**: Beats Qwen2.5-72B general on code tasks

### Runtimes
- **ExLlamaV2**: 85% faster than llama.cpp (use via text-gen-webui)
- **Ollama**: Easiest setup, solid performance
- **vLLM**: Best for multi-user serving

### Embedding Models
- **BGE-M3**: Best all-around (~1GB VRAM, 8192 tokens)
- **Nomic Embed v1.5**: Most efficient (262MB VRAM)

*Full guide saved from Compass artifact*

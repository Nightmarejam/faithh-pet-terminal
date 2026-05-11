# The definitive RTX 3090 local LLM guide for December 2025

**32B models are your ceiling, 14B-24B is the sweet spot, and quantization quality has reached the point where Q4_K_M produces near-native results.** The RTX 3090 remains the best value proposition in local LLM hardware—its 24GB VRAM enables running GPT-4-class models locally with meaningful context lengths. For reasoning tasks, **QwQ-32B** at Q4_K_M delivers benchmark scores matching DeepSeek-R1 (a 671B parameter model) while generating 22 tokens/second. For coding, **Qwen2.5-Coder-32B** matches GPT-4o on the Aider benchmark at 73.7% while fitting comfortably in VRAM.

The local AI ecosystem has matured dramatically in late 2025. Community consensus on r/LocalLLaMA strongly favors the Qwen family for both reasoning and coding, with DeepSeek's distilled models punching well above their weight class. The runtime landscape has also stabilized—**ExLlamaV2** delivers 85% faster inference than llama.cpp for pure GPU workloads, while **Ollama** offers one-command simplicity for those prioritizing convenience over raw performance.

## Best reasoning models ranked by real-world capability

**QwQ-32B emerges as the consensus "king of consumer hardware reasoning"** in December 2025. This model achieves 79.5% on AIME24 math benchmarks (compared to 79.8% for the full DeepSeek-R1 at 671B parameters) and 73.1 on LiveBench, actually outperforming the vastly larger model on general reasoning tasks. At Q4_K_M quantization, it consumes approximately **19-20GB VRAM** and supports 12-15K context—enough for substantial conversations and document analysis.

The runner-up for reasoning is **DeepSeek-R1-Distill-Qwen-32B**, which outperforms OpenAI's o1-mini while requiring similar VRAM. For users needing longer context windows, the **DeepSeek-R1-Distill-Qwen-14B** variant offers an exceptional compromise—running at Q6_K or even Q8_0 quantization with **43,000+ tokens of context** while maintaining strong reasoning capabilities.

| Model | Quantization | VRAM | Context | Speed |
|-------|-------------|------|---------|-------|
| QwQ-32B | Q4_K_M | ~20GB | 12-15K | 22 t/s |
| DeepSeek-R1-Distill-32B | Q4_K_M | ~19GB | 12-15K | 20-25 t/s |
| Qwen3-32B | Q4_K_M | ~23GB | 12K | 22 t/s |
| Mistral Small 24B | Q4_K_M | ~24GB | **36K** | 30-35 t/s |
| DeepSeek-R1-Distill-14B | Q6_K | ~24GB | **43K** | 40 t/s |

For general chat and longer documents, **Mistral Small 24B** deserves special mention—it achieves **36,000 tokens of context** at Q4_K_M, making it ideal for RAG applications and document summarization where context length matters more than peak reasoning ability. The **Qwen3-30B-A3B** MoE model also performs excellently, activating only 3B parameters per forward pass for significantly faster inference (35 t/s) while fitting in 24GB.

A critical finding: **70B+ models are not practical for single-GPU 24GB setups**. Llama 3.3 70B at Q4 requires approximately 35GB, and while aggressive 2-2.5 bit quantization exists, quality degradation becomes substantial. Users consistently report that a well-quantized 32B model outperforms an aggressively quantized 70B model in practice.

## Coding models where specialized training pays dividends

**Qwen2.5-Coder-32B-Instruct stands alone as the best open-source coding model** that fits in consumer VRAM. Matching GPT-4o's 73.7% score on the Aider code editing benchmark, this model handles everything from autocomplete to complex multi-file refactoring. At Q4_K_M quantization, it runs at **37-40 tokens/second** on the RTX 3090—fast enough for interactive coding assistance.

The research reveals a crucial insight: **specialized coding models significantly outperform larger general models** for programming tasks. The Qwen2.5-Coder-14B surpasses Qwen2.5-72B (general) on code benchmarks despite being one-fifth the size. This specialization advantage comes from training on 5.5 trillion code tokens with Fill-in-the-Middle (FIM) training for autocomplete support.

For users needing longer context windows for repository-level understanding, **DeepSeek-Coder-V2-Lite (16B)** offers 60,000 tokens at Q4_K_M with support for 338 programming languages. The MoE architecture activates only 2.4B parameters per forward pass, making inference remarkably efficient. **Codestral 22B** from Mistral excels specifically at repository-level tasks and achieves strong RepoBench scores for large codebase navigation.

Quantization matters less for coding than many assume. Research shows Q4_K_M produces only +0.25 perplexity increase versus baseline, and studies on energy efficiency demonstrate that "moving from Q4 to FP16 yields only minimal accuracy gains at substantial energy cost." The practical recommendation: use Q4_K_M for most coding tasks, upgrading to Q5_K_M or Q6_K only for complex debugging scenarios where precision matters.

For IDE integration, the recommended setup combines **Qwen2.5-Coder-32B** for chat/complex tasks with **Qwen2.5-Coder-7B** (~4.7GB) for fast autocomplete. Continue (VS Code extension) and llama.vscode both support this dual-model configuration with Ollama backends.

## Inference runtimes compared head-to-head

The runtime landscape splits into three clear tiers based on your priorities: **ExLlamaV2 for maximum speed, Ollama for simplicity, and vLLM for multi-user serving**.

**ExLlamaV2** delivers the fastest single-user inference, clocking **85% faster token generation than llama.cpp** on RTX 3090. Testing with Llama-2-13B shows 56-64 tokens/second on ExLlamaV2 compared to 30-35 t/s on llama.cpp. The trade-off is complexity—it requires NVIDIA GPUs exclusively and works best through text-generation-webui rather than standalone. The EXL2 quantization format allows arbitrary bit-widths (3.0 to 8.0 bpw), enabling precise VRAM optimization.

**Ollama** has become the de facto standard for ease of use. A single command (`ollama run qwen2.5-coder:32b`) downloads and runs models instantly. Performance is solid at approximately **112 tokens/second on 8B Q4_K_M models**, using llama.cpp as its backend. The OpenAI-compatible REST API integrates seamlessly with Python through the official library or direct HTTP calls. The limitation: GGUF format only, no GPTQ/EXL2 support, and sequential processing limits multi-GPU scaling.

**vLLM** optimizes for throughput over single-request latency. PagedAttention enables serving **100 concurrent users at 12.88 t/s each** on RTX 3090, making it ideal for local API servers with multiple clients. The downside is aggressive VRAM pre-allocation (~90%) and optimization that favors datacenter GPUs over consumer cards.

**text-generation-webui (oobabooga)** offers maximum flexibility—it supports every quantization format (GGUF, GPTQ, AWQ, EXL2, HQQ) and can use ExLlamaV2 as a backend for best-in-class performance. Features include LoRA training, vision support, web search integration, and file attachments. For power users wanting one tool that does everything, this remains the top choice.

| Runtime | Best Speed | Ease | Python API | Formats | Best Use |
|---------|-----------|------|-----------|---------|----------|
| ExLlamaV2 | ⭐⭐⭐⭐⭐ | ⭐⭐ | Via wrapper | EXL2/GPTQ | Max speed |
| Ollama | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Excellent | GGUF | Quick start |
| vLLM | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Native | GPTQ/AWQ | Multi-user |
| text-gen-webui | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Good | All | Flexibility |
| LM Studio | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Basic | GGUF | GUI users |
| llama.cpp | ⭐⭐⭐⭐ | ⭐⭐⭐ | Server mode | GGUF | CPU/GPU hybrid |

For Python backends, all runtimes support OpenAI-compatible APIs. Ollama runs on port 11434, vLLM on 8000, LM Studio on 1234. A universal integration looks like:

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:11434/v1", api_key="not-needed")
```

## Multi-model setups and VRAM allocation reality

**Running two models simultaneously on 24GB is technically possible but rarely practical.** A 14B model at Q4_K_M consumes 8-9GB for weights, and an 8B model adds another 5GB. Adding KV cache for both models leaves virtually no room for meaningful context lengths. The community consensus from r/LocalLLaMA is clear: running one model well with adequate context beats running multiple constrained models.

The exception involves **embedding models for RAG**, which are lightweight enough to run alongside LLMs. BGE-M3 requires only ~1GB VRAM at FP16, and nomic-embed-text-v1.5 uses just 262MB. A practical RAG configuration runs the embedding model persistently while using Ollama to swap LLMs on demand.

**VRAM allocation follows predictable patterns.** Model weights dominate, but KV cache grows linearly with context length. For a 14B model at Q4_K_M with 32K context:

- Model weights: ~8-9GB
- KV cache: ~3-4GB  
- CUDA overhead: ~1GB
- System reserve: ~1GB
- Available headroom: ~6-10GB

**KV cache quantization is underutilized** and can double effective context length with minimal quality loss. Both llama.cpp and koboldcpp support Q8 key cache with Q4/Q5 value cache—enabling a 32B model to achieve 20K+ context where 12K would otherwise be the limit.

Common pitfalls from user reports include over-quantizing (using Q4 when Q5_K_M or Q6_K would fit), running display output through the GPU (use integrated graphics or run headless), and attempting partial CPU offloading (usually worse than using a smaller model fully on GPU).

## Embedding models have advanced far beyond all-mpnet-base-v2

**all-mpnet-base-v2 is now significantly outperformed by 2024-2025 models.** While still functional, its MTEB score of ~63-65% and 384-token maximum sequence length cannot compete with modern alternatives achieving 68-70%+ scores and 8192-token contexts. For new projects, migration is strongly recommended.

**BGE-M3** emerges as the top all-around choice for RAG. Supporting **dense, sparse, and multi-vector retrieval** simultaneously, it handles 100+ languages with an 8192-token context window. At ~1GB VRAM (FP16), it fits easily alongside any LLM. The hybrid retrieval capability means you can combine semantic search with keyword matching for improved accuracy.

**Nomic Embed v1.5** offers the best efficiency, requiring only **262MB VRAM** while supporting Matryoshka truncation—enabling storage of 256-dimensional vectors (3x smaller) with only ~10% quality degradation. The December 2024 **Nomic Embed v2-MoE** release introduced the first MoE embedding model, activating only 305M of 475M parameters while matching models twice its size.

**Jina Embeddings v3** provides task-specific optimization through LoRA adapters, allowing the same base model to optimize differently for query embedding versus document embedding. This matters for RAG where queries and documents benefit from different treatment.

For RTX 3090 RAG setups, the optimal configuration pairs **BGE-M3 or Nomic Embed v1.5** with a 14B-24B LLM. The embedding model's ~1GB footprint leaves ample room for context, and both models integrate seamlessly with popular frameworks like LangChain and LlamaIndex.

## Recommended configurations for different use cases

**Maximum reasoning capability**: QwQ-32B at Q4_K_M through text-generation-webui with ExLlamaV2 backend. Expect 22 t/s with 12-15K context—sufficient for complex multi-turn reasoning while approaching GPT-4-class performance on benchmarks.

**Coding workstation**: Qwen2.5-Coder-32B at Q4_K_M for chat, Qwen2.5-Coder-7B at Q4_K_M for autocomplete, both through Ollama. Configure Continue or llama.vscode to use the smaller model for tab completion and the larger model for chat interactions.

**RAG application**: Mistral Small 24B at Q4_K_M (for 36K context) with BGE-M3 embeddings, served through Ollama with Python integration. This configuration handles document ingestion, semantic search, and generation in a single-GPU setup.

**Balanced everyday use**: Qwen3-14B at Q5_K_M or Q6_K through Ollama. This allows **50,000+ tokens of context** with near-native quantization quality, 40+ t/s generation speed, and enough VRAM headroom for comfortable operation.

**Multi-user local server**: Deploy vLLM with Qwen2.5-32B-Instruct or Mistral Small 24B. PagedAttention enables efficient batching for multiple concurrent users, making this suitable for small team deployments.

The RTX 3090 at $700-900 used continues to offer the best price-to-VRAM ratio in December 2025—delivering 24GB versus the RTX 4090's similar 24GB at $1600+. For local LLM enthusiasts, this generation of hardware paired with the current quality of quantized models represents a practical path to AI independence without cloud dependencies or subscription costs.
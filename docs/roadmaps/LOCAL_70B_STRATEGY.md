# Local 70B Model Strategy for FAITHH

## Executive Summary

After cleaning up ~98GB of unnecessary models, we now have a streamlined setup:
- **qwen25-grounded:latest** (9GB) - Primary grounded model
- **llama3.3:70b** (42GB) - Heavy reasoning (slow but powerful)
- **gemini-2.0-flash-exp** (cloud) - Fast/cost efficient

## Current Status

### ✅ Completed
- Cleaned up 98GB of model bloat
- Updated config.yaml to use correct models
- Verified qwen25-grounded performance (18s load, 1.8s inference)

### ⚠️ Issues Identified
- llama3.3:70b is very slow to load (>30s timeout)
- Need llama.cpp for better local performance
- Missing intelligent model routing based on query complexity

## Strategic Options

### Option 1: Ollama-Only (Recommended for now)
**Pros:**
- Already working
- Simple integration
- qwen25-grounded is excellent for grounded responses

**Cons:**
- 70B model slow to load
- Less control over memory management

**Implementation:**
```yaml
# Use qwen25-grounded for 90% of queries
# Use llama3.3:70b for complex reasoning only
# Add intelligent routing in llm_providers.py
```

### Option 2: Hybrid Ollama + llama.cpp (Long-term goal)
**Pros:**
- Better performance for local 70B
- Full privacy control
- GPU offloading optimization

**Cons:**
- Complex setup
- CUDA configuration challenges
- Additional maintenance

**Implementation:**
```bash
# 1. Fix CUDA setup for llama.cpp
# 2. Download/convert 70B model to GGUF
# 3. Add llama.cpp provider to backend
# 4. Implement smart routing
```

### Option 3: Cloud-Heavy (Alternative)
**Pros:**
- No local resource constraints
- Always latest models
- Simple maintenance

**Cons:**
- Privacy concerns
- Ongoing costs
- Dependency on external services

## Recommended Implementation Plan

### Phase 1: Optimize Current Setup (Immediate)
1. **Update llm_providers.py** with intelligent routing
   - Simple queries → qwen25-grounded
   - Complex reasoning → llama3.3:70b
   - Fast/cost → gemini-2.0-flash

2. **Add query complexity detection**
   - Token count threshold
   - Intent-based routing
   - Performance monitoring

3. **Implement model warming strategy**
   - Pre-load 70B model during startup
   - Keep in memory for heavy sessions

### Phase 2: Add llama.cpp Support (Next Sprint)
1. **Fix CUDA configuration**
   - Proper CUDA toolkit installation
   - Environment variables setup
   - Build llama.cpp with GPU support

2. **Model acquisition**
   - Convert Ollama model to GGUF
   - Or download pre-quantized version
   - Test performance vs Ollama

3. **Integration**
   - Add llama.cpp provider
   - Compare performance metrics
   - Choose optimal setup

### Phase 3: Advanced Routing (Future)
1. **Semantic model selection**
   - Route based on query domain
   - Multi-model ensemble
   - Performance-based fallbacks

2. **Specialist models**
   - Code completion models
   - Mathematical reasoning
   - Creative writing

## Technical Requirements

### Hardware Analysis
- **RTX 3090**: 24GB VRAM (10GB used by Ollama, 14GB free)
- **System RAM**: 47GB available
- **Total**: ~67GB memory for 70B model

### Performance Targets
- **qwen25-grounded**: <2s response time ✅
- **llama3.3:70b**: <10s first response, <2s/token
- **llama.cpp 70B**: <5s first response, <1s/token

## Decision Matrix

| Factor | Ollama | llama.cpp | Cloud |
|--------|--------|-----------|--------|
| Privacy | ✅ | ✅✅ | ❌ |
| Performance | ⚠️ | ✅ | ✅✅ |
| Setup Complexity | ✅ | ❌ | ✅✅ |
| Maintenance | ✅ | ⚠️ | ✅✅ |
| Cost | ✅ | ✅ | ❌ |

## Next Actions

1. **This Week**: Implement intelligent routing in llm_providers.py
2. **Next Week**: Test llama.cpp CUDA setup
3. **Following Week**: Performance comparison and optimization

## Success Metrics

- Response time <5s for 90% of queries
- 70B model utilization for complex queries
- No degradation in grounded response quality
- Improved user satisfaction with thought partner capabilities

---

*Last Updated: 2026-02-22*
*Priority: High - Core to FAITHH v4 vision*

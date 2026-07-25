# GPU-Aware Model Routing Guide
**Date:** 2026-02-19  
**Version:** Phase 4 Week 1  
**Purpose:** Document the intelligent model selection system that optimizes for GPU availability and query complexity

---

## Overview

FAITHH's GPU-aware routing automatically selects the optimal language model based on:
1. **Query intent** (simple, coding, reasoning, complex)
2. **GPU availability** (gaming mode detection)
3. **Hardware constraints** (RTX 3090 vs GTX 1080 Ti)

This ensures fast responses for simple queries while leveraging powerful models for complex tasks, all while respecting gaming needs.

---

## Architecture

```
User Query → Intent Detection → GPU Check → Model Selection → LLM Inference
     ↓               ↓              ↓              ↓              ↓
  "Write code"   is_coding    is_gaming()   qwen2.5-coder  Response
```

### Key Components

1. **Intent Detection** (`backend/intent_detection.py`)
   - Analyzes query for patterns
   - Sets flags: `is_coding`, `is_reasoning`, `is_complex_query`
   - Uses regex patterns with word boundaries to reduce false positives

2. **GPU Awareness** (`faithh_professional_backend_fixed.py`)
   - `is_gaming_active()` - Checks for gaming/streaming processes
   - `select_gpu_aware_model()` - Chooses model based on intent + GPU state
   - Process monitoring via `psutil`

3. **UI Integration** (`faithh_pet_v4.html`)
   - Default model set to `'auto'`
   - Model selection indicator shows routing reason
   - Fallback to manual selection if needed

---

## Model Selection Logic

### Priority Order (Coding > Reasoning > Default)

```python
if is_coding:
    return "qwen2.5-coder:14b"  # Specialized for code
elif is_reasoning or is_complex:
    return "deepseek-r1:32b"   # Fast reasoning (32B)
else:
    return "qwen25-grounded:latest"  # Daily driver (14B)
```

### Gaming Mode Override

When gaming processes are detected:
```python
if is_gaming_active():
    return "llama3.1:8b"  # Lightweight, reserves RTX 3090
```

**Gaming Processes Monitored:**
- steam, Steam, STEAM
- obs, OBS, ObsStudio
- elgato, Elgato, GameCapture
- nvidia-settings, nvidia-smi

---

## Model Profiles

| Model | Size | Use Case | Strengths | Weaknesses |
|-------|------|----------|-----------|------------|
| **qwen25-grounded:latest** | 14B | Default/FAITHH context | Anti-hallucination, grounded | Slower than 8B |
| **qwen2.5-coder:14b** | 14B | Coding queries | Code generation, debugging | Not for general chat |
| **deepseek-r1:32b** | 32B | Reasoning | Fast, coherent reasoning | Larger VRAM usage |
| **llama3.1:8b** | 8B | Gaming mode | Fast, lightweight | Less capable |
| **llama3.3:70b** | 70B | Complex reasoning | Highest quality | Very slow, timeout issues |

---

## Intent Detection Patterns

### Coding Patterns (High Specificity)
```regex
r'\bwrite (a |some )?code\b'
r'\bcreate (a |some )?function\b'
r'\bdebug (this |my |the )?code\b'
r'\bparse (a |some |the )?json\b'
```

### Reasoning Patterns (Conceptual)
```regex
r'\bcompare (and|versus|vs)\b'
r'\banalyze\b'
r'\bphilosophical\b'
r'\bthe relationship between\b'
r'\bwhat if\b'
```

### Complex Query Detection
- Length > 100 characters
- Contains "and" or "or"
- Multi-part queries

---

## Configuration

### Backend Settings
```python
# Timeout increased for large models
OLLAMA_READ_TIMEOUT = 300  # 5 minutes

# GPU selection
CUDA_VISIBLE_DEVICES = "1"  # RTX 3090 only
```

### UI Settings
```javascript
// Default model
let currentModel = 'auto';

// Model options with auto mode
{ id: 'auto', label: '🔄 Auto-Select (GPU-Aware)', category: 'auto' }
```

---

## Testing the Routing

### Test Scenarios

```bash
# Simple query → qwen25-grounded:latest
curl -s http://localhost:5557/api/chat -X POST \
  -H "Content-Type: application/json" \
  -d '{"query":"Hello, how are you?", "model":"auto"}'

# Coding query → qwen2.5-coder:14b
curl -s http://localhost:5557/api/chat -X POST \
  -H "Content-Type: application/json" \
  -d '{"query":"Write a Python function to parse JSON", "model":"auto"}'

# Reasoning query → deepseek-r1:32b
curl -s http://localhost:5557/api/chat -X POST \
  -H "Content-Type: application/json" \
  -d '{"query":"Analyze the philosophical implications of AI", "model":"auto"}'
```

### Debug Output

Backend logs show:
```
🧠 Intent flags: reasoning=False, coding=True, complex=False
💻 Coding query - using coder model
🔄 GPU-Aware Model override: llama31-faithh:latest -> qwen2.5-coder:14b
```

---

## Performance Considerations

### Response Times (Approximate)
| Model | Simple Query | Complex Query | Coding |
|-------|--------------|---------------|--------|
| qwen25-grounded:latest | 1-2s | 5-10s | N/A |
| qwen2.5-coder:14b | N/A | N/A | 2-5s |
| deepseek-r1:32b | 2-3s | 10-20s | N/A |
| llama3.3:70b | 5-10s | 60-90s | N/A |

### GPU Memory Usage
| Model | VRAM Required | CPU Offload |
|-------|---------------|-------------|
| 8B | ~6GB | Minimal |
| 14B | ~10GB | Partial |
| 32B | ~20GB | Significant |
| 70B | ~40GB+ | Heavy |

---

## Troubleshooting

### Common Issues

1. **Model returns None**
   - Check backend logs for timeout
   - Verify model is downloaded: `ollama list`
   - Check GPU memory: `nvidia-smi`

2. **Wrong model selected**
   - Review intent flags in logs
   - Check pattern matching in `intent_detection.py`
   - Verify query doesn't contain ambiguous words

3. **Gaming mode not triggering**
   - Check process list: `ps aux | grep -i steam`
   - Verify gaming process names in code
   - Ensure psutil can access process info

4. **Slow responses**
   - Consider using smaller model for task
   - Check GPU utilization
   - Monitor system load

### Debug Commands

```bash
# Check model routing
tail -f /home/jonat/ai-stack/backend.log | grep "GPU-Aware"

# Test intent detection
python3 -c "
from backend.intent_detection import detect_query_intent
print(detect_query_intent('Write a Python function'))
"

# Monitor GPU
nvidia-smi -l 1
```

---

## Future Enhancements

### Phase 4 Roadmap
1. **ML Chip Integration** - Use semantic similarity for routing
2. **Multi-GPU Support** - Distribute models across GPUs
3. **Performance Monitoring** - Track response times per model
4. **Adaptive Selection** - Learn from user feedback

### Advanced Features
- Context-aware routing (project-specific models)
- User preference learning
- Dynamic timeout adjustment
- Model warmup for frequently used models

---

## Best Practices

1. **Trust the Auto-Router** - It's tuned for your hardware
2. **Override When Needed** - Manual selection available
3. **Monitor Performance** - Check logs for routing decisions
4. **Provide Feedback** - Help improve pattern matching

---

**Remember**: The goal is fast, accurate responses while respecting your gaming time. The router learns and improves with each interaction.

# UI Smart Routing Test Report

**Date:** 2026-01-19  
**Status:** Ready for Manual Testing  
**Backend:** ✅ Healthy  
**Models:** ✅ All 12 available  

---

## Pre-Test Results ✅

### Backend Health
- Status: Healthy
- All features enabled
- Responding correctly

### Model Availability
- Total models: 12
- Key models present:
  - ✅ llama31-faithh:latest (8.5 GB)
  - ✅ qwen3-faithh:latest (18 GB)
  - ✅ qwen25-coder-optimized:latest (9.0 GB)
  - ✅ deepseek-r1-optimized:latest (19 GB)

### Direct Model Test
- Tested llama31-faithh:latest via backend
- ✅ Responding in ~15 seconds
- Response quality: Good

---

## Manual UI Testing Instructions

### Step 1: Open UI
1. Open Chrome browser
2. Navigate to: `http://localhost:5557/`
3. Open DevTools (F12) → Console tab
4. Look for any JavaScript errors on load

### Step 2: Enable Auto-Routing
1. Find model dropdown (should show 6 options)
2. Select: "🔄 Auto-Select (Smart Routing)"
3. Console should show: `[Model] Auto-routing enabled`

### Step 3: Test Queries

#### Quick Queries (Expected: llama31-faithh)
| Query | Expected | Console Log | Pass/Fail | Notes |
|-------|----------|-------------|-----------|-------|
| "What's the capital of France?" | llama31-faithh | Intent: quick | | |
| "Hello, how are you?" | llama31-faithh | Intent: quick | | |
| "What time is it?" | llama31-faithh | Intent: quick | | |

#### Code Queries (Expected: qwen25-coder or qwen3-faithh)
| Query | Expected | Console Log | Pass/Fail | Notes |
|-------|----------|-------------|-----------|-------|
| "Write a Python function to find duplicates" | qwen25-coder | Intent: coding | | |
| "Debug this factorial function" | qwen25-coder | Intent: coding | | |
| "Create a React component" | qwen25-coder | Intent: coding | | |

#### Reasoning Queries (Expected: qwen3-faithh or deepseek-r1)
| Query | Expected | Console Log | Pass/Fail | Notes |
|-------|----------|-------------|-----------|-------|
| "Explain the trolley problem" | qwen3-faithh | Intent: reasoning | | |
| "Quantum computing implications" | qwen3-faithh | Intent: reasoning | | |
| "Compare Python vs JavaScript" | qwen3-faithh | Intent: reasoning | | |

#### Edge Cases
| Query | Expected | Console Log | Pass/Fail | Notes |
|-------|----------|-------------|-----------|-------|
| "" (empty) | llama31-faithh | Intent: general | | |
| "console.log('test');" | qwen25-coder | Intent: coding | | |
| Very long query (500+ chars) | varies | | | |

### Step 4: Visual Checks

For each test, verify:
- [ ] Auto-route info appears below model dropdown
- [ ] Format: `🔄 Auto-selected: [model] (reason)`
- [ ] Model switches smoothly in dropdown
- [ ] No JavaScript errors in console
- [ ] Response time reasonable (<30s)

---

## Console Log Examples

### Successful Auto-Routing
```
[Model] Auto-routing enabled
[Model] Intent detected: quick
[Model] Auto-selected: llama31-faithh:latest (simple query, using fastest model)
```

### Code Detection
```
[Model] Intent detected: coding
[Model] Auto-selected: qwen25-coder-optimized:latest (code-related query detected)
```

### Reasoning Detection
```
[Model] Intent detected: reasoning
[Model] Auto-selected: qwen3-faithh:latest (complex reasoning required)
```

---

## Troubleshooting

### If routing doesn't work:
1. Check if "auto" is in MODEL_OPTIONS array
2. Verify getEffectiveModel() function exists
3. Look for JavaScript errors in console

### If models are slow:
1. Check backend.log for errors
2. Verify Ollama models are loaded: `ollama list`
3. Check GPU memory usage

### If auto-route info doesn't show:
1. Check CSS for .auto-route-info
2. Verify routeInfo element is created
3. Check if message-header exists

---

## Test Results Template

Copy and paste this format for your results:

```markdown
## Test Results

### Quick Queries
| Query | Expected | Actual | Pass/Fail | Notes |
|-------|----------|--------|-----------|-------|
| "What's the capital of France?" | llama31-faithh | llama31-faithh | ✅ | Fast response |
| "Hello, how are you?" | llama31-faithh | qwen3-faithh | ⚠️ | Slower but works |

### Code Queries
| Query | Expected | Actual | Pass/Fail | Notes |
|-------|----------|--------|-----------|-------|
| [Add your results] | | | | |

### Issues Found
- [List any issues or unexpected behavior]

### Recommendations
- [Any improvements needed]
```

---

## Next Steps After Testing

1. **If all tests pass:** Proceed to Phase 2 (Update Documentation)
2. **If issues found:** Document and fix routing logic
3. **If models are slow:** Consider optimizing model selection

---

**Ready for manual testing!** 🚀

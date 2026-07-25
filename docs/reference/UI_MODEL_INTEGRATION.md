# UI Model Integration Guide

## Overview
The FAITHH UI (`faithh_pet_v4.html`) has specific locations where models are configured. When adding new models, update these sections:

## 1. Model List (line ~3334)
```javascript
// In the models array, add entries for category: 'faithh'
{
    id: 'qwen25-grounded:latest',
    label: '🎯 FAITHH Grounded (14B) - Anti-Hallucination',
    category: 'faithh'
}
```

## 2. Default Model Mapping (line ~3430)
```javascript
// In the defaultModelForProvider object
faithh: { model: 'qwen25-grounded:latest', reason: 'FAITHH context — grounded model (Qwen 2.5 14B)' }
```

## 3. Model Display Names (line ~5010)
```javascript
// In the modelDisplayNames object
'qwen25-grounded:latest': '🎯 Grounded (14B)',
```

## 4. Model Descriptions (Optional)
If adding descriptions, look for the modelDescriptions object around line 5000.

## Key Patterns
- **ID format**: Always include `:latest` suffix for Ollama models
- **Label format**: Use emoji + descriptive name + parameter count
- **Category**: Use `'faithh'` for FAITHH-specific models
- **Display name**: Short version for UI display

## Current Grounded Models
- `llama31-grounded:latest` - 8B parameters (Llama 3.1)
- `qwen25-grounded:latest` - 14B parameters (Qwen 2.5) [NEW]

## Testing After Changes
1. Open UI at http://localhost:5557/
2. Check model dropdown shows new model
3. Verify default selection works
4. Test a query to ensure model routing works

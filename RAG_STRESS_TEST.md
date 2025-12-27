# FAITHH RAG Stress Test Queries
**Purpose**: Verify knowledge base coverage across all projects and sources
**Date**: 2025-12-26

---

## Test Categories

### 🎯 Project-Specific Queries

**FAITHH/Technical:**
1. "What embedding dimensions have we used and why did we switch?"
2. "Explain the scaffolding system we built"
3. "What's the difference between FAITHH and FAITHH Lite?"
4. "What backend versions have we created?"

**Constella:**
5. "What is the Astris formula?"
6. "Explain the Penumbra Accord"
7. "What are the components of the Constella framework?"
8. "How does resonance work in Constella?"

**Tom Cat Sound:**
9. "What are the Tom Cat Sound pricing tiers?"
10. "Who are my partners in the audio business?"
11. "What equipment do we use for mastering?"

**Infrastructure:**
12. "How is my NAS organized?"
13. "What devices are on my Tailscale network?"
14. "What are the specs of the ProLiant Gen8?"

---

### 🔍 Cross-Source Queries (should pull from multiple AI sources)

15. "What decisions have I made about database choices?"
16. "What's my hardware ecosystem look like?"
17. "What have I worked on with AI assistants this month?"

---

### 🧠 Memory/Context Queries

18. "What was I working on in early December?"
19. "What gaps did we identify in FAITHH's capabilities?"
20. "What's the 'affordable but mighty' philosophy?"

---

### ⚡ Edge Cases

21. "What's the Harmony-AI bridge?" (already tested - worked!)
22. "Do you know my ADHD-related preferences?"
23. "What automation scripts have we created?"
24. "What's deferred until cash flow allows?"

---

## Scoring Guide

For each query, rate:
- **Relevance**: Did RAG find related content? (0-5)
- **Accuracy**: Was the response factually correct? (0-5)
- **Completeness**: Did it cover what you expected? (0-5)

**Target**: Average 4+ across all queries = RAG is solid

---

## Results Log

| # | Query (short) | RAG Used? | Relevance | Accuracy | Complete | Notes |
|---|---------------|-----------|-----------|----------|----------|-------|
| 1 | Embedding dims | | | | | |
| 2 | Scaffolding | | | | | |
| 3 | FAITHH vs Lite | | | | | |
| ... | ... | | | | | |

---

## Quick Test Commands (from service box)

```bash
# Test a query from command line
curl -s -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "YOUR QUERY HERE", "session_id": "test"}' | jq '.rag_used, .rag_results[:1]'
```

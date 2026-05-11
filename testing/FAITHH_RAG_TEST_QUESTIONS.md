# FAITHH RAG Test Questions
**Created**: 2025-12-30
**Purpose**: Validate that FAITHH can retrieve relevant context from the Gen 8 ChromaDB
**Collection**: faithh_knowledge_base (27,494 chunks, BGE-768 embeddings)

---

## How to Use These Tests

Each question targets specific indexed content. After asking FAITHH, verify:
1. Does the response reference the expected source material?
2. Is the information accurate and current?
3. Are multiple relevant chunks being retrieved?

---

## Test Category 1: Life Map & Personal Context

### Q1.1: Core Pattern
**Question**: "What are the three main ways I express harmony in my work?"
**Expected sources**: LIFE_MAP.md
**Should mention**: Constella (civic), Floating Garden Soundworks (audio), FAITHH (workflow)

### Q1.2: Current Priorities
**Question**: "What are my current project priorities and what path should I focus on?"
**Expected sources**: LIFE_MAP.md, project_states.json
**Should mention**: Path A/B/C options, FGS income vs FAITHH investment tradeoff

### Q1.3: Blocking Issues
**Question**: "What's actually blocking my progress according to my own documentation?"
**Expected sources**: LIFE_MAP.md
**Should mention**: "What should I work on right now", income vs building loop

---

## Test Category 2: Technical Infrastructure

### Q2.1: ChromaDB Setup
**Question**: "How is ChromaDB configured in my system and what embedding model does it use?"
**Expected sources**: CHROMADB_STATUS.md, ARCHITECTURE.md, backend docs
**Should mention**: BGE embeddings, 768 dimensions, collection names

### Q2.2: Gen 8 Server
**Question**: "What services are running on my Gen 8 server?"
**Expected sources**: GEN8_SERVICES_PLAN.md
**Should mention**: Pi-hole, Uptime Kuma, ChromaDB (note: doc may say "planned" - good test of staleness)

### Q2.3: Network Architecture
**Question**: "How are my devices connected and what are their Tailscale IPs?"
**Expected sources**: parity/network_infrastructure.md, docs with network info
**Should mention**: Windows desktop, MacBook, NAS, Gen 8

---

## Test Category 3: Constella Framework

### Q3.1: Token Mechanics
**Question**: "How do Astris and Auctor tokens work in Constella?"
**Expected sources**: Constella framework docs, RFCs
**Should mention**: Token types, governance mechanics, evidence levels

### Q3.2: Penumbra Accord
**Question**: "What is the Penumbra Accord and what's its purpose?"
**Expected sources**: Constella governance docs
**Should mention**: Mediation, repair, reintegration flow

### Q3.3: Harmony Module
**Question**: "What does the Harmony module in Constella do?"
**Expected sources**: constella.md, Harmony docs
**Should mention**: HRV/sleep/RPE protocol, wellness not medical

---

## Test Category 4: Audio/FGS Business

### Q4.1: Business Structure
**Question**: "What is the structure of Tom Cat Sound LLC and Floating Garden Soundworks?"
**Expected sources**: LIFE_MAP.md, tomcat project docs
**Should mention**: Oregon LLC, partners (Thomas, Kevin exiting), boutique mastering

### Q4.2: Audio Workflow
**Question**: "How does remote collaboration work with my South Dakota partner?"
**Expected sources**: audio.md, Audio workflow docs
**Should mention**: JackTrip/SonoBus, Luna DAW, M2 Mac Mini

### Q4.3: Equipment Setup
**Question**: "What audio equipment do I have for mastering work?"
**Expected sources**: Audio docs, tier documentation
**Should mention**: UAD interfaces, WaveLab, Sonarworks, headphone correction

---

## Test Category 5: Conversation History Recall

### Q5.1: Recent Discussions
**Question**: "What have I been discussing about ComfyUI and image generation?"
**Expected sources**: chatgpt conversations
**Should mention**: Workflows, GPU limitations (1080 Ti vs 3090), templates

### Q5.2: Technical Problem Solving
**Question**: "What issues have I worked through with FAITHH backend development?"
**Expected sources**: claude/chatgpt conversations
**Should mention**: RAG issues, embedding dimensions, ChromaDB queries

---

## Test Category 6: Cross-Domain Synthesis

### Q6.1: Big Picture
**Question**: "How do all my projects connect to my long-term vision?"
**Expected sources**: LIFE_MAP.md, Constella docs, FAITHH docs
**Should synthesize**: Farm/studio property, Constella pilots, FAITHH as coherence layer

### Q6.2: Decision Support
**Question**: "Based on everything you know about me, what should I focus on this week?"
**Expected sources**: Multiple - LIFE_MAP, project_states, recent conversations
**Should demonstrate**: Contextual awareness, priority understanding, practical suggestion

---

## Scoring Guide

For each question, rate FAITHH's response:

| Score | Criteria |
|-------|----------|
| ⭐⭐⭐⭐⭐ | Retrieves exact relevant content, accurate, well-synthesized |
| ⭐⭐⭐⭐ | Finds relevant content, mostly accurate, minor gaps |
| ⭐⭐⭐ | Partially relevant, some accuracy issues or missing context |
| ⭐⭐ | Tangentially related, significant gaps |
| ⭐ | Misses the point or retrieves irrelevant content |
| ❌ | No relevant retrieval or hallucinated response |

---

## Expected Issues (Known Gaps)

Based on indexing analysis, these queries may fail or underperform:

1. **Pre-October 2025 history** - Only Oct-Dec conversations indexed
2. **Windows-specific content** - 93k docs on offline Windows not accessible
3. **Stale documentation** - Some docs not updated (e.g., Gen 8 "planned" vs running)
4. **Recent session context** - Today's conversation not yet indexed

---

## After Testing

Document results in a test report:
```markdown
## FAITHH RAG Test Results - [DATE]

### Summary
- Tests run: X
- Pass (⭐⭐⭐+): X
- Partial (⭐⭐): X  
- Fail (⭐ or ❌): X

### Notable Issues
- [List specific retrieval failures]

### Recommendations
- [What needs to be indexed/updated]
```

---

*Test suite created Dec 30, 2025 for FAITHH knowledge base validation*

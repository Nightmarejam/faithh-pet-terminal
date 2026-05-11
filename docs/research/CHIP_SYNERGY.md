# Research Request: FAITHH Battle Chip Synergy System

**Created**: 2025-12-30
**Type**: Design Research / Architecture Exploration
**Goal**: Make the "chip" system more intelligent and synergistic

---

## 🎮 Background: The Battle Chip Metaphor

FAITHH (Friendly AI Teaching & Helping Hub) uses a "battle chip" architecture inspired by **MegaMan Battle Network**. In MMBN:
- NetNavis equip "Battle Chips" for different abilities
- Chips can combine into "Program Advances" (powerful combos)
- Chips have "codes" (A-Z, *) that determine compatibility
- The folder (deck) is curated for synergy

### Current FAITHH Chips

| Chip Name | Trigger | Data Source | Purpose |
|-----------|---------|-------------|---------|
| `self_awareness` | "faithh", "what are you" | `faithh_memory.json` | FAITHH's identity/capabilities |
| `constella` | "astris", "harmonic" | Constella context files | Domain framework knowledge |
| `decisions` | "why did we", "rationale" | `decisions_log.json` | Historical decision reasoning |
| `project_state` | "priorities", "status" | `project_states.json` | Current project phases |
| `scaffolding` | "where was I", "catch me up" | `scaffolding_state.json` | Session continuity |
| `rag_search` | Various keywords | ChromaDB (27k docs) | Semantic memory search |
| `conversation_history` | Always (with session) | In-memory | Recent exchange context |
| `filesystem_chip` | File operations | Local FS | Read/write files |

---

## 🔴 Current Problems

### 1. Chips Fire Independently
Each chip checks its own keywords and adds context. No awareness of what other chips found.

```python
# Current flow (simplified)
if "constella" in query:
    add_constella_context()
if "faithh" in query:
    add_self_awareness()
if use_rag:
    add_rag_results()
# All contexts concatenated, sent to LLM
```

### 2. Keyword Matching is Brittle
- "Tom Cat Sound LLC" doesn't trigger RAG (no keyword match)
- User has to know magic words
- Misses semantic intent

### 3. Context Overflow Risk
If multiple chips fire, context can exceed LLM window:
- self_awareness: ~500 tokens
- constella: ~800 tokens  
- project_state: ~600 tokens
- rag_results (3 docs): ~1500 tokens
- scaffolding: ~400 tokens
- **Total: 3800+ tokens** just in context, before user query and response

### 4. No Synergy / Combos
In MMBN, LifeSword = Sword + WideSwrd + LongSwrd (same code)
In FAITHH, we could have:
- **Context Recovery** = scaffolding + rag_search (where was I + what did we discuss)
- **Decision Audit** = decisions + rag_search (why + supporting evidence)
- **Project Deep Dive** = project_state + constella + rag_search (status + framework + history)

But currently these are just additive, not synergistic.

---

## 🔬 Research Questions

### Q1: How Should Chips Communicate?

**Option A: Sequential Pipeline**
```
Query → Intent Classifier → Chip 1 → Chip 2 (informed by Chip 1) → LLM
```
Pro: Each chip can use previous chip's output
Con: Latency stacks up

**Option B: Parallel with Merge**
```
Query → [Chip 1, Chip 2, Chip 3] → Merger/Ranker → LLM
```
Pro: Fast
Con: No inter-chip awareness

**Option C: Coordinator Chip**
```
Query → Meta-Chip (decides which chips, in what order) → Selected Chips → LLM
```
Pro: Intelligent routing
Con: Complexity, another LLM call?

**Research needed**: What patterns exist in multi-agent / RAG fusion systems?

---

### Q2: Better Routing Than Keywords?

**Current**: Regex/keyword matching
```python
constella_keywords = ['constella', 'astris', 'auctor', ...]
if any(kw in query_lower for kw in constella_keywords):
    intent['is_constella_query'] = True
```

**Alternatives**:

1. **Embedding Similarity**
   - Embed the query
   - Compare to "chip signature" embeddings
   - Route to chips above threshold
   - Pro: Semantic understanding
   - Con: Latency, need to define signatures

2. **Lightweight Classifier**
   - Train small model on (query → chips) pairs
   - Could be distilled from larger model
   - Pro: Fast, learned patterns
   - Con: Need training data, maintenance

3. **LLM-as-Router (first pass)**
   - Quick LLM call: "Which chips are relevant?"
   - Pro: Flexible, understands nuance
   - Con: Latency, cost

4. **Hybrid: Keywords + Embedding Fallback**
   - If keywords match → use those chips
   - If no keywords → embedding similarity
   - Pro: Fast for known patterns, smart fallback
   - Con: Two systems to maintain

**Research needed**: What's the latency/accuracy tradeoff? Examples from industry?

---

### Q3: Program Advances (Chip Combos)

**MMBN Inspiration**:
- Specific chip combinations = special move
- Must be adjacent in folder, same code
- More powerful than individual chips

**FAITHH Potential Combos**:

| Combo Name | Chips | Trigger | Special Behavior |
|------------|-------|---------|------------------|
| **Context Recovery** | scaffolding + rag | "catch me up" | RAG filters to recent project docs |
| **Decision Audit** | decisions + rag | "why did we X" | RAG finds supporting conversations |
| **Project Status+** | project_state + constella | project name mentioned | Constella principles applied to status |
| **Full Recall** | scaffolding + rag + conversation_history | "everything about X" | Comprehensive context assembly |
| **Debug Mode** | filesystem + rag | code/file mentioned | RAG finds related code discussions |

**Implementation Ideas**:
1. Define combo conditions (which chips + what query patterns)
2. When combo detected, run special merge logic
3. Output could be: summarized, re-ranked, or specially formatted

**Research needed**: How to define combo triggers elegantly? Learning combos from usage?

---

### Q4: Context Window Management

**Problem**: 8k-32k context windows fill fast

**Strategies**:

1. **Priority Ranking**
   - Score each chip's relevance to query
   - Only include top N tokens worth
   - Pro: Always fits
   - Con: Might miss important context

2. **Summarization Layer**
   - Each chip summarizes its output to ~200 tokens
   - Full context available if LLM asks
   - Pro: Consistent size
   - Con: Lossy, latency

3. **Dynamic Truncation**
   - Start with full context
   - If over limit, truncate lowest-relevance sections
   - Pro: Maximizes info
   - Con: Complex scoring

4. **Two-Pass Approach**
   - Pass 1: LLM sees summaries, decides what to expand
   - Pass 2: Full context for selected chips
   - Pro: LLM-guided relevance
   - Con: Two LLM calls

**Research needed**: What do production RAG systems do? LangChain, LlamaIndex patterns?

---

### Q5: Learning from Feedback

**Could FAITHH learn which chips work well?**

1. **Implicit Feedback**
   - Track: query → chips used → response length / follow-up questions
   - If user asks clarifying question → chips might have missed
   - If user says "thanks" / moves on → chips were sufficient

2. **Explicit Feedback**
   - Thumbs up/down on responses
   - "Was this helpful?" prompt
   - Link feedback to chip combination used

3. **Adaptation**
   - Adjust chip trigger thresholds based on feedback
   - Learn new keyword associations
   - Personalize chip priorities to user patterns

**Research needed**: Reinforcement learning from human feedback (RLHF) at small scale? Simpler heuristics?

---

## 🎯 Desired Outcome

A chip system that:
1. **Routes intelligently** - Semantic understanding, not just keywords
2. **Synergizes** - Chips enhance each other (Program Advances)
3. **Manages context** - Stays within LLM limits gracefully
4. **Learns** - Gets better with use
5. **Stays fast** - Response time < 15 seconds total

---

## 📚 Suggested Research Areas

1. **Multi-agent RAG systems** - How do they coordinate?
2. **Query routing in RAG** - Semantic routers, learned routers
3. **Context compression** - Summarization, selective retrieval
4. **Ensemble methods** - How to merge multiple retrieval sources
5. **RLHF for retrieval** - Learning from implicit/explicit feedback
6. **MegaMan Battle Network mechanics** - Deep dive on Program Advances for inspiration

---

## 🔧 Technical Constraints

- **Hardware**: Mac M1 Pro (16GB) + HP ProLiant Gen8 (Xeon, 16GB)
- **LLMs**: Ollama (llama3.1:8b local) or Groq API (llama-3.3-70b cloud)
- **Vector DB**: ChromaDB on Gen 8 (27,568 docs, BGE-768 embeddings)
- **Latency Budget**: < 15 seconds total response time
- **No Training Infrastructure**: Can't fine-tune large models, need inference-time solutions

---

## 💡 Initial Ideas to Explore

1. **"Chip Codes" via Embedding Clusters**
   - Cluster the 27k docs into ~10-20 topics
   - Each cluster = a "code"
   - Chips with same code are compatible

2. **Router as Embedding Classifier**
   - Pre-compute "ideal query" embedding for each chip
   - New query → cosine similarity to each chip
   - Threshold-based activation

3. **Program Advance Detection**
   - If 2+ chips above threshold + query matches combo pattern
   - Trigger special combo handler

4. **Context Budget Allocation**
   - Total budget: 4000 tokens
   - Allocate proportionally to relevance scores
   - Reserve 500 for conversation history always

---

*Research handoff created - Dec 30, 2025*
*For: Deep Research Chat / Architecture Exploration*


---

# FAITHH Chip Synergy System: Research Findings & Recommendations

**Research Date**: December 30, 2025  
**Sources**: 30+ academic papers, industry articles, and framework documentation  
**Goal**: Design intelligent chip routing and synergy for FAITHH's "battle chip" architecture

---

## Executive Summary

Based on research into RAG routing, multi-agent systems, semantic routers, and context management, here are the key findings and recommendations for improving FAITHH's chip system:

### Key Insights

1. **Semantic routing is production-ready** - Libraries like `semantic-router` provide fast (~10-50ms) embedding-based routing without LLM calls
2. **Hybrid routing works best** - Combine keyword heuristics (fast) with semantic fallback (smart)
3. **Context budget allocation is critical** - Dynamic allocation based on query type beats fixed allocations
4. **Chip "fusion" patterns exist** - RAG Fusion, multi-retriever systems show how to merge multiple sources
5. **MMBN "Program Advances" map to "Ensemble Methods"** - Combining chips is analogous to ensemble ML

---

## Part 1: Routing Strategies (Replacing Keyword Matching)

### Current FAITHH Approach
```python
# Brittle keyword matching
if any(kw in query_lower for kw in constella_keywords):
    intent['is_constella_query'] = True
```

### Recommended: Hybrid Router

**Architecture**: Keyword heuristics → Semantic router fallback

```python
# Step 1: Fast keyword check (< 1ms)
if has_obvious_keywords(query):
    return keyword_route(query)

# Step 2: Semantic routing (10-50ms)
return semantic_route(query)
```

### Implementation Options

#### Option A: Use `semantic-router` Library
```python
from semantic_router import Route
from semantic_router.encoders import HuggingFaceEncoder
from semantic_router.layer import RouteLayer

# Define routes with example utterances
constella_route = Route(
    name="constella",
    utterances=[
        "What is the Astris formula?",
        "How does harmonic governance work?",
        "Explain the resonance gap concept",
        "Tell me about civic tome principles",
    ]
)

business_route = Route(
    name="business", 
    utterances=[
        "What's the status of Tom Cat Sound?",
        "How is Floating Garden Soundworks doing?",
        "Tell me about my audio business",
        "What equipment do we have?",
    ]
)

# Use local encoder (BGE works great)
encoder = HuggingFaceEncoder(model_name="BAAI/bge-base-en-v1.5")
route_layer = RouteLayer(encoder=encoder, routes=[constella_route, business_route])

# Route query
result = route_layer(query)  # Returns route name or None
```

**Pros**: Production-ready, fast, works with your existing BGE embeddings  
**Cons**: Another dependency, need to maintain utterance lists

#### Option B: Centroid-Based Custom Router
Pre-compute a "signature embedding" for each chip, compare query embedding:

```python
class ChipRouter:
    def __init__(self, embedder):
        self.embedder = embedder
        self.chip_signatures = {}
    
    def register_chip(self, chip_name, sample_queries):
        """Create centroid embedding from sample queries"""
        embeddings = self.embedder.encode(sample_queries)
        centroid = embeddings.mean(axis=0)
        self.chip_signatures[chip_name] = centroid
    
    def route(self, query, threshold=0.7):
        """Find matching chips above threshold"""
        query_emb = self.embedder.encode([query])[0]
        matches = []
        for chip, signature in self.chip_signatures.items():
            similarity = cosine_similarity(query_emb, signature)
            if similarity > threshold:
                matches.append((chip, similarity))
        return sorted(matches, key=lambda x: x[1], reverse=True)
```

**Pros**: Uses existing embedder, no new dependencies, full control  
**Cons**: Need to tune thresholds, maintain sample queries

### Recommended Thresholds
Based on research, start with:
- **High confidence**: > 0.80 (definitely activate chip)
- **Medium confidence**: 0.65-0.80 (activate if no high-confidence match)
- **Low confidence**: < 0.65 (don't activate)

---

## Part 2: Chip Synergy ("Program Advances")

### MMBN Inspiration → RAG Fusion Patterns

In MegaMan Battle Network, Program Advances combine compatible chips for powerful effects.  
In RAG systems, this maps to **Fusion Retrieval** and **Ensemble Methods**.

### Proposed FAITHH Program Advances

| Advance Name | Chips Combined | Trigger Pattern | Special Behavior |
|--------------|----------------|-----------------|------------------|
| **Context Recovery** | scaffolding + rag | "where was I", "catch me up" | RAG filters to recent project docs, scaffolding provides timeline |
| **Decision Audit** | decisions + rag | "why did we X", "rationale" | RAG finds supporting conversations, decisions provides reasoning |
| **Project Deep Dive** | project_state + rag + constella | project name + detail request | Full project context with framework principles |
| **Business Review** | project_state + rag | business-related query | Combines current state with historical data |
| **Full Recall** | all chips | "everything about X" | Comprehensive context assembly with deduplication |

### Implementation: Chip Combiner

```python
class ChipCombiner:
    def __init__(self):
        self.advances = {
            "context_recovery": {
                "chips": ["scaffolding", "rag_search"],
                "triggers": ["where was i", "catch me up", "continue"],
                "merge_strategy": "timeline_priority"
            },
            "decision_audit": {
                "chips": ["decisions", "rag_search"],
                "triggers": ["why did", "rationale", "reasoning"],
                "merge_strategy": "evidence_chain"
            }
        }
    
    def detect_advance(self, active_chips, query):
        """Check if active chips form a Program Advance"""
        for advance_name, config in self.advances.items():
            required = set(config["chips"])
            if required.issubset(set(active_chips)):
                # Check trigger patterns
                if any(t in query.lower() for t in config["triggers"]):
                    return advance_name, config["merge_strategy"]
        return None, "default"
    
    def merge_contexts(self, chip_outputs, strategy):
        """Merge chip outputs using specified strategy"""
        if strategy == "timeline_priority":
            # Sort by recency, deduplicate
            return self._timeline_merge(chip_outputs)
        elif strategy == "evidence_chain":
            # Structure as claim → evidence
            return self._evidence_merge(chip_outputs)
        else:
            return self._default_merge(chip_outputs)
```

---

## Part 3: Context Window Management

### The Problem
With 8k-32k token windows, multiple chips can overflow:
- self_awareness: ~500 tokens
- constella: ~800 tokens
- project_state: ~600 tokens
- rag_results (5 docs): ~2500 tokens
- scaffolding: ~400 tokens
- conversation_history: ~1000 tokens
- **Total: 5800+ tokens** before query and response

### Research-Backed Solutions

#### Strategy 1: Dynamic Budget Allocation
Allocate tokens based on query type:

```python
def allocate_context_budget(query_type, total_budget=6000):
    """Dynamically allocate token budget based on query needs"""
    allocations = {
        "simple_factual": {
            "rag": 0.6, "history": 0.2, "system": 0.2
        },
        "project_status": {
            "project_state": 0.4, "rag": 0.3, "scaffolding": 0.2, "system": 0.1
        },
        "deep_research": {
            "rag": 0.7, "history": 0.15, "system": 0.15
        },
        "continuation": {
            "scaffolding": 0.4, "history": 0.4, "rag": 0.1, "system": 0.1
        }
    }
    
    alloc = allocations.get(query_type, allocations["simple_factual"])
    return {k: int(v * total_budget) for k, v in alloc.items()}
```

#### Strategy 2: Relevance-Weighted Truncation
Score each chip's output by relevance to query, truncate lowest-scored content:

```python
def truncate_by_relevance(chip_outputs, query, max_tokens=4000):
    """Keep most relevant content within token budget"""
    scored = []
    for chip_name, content in chip_outputs.items():
        # Score relevance (could use embedding similarity)
        relevance = compute_relevance(content, query)
        scored.append((chip_name, content, relevance))
    
    # Sort by relevance, accumulate until budget
    scored.sort(key=lambda x: x[2], reverse=True)
    
    result = {}
    used_tokens = 0
    for chip_name, content, _ in scored:
        content_tokens = count_tokens(content)
        if used_tokens + content_tokens <= max_tokens:
            result[chip_name] = content
            used_tokens += content_tokens
        else:
            # Truncate this chip's content to fit remaining budget
            remaining = max_tokens - used_tokens
            if remaining > 100:  # Only include if meaningful
                result[chip_name] = truncate_to_tokens(content, remaining)
            break
    
    return result
```

#### Strategy 3: Hierarchical Summarization
Compress older/less-relevant content:

```python
def hierarchical_compress(content, target_tokens):
    """Compress content to target token count"""
    current_tokens = count_tokens(content)
    
    if current_tokens <= target_tokens:
        return content
    
    # Use LLM to summarize (or rule-based extraction)
    summary_prompt = f"""Summarize the following in {target_tokens} tokens, 
    preserving key facts and decisions:
    
    {content}"""
    
    return llm_summarize(summary_prompt)
```

### Recommended Approach for FAITHH
Given your 8k context with llama3.1:8b:

| Component | Token Budget | Notes |
|-----------|--------------|-------|
| System prompt | 500 | Fixed, includes FAITHH identity |
| Query + history | 1000 | Last 3-5 exchanges |
| Primary chip(s) | 2500 | RAG results or specialized context |
| Secondary chips | 1500 | Compressed summaries |
| Output buffer | 2500 | Reserved for response |
| **Total** | 8000 | |

---

## Part 4: Implementation Roadmap

### Phase 1: Quick Wins (1-2 hours)
1. ✅ **Already done**: Fixed RAG category filter to include all docs
2. ✅ **Already done**: Added business keywords to intent detection
3. **TODO**: Add RAG fallback when no specific chip triggers

```python
# At end of build_integrated_context:
if use_rag and CHROMA_CONNECTED and 'rag_search' not in integrations_used:
    # No chip fired - try RAG as general fallback
    if not intent.get('needs_orientation'):
        results = query_collection(query_text, n_results=3)
        if results and results['documents'][0]:
            rag_results = results['documents'][0]
            integrations_used.append('rag_search_fallback')
```

### Phase 2: Semantic Router (2-3 hours)
1. Install semantic-router: `pip install semantic-router`
2. Define utterances for each chip
3. Create hybrid router (keywords + semantic)
4. Test with diverse queries

### Phase 3: Program Advances (3-4 hours)
1. Define advance combinations and triggers
2. Implement merge strategies
3. Add advance detection to intent system
4. Test chip combinations

### Phase 4: Context Management (2-3 hours)
1. Implement token counting
2. Add dynamic budget allocation
3. Create relevance scoring
4. Test with complex queries

---

## Part 5: Metrics to Track

### Chip Performance
- **Activation rate**: How often each chip fires
- **Relevance score**: User satisfaction when chip fires vs. doesn't
- **Response quality**: Thumbs up/down correlation with chip combinations

### System Health
- **Token utilization**: Average % of context window used
- **Latency breakdown**: Time per chip, routing time, LLM time
- **RAG hit rate**: % of queries where RAG finds relevant docs

### Suggested Logging
```python
# Add to each request
log_entry = {
    "timestamp": datetime.now().isoformat(),
    "query": query_text,
    "intent_detected": intent,
    "chips_activated": integrations_used,
    "advance_detected": advance_name,
    "tokens_used": {
        "total": total_tokens,
        "by_chip": chip_token_counts
    },
    "response_time_ms": elapsed_ms,
    "user_feedback": None  # Filled in later if provided
}
```

---

## Appendix: Key Research Sources

### Routing
- **RAGRouter** (arXiv 2505.23052): Contrastive learning for RAG-aware routing
- **semantic-router**: Production library for embedding-based routing
- **LangChain/LlamaIndex**: Multi-index routing patterns

### Fusion & Multi-Retriever
- **RAG Fusion**: Reciprocal rank fusion for combining retrieval results
- **Multi-Vector Retriever**: Decoupling retrieval from synthesis

### Context Management
- **Context Collapse Crisis**: Multi-turn RAG degradation patterns
- **Dynamic Budget Allocation**: Query-adaptive token distribution
- **Hierarchical Summarization**: Compressing older context

---

## Next Steps for Claude Code

1. **Implement RAG fallback** (Phase 1, item 3)
2. **Create chip router module** with semantic routing
3. **Add Program Advance detection**
4. **Implement token budgeting**

The research supports the MMBN-inspired approach - chips working together (fusion) outperforms independent activation.

---

*Research compiled by Claude - December 30, 2025*


---

# FAITHH Chip Synergy Research - Supplement
## Addressing Implementation Loose Ends
*Compiled: December 30, 2025*

This document supplements `CHIP_SYNERGY_RESEARCH_FINDINGS.md` with specific solutions for identified gaps.

---

## 1. Conflict Resolution Between Chips

### The Problem
When chips contradict each other:
- `decision_logs`: "We chose React for the frontend"
- `rag_search`: Returns old docs about "considering Vue vs React"
- Which wins? How do we detect and resolve?

### Research Findings

#### MADAM-RAG (Multi-Agent Debate)
**Source**: arXiv 2504.13079 (April 2025)

Multi-agent approach where LLM agents debate over conflicting evidence:
1. Each agent represents one document/source
2. Agents discuss across multiple rounds
3. Aggregator collates responses, discards misinformation

**Results**: +11.4% on ambiguous queries, +15.8% on filtering misinformation

**FAITHH Application**: Too heavy for real-time (adds multiple LLM calls). Better for offline analysis.

#### Astute RAG (Lightweight)
**Source**: Wang et al., 2024

1. Generate internal parametric knowledge document
2. Cluster retrieved + parametric into "consistent" vs "conflicting" groups
3. Select most reliable cluster for final answer

**FAITHH Application**: Can implement as post-retrieval step before LLM call.

#### ICR Framework (8 Conflict Categories)
**Source**: ScienceDirect, November 2025

Defines 8 conflict scenarios with targeted resolution strategies:
1. **Temporal conflicts**: Prefer recency (decision_logs > old RAG docs)
2. **Authority conflicts**: Prefer authoritative source
3. **Specificity conflicts**: Prefer more specific information
4. **Completeness conflicts**: Prefer more complete answer

Uses Direct Preference Optimization (DPO) for training resolution.

### Recommended FAITHH Implementation

```python
def resolve_chip_conflicts(chip_results: dict, query: str) -> dict:
    """
    Lightweight conflict resolution for FAITHH.
    
    Priority order (configurable):
    1. decision_logs (explicit decisions trump speculation)
    2. project_state (current state > historical)
    3. scaffolding (active context)
    4. constella (curated knowledge)
    5. rag_search (general knowledge, may be outdated)
    """
    PRIORITY = {
        'decision_logs': 5,
        'project_state': 4,
        'scaffolding': 3,
        'constella': 2,
        'rag_search': 1
    }
    
    # Detect conflicts: same entity, different values
    conflicts = detect_entity_conflicts(chip_results)
    
    if not conflicts:
        return chip_results  # No conflicts, merge normally
    
    # For each conflict, keep higher-priority source
    resolved = {}
    for conflict in conflicts:
        winner = max(conflict['sources'], key=lambda s: PRIORITY.get(s, 0))
        resolved[conflict['entity']] = conflict['sources'][winner]
        
        # Log for transparency
        log_conflict_resolution(conflict, winner)
    
    return merge_with_resolved(chip_results, resolved)
```

### Conflict Detection Heuristics

| Conflict Type | Detection | Resolution |
|--------------|-----------|------------|
| Temporal | Same topic, different dates | Prefer most recent |
| Decision vs Speculation | "We decided X" vs "considering X" | Prefer decision |
| State vs History | "Current status: X" vs "Previously: Y" | Prefer current |
| Contradictory Facts | Entity A = X vs Entity A = Y | Use chip priority |

### Transparency Pattern
When conflicts detected, append to response:
> "Note: I found conflicting information about [topic]. Using the most recent decision from [date]."

---

## 2. Token Budget Allocation

### The Problem
With llama3.1:8b (8k context) or Groq models, how many tokens per chip?

### Research Findings

#### Production RAG Token Breakdown
**Source**: ragaboutit.com (December 2025)

Typical RAG query token consumption:
- Query expansion: 50-150 tokens
- Context (retrieved docs): **2,000-8,000 tokens**
- Response generation: 500-2,000 tokens
- Retry/fallback: 1,000-4,000 additional per failure

#### Cost-Optimized Pattern
**Source**: app.ailog.fr (November 2025)

```python
# Aggressive but effective
docs = vector_db.search(query_emb, limit=3)  # Not 10
context = compress_context(docs)  # 500 tokens, not 5000
```

#### Adaptive Budget Algorithm
**Source**: dev.to (December 2025)

```python
def adaptive_rag_query(
    question: str,
    max_context_tokens: int = 6000,
    min_chunks: int = 2,
    max_chunks: int = 10
):
    selected_chunks = []
    total_tokens = 0
    
    for match in results.matches:
        chunk_tokens = count_tokens(match.metadata["text"])
        
        if len(selected_chunks) < min_chunks:
            # Always include minimum chunks
            selected_chunks.append(match)
            total_tokens += chunk_tokens
        elif total_tokens + chunk_tokens <= max_context_tokens:
            # Add if within budget
            selected_chunks.append(match)
            total_tokens += chunk_tokens
        else:
            break  # Budget exhausted
    
    return selected_chunks
```

### Recommended FAITHH Token Budget

For **8k context window** (llama3.1:8b local):

| Component | Tokens | Notes |
|-----------|--------|-------|
| System prompt | 500 | FAITHH identity, chip instructions |
| Query + history | 300 | Current turn + 1-2 previous |
| **Chip contexts** | **4,500** | Total for all chips |
| Response buffer | 1,500 | Model output |
| Safety margin | 1,200 | Tokenizer variance |

**Per-Chip Allocation** (4,500 total):

| Chip | Default % | Tokens | Rationale |
|------|-----------|--------|-----------|
| rag_search | 40% | 1,800 | Primary knowledge source |
| scaffolding | 20% | 900 | Current project context |
| decision_logs | 15% | 675 | Decision history |
| project_state | 10% | 450 | Structured state |
| constella | 10% | 450 | Framework principles |
| conversation_history | 5% | 225 | Recent turns |

### Dynamic Reallocation by Query Type

```python
QUERY_TYPE_BUDGETS = {
    "factual_lookup": {
        "rag_search": 0.70,
        "constella": 0.20,
        "scaffolding": 0.10
    },
    "project_status": {
        "project_state": 0.40,
        "scaffolding": 0.30,
        "rag_search": 0.20,
        "decision_logs": 0.10
    },
    "decision_review": {
        "decision_logs": 0.50,
        "rag_search": 0.30,
        "scaffolding": 0.20
    },
    "constella_query": {
        "constella": 0.60,
        "rag_search": 0.30,
        "scaffolding": 0.10
    }
}

def allocate_budget(query_type: str, total_tokens: int = 4500) -> dict:
    ratios = QUERY_TYPE_BUDGETS.get(query_type, QUERY_TYPE_BUDGETS["factual_lookup"])
    return {chip: int(ratio * total_tokens) for chip, ratio in ratios.items()}
```

### For Groq (32k+ context)
Scale budgets proportionally. With more room:
- Increase rag_search to 60%
- Add more conversation_history (better continuity)
- Include more decision_logs context

---

## 3. Flask Async Patterns for Parallel Retrieval

### The Problem
Research assumes `asyncio.gather()`, but FAITHH backend is Flask (synchronous).

### Solution: Flask-Executor

**Source**: PyPI flask-executor

```bash
pip install flask-executor
```

```python
from flask import Flask
from flask_executor import Executor

app = Flask(__name__)
app.config['EXECUTOR_TYPE'] = 'thread'
app.config['EXECUTOR_MAX_WORKERS'] = 5
executor = Executor(app)
```

### Parallel Chip Retrieval Pattern

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Global executor (initialize once)
chip_executor = ThreadPoolExecutor(max_workers=5)

def retrieve_from_chip(chip_name: str, query: str, budget: int) -> dict:
    """Individual chip retrieval function."""
    start = time.time()
    
    if chip_name == "rag_search":
        results = chromadb_search(query, limit=budget // 200)  # ~200 tokens per chunk
    elif chip_name == "decision_logs":
        results = get_decision_logs(query, limit=budget // 150)
    elif chip_name == "scaffolding":
        results = get_scaffolding_context()
    # ... other chips
    
    return {
        "chip": chip_name,
        "results": results,
        "latency_ms": (time.time() - start) * 1000
    }

def parallel_chip_retrieval(query: str, active_chips: list, budgets: dict) -> dict:
    """
    Execute all chip retrievals in parallel.
    
    Without parallel: 5 chips × 500ms = 2500ms
    With parallel: max(500ms across all) ≈ 500-600ms
    """
    futures = {}
    
    # Submit all chips to thread pool
    for chip in active_chips:
        future = chip_executor.submit(
            retrieve_from_chip,
            chip,
            query,
            budgets.get(chip, 500)
        )
        futures[future] = chip
    
    # Collect results as they complete
    results = {}
    for future in as_completed(futures, timeout=3.0):  # 3 second max
        chip_name = futures[future]
        try:
            results[chip_name] = future.result()
        except Exception as e:
            results[chip_name] = {"error": str(e), "results": []}
            log_chip_error(chip_name, e)
    
    return results
```

### Integration with FAITHH Backend

```python
# In faithh_professional_backend_fixed.py

def process_query_with_parallel_chips(query: str, intent: dict) -> str:
    """Main query processing with parallel chip retrieval."""
    
    # 1. Determine active chips from intent
    active_chips = intent.get('integrations', ['rag_search'])
    
    # 2. Allocate token budgets
    query_type = classify_query_type(query)
    budgets = allocate_budget(query_type)
    
    # 3. Parallel retrieval (THE KEY OPTIMIZATION)
    chip_results = parallel_chip_retrieval(query, active_chips, budgets)
    
    # 4. Resolve conflicts
    resolved = resolve_chip_conflicts(chip_results, query)
    
    # 5. Apply RRF fusion if multiple chips
    if len(active_chips) > 1:
        fused = weighted_rrf_fusion(resolved)
    else:
        fused = resolved
    
    # 6. Truncate to budget and reorder
    context = build_context_with_budget(fused, total_budget=4500)
    context = long_context_reorder(context)  # Best info at edges
    
    # 7. Generate response
    return generate_response(query, context)
```

### Why ThreadPoolExecutor (not ProcessPoolExecutor)

| Factor | ThreadPoolExecutor | ProcessPoolExecutor |
|--------|-------------------|---------------------|
| I/O-bound work (HTTP, DB) | ✅ Perfect | Overkill |
| Startup overhead | Low | High (process fork) |
| Memory sharing | Shares Flask context | Isolated |
| GIL limitation | Not an issue for I/O | Bypasses GIL |
| ChromaDB client | Shared connection | Need new connection per process |

**Verdict**: ThreadPoolExecutor is correct for FAITHH's I/O-bound chip retrieval.

---

## 4. Cold Start & Default Weights

### The Problem
Bandit learning needs history. What defaults do we use initially?

### Recommended Default Weights

Based on expected query distribution and chip reliability:

```python
DEFAULT_CHIP_WEIGHTS = {
    "rag_search": 1.0,        # Baseline, always useful
    "scaffolding": 0.9,       # High value for project context
    "decision_logs": 0.85,    # Explicit decisions valuable
    "project_state": 0.8,     # Structured but limited
    "constella": 0.75,        # Domain-specific, narrow trigger
    "conversation_history": 0.6,  # Useful but often redundant
    "self_awareness": 0.5,    # Meta-queries only
    "filesystem": 0.4         # Rarely needed
}
```

### Cold Start Strategy

**Phase 1: Rule-based (Weeks 1-2)**
- Use keyword routing + DEFAULT_CHIP_WEIGHTS
- Log everything: query, chips used, latency, any user feedback

**Phase 2: Empirical Tuning (Weeks 3-4)**
- Review logs, identify patterns
- Manually adjust weights based on observed performance
- Example: If decision_logs often provides stale info, reduce to 0.7

**Phase 3: Bandit Learning (Month 2+)**
- Requires ~500+ logged queries with implicit feedback
- Implicit signals:
  - Follow-up questions = bad response (penalty)
  - Conversation continues smoothly = good (reward)
  - User edits/corrects = bad (penalty)
  - Long response read time = engaged (reward)

### Minimum Data for Bandit

| Approach | Min Queries | Notes |
|----------|-------------|-------|
| Thompson Sampling | 100-200 | Fast convergence |
| UCB1 | 200-500 | More exploration |
| ε-greedy | 50-100 | Simple but less optimal |

**Recommendation**: Start with ε-greedy (ε=0.1), switch to Thompson after 200 queries.

---

## 5. Evaluation Metrics

### What to Log

```python
@dataclass
class QueryMetrics:
    # Identification
    query_id: str
    timestamp: datetime
    query_text: str
    
    # Routing
    intent_detected: str
    chips_activated: List[str]
    advance_detected: Optional[str]
    
    # Performance
    total_latency_ms: float
    chip_latencies_ms: Dict[str, float]
    tokens_used: Dict[str, int]
    
    # Quality signals (collected async)
    follow_up_within_60s: bool = False
    user_edited_response: bool = False
    thumbs_up: Optional[bool] = None
    conversation_continued: bool = False
```

### Key Metrics to Track

| Metric | Calculation | Target |
|--------|-------------|--------|
| **Latency P50** | Median response time | < 5s |
| **Latency P95** | 95th percentile | < 15s |
| **Chip Hit Rate** | Queries where chip contributed | > 60% for rag_search |
| **Follow-up Rate** | Immediate clarification needed | < 20% |
| **Multi-chip Utilization** | Queries using 2+ chips | > 40% |
| **Conflict Rate** | Queries with detected conflicts | Track trend |
| **Token Efficiency** | Useful tokens / Total tokens | > 70% |

### A/B Testing Framework

```python
def ab_test_routing(query: str, user_id: str) -> dict:
    """Simple A/B test for chip routing strategies."""
    
    # Deterministic bucket based on user_id
    bucket = hash(user_id) % 100
    
    if bucket < 50:
        # Control: keyword routing
        strategy = "keyword"
        chips = keyword_route(query)
    else:
        # Treatment: semantic routing
        strategy = "semantic"
        chips = semantic_route(query)
    
    return {
        "strategy": strategy,
        "chips": chips,
        "bucket": bucket
    }
```

### Dashboard Queries (for future)

```sql
-- Average latency by chip combination
SELECT 
    chips_activated,
    AVG(total_latency_ms) as avg_latency,
    COUNT(*) as query_count
FROM query_metrics
GROUP BY chips_activated
ORDER BY query_count DESC;

-- Follow-up rate by intent type
SELECT
    intent_detected,
    AVG(CASE WHEN follow_up_within_60s THEN 1 ELSE 0 END) as followup_rate
FROM query_metrics
GROUP BY intent_detected;

-- Token efficiency trend
SELECT
    DATE(timestamp) as day,
    AVG(tokens_used_total) as avg_tokens,
    AVG(total_latency_ms) as avg_latency
FROM query_metrics
GROUP BY DATE(timestamp);
```

---

## 6. Implementation Priority

Based on research, recommended implementation order:

### Immediate (This Session)
1. ✅ RAG fallback (already done)
2. **Parallel chip retrieval** with ThreadPoolExecutor
3. **Basic token budgeting** (static allocation)

### Next Session
4. **Weighted RRF fusion** for multi-chip results
5. **Conflict detection** (simple heuristics)
6. **Query metrics logging**

### Future Sessions
7. **Semantic routing** (hybrid keyword + embedding)
8. **Program Advance detection**
9. **Dynamic budget allocation**
10. **Cross-encoder reranking**

### Deferred (Month 2+)
11. Bandit learning for chip selection
12. A/B testing framework
13. Dashboard and analytics

---

## Quick Reference: Code Snippets Ready to Implement

### 1. ThreadPoolExecutor Setup
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
CHIP_EXECUTOR = ThreadPoolExecutor(max_workers=5)
```

### 2. Token Counter
```python
def count_tokens(text: str) -> int:
    """Rough token count (4 chars ≈ 1 token for English)."""
    return len(text) // 4
```

### 3. Budget Enforcer
```python
def enforce_budget(chunks: list, budget: int) -> list:
    """Greedily select chunks within token budget."""
    selected, total = [], 0
    for chunk in chunks:
        tokens = count_tokens(chunk['content'])
        if total + tokens <= budget:
            selected.append(chunk)
            total += tokens
    return selected
```

### 4. Simple Conflict Flag
```python
def has_temporal_conflict(results: list) -> bool:
    """Check if results span significant time range."""
    dates = [r.get('date') for r in results if r.get('date')]
    if len(dates) < 2:
        return False
    return (max(dates) - min(dates)).days > 30
```

---

*Supplement compiled by Claude - December 30, 2025*
*Addresses gaps identified in main research document*

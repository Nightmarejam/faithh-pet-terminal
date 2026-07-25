# FAITHH Auto-Indexer Specification

*Auto-generated from knowledge graph on 2025-12-29*

---

## Tiered Storage System

### Tier 1 Indexed

**Description:** High-value content, fully indexed in RAG

**Storage:** ChromaDB

**Retention:** permanent


**Criteria:**
- Contains code blocks (>10 lines)
- Contains explicit decisions or conclusions
- Contains technical explanations (>200 words)
- Contains project-specific terminology
- Contains financial data or business decisions
- User explicitly marks as important

### Tier 2 Archived

**Description:** Low-value but kept for audit trail

**Storage:** flat_file

**Retention:** 1 year


**Criteria:**
- Short responses (<50 words) without code
- Acknowledgments and confirmations
- Clarifying questions
- Intermediate steps in longer workflows

### Tier 3 Discarded

**Description:** Noise, not stored

**Storage:** None

**Retention:** None


**Criteria:**
- Single word responses
- Greetings only
- Empty or error responses
- Duplicate content

---

## Negative Examples Archive

**Description:** Failed approaches kept for learning

**Storage:** separate_collection

**Purpose:** Avoid repeating mistakes, learn from failures


**Criteria:**
- Approaches explicitly marked as failed
- Corrections to previous responses
- User feedback indicating wrong direction

---

## Quality Signals

### ✅ Positive Signals (Index)

- **keyword_matches:** ['decision', 'conclusion', 'solution', 'fixed', 'resolved']
- **has_code_blocks:** True
- **word_count_min:** 100
- **has_structured_data:** True

### ❌ Negative Signals (Archive/Discard)

- **keyword_matches:** ['okay', 'sure', 'got it', 'thanks']
- **word_count_max:** 30
- **is_question_only:** True

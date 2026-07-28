"""
Enhanced Chip Integration for FAITHH
Adds weighted RRF fusion and Program Advance detection to existing parallel chip system

Integrate this into your existing build_integrated_context function
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Import existing components
import sys
import os
sys.path.append(os.path.dirname(__file__))

# Phase 2 ML Components
try:
    from ml.performance_tracker import performance_tracker, QueryPerformance
    from ml.weight_optimizer import weight_optimizer
    from ml.semantic_intent_detector import semantic_intent_detector
    PHASE2_ENABLED = True
    print("🤖 Phase 2 ML components loaded")
except ImportError as e:
    print(f"⚠️ Phase 2 ML components not available: {e}")
    PHASE2_ENABLED = False

# ---------------------------
# Program Advance Detection
# ---------------------------

PROGRAM_ADVANCES = {
    "full_recall": {
        "chips": ["scaffolding", "rag_search", "decisions", "project_state"],
        "triggers": ["everything about", "complete history", "all information", "full context"],
        "merge_strategy": "comprehensive",
        "description": "Maximum context assembly",
        "semantic_queries": [
            "tell me everything about this topic",
            "give me the complete history",
            "all information you have on this",
            "comprehensive overview of everything",
            "full context dump on this subject",
            "dump all context"
        ]
    },
    "business_review": {
        "chips": ["project_state", "rag_search"],
        "triggers": ["business", "tom cat", "tomcat", "floating garden", "llc", "revenue", "clients"],
        "merge_strategy": "business_focus",
        "description": "Business-focused project review",
        "semantic_queries": [
            "how is the business doing",
            "review my business projects",
            "what's the status of my LLC",
            "audio business update",
            "client and revenue status",
            "business finances and clients"
        ]
    },
    "context_recovery": {
        "chips": ["scaffolding", "rag_search"],
        "triggers": ["where was i", "catch me up", "what was i doing", "back up to speed", "up to date"],
        "merge_strategy": "timeline_priority",
        "description": "Recovers full project context with timeline",
        "semantic_queries": [
            "where was I in this project",
            "catch me up on what I was doing",
            "what was I working on last time",
            "resume my previous work",
            "get me back up to speed",
            "bring me up to date on progress"
        ]
    },
    "decision_audit": {
        "chips": ["decisions", "rag_search"],
        "triggers": ["why did", "rationale", "reasoning", "what was the thinking", "alternatives"],
        "merge_strategy": "evidence_chain",
        "description": "Audits decisions with supporting evidence",
        "semantic_queries": [
            "why did we make this decision",
            "what was the rationale behind this choice",
            "explain the reasoning for this approach",
            "what alternatives did we consider",
            "justify this technical decision",
            "explain why we went this direction"
        ]
    },
    "project_deep_dive": {
        "chips": ["project_state", "rag_search", "constella"],
        "triggers": ["project status", "project state", "project overview", "progress", "phase", "ucf", "penumbra", "civic floor", "constella", "civic tome", "astris", "auctor", "governance", "constitutional", "founding diversity", "strategy escape"],
        "merge_strategy": "comprehensive",
        "description": "Complete project analysis with framework principles",
        "semantic_queries": [
            "what is the current project status",
            "how is the project progressing",
            "give me a project overview",
            "what phase are we in",
            "summarize the project state"
        ]
    },
    "alife_research": {
        "chips": ["rag_search", "constella"],
        "triggers": [
            "experiment", "exp ", "alife", "population", "collapse", "adaptation",
            "strategy escape", "founding diversity", "floor rider", "gamer",
            "penumbra zone", "predator", "drain", "genome", "agent", "tick",
            "oscillat", "arms race", "monoculture", "diversity floor",
            "naked strategy", "defender", "parasite", "wave", "commons pool"
        ],
        "merge_strategy": "evidence_chain",
        "description": "ALife experiment retrieval with constitutional evidence chain",
        "semantic_queries": [
            "what did the alife experiments show",
            "what happened in experiment",
            "what does the simulation evidence say",
            "population dynamics findings",
            "constitutional principle evidence from alife"
        ]
    }
}

# Semantic detection threshold (0.0-1.0, higher = more strict)
# 0.65 balances catching paraphrases vs false positives
PA_SEMANTIC_THRESHOLD = 0.65

# PA embeddings cache (populated at first use)
PA_EMBEDDINGS: Dict[str, Any] = {}
_pa_embedder = None

def _get_pa_embedder():
    """Lazy-load the embedding model for PA semantic matching.
    
    IMPORTANT: Must force device='cpu' to prevent CUDA initialization on sm_61 GPUs
    (GTX 1080 Ti). Without this, SentenceTransformer detects cuda:0 and crashes WSL.
    See decisions_log.json infra_002 for root cause documentation.
    """
    global _pa_embedder
    if _pa_embedder is None:
        try:
            import os
            os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Block CUDA before import
            from sentence_transformers import SentenceTransformer
            _pa_embedder = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
            print("✅ PA semantic embedder loaded (all-MiniLM-L6-v2, CPU-only)")
        except Exception as e:
            print(f"⚠️ PA semantic embedder failed to load: {e}")
            _pa_embedder = False  # Mark as failed, don't retry
    return _pa_embedder if _pa_embedder else None

def _generate_pa_embeddings():
    """Generate embeddings for all PA semantic queries."""
    global PA_EMBEDDINGS
    if PA_EMBEDDINGS:
        return PA_EMBEDDINGS
    
    embedder = _get_pa_embedder()
    if not embedder:
        return {}
    
    import numpy as np
    
    for pa_name, config in PROGRAM_ADVANCES.items():
        queries = config.get("semantic_queries", [])
        if queries:
            # Embed all semantic queries and average them
            embeddings = embedder.encode(queries)
            centroid = np.mean(embeddings, axis=0)
            PA_EMBEDDINGS[pa_name] = {
                "centroid": centroid,
                "queries": queries
            }
    
    print(f"✅ PA embeddings generated for {len(PA_EMBEDDINGS)} Program Advances")
    return PA_EMBEDDINGS

def detect_program_advance_hybrid(
    query: str, 
    active_chips: List[str] = None,
    query_embedding: Any = None
) -> Tuple[Optional[str], Optional[str], str]:
    """
    Hybrid Program Advance detection: trigger phrases (fast) + semantic (fallback).
    
    Args:
        query: User query text
        active_chips: List of active chip names (for chip requirement check)
        query_embedding: Pre-computed query embedding (optional, saves compute)
    
    Returns:
        (advance_name, merge_strategy, detection_method) or (None, None, "none")
        detection_method is one of: "trigger", "semantic", "none"
    """
    import numpy as np
    
    query_lower = query.lower()
    
    # FAST PATH: Trigger phrase matching
    for pa_name, config in PROGRAM_ADVANCES.items():
        triggers = config.get("triggers", [])
        if any(trigger in query_lower for trigger in triggers):
            # Check chip requirements if active_chips provided
            if active_chips is not None:
                required_chips = set(config["chips"])
                if not required_chips.issubset(set(active_chips)):
                    continue  # Chips not available, skip
            return pa_name, config["merge_strategy"], "trigger"
    
    # SLOW PATH: Semantic similarity matching
    embedder = _get_pa_embedder()
    if not embedder:
        return None, None, "none"
    
    # Generate PA embeddings if not cached
    pa_embeddings = _generate_pa_embeddings()
    if not pa_embeddings:
        return None, None, "none"
    
    # Get query embedding
    if query_embedding is None:
        query_embedding = embedder.encode([query])[0]
    
    # Find best matching PA
    best_pa = None
    best_score = 0.0
    best_strategy = None
    
    for pa_name, pa_data in pa_embeddings.items():
        centroid = pa_data["centroid"]
        # Cosine similarity
        norm_q = np.linalg.norm(query_embedding)
        norm_c = np.linalg.norm(centroid)
        if norm_q == 0 or norm_c == 0:
            continue
        similarity = np.dot(query_embedding, centroid) / (norm_q * norm_c)
        
        if similarity > best_score and similarity >= PA_SEMANTIC_THRESHOLD:
            # Check chip requirements if active_chips provided
            if active_chips is not None:
                required_chips = set(PROGRAM_ADVANCES[pa_name]["chips"])
                if not required_chips.issubset(set(active_chips)):
                    continue  # Chips not available, skip
            best_pa = pa_name
            best_score = similarity
            best_strategy = PROGRAM_ADVANCES[pa_name]["merge_strategy"]
    
    if best_pa:
        print(f"   🎯 Semantic PA match: {best_pa} (score: {best_score:.3f})")
        return best_pa, best_strategy, "semantic"
    
    return None, None, "none"

def get_pa_chips_for_query(query: str) -> set:
    """
    Pre-detect which chips should be forced to fire for potential PA activation.
    Uses hybrid detection without chip requirement check.
    
    Returns: Set of chip names that should be activated
    """
    pa_name, _, method = detect_program_advance_hybrid(query, active_chips=None)
    if pa_name:
        chips = set(PROGRAM_ADVANCES[pa_name]["chips"])
        print(f"   🎯 PA Pre-detect ({method}): '{pa_name}' may fire, forcing chips: {list(chips)}")
        return chips
    return set()

def detect_program_advance(active_chips: List[str], query: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Detect if active chips form a Program Advance.
    
    Returns:
        (advance_name, merge_strategy) or (None, None)
    """
    query_lower = query.lower()
    
    for advance_name, config in PROGRAM_ADVANCES.items():
        required_chips = set(config["chips"])
        active_set = set(active_chips)
        
        # Check if we have the required chips
        if not required_chips.issubset(active_set):
            continue
        
        # Check if query matches trigger patterns
        triggers = config["triggers"]
        if any(trigger in query_lower for trigger in triggers):
            return advance_name, config["merge_strategy"]
    
    return None, None

def apply_merge_strategy(chip_results: Dict[str, Any], strategy: str, query: str) -> str:
    """
    Apply special merge logic for Program Advances.
    """
    if strategy == "timeline_priority":
        return merge_timeline_priority(chip_results, query)
    elif strategy == "evidence_chain":
        return merge_evidence_chain(chip_results, query)
    elif strategy == "comprehensive":
        return merge_comprehensive(chip_results, query)
    elif strategy == "business_focus":
        return merge_business_focus(chip_results, query)
    else:
        return merge_default(chip_results, query)

def merge_timeline_priority(chip_contexts: Dict[str, Tuple[str, str]], query: str) -> str:
    """
    Timeline Priority Merge for Context Recovery.
    Emphasizes recent information and chronological flow.
    """
    parts = []
    
    # Start with scaffolding (timeline)
    if "scaffolding" in chip_contexts and chip_contexts["scaffolding"]:
        context, _ = chip_contexts["scaffolding"]
        parts.append("=== RECENT PROJECT CONTEXT ===")
        parts.append(context)
    
    # Add RAG results filtered for recent/relevant content
    if "rag_search" in chip_contexts and chip_contexts["rag_search"]:
        context, _ = chip_contexts["rag_search"]
        parts.append("\n=== RELATED DISCUSSIONS ===")
        # In a full implementation, this would filter RAG by date/relevance
        parts.append(context)
    
    return "\n\n".join(parts)

def merge_evidence_chain(chip_contexts: Dict[str, Tuple[str, str]], query: str) -> str:
    """
    Evidence Chain Merge for Decision Audit.
    Structures content as claim → evidence.
    """
    parts = []
    
    # Start with decisions (claims)
    if "decisions" in chip_contexts and chip_contexts["decisions"]:
        context, _ = chip_contexts["decisions"]
        parts.append("=== DECISIONS ===")
        parts.append(context)
    
    # Add RAG results as supporting evidence
    if "rag_search" in chip_contexts and chip_contexts["rag_search"]:
        context, _ = chip_contexts["rag_search"]
        parts.append("\n=== SUPPORTING EVIDENCE ===")
        parts.append(context)
    
    return "\n\n".join(parts)

def merge_comprehensive(chip_contexts: Dict[str, Tuple[str, str]], query: str) -> str:
    """
    Comprehensive merge for complex queries.
    Includes all available context with smart ordering.
    """
    priority_order = ["project_state", "constella", "rag_search", "decisions", "scaffolding"]
    parts = []
    
    for chip in priority_order:
        if chip in chip_contexts and chip_contexts[chip]:
            context, _ = chip_contexts[chip]
            chip_name = chip.replace("_", " ").title()
            parts.append(f"=== {chip_name.upper()} ===")
            parts.append(context)
    
    return "\n\n".join(parts)

def merge_business_focus(chip_contexts: Dict[str, Tuple[str, str]], query: str) -> str:
    """
    Business-focused merge for business queries.
    Prioritizes business-relevant information.
    """
    parts = []
    
    # Business state first
    if "project_state" in chip_contexts and chip_contexts["project_state"]:
        context, _ = chip_contexts["project_state"]
        parts.append("=== BUSINESS STATUS ===")
        parts.append(context)
    
    # Related discussions
    if "rag_search" in chip_contexts and chip_contexts["rag_search"]:
        context, _ = chip_contexts["rag_search"]
        parts.append("\n=== BUSINESS DISCUSSIONS ===")
        parts.append(context)
    
    return "\n\n".join(parts)

def merge_default(chip_contexts: Dict[str, Tuple[str, str]], query: str) -> str:
    """
    Default merge strategy.
    """
    parts = []
    for chip_name, (context, _) in chip_contexts.items():
        if context and context.strip():
            parts.append(context)
    return "\n\n".join(parts)

# ---------------------------
# Weighted RRF Fusion
# ---------------------------

DEFAULT_CHIP_WEIGHTS = {
    "rag_search": 0.7,
    "google_search": 0.75,
    "decisions": 0.8,
    "constella": 0.75,
    "conversation_history": 0.6,
    "self_awareness": 0.5,
    "project_structure": 0.4,
    "scaffolding": 0.3
}

def weighted_rrf_fusion(chip_contexts: Dict[str, Tuple[str, str]], intent: Dict[str, Any] = None, k: int = 60, query_text: str = None) -> str:
    """
    Weighted Reciprocal Rank Fusion for combining chip results with Phase 2 ML optimization.
    
    Args:
        chip_contexts: Dict of chip_name -> (context, chip_type)
        intent: Query intent for dynamic weight adjustment
        k: RRF constant (typically 60)
        query_text: Original query text for ML optimization
    
    Returns:
        Fused content string
    """
    if len(chip_contexts) <= 1:
        # No fusion needed for single chip
        chip_name, (context, _) = next(iter(chip_contexts.items()))
        return context
    
    fused_parts = []
    
    # Start with default weights
    weights = DEFAULT_CHIP_WEIGHTS.copy()
    
    # Phase 2: Apply ML-based weight optimization
    if PHASE2_ENABLED and query_text and intent:
        try:
            # Use semantic intent detection for better understanding
            enhanced_intent = semantic_intent_detector.detect_intent(query_text)
            
            # Use weight optimizer if trained
            if weight_optimizer.is_trained:
                optimized_weights = weight_optimizer.optimize_weights_for_query(query_text, enhanced_intent, weights)
                weights.update(optimized_weights)
                print(f"🤖 Applied ML-optimized weights")
            
            # Apply semantic intent-based adjustments
            if enhanced_intent.get('semantic_confidence', 0) > 0.7:
                # High confidence semantic detection - apply specific optimizations
                if enhanced_intent.get('is_alife_query'):
                    weights['rag_search'] = 0.9
                    weights['scaffolding'] = 0.1
                    weights['project_structure'] = 0.1
                elif enhanced_intent.get('is_self_query'):
                    weights['self_awareness'] = 0.8
                    weights['rag_search'] = 0.6
                elif enhanced_intent.get('is_why_question'):
                    weights['decisions'] = 0.8
                    weights['rag_search'] = 0.7
                elif enhanced_intent.get('is_project_query'):
                    weights['project_structure'] = 0.7
                    weights['rag_search'] = 0.6
                    weights['scaffolding'] = 0.5
                
                print(f"🧠 Applied semantic intent optimization (confidence: {enhanced_intent.get('semantic_confidence', 0):.3f})")
            
        except Exception as e:
            print(f"⚠️ Phase 2 optimization failed: {e}")
    
    # Fallback to traditional intent-based adjustment
    elif intent and intent.get('is_alife_query'):
        weights['rag_search'] = 0.9
        weights['scaffolding'] = 0.1
        weights['project_structure'] = 0.1
    
    # Sort chips by weight (descending)
    sorted_chips = sorted(
        chip_contexts.items(),
        key=lambda x: weights.get(x[0], 0.5),
        reverse=True
    )
    
    # Build fused content with weight information
    for chip_name, (context, chip_type) in sorted_chips:
        if context and context.strip():
            weight = weights.get(chip_name, 0.5)
            chip_display = chip_name.replace("_", " ").title()
            
            # Add Phase 2 indicators
            weight_indicator = ""
            if PHASE2_ENABLED and weight_optimizer.is_trained:
                weight_indicator = " (ML)"
            elif intent and intent.get('semantic_confidence', 0) > 0.7:
                weight_indicator = " (AI)"
            
            fused_parts.append(f"=== {chip_display.upper()} (Weight: {weight:.2f}{weight_indicator}) ===")
            fused_parts.append(context)
    
    return "\n\n".join(fused_parts)

# ---------------------------
# Enhanced Context Builder
# ---------------------------

def build_enhanced_context(query_text: str, intent: Dict[str, Any], chip_results: Dict[str, Any], 
                          rag_results: List[str] = None, session_id: str = None, model_used: str = None, provider_used: str = None) -> Dict[str, Any]:
    """
    Enhanced context builder with Program Advance detection, RRF fusion, and Phase 2 performance tracking.
    
    This function replaces the context assembly part of build_integrated_context.
    
    Returns:
        Dictionary with:
        - context: Final assembled context
        - integrations_used: List of chips that contributed
        - advance_detected: Program Advance name if detected
        - merge_strategy: Strategy used
        - metrics: Performance and quality metrics
        - phase2_optimization: Phase 2 optimization details
    """
    start_time = time.time()
    query_id = session_id or f"query_{int(time.time() * 1000)}"
    
    # Extract chip contexts from results
    chip_contexts = {}
    integrations_used = []
    
    for chip_name, result in chip_results.items():
        if result is None:
            continue
        
        if chip_name == "rag":
            context, rag_docs, chip_type = result
            if context:
                chip_contexts["rag_search"] = (context, chip_type)
                integrations_used.append("rag_search")
        else:
            context, chip_type = result
            if context:
                chip_contexts[chip_name] = (context, chip_type)
                if chip_type:
                    integrations_used.append(chip_type)
    
    # Phase 2: Enhanced intent detection
    enhanced_intent = intent
    if PHASE2_ENABLED:
        try:
            enhanced_intent = semantic_intent_detector.detect_intent(query_text)
            print(f"🧠 Enhanced intent: {enhanced_intent.get('detected_by', 'regex')}")
        except Exception as e:
            print(f"⚠️ Enhanced intent detection failed: {e}")
    
    # Detect Program Advances
    advance_name, merge_strategy = detect_program_advance(integrations_used, query_text)
    
    # Apply merge strategy with Phase 2 optimization
    if advance_name:
        # Program Advance detected - use special merge
        final_context = apply_merge_strategy(chip_contexts, merge_strategy, query_text)
        method_used = f"program_advance_{advance_name}"
    elif len(chip_contexts) > 1:
        # Multiple chips - use RRF fusion with Phase 2 optimization
        final_context = weighted_rrf_fusion(chip_contexts, enhanced_intent, query_text=query_text)
        method_used = "weighted_rrf_fusion"
    else:
        # Single chip - use as-is
        if chip_contexts:
            final_context = next(iter(chip_contexts.values()))[0]
            method_used = "single_chip"
        else:
            final_context = ""
            method_used = "no_chips"
    
    # Build metrics
    assembly_time = (time.time() - start_time) * 1000
    total_tokens = len(final_context) // 4  # Rough estimate
    
    metrics = {
        "assembly_time_ms": assembly_time,
        "total_tokens": total_tokens,
        "chips_used": len(integrations_used),
        "method": method_used,
        "advance_detected": advance_name,
        "merge_strategy": merge_strategy
    }
    
    # Phase 2: Track performance
    phase2_optimization = {}
    if PHASE2_ENABLED and model_used and provider_used:
        try:
            # Create performance record
            perf_record = QueryPerformance(
                query_id=query_id,
                timestamp=datetime.now(),
                intent=enhanced_intent,
                weights_used={},  # Will be populated if weight optimization was used
                chip_results=chip_results,
                response_time=assembly_time / 1000,
                model_used=model_used,
                provider_used=provider_used,
                accuracy_score=None,  # Will be updated with user feedback
                user_feedback=None,
                context_tokens=total_tokens,
                coherence_score=None,
                success=True,
                error_info=None
            )
            
            # Track the performance
            performance_tracker.track_query(perf_record)
            
            phase2_optimization = {
                "performance_tracked": True,
                "query_id": query_id,
                "enhanced_intent": enhanced_intent.get('detected_by', 'regex'),
                "semantic_confidence": enhanced_intent.get('semantic_confidence', 0),
                "ml_optimization": weight_optimizer.is_trained
            }
            
            print(f"📊 Performance tracked for {query_id}")
            
        except Exception as e:
            print(f"⚠️ Performance tracking failed: {e}")
            phase2_optimization = {"performance_tracked": False, "error": str(e)}
    
    return {
        "context": final_context,
        "integrations_used": integrations_used,
        "advance_detected": advance_name,
        "merge_strategy": merge_strategy,
        "metrics": metrics,
        "phase2_optimization": phase2_optimization
    }

# ---------------------------
# Integration Helper
# ---------------------------

def enhance_existing_context_builder(existing_results: Dict[str, Any], query_text: str, 
                                  intent: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance existing chip results with Program Advance detection and RRF fusion.
    
    Use this to upgrade your existing build_integrated_context without rewriting it.
    
    Args:
        existing_results: Results from your existing parallel chip retrieval
        query_text: Original query
        intent: Detected intent
    
    Returns:
        Enhanced results dictionary
    """
    # Extract chip results from existing format
    chip_results = {}
    
    # Map your existing chip names to enhanced format
    chip_mapping = {
        "history": "conversation_history",
        "self": "self_awareness",
        "rag": "rag_search",
        "decisions": "decisions",
        "project": "project_state",
        "scaffolding": "scaffolding",
        "structure": "project_structure"
    }
    
    # This would need to be adapted based on your existing result format
    # For now, assume we have the chip_results in the right format
    
    # Apply enhanced context building
    enhanced = build_enhanced_context(
        query_text=query_text,
        intent=intent,
        chip_results=existing_results.get("chip_results", {}),
        rag_results=existing_results.get("rag_results", []),
        session_id=existing_results.get("session_id")
    )
    
    return enhanced

if __name__ == "__main__":
    # Test Program Advance detection
    test_cases = [
        ("where was I with the FAITHH project?", ["scaffolding", "rag_search"]),
        ("why did we choose React for the frontend?", ["decisions", "rag_search"]),
        ("what's the current status of Tom Cat Sound?", ["project_state", "rag_search"]),
        ("tell me everything about the Constella framework", ["project_state", "rag_search", "constella"])
    ]
    
    print("=== Program Advance Detection Test ===")
    for query, chips in test_cases:
        advance, strategy = detect_program_advance(chips, query)
        print(f"Query: {query}")
        print(f"Chips: {chips}")
        print(f"Advance: {advance or 'None'}")
        print(f"Strategy: {strategy or 'None'}")
        print()

"""
FAITHH Parallel Chip Engine
Implements parallel chip retrieval with weighted RRF fusion
Based on CHIP_SYNERGY.md research findings

Key Features:
- Parallel chip execution (ThreadPoolExecutor)
- Weighted Reciprocal Rank Fusion (RRF)
- Token budget allocation
- Conflict detection
- Performance metrics
"""

from __future__ import annotations

import json
import time
import math
from datetime import datetime
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

# Import existing FAITHH components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.data_loaders import load_json, load_yaml
from backend.intent_detection import detect_intent


# ---------------------------
# Configuration & Types
# ---------------------------

@dataclass
class ChipResult:
    """Result from a single chip retrieval."""
    chip_name: str
    content: str
    sources: List[Dict[str, Any]]
    relevance_score: float
    latency_ms: float
    token_count: int
    error: Optional[str] = None

@dataclass
class QueryMetrics:
    """Metrics for query performance tracking."""
    query_id: str
    timestamp: datetime
    query_text: str
    intent_detected: str
    chips_activated: List[str]
    advance_detected: Optional[str]
    total_latency_ms: float
    chip_latencies_ms: Dict[str, float]
    tokens_used: Dict[str, int]
    conflicts_detected: List[str]

# Default chip weights based on research
DEFAULT_CHIP_WEIGHTS = {
    "rag_search": 1.0,
    "scaffolding": 0.9,
    "decision_logs": 0.85,
    "project_state": 0.8,
    "constella": 0.75,
    "conversation_history": 0.6,
    "self_awareness": 0.5,
    "filesystem": 0.4
}

# Token budget allocation by query type (from research)
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
    },
    "default": {
        "rag_search": 0.40,
        "scaffolding": 0.20,
        "decision_logs": 0.15,
        "project_state": 0.10,
        "constella": 0.10,
        "conversation_history": 0.05
    }
}

# ---------------------------
# Utility Functions
# ---------------------------

def count_tokens(text: str) -> int:
    """Rough token count (4 chars ≈ 1 token for English)."""
    return len(text) // 4

def classify_query_type(query: str) -> str:
    """Simple query classification for budget allocation."""
    query_lower = query.lower()
    
    # Check for specific patterns
    if any(term in query_lower for term in ["what is", "tell me about", "explain", "define"]):
        if "constella" in query_lower or any(x in query_lower for x in ["astris", "auctor", "harmonic"]):
            return "constella_query"
        return "factual_lookup"
    
    if any(term in query_lower for term in ["status", "progress", "where are we", "current state"]):
        return "project_status"
    
    if any(term in query_lower for term in ["why did", "decision", "rationale", "reasoning"]):
        return "decision_review"
    
    return "default"

def allocate_token_budget(query_type: str, total_tokens: int = 4500) -> Dict[str, int]:
    """Allocate token budget based on query type."""
    ratios = QUERY_TYPE_BUDGETS.get(query_type, QUERY_TYPE_BUDGETS["default"])
    return {chip: int(ratio * total_tokens) for chip, ratio in ratios.items()}

# ---------------------------
# Chip Retrieval Functions
# ---------------------------

class ChipRetriever:
    """Handles individual chip retrieval logic."""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(__file__))
        self.chroma_client = None
        self._init_chroma()
    
    def _init_chroma(self):
        """Initialize ChromaDB connection."""
        try:
            import chromadb
            self.chroma_client = chromadb.HttpClient(host="servicebox.taileb8c60.ts.net", port=8000)
            self.collection = self.chroma_client.get_collection("faithh_knowledge_base")
        except Exception as e:
            print(f"ChromaDB connection failed: {e}")
            self.chroma_client = None
    
    def retrieve_rag_search(self, query: str, budget: int) -> ChipResult:
        """Retrieve from RAG/ChromaDB."""
        start_time = time.time()
        
        if not self.chroma_client:
            return ChipResult(
                chip_name="rag_search",
                content="",
                sources=[],
                relevance_score=0.0,
                latency_ms=0,
                token_count=0,
                error="ChromaDB not connected"
            )
        
        try:
            # Estimate number of docs based on budget (~200 tokens per doc)
            n_docs = max(1, budget // 200)
            results = self.collection.query(
                query_texts=[query],
                n_results=n_docs
            )
            
            if results['documents'] and results['documents'][0]:
                documents = results['documents'][0]
                metadatas = results['metadatas'][0] if results['metadatas'] else [{}] * len(documents)
                distances = results['distances'][0] if results['distances'] else [1.0] * len(documents)
                
                # Build content with sources
                content_parts = []
                sources = []
                
                for doc, meta, dist in zip(documents, metadatas, distances):
                    content_parts.append(doc)
                    sources.append({
                        "content": doc[:200] + "..." if len(doc) > 200 else doc,
                        "metadata": meta,
                        "distance": dist
                    })
                
                content = "\n\n".join(content_parts)
                
                # Calculate relevance score (inverse of average distance)
                avg_distance = sum(distances) / len(distances) if distances else 1.0
                relevance_score = 1.0 / (1.0 + avg_distance)
                
                return ChipResult(
                    chip_name="rag_search",
                    content=content,
                    sources=sources,
                    relevance_score=relevance_score,
                    latency_ms=(time.time() - start_time) * 1000,
                    token_count=count_tokens(content)
                )
            else:
                return ChipResult(
                    chip_name="rag_search",
                    content="",
                    sources=[],
                    relevance_score=0.0,
                    latency_ms=(time.time() - start_time) * 1000,
                    token_count=0
                )
                
        except Exception as e:
            return ChipResult(
                chip_name="rag_search",
                content="",
                sources=[],
                relevance_score=0.0,
                latency_ms=(time.time() - start_time) * 1000,
                token_count=0,
                error=str(e)
            )
    
    def retrieve_scaffolding(self, query: str, budget: int) -> ChipResult:
        """Retrieve scaffolding context."""
        start_time = time.time()
        
        try:
            scaffolding_path = os.path.join(self.base_dir, "scaffolding_state.json")
            scaffolding = load_json(scaffolding_path)
            
            if scaffolding:
                # Build context from scaffolding
                content_parts = []
                
                if scaffolding.get("open_loops"):
                    content_parts.append("Open Loops:\n" + "\n".join(f"- {loop}" for loop in scaffolding["open_loops"][:5]))
                
                if scaffolding.get("parked_tangents"):
                    content_parts.append("Parked Tangents:\n" + "\n".join(f"- {tangent}" for tangent in scaffolding["parked_tangents"][:3]))
                
                if scaffolding.get("last_focus"):
                    content_parts.append(f"Last Focus: {scaffolding['last_focus']}")
                
                content = "\n\n".join(content_parts)
                
                # Truncate to budget if needed
                if count_tokens(content) > budget:
                    content = content[:budget * 4]  # Rough truncation
                
                return ChipResult(
                    chip_name="scaffolding",
                    content=content,
                    sources=[{"type": "scaffolding_state", "updated": scaffolding.get("updated")}],
                    relevance_score=0.8,  # High relevance for project context
                    latency_ms=(time.time() - start_time) * 1000,
                    token_count=count_tokens(content)
                )
            else:
                return ChipResult(
                    chip_name="scaffolding",
                    content="",
                    sources=[],
                    relevance_score=0.0,
                    latency_ms=(time.time() - start_time) * 1000,
                    token_count=0
                )
                
        except Exception as e:
            return ChipResult(
                chip_name="scaffolding",
                content="",
                sources=[],
                relevance_score=0.0,
                latency_ms=(time.time() - start_time) * 1000,
                token_count=0,
                error=str(e)
            )
    
    def retrieve_decision_logs(self, query: str, budget: int) -> ChipResult:
        """Retrieve decision logs."""
        start_time = time.time()
        
        try:
            decisions_path = os.path.join(self.base_dir, "decisions_log.json")
            decisions = load_json(decisions_path)
            
            if decisions and decisions.get("decisions"):
                # Get recent decisions (last 10)
                recent_decisions = decisions["decisions"][-10:]
                
                content_parts = []
                sources = []
                
                for decision in recent_decisions:
                    decision_text = f"Decision: {decision.get('decision', 'N/A')}\n"
                    decision_text += f"Rationale: {decision.get('rationale', 'N/A')}\n"
                    decision_text += f"Date: {decision.get('date', 'N/A')}\n"
                    
                    content_parts.append(decision_text)
                    sources.append({
                        "type": "decision",
                        "decision": decision.get('decision'),
                        "date": decision.get('date'),
                        "rationale": decision.get('rationale')
                    })
                
                content = "\n\n".join(content_parts)
                
                # Truncate to budget if needed
                if count_tokens(content) > budget:
                    content = content[:budget * 4]
                
                return ChipResult(
                    chip_name="decision_logs",
                    content=content,
                    sources=sources,
                    relevance_score=0.85,  # High relevance for decisions
                    latency_ms=(time.time() - start_time) * 1000,
                    token_count=count_tokens(content)
                )
            else:
                return ChipResult(
                    chip_name="decision_logs",
                    content="",
                    sources=[],
                    relevance_score=0.0,
                    latency_ms=(time.time() - start_time) * 1000,
                    token_count=0
                )
                
        except Exception as e:
            return ChipResult(
                chip_name="decision_logs",
                content="",
                sources=[],
                relevance_score=0.0,
                latency_ms=(time.time() - start_time) * 1000,
                token_count=0,
                error=str(e)
            )
    
    def retrieve_project_state(self, query: str, budget: int) -> ChipResult:
        """Retrieve project state."""
        start_time = time.time()
        
        try:
            projects_path = os.path.join(self.base_dir, "project_states.json")
            projects = load_json(projects_path)
            
            if projects:
                content_parts = []
                sources = []
                
                for project_name, project_data in projects.items():
                    if isinstance(project_data, dict):
                        content_parts.append(f"Project: {project_name}")
                        content_parts.append(f"Status: {project_data.get('status', 'N/A')}")
                        content_parts.append(f"Phase: {project_data.get('phase', 'N/A')}")
                        
                        if project_data.get('last_updated'):
                            content_parts.append(f"Updated: {project_data['last_updated']}")
                        
                        content_parts.append("---")
                        
                        sources.append({
                            "type": "project",
                            "name": project_name,
                            "status": project_data.get('status'),
                            "phase": project_data.get('phase')
                        })
                
                content = "\n".join(content_parts)
                
                # Truncate to budget if needed
                if count_tokens(content) > budget:
                    content = content[:budget * 4]
                
                return ChipResult(
                    chip_name="project_state",
                    content=content,
                    sources=sources,
                    relevance_score=0.8,
                    latency_ms=(time.time() - start_time) * 1000,
                    token_count=count_tokens(content)
                )
            else:
                return ChipResult(
                    chip_name="project_state",
                    content="",
                    sources=[],
                    relevance_score=0.0,
                    latency_ms=(time.time() - start_time) * 1000,
                    token_count=0
                )
                
        except Exception as e:
            return ChipResult(
                chip_name="project_state",
                content="",
                sources=[],
                relevance_score=0.0,
                latency_ms=(time.time() - start_time) * 1000,
                token_count=0,
                error=str(e)
            )
    
    def retrieve_constella(self, query: str, budget: int) -> ChipResult:
        """Retrieve Constella framework context."""
        start_time = time.time()
        
        try:
            # Look for constella files
            constella_dir = os.path.join(self.base_dir, "projects", "constella-framework")
            
            if os.path.exists(constella_dir):
                # Get key constella files
                readme_path = os.path.join(constella_dir, "README.md")
                concepts_path = os.path.join(constella_dir, "CONCEPTS.md")
                
                content_parts = ["Constella Framework Context:"]
                sources = []
                
                if os.path.exists(readme_path):
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        readme_content = f.read()[:1000]  # First 1000 chars
                        content_parts.append(f"README:\n{readme_content}")
                        sources.append({"type": "file", "name": "README.md"})
                
                if os.path.exists(concepts_path):
                    with open(concepts_path, 'r', encoding='utf-8') as f:
                        concepts_content = f.read()[:1000]
                        content_parts.append(f"CONCEPTS:\n{concepts_content}")
                        sources.append({"type": "file", "name": "CONCEPTS.md"})
                
                content = "\n\n".join(content_parts)
                
                # Truncate to budget if needed
                if count_tokens(content) > budget:
                    content = content[:budget * 4]
                
                return ChipResult(
                    chip_name="constella",
                    content=content,
                    sources=sources,
                    relevance_score=0.75,
                    latency_ms=(time.time() - start_time) * 1000,
                    token_count=count_tokens(content)
                )
            else:
                return ChipResult(
                    chip_name="constella",
                    content="",
                    sources=[],
                    relevance_score=0.0,
                    latency_ms=(time.time() - start_time) * 1000,
                    token_count=0
                )
                
        except Exception as e:
            return ChipResult(
                chip_name="constella",
                content="",
                sources=[],
                relevance_score=0.0,
                latency_ms=(time.time() - start_time) * 1000,
                token_count=0,
                error=str(e)
            )


# ---------------------------
# Parallel Engine
# ---------------------------

class ParallelChipEngine:
    """Main parallel chip retrieval and fusion engine."""
    
    def __init__(self, max_workers: int = 5):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.retriever = ChipRetriever()
        self.chip_methods = {
            "rag_search": self.retriever.retrieve_rag_search,
            "scaffolding": self.retriever.retrieve_scaffolding,
            "decision_logs": self.retriever.retrieve_decision_logs,
            "project_state": self.retriever.retrieve_project_state,
            "constella": self.retriever.retrieve_constella
        }
    
    def retrieve_from_chip(self, chip_name: str, query: str, budget: int) -> ChipResult:
        """Execute retrieval for a single chip."""
        if chip_name in self.chip_methods:
            return self.chip_methods[chip_name](query, budget)
        else:
            return ChipResult(
                chip_name=chip_name,
                content="",
                sources=[],
                relevance_score=0.0,
                latency_ms=0,
                token_count=0,
                error=f"Unknown chip: {chip_name}"
            )
    
    def parallel_chip_retrieval(self, query: str, active_chips: List[str], budgets: Dict[str, int]) -> Dict[str, ChipResult]:
        """
        Execute all chip retrievals in parallel.
        
        Without parallel: 5 chips × 500ms = 2500ms
        With parallel: max(500ms across all) ≈ 500-600ms
        """
        futures = {}
        
        # Submit all chips to thread pool
        for chip in active_chips:
            if chip in self.chip_methods:  # Only process known chips
                future = self.executor.submit(
                    self.retrieve_from_chip,
                    chip,
                    query,
                    budgets.get(chip, 500)
                )
                futures[future] = chip
        
        # Collect results as they complete
        results = {}
        for future in as_completed(futures, timeout=5.0):  # 5 second max wait
            chip_name = futures[future]
            try:
                results[chip_name] = future.result()
            except Exception as e:
                results[chip_name] = ChipResult(
                    chip_name=chip_name,
                    content="",
                    sources=[],
                    relevance_score=0.0,
                    latency_ms=0,
                    token_count=0,
                    error=str(e)
                )
        
        return results
    
    def weighted_rrf_fusion(self, chip_results: Dict[str, ChipResult], k: int = 60) -> Dict[str, Any]:
        """
        Weighted Reciprocal Rank Fusion for combining chip results.
        
        RRF formula: score = sum(w_i / (k + rank_i))
        where w_i is chip weight, rank_i is rank in that chip
        """
        if len(chip_results) <= 1:
            # No fusion needed for single chip
            chip_name, result = next(iter(chip_results.items()))
            return {
                "fused_content": result.content,
                "sources": result.sources,
                "method": "single_chip",
                "chip_used": chip_name
            }
        
        # Collect all sources from all chips with their ranks
        all_sources = []
        
        for chip_name, chip_result in chip_results.items():
            if chip_result.error or not chip_result.sources:
                continue
                
            chip_weight = DEFAULT_CHIP_WEIGHTS.get(chip_name, 1.0)
            
            for rank, source in enumerate(chip_result.sources, 1):
                all_sources.append({
                    "source": source,
                    "chip": chip_name,
                    "rank": rank,
                    "weight": chip_weight,
                    "rrf_score": chip_weight / (k + rank)
                })
        
        if not all_sources:
            return {
                "fused_content": "",
                "sources": [],
                "method": "rrf_fusion",
                "note": "No sources to fuse"
            }
        
        # Sort by RRF score (descending)
        all_sources.sort(key=lambda x: x["rrf_score"], reverse=True)
        
        # Build fused content from top sources
        fused_parts = []
        final_sources = []
        
        for source_info in all_sources[:10]:  # Top 10 sources
            source = source_info["source"]
            fused_parts.append(source.get("content", str(source)))
            final_sources.append({
                **source,
                "chip": source_info["chip"],
                "rrf_score": source_info["rrf_score"]
            })
        
        fused_content = "\n\n".join(fused_parts)
        
        return {
            "fused_content": fused_content,
            "sources": final_sources,
            "method": "rrf_fusion",
            "chips_used": list(chip_results.keys()),
            "total_sources": len(all_sources)
        }
    
    def detect_conflicts(self, chip_results: Dict[str, ChipResult]) -> List[str]:
        """Simple conflict detection between chip results."""
        conflicts = []
        
        # Check for temporal conflicts
        all_dates = []
        for chip_result in chip_results.values():
            for source in chip_result.sources:
                if source.get("date"):
                    try:
                        # Simple date parsing
                        date_str = source["date"]
                        if isinstance(date_str, str):
                            all_dates.append(date_str)
                    except:
                        continue
        
        if len(all_dates) > 1:
            # Simple heuristic: if we have dates spanning more than 30 days
            conflicts.append("temporal_conflict")
        
        # Check for contradictory information (simplified)
        # In a full implementation, this would use entity extraction and comparison
        
        return conflicts
    
    def process_query(self, query: str, intent: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main query processing with parallel chip retrieval and fusion.
        
        Returns:
            Dictionary with:
            - content: Fused content from chips
            - sources: Combined sources
            - metrics: Performance and quality metrics
            - conflicts: Any detected conflicts
        """
        start_time = time.time()
        query_id = f"query_{int(start_time * 1000)}"
        
        # 1. Determine active chips from intent
        if intent is None:
            intent = detect_intent(query)
        
        active_chips = intent.get('integrations', ['rag_search'])
        
        # Filter to only available chips
        available_chips = [chip for chip in active_chips if chip in self.chip_methods]
        
        if not available_chips:
            available_chips = ['rag_search']  # Fallback to RAG
        
        # 2. Allocate token budgets
        query_type = classify_query_type(query)
        budgets = allocate_token_budget(query_type)
        
        # 3. Parallel retrieval
        chip_results = self.parallel_chip_retrieval(query, available_chips, budgets)
        
        # 4. Detect conflicts
        conflicts = self.detect_conflicts(chip_results)
        
        # 5. Apply RRF fusion if multiple chips
        if len(chip_results) > 1:
            fusion_result = self.weighted_rrf_fusion(chip_results)
        else:
            # Single chip case
            chip_name, result = next(iter(chip_results.items()))
            fusion_result = {
                "fused_content": result.content,
                "sources": result.sources,
                "method": "single_chip",
                "chip_used": chip_name
            }
        
        # 6. Build metrics
        total_latency_ms = (time.time() - start_time) * 1000
        chip_latencies_ms = {chip: result.latency_ms for chip, result in chip_results.items()}
        tokens_used = {chip: result.token_count for chip, result in chip_results.items()}
        
        metrics = QueryMetrics(
            query_id=query_id,
            timestamp=datetime.now(),
            query_text=query,
            intent_detected=str(intent.get('intent', 'unknown')),
            chips_activated=available_chips,
            advance_detected=None,  # TODO: Implement Program Advance detection
            total_latency_ms=total_latency_ms,
            chip_latencies_ms=chip_latencies_ms,
            tokens_used=tokens_used,
            conflicts_detected=conflicts
        )
        
        return {
            "content": fusion_result["fused_content"],
            "sources": fusion_result["sources"],
            "method": fusion_result["method"],
            "chips_used": fusion_result.get("chips_used", available_chips),
            "metrics": metrics,
            "conflicts": conflicts,
            "query_type": query_type,
            "budgets": budgets
        }


# ---------------------------
# Global Instance
# ---------------------------

# Global engine instance (initialize once)
PARALLEL_CHIP_ENGINE = ParallelChipEngine(max_workers=5)


def get_parallel_chip_engine() -> ParallelChipEngine:
    """Get the global parallel chip engine instance."""
    return PARALLEL_CHIP_ENGINE


# ---------------------------
# Integration Helper
# ---------------------------

def process_query_with_parallel_chips(query: str, intent: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function for integration with existing FAITHH backend.
    
    Usage:
        result = process_query_with_parallel_chips(query, intent)
        context = result['content']
        sources = result['sources']
        metrics = result['metrics']
    """
    engine = get_parallel_chip_engine()
    return engine.process_query(query, intent)


if __name__ == "__main__":
    # Quick test
    test_query = "What's the current status of the FAITHH project?"
    result = process_query_with_parallel_chips(test_query)
    
    print("=== Parallel Chip Engine Test ===")
    print(f"Query: {test_query}")
    print(f"Chips used: {result['chips_used']}")
    print(f"Method: {result['method']}")
    print(f"Total latency: {result['metrics'].total_latency_ms:.2f}ms")
    print(f"Content length: {len(result['content'])} chars")
    print(f"Sources found: {len(result['sources'])}")
    print(f"Conflicts: {result['conflicts']}")
    print("\nContent preview:")
    print(result['content'][:500] + "..." if len(result['content']) > 500 else result['content'])

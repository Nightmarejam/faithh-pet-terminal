"""
FAITHH Coherence Arbiter - Measures semantic convergence between RAG and ML chip routing signals

This module calculates convergence scores between RAG retrieval results and ML chip activations
to provide quantitative coherence measurement for the FAITHH system.

KEY INSIGHT: RAG Result Types and Embedding Availability
========================================================

The arbiter handles two distinct RAG result types:

1. Document-based RAG (broad open-ended queries):
   - Returns structured objects with 'document', 'embedding', 'distance', 'metadata', 'id'
   - Has full 384-dim embeddings from ChromaDB
   - Enables full convergence calculation with rag_chip_alignment signals
   - Example: "Tell me about my recent work across all projects"

2. Conversation-based RAG (focused/project queries):
   - Returns plain text conversation chunks (strings) 
   - No document embeddings - these are conversational excerpts
   - Appropriately falls back to signal_strength_only scoring
   - Example: "What is the current status of FAITHH Phase 4?"

This distinction is CORRECT BEHAVIOR, not a bug:
- Conversation chunks shouldn't have document embeddings as they're dialogue excerpts
- Signal strength fallback provides meaningful scoring for conversational relevance
- Only document-based queries should trigger full convergence calculation

Do NOT "fix" the conversation-based queries to have embeddings - this would be incorrect.

PHASE 2: Anchor Validation
=========================
Phase 2 adds ground truth validation of claims from canonical state files.
Currently validates FAITHH project phase status against actual system behavior.

KNOWN LIMITATION: Anchor validation only fires when rag_chip_alignment triggers
(i.e., when both RAG embeddings and chip embeddings are available). 
Conversation-based RAG queries (signal_strength_only) will show anchor_score: null.
This is expected behavior - anchor validation requires full convergence calculation
to provide meaningful validation context.
"""

import numpy as np
import time
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Phase 3: Tunable thresholds for tier and behavior (centralized for later adjustment)
COHERENCE_TIER_HIGH_THRESHOLD = 0.6
COHERENCE_TIER_MEDIUM_THRESHOLD = 0.3
ANCHOR_VALID_THRESHOLD = 0.7
LOW_CONFIDENCE_TIER = "low"

def _enrich_phase3_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add Phase 3 fields: tier, reasons, low_confidence, suggested_behavior.
    Keeps all existing keys; adds new ones for UI and behavior hooks.
    """
    score = metadata.get("convergence_score", 0.5)
    raw = metadata.get("raw_convergence", 0.5)
    signals = metadata.get("convergence_signals", [])
    anchor = metadata.get("anchor_validation", {})
    anchor_enabled = anchor.get("enabled", False)
    faithh_phase = anchor.get("faithh_phase", {}) if isinstance(anchor.get("faithh_phase"), dict) else {}
    anchor_score = faithh_phase.get("validation_score")
    anchor_valid = faithh_phase.get("is_valid", False)

    reasons = list(signals) if signals else []
    if anchor_enabled and anchor_score is not None:
        reasons.append(f"anchor_validation_{anchor_score:.2f}")
    if "rag_chip_alignment" in signals:
        reasons.append("strong_rag_chip_alignment")
    if anchor_valid:
        reasons.append("anchor_phase3_pass")

    if score >= COHERENCE_TIER_HIGH_THRESHOLD and (not anchor_enabled or anchor_valid):
        tier = "high"
    elif score >= COHERENCE_TIER_MEDIUM_THRESHOLD:
        tier = "medium"
    else:
        tier = LOW_CONFIDENCE_TIER

    low_confidence = tier == LOW_CONFIDENCE_TIER or (anchor_enabled and not anchor_valid and anchor_score is not None)

    if low_confidence:
        suggested_behavior = "hedge"
    elif tier == "medium" and anchor_enabled and not anchor_valid:
        suggested_behavior = "recheck_sources"
    else:
        suggested_behavior = "ok"

    metadata["tier"] = tier
    metadata["reasons"] = reasons
    metadata["low_confidence"] = low_confidence
    metadata["suggested_behavior"] = suggested_behavior
    return metadata


class CoherenceArbiter:
    """Measures semantic convergence between FAITHH subsystems with Phase 2 anchor validation"""
    
    def __init__(self, timeout_ms: int = 100):
        self.timeout_ms = timeout_ms
        self.embedding_model_name = "all-MiniLM-L6-v2 (384-dim)"
        self.start_time = time.time()
        
        # Phase 2: Initialize anchor validator
        try:
            from .anchor_validator import AnchorValidator
            self.anchor_validator = AnchorValidator()
            self.phase2_enabled = True
        except ImportError:
            self.anchor_validator = None
            self.phase2_enabled = False
        
    def measure_convergence(self, rag_results: List[Dict], chip_activations: List[Dict], 
                          query_embedding: Optional[np.ndarray] = None,
                          ml_chips=None, ml_chip_centroids=None) -> Dict[str, Any]:
        """
        Measure semantic convergence between RAG and chip signals
        
        Args:
            rag_results: List of RAG retrieval results with embeddings
            chip_activations: List of activated ML chips with centroids
            query_embedding: Query embedding (optional, for additional analysis)
            
        Returns:
            Dict with coherence metrics and metadata
        """
        start_time = time.time()
        
        try:
            # Check timeout
            if (time.time() - start_time) * 1000 > self.timeout_ms:
                logger.warning(f"Coherence arbiter timed out after {self.timeout_ms}ms")
                return _enrich_phase3_metadata(self._fallback_result("timeout"))
            
            # Extract signals
            rag_embeddings = self._extract_rag_embeddings(rag_results)
            # Do NOT derive ids from ml_chips: the backend only appends to
            # ML_CHIP_IDS for chips that had a valid 384/768-dim centroid, while
            # ML_CHIPS holds every chip. Deriving ids from ml_chips would produce a
            # longer list and silently misalign the id->centroid zip. Both halves are
            # resolved together from the backend module so they stay a matched pair.
            chip_embeddings = self._extract_chip_embeddings(chip_activations)
            
            # Handle edge cases
            if not rag_embeddings or not chip_embeddings:
                # If we don't have embeddings, we can still provide a meaningful score
                # based on signal strength alone
                signal_strength = self._calculate_signal_strength(rag_results, chip_activations)
                out = {
                    "convergence_score": signal_strength * 0.5,  # Reduce score for no convergence data
                    "raw_convergence": 0.5,
                    "signal_weight": signal_strength,
                    "convergence_signals": ["signal_strength_only"],
                    "signal_strength": {
                        "rag": self._rag_signal_strength(rag_results),
                        "chips": self._chip_signal_strength(chip_activations)
                    },
                    "details": {
                        "rag_chunks": len(rag_results),
                        "chips_activated": len(chip_activations),
                        "no_embeddings": True,
                        "calculation_time_ms": (time.time() - start_time) * 1000
                    }
                }
                if self.phase2_enabled and self.anchor_validator:
                    try:
                        validation_result = self.anchor_validator.validate_faithh_phase(
                            ml_chips=ml_chips,
                            ml_chip_centroids=ml_chip_centroids
                        )
                        out["anchor_validation"] = {
                            "enabled": True,
                            "faithh_phase": validation_result,
                            "validation_timestamp": validation_result.get("validation_timestamp"),
                        }
                    except Exception as e:
                        out["anchor_validation"] = {"enabled": True, "error": str(e), "validation_timestamp": datetime.now().isoformat()}
                else:
                    out["anchor_validation"] = {"enabled": False, "reason": "Phase 2 not available"}
                return _enrich_phase3_metadata(out)
            
            # Calculate convergence matrix
            convergence_matrix = self._calculate_convergence_matrix(rag_embeddings, chip_embeddings)
            
            # Calculate convergence score using np.mean(np.max(..., axis=1))
            convergence_score = np.mean(np.max(convergence_matrix, axis=1))
            
            # Calculate signal strength with real teeth
            signal_strength = self._calculate_signal_strength(rag_results, chip_activations)
            
            # Apply signal weight
            final_score = convergence_score * signal_strength
            
            # Generate metadata
            metadata = {
                "convergence_score": float(np.clip(final_score, 0.0, 1.0)),
                "raw_convergence": float(convergence_score),
                "signal_weight": float(signal_strength),
                "convergence_signals": ["rag_chip_alignment"],
                "signal_strength": {
                    "rag": self._rag_signal_strength(rag_results),
                    "chips": self._chip_signal_strength(chip_activations)
                },
                "details": {
                    "rag_chunks": len(rag_results),
                    "chips_activated": len(chip_activations),
                    "convergence_matrix_shape": convergence_matrix.shape,
                    "max_alignment": float(np.max(convergence_matrix)),
                    "calculation_time_ms": (time.time() - start_time) * 1000
                }
            }
            
            # Phase 2: Add anchor validation if enabled
            if self.phase2_enabled and self.anchor_validator:
                try:
                    validation_result = self.anchor_validator.validate_faithh_phase(
                        ml_chips=ml_chips,
                        ml_chip_centroids=ml_chip_centroids
                    )
                    metadata["anchor_validation"] = {
                        "enabled": True,
                        "faithh_phase": validation_result,
                        "validation_timestamp": validation_result.get('validation_timestamp')
                    }
                except Exception as e:
                    metadata["anchor_validation"] = {
                        "enabled": True,
                        "error": str(e),
                        "validation_timestamp": datetime.now().isoformat()
                    }
            else:
                metadata["anchor_validation"] = {
                    "enabled": False,
                    "reason": "Phase 2 not available"
                }
            
            logger.debug(f"Coherence measured: {metadata['convergence_score']:.3f} "
                        f"(convergence: {metadata['raw_convergence']:.3f}, "
                        f"weight: {metadata['signal_weight']:.3f})")
            
            return _enrich_phase3_metadata(metadata)
            
        except Exception as e:
            logger.error(f"Coherence arbiter error: {e}")
            return _enrich_phase3_metadata(self._fallback_result(f"error: {str(e)}"))
    
    def _extract_rag_embeddings(self, rag_results: List[Dict]) -> List[np.ndarray]:
        """Extract embeddings from RAG results"""
        embeddings = []
        
        for result in rag_results:
            # Handle different RAG result formats
            if isinstance(result, dict):
                # Standard format with embedding field
                if 'embedding' in result and result['embedding'] is not None:
                    embedding = np.array(result['embedding'])
                    embeddings.append(embedding)  # Keep as numpy array
                # Alternative format with metadata
                elif 'metadata' in result and 'embedding' in result['metadata']:
                    embedding = np.array(result['metadata']['embedding'])
                    embeddings.append(embedding)  # Keep as numpy array
                # Document with distance but no embedding - skip these
                elif 'document' in result and 'distance' in result and 'embedding' not in result:
                    # Skip results without embeddings
                    continue
            elif isinstance(result, str):
                # String result - try to parse as JSON to extract embeddings
                try:
                    import json
                    parsed = json.loads(result)
                    if isinstance(parsed, dict) and 'embedding' in parsed and parsed['embedding'] is not None:
                        embedding = np.array(parsed['embedding'])
                        embeddings.append(embedding)
                except (json.JSONDecodeError, KeyError):
                    # Plain text document - no embedding available
                    continue
                
        # If no embeddings found, we'll need to handle this gracefully
        # This can happen when RAG results don't include embeddings
        if not embeddings and rag_results:
            pass  # Removed debug print for production
            
        return embeddings
    
    def _extract_chip_embeddings(self, chip_activations: List[Dict],
                                 ml_chip_centroids=None,
                                 ml_chip_ids=None) -> List[np.ndarray]:
        """Extract centroids from activated ML chips"""
        embeddings = []

        if ml_chip_centroids is None or ml_chip_ids is None:
            # Read the centroids off the already-loaded backend module instead of
            # importing it.
            #
            # The backend runs as `python faithh_professional_backend_fixed.py`, so it
            # lives in sys.modules as "__main__". Importing it *by name* creates a
            # second module object and re-executes the file top to bottom, which
            # re-registers its Prometheus collectors against the default global
            # registry and raises:
            #     ValueError: Duplicated timeseries in CollectorRegistry:
            #                 {'faithh_requests_total', 'faithh_requests_created', ...}
            # That is not an ImportError, so the old `except ImportError` here never
            # caught it. It propagated to measure_convergence's handler, which
            # returned a hardcoded 0.5 — every coherence score the system reported
            # was that constant, not a measurement.
            import sys
            _mod = (sys.modules.get("faithh_professional_backend_fixed")
                    or sys.modules.get("__main__"))
            if ml_chip_centroids is None:
                ml_chip_centroids = getattr(_mod, "ML_CHIP_CENTROIDS", None)
            if ml_chip_ids is None:
                ml_chip_ids = getattr(_mod, "ML_CHIP_IDS", None)

        if ml_chip_centroids is None or ml_chip_ids is None:
            return embeddings

        # Create mapping from chip ID to centroid
        id_to_centroid = dict(zip(ml_chip_ids, ml_chip_centroids))
        
        for chip in chip_activations:
            chip_id = chip.get('id')
            if chip_id and chip_id in id_to_centroid:
                centroid = id_to_centroid[chip_id]
                embeddings.append(np.array(centroid))
                
        return embeddings
    
    def _calculate_convergence_matrix(self, rag_embeddings: List[np.ndarray], 
                                   chip_embeddings: List[np.ndarray]) -> np.ndarray:
        """Calculate cosine similarity matrix between RAG and chip embeddings"""
        # Convert to numpy arrays
        rag_matrix = np.array(rag_embeddings)
        chip_matrix = np.array(chip_embeddings)
        
        # Normalize embeddings for cosine similarity
        rag_norm = np.linalg.norm(rag_matrix, axis=1, keepdims=True)
        chip_norm = np.linalg.norm(chip_matrix, axis=1, keepdims=True)
        
        # Avoid division by zero
        rag_norm = np.where(rag_norm == 0, 1, rag_norm)
        chip_norm = np.where(chip_norm == 0, 1, chip_norm)
        
        rag_normalized = rag_matrix / rag_norm
        chip_normalized = chip_matrix / chip_norm
        
        # Calculate cosine similarity matrix
        convergence_matrix = np.dot(rag_normalized, chip_normalized.T)
        
        return convergence_matrix
    
    def _calculate_signal_strength(self, rag_results: List[Dict], 
                                chip_activations: List[Dict]) -> float:
        """
        Calculate signal strength with real teeth
        Returns values that meaningfully distinguish signal quality
        """
        rag_strength = self._rag_signal_strength(rag_results)
        chip_strength = self._chip_signal_strength(chip_activations)
        
        # If one modality has no signal, use the other modality's strength
        # This prevents a zero signal in one modality from zeroing out everything
        if rag_strength == 0.0 and chip_strength == 0.0:
            return 0.0  # Both have no signal
        elif chip_strength == 0.0:
            return rag_strength * 0.7  # Only RAG signal, penalize for missing chips
        elif rag_strength == 0.0:
            return chip_strength * 0.7  # Only chip signal, penalize for missing RAG
        else:
            # Both signals present - use minimum to ensure both are good
            combined_strength = min(rag_strength, chip_strength)
            return combined_strength
    
    def _rag_signal_strength(self, rag_results: List[Dict]) -> float:
        """Calculate RAG signal strength with meaningful variation"""
        if not rag_results:
            return 0.0
        
        strength = 1.0
        
        # Penalty for low result count
        if len(rag_results) < 3:
            strength *= 0.7
        elif len(rag_results) < 5:
            strength *= 0.85
        
        # Penalty for high distances (poor matches)
        distances = []
        for result in rag_results:
            if isinstance(result, dict) and 'distance' in result:
                distances.append(result['distance'])
        
        if distances:
            avg_distance = np.mean(distances)
            # Distance in ChromaDB is typically 0-2 for cosine similarity
            # Higher distance = worse match
            if avg_distance > 1.5:
                strength *= 0.6
            elif avg_distance > 1.2:
                strength *= 0.8
            elif avg_distance > 1.0:
                strength *= 0.9
        
        # Penalty for fallback usage
        for result in rag_results:
            if isinstance(result, dict) and result.get('fallback', False):
                strength *= 0.5
                break
        
        return np.clip(strength, 0.0, 1.0)
    
    def _chip_signal_strength(self, chip_activations: List[Dict]) -> float:
        """Calculate chip signal strength with meaningful variation"""
        if not chip_activations:
            return 0.0
        
        strength = 1.0
        
        # Penalty for low activation count
        if len(chip_activations) < 2:
            strength *= 0.7
        elif len(chip_activations) < 4:
            strength *= 0.85
        
        # Penalty for low similarity scores
        similarities = []
        for chip in chip_activations:
            if isinstance(chip, dict) and 'score' in chip:
                similarities.append(chip['score'])
        
        if similarities:
            avg_similarity = np.mean(similarities)
            # Chip scores are typically 0-1 for cosine similarity
            if avg_similarity < 0.3:
                strength *= 0.5
            elif avg_similarity < 0.5:
                strength *= 0.7
            elif avg_similarity < 0.7:
                strength *= 0.85
        
        # Penalty for threshold-just-made-it activations
        for chip in chip_activations:
            if isinstance(chip, dict) and chip.get('score', 1.0) < 0.2:
                strength *= 0.8
                break
        
        return np.clip(strength, 0.0, 1.0)
    
    def _fallback_result(self, reason: str) -> Dict[str, Any]:
        """Generate fallback result for error cases"""
        return {
            "convergence_score": 0.5,  # Neutral fallback
            "raw_convergence": 0.5,
            "signal_weight": 0.5,
            "convergence_signals": [],
            "signal_strength": {"rag": 0.5, "chips": 0.5},
            "details": {
                "fallback_reason": reason,
                "rag_chunks": 0,
                "chips_activated": 0,
                "calculation_time_ms": 0.0
            }
        }

# Global instance for reuse
_arbiter_instance = None

def get_coherence_arbiter(timeout_ms: int = 100) -> CoherenceArbiter:
    """Get or create coherence arbiter instance"""
    global _arbiter_instance
    if _arbiter_instance is None or _arbiter_instance.timeout_ms != timeout_ms:
        _arbiter_instance = CoherenceArbiter(timeout_ms)
    return _arbiter_instance

def measure_convergence(rag_results: List[Dict], chip_activations: List[Dict], 
                        query_embedding: Optional[np.ndarray] = None, 
                        timeout_ms: int = 100) -> Dict[str, Any]:
    """
    Convenience function for measuring convergence
    
    Args:
        rag_results: RAG retrieval results
        chip_activations: ML chip activations
        query_embedding: Optional query embedding
        timeout_ms: Maximum calculation time in milliseconds
        
    Returns:
        Coherence measurement metadata
    """
    arbiter = get_coherence_arbiter(timeout_ms)
    return arbiter.measure_convergence(rag_results, chip_activations, query_embedding)

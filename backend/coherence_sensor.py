#!/usr/bin/env python3
"""
Coherence Sensor v0.1 - Harmony-AI Bridge Implementation
Based on: harmony_ai_bridge_v1.0.0.md

This module implements the Output-Coherence Sensor concept:
- Monitors generated responses for internal consistency
- Detects contradiction, drift, and hallucination markers
- Returns coherence metrics for potential attention rebalancing

Harmony Parallel: Plantar/palmar mechanoreception
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class CoherenceReport:
    """Output of coherence analysis"""
    score: float  # 0.0 (incoherent) to 1.0 (fully coherent)
    contradictions: List[str]
    drift_detected: bool
    hallucination_risk: float  # 0.0 to 1.0
    confidence_without_grounding: bool
    recommendations: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "coherence_score": round(self.score, 3),
            "contradictions": self.contradictions,
            "drift_detected": self.drift_detected,
            "hallucination_risk": round(self.hallucination_risk, 3),
            "confidence_without_grounding": self.confidence_without_grounding,
            "recommendations": self.recommendations
        }


class CoherenceSensor:
    """
    Output-Coherence Sensor
    
    Monitors generated tokens/text for:
    - Logical continuity
    - Internal contradiction
    - Topic drift
    - Style consistency
    - Hallucination markers
    """
    
    # Contradiction patterns (says X then says not-X)
    CONTRADICTION_MARKERS = [
        (r"I don't have.*information", r"(?:As I recall|I remember|We've discussed)"),
        (r"I'm not sure", r"(?:definitely|certainly|absolutely)"),
        (r"(?:cannot|can't) access", r"(?:found|retrieved|located)"),
    ]
    
    # Hallucination risk markers (confident claims without grounding)
    HALLUCINATION_MARKERS = [
        r"As (?:I recall|you mentioned|we discussed)(?! in our)",  # False memory claims
        r"(?:definitely|certainly|absolutely) (?:is|are|was|were)",  # Overconfident
        r"studies (?:show|prove|demonstrate)",  # Uncited studies
        r"research (?:indicates|suggests|confirms)",  # Uncited research
        r"experts (?:agree|say|believe)",  # Uncited experts
    ]
    
    # Grounding indicators (evidence of RAG/retrieval support)
    GROUNDING_MARKERS = [
        r"according to",
        r"from the document",
        r"the (?:file|text|source) (?:says|states|mentions)",
        r"based on (?:your|the) (?:documents?|files?|notes?)",
        r"I found in",
    ]
    
    # Uncertainty markers (appropriate epistemic humility)
    UNCERTAINTY_MARKERS = [
        r"I'm not (?:sure|certain)",
        r"(?:may|might|could) be",
        r"(?:appears|seems) to",
        r"I don't have (?:specific|detailed|direct)",
        r"I (?:can't|cannot) verify",
    ]
    
    def __init__(self, sensitivity: float = 0.5):
        """
        Initialize sensor with sensitivity level.
        
        Args:
            sensitivity: 0.0 (lenient) to 1.0 (strict)
        """
        self.sensitivity = sensitivity
    
    def analyze(
        self, 
        query: str, 
        response: str, 
        rag_context: str = None,
        rag_used: bool = False
    ) -> CoherenceReport:
        """
        Analyze response coherence.
        
        Args:
            query: Original user query
            response: Generated response text
            rag_context: RAG-retrieved context (if any)
            rag_used: Whether RAG was used for this response
            
        Returns:
            CoherenceReport with analysis results
        """
        contradictions = self._detect_contradictions(response)
        drift = self._detect_drift(query, response)
        hallucination_risk, confidence_ungrounded = self._assess_hallucination_risk(
            response, rag_context, rag_used
        )
        
        # Calculate overall coherence score
        score = self._calculate_score(
            contradictions, drift, hallucination_risk, confidence_ungrounded
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            score, contradictions, drift, hallucination_risk, confidence_ungrounded
        )
        
        return CoherenceReport(
            score=score,
            contradictions=contradictions,
            drift_detected=drift,
            hallucination_risk=hallucination_risk,
            confidence_without_grounding=confidence_ungrounded,
            recommendations=recommendations
        )
    
    def _detect_contradictions(self, response: str) -> List[str]:
        """Detect internal contradictions in response."""
        contradictions = []
        response_lower = response.lower()
        
        for pattern_a, pattern_b in self.CONTRADICTION_MARKERS:
            match_a = re.search(pattern_a, response_lower, re.IGNORECASE)
            match_b = re.search(pattern_b, response_lower, re.IGNORECASE)
            
            if match_a and match_b:
                contradictions.append(
                    f"Potential contradiction: '{match_a.group()}' vs '{match_b.group()}'"
                )
        
        return contradictions
    
    def _detect_drift(self, query: str, response: str) -> bool:
        """Detect topic drift from original query."""
        # Extract key terms from query (simple approach)
        query_terms = set(re.findall(r'\b\w{4,}\b', query.lower()))
        response_terms = set(re.findall(r'\b\w{4,}\b', response.lower()))
        
        if not query_terms:
            return False
        
        # Calculate overlap
        overlap = len(query_terms & response_terms) / len(query_terms)
        
        # Drift detected if less than 30% of query terms appear in response
        # (adjusted by sensitivity)
        threshold = 0.3 * (1 + self.sensitivity)
        return overlap < threshold
    
    def _assess_hallucination_risk(
        self, 
        response: str, 
        rag_context: str,
        rag_used: bool
    ) -> Tuple[float, bool]:
        """
        Assess hallucination risk.
        
        Returns:
            Tuple of (risk_score, confidence_without_grounding)
        """
        hallucination_count = 0
        grounding_count = 0
        uncertainty_count = 0
        
        # Count markers
        for pattern in self.HALLUCINATION_MARKERS:
            hallucination_count += len(re.findall(pattern, response, re.IGNORECASE))
        
        for pattern in self.GROUNDING_MARKERS:
            grounding_count += len(re.findall(pattern, response, re.IGNORECASE))
        
        for pattern in self.UNCERTAINTY_MARKERS:
            uncertainty_count += len(re.findall(pattern, response, re.IGNORECASE))
        
        # Calculate risk
        # Higher risk if: many hallucination markers, few grounding markers, no RAG
        base_risk = min(1.0, hallucination_count * 0.2)
        
        # Reduce risk if grounded
        if grounding_count > 0:
            base_risk *= 0.5
        
        # Reduce risk if appropriately uncertain
        if uncertainty_count > 0:
            base_risk *= 0.7
        
        # Increase risk if no RAG but making confident claims
        confidence_ungrounded = (
            not rag_used and 
            hallucination_count > 0 and 
            grounding_count == 0
        )
        
        if confidence_ungrounded:
            base_risk = min(1.0, base_risk + 0.3)
        
        return base_risk, confidence_ungrounded
    
    def _calculate_score(
        self,
        contradictions: List[str],
        drift: bool,
        hallucination_risk: float,
        confidence_ungrounded: bool
    ) -> float:
        """Calculate overall coherence score."""
        score = 1.0
        
        # Deduct for contradictions
        score -= len(contradictions) * 0.2
        
        # Deduct for drift
        if drift:
            score -= 0.15
        
        # Deduct for hallucination risk
        score -= hallucination_risk * 0.3
        
        # Deduct for ungrounded confidence
        if confidence_ungrounded:
            score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    def _generate_recommendations(
        self,
        score: float,
        contradictions: List[str],
        drift: bool,
        hallucination_risk: float,
        confidence_ungrounded: bool
    ) -> List[str]:
        """Generate recommendations for improving response."""
        recommendations = []
        
        if score < 0.5:
            recommendations.append("PHASE_FLIP: Switch to consolidation mode")
        
        if contradictions:
            recommendations.append("REBALANCE: Increase attention to prior context")
        
        if drift:
            recommendations.append("REBALANCE: Re-anchor to original query terms")
        
        if hallucination_risk > 0.5:
            recommendations.append("GROUND: Increase RAG retrieval weight")
        
        if confidence_ungrounded:
            recommendations.append("CALIBRATE: Add uncertainty markers or retrieve supporting evidence")
        
        if not recommendations:
            recommendations.append("COHERENT: No intervention needed")
        
        return recommendations


# Singleton instance for easy import
sensor = CoherenceSensor(sensitivity=0.5)


def analyze_response(
    query: str, 
    response: str, 
    rag_context: str = None,
    rag_used: bool = False
) -> Dict:
    """
    Convenience function to analyze response coherence.
    
    Usage:
        from coherence_sensor import analyze_response
        report = analyze_response(query, response, rag_used=True)
    """
    report = sensor.analyze(query, response, rag_context, rag_used)
    return report.to_dict()


if __name__ == "__main__":
    # Test the sensor
    test_query = "What is the Harmony-AI mapping?"
    
    test_response_good = """
    The Harmony-AI mapping connects biomechanical principles to transformer architecture.
    Based on the documents, it proposes four mechanisms: Output-Coherence Sensor,
    Attention Rebalancer, Phase-Flip Controller, and Micro-Buoyancy Manager.
    These correspond to body systems that maintain stability under load.
    """
    
    test_response_bad = """
    I don't have information about Harmony-AI mapping. As I recall, we discussed this
    extensively last week! The research definitely proves that this is the most important
    framework. Experts agree that it will revolutionize AI. Studies show 95% improvement.
    """
    
    print("=" * 60)
    print("Testing GOOD response:")
    print("=" * 60)
    result = analyze_response(test_query, test_response_good, rag_used=True)
    for k, v in result.items():
        print(f"  {k}: {v}")
    
    print("\n" + "=" * 60)
    print("Testing BAD response:")
    print("=" * 60)
    result = analyze_response(test_query, test_response_bad, rag_used=False)
    for k, v in result.items():
        print(f"  {k}: {v}")

"""
FAITHH Phase 2 - Semantic Intent Detector
Uses semantic similarity to detect query intent beyond regex patterns.
"""

import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from sentence_transformers import SentenceTransformer
import json
import sys
import os

try:
    import torch
except ImportError:
    torch = None  # type: ignore

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from backend.intent_detection import detect_query_intent

class SemanticIntentDetector:
    """Semantic intent detection using embedding similarity"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.intent_embeddings = {}
        self.similarity_threshold = 0.7
        self.confidence_threshold = 0.6
        self.device = self._pick_device()
        self._load_model()
        self._precompute_intent_embeddings()

    @staticmethod
    def _pick_device() -> str:
        """Prefer CUDA with compute capability >= 7.0 (Volta+); else CPU (avoids sm_61 crashes)."""
        if torch is None or not torch.cuda.is_available():
            return "cpu"
        device = "cpu"
        try:
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                if props.major >= 7:
                    device = f"cuda:{i}"
                    break
        except Exception:
            return "cpu"
        return device
    
    def _load_model(self):
        """Load sentence transformer model"""
        try:
            print(f"📦 Loading semantic model: {self.model_name} (device={self.device})")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            print(f"✅ Model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            if self.device != "cpu":
                try:
                    print("⚠️ Retrying on CPU...")
                    self.device = "cpu"
                    self.model = SentenceTransformer(self.model_name, device="cpu")
                    print("✅ Model loaded on CPU")
                    return
                except Exception as e2:
                    print(f"❌ CPU fallback failed: {e2}")
            print("⚠️ Falling back to regex-only intent detection")
            self.model = None
    
    def _precompute_intent_embeddings(self):
        """Precompute embeddings for intent patterns"""
        if self.model is None:
            return
        
        # Define intent patterns with descriptions
        intent_patterns = {
            'alife_query': [
                "ALIFE experiment simulation agent evolution genome",
                "artificial life simulation with genetic algorithms",
                "evolutionary computation with adaptive agents",
                "wave interference patterns and beat frequencies",
                "harmonic dual-wave interference experiments",
                "agent shield activation and energy management"
            ],
            'self_query': [
                "information about FAITHH AI assistant capabilities",
                "what can FAITHH do for project management",
                "FAITHH's role in maintaining project coherence",
                "how does FAITHH help with multiple projects",
                "FAITHH's architecture and design principles"
            ],
            'why_question': [
                "rationale behind technical decisions and choices",
                "why was this particular approach selected",
                "reasoning for using specific technologies",
                "what alternatives were considered",
                "justification for architectural decisions"
            ],
            'next_action_query': [
                "what should I do next in this project",
                "what are the next steps to take",
                "where should I focus my efforts now",
                "what is the priority for this task",
                "how should I proceed with implementation"
            ],
            'project_query': [
                "current status of project development",
                "project phase and progress tracking",
                "what phase are we currently in",
                "project overview and current state",
                "project management and coordination"
            ],
            'constella_query': [
                "Constella framework principles and applications",
                "astris and auctor token concepts",
                "framework philosophy and core tenets",
                "Constella integration with FAITHH system",
                "framework components and usage patterns"
            ],
            'business_query': [
                "business revenue and client relationships",
                "LLC formation and financial management",
                "tomcat audio business operations",
                "client project tracking and billing",
                "business strategy and market analysis"
            ],
            'recent_changes_query': [
                "recent changes and updates to the system",
                "what has been modified recently",
                "latest commits and modifications",
                "recent development activity",
                "what's new in the codebase"
            ]
        }
        
        print("🧠 Computing intent embeddings...")
        
        for intent_type, patterns in intent_patterns.items():
            embeddings = self.model.encode(patterns)
            # Compute mean embedding for the intent type
            intent_embedding = np.mean(embeddings, axis=0)
            self.intent_embeddings[intent_type] = intent_embedding
            print(f"   {intent_type}: {len(patterns)} patterns embedded")
        
        print(f"✅ Precomputed embeddings for {len(self.intent_embeddings)} intent types")
    
    def detect_intent(self, query_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Detect intent using semantic similarity"""
        # First try traditional regex detection
        intent = detect_query_intent(query_text)
        
        # If high confidence in regex result, return it
        if self._is_high_confidence_regex(intent, query_text):
            return intent
        
        # Use semantic detection for ambiguous or low-confidence cases
        if self.model is None:
            return intent
        
        # Compute query embedding
        try:
            query_embedding = self.model.encode([query_text])
            query_embedding = query_embedding[0]
            
            # Calculate similarity with each intent type
            intent_scores = {}
            for intent_type, intent_embedding in self.intent_embeddings.items():
                similarity = self._cosine_similarity(query_embedding, intent_embedding)
                intent_scores[intent_type] = similarity
            
            # Find best matching intent
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            intent_type, similarity = best_intent
            
            # Check if similarity is above threshold
            if similarity >= self.similarity_threshold:
                # Update intent with semantic detection result
                intent[f'semantic_{intent_type}'] = True
                intent['semantic_confidence'] = similarity
                intent['detected_by'] = 'semantic'
                
                # Add semantic detection to patterns matched
                intent['patterns_matched'].append(f"semantic_{intent_type} (confidence: {similarity:.3f})")
                
                # Override low-confidence regex results
                for key in intent:
                    if key.startswith('is_') and intent[key]:
                        intent[key] = False
                
                print(f"🧠 Semantic intent detected: {intent_type} (confidence: {similarity:.3f})")
            
            return intent
            
        except Exception as e:
            print(f"❌ Error in semantic detection: {e}")
            return intent
    
    def detect_multi_intent(self, query_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Detect multiple intents in a single query"""
        # Start with semantic detection
        primary_intent = self.detect_intent(query_text, context)
        
        if self.model is None:
            return primary_intent
        
        try:
            query_embedding = self.model.encode([query_text])
            query_embedding = query_embedding[0]
            
            # Find all intents above threshold
            detected_intents = []
            intent_scores = {}
            
            for intent_type, intent_embedding in self.intent_embeddings.items():
                similarity = self._cosine_similarity(query_embedding, intent_embedding)
                if similarity >= self.similarity_threshold:
                    detected_intents.append((intent_type, similarity))
                    intent_scores[intent_type] = similarity
            
            if len(detected_intents) <= 1:
                # Single intent detected
                return primary_intent
            
            # Sort by similarity score
            detected_intents.sort(key=lambda x: x[1], reverse=True)
            
            # Create multi-intent result
            multi_intent = {
                'is_multi_intent': True,
                'primary_intent': detected_intents[0][0],
                'primary_confidence': detected_intents[0][1],
                'detected_intents': [],
                'detected_by': 'semantic',
                'patterns_matched': []
            }
            
            # Add all detected intents
            for intent_type, confidence in detected_intents:
                multi_intent['detected_intents'].append({
                    'intent_type': intent_type,
                    'confidence': confidence
                })
                multi_intent['patterns_matched'].append(f"semantic_{intent_type} (confidence: {confidence:.3f})")
            
            # Update primary intent flags
            for key in primary_intent:
                if key.startswith('is_'):
                    primary_intent[key] = False
            
            # Set primary intent
            primary_type = detected_intents[0][0]
            primary_intent[f'is_{primary_type}'] = True
            primary_intent['semantic_confidence'] = detected_intents[0][1]
            
            print(f"🧠 Multi-intent detected: {[intent['intent_type'] for intent in detected_intents]}")
            
            return multi_intent
            
        except Exception as e:
            print(f"❌ Error in multi-intent detection: {e}")
            return primary_intent
    
    def resolve_intent_conflict(self, detected_intents: List[Tuple[str, float]], 
                                context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Resolve conflicts when multiple intents are detected"""
        if not detected_intents:
            return {'is_multi_intent': False}
        
        # Sort by confidence score
        detected_intents.sort(key=lambda x: x[1], reverse=True)
        
        # Priority scoring for different intent types
        priority_scores = {
            'alife_query': 0.9,      # High priority - specific domain knowledge
            'self_query': 0.8,       # High priority - system self-awareness
            'why_question': 0.7,       # Medium-high - rationale important
            'next_action_query': 0.8,   # High priority - action guidance
            'project_query': 0.6,     # Medium - project management
            'constella_query': 0.5,   # Medium - framework knowledge
            'business_query': 0.4,     # Lower - business context
            'recent_changes_query': 0.3  # Low - recent activity
        }
        
        # Calculate weighted scores
        scored_intents = []
        for intent_type, confidence, score in detected_intents:
            priority = priority_scores.get(intent_type, 0.5)
            # Combine confidence and priority
            combined_score = (confidence * 0.6) + (priority * 0.4)
            scored_intents.append((intent_type, confidence, combined_score))
        
        # Sort by combined score
        scored_intents.sort(key=lambda x: x[2], reverse=True)
        
        # Create resolved intent
        resolved_intent = {
            'is_multi_intent': True,
            'primary_intent': scored_intents[0][0],
            'primary_confidence': scored_intents[0][1],
            'detected_intents': detected_intents,
            'resolved_by': 'priority_scoring',
            'patterns_matched': []
        }
        
        # Add patterns matched for resolved intents
        for intent_type, confidence, _ in scored_intents:
            resolved_intent['patterns_matched'].append(f"semantic_{intent_type} (confidence: {confidence:.3f})")
        
        # Set primary intent flags
        primary_type = scored_intents[0][0]
        resolved_intent[f'is_{primary_type}'] = True
        resolved_intent['semantic_confidence'] = scored_intents[0][1]
        
        # Add context-based resolution if available
        if context:
            context_resolution = self._resolve_with_context(scored_intents, context)
            if context_resolution:
                resolved_intent.update(context_resolution)
        
        print(f"🧠 Intent conflict resolved: {resolved_intent['primary_intent']} (priority: {scored_intents[0][2]:.3f})")
        
        return resolved_intent
    
    def _resolve_with_context(self, scored_intents: List[Tuple[str, float]], 
                               context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Resolve intent conflicts using conversation context"""
        # Look at recent conversation history for clues
        recent_queries = context.get('recent_queries', [])
        
        # Simple heuristic: if recent queries contain keywords for an intent, boost its priority
        context_boosts = {}
        
        for intent_type, confidence, score in scored_intents:
            boost = 0.0
            
            # Check recent queries for intent keywords
            for recent_query in recent_queries[-5:]:  # Last 5 queries
                query_lower = recent_query.lower()
                
                if intent_type == 'alife_query':
                    if any(keyword in query_lower for keyword in ['experiment', 'simulation', 'agent', 'genome']):
                        boost += 0.2
                elif intent_type == 'project_query':
                    if any(keyword in query_lower for keyword in ['project', 'phase', 'status', 'progress']):
                        boost += 0.2
                elif intent_type == 'why_question':
                    if any(keyword in query_lower for keyword in ['why', 'rationale', 'reasoning']):
                        boost += 0.2
            
            context_boosts[intent_type] = boost
        
        if context_boosts:
            # Adjust scores based on context
            adjusted_intents = []
            for intent_type, confidence, score in scored_intents:
                boost = context_boosts.get(intent_type, 0.0)
                adjusted_score = score + boost
                adjusted_intents.append((intent_type, confidence, adjusted_score))
            
            # Re-sort with context boosts
            adjusted_intents.sort(key=lambda x: x[2], reverse=True)
            
            return {'context_boosts': context_boosts}
        
        return None
    
    def _is_high_confidence_regex(self, intent: Dict[str, Any], query_text: str) -> bool:
        """Check if regex detection has high confidence"""
        # High confidence if multiple patterns matched
        pattern_count = len(intent.get('patterns_matched', []))
        
        # Also check for explicit intent indicators
        explicit_indicators = [
            'is_alife_query', 'is_self_query', 'is_why_question',
            'is_next_action_query', 'is_project_query'
        ]
        
        explicit_matches = sum(1 for key in explicit_indicators if intent.get(key, False))
        
        return pattern_count >= 2 or explicit_matches >= 1
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm_a = np.linalg.norm(vec1)
        norm_b = np.linalg.norm(vec2)
        return dot_product / (norm_a * norm_b)
    
    def get_intent_statistics(self) -> Dict[str, Any]:
        """Get statistics about intent detection performance"""
        return {
            'model_loaded': self.model is not None,
            'precomputed_intents': len(self.intent_embeddings),
            'similarity_threshold': self.similarity_threshold,
            'confidence_threshold': self.confidence_threshold,
            'supported_intents': list(self.intent_embeddings.keys()) if self.model else []
        }

# Global instance
semantic_intent_detector = SemanticIntentDetector()

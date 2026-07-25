#!/usr/bin/env python3
"""
FAITHH Quality Filter Module
Implements tiered storage for the auto-indexer based on knowledge graph rules.

This module filters incoming responses before indexing to reduce noise
and improve RAG retrieval quality.

Usage:
    from quality_filter import QualityFilter
    
    qf = QualityFilter()
    tier = qf.classify(response_text)
    # Returns: 'tier_1_index', 'tier_2_archive', 'tier_3_discard', or 'negative_example'
"""

import re
import hashlib
from typing import Literal, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

# Type alias for tier classification
TierType = Literal['tier_1_index', 'tier_2_archive', 'tier_3_discard', 'negative_example']


@dataclass
class FilterResult:
    """Result of quality filtering"""
    tier: TierType
    score: float
    reasons: list[str]
    metadata: Dict[str, Any]


class QualityFilter:
    """
    Classifies responses into storage tiers based on quality signals.
    
    Tiers:
        tier_1_index: High-value content, fully indexed in RAG (ChromaDB)
        tier_2_archive: Low-value but kept for audit trail (flat file)
        tier_3_discard: Noise, not stored
        negative_example: Failed approaches kept for learning
    """
    
    # Positive signals - increase likelihood of tier 1
    POSITIVE_KEYWORDS = [
        'decision', 'conclusion', 'solution', 'fixed', 'resolved',
        'implemented', 'created', 'built', 'designed', 'architecture',
        'because', 'therefore', 'the reason', 'this means',
        'step 1', 'step 2', 'first,', 'second,', 'finally,',
        'important', 'critical', 'key insight', 'learned',
        'tom cat sound', 'faithh', 'constella', 'floating garden',
        'chromadb', 'rag', 'embedding', 'indexing'
    ]
    
    # Negative signals - increase likelihood of tier 2/3
    NEGATIVE_KEYWORDS = [
        'okay', 'ok', 'sure', 'got it', 'thanks', 'thank you',
        'sounds good', 'perfect', 'great', 'yes', 'no',
        'i see', 'understood', 'will do', 'noted'
    ]
    
    # Failure indicators - route to negative examples
    FAILURE_KEYWORDS = [
        'failed', 'error', 'mistake', 'wrong', 'incorrect',
        'doesn\'t work', 'broken', 'bug', 'issue',
        'actually,', 'correction:', 'i was wrong', 'let me fix'
    ]
    
    # Project-specific terminology (boost for tier 1)
    PROJECT_TERMS = [
        'tom cat sound', 'floating garden', 'soundworks',
        'faithh', 'battle chip', 'pet terminal',
        'constella', 'governance', 'token',
        'celestial equilibrium', 'harmonic alignment',
        'scaffolding', 'knowledge graph'
    ]
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize filter with optional config override."""
        self.config = self._load_config(config_path)
        self.stats = {
            'tier_1_index': 0,
            'tier_2_archive': 0,
            'tier_3_discard': 0,
            'negative_example': 0
        }
    
    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Load configuration from knowledge graph YAML or use defaults."""
        default_config = {
            'min_words_tier1': 100,
            'max_words_tier3': 30,
            'code_block_boost': 0.3,
            'project_term_boost': 0.2,
            'positive_keyword_boost': 0.1,
            'negative_keyword_penalty': 0.15,
            'tier1_threshold': 0.5,
            'tier2_threshold': 0.2
        }
        
        if config_path and config_path.exists():
            try:
                import yaml
                with open(config_path) as f:
                    docs = list(yaml.safe_load_all(f))
                    for doc in docs:
                        if doc and 'indexing_rules' in doc:
                            # Extract thresholds from YAML if present
                            rules = doc['indexing_rules']
                            # Could customize config from YAML here
                            break
            except Exception as e:
                print(f"Warning: Could not load config from {config_path}: {e}")
        
        return default_config
    
    def classify(self, text: str, metadata: Optional[Dict] = None) -> FilterResult:
        """
        Classify a response into a storage tier.
        
        Args:
            text: The response text to classify
            metadata: Optional metadata (sender, timestamp, etc.)
            
        Returns:
            FilterResult with tier, score, reasons, and metadata
        """
        if metadata is None:
            metadata = {}
        
        reasons = []
        score = 0.5  # Start neutral
        
        # Basic checks
        text_lower = text.lower().strip()
        word_count = len(text.split())
        
        # Check for empty/minimal content
        if not text_lower or word_count < 3:
            return FilterResult(
                tier='tier_3_discard',
                score=0.0,
                reasons=['Empty or near-empty content'],
                metadata={'word_count': word_count, **metadata}
            )
        
        # Length scoring
        if word_count < self.config['max_words_tier3']:
            score -= 0.3
            reasons.append(f'Very short ({word_count} words)')
        elif word_count >= self.config['min_words_tier1']:
            score += 0.2
            reasons.append(f'Substantial length ({word_count} words)')
        
        # Code block detection
        code_blocks = len(re.findall(r'```[\s\S]*?```', text))
        if code_blocks > 0:
            score += self.config['code_block_boost']
            reasons.append(f'Contains {code_blocks} code block(s)')
        
        # Inline code detection
        inline_code = len(re.findall(r'`[^`]+`', text))
        if inline_code > 3:
            score += 0.1
            reasons.append(f'Contains {inline_code} inline code references')
        
        # Structured data detection (tables, lists, YAML)
        has_table = '|' in text and text.count('|') > 4
        has_list = bool(re.search(r'^[\s]*[-*]\s', text, re.MULTILINE))
        has_numbered = bool(re.search(r'^[\s]*\d+\.\s', text, re.MULTILINE))
        
        if has_table:
            score += 0.15
            reasons.append('Contains table')
        if has_list or has_numbered:
            score += 0.1
            reasons.append('Contains structured list')
        
        # Keyword analysis
        positive_matches = sum(1 for kw in self.POSITIVE_KEYWORDS if kw in text_lower)
        negative_matches = sum(1 for kw in self.NEGATIVE_KEYWORDS if kw in text_lower)
        project_matches = sum(1 for term in self.PROJECT_TERMS if term in text_lower)
        failure_matches = sum(1 for kw in self.FAILURE_KEYWORDS if kw in text_lower)
        
        if positive_matches > 0:
            boost = min(positive_matches * self.config['positive_keyword_boost'], 0.3)
            score += boost
            reasons.append(f'{positive_matches} positive keyword(s)')
        
        if negative_matches > 0:
            penalty = min(negative_matches * self.config['negative_keyword_penalty'], 0.3)
            score -= penalty
            reasons.append(f'{negative_matches} negative keyword(s)')
        
        if project_matches > 0:
            boost = min(project_matches * self.config['project_term_boost'], 0.4)
            score += boost
            reasons.append(f'{project_matches} project term(s)')
        
        # Check for failure/correction patterns
        if failure_matches > 0:
            # Check if this is a correction or learning moment
            if any(phrase in text_lower for phrase in ['let me fix', 'correction:', 'actually,']):
                return FilterResult(
                    tier='negative_example',
                    score=score,
                    reasons=['Contains correction/failure learning'],
                    metadata={
                        'word_count': word_count,
                        'failure_keywords': failure_matches,
                        **metadata
                    }
                )
        
        # Clamp score
        score = max(0.0, min(1.0, score))
        
        # Determine tier based on score
        if score >= self.config['tier1_threshold']:
            tier = 'tier_1_index'
        elif score >= self.config['tier2_threshold']:
            tier = 'tier_2_archive'
        else:
            tier = 'tier_3_discard'
        
        # Update stats
        self.stats[tier] += 1
        
        return FilterResult(
            tier=tier,
            score=score,
            reasons=reasons,
            metadata={
                'word_count': word_count,
                'code_blocks': code_blocks,
                'positive_keywords': positive_matches,
                'negative_keywords': negative_matches,
                'project_terms': project_matches,
                **metadata
            }
        )
    
    def get_stats(self) -> Dict[str, int]:
        """Return classification statistics."""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset classification statistics."""
        for key in self.stats:
            self.stats[key] = 0


class TieredStorage:
    """
    Manages storage across tiers.
    
    - Tier 1: ChromaDB (via existing indexer)
    - Tier 2: Flat file archive
    - Tier 3: Discarded (not stored)
    - Negative: Separate collection for learning
    """
    
    def __init__(self, 
                 archive_path: Path = None,
                 negative_path: Path = None,
                 chromadb_host: str = "localhost",
                 chromadb_port: int = 8000):
        """Initialize storage backends."""
        self.archive_path = archive_path or Path.home() / "ai-stack" / "data" / "tier2_archive.jsonl"
        self.negative_path = negative_path or Path.home() / "ai-stack" / "data" / "negative_examples.jsonl"
        
        # Ensure directories exist
        self.archive_path.parent.mkdir(parents=True, exist_ok=True)
        self.negative_path.parent.mkdir(parents=True, exist_ok=True)
        
        # ChromaDB connection (for tier 1)
        self.chromadb_host = chromadb_host
        self.chromadb_port = chromadb_port
        self._chromadb_client = None
        self._collection = None
    
    def _get_chromadb(self):
        """Lazy-load ChromaDB connection."""
        if self._chromadb_client is None:
            import chromadb
            self._chromadb_client = chromadb.HttpClient(
                host=self.chromadb_host, 
                port=self.chromadb_port
            )
            self._collection = self._chromadb_client.get_or_create_collection(
                name="documents_768"
            )
        return self._collection
    
    def store(self, text: str, filter_result: FilterResult, doc_id: str = None) -> bool:
        """
        Store content in appropriate tier.
        
        Args:
            text: Content to store
            filter_result: Classification result from QualityFilter
            doc_id: Optional document ID (generated if not provided)
            
        Returns:
            True if stored successfully, False otherwise
        """
        if doc_id is None:
            doc_id = hashlib.md5(text.encode()).hexdigest()[:16]
        
        timestamp = datetime.now().isoformat()
        
        if filter_result.tier == 'tier_1_index':
            return self._store_tier1(text, filter_result, doc_id, timestamp)
        elif filter_result.tier == 'tier_2_archive':
            return self._store_tier2(text, filter_result, doc_id, timestamp)
        elif filter_result.tier == 'negative_example':
            return self._store_negative(text, filter_result, doc_id, timestamp)
        else:  # tier_3_discard
            # Log but don't store
            return True
    
    def _store_tier1(self, text: str, result: FilterResult, doc_id: str, timestamp: str) -> bool:
        """Store in ChromaDB for RAG retrieval."""
        try:
            collection = self._get_chromadb()
            collection.add(
                documents=[text],
                ids=[f"auto_{doc_id}"],
                metadatas=[{
                    "source": "auto_indexer",
                    "tier": "tier_1",
                    "score": result.score,
                    "timestamp": timestamp,
                    **result.metadata
                }]
            )
            return True
        except Exception as e:
            print(f"Error storing to ChromaDB: {e}")
            return False
    
    def _store_tier2(self, text: str, result: FilterResult, doc_id: str, timestamp: str) -> bool:
        """Store in flat file archive."""
        try:
            record = {
                "id": doc_id,
                "timestamp": timestamp,
                "text": text,
                "score": result.score,
                "reasons": result.reasons,
                "metadata": result.metadata
            }
            with open(self.archive_path, 'a') as f:
                f.write(json.dumps(record) + '\n')
            return True
        except Exception as e:
            print(f"Error storing to archive: {e}")
            return False
    
    def _store_negative(self, text: str, result: FilterResult, doc_id: str, timestamp: str) -> bool:
        """Store in negative examples collection."""
        try:
            record = {
                "id": doc_id,
                "timestamp": timestamp,
                "text": text,
                "score": result.score,
                "reasons": result.reasons,
                "metadata": {**result.metadata, "type": "negative_example"}
            }
            with open(self.negative_path, 'a') as f:
                f.write(json.dumps(record) + '\n')
            return True
        except Exception as e:
            print(f"Error storing negative example: {e}")
            return False


# Convenience function for direct use
def filter_and_store(text: str, metadata: Dict = None) -> FilterResult:
    """
    One-shot filter and store function.
    
    Usage:
        from quality_filter import filter_and_store
        result = filter_and_store(response_text, {"source": "faithh_chat"})
    """
    qf = QualityFilter()
    storage = TieredStorage()
    
    result = qf.classify(text, metadata)
    storage.store(text, result)
    
    return result


# CLI for testing
if __name__ == "__main__":
    import sys
    
    print("=" * 70)
    print("FAITHH Quality Filter - Test Mode")
    print("=" * 70)
    
    qf = QualityFilter()
    
    # Test cases
    test_cases = [
        # Should be tier 1 (high value)
        ("Here's the solution: I implemented a new RAG pipeline using ChromaDB. "
         "The key insight was that we needed to chunk conversations by topic, "
         "not just by message. This fixed the retrieval accuracy issue we discussed. "
         "```python\ndef chunk_by_topic(messages):\n    # implementation\n    pass\n```",
         "tier_1_index"),
        
        # Should be tier 2 (archive)
        ("I see what you mean. That makes sense for the Tom Cat Sound project.",
         "tier_2_archive"),
        
        # Should be tier 3 (discard)
        ("Okay, sounds good!",
         "tier_3_discard"),
        
        # Should be negative example
        ("Actually, I was wrong about that. Let me fix the previous approach. "
         "The error was in the embedding dimension - it should be 768, not 384.",
         "negative_example"),
    ]
    
    print("\nRunning test cases...\n")
    
    for text, expected in test_cases:
        result = qf.classify(text)
        status = "✅" if result.tier == expected else "❌"
        print(f"{status} Expected: {expected}, Got: {result.tier}")
        print(f"   Score: {result.score:.2f}")
        print(f"   Reasons: {', '.join(result.reasons)}")
        print()
    
    print("Stats:", qf.get_stats())
    print()
    
    # Interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == "-i":
        print("\nInteractive mode - paste text and press Enter twice to classify:")
        print("(Type 'quit' to exit)\n")
        
        while True:
            lines = []
            while True:
                line = input()
                if line == "":
                    break
                if line.lower() == "quit":
                    sys.exit(0)
                lines.append(line)
            
            if lines:
                text = "\n".join(lines)
                result = qf.classify(text)
                print(f"\n→ Tier: {result.tier}")
                print(f"→ Score: {result.score:.2f}")
                print(f"→ Reasons: {', '.join(result.reasons)}")
                print()

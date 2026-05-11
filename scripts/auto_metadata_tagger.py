#!/usr/bin/env python3
"""
Automated Metadata Tagging Pipeline for FAITHH
Classifies documents and adds appropriate metadata automatically.
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import chromadb
from sentence_transformers import SentenceTransformer

class MetadataTagger:
    """Automated metadata classification and tagging system"""
    
    def __init__(self):
        self.client = chromadb.HttpClient(host="192.158.1.243", port=8000)
        self.collection = self.client.get_collection(name="faithh_knowledge_base")
        
        # Load sentence transformer for semantic classification
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Pre-defined classification patterns
        self.patterns = {
            'alife_experiment': {
                'keywords': ['experiment', 'simulation', 'agent', 'genome', 'evolution', 'alife'],
                'patterns': [r'exp\s*\d+', r'experiment\s*\d+', r'harmonic', r'interference', r'red queen'],
                'document_types': ['summary', 'bug_fix', 'design', 'analysis', 'progression', 'results']
            },
            'business': {
                'keywords': ['revenue', 'client', 'llc', 'tomcat', 'business', 'financial'],
                'patterns': [r'\bllc\b', r'\btomcat\b', r'\bfloating garden\b'],
                'document_types': ['financial', 'client', 'project', 'strategy']
            },
            'technical': {
                'keywords': ['code', 'implementation', 'backend', 'frontend', 'api', 'docker'],
                'patterns': [r'\.py$', r'\.js$', r'http://', r'api/', r'docker'],
                'document_types': ['implementation', 'documentation', 'configuration']
            },
            'decision': {
                'keywords': ['decision', 'choice', 'rationale', 'why', 'because', 'selected'],
                'patterns': [r'why\s+did\s+we', r'rationale', r'decision\s+made'],
                'document_types': ['decision', 'rationale', 'analysis']
            },
            'constella': {
                'keywords': ['constella', 'framework', 'astris', 'auctor', 'principles'],
                'patterns': [r'constella', r'framework', r'astris', r'auctor'],
                'document_types': ['framework', 'principles', 'guidelines']
            }
        }
        
        # Content level classification
        self.content_levels = {
            'high_level': ['summary', 'overview', 'status', 'progress', 'results'],
            'detailed': ['implementation', 'detailed', 'specific', 'technical', 'code'],
            'analysis': ['analysis', 'comparison', 'evaluation', 'assessment']
        }
    
    def classify_source_type(self, content: str, source: str = "") -> str:
        """Classify the source type of a document"""
        content_lower = content.lower()
        
        # Check ALIFE experiments first (most specific)
        if any(keyword in content_lower for keyword in self.patterns['alife_experiment']['keywords']):
            if any(re.search(pattern, content_lower) for pattern in self.patterns['alife_experiment']['patterns']):
                return 'alife_experiment'
        
        # Check other categories
        for source_type, patterns in self.patterns.items():
            if source_type == 'alife_experiment':
                continue
                
            keyword_match = any(keyword in content_lower for keyword in patterns['keywords'])
            pattern_match = any(re.search(pattern, content_lower) for pattern in patterns['patterns'])
            
            if keyword_match or pattern_match:
                return source_type
        
        return 'general'
    
    def classify_document_type(self, content: str, source_type: str) -> str:
        """Classify the specific document type within a source type"""
        content_lower = content.lower()
        
        if source_type in self.patterns:
            doc_types = self.patterns[source_type]['document_types']
            
            # Check for explicit document type indicators
            for doc_type in doc_types:
                if doc_type in content_lower:
                    return doc_type
            
            # Use semantic similarity for classification
            return self._semantic_document_type_classification(content, doc_types)
        
        return 'document'
    
    def _semantic_document_type_classification(self, content: str, doc_types: List[str]) -> str:
        """Use semantic similarity to classify document type"""
        try:
            # Create embeddings for content and document types
            content_embedding = self.embedder.encode([content])
            type_embeddings = self.embedder.encode(doc_types)
            
            # Calculate similarities
            similarities = []
            for i, type_embedding in enumerate(type_embeddings):
                similarity = self._cosine_similarity(content_embedding[0], type_embedding)
                similarities.append((doc_types[i], similarity))
            
            # Return the type with highest similarity
            best_match = max(similarities, key=lambda x: x[1])
            return best_match[0] if best_match[1] > 0.3 else 'document'
            
        except Exception as e:
            print(f"⚠️ Semantic classification failed: {e}")
            return 'document'
    
    def classify_content_level(self, content: str) -> str:
        """Classify the content level (high_level, detailed, analysis)"""
        content_lower = content.lower()
        
        for level, indicators in self.content_levels.items():
            if any(indicator in content_lower for indicator in indicators):
                return level
        
        # Default to detailed for technical content
        if any(word in content_lower for word in ['code', 'implementation', 'technical']):
            return 'detailed'
        
        return 'high_level'
    
    def extract_experiment_id(self, content: str) -> Optional[int]:
        """Extract experiment ID from ALIFE content"""
        # Look for patterns like "Experiment 4", "Exp 4", etc.
        patterns = [
            r'experiment\s*(\d+)',
            r'exp\s*(\d+)',
            r'experiment\s*#?(\d+)',
            r'phase\s*(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content.lower())
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    def generate_query_keywords(self, content: str, source_type: str, document_type: str) -> str:
        """Generate relevant query keywords for the document"""
        content_lower = content.lower()
        
        # Extract key terms based on source type
        if source_type == 'alife_experiment':
            keywords = []
            
            # Add experiment-specific keywords
            if 'harmonic' in content_lower:
                keywords.append('harmonic')
            if 'interference' in content_lower:
                keywords.append('interference')
            if 'bug' in content_lower or 'fix' in content_lower:
                keywords.extend(['bugs', 'fixes'])
            if 'status' in content_lower or 'results' in content_lower:
                keywords.extend(['status', 'results'])
            if 'design' in content_lower:
                keywords.append('design')
            if 'red_queen' in content_lower:
                keywords.append('red_queen')
            if 'dynamics' in content_lower:
                keywords.append('dynamics')
            
            # Add experiment ID if found
            exp_id = self.extract_experiment_id(content)
            if exp_id is not None:
                keywords.append(f'experiment_{exp_id}')
            
            return ','.join(keywords) if keywords else 'alife,experiment'
        
        elif source_type == 'business':
            keywords = []
            if 'revenue' in content_lower:
                keywords.append('revenue')
            if 'client' in content_lower:
                keywords.append('client')
            if 'financial' in content_lower:
                keywords.append('financial')
            return ','.join(keywords) if keywords else 'business'
        
        elif source_type == 'technical':
            keywords = []
            if 'api' in content_lower:
                keywords.append('api')
            if 'backend' in content_lower:
                keywords.append('backend')
            if 'frontend' in content_lower:
                keywords.append('frontend')
            return ','.join(keywords) if keywords else 'technical'
        
        return source_type
    
    def generate_metadata(self, content: str, source: str = "") -> Dict[str, any]:
        """Generate complete metadata for a document"""
        metadata = {
            'indexed_at': datetime.now().isoformat(),
            'auto_tagged': True
        }
        
        # Classify source type
        source_type = self.classify_source_type(content, source)
        metadata['source_type'] = source_type
        
        # Classify document type
        document_type = self.classify_document_type(content, source_type)
        metadata['document_type'] = document_type
        
        # Classify content level
        content_level = self.classify_content_level(content)
        metadata['content_level'] = content_level
        
        # Generate query keywords
        query_keywords = self.generate_query_keywords(content, source_type, document_type)
        metadata['query_keywords'] = query_keywords
        
        # Add source-specific metadata
        if source_type == 'alife_experiment':
            exp_id = self.extract_experiment_id(content)
            if exp_id is not None:
                metadata['experiment_id'] = exp_id
        
        # Add category based on source type
        if source_type == 'alife_experiment':
            metadata['category'] = 'alife_results'
        elif source_type == 'business':
            metadata['category'] = 'business'
        elif source_type == 'technical':
            metadata['category'] = 'technical'
        else:
            metadata['category'] = 'general'
        
        return metadata
    
    def _cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        import numpy as np
        dot_product = np.dot(vec1, vec2)
        norm_a = np.linalg.norm(vec1)
        norm_b = np.linalg.norm(vec2)
        return dot_product / (norm_a * norm_b)
    
    def validate_metadata(self, metadata: Dict[str, any]) -> Tuple[bool, List[str]]:
        """Validate metadata against schema requirements"""
        errors = []
        
        # Required fields
        required_fields = ['source_type', 'document_type', 'content_level', 'query_keywords']
        for field in required_fields:
            if field not in metadata:
                errors.append(f"Missing required field: {field}")
        
        # Field type validation
        if 'query_keywords' in metadata and not isinstance(metadata['query_keywords'], str):
            errors.append("query_keywords must be a string")
        
        if 'experiment_id' in metadata and not isinstance(metadata['experiment_id'], int):
            errors.append("experiment_id must be an integer")
        
        # Value validation
        valid_source_types = list(self.patterns.keys()) + ['general']
        if 'source_type' in metadata and metadata['source_type'] not in valid_source_types:
            errors.append(f"Invalid source_type: {metadata['source_type']}")
        
        valid_content_levels = ['high_level', 'detailed', 'analysis']
        if 'content_level' in metadata and metadata['content_level'] not in valid_content_levels:
            errors.append(f"Invalid content_level: {metadata['content_level']}")
        
        return len(errors) == 0, errors
    
    def tag_document(self, content: str, source: str = "", doc_id: str = None) -> Dict[str, any]:
        """Tag a single document with metadata"""
        print(f"🏷️ Auto-tagging document: {doc_id or 'unknown'}")
        
        # Generate metadata
        metadata = self.generate_metadata(content, source)
        
        # Validate metadata
        is_valid, errors = self.validate_metadata(metadata)
        if not is_valid:
            print(f"⚠️ Metadata validation errors: {errors}")
            # Add validation errors to metadata for debugging
            metadata['validation_errors'] = errors
        
        print(f"   Source type: {metadata.get('source_type')}")
        print(f"   Document type: {metadata.get('document_type')}")
        print(f"   Content level: {metadata.get('content_level')}")
        print(f"   Keywords: {metadata.get('query_keywords')}")
        
        return metadata

def main():
    """Test the auto metadata tagger"""
    tagger = MetadataTagger()
    
    # Test with ALIFE content
    alife_content = """
    Experiment 4: Harmonic Interference — Results Summary
    
    Scientific question: Does spatial cognitive stratification emerge when agents face
    overlapping wave sources with different frequencies? Can agents evolve to track
    beat frequencies in the interference zone?
    
    Outcome: RED_QUEEN_CONTINUES (Outcome #4 of 4 valid outcomes).
    Key finding: Beat-genome agents dominated at tick 1000 but neither strategy
    achieves permanent dominance.
    """
    
    metadata = tagger.tag_document(alife_content, "docs/research/EXP4_RESULTS.md", "test_doc_1")
    print(f"\nGenerated metadata: {json.dumps(metadata, indent=2)}")

if __name__ == "__main__":
    main()

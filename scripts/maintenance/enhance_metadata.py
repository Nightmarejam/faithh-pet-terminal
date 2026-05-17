#!/usr/bin/env python3
"""
Metadata Enhancement Pipeline
Enhances existing ChromaDB documents with domain classification, timestamps, and quality metrics
"""

import sys
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections import Counter
import random

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import chromadb
from dotenv import load_dotenv
import os

load_dotenv()

CHROMA_URL = os.getenv("CHROMA_URL", "http://192.158.1.10:8000")
COLLECTION_NAME = "faithh_knowledge_base"
BATCH_SIZE = 100

# Domain classification keywords
DOMAIN_KEYWORDS = {
    'alife': ['alife', 'artificial life', 'experiment', 'simulation', 'agents', 'evolution', 'predator', 'prey', 'population', 'tick', 'wave', 'interference'],
    'technology': ['python', 'code', 'programming', 'api', 'backend', 'frontend', 'docker', 'server', 'database', 'chromadb', 'gpu', 'cuda'],
    'music': ['music', 'audio', 'sound', 'tom cat', 'mixing', 'mastering', 'production', 'frequency', 'waveform', 'acoustic'],
    'law': ['legal', 'law', 'court', 'case', 'statute', 'regulation', 'jurisdiction', 'contract', 'copyright', 'patent'],
    'finance': ['tax', 'financial', 'income', 'expense', 'business', 'llc', 'revenue', 'profit', 'cost', 'budget'],
    'healthcare': ['health', 'medical', 'clinical', 'patient', 'treatment', 'diagnosis', 'therapy', 'medicine'],
    'science': ['research', 'study', 'experiment', 'data', 'analysis', 'hypothesis', 'method', 'results', 'conclusion'],
    'education': ['learning', 'teaching', 'course', 'tutorial', 'student', 'knowledge', 'curriculum', 'lesson'],
    'business': ['strategy', 'management', 'operations', 'marketing', 'sales', 'customer', 'market', 'product'],
    'history': ['historical', 'past', 'ancient', 'timeline', 'chronology', 'era', 'period', 'century'],
    'environment': ['climate', 'environment', 'sustainability', 'green', 'eco', 'nature', 'conservation', 'energy'],
    'social_sciences': ['psychology', 'sociology', 'anthropology', 'behavior', 'culture', 'society', 'community']
}

class MetadataEnhancer:
    def __init__(self):
        self.client = chromadb.HttpClient(host=CHROMA_URL.replace("http://", "").split(":")[0],
                                         port=int(CHROMA_URL.split(":")[-1]))
        self.collection = self.client.get_collection(COLLECTION_NAME)
        self.total_docs = self.collection.count()
        self.processed = 0
        self.enhanced = 0
        
    def classify_domain(self, document):
        """Classify document domain based on content keywords"""
        doc_lower = document.lower()
        domain_scores = {}
        
        for domain, keywords in DOMAIN_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword in doc_lower:
                    score += doc_lower.count(keyword)
            domain_scores[domain] = score
        
        # Return domain with highest score, or 'other' if no matches
        if domain_scores:
            best_domain = max(domain_scores, key=domain_scores.get)
            if domain_scores[best_domain] > 0:
                return best_domain, domain_scores[best_domain]
        
        return 'other', 0
    
    def estimate_created_at(self, metadata):
        """Estimate creation date from existing metadata"""
        # Check for existing timestamp fields
        for field in ['timestamp', 'migrated_at', 'updated_at']:
            if field in metadata:
                try:
                    if isinstance(metadata[field], str):
                        # Parse ISO format, ensure timezone-aware
                        dt = datetime.fromisoformat(metadata[field].replace('Z', '+00:00'))
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        return dt
                    elif isinstance(metadata[field], (int, float)):
                        # Assume Unix timestamp
                        return datetime.fromtimestamp(metadata[field], timezone.utc)
                except:
                    pass
        
        # Check date_month and date_year
        if 'date_year' in metadata and 'date_month' in metadata:
            try:
                year = int(metadata['date_year'])
                month = int(metadata['date_month'].split('-')[1]) if '-' in metadata['date_month'] else 1
                return datetime(year, month, 1, tzinfo=timezone.utc)
            except:
                pass
        
        # Default to recent date with some randomness
        days_ago = random.randint(30, 365)
        return datetime.now(timezone.utc) - timedelta(days=days_ago)
    
    def calculate_quality_score(self, document, metadata):
        """Calculate quality score based on various factors"""
        score = 0.5  # Base score
        
        # Length factor (prefer substantial content)
        doc_length = len(document)
        if 100 <= doc_length <= 5000:
            score += 0.2
        elif doc_length > 5000:
            score += 0.1
        
        # Structure factor (has paragraphs, lists)
        if '\n\n' in document:  # Multiple paragraphs
            score += 0.1
        if any(marker in document for marker in ['-', '*', '1.', '2.']):  # Lists
            score += 0.1
        
        # Source type factor
        source_type = metadata.get('source_type', '').lower()
        if source_type in ['technical_explanation', 'project_discussion']:
            score += 0.2
        elif source_type in ['document_content', 'json_data']:
            score += 0.1
        
        # Existing quality score if present
        if 'quality_score' in metadata:
            try:
                existing_score = float(metadata['quality_score'])
                score = (score + existing_score) / 2  # Average with existing
            except:
                pass
        
        return min(1.0, max(0.0, score))
    
    def enhance_document(self, doc_id, document, metadata):
        """Enhance a single document's metadata"""
        if not metadata:
            metadata = {}
        
        enhanced = metadata.copy()
        
        # Add domain classification
        if 'domain' not in enhanced:
            domain, confidence = self.classify_domain(document)
            enhanced['domain'] = domain
            enhanced['domain_confidence'] = confidence
        
        # Add created_at timestamp
        if 'created_at' not in enhanced:
            created_at = self.estimate_created_at(metadata)
            enhanced['created_at'] = created_at.isoformat()
            enhanced['data_freshness_days'] = (datetime.now(timezone.utc) - created_at).days
        
        # Add/enhance quality score
        quality_score = self.calculate_quality_score(document, metadata)
        enhanced['quality_score'] = quality_score
        
        # Add content metrics
        enhanced['word_count'] = len(document.split())
        enhanced['character_count'] = len(document)
        
        # Add enhancement tracking
        enhanced['enhanced_at'] = datetime.now(timezone.utc).isoformat()
        enhanced['enhancement_version'] = '1.0'
        
        return enhanced
    
    def process_batch(self, offset=0):
        """Process a batch of documents"""
        try:
            # Get batch of documents
            results = self.collection.get(
                limit=BATCH_SIZE,
                offset=offset,
                include=['documents', 'metadatas']
            )
            
            if not results['ids']:
                return False  # No more documents
            
            enhancements = []
            for i, (doc_id, document, metadata) in enumerate(zip(results['ids'], results['documents'], results['metadatas'])):
                self.processed += 1
                
                # Check if enhancement needed
                needs_enhancement = (
                    not metadata or 
                    'domain' not in metadata or 
                    'created_at' not in metadata or
                    'quality_score' not in metadata
                )
                
                if needs_enhancement:
                    enhanced_metadata = self.enhance_document(doc_id, document, metadata or {})
                    enhancements.append((doc_id, enhanced_metadata))
                    self.enhanced += 1
                
                # Progress indicator
                if self.processed % 10 == 0:
                    progress = (self.processed / self.total_docs) * 100
                    print(f"  Progress: {self.processed}/{self.total_docs} ({progress:.1f}%) - Enhanced: {self.enhanced}")
            
            # Apply enhancements
            if enhancements:
                ids = [item[0] for item in enhancements]
                metadatas = [item[1] for item in enhancements]
                
                self.collection.update(
                    ids=ids,
                    metadatas=metadatas
                )
                
                print(f"  ✅ Enhanced {len(enhancements)} documents in batch")
            
            return True  # Continue processing
            
        except Exception as e:
            print(f"  ❌ Error processing batch: {e}")
            return False
    
    def run_enhancement(self):
        """Run the full enhancement process"""
        print(f"=== Metadata Enhancement Pipeline ===")
        print(f"Collection: {COLLECTION_NAME}")
        print(f"Total documents: {self.total_docs}")
        print(f"Batch size: {BATCH_SIZE}")
        print()
        
        offset = 0
        while self.process_batch(offset):
            offset += BATCH_SIZE
        
        print()
        print("=== Enhancement Complete ===")
        print(f"Documents processed: {self.processed}")
        print(f"Documents enhanced: {self.enhanced}")
        if self.processed > 0:
            print(f"Enhancement rate: {(self.enhanced/self.processed)*100:.1f}%")
        else:
            print("Enhancement rate: N/A (no documents processed)")
        
        # Save enhancement report
        report = {
            "total_documents": self.total_docs,
            "processed": self.processed,
            "enhanced": self.enhanced,
            "enhancement_rate": self.enhanced/self.processed if self.processed > 0 else 0,
            "enhanced_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        with open("logs/metadata_enhancement_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"Report saved to logs/metadata_enhancement_report.json")

if __name__ == "__main__":
    enhancer = MetadataEnhancer()
    enhancer.run_enhancement()

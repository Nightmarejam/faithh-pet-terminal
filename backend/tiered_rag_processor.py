#!/usr/bin/env python3
"""
Tiered RAG Processor for FAITHH Backend
Implements dynamic three-tier storage with access pattern tracking
"""

import chromadb
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import os

class TieredRAGProcessor:
    """Three-tier RAG system with dynamic data classification"""
    
    def __init__(self):
        # Tier configurations
        self.tiers = {
            1: {
                'name': 'tier1_hot_768',
                'max_docs': 50000,  # 20GB ~50k docs
                'location': 'local',
                'client': None,
                'collection': None
            },
            2: {
                'name': 'tier2_warm_768', 
                'max_docs': 500000,  # 500GB ~500k docs
                'location': 'gen8',
                'client': None,
                'collection': None
            },
            3: {
                'name': 'tier3_archive_768',
                'max_docs': -1,  # Unlimited
                'location': 'nas',
                'client': None,
                'collection': None
            }
        }
        
        # Access tracking
        self.access_patterns = {}
        self.last_access = {}
        self.access_frequency = {}
        
        # Initialize connections
        self._initialize_connections()
        
    def _initialize_connections(self):
        """Initialize connections to all tiers"""
        
        # Tier 1: Local hot cache
        try:
            self.tiers[1]['client'] = chromadb.PersistentClient(path="./chroma_db/tier1")
            self.tiers[1]['collection'] = self.tiers[1]['client'].get_or_create_collection(
                name=self.tiers[1]['name']
            )
            print(f"✅ Tier 1 (hot cache) initialized: {self.tiers[1]['collection'].count()} docs")
        except Exception as e:
            print(f"⚠️ Tier 1 initialization failed: {e}")
            
        # Tier 2: Gen8 warm storage
        try:
            self.tiers[2]['client'] = chromadb.HttpClient(host='100.79.85.32', port=8000)
            # Use existing collection for now, create separate later
            self.tiers[2]['collection'] = self.tiers[2]['client'].get_collection('faithh_knowledge_base')
            print(f"✅ Tier 2 (warm storage) initialized: {self.tiers[2]['collection'].count()} docs")
        except Exception as e:
            print(f"⚠️ Tier 2 initialization failed: {e}")
            
        # Tier 3: NAS archive (placeholder for now)
        print("ℹ️ Tier 3 (archive) - NAS integration planned")
        
    def record_access(self, doc_id: str, tier: int):
        """Record document access for pattern tracking"""
        now = time.time()
        
        self.last_access[doc_id] = now
        self.access_frequency[doc_id] = self.access_frequency.get(doc_id, 0) + 1
        
        # Store tier information
        if 'tiers' not in self.access_patterns[doc_id]:
            self.access_patterns[doc_id] = {'tiers': [], 'frequency': 0}
        self.access_patterns[doc_id]['tiers'].append((now, tier))
        self.access_patterns[doc_id]['frequency'] = self.access_frequency[doc_id]['frequency'] + 1
        
    def should_promote(self, doc_id: str, current_tier: int) -> bool:
        """Determine if document should be promoted to higher tier"""
        
        if current_tier == 3:  # Archive to warm
            recent_accesses = self._count_recent_accesses(doc_id, days=30)
            return recent_accesses > 5
        elif current_tier == 2:  # Warm to hot
            recent_accesses = self._count_recent_accesses(doc_id, days=7)
            return recent_accesses > 10
            
        return False
        
    def should_demote(self, doc_id: str, current_tier: int) -> bool:
        """Determine if document should be demoted to lower tier"""
        
        if current_tier == 1:  # Hot to warm
            recent_accesses = self._count_recent_accesses(doc_id, days=7)
            return recent_accesses < 2
        elif current_tier == 2:  # Warm to archive
            recent_accesses = self._count_recent_accesses(doc_id, days=90)
            return recent_accesses == 0
            
        return False
        
    def _count_recent_accesses(self, doc_id: str, days: int) -> int:
        """Count accesses in recent days"""
        if doc_id not in self.access_patterns:
            return 0
            
        cutoff = time.time() - (days * 24 * 3600)
        count = 0
        
        for access_time, tier in self.access_patterns[doc_id]['tiers']:
            if access_time > cutoff:
                count += 1
                
        return count
        
    def route_document(self, doc_metadata: Dict) -> int:
        """Route new document to appropriate tier based on metadata"""
        
        base_score = 0
        
        # Source priority scoring
        source = doc_metadata.get('source', 'unknown')
        if source == 'chat':
            base_score += 3
        elif source == 'alife':
            base_score += 2
        elif source == 'gov_api':
            base_score += 1
        elif source == 'manual':
            base_score += 2
            
        # Recency scoring
        created_at = doc_metadata.get('created_at', datetime.now().isoformat())
        if isinstance(created_at, str):
            try:
                created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                age_days = (datetime.now() - created_dt.replace(tzinfo=None)).days
                
                if age_days < 1:
                    base_score += 3
                elif age_days < 7:
                    base_score += 2
                elif age_days < 30:
                    base_score += 1
            except:
                pass
                
        # Size consideration (smaller docs get priority)
        size = doc_metadata.get('size', 0)
        if size < 1000:  # <1KB
            base_score += 1
            
        # Route based on score
        if base_score >= 6:
            return 1  # Hot cache
        elif base_score >= 3:
            return 2  # Warm storage
        else:
            return 3  # Archive
            
    def query(self, query_text: str, n_results: int = 5) -> List[Dict]:
        """Smart tiered query with automatic cache promotion"""
        
        results = []
        
        # Tier 1: Check hot cache first
        if self.tiers[1]['collection']:
            try:
                tier1_results = self.tiers[1]['collection'].query(
                    query_texts=[query_text],
                    n_results=n_results
                )
                
                for i, (doc, meta, dist) in enumerate(zip(
                    tier1_results['documents'][0],
                    tier1_results['metadatas'][0] if tier1_results.get('metadatas') else [{}] * len(tier1_results['documents'][0]),
                    tier1_results['distances'][0]
                )):
                    doc_id = meta.get('id', f'tier1_doc_{i}')
                    self.record_access(doc_id, 1)
                    results.append({
                        'document': doc,
                        'metadata': meta,
                        'distance': dist,
                        'tier': 1,
                        'id': doc_id
                    })
            except Exception as e:
                print(f"Tier 1 query error: {e}")
                
        # If we have enough results from Tier 1, return them
        if len(results) >= n_results:
            return results[:n_results]
            
        # Tier 2: Query warm storage for additional results
        remaining = n_results - len(results)
        if self.tiers[2]['collection']:
            try:
                tier2_results = self.tiers[2]['collection'].query(
                    query_texts=[query_text],
                    n_results=remaining * 2  # Get extras for promotion
                )
                
                for i, (doc, meta, dist) in enumerate(zip(
                    tier2_results['documents'][0],
                    tier2_results['metadatas'][0] if tier2_results.get('metadatas') else [{}] * len(tier2_results['documents'][0]),
                    tier2_results['distances'][0]
                )):
                    doc_id = meta.get('id', f'tier2_doc_{i}')
                    self.record_access(doc_id, 2)
                    
                    # Check if should promote to Tier 1
                    if self.should_promote(doc_id, 2) and len(results) < n_results:
                        self._promote_to_tier1(doc, meta, doc_id)
                    
                    results.append({
                        'document': doc,
                        'metadata': meta,
                        'distance': dist,
                        'tier': 2,
                        'id': doc_id
                    })
            except Exception as e:
                print(f"Tier 2 query error: {e}")
                
        # Return top N results
        return results[:n_results]
        
    def _promote_to_tier1(self, document: str, metadata: Dict, doc_id: str):
        """Promote frequently accessed document to hot cache"""
        
        if not self.tiers[1]['collection']:
            return
            
        try:
            # Check if Tier 1 is full
            if self.tiers[1]['collection'].count() >= self.tiers[1]['max_docs']:
                self._evict_from_tier1()
                
            # Add to Tier 1 with updated metadata
            updated_metadata = metadata.copy()
            updated_metadata['tier'] = 1
            updated_metadata['promoted_at'] = datetime.now().isoformat()
            updated_metadata['promotion_source'] = 'tier2'
            
            self.tiers[1]['collection'].add(
                documents=[document],
                metadatas=[updated_metadata],
                ids=[f"promoted_{doc_id}"]
            )
            
            print(f"📈 Promoted {doc_id} to Tier 1")
            
        except Exception as e:
            print(f"Promotion error: {e}")
            
    def _evict_from_tier1(self):
        """Remove least recently used document from Tier 1"""
        
        if not self.tiers[1]['collection']:
            return
            
        try:
            # Get documents with access times
            docs = self.tiers[1]['collection'].get(
                limit=1,
                where={"tier": 1}
            )
            
            if docs['ids']:
                evict_id = docs['ids'][0]
                self.tiers[1]['collection'].delete(ids=[evict_id])
                print(f"📉 Evicted {evict_id} from Tier 1")
                
        except Exception as e:
            print(f"Eviction error: {e}")
            
    def get_stats(self) -> Dict:
        """Get statistics about tier usage"""
        
        stats = {
            'tiers': {},
            'total_documents': 0,
            'access_patterns': len(self.access_patterns)
        }
        
        for tier_num, tier_config in self.tiers.items():
            if tier_config['collection']:
                count = tier_config['collection'].count()
                stats['tiers'][tier_num] = {
                    'name': tier_config['name'],
                    'count': count,
                    'max_docs': tier_config['max_docs'],
                    'utilization': count / tier_config['max_docs'] if tier_config['max_docs'] > 0 else 0
                }
                stats['total_documents'] += count
                
        return stats

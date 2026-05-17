#!/usr/bin/env python3
"""
Bulk Metadata Update Tool for FAITHH
Updates existing documents with proper metadata schema.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any
import chromadb
import sys
import os
sys.path.append(os.path.dirname(__file__))
from auto_metadata_tagger import MetadataTagger
from metadata_validator import MetadataValidator

class BulkMetadataUpdater:
    """Bulk updates metadata for existing documents"""
    
    def __init__(self):
        self.client = chromadb.HttpClient(host="192.158.1.10", port=8000)
        self.collection = self.client.get_collection(name="faithh_knowledge_base")
        
        self.tagger = MetadataTagger()
        self.validator = MetadataValidator()
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'updated': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
    
    def update_document_metadata(self, doc_id: str, document: str, existing_metadata: Dict[str, Any]) -> bool:
        """Update metadata for a single document"""
        try:
            # Skip if already properly tagged
            if existing_metadata.get('auto_tagged') and self._has_required_metadata(existing_metadata):
                print(f"⏭️ Skipping {doc_id}: already properly tagged")
                self.stats['skipped'] += 1
                return True
            
            # Generate new metadata
            new_metadata = self.tagger.generate_metadata(document)
            
            # Preserve some existing fields
            preserved_fields = ['source', 'original_category', 'session_id']
            for field in preserved_fields:
                if field in existing_metadata:
                    new_metadata[field] = existing_metadata[field]
            
            # Mark as auto-tagged
            new_metadata['auto_tagged'] = True
            new_metadata['updated_at'] = datetime.now().isoformat()
            
            # Validate new metadata
            is_valid, errors = self.validator.validate_metadata(new_metadata, doc_id)
            if not is_valid:
                print(f"⚠️ Validation errors for {doc_id}: {errors}")
                # Try to fix issues
                new_metadata = self.validator.fix_metadata_issues(doc_id, new_metadata)
                is_valid, errors = self.validator.validate_metadata(new_metadata, doc_id)
                if not is_valid:
                    print(f"❌ Cannot fix {doc_id}: {errors}")
                    self.stats['failed'] += 1
                    self.stats['errors'].append(f"{doc_id}: {errors}")
                    return False
            
            # Update the document
            self.collection.update(
                ids=[doc_id],
                metadatas=[new_metadata]
            )
            
            print(f"✅ Updated {doc_id}")
            print(f"   Source type: {new_metadata.get('source_type')}")
            print(f"   Document type: {new_metadata.get('document_type')}")
            
            self.stats['updated'] += 1
            return True
            
        except Exception as e:
            print(f"❌ Failed to update {doc_id}: {e}")
            self.stats['failed'] += 1
            self.stats['errors'].append(f"{doc_id}: {str(e)}")
            return False
    
    def _has_required_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Check if metadata has all required fields"""
        required_fields = ['source_type', 'document_type', 'content_level', 'query_keywords']
        return all(field in metadata for field in required_fields)
    
    def update_batch(self, limit: int = 100, batch_size: int = 10) -> Dict[str, Any]:
        """Update metadata for a batch of documents"""
        print(f"🔄 Starting bulk metadata update (limit: {limit}, batch size: {batch_size})")
        
        try:
            # Get documents to update
            results = self.collection.get(limit=limit, include=['metadatas', 'documents'])
            
            if not results['ids']:
                print("⚠️ No documents found")
                return self.stats
            
            print(f"📊 Found {len(results['ids'])} documents to process")
            
            # Process in batches
            for i in range(0, len(results['ids']), batch_size):
                batch_end = min(i + batch_size, len(results['ids']))
                batch_ids = results['ids'][i:batch_end]
                batch_docs = results['documents'][i:batch_end]
                batch_metas = results['metadatas'][i:batch_end]
                
                print(f"\n📦 Processing batch {i//batch_size + 1}/{(len(results['ids']) + batch_size - 1)//batch_size}")
                
                for j, doc_id in enumerate(batch_ids):
                    self.stats['total_processed'] += 1
                    
                    document = batch_docs[j] if j < len(batch_docs) else ""
                    existing_metadata = batch_metas[j] if j < len(batch_metas) else {}
                    
                    # Truncate very long documents for processing
                    if len(document) > 10000:
                        document = document[:10000] + "..."
                    
                    success = self.update_document_metadata(doc_id, document, existing_metadata)
                    
                    # Small delay to avoid overwhelming ChromaDB
                    time.sleep(0.1)
                
                # Brief pause between batches
                if batch_end < len(results['ids']):
                    time.sleep(1)
            
            self.print_summary()
            return self.stats
            
        except Exception as e:
            print(f"❌ Bulk update failed: {e}")
            self.stats['errors'].append(f"Bulk update: {str(e)}")
            return self.stats
    
    def update_by_source_type(self, source_type: str, limit: int = 50) -> Dict[str, Any]:
        """Update documents by specific source type"""
        print(f"🎯 Updating documents with source_type: {source_type}")
        
        try:
            # Query for documents with specific source type or category
            results = self.collection.query(
                query_texts=[source_type],
                n_results=limit,
                where={"$or": [
                    {"source_type": source_type},
                    {"category": source_type}
                ]}
            )
            
            if not results['ids'][0]:
                print(f"⚠️ No documents found for source_type: {source_type}")
                return self.stats
            
            print(f"📊 Found {len(results['ids'][0])} documents for {source_type}")
            
            # Process each document
            for i, doc_id in enumerate(results['ids'][0]):
                self.stats['total_processed'] += 1
                
                # Get full document
                full_results = self.collection.get(ids=[doc_id], include=['metadatas', 'documents'])
                
                if full_results['ids']:
                    document = full_results['documents'][0] if full_results['documents'] else ""
                    existing_metadata = full_results['metadatas'][0] if full_results['metadatas'] else {}
                    
                    success = self.update_document_metadata(doc_id, document, existing_metadata)
                    
                    if i % 10 == 0:
                        print(f"Processed {i+1}/{len(results['ids'][0])} documents")
            
            self.print_summary()
            return self.stats
            
        except Exception as e:
            print(f"❌ Source type update failed: {e}")
            self.stats['errors'].append(f"Source type update: {str(e)}")
            return self.stats
    
    def fix_conversation_metadata(self) -> Dict[str, Any]:
        """Fix metadata for conversation documents specifically"""
        print(f"💬 Fixing conversation document metadata")
        
        try:
            # Get conversation documents
            results = self.collection.query(
                query_texts=["conversation"],
                n_results=100,
                where={"category": "live_chat"}
            )
            
            if not results['ids'][0]:
                print("⚠️ No conversation documents found")
                return self.stats
            
            print(f"📊 Found {len(results['ids'][0])} conversation documents")
            
            # Process each conversation document
            for i, doc_id in enumerate(results['ids'][0]):
                self.stats['total_processed'] += 1
                
                # Get full document
                full_results = self.collection.get(ids=[doc_id], include=['metadatas', 'documents'])
                
                if full_results['ids']:
                    document = full_results['documents'][0] if full_results['documents'] else ""
                    existing_metadata = full_results['metadatas'][0] if full_results['metadatas'] else {}
                    
                    # Special handling for conversations
                    new_metadata = existing_metadata.copy()
                    new_metadata.update({
                        'source_type': 'conversation',
                        'document_type': 'chat_log',
                        'content_level': 'detailed',
                        'query_keywords': 'conversation,chat,discussion',
                        'category': 'conversation',
                        'auto_tagged': True,
                        'updated_at': datetime.now().isoformat()
                    })
                    
                    # Update the document
                    self.collection.update(
                        ids=[doc_id],
                        metadatas=[new_metadata]
                    )
                    
                    print(f"✅ Fixed conversation {doc_id}")
                    self.stats['updated'] += 1
            
            self.print_summary()
            return self.stats
            
        except Exception as e:
            print(f"❌ Conversation fix failed: {e}")
            self.stats['errors'].append(f"Conversation fix: {str(e)}")
            return self.stats
    
    def print_summary(self):
        """Print update summary"""
        print(f"\n📊 Bulk Update Summary:")
        print(f"   Total processed: {self.stats['total_processed']}")
        print(f"   Updated: {self.stats['updated']}")
        print(f"   Failed: {self.stats['failed']}")
        print(f"   Skipped: {self.stats['skipped']}")
        
        if self.stats['errors']:
            print(f"\n❌ Errors ({len(self.stats['errors'])}):")
            for error in self.stats['errors'][:5]:  # Show first 5 errors
                print(f"   - {error}")
        
        if self.stats['total_processed'] > 0:
            success_rate = (self.stats['updated'] / self.stats['total_processed']) * 100
            print(f"\n✅ Success rate: {success_rate:.1f}%")

def main():
    """Run bulk metadata update"""
    updater = BulkMetadataUpdater()
    
    print("🚀 FAITHH Bulk Metadata Update Tool")
    print("=" * 50)
    
    # First fix conversation documents
    print("\n1️⃣ Fixing conversation documents...")
    updater.fix_conversation_metadata()
    
    # Reset stats for other updates
    updater.stats = {
        'total_processed': 0,
        'updated': 0,
        'failed': 0,
        'skipped': 0,
        'errors': []
    }
    
    # Update other documents
    print("\n2️⃣ Updating other documents...")
    updater.update_batch(limit=50, batch_size=5)

if __name__ == "__main__":
    main()

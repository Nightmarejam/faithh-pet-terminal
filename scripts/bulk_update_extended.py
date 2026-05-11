#!/usr/bin/env python3
"""
Extended Bulk Metadata Update for Phase 1 Completion
Processes larger batches to achieve 80% auto-tagging coverage.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import chromadb
import sys
import os
sys.path.append(os.path.dirname(__file__))
from bulk_metadata_update import BulkMetadataUpdater

class ExtendedBulkUpdater(BulkMetadataUpdater):
    """Extended bulk updater with larger batch capabilities"""
    
    def __init__(self):
        super().__init__()
        self.extended_stats = {
            'start_time': datetime.now(),
            'batches_processed': 0,
            'documents_per_batch': 0,
            'processing_rate': 0,
            'estimated_completion': None
        }
    
    def update_large_batch(self, target_docs: int = 10000, batch_size: int = 1000) -> Dict[str, Any]:
        """Update a large batch of documents with progress tracking"""
        print(f"🚀 Starting extended bulk update (target: {target_docs:,} docs, batch size: {batch_size})")
        
        try:
            # Get total document count
            total_results = self.collection.get(limit=1, include=['metadatas'])
            
            # Estimate total documents (ChromaDB doesn't provide count directly)
            # We'll query in chunks and count
            print("📊 Counting total documents...")
            total_docs = self._count_total_documents()
            
            if total_docs == 0:
                print("⚠️ No documents found")
                return self.stats
            
            print(f"📊 Total documents in collection: {total_docs:,}")
            
            # Calculate how many to process (avoid already processed)
            processed_docs = self.stats['total_processed']
            remaining_to_process = min(target_docs, total_docs - processed_docs)
            
            if remaining_to_process <= 0:
                print("✅ All target documents already processed")
                return self.stats
            
            print(f"📋 Processing {remaining_to_process:,} documents ({processed_docs:,} already processed)")
            
            # Process in large batches using query with where clause to skip processed docs
            processed_in_session = 0
            
            # Get documents that haven't been auto-tagged
            print("📊 Finding documents that need metadata updates...")
            
            # Use a simple approach - get documents and filter
            all_results = self.collection.get(
                limit=remaining_to_process + 1000,  # Get extra to account for already processed
                include=['metadatas', 'documents']
            )
            
            if not all_results['ids']:
                print("⚠️ No documents found")
                return self.stats
            
            # Filter out already processed documents
            unprocessed_docs = []
            for i, doc_id in enumerate(all_results['ids']):
                metadata = all_results['metadatas'][i] if i < len(all_results['metadatas']) else {}
                
                # Skip if already auto-tagged and has required metadata
                if metadata.get('auto_tagged') and self._has_required_metadata(metadata):
                    continue
                
                unprocessed_docs.append({
                    'id': doc_id,
                    'document': all_results['documents'][i] if i < len(all_results['documents']) else "",
                    'metadata': metadata
                })
                
                if len(unprocessed_docs) >= remaining_to_process:
                    break
            
            print(f"📋 Found {len(unprocessed_docs)} documents to process")
            
            # Process in batches
            for batch_start in range(0, len(unprocessed_docs), batch_size):
                batch_end = min(batch_start + batch_size, len(unprocessed_docs))
                batch = unprocessed_docs[batch_start:batch_end]
                
                print(f"\n📦 Processing batch {self.extended_stats['batches_processed'] + 1}")
                print(f"   Documents: {batch_start:,} - {batch_end:,}")
                
                # Process batch
                batch_start_time = time.time()
                
                for doc_data in batch:
                    doc_id = doc_data['id']
                    document = doc_data['document']
                    existing_metadata = doc_data['metadata']
                    
                    self.stats['total_processed'] += 1
                    processed_in_session += 1
                    
                    # Truncate very long documents
                    if len(document) > 5000:
                        document = document[:5000] + "..."
                    
                    success = self.update_document_metadata(doc_id, document, existing_metadata)
                    
                    # Progress indicator
                    if processed_in_session % 100 == 0:
                        elapsed = time.time() - batch_start_time
                        rate = processed_in_session / elapsed if elapsed > 0 else 0
                        print(f"   Processed {processed_in_session:,} documents ({rate:.1f} docs/sec)")
                
                # Update batch statistics
                batch_time = time.time() - batch_start_time
                self.extended_stats['batches_processed'] += 1
                self.extended_stats['documents_per_batch'] = len(batch)
                
                if batch_time > 0:
                    self.extended_stats['processing_rate'] = len(batch) / batch_time
                
                # Calculate estimated completion
                remaining_docs = remaining_to_process - processed_in_session
                if self.extended_stats['processing_rate'] > 0:
                    estimated_seconds = remaining_docs / self.extended_stats['processing_rate']
                    self.extended_stats['estimated_completion'] = datetime.now() + timedelta(seconds=estimated_seconds)
                
                # Brief pause between batches
                if batch_end < len(unprocessed_docs):
                    print(f"   ⏱️ Batch completed in {batch_time:.1f}s, pausing...")
                    time.sleep(2)
            
            self.print_extended_summary()
            return self.stats
            
        except Exception as e:
            print(f"❌ Extended bulk update failed: {e}")
            self.stats['errors'].append(f"Extended update: {str(e)}")
            return self.stats
    
    def _count_total_documents(self) -> int:
        """Count total documents in collection"""
        try:
            # Use query to get all documents (empty query returns all)
            results = self.collection.query(
                query_texts=[""],
                n_results=1,
                include=['metadatas']
            )
            
            if results['ids'] and results['ids'][0]:
                return len(results['ids'][0])
            else:
                return 0
            
        except Exception as e:
            print(f"⚠️ Error counting documents: {e}")
            return 0
    
    def print_extended_summary(self):
        """Print extended summary with performance metrics"""
        elapsed = datetime.now() - self.extended_stats['start_time']
        
        print(f"\n📊 Extended Bulk Update Summary:")
        print(f"   Total processed: {self.stats['total_processed']:,}")
        print(f"   Updated: {self.stats['updated']:,}")
        print(f"   Failed: {self.stats['failed']:,}")
        print(f"   Skipped: {self.stats['skipped']:,}")
        print(f"   Batches processed: {self.extended_stats['batches_processed']}")
        
        if self.extended_stats['processing_rate'] > 0:
            print(f"   Processing rate: {self.extended_stats['processing_rate']:.1f} docs/sec")
        
        print(f"   Total time: {elapsed}")
        
        if self.extended_stats['estimated_completion']:
            print(f"   Estimated completion: {self.extended_stats['estimated_completion'].strftime('%Y-%m-%d %H:%M')}")
        
        if self.stats['errors']:
            print(f"\n❌ Errors ({len(self.stats['errors'])}):")
            for error in self.stats['errors'][:3]:
                print(f"   - {error}")
        
        if self.stats['total_processed'] > 0:
            success_rate = (self.stats['updated'] / self.stats['total_processed']) * 100
            print(f"\n✅ Success rate: {success_rate:.1f}%")

def main():
    """Run extended bulk metadata update"""
    updater = ExtendedBulkUpdater()
    
    print("🚀 FAITHH Extended Bulk Metadata Update")
    print("=" * 50)
    
    # Process 10,000 documents to significantly improve coverage
    updater.update_large_batch(target_docs=10000, batch_size=1000)

if __name__ == "__main__":
    main()

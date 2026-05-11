#!/usr/bin/env python3
"""
Index Metadata Automation Documentation into ChromaDB
Makes the documentation available for FAITHH queries.
"""

import chromadb
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(__file__))
from auto_metadata_tagger import MetadataTagger

def index_metadata_documentation():
    """Index the metadata automation system documentation"""
    
    # Connect to ChromaDB
    client = chromadb.HttpClient(host="192.158.1.243", port=8000)
    collection = client.get_collection(name="faithh_knowledge_base")
    
    # Read the documentation
    doc_path = "/home/jonat/ai-stack/docs/reference/METADATA_AUTOMATION_SYSTEM.md"
    
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📖 Read documentation: {len(content)} characters")
        
        # Generate metadata for the documentation
        tagger = MetadataTagger()
        metadata = tagger.generate_metadata(content, doc_path)
        
        # Override some fields for documentation
        metadata.update({
            'source_type': 'technical',
            'document_type': 'documentation',
            'content_level': 'high_level',
            'category': 'system_documentation',
            'auto_tagged': True,
            'indexed_at': datetime.now().isoformat(),
            'doc_version': '1.0',
            'implementation_date': '2026-03-26'
        })
        
        # Create document ID
        doc_id = "metadata_automation_system_docs"
        
        # Check if document already exists
        try:
            existing = collection.get(ids=[doc_id], include=['metadatas'])
            if existing['ids']:
                print(f"🔄 Updating existing documentation: {doc_id}")
                collection.update(
                    ids=[doc_id],
                    documents=[content],
                    metadatas=[metadata]
                )
            else:
                print(f"📝 Adding new documentation: {doc_id}")
                collection.add(
                    ids=[doc_id],
                    documents=[content],
                    metadatas=[metadata]
                )
        except Exception as e:
            print(f"⚠️ Check failed, adding as new: {e}")
            collection.add(
                ids=[doc_id],
                documents=[content],
                metadatas=[metadata]
            )
        
        print(f"✅ Successfully indexed metadata automation documentation")
        print(f"   Source type: {metadata['source_type']}")
        print(f"   Document type: {metadata['document_type']}")
        print(f"   Content level: {metadata['content_level']}")
        print(f"   Keywords: {metadata['query_keywords']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to index documentation: {e}")
        return False

def create_phase1_summary():
    """Create and index a Phase 1 summary document"""
    
    summary_content = """
FAITHH Enhancement Roadmap - Phase 1 Completion Status

Implementation Date: March 26, 2026
Status: In Progress - Core Components Complete

Phase 1 Objectives:
✅ Automated Metadata Tagging Pipeline - COMPLETE
✅ Enhanced Query Routing - COMPLETE  
✅ Metadata Validation System - COMPLETE
✅ Bulk Update Capability - COMPLETE
✅ Monitoring Dashboard - COMPLETE
⏳ Knowledge Base Integration - IN PROGRESS
⏳ Full Bulk Update - PENDING
⏳ Schema Compliance Improvement - PENDING

Key Achievements:
- Successfully resolved semantic search "power steering" issue
- ALIFE queries now correctly retrieve Experiment 4 data
- Model properly uses RAG context with citations
- 145 documents updated with proper metadata (100% success rate)
- Real-time monitoring dashboard operational

Current Metrics:
- Overall Health Score: 48.8% (Target: 80%)
- Auto-tagging Coverage: 25% (Target: 80%)
- Schema Compliance: 23.6% (Target: 95%)
- Documents Updated: 145 of ~36,000 (4% coverage)

Next Steps:
1. Complete knowledge base integration
2. Run bulk update on all remaining documents
3. Improve schema compliance to 95%
4. Establish automated monitoring with alerts
5. Validate Phase 1 completion metrics

Impact:
- Query accuracy significantly improved for ALIFE queries
- System now routes queries to correct document types
- Foundation established for Phase 2 intelligence features
- Metadata automation eliminates manual entry requirements
"""
    
    try:
        # Connect to ChromaDB
        client = chromadb.HttpClient(host="192.158.1.243", port=8000)
        collection = client.get_collection(name="faithh_knowledge_base")
        
        # Generate metadata
        tagger = MetadataTagger()
        metadata = tagger.generate_metadata(summary_content)
        
        # Override for project summary
        metadata.update({
            'source_type': 'project_state',
            'document_type': 'progression',
            'content_level': 'high_level',
            'category': 'project_docs',
            'auto_tagged': True,
            'indexed_at': datetime.now().isoformat(),
            'phase': '1',
            'status': 'in_progress'
        })
        
        doc_id = "phase1_completion_status"
        
        # Add or update
        try:
            existing = collection.get(ids=[doc_id], include=['metadatas'])
            if existing['ids']:
                collection.update(ids=[doc_id], documents=[summary_content], metadatas=[metadata])
                print(f"🔄 Updated Phase 1 summary")
            else:
                collection.add(ids=[doc_id], documents=[summary_content], metadatas=[metadata])
                print(f"📝 Added Phase 1 summary")
        except:
            collection.add(ids=[doc_id], documents=[summary_content], metadatas=[metadata])
            print(f"📝 Added Phase 1 summary")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create Phase 1 summary: {e}")
        return False

def main():
    """Main execution function"""
    print("🚀 Indexing Metadata Automation Documentation")
    print("=" * 50)
    
    # Index main documentation
    success1 = index_metadata_documentation()
    
    # Create Phase 1 summary
    success2 = create_phase1_summary()
    
    if success1 and success2:
        print("\n✅ Documentation indexing completed successfully")
        print("FAITHH can now provide informed responses about the metadata automation system")
    else:
        print("\n⚠️ Some indexing operations failed")

if __name__ == "__main__":
    main()

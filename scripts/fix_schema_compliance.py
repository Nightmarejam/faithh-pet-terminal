#!/usr/bin/env python3
"""
Fix Schema Compliance Issues
Addresses the validation errors to reach 95% compliance target.
"""

import chromadb
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(__file__))
from metadata_validator import MetadataValidator

class SchemaComplianceFixer:
    """Fixes schema compliance issues in existing documents"""
    
    def __init__(self):
        self.client = chromadb.HttpClient(host="servicebox.taileb8c60.ts.net", port=8000)
        self.collection = self.client.get_collection(name="faithh_knowledge_base")
        self.validator = MetadataValidator()
        
        # Legacy value mappings
        self.legacy_mappings = {
            'source_type': {
                'project_discussion': 'business',
                'technical_explanation': 'technical', 
                'json_data': 'technical',
                'document_content': 'general',
                'unknown': 'general',
                'conversation': 'conversation'
            },
            'category': {
                'project_docs': 'business',
                'live_chat': 'conversation',
                'general': 'general'
            }
        }
        
        self.stats = {
            'total_processed': 0,
            'fixed': 0,
            'failed': 0,
            'errors': []
        }
    
    def fix_document_schema(self, doc_id: str, document: str, metadata: dict) -> bool:
        """Fix schema compliance issues for a single document"""
        try:
            fixed_metadata = metadata.copy()
            fixes_applied = []
            
            # Fix missing required fields
            required_fields = ['source_type', 'document_type', 'content_level', 'query_keywords']
            for field in required_fields:
                if field not in fixed_metadata:
                    if field == 'source_type':
                        fixed_metadata[field] = self._infer_source_type(document)
                    elif field == 'document_type':
                        fixed_metadata[field] = 'document'
                    elif field == 'content_level':
                        fixed_metadata[field] = self._infer_content_level(document)
                    elif field == 'query_keywords':
                        fixed_metadata[field] = fixed_metadata.get('source_type', 'general')
                    
                    fixes_applied.append(f"Added {field}")
            
            # Fix legacy source_type values
            if fixed_metadata.get('source_type') in self.legacy_mappings['source_type']:
                old_value = fixed_metadata['source_type']
                new_value = self.legacy_mappings['source_type'][old_value]
                fixed_metadata['source_type'] = new_value
                fixes_applied.append(f"Mapped source_type: {old_value} → {new_value}")
            
            # Fix legacy category values
            if fixed_metadata.get('category') in self.legacy_mappings['category']:
                old_value = fixed_metadata['category']
                new_value = self.legacy_mappings['category'][old_value]
                fixed_metadata['category'] = new_value
                fixes_applied.append(f"Mapped category: {old_value} → {new_value}")
            
            # Fix category based on source_type
            if 'category' not in fixed_metadata and 'source_type' in fixed_metadata:
                source_type = fixed_metadata['source_type']
                category_map = {
                    'alife_experiment': 'alife_results',
                    'business': 'business',
                    'technical': 'technical',
                    'decision': 'general',
                    'constella': 'general',
                    'conversation': 'conversation',
                    'general': 'general'
                }
                fixed_metadata['category'] = category_map.get(source_type, 'general')
                fixes_applied.append(f"Set category from source_type")
            
            # Add timestamps
            if 'indexed_at' not in fixed_metadata:
                fixed_metadata['indexed_at'] = datetime.now().isoformat()
                fixes_applied.append("Added indexed_at")
            
            if 'updated_at' not in fixed_metadata:
                fixed_metadata['updated_at'] = datetime.now().isoformat()
                fixes_applied.append("Added updated_at")
            
            # Mark as fixed
            fixed_metadata['schema_fixed'] = True
            fixed_metadata['schema_fix_date'] = datetime.now().isoformat()
            
            # Validate the fixed metadata
            is_valid, errors = self.validator.validate_metadata(fixed_metadata, doc_id)
            if not is_valid:
                print(f"   ⚠️ Still has validation errors: {errors}")
                self.stats['failed'] += 1
                return False
            
            # Update the document
            self.collection.update(
                ids=[doc_id],
                metadatas=[fixed_metadata]
            )
            
            if fixes_applied:
                print(f"   ✅ Fixed {doc_id}: {', '.join(fixes_applied[:3])}")
            else:
                print(f"   ✅ Already compliant: {doc_id}")
            
            self.stats['fixed'] += 1
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to fix {doc_id}: {e}")
            self.stats['failed'] += 1
            self.stats['errors'].append(f"{doc_id}: {str(e)}")
            return False
    
    def _infer_source_type(self, document: str) -> str:
        """Infer source type from document content"""
        content_lower = document.lower()
        
        # Check for ALIFE indicators
        if any(keyword in content_lower for keyword in ['experiment', 'simulation', 'agent', 'genome', 'alife']):
            return 'alife_experiment'
        
        # Check for business indicators
        if any(keyword in content_lower for keyword in ['revenue', 'client', 'llc', 'business', 'financial']):
            return 'business'
        
        # Check for technical indicators
        if any(keyword in content_lower for keyword in ['code', 'implementation', 'api', 'backend', 'frontend']):
            return 'technical'
        
        # Check for decision indicators
        if any(keyword in content_lower for keyword in ['decision', 'rationale', 'why', 'choice']):
            return 'decision'
        
        # Check for conversation indicators
        if any(keyword in content_lower for keyword in ['user:', 'assistant:', 'conversation', 'chat']):
            return 'conversation'
        
        return 'general'
    
    def _infer_content_level(self, document: str) -> str:
        """Infer content level from document content"""
        content_lower = document.lower()
        
        # Check for high-level indicators
        if any(keyword in content_lower for keyword in ['summary', 'overview', 'status', 'progress']):
            return 'high_level'
        
        # Check for detailed indicators
        if any(keyword in content_lower for keyword in ['implementation', 'detailed', 'specific', 'code']):
            return 'detailed'
        
        # Check for analysis indicators
        if any(keyword in content_lower for keyword in ['analysis', 'comparison', 'evaluation']):
            return 'analysis'
        
        return 'high_level'  # Default to high_level
    
    def fix_all_compliance_issues(self, limit: int = 200) -> dict:
        """Fix schema compliance issues for all documents"""
        print(f"🔧 Fixing schema compliance issues (limit: {limit})")
        
        try:
            # Get documents to check
            results = self.collection.get(limit=limit, include=['metadatas', 'documents'])
            
            if not results['ids']:
                print("⚠️ No documents found")
                return self.stats
            
            print(f"📊 Found {len(results['ids'])} documents to check")
            
            # Process each document
            for i, doc_id in enumerate(results['ids']):
                self.stats['total_processed'] += 1
                
                document = results['documents'][i] if i < len(results['documents']) else ""
                metadata = results['metadatas'][i] if i < len(results['metadatas']) else {}
                
                # Check if it needs fixing
                is_valid, errors = self.validator.validate_metadata(metadata, doc_id)
                
                if is_valid:
                    print(f"   ⏭️ Already compliant: {doc_id}")
                    self.stats['fixed'] += 1
                else:
                    print(f"🔧 Fixing: {doc_id}")
                    self.fix_document_schema(doc_id, document, metadata)
                
                # Progress indicator
                if (i + 1) % 20 == 0:
                    print(f"   Processed {i+1}/{len(results['ids'])} documents")
            
            self.print_summary()
            return self.stats
            
        except Exception as e:
            print(f"❌ Schema compliance fix failed: {e}")
            self.stats['errors'].append(f"Batch fix: {str(e)}")
            return self.stats
    
    def print_summary(self):
        """Print fix summary"""
        print(f"\n📊 Schema Compliance Fix Summary:")
        print(f"   Total processed: {self.stats['total_processed']}")
        print(f"   Fixed: {self.stats['fixed']}")
        print(f"   Failed: {self.stats['failed']}")
        
        if self.stats['errors']:
            print(f"\n❌ Errors ({len(self.stats['errors'])}):")
            for error in self.stats['errors'][:3]:
                print(f"   - {error}")
        
        if self.stats['total_processed'] > 0:
            success_rate = (self.stats['fixed'] / self.stats['total_processed']) * 100
            print(f"\n✅ Success rate: {success_rate:.1f}%")

def main():
    """Run schema compliance fixes"""
    fixer = SchemaComplianceFixer()
    
    print("🔧 FAITHH Schema Compliance Fixer")
    print("=" * 50)
    
    # Fix compliance issues
    fixer.fix_all_compliance_issues(limit=200)

if __name__ == "__main__":
    main()

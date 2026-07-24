#!/usr/bin/env python3
"""
Metadata Schema Validator for FAITHH
Ensures all documents comply with the metadata schema requirements.
"""

import json
import sys
from typing import Dict, List, Tuple, Any
from datetime import datetime
import chromadb

class MetadataValidator:
    """Validates metadata against schema requirements"""
    
    def __init__(self):
        self.client = chromadb.HttpClient(host="servicebox.taileb8c60.ts.net", port=8000)
        self.collection = self.client.get_collection(name="faithh_knowledge_base")
        
        # Schema definition
        self.schema = {
            'required_fields': {
                'all': ['source_type', 'document_type', 'content_level', 'query_keywords'],
                'alife_experiment': ['experiment_id'],
                'conditional': {
                    'source_type': {
                        'alife_experiment': ['experiment_id'],
                        'business': [],
                        'technical': [],
                        'decision': [],
                        'constella': [],
                        'general': []
                    }
                }
            },
            'field_types': {
                'source_type': str,
                'document_type': str,
                'content_level': str,
                'query_keywords': str,
                'experiment_id': int,
                'indexed_at': str,
                'category': str,
                'auto_tagged': bool
            },
            'allowed_values': {
                'source_type': ['alife_experiment', 'business', 'technical', 'decision', 'constella', 'general', 'conversation'],
                'document_type': [
                    'summary', 'bug_fix', 'design', 'analysis', 'progression', 'results',
                    'financial', 'client', 'project', 'strategy',
                    'implementation', 'documentation', 'configuration',
                    'decision', 'rationale',
                    'framework', 'principles', 'guidelines',
                    'document', 'chat_log'
                ],
                'content_level': ['high_level', 'detailed', 'analysis'],
                'category': ['alife_results', 'business', 'technical', 'general', 'conversation']
            }
        }
        
        # Validation statistics
        self.stats = {
            'total_documents': 0,
            'valid_documents': 0,
            'invalid_documents': 0,
            'errors': {}
        }
    
    def validate_field_types(self, metadata: Dict[str, Any]) -> List[str]:
        """Validate field types in metadata"""
        errors = []
        
        for field, expected_type in self.schema['field_types'].items():
            if field in metadata:
                value = metadata[field]
                if not isinstance(value, expected_type):
                    # Allow string to int conversion for experiment_id
                    if field == 'experiment_id' and isinstance(value, str):
                        try:
                            int(value)
                        except ValueError:
                            errors.append(f"Field '{field}' should be {expected_type.__name__}, got {type(value).__name__}")
                    else:
                        errors.append(f"Field '{field}' should be {expected_type.__name__}, got {type(value).__name__}")
        
        return errors
    
    def validate_allowed_values(self, metadata: Dict[str, Any]) -> List[str]:
        """Validate that fields use allowed values"""
        errors = []
        
        for field, allowed_values in self.schema['allowed_values'].items():
            if field in metadata and metadata[field] not in allowed_values:
                errors.append(f"Field '{field}' has invalid value '{metadata[field]}'. Allowed: {allowed_values}")
        
        return errors
    
    def validate_required_fields(self, metadata: Dict[str, Any]) -> List[str]:
        """Validate that all required fields are present"""
        errors = []
        
        # Check universally required fields
        for field in self.schema['required_fields']['all']:
            if field not in metadata:
                errors.append(f"Missing required field: {field}")
        
        # Check conditional required fields
        source_type = metadata.get('source_type')
        if source_type in self.schema['required_fields']['conditional']['source_type']:
            conditional_fields = self.schema['required_fields']['conditional']['source_type'][source_type]
            for field in conditional_fields:
                if field not in metadata:
                    errors.append(f"Missing required field for {source_type}: {field}")
        
        return errors
    
    def validate_query_keywords_format(self, metadata: Dict[str, Any]) -> List[str]:
        """Validate query keywords format"""
        errors = []
        
        if 'query_keywords' in metadata:
            keywords = metadata['query_keywords']
            if isinstance(keywords, str):
                # Check if keywords are comma-separated and not empty
                if not keywords.strip():
                    errors.append("query_keywords cannot be empty")
                elif ',' in keywords:
                    # Check for empty keywords between commas
                    parts = keywords.split(',')
                    if any(not part.strip() for part in parts):
                        errors.append("query_keywords contains empty values")
            else:
                errors.append("query_keywords must be a string")
        
        return errors
    
    def validate_timestamp_format(self, metadata: Dict[str, Any]) -> List[str]:
        """Validate timestamp format"""
        errors = []
        
        if 'indexed_at' in metadata:
            timestamp = metadata['indexed_at']
            try:
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                errors.append("indexed_at must be a valid ISO timestamp")
        
        return errors
    
    def validate_metadata(self, metadata: Dict[str, Any], doc_id: str = None) -> Tuple[bool, List[str]]:
        """Complete metadata validation"""
        all_errors = []
        
        # Run all validation checks
        all_errors.extend(self.validate_required_fields(metadata))
        all_errors.extend(self.validate_field_types(metadata))
        all_errors.extend(self.validate_allowed_values(metadata))
        all_errors.extend(self.validate_query_keywords_format(metadata))
        all_errors.extend(self.validate_timestamp_format(metadata))
        
        # Update statistics
        self.stats['total_documents'] += 1
        if all_errors:
            self.stats['invalid_documents'] += 1
            for error in all_errors:
                error_type = error.split(':')[0]
                self.stats['errors'][error_type] = self.stats['errors'].get(error_type, 0) + 1
        else:
            self.stats['valid_documents'] += 1
        
        return len(all_errors) == 0, all_errors
    
    def validate_collection(self, limit: int = 100) -> Dict[str, Any]:
        """Validate all documents in the collection"""
        print(f"🔍 Validating metadata in collection (limit: {limit})...")
        
        try:
            # Get all documents
            results = self.collection.get(limit=limit, include=['metadatas', 'documents'])
            
            if not results['ids']:
                print("⚠️ No documents found in collection")
                return self.stats
            
            print(f"📊 Found {len(results['ids'])} documents to validate")
            
            # Validate each document
            for i, doc_id in enumerate(results['ids']):
                metadata = results['metadatas'][i] if results['metadatas'] else {}
                
                is_valid, errors = self.validate_metadata(metadata, doc_id)
                
                if not is_valid:
                    print(f"❌ {doc_id}: {len(errors)} errors")
                    for error in errors[:3]:  # Show first 3 errors
                        print(f"   - {error}")
                elif i % 20 == 0:  # Progress indicator
                    print(f"✅ Validated {i+1}/{len(results['ids'])} documents")
            
            # Print summary
            self.print_validation_summary()
            
            return self.stats
            
        except Exception as e:
            print(f"❌ Error validating collection: {e}")
            return self.stats
    
    def validate_single_document(self, doc_id: str) -> Tuple[bool, List[str]]:
        """Validate a single document by ID"""
        try:
            results = self.collection.get(ids=[doc_id], include=['metadatas', 'documents'])
            
            if not results['ids']:
                return False, [f"Document not found: {doc_id}"]
            
            metadata = results['metadatas'][0] if results['metadatas'] else {}
            return self.validate_metadata(metadata, doc_id)
            
        except Exception as e:
            return False, [f"Error retrieving document: {e}"]
    
    def fix_metadata_issues(self, doc_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to fix common metadata issues"""
        fixed_metadata = metadata.copy()
        fixes_applied = []
        
        # Fix missing fields with defaults
        if 'source_type' not in fixed_metadata:
            fixed_metadata['source_type'] = 'general'
            fixes_applied.append("Added default source_type")
        
        if 'document_type' not in fixed_metadata:
            fixed_metadata['document_type'] = 'document'
            fixes_applied.append("Added default document_type")
        
        if 'content_level' not in fixed_metadata:
            fixed_metadata['content_level'] = 'high_level'
            fixes_applied.append("Added default content_level")
        
        if 'query_keywords' not in fixed_metadata:
            fixed_metadata['query_keywords'] = fixed_metadata['source_type']
            fixes_applied.append("Added default query_keywords")
        
        # Fix type issues
        if 'experiment_id' in fixed_metadata and isinstance(fixed_metadata['experiment_id'], str):
            try:
                fixed_metadata['experiment_id'] = int(fixed_metadata['experiment_id'])
                fixes_applied.append("Converted experiment_id to integer")
            except ValueError:
                pass
        
        # Fix timestamp
        if 'indexed_at' not in fixed_metadata:
            fixed_metadata['indexed_at'] = datetime.now().isoformat()
            fixes_applied.append("Added indexed_at timestamp")
        
        # Fix category based on source_type
        if 'category' not in fixed_metadata:
            category_map = {
                'alife_experiment': 'alife_results',
                'business': 'business',
                'technical': 'technical',
                'general': 'general'
            }
            fixed_metadata['category'] = category_map.get(fixed_metadata['source_type'], 'general')
            fixes_applied.append("Added category based on source_type")
        
        print(f"🔧 Applied {len(fixes_applied)} fixes to {doc_id}:")
        for fix in fixes_applied:
            print(f"   - {fix}")
        
        return fixed_metadata
    
    def print_validation_summary(self):
        """Print validation summary statistics"""
        print(f"\n📊 Validation Summary:")
        print(f"   Total documents: {self.stats['total_documents']}")
        print(f"   Valid documents: {self.stats['valid_documents']}")
        print(f"   Invalid documents: {self.stats['invalid_documents']}")
        
        if self.stats['invalid_documents'] > 0:
            print(f"\n❌ Error breakdown:")
            for error_type, count in self.stats['errors'].items():
                print(f"   {error_type}: {count}")
        
        if self.stats['total_documents'] > 0:
            validity_rate = (self.stats['valid_documents'] / self.stats['total_documents']) * 100
            print(f"\n✅ Validity rate: {validity_rate:.1f}%")

def main():
    """Run metadata validation"""
    validator = MetadataValidator()
    
    # Validate collection
    stats = validator.validate_collection(limit=50)
    
    # Test with a specific document
    print(f"\n🔍 Testing specific document validation...")
    test_metadata = {
        'source_type': 'alife_experiment',
        'document_type': 'summary',
        'content_level': 'high_level',
        'query_keywords': 'harmonic,interference,experiment_4',
        'experiment_id': 4,
        'category': 'alife_results'
    }
    
    is_valid, errors = validator.validate_metadata(test_metadata, "test_doc")
    print(f"Test document validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
    if errors:
        for error in errors:
            print(f"   - {error}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Metadata Automation Monitoring Dashboard
Tracks the health and performance of the metadata tagging system.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import chromadb
from collections import defaultdict, Counter
import sys
import os
sys.path.append(os.path.dirname(__file__))
from metadata_validator import MetadataValidator

class MetadataMonitor:
    """Monitor metadata automation health and performance"""
    
    def __init__(self):
        self.client = chromadb.HttpClient(host="servicebox.taileb8c60.ts.net", port=8000)
        self.collection = self.client.get_collection(name="faithh_knowledge_base")
        self.validator = MetadataValidator()
        
        # Monitoring data
        self.metrics = {
            'total_documents': 0,
            'auto_tagged_documents': 0,
            'schema_compliant': 0,
            'source_type_distribution': Counter(),
            'document_type_distribution': Counter(),
            'content_level_distribution': Counter(),
            'recent_indexing': [],
            'validation_errors': Counter(),
            'indexing_performance': []
        }
    
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive metadata metrics"""
        print("📊 Collecting metadata metrics...")
        
        try:
            # Get sample of documents for analysis
            results = self.collection.get(limit=200, include=['metadatas', 'documents'])
            
            if not results['ids']:
                print("⚠️ No documents found")
                return self.metrics
            
            self.metrics['total_documents'] = len(results['ids'])
            
            # Analyze each document
            for i, doc_id in enumerate(results['ids']):
                metadata = results['metadatas'][i] if results['metadatas'] else {}
                document = results['documents'][i] if results['documents'] else ""
                
                # Check auto-tagging status
                if metadata.get('auto_tagged'):
                    self.metrics['auto_tagged_documents'] += 1
                
                # Validate schema compliance
                is_valid, errors = self.validator.validate_metadata(metadata, doc_id)
                if is_valid:
                    self.metrics['schema_compliant'] += 1
                else:
                    for error in errors:
                        error_type = error.split(':')[0]
                        self.metrics['validation_errors'][error_type] += 1
                
                # Track distributions
                source_type = metadata.get('source_type', 'unknown')
                self.metrics['source_type_distribution'][source_type] += 1
                
                document_type = metadata.get('document_type', 'unknown')
                self.metrics['document_type_distribution'][document_type] += 1
                
                content_level = metadata.get('content_level', 'unknown')
                self.metrics['content_level_distribution'][content_level] += 1
                
                # Track recent indexing
                indexed_at = metadata.get('indexed_at')
                if indexed_at:
                    try:
                        index_time = datetime.fromisoformat(indexed_at.replace('Z', '+00:00'))
                        if datetime.now() - index_time < timedelta(hours=24):
                            self.metrics['recent_indexing'].append({
                                'doc_id': doc_id,
                                'indexed_at': indexed_at,
                                'auto_tagged': metadata.get('auto_tagged', False)
                            })
                    except:
                        pass
            
            return self.metrics
            
        except Exception as e:
            print(f"❌ Error collecting metrics: {e}")
            return self.metrics
    
    def calculate_health_score(self) -> Dict[str, Any]:
        """Calculate overall system health score"""
        if self.metrics['total_documents'] == 0:
            return {'overall': 0, 'components': {}}
        
        # Component scores
        scores = {}
        
        # Auto-tagging coverage (target: >80%)
        auto_tag_rate = (self.metrics['auto_tagged_documents'] / self.metrics['total_documents']) * 100
        scores['auto_tagging'] = min(100, auto_tag_rate * 1.25)  # Scale to 100%
        
        # Schema compliance (target: >95%)
        compliance_rate = (self.metrics['schema_compliant'] / self.metrics['total_documents']) * 100
        scores['schema_compliance'] = min(100, compliance_rate * 1.05)  # Scale to 100%
        
        # Source type diversity (good distribution across types)
        source_types = len(self.metrics['source_type_distribution'])
        scores['diversity'] = min(100, source_types * 10)  # 10 points per type, max 100
        
        # Recent indexing activity (target: >10 in last 24h)
        recent_count = len(self.metrics['recent_indexing'])
        scores['activity'] = min(100, recent_count * 5)  # 5 points per recent doc, max 100
        
        # Overall score (weighted average)
        weights = {'auto_tagging': 0.3, 'schema_compliance': 0.4, 'diversity': 0.1, 'activity': 0.2}
        overall = sum(scores[component] * weights[component] for component in scores)
        
        return {
            'overall': round(overall, 1),
            'components': scores,
            'grades': self._get_health_grades(scores)
        }
    
    def _get_health_grades(self, scores: Dict[str, float]) -> Dict[str, str]:
        """Convert scores to letter grades"""
        grades = {}
        for component, score in scores.items():
            if score >= 90:
                grades[component] = 'A'
            elif score >= 80:
                grades[component] = 'B'
            elif score >= 70:
                grades[component] = 'C'
            elif score >= 60:
                grades[component] = 'D'
            else:
                grades[component] = 'F'
        return grades
    
    def print_dashboard(self):
        """Print monitoring dashboard"""
        health = self.calculate_health_score()
        
        print("\n" + "=" * 60)
        print("🎛️ FAITHH METADATA AUTOMATION DASHBOARD")
        print("=" * 60)
        
        # Overall health
        print(f"\n📈 Overall Health: {health['overall']}% ({self._get_grade_letter(health['overall'])})")
        
        # Component scores
        print(f"\n📊 Component Scores:")
        for component, score in health['components'].items():
            grade = health['grades'][component]
            print(f"   {component.replace('_', ' ').title()}: {score:.1f}% (Grade {grade})")
        
        # Key metrics
        print(f"\n📋 Key Metrics:")
        print(f"   Total Documents: {self.metrics['total_documents']:,}")
        print(f"   Auto-tagged: {self.metrics['auto_tagged_documents']:,} ({self._auto_tag_percentage():.1f}%)")
        print(f"   Schema Compliant: {self.metrics['schema_compliant']:,} ({self._compliance_percentage():.1f}%)")
        print(f"   Recent Indexing: {len(self.metrics['recent_indexing'])} (last 24h)")
        
        # Distribution breakdowns
        if self.metrics['source_type_distribution']:
            print(f"\n🏷️ Source Type Distribution:")
            for source_type, count in self.metrics['source_type_distribution'].most_common(5):
                percentage = (count / self.metrics['total_documents']) * 100
                print(f"   {source_type}: {count} ({percentage:.1f}%)")
        
        if self.metrics['document_type_distribution']:
            print(f"\n📄 Document Type Distribution:")
            for doc_type, count in self.metrics['document_type_distribution'].most_common(5):
                percentage = (count / self.metrics['total_documents']) * 100
                print(f"   {doc_type}: {count} ({percentage:.1f}%)")
        
        # Validation errors
        if self.metrics['validation_errors']:
            print(f"\n❌ Validation Errors:")
            for error_type, count in self.metrics['validation_errors'].most_common(5):
                print(f"   {error_type}: {count}")
        
        # Recent activity
        if self.metrics['recent_indexing']:
            print(f"\n⏰ Recent Indexing Activity (last 10):")
            for item in self.metrics['recent_indexing'][-10:]:
                auto_tag = "🏷️" if item['auto_tagged'] else "📝"
                print(f"   {auto_tag} {item['doc_id']} - {item['indexed_at']}")
        
        print(f"\n🕐 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
    
    def _auto_tag_percentage(self) -> float:
        """Calculate auto-tagging percentage"""
        if self.metrics['total_documents'] == 0:
            return 0.0
        return (self.metrics['auto_tagged_documents'] / self.metrics['total_documents']) * 100
    
    def _compliance_percentage(self) -> float:
        """Calculate schema compliance percentage"""
        if self.metrics['total_documents'] == 0:
            return 0.0
        return (self.metrics['schema_compliant'] / self.metrics['total_documents']) * 100
    
    def _get_grade_letter(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def export_metrics(self, filename: str = None) -> str:
        """Export metrics to JSON file"""
        if filename is None:
            filename = f"metadata_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.metrics,
            'health_score': self.calculate_health_score()
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            print(f"📁 Metrics exported to: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return ""

def main():
    """Run metadata monitoring"""
    monitor = MetadataMonitor()
    
    # Collect metrics
    monitor.collect_metrics()
    
    # Display dashboard
    monitor.print_dashboard()
    
    # Export metrics
    monitor.export_metrics()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
FAITHH Knowledge Base Monitoring System
=====================================
Tracks knowledge base growth, freshness, and health metrics.

This module monitors:
- ChromaDB collection growth and statistics
- Content freshness and staleness detection
- Knowledge base health indicators
- Automated alerts for issues
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None

class KnowledgeBaseMonitor:
    """Monitor knowledge base health and metrics"""
    
    def __init__(self, chroma_host="100.79.85.32", chroma_port=8000):
        self.chroma_host = chroma_host
        self.chroma_port = chroma_port
        self.client = None
        self.metrics_history = []
        self.alerts = []
        
    def connect_chromadb(self):
        """Connect to ChromaDB client"""
        if not chromadb:
            raise ImportError("chromadb not available")
        
        try:
            self.client = chromadb.HttpClient(
                host=self.chroma_host,
                port=self.chroma_port,
                settings=Settings(allow_reset=False, anonymized_telemetry=False)
            )
            return True
        except Exception as e:
            print(f"Failed to connect to ChromaDB: {e}")
            return False
    
    def get_collection_stats(self) -> Dict:
        """Get comprehensive collection statistics"""
        if not self.client:
            if not self.connect_chromadb():
                return {"error": "Could not connect to ChromaDB"}
        
        try:
            collections = self.client.list_collections()
            stats = {
                "timestamp": datetime.now().isoformat(),
                "total_collections": len(collections),
                "collections": []
            }
            
            total_documents = 0
            for collection in collections:
                try:
                    count = collection.count()
                    collection_info = {
                        "name": collection.name,
                        "document_count": count,
                        "metadata": collection.metadata or {}
                    }
                    
                    # Get sample documents to assess freshness
                    if count > 0:
                        try:
                            # Get a few documents to check timestamps
                            results = collection.peek(limit=5)
                            if results and 'metadatas' in results and results['metadatas']:
                                timestamps = []
                                for metadata in results['metadatas']:
                                    if metadata and 'timestamp' in metadata:
                                        timestamps.append(metadata['timestamp'])
                                    elif metadata and 'created_at' in metadata:
                                        timestamps.append(metadata['created_at'])
                                
                                if timestamps:
                                    latest = max(timestamps)
                                    oldest = min(timestamps)
                                    collection_info.update({
                                        "latest_timestamp": latest,
                                        "oldest_timestamp": oldest,
                                        "freshness_score": self._calculate_freshness_score(timestamps)
                                    })
                        except Exception as e:
                            collection_info["freshness_error"] = str(e)
                    
                    stats["collections"].append(collection_info)
                    total_documents += count
                    
                except Exception as e:
                    stats["collections"].append({
                        "name": collection.name,
                        "error": str(e),
                        "document_count": 0
                    })
            
            stats["total_documents"] = total_documents
            return stats
            
        except Exception as e:
            return {"error": f"Failed to get collection stats: {e}"}
    
    def _calculate_freshness_score(self, timestamps: List) -> float:
        """Calculate freshness score (0.0 = stale, 1.0 = fresh)"""
        if not timestamps:
            return 0.0
        
        now = datetime.now()
        age_days = []
        
        for ts in timestamps:
            try:
                if isinstance(ts, str):
                    # Try different timestamp formats
                    for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
                        try:
                            dt = datetime.strptime(ts, fmt)
                            age_days.append((now - dt).days)
                            break
                        except ValueError:
                            continue
                elif isinstance(ts, (int, float)):
                    # Assume Unix timestamp
                    dt = datetime.fromtimestamp(ts)
                    age_days.append((now - dt).days)
            except Exception:
                continue
        
        if not age_days:
            return 0.0
        
        avg_age = sum(age_days) / len(age_days)
        
        # Freshness score: 1.0 for < 7 days, 0.0 for > 90 days
        if avg_age <= 7:
            return 1.0
        elif avg_age >= 90:
            return 0.0
        else:
            # Linear decay from 1.0 to 0.0 between 7 and 90 days
            return 1.0 - ((avg_age - 7) / (90 - 7))
    
    def monitor_growth_trends(self, days: int = 30) -> Dict:
        """Analyze growth trends over specified period"""
        # This would typically read from historical data
        # For now, we'll calculate basic growth metrics
        
        current_stats = self.get_collection_stats()
        if "error" in current_stats:
            return current_stats
        
        # Calculate growth rates (simplified)
        total_docs = current_stats.get("total_documents", 0)
        
        trends = {
            "period_days": days,
            "current_total": total_docs,
            "estimated_daily_growth": total_docs / max(days, 1),  # Simplified
            "growth_rate": "stable" if total_docs > 1000 else "growing",
            "projection_30_days": total_docs + (total_docs / max(days, 1) * 30),
            "projection_90_days": total_docs + (total_docs / max(days, 1) * 90)
        }
        
        return trends
    
    def detect_anomalies(self) -> List[Dict]:
        """Detect potential issues with the knowledge base"""
        anomalies = []
        current_stats = self.get_collection_stats()
        
        if "error" in current_stats:
            anomalies.append({
                "type": "connection_error",
                "severity": "high",
                "message": current_stats["error"],
                "timestamp": datetime.now().isoformat()
            })
            return anomalies
        
        # Check for stale collections
        for collection in current_stats.get("collections", []):
            if "freshness_score" in collection:
                freshness = collection["freshness_score"]
                if freshness < 0.3:
                    anomalies.append({
                        "type": "stale_content",
                        "severity": "medium",
                        "collection": collection["name"],
                        "freshness_score": freshness,
                        "message": f"Collection {collection['name']} has stale content (freshness: {freshness:.2f})",
                        "timestamp": datetime.now().isoformat()
                    })
                elif freshness < 0.1:
                    anomalies.append({
                        "type": "very_stale_content",
                        "severity": "high",
                        "collection": collection["name"],
                        "freshness_score": freshness,
                        "message": f"Collection {collection['name']} has very stale content (freshness: {freshness:.2f})",
                        "timestamp": datetime.now().isoformat()
                    })
        
        # Check for empty collections
        for collection in current_stats.get("collections", []):
            if collection.get("document_count", 0) == 0:
                anomalies.append({
                    "type": "empty_collection",
                    "severity": "low",
                    "collection": collection["name"],
                    "message": f"Collection {collection['name']} is empty",
                    "timestamp": datetime.now().isoformat()
                })
        
        # Check for connection issues
        total_collections = current_stats.get("total_collections", 0)
        if total_collections == 0:
            anomalies.append({
                "type": "no_collections",
                "severity": "high",
                "message": "No collections found in ChromaDB",
                "timestamp": datetime.now().isoformat()
            })
        
        return anomalies
    
    def generate_health_report(self) -> Dict:
        """Generate comprehensive health report"""
        stats = self.get_collection_stats()
        trends = self.monitor_growth_trends()
        anomalies = self.detect_anomalies()
        
        # Calculate overall health score
        health_score = 1.0
        if anomalies:
            for anomaly in anomalies:
                if anomaly["severity"] == "high":
                    health_score -= 0.3
                elif anomaly["severity"] == "medium":
                    health_score -= 0.1
                elif anomaly["severity"] == "low":
                    health_score -= 0.05
        
        health_score = max(0.0, health_score)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "health_score": health_score,
            "health_status": "excellent" if health_score >= 0.9 else "good" if health_score >= 0.7 else "fair" if health_score >= 0.5 else "poor",
            "statistics": stats,
            "trends": trends,
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "recommendations": self._generate_recommendations(anomalies, stats)
        }
        
        return report
    
    def _generate_recommendations(self, anomalies: List[Dict], stats: Dict) -> List[str]:
        """Generate recommendations based on anomalies and stats"""
        recommendations = []
        
        if not anomalies:
            recommendations.append("Knowledge base appears healthy - continue regular monitoring")
            return recommendations
        
        # Check for stale content
        stale_anomalies = [a for a in anomalies if a["type"] in ["stale_content", "very_stale_content"]]
        if stale_anomalies:
            recommendations.append("Update stale content in affected collections to improve freshness")
        
        # Check for empty collections
        empty_anomalies = [a for a in anomalies if a["type"] == "empty_collection"]
        if empty_anomalies:
            recommendations.append("Consider adding content to empty collections or removing them")
        
        # Check for connection issues
        connection_anomalies = [a for a in anomalies if a["type"] in ["connection_error", "no_collections"]]
        if connection_anomalies:
            recommendations.append("Resolve ChromaDB connection issues immediately")
        
        # Check growth trends
        total_docs = stats.get("total_documents", 0)
        if total_docs < 1000:
            recommendations.append("Consider adding more content to reach critical mass for better RAG performance")
        
        return recommendations
    
    def save_metrics(self, filename: str = "knowledge_base_metrics.json"):
        """Save current metrics to file"""
        report = self.generate_health_report()
        
        try:
            # Load existing metrics if file exists
            metrics_file = Path("ml/output") / filename
            metrics_file.parent.mkdir(exist_ok=True, parents=True)
            
            existing_data = []
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    existing_data = json.load(f)
            
            # Add current report
            existing_data.append(report)
            
            # Keep only last 30 days of data
            cutoff_date = datetime.now() - timedelta(days=30)
            existing_data = [
                entry for entry in existing_data
                if datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00")) > cutoff_date
            ]
            
            # Save updated metrics
            with open(metrics_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Failed to save metrics: {e}")
            return False


def main():
    """Run knowledge base monitoring"""
    print("🔍 FAITHH Knowledge Base Monitoring")
    print("=" * 50)
    
    monitor = KnowledgeBaseMonitor()
    
    # Generate health report
    print("\n📊 Generating health report...")
    report = monitor.generate_health_report()
    
    # Display key metrics
    print(f"\n🎯 Health Score: {report['health_score']:.2f} ({report['health_status']})")
    print(f"📚 Total Documents: {report['statistics'].get('total_documents', 'Unknown')}")
    print(f"📁 Total Collections: {report['statistics'].get('total_collections', 'Unknown')}")
    print(f"⚠️  Anomalies Found: {report['anomaly_count']}")
    
    # Display anomalies if any
    if report['anomalies']:
        print(f"\n⚠️  Anomalies:")
        for anomaly in report['anomalies'][:5]:  # Show first 5
            print(f"   - {anomaly['message']} ({anomaly['severity']})")
        if len(report['anomalies']) > 5:
            print(f"   ... and {len(report['anomalies']) - 5} more")
    
    # Display recommendations
    if report['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"   - {rec}")
    
    # Save metrics
    print(f"\n💾 Saving metrics...")
    if monitor.save_metrics():
        print("✅ Metrics saved to ml/output/knowledge_base_metrics.json")
    else:
        print("❌ Failed to save metrics")
    
    print(f"\n🏁 Monitoring complete!")


if __name__ == "__main__":
    main()

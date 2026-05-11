"""
Master Reference Auto-Update Blueprint

Flask blueprint that enables FAITHH to:
1. Search for information about unknown sections
2. Log discoveries for review
3. Update master references when approved

Add to backend with:
    from discovery_blueprint import create_discovery_blueprint
    discovery_bp = create_discovery_blueprint(collection, CHROMA_CONNECTED)
    app.register_blueprint(discovery_bp)
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import json
from pathlib import Path
import re


def create_discovery_blueprint(collection, chroma_connected):
    """
    Factory function to create discovery blueprint
    """
    
    discovery = Blueprint('discovery', __name__)
    
    # Discovery queries configuration
    DISCOVERY_QUERIES = {
        "ucf": ["UCF unified civic framework", "UCF governance mechanism"],
        "tokens": ["Astris Auctor token", "token voting governance"],
        "tome": ["civic tome documentation", "tome entry structure"],
        "penumbra": ["penumbra accord constella", "penumbra edge case"],
        "map_of_intent": ["map of intent constella", "intent alignment"],
        "relationships": ["constella components connect", "decision flow"],
        "decisions": ["we decided constella", "design decision governance"]
    }
    
    # Pending discoveries awaiting approval
    PENDING_DISCOVERIES = []
    
    @discovery.route('/api/discover/<section>', methods=['GET'])
    def discover_section(section):
        """
        Search for information about a specific section
        
        GET /api/discover/ucf
        GET /api/discover/tokens
        """
        if not chroma_connected:
            return jsonify({'error': 'ChromaDB not connected'}), 503
        
        if section not in DISCOVERY_QUERIES:
            return jsonify({
                'error': f'Unknown section: {section}',
                'available': list(DISCOVERY_QUERIES.keys())
            }), 400
        
        queries = DISCOVERY_QUERIES[section]
        all_results = []
        seen_docs = set()
        
        for query in queries:
            try:
                results = collection.query(
                    query_texts=[query],
                    n_results=5,
                    where={"$or": [
                        {"category": "claude_conversation_chunk"},
                        {"category": "claude_conversation"}
                    ]}
                )
                
                if results['documents'] and results['documents'][0]:
                    for i, doc in enumerate(results['documents'][0]):
                        # Deduplicate
                        doc_hash = hash(doc[:200])
                        if doc_hash in seen_docs:
                            continue
                        seen_docs.add(doc_hash)
                        
                        distance = results['distances'][0][i] if results['distances'] else 1.0
                        
                        if distance < 0.7:  # Good match threshold
                            all_results.append({
                                'query': query,
                                'excerpt': doc[:500],
                                'distance': distance,
                                'relevance': 'high' if distance < 0.4 else 'medium'
                            })
            except Exception as e:
                print(f"Discovery query failed: {e}")
        
        # Sort by relevance
        all_results.sort(key=lambda x: x['distance'])
        
        return jsonify({
            'section': section,
            'discoveries': all_results[:10],
            'count': len(all_results),
            'queries_used': queries
        })
    
    @discovery.route('/api/discover/all', methods=['GET'])
    def discover_all():
        """
        Run discovery for all unknown sections
        """
        if not chroma_connected:
            return jsonify({'error': 'ChromaDB not connected'}), 503
        
        all_discoveries = {}
        
        for section in DISCOVERY_QUERIES:
            queries = DISCOVERY_QUERIES[section]
            section_results = []
            
            for query in queries:
                try:
                    results = collection.query(
                        query_texts=[query],
                        n_results=3,
                        where={"$or": [
                            {"category": "claude_conversation_chunk"},
                            {"category": "claude_conversation"}
                        ]}
                    )
                    
                    if results['documents'] and results['documents'][0]:
                        for i, doc in enumerate(results['documents'][0]):
                            distance = results['distances'][0][i]
                            if distance < 0.6:
                                section_results.append({
                                    'excerpt': doc[:300],
                                    'distance': distance
                                })
                except:
                    pass
            
            if section_results:
                section_results.sort(key=lambda x: x['distance'])
                all_discoveries[section] = {
                    'found': True,
                    'best_match': section_results[0],
                    'total_matches': len(section_results)
                }
            else:
                all_discoveries[section] = {
                    'found': False,
                    'message': 'No relevant information found'
                }
        
        # Summary
        found_count = sum(1 for v in all_discoveries.values() if v['found'])
        
        return jsonify({
            'discoveries': all_discoveries,
            'summary': {
                'sections_with_info': found_count,
                'sections_empty': len(DISCOVERY_QUERIES) - found_count
            }
        })
    
    @discovery.route('/api/discovery/suggest', methods=['POST'])
    def suggest_update():
        """
        Log a discovery for review and potential master doc update
        
        POST body:
        {
            "section": "ucf",
            "discovered_text": "UCF handles compliance through...",
            "source": "conversation about governance",
            "confidence": "medium"
        }
        """
        data = request.json
        
        required = ['section', 'discovered_text']
        if not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        suggestion = {
            'id': len(PENDING_DISCOVERIES) + 1,
            'section': data['section'],
            'discovered_text': data['discovered_text'],
            'source': data.get('source', 'unknown'),
            'confidence': data.get('confidence', 'low'),
            'suggested_at': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        PENDING_DISCOVERIES.append(suggestion)
        
        # Also save to file for persistence
        discoveries_file = Path.home() / "ai-stack/docs/pending_discoveries.json"
        try:
            existing = []
            if discoveries_file.exists():
                with open(discoveries_file, 'r') as f:
                    existing = json.load(f)
            existing.append(suggestion)
            with open(discoveries_file, 'w') as f:
                json.dump(existing, f, indent=2)
        except Exception as e:
            print(f"Failed to save discovery: {e}")
        
        return jsonify({
            'success': True,
            'suggestion_id': suggestion['id'],
            'message': 'Discovery logged for review'
        })
    
    @discovery.route('/api/discovery/pending', methods=['GET'])
    def get_pending():
        """Get all pending discovery suggestions"""
        discoveries_file = Path.home() / "ai-stack/docs/pending_discoveries.json"
        
        try:
            if discoveries_file.exists():
                with open(discoveries_file, 'r') as f:
                    pending = json.load(f)
                return jsonify({'pending': pending, 'count': len(pending)})
            else:
                return jsonify({'pending': [], 'count': 0})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @discovery.route('/api/master_reference/status', methods=['GET'])
    def master_reference_status():
        """
        Get current status of master reference document
        Shows which sections are known, partial, or unknown
        """
        master_file = Path.home() / "ai-stack/docs/CONSTELLA_MASTER_REFERENCE.md"
        
        try:
            if not master_file.exists():
                return jsonify({'error': 'Master reference not found'}), 404
            
            with open(master_file, 'r') as f:
                content = f.read()
            
            # Parse confidence levels
            known = len(re.findall(r'✅ \*\*KNOWN\*\*', content))
            partial = len(re.findall(r'🔶 \*\*PARTIAL\*\*', content))
            unknown = len(re.findall(r'❓ \*\*UNKNOWN\*\*', content))
            
            # Get last updated
            updated_match = re.search(r'\*\*Last Updated\*\*: (\d{4}-\d{2}-\d{2})', content)
            last_updated = updated_match.group(1) if updated_match else 'unknown'
            
            return jsonify({
                'status': 'active',
                'confidence_levels': {
                    'known': known,
                    'partial': partial,
                    'unknown': unknown
                },
                'last_updated': last_updated,
                'file': str(master_file),
                'completeness': f"{known}/{known + partial + unknown} sections complete"
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return discovery


# Standalone test
if __name__ == "__main__":
    print("Discovery Blueprint - Use with Flask app")
    print("Import with: from discovery_blueprint import create_discovery_blueprint")

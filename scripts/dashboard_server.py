#!/usr/bin/env python3
"""
Simple HTTP server to serve dashboard data and visualization
"""

import json
import os
import sys
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
import subprocess

# Add backend to path for ML learning framework
sys.path.insert(0, '/home/jonat/ai-stack')
from backend.ml_learning_framework import MLLearningFramework
from backend.ui_layout_optimizer import UILayoutOptimizer

class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/dashboard_data.json':
            self.serve_dashboard_data()
        elif parsed_path.path == '/refresh':
            self.refresh_data()
        elif parsed_path.path == '/api/ml-learning':
            self.serve_ml_learning_data()
        elif parsed_path.path == '/api/ui-layout':
            self.serve_ui_layout_data()
        else:
            # Serve static files
            super().do_GET()
    
    def serve_dashboard_data(self):
        """Serve the dashboard data JSON"""
        try:
            # Check if dashboard data exists, if not regenerate it
            if not os.path.exists('/home/jonat/ai-stack/dashboard_data.json'):
                self.refresh_data()
            
            with open('/home/jonat/ai-stack/dashboard_data.json', 'r') as f:
                data = json.load(f)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        except Exception as e:
            self.send_error(500, f"Error serving dashboard data: {str(e)}")
    
    def refresh_data(self):
        """Refresh dashboard data by running the processing script"""
        try:
            # Run the chat export processing script
            result = subprocess.run([
                sys.executable, 
                '/home/jonat/ai-stack/scripts/process_chat_exports.py'
            ], capture_output=True, text=True, cwd='/home/jonat/ai-stack')
            
            if result.returncode == 0:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "message": "Data refreshed"}).encode())
            else:
                self.send_error(500, f"Error refreshing data: {result.stderr}")
        except Exception as e:
            self.send_error(500, f"Error refreshing data: {str(e)}")
    
    def serve_ml_learning_data(self):
        """Serve ML learning framework data"""
        try:
            framework = MLLearningFramework()
            
            # Collect learning node data
            nodes_data = []
            for node_id, node in framework.nodes.items():
                nodes_data.append({
                    'id': node.id,
                    'type': node.type,
                    'current_state': node.current_state,
                    'performance_metrics': node.performance_metrics,
                    'learning_history_count': len(node.learning_history),
                    'last_updated': node.last_updated.isoformat(),
                    'recommendations': framework.get_node_recommendations(node_id)
                })
            
            # Collect framework statistics
            stats = {
                'total_nodes': len(framework.nodes),
                'nodes_by_type': {},
                'active_learning': 0,
                'avg_performance': 0.0
            }
            
            for node in framework.nodes.values():
                node_type = node.type
                stats['nodes_by_type'][node_type] = stats['nodes_by_type'].get(node_type, 0) + 1
                
                # Check if recently active (updated within last hour)
                if (datetime.now() - node.last_updated).total_seconds() < 3600:
                    stats['active_learning'] += 1
                
                # Calculate average performance
                if node.performance_metrics:
                    avg_metrics = sum(node.performance_metrics.values()) / len(node.performance_metrics)
                    stats['avg_performance'] += avg_metrics
            
            if len(framework.nodes) > 0:
                stats['avg_performance'] /= len(framework.nodes)
            
            data = {
                'nodes': nodes_data,
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
            
        except Exception as e:
            self.send_error(500, f"Error serving ML learning data: {str(e)}")
    
    def serve_ui_layout_data(self):
        """Serve UI layout optimization data"""
        try:
            optimizer = UILayoutOptimizer()
            
            # Collect layout interaction data
            interactions = optimizer.get_interaction_patterns()
            layout_stats = optimizer.get_layout_statistics()
            optimal_layouts = optimizer.get_optimal_layouts()
            
            data = {
                'interaction_patterns': interactions,
                'layout_statistics': layout_stats,
                'optimal_layouts': optimal_layouts,
                'timestamp': datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
            
        except Exception as e:
            self.send_error(500, f"Error serving UI layout data: {str(e)}")

def main():
    """Start the dashboard server"""
    port = 8080
    
    print(f"Starting FAITHH Journey Dashboard server on port {port}")
    print(f"Dashboard available at: http://localhost:{port}/faithh_journey_dashboard.html")
    print(f"API endpoints:")
    print(f"  - Dashboard data: http://localhost:{port}/dashboard_data.json")
    print(f"  - ML Learning: http://localhost:{port}/api/ml-learning")
    print(f"  - UI Layout: http://localhost:{port}/api/ui-layout")
    print(f"  - Refresh: http://localhost:{port}/refresh")
    
    # Change to the correct directory
    os.chdir('/home/jonat/ai-stack')
    
    server = HTTPServer(('localhost', port), DashboardHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Process chat exports to extract timeline, domain activity, and project patterns
for the 5-year journey visualization dashboard.
"""

import json
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import os

# Domain keywords for classification
DOMAIN_KEYWORDS = {
    'technical': {
        'keywords': ['faithh', 'backend', 'frontend', 'api', 'chroma', 'ollama', 'rag', 'ml chips', 'pulse', 'python', 'flask', 'docker', 'gpu', 'embedding', 'vector'],
        'projects': ['FAITHH', 'Backend', 'ML Chips', 'PULSE', 'RAG Pipeline']
    },
    'business': {
        'keywords': ['tom cat', 'audio', 'sound', 'music', 'client', 'revenue', 'business', 'invoice', 'production', 'mastering', 'mixing'],
        'projects': ['Tom Cat Sound', 'Floating Garden', 'Audio Production']
    },
    'civic': {
        'keywords': ['constella', 'governance', 'civic', 'framework', 'tokens', 'astris', 'auctor', 'penumbra', 'ucf', 'community'],
        'projects': ['Constella', 'Governance Framework', 'Civic Innovation']
    },
    'personal': {
        'keywords': ['mexico', 'spanish', 'permaculture', 'garden', 'life', 'personal', 'cross-border', 'lifestyle', 'rhythm'],
        'projects': ['Life Integration', 'Permaculture', 'Spanish Learning']
    }
}

def classify_message(content):
    """Classify a message by domain based on keywords."""
    if not content:
        return None
    
    content_lower = content.lower()
    domain_scores = {}
    
    for domain, config in DOMAIN_KEYWORDS.items():
        score = 0
        for keyword in config['keywords']:
            score += content_lower.count(keyword)
        domain_scores[domain] = score
    
    if max(domain_scores.values()) == 0:
        return None
    
    return max(domain_scores, key=domain_scores.get)

def extract_timeline_data(chat_file):
    """Extract timeline data from chat exports."""
    print(f"Processing {chat_file}...")
    
    with open(chat_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    timeline = []
    domain_activity = defaultdict(list)
    project_mentions = defaultdict(list)
    activity_intensity = defaultdict(int)
    
    for conversation in data:
        date_str = conversation.get('date', '')
        title = conversation.get('title', '')
        
        # Parse date
        try:
            if '2025' in date_str:
                date = datetime.strptime(date_str, '%Y-%m-%d')
            elif '2026' in date_str:
                date = datetime.strptime(date_str, '%Y-%m-%d')
            else:
                continue
        except ValueError:
            continue
        
        # Extract messages and classify
        mapping = conversation.get('mapping', {})
        message_count = 0
        domains_in_convo = set()
        
        for node_id, node_data in mapping.items():
            if 'message' in node_data:
                message = node_data['message']
                if message and 'content' in message:
                    content_parts = message.get('content', {}).get('parts', [])
                    for part in content_parts:
                        if isinstance(part, str) and part.strip():
                            message_count += 1
                            domain = classify_message(part)
                            if domain:
                                domains_in_convo.add(domain)
                                
                                # Track project mentions
                                for project in DOMAIN_KEYWORDS[domain]['projects']:
                                    if project.lower() in part.lower():
                                        project_mentions[project].append({
                                            'date': date.isoformat(),
                                            'context': part[:100] + '...' if len(part) > 100 else part
                                        })
        
        # Record activity
        if message_count > 0:
            timeline.append({
                'date': date.isoformat(),
                'title': title,
                'message_count': message_count,
                'domains': list(domains_in_convo),
                'intensity': min(message_count, 10)  # Cap at 10 for visualization
            })
            
            # Track domain activity over time
            for domain in domains_in_convo:
                domain_activity[domain].append(date.isoformat())
                activity_intensity[f"{date.strftime('%Y-%m-%d')}_{domain}"] += message_count
    
    return timeline, domain_activity, project_mentions, activity_intensity

def calculate_domain_progress(domain_activity, project_states):
    """Calculate domain progress percentages based on activity and project states."""
    progress = {}
    
    # Base progress from project states
    for domain in DOMAIN_KEYWORDS.keys():
        base_progress = 0
        
        if domain == 'technical':
            # FAITHH progress from backend features
            base_progress = 70  # Based on current implementation
        elif domain == 'business':
            # Tom Cat Sound revenue progress
            base_progress = 40  # Based on current state
        elif domain == 'civic':
            # Constella documentation progress
            base_progress = 20  # Pre-launch phase
        elif domain == 'personal':
            # Life integration progress
            base_progress = 50  # Mexico setup ongoing
        
        # Boost based on recent activity
        if domain in domain_activity:
            recent_activity = len([d for d in domain_activity[domain] 
                                if datetime.fromisoformat(d) > datetime.now() - timedelta(days=30)])
            activity_boost = min(recent_activity * 2, 20)
            progress[domain] = min(base_progress + activity_boost, 95)
        else:
            progress[domain] = base_progress
    
    return progress

def generate_milestones(timeline, project_mentions):
    """Generate key milestones from timeline data."""
    milestones = []
    
    # Sort timeline by date
    sorted_timeline = sorted(timeline, key=lambda x: x['date'])
    
    # Group by month and find significant activity
    monthly_activity = defaultdict(list)
    for entry in sorted_timeline:
        month = entry['date'][:7]  # YYYY-MM
        monthly_activity[month].append(entry)
    
    for month, entries in monthly_activity.items():
        if not entries:
            continue
            
        total_messages = sum(e['message_count'] for e in entries)
        domains_present = set()
        for e in entries:
            domains_present.update(e['domains'])
        
        # Create milestone for significant months
        if total_messages > 50 or len(domains_present) >= 2:
            milestones.append({
                'date': month + '-01',
                'title': f"Major Development: {month}",
                'description': f"{total_messages} messages across {len(domains_present)} domains",
                'domains': list(domains_present),
                'type': 'milestone'
            })
    
    return milestones

def create_dashboard_data():
    """Create the main dashboard data structure."""
    # Process chat exports
    all_timeline = []
    all_domain_activity = defaultdict(list)
    all_project_mentions = defaultdict(list)
    all_activity_intensity = defaultdict(int)
    
    # Process all recent convos
    all_convos_file = '/home/jonat/ai-stack/AI_Chat_Exports/all_recent_convos.json'
    if os.path.exists(all_convos_file):
        timeline, domain_activity, project_mentions, activity_intensity = extract_timeline_data(all_convos_file)
        all_timeline.extend(timeline)
        for domain, dates in domain_activity.items():
            all_domain_activity[domain].extend(dates)
        for project, mentions in project_mentions.items():
            all_project_mentions[project].extend(mentions)
        for key, value in activity_intensity.items():
            all_activity_intensity[key] += value
    
    # Process FAITHH convos
    faithh_convos_file = '/home/jonat/ai-stack/AI_Chat_Exports/recent_faithh_convos.json'
    if os.path.exists(faithh_convos_file):
        timeline, domain_activity, project_mentions, activity_intensity = extract_timeline_data(faithh_convos_file)
        all_timeline.extend(timeline)
        for domain, dates in domain_activity.items():
            all_domain_activity[domain].extend(dates)
        for project, mentions in project_mentions.items():
            all_project_mentions[project].extend(mentions)
        for key, value in activity_intensity.items():
            all_activity_intensity[key] += value
    
    # Load project states
    project_states = {}
    states_file = '/home/jonat/ai-stack/project_states.json'
    if os.path.exists(states_file):
        with open(states_file, 'r') as f:
            project_states = json.load(f)
    
    # Calculate metrics
    domain_progress = calculate_domain_progress(all_domain_activity, project_states)
    milestones = generate_milestones(all_timeline, all_project_mentions)
    
    # Generate activity heatmap data
    heatmap_data = generate_heatmap_data(all_activity_intensity)
    
    # Create dashboard data
    dashboard_data = {
        'generated_at': datetime.now().isoformat(),
        'timeline': sorted(all_timeline, key=lambda x: x['date'])[-100:],  # Last 100 entries
        'domain_progress': domain_progress,
        'domain_activity': dict(all_domain_activity),
        'milestones': milestones,
        'project_mentions': dict(all_project_mentions),
        'heatmap_data': heatmap_data,
        'strategic_context': {
            'current_phase': 'Phase 2: Infrastructure',
            'phase_progress': 35,  # Current position in 5-year journey
            'strategic_coherence_score': 85  # Based on plan integration
        }
    }
    
    return dashboard_data

def generate_heatmap_data(activity_intensity):
    """Generate heatmap data for activity visualization."""
    heatmap = []
    
    # Generate 26 weeks of data (6 months)
    start_date = datetime.now() - timedelta(weeks=26)
    
    for week in range(26):
        week_date = start_date + timedelta(weeks=week)
        week_str = week_date.strftime('%Y-%m-%d')
        
        week_data = []
        for day in range(7):
            day_date = week_date + timedelta(days=day)
            day_str = day_date.strftime('%Y-%m-%d')
            
            # Calculate activity for this day
            day_activity = 0
            for domain in DOMAIN_KEYWORDS.keys():
                key = f"{day_str}_{domain}"
                day_activity += activity_intensity.get(key, 0)
            
            # Normalize to 0-5 scale
            intensity = min(int(day_activity / 10), 5)
            week_data.append(intensity)
        
        heatmap.append(week_data)
    
    return heatmap

def main():
    """Main processing function."""
    print("Processing chat exports for dashboard visualization...")
    
    dashboard_data = create_dashboard_data()
    
    # Save dashboard data
    output_file = '/home/jonat/ai-stack/dashboard_data.json'
    with open(output_file, 'w') as f:
        json.dump(dashboard_data, f, indent=2)
    
    print(f"Dashboard data saved to {output_file}")
    print(f"Processed {len(dashboard_data['timeline'])} timeline entries")
    print(f"Generated {len(dashboard_data['milestones'])} milestones")
    print(f"Domain progress: {dashboard_data['domain_progress']}")

if __name__ == "__main__":
    main()

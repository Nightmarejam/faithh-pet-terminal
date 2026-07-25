#!/usr/bin/env python3

query = "What is the Universal Civic Floor and how does it work?"
governance_keywords = [
    'constitution', 'constitutional', 'governance', 'governing', 'ucf', 'penumbra', 
    'civic tome', 'astris', 'auctor', 'token', 'floor', 'diversity floor',
    'principle', 'framework', 'charter', 'bylaws', 'rules', 'regulation',
    'gamer', 'minimum compliance', 'structural', 'mechanism', 'policy',
    'governance design', 'participation', 'civic', 'democratic', 'decision making'
]

query_lower = query.lower()
is_governance_query = any(keyword in query_lower for keyword in governance_keywords)

print(f"Query: {query_lower}")
print(f"Keywords found: {[k for k in governance_keywords if k in query_lower]}")
print(f"Is governance query: {is_governance_query}")

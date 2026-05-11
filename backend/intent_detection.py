"""
FAITHH Backend — Intent Detection
Analyzes user queries to determine which integrations/chips should fire.
Extracted from faithh_professional_backend_fixed.py for modularity.
"""

import re


def detect_query_intent(query_text):
    """
    Analyze query to determine which integrations to use
    Returns dict with flags and matched patterns
    """
    query_lower = query_text.lower()
    intent = {
        'is_self_query': False,
        'is_why_question': False,
        'is_next_action_query': False,
        'is_project_query': False,
        'is_constella_query': False,
        'is_business_query': False,
        'is_recent_changes_query': False,
        'needs_orientation': False,
        'is_tangent': False,
        'is_reasoning': False,
        'is_coding': False,
        'is_complex_query': False,
        'patterns_matched': []
    }
    
    # Pattern 1: Self-awareness (asking about FAITHH itself)
    self_patterns = [
        r'\bfaithh\b',
        r'what are you',
        r'what is your',
        r'tell me about yourself',
        r'who are you',
        r'what do you do'
    ]
    for pattern in self_patterns:
        if re.search(pattern, query_lower):
            intent['is_self_query'] = True
            intent['patterns_matched'].append(f"self: {pattern}")
            break
    
    # Pattern 2: "Why" decisions (asking rationale)
    why_patterns = [
        r'why did (we|you|i) (choose|use|pick|select|go with)',
        r'why.*instead of',
        r'why.*over',
        r'what was the reason',
        r'rationale for',
        r'why.*decision'
    ]
    for pattern in why_patterns:
        if re.search(pattern, query_lower):
            intent['is_why_question'] = True
            intent['patterns_matched'].append(f"why: {pattern}")
            break
    
    # Pattern 3: Next actions (asking what to work on)
    next_patterns = [
        r'what should (i|we) work on',
        r"what('s| is) next",
        r'what to do next',
        r'what should (i|we) focus on',
        r'what are (my|the) priorities',
        r'where should (i|we) start',
        r'what.*missing'
    ]
    for pattern in next_patterns:
        if re.search(pattern, query_lower):
            intent['is_next_action_query'] = True
            intent['patterns_matched'].append(f"next: {pattern}")
            break
    
    # Pattern 3b: General project queries (asking about projects, status, state)
    project_patterns = [
        r'what (projects|am i working on|are my projects)',
        r'(my |the |current )?projects',
        r'project (status|state|overview|summary)',
        r'what.*working on',
        r'(tell|show) me (about )?(my |the )?projects',
        r'how.*projects.*going',
    ]
    for pattern in project_patterns:
        if re.search(pattern, query_lower):
            intent['is_project_query'] = True
            intent['patterns_matched'].append(f"project: {pattern}")
            break

    # Pattern 4: Constella queries (domain-specific)
    constella_keywords = ['constella', 'astris', 'auctor', 'civic tome', 'penumbra',
                          'ucf', 'resonance gap', 'harmonic', 'celestial equilibrium']
    if any(kw in query_lower for kw in constella_keywords):
        intent['is_constella_query'] = True
    
    # Pattern 4b: Business/Audio queries (Tom Cat Sound, FGS)
    business_keywords = ['tom cat', 'tomcat', 'floating garden', 'soundworks', 'fgs',
                         'mastering', 'audio business', 'llc', 'audio production',
                         'equipment', 'clients', 'pricing', 'grant', 'sbdc']
    if any(kw in query_lower for kw in business_keywords):
        intent['is_business_query'] = True
        intent['patterns_matched'].append(f"business: matched")
    
    # Pattern 5b: Recent changes queries (what was updated/changed recently?)
    recent_patterns = [
        r'(last|latest|recent|newest) (update|change|commit|modification|edit)',
        r'what (did we|have we|was) (just )?(update|change|modify|edit|touch|do)',
        r'what (was|were) (the )?(last|latest|recent) (thing|change|update)',
        r'what.*touched up',
        r'what.*last.*update',
        r'what changed',
        r'what did (we|you) (just )?do',
        r'(show|tell).*recent (changes|updates|commits)',
    ]
    for pattern in recent_patterns:
        if re.search(pattern, query_lower):
            intent['is_recent_changes_query'] = True
            intent['patterns_matched'].append(f"recent_changes: {pattern}")
            break

    # Pattern 5: Orientation queries (scaffolding - where am I?)
    orientation_patterns = [
        r'where (was i|did i leave off|am i|are we)',
        r'what was i (working on|doing)',
        r'catch me up',
        r'bring me up to speed',
        r"what('s| is) (the |my )?(status|progress)",
        r"(my |the |what('s| is) )progress",
        r"what('s| is| have i) (been )?(done|complete|finished)",
        r'am i on track',
        r'where (did we|do we) stand',
        r'what have (i|we) (done|accomplished|completed)',
        r'update me'
    ]
    for pattern in orientation_patterns:
        if re.search(pattern, query_lower):
            intent['needs_orientation'] = True
            intent['patterns_matched'].append(f"orientation: {pattern}")
            break
    
    # Pattern 6: Reasoning queries (complex thinking)
    reasoning_patterns = [
        r'\bcompare (and|versus|vs)\b',
        r'\banalyze\b',
        r'\bevaluate\b',
        r'\bphilosophy\b',
        r'\bphilosophical\b',
        r'\bimplication(s)?\b',
        r'\bcontrast\b',
        r'\bsynthesize\b',
        r'\bwhat (if|would happen)\b',
        r'\bhypothetical\b',
        r'\btheoretical\b',
        r'\babstract\b',
        r'\bconceptual\b',
        r'\bfundamental\b',
        r'\bprinciple(s)?\b',
        r'\bexplain (the |a )?concept\b',
        r'\bmeaning of\b',
        r'\bwhy does\b',
        r'\bhow does\b.*work',
        r'\bwhat if\b',
        r'\bthe relationship between\b',
    ]
    for pattern in reasoning_patterns:
        if re.search(pattern, query_lower):
            intent['is_reasoning'] = True
            intent['patterns_matched'].append(f"reasoning: {pattern}")
            break
    
    # Pattern 7: Coding queries
    coding_patterns = [
        r'\bwrite (a |some )?code\b',
        r'\bwrite (a |some )?program\b',
        r'\bwrite (a |some )?script\b',
        r'\bcreate (a |some )?function\b',
        r'\bimplement (a |some )?function\b',
        r'\bdebug (this |my |the )?code\b',
        r'\bfix (this |my |the )?code\b',
        r'\bparse (a |some |the )?json\b',
        r'\bcompile (this |my |the )?code\b',
        r'\bhow to (code|program|script)\b',
        r'\bpython (code|script|function)\b',
        r'\bjavascript (code|script|function)\b',
        r'\bjava (code|class|method)\b',
        r'\bc\+\+ (code|class|function)\b',
        r'\bvariable(s)?\b.*(in|for|of)',
        r'\bloop(s)?\b.*(through|over|in)',
        r'\bif (statement|condition|clause)\b',
        r'\bclass (definition|structure|hierarchy)\b',
        r'\bobject(.*oriented)?\b',
        r'\bmethod(s)?\b.*(call|invoke)',
        r'\bapi (endpoint|call|request)\b',
        r'\blibrary (function|method|import)\b',
        r'\bframework (usage|configuration|setup)\b',
    ]
    for pattern in coding_patterns:
        if re.search(pattern, query_lower):
            intent['is_coding'] = True
            intent['patterns_matched'].append(f"coding: {pattern}")
            break
    
    # Pattern 8: Complex queries (longer, multi-part)
    if len(query_text) > 100 and (' and ' in query_lower or ' or ' in query_lower):
        intent['is_complex_query'] = True
        intent['patterns_matched'].append("complex: long multi-part query")
    
    return intent

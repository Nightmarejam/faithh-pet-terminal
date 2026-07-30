"""
FAITHH Backend — Intent Detection
Analyzes user queries to determine which integrations/chips should fire.
Extracted from faithh_professional_backend_fixed.py for modularity.
"""

import re


def detect_query_intent(query_text):
    # Logic for Humans: Regex-scan the user message and set boolean flags (self-query, RAG vs ALIFE, governance, coding, etc.) that downstream chips and RAG use.
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
        'is_alife_query': False,
        'needs_orientation': False,
        'is_tangent': False,
        'is_reasoning': False,
        'is_coding': False,
        'is_complex_query': False,
        'is_social': False,
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
    
    # Pattern 8: ALIFE queries (experiments, simulations, waves)
    alife_patterns = [
        r'\balife\b',
        r'\bartificial life\b',
        r'\bexperiment [0-9]+\b',
        r'\bexp[0-9]+\b',
        r'\bsimulation\b',
        r'\bwave[s]?\b',
        r'\bagent[s]?\b.*\bevolution\b',
        r'\bgenome[s]?\b.*\bevolution\b',
        r'\bharmonic\b.*\binterference\b',
        r'\bstealth\b.*\bwaves?\b',
        r'\bshield[s]?\b.*\bdefense\b',
        r'\bpredator\b.*\bprey\b',
        r'\btick[s]?\b.*\bsimulation\b',
        r'\bpopulation\b.*\bdynamics\b',
    ]
    for pattern in alife_patterns:
        if re.search(pattern, query_lower):
            intent['is_alife_query'] = True
            intent['patterns_matched'].append(f"alife: {pattern}")
            break
    
    # Pattern 9: Complex queries (longer, multi-part)
    if len(query_text) > 100 and (' and ' in query_lower or ' or ' in query_lower):
        intent['is_complex_query'] = True
        intent['patterns_matched'].append("complex: long multi-part query")

    # Pattern 10: Social / smalltalk — a greeting is not a knowledge-base question.
    #
    # "Hello there, it has been a while. How are you" used to fire RAG, pull in
    # unrelated infrastructure notes, and get answered with speculation about port
    # 5557. The retrieval was working; it simply had nothing relevant, which the
    # flat ML-topic spread (top match 55%) already showed.
    #
    # Two guards keep this from suppressing real questions:
    #   - nothing substantive may have matched, so "Hi, what is Constella?" still
    #     retrieves (is_constella_query wins)
    #   - the message must be short, so a greeting prefixed to a long technical
    #     question does not silence retrieval for the whole thing
    _substantive = any(intent[k] for k in (
        'is_self_query', 'is_why_question', 'is_next_action_query',
        'is_project_query', 'is_constella_query', 'is_business_query',
        'is_recent_changes_query', 'is_alife_query', 'is_coding',
        'is_reasoning', 'needs_orientation', 'is_complex_query',
    ))
    social_patterns = [
        r'^\s*(hi|hey|hello|yo|sup|howdy|greetings)\b',
        r'\bhow are you\b',
        r"\bhow'?s it going\b",
        r'\bhow have you been\b',
        r'\bgood (morning|afternoon|evening|night)\b',
        r"\bit'?s been a while\b",
        r'\bit has been a while\b',
        r'\blong time no see\b',
        r'\bnice to (meet|see) you\b',
        r'^\s*(thanks|thank you|thx|ty)\b',
        r'^\s*(bye|goodbye|see ya|later|goodnight)\b',
    ]
    # Filler that carries no retrievable content once the greeting is removed.
    _social_filler = {
        'there', 'again', 'friend', 'buddy', 'today', 'tonight', 'much', 'well',
        'doing', 'you', 'your', 'i', 'am', 'is', 'it', 'a', 'the', 'and', 'so',
        'just', 'ok', 'okay', 'lol', 'haha', 'my', 'me', 'to', 'been', 'of',
    }
    if not _substantive and len(query_lower.split()) <= 14:
        matched = None
        for pattern in social_patterns:
            if re.search(pattern, query_lower):
                matched = pattern
                break
        if matched:
            # Strip every social phrase and see what is left. A word-count cap alone
            # is not enough: "hello, why did the backend fail on port 5557?" is short
            # and starts with a greeting, but the remainder is a real question.
            residual = query_lower
            for pattern in social_patterns:
                residual = re.sub(pattern, ' ', residual)
            residual = re.sub(r'[^a-z0-9\s]', ' ', residual)
            content = [w for w in residual.split() if w not in _social_filler]
            if len(content) <= 2:
                intent['is_social'] = True
                intent['patterns_matched'].append(f"social: {matched}")

    return intent

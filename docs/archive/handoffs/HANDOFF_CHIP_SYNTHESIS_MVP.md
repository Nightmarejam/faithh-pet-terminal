# Handoff: Chip Synthesis MVP Implementation

**Priority**: P1
**Owner**: FAITHH
**Agents**: [claude_code]
**Date**: 2026-01-01

---

## Objective

Implement the foundation for personalized chip synthesis:
1. PULSE pattern tracking system
2. Chip proposal mechanism
3. Personalized chip storage
4. One Program Advance as proof of concept

## Out of Scope (Phase 2)
- Federated learning
- Complex chip evolution/merging
- Full chip management UI
- Sensitive pattern filtering

---

## Files to Create/Modify

### New Files
- `pulse_pattern_tracker.py` - Pattern detection engine
- `personalized_chips.json` - User's learned chip library
- `chip_synthesis.py` - Chip creation and PA logic

### Modify
- `faithh_professional_backend_fixed.py` - Integrate PULSE + personalized chips

---

## Implementation

### Step 1: Create PULSE Pattern Tracker

Create `pulse_pattern_tracker.py`:
```python
"""
PULSE Pattern Tracker
Monitors user interactions to detect chip-worthy patterns
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

PATTERN_FILE = Path(__file__).parent / "pulse_patterns.json"
CHIP_LIBRARY_FILE = Path(__file__).parent / "personalized_chips.json"

# Thresholds
MIN_OCCURRENCES = 5  # Pattern must occur 5+ times
RECENCY_WINDOW_DAYS = 30  # Only consider recent patterns
PA_UNLOCK_THRESHOLD = 3  # Chip combo must occur 3+ times for PA

class PulsePatternTracker:
    def __init__(self):
        self.patterns = self._load_patterns()
        self.chip_library = self._load_chip_library()
    
    def _load_patterns(self):
        if PATTERN_FILE.exists():
            with open(PATTERN_FILE, 'r') as f:
                return json.load(f)
        return {
            "chip_sequences": [],  # Track chip combo sequences
            "topic_clusters": defaultdict(int),  # Track topic frequencies
            "time_patterns": defaultdict(list),  # Track time-based patterns
            "keyword_frequencies": defaultdict(int),
            "last_updated": None
        }
    
    def _save_patterns(self):
        self.patterns["last_updated"] = datetime.now().isoformat()
        with open(PATTERN_FILE, 'w') as f:
            json.dump(self.patterns, f, indent=2, default=str)
    
    def _load_chip_library(self):
        if CHIP_LIBRARY_FILE.exists():
            with open(CHIP_LIBRARY_FILE, 'r') as f:
                return json.load(f)
        return {
            "personalized_chips": [],
            "program_advances": [],
            "pending_proposals": [],
            "archived_chips": []
        }
    
    def _save_chip_library(self):
        with open(CHIP_LIBRARY_FILE, 'w') as f:
            json.dump(self.chip_library, f, indent=2)
    
    def record_interaction(self, query: str, chips_used: list, timestamp: datetime = None):
        """Record a user interaction for pattern analysis"""
        timestamp = timestamp or datetime.now()
        
        # Track chip sequences (for PA detection)
        if chips_used:
            self.patterns["chip_sequences"].append({
                "chips": chips_used,
                "timestamp": timestamp.isoformat(),
                "query_snippet": query[:100]
            })
        
        # Track time patterns
        hour = timestamp.hour
        time_bucket = "morning" if 5 <= hour < 12 else "afternoon" if 12 <= hour < 17 else "evening" if 17 <= hour < 21 else "night"
        self.patterns["time_patterns"][time_bucket].append({
            "chips": chips_used,
            "timestamp": timestamp.isoformat()
        })
        
        # Track keywords (simple frequency)
        keywords = self._extract_keywords(query)
        for kw in keywords:
            self.patterns["keyword_frequencies"][kw] += 1
        
        # Keep only recent data (rolling window)
        self._prune_old_data()
        self._save_patterns()
        
        # Check for new patterns
        return self._analyze_patterns()
    
    def _extract_keywords(self, query: str) -> list:
        """Extract meaningful keywords from query"""
        # Simple keyword extraction - could be enhanced with NLP
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'what', 'how', 'why', 'when', 'where', 'who', 'i', 'me', 'my', 'you', 'your', 'it', 'this', 'that', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'can', 'do', 'does', 'did', 'have', 'has', 'had'}
        words = query.lower().split()
        return [w for w in words if len(w) > 3 and w not in stopwords]
    
    def _prune_old_data(self):
        """Remove data older than RECENCY_WINDOW_DAYS"""
        cutoff = datetime.now() - timedelta(days=RECENCY_WINDOW_DAYS)
        cutoff_iso = cutoff.isoformat()
        
        self.patterns["chip_sequences"] = [
            seq for seq in self.patterns["chip_sequences"]
            if seq["timestamp"] > cutoff_iso
        ]
        
        for bucket in self.patterns["time_patterns"]:
            self.patterns["time_patterns"][bucket] = [
                entry for entry in self.patterns["time_patterns"][bucket]
                if entry["timestamp"] > cutoff_iso
            ]
    
    def _analyze_patterns(self) -> dict:
        """Analyze patterns and return any proposals"""
        proposals = {
            "new_chip_candidates": [],
            "pa_candidates": []
        }
        
        # Check for PA candidates (chip combos used together 3+ times)
        combo_counts = defaultdict(int)
        for seq in self.patterns["chip_sequences"]:
            chips = tuple(sorted(seq["chips"]))
            if len(chips) >= 2:
                combo_counts[chips] += 1
        
        for combo, count in combo_counts.items():
            if count >= PA_UNLOCK_THRESHOLD:
                # Check if PA already exists
                existing_pas = [pa["combination"] for pa in self.chip_library["program_advances"]]
                if list(combo) not in existing_pas:
                    proposals["pa_candidates"].append({
                        "combination": list(combo),
                        "times_used": count,
                        "suggested_name": self._generate_pa_name(combo)
                    })
        
        # Check for topic clusters (keywords used 5+ times)
        for keyword, count in self.patterns["keyword_frequencies"].items():
            if count >= MIN_OCCURRENCES:
                # Check if chip already exists for this topic
                existing_triggers = []
                for chip in self.chip_library["personalized_chips"]:
                    existing_triggers.extend(chip.get("triggers", {}).get("keywords", []))
                
                if keyword not in existing_triggers:
                    proposals["new_chip_candidates"].append({
                        "keyword": keyword,
                        "frequency": count,
                        "suggested_name": f"{keyword.title()} Focus"
                    })
        
        return proposals
    
    def _generate_pa_name(self, combo: tuple) -> str:
        """Generate a name for a Program Advance based on its chips"""
        pa_names = {
            ("decisions", "rag_search", "scaffolding"): "Project Historian",
            ("constella", "rag_search", "self_awareness"): "Framework Architect",
            ("project_state", "scaffolding"): "Status Commander",
            ("rag_search", "self_awareness"): "Knowledge Weaver"
        }
        sorted_combo = tuple(sorted(combo))
        return pa_names.get(sorted_combo, f"Combo: {' + '.join(combo)}")
    
    def propose_chip(self, name: str, description: str, triggers: dict, actions: dict) -> dict:
        """Create a chip proposal for user approval"""
        proposal = {
            "id": f"proposed_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "name": name,
            "description": description,
            "triggers": triggers,
            "actions": actions,
            "proposed_at": datetime.now().isoformat(),
            "status": "pending"
        }
        self.chip_library["pending_proposals"].append(proposal)
        self._save_chip_library()
        return proposal
    
    def approve_chip(self, proposal_id: str) -> dict:
        """User approves a chip proposal"""
        for i, proposal in enumerate(self.chip_library["pending_proposals"]):
            if proposal["id"] == proposal_id:
                approved_chip = {
                    **proposal,
                    "id": f"chip_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "status": "active",
                    "approved_at": datetime.now().isoformat(),
                    "times_used": 0,
                    "user_rating": None
                }
                self.chip_library["personalized_chips"].append(approved_chip)
                self.chip_library["pending_proposals"].pop(i)
                self._save_chip_library()
                return approved_chip
        return None
    
    def reject_chip(self, proposal_id: str) -> bool:
        """User rejects a chip proposal"""
        for i, proposal in enumerate(self.chip_library["pending_proposals"]):
            if proposal["id"] == proposal_id:
                self.chip_library["pending_proposals"].pop(i)
                self._save_chip_library()
                return True
        return False
    
    def unlock_program_advance(self, combination: list, name: str) -> dict:
        """Unlock a Program Advance"""
        pa = {
            "id": f"pa_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "name": name,
            "combination": combination,
            "unlocked_at": datetime.now().isoformat(),
            "times_used": 0,
            "level": 1
        }
        self.chip_library["program_advances"].append(pa)
        self._save_chip_library()
        return pa
    
    def get_active_personalized_chips(self) -> list:
        """Get all active personalized chips"""
        return [c for c in self.chip_library["personalized_chips"] if c["status"] == "active"]
    
    def get_program_advances(self) -> list:
        """Get all unlocked Program Advances"""
        return self.chip_library["program_advances"]
    
    def get_pending_proposals(self) -> list:
        """Get chips awaiting user approval"""
        return self.chip_library["pending_proposals"]


# Global instance
pulse_tracker = PulsePatternTracker()
```

### Step 2: Create API Endpoints

Add to `faithh_professional_backend_fixed.py` (near other routes):
```python
from pulse_pattern_tracker import pulse_tracker

@app.route('/api/pulse/status', methods=['GET'])
def pulse_status():
    """Get PULSE learning status"""
    return jsonify({
        "active_chips": len(pulse_tracker.get_active_personalized_chips()),
        "program_advances": len(pulse_tracker.get_program_advances()),
        "pending_proposals": len(pulse_tracker.get_pending_proposals()),
        "patterns_tracked": len(pulse_tracker.patterns.get("chip_sequences", []))
    })

@app.route('/api/pulse/proposals', methods=['GET'])
def get_proposals():
    """Get pending chip proposals"""
    return jsonify({
        "proposals": pulse_tracker.get_pending_proposals()
    })

@app.route('/api/pulse/approve', methods=['POST'])
def approve_proposal():
    """Approve a chip proposal"""
    data = request.json
    proposal_id = data.get('proposal_id')
    result = pulse_tracker.approve_chip(proposal_id)
    if result:
        return jsonify({"success": True, "chip": result})
    return jsonify({"success": False, "error": "Proposal not found"}), 404

@app.route('/api/pulse/reject', methods=['POST'])
def reject_proposal():
    """Reject a chip proposal"""
    data = request.json
    proposal_id = data.get('proposal_id')
    result = pulse_tracker.reject_chip(proposal_id)
    return jsonify({"success": result})

@app.route('/api/pulse/chips', methods=['GET'])
def get_personalized_chips():
    """Get user's personalized chip library"""
    return jsonify({
        "personalized_chips": pulse_tracker.get_active_personalized_chips(),
        "program_advances": pulse_tracker.get_program_advances()
    })
```

### Step 3: Integrate PULSE into Chat Flow

Modify the `/api/chat` endpoint to record interactions:

Find the section after successful response generation and add:
```python
# Record interaction for PULSE pattern learning
try:
    from pulse_pattern_tracker import pulse_tracker
    proposals = pulse_tracker.record_interaction(
        query=message,
        chips_used=integrations_used,
        timestamp=datetime.now()
    )
    
    # Check for PA unlocks
    if proposals.get("pa_candidates"):
        for pa in proposals["pa_candidates"]:
            # Auto-unlock first PA as proof of concept
            if pa["combination"] == ["decisions", "rag_search", "scaffolding"]:
                pulse_tracker.unlock_program_advance(
                    combination=pa["combination"],
                    name="Project Historian"
                )
                # Add PA notification to response
                response_data["pa_unlocked"] = {
                    "name": "Project Historian",
                    "message": "🎉 Program Advance Unlocked! By combining RAG, Decisions, and Scaffolding, you've unlocked Project Historian - I can now generate project evolution narratives!"
                }
except Exception as e:
    print(f"PULSE tracking error: {e}")
```

### Step 4: Initialize Empty Chip Library

Create `personalized_chips.json`:
```json
{
  "personalized_chips": [],
  "program_advances": [],
  "pending_proposals": [],
  "archived_chips": []
}
```

Create `pulse_patterns.json`:
```json
{
  "chip_sequences": [],
  "topic_clusters": {},
  "time_patterns": {},
  "keyword_frequencies": {},
  "last_updated": null
}
```

---

## Testing

### Test 1: Verify PULSE Status Endpoint
```bash
curl http://localhost:5557/api/pulse/status | jq .
```

Expected:
```json
{
  "active_chips": 0,
  "program_advances": 0,
  "pending_proposals": 0,
  "patterns_tracked": 0
}
```

### Test 2: Send Multiple Queries to Build Patterns
```bash
# Send 5+ queries that trigger similar chips
for i in {1..5}; do
  curl -s -X POST http://localhost:5557/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "What decisions did we make about the project?", "model": "llama3.1:8b"}'
  sleep 2
done
```

### Test 3: Check Pattern Detection
```bash
cat ~/ai-stack/pulse_patterns.json | jq '.chip_sequences | length'
```

### Test 4: Trigger PA Unlock (Project Historian)
```bash
# Query that triggers RAG + Decisions + Scaffolding together
curl -s -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the history of FAITHH project and what decisions shaped it?", "model": "llama3.1:8b"}' | jq '.pa_unlocked'
```

---

## Acceptance Criteria

- [ ] `pulse_pattern_tracker.py` created and imports without errors
- [ ] `/api/pulse/status` returns valid JSON
- [ ] Interactions are recorded in `pulse_patterns.json`
- [ ] Chip sequences track which chips fire together
- [ ] PA detection works when combo threshold reached
- [ ] "Project Historian" PA can be unlocked
- [ ] No errors in normal chat flow

---

## Rollback

Delete the new files and remove PULSE-related code from backend:
```bash
rm ~/ai-stack/pulse_pattern_tracker.py
rm ~/ai-stack/pulse_patterns.json
rm ~/ai-stack/personalized_chips.json
```

---

## Next Phase (Not This Handoff)

- UI for viewing/managing personalized chips
- Chip proposal notifications in chat
- More PA combinations
- Time-based chip triggers (Morning Briefing)
- Keyword clustering for topic-based chips

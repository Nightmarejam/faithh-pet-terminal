# 🎴 FAITHH Battle Chip System - Complete Design

## Vision: Chips as Agentic Tools

Battle Chips are modular AI tools that can work independently or chain together to create powerful agentic workflows.

---

## 🎮 User Interaction Flow

### 1. Browsing Chips
```
User clicks "CHIPS" tab
↓
Sees library of available chips
↓
Each chip shows: Icon, Name, Code, Description
```

### 2. Equipping Chips
```
User clicks chip in library
↓
Chip moves to first empty slot in top bar
↓
System checks for combos
↓
User can equip up to 5 chips
```

### 3. Managing Chips
```
Hover over active chip → X button appears
↓
Click X → Chip removed, slot becomes empty
↓
OR click "CLEAR ALL" → All chips removed
```

### 4. Executing Chips

**Option A: Execute All**
```
User clicks "EXECUTE" button
↓
All equipped chips run in sequence
↓
Each chip removed after execution
↓
Results displayed in chat
```

**Option B: Selective Execution**
```
User clicks chips to select (yellow border)
↓
User clicks "EXECUTE"
↓
Only selected chips run
↓
Selected chips removed
```

### 5. Agentic Workflow
```
User equips: RAG + Code Gen + Debug
↓
Clicks EXECUTE
↓
Agent workflow activates:
  1. RAG searches for similar code
  2. Code Gen uses RAG results as context
  3. Debug validates the output
↓
Final result returned
```

---

## 🔧 Technical Architecture

### Frontend (UI)

**Chip Slot Management:**
```javascript
activeChipSlots = [null, null, null, null, null]
selectedChips = Set()  // Indices of selected chips

equipChip(chip) {
  // Find first empty slot
  // Add chip to slot
  // Update UI
  // Check for combos
}

removeChip(slotIndex) {
  // Remove from slot
  // Clear selection
  // Update UI
}

executeChips() {
  // Get selected chips (or all if none selected)
  // Call backend API
  // Remove executed chips
  // Display results
}
```

**Combo Detection:**
```javascript
checkForCombos() {
  // Count matching code letters
  // If 3+ match: display combo bonus
  // Apply combo effects (faster, better results)
}
```

### Backend (API)

**Endpoint: POST /api/chip/execute**
```python
Input: {
  "chips": [
    {"id": "rag_query", "params": {"query": "user input"}},
    {"id": "code_gen", "params": {"context": "from_previous"}},
    {"id": "debug", "params": {"code": "from_previous"}}
  ],
  "mode": "sequence" | "parallel" | "conditional"
}

Output: {
  "results": [
    {"chip": "rag_query", "output": {...}},
    {"chip": "code_gen", "output": {...}},
    {"chip": "debug", "output": {...}}
  ],
  "final_result": "Combined output",
  "execution_time": 2.5,
  "combo_bonus": true
}
```

**Chip Execution Engine:**
```python
class ChipExecutor:
    def execute_chip(self, chip_id, params, context=None):
        """Execute a single chip"""
        chip_class = self.chip_registry[chip_id]
        chip_instance = chip_class()
        return chip_instance.run(params, context)
    
    def execute_workflow(self, chips, mode="sequence"):
        """Execute multiple chips with workflow logic"""
        results = []
        context = {}
        
        for chip_config in chips:
            result = self.execute_chip(
                chip_config['id'],
                chip_config['params'],
                context
            )
            results.append(result)
            context.update(result)  # Pass output to next chip
        
        return self.combine_results(results)
```

---

## 📦 Chip Types & Categories

### 1. RAG/Knowledge Chips (Green)
**Purpose:** Search and retrieve information

- **RAG Query** (Code: R)
  - Input: Search term
  - Output: Relevant documents
  - Agent use: Provide context for other chips

- **Semantic Search** (Code: S)
  - Input: Natural language question
  - Output: Best matching answers
  - Agent use: Find specific information

- **Context Builder** (Code: C)
  - Input: Topic
  - Output: Comprehensive context package
  - Agent use: Gather all relevant info

### 2. Code Chips (Blue)
**Purpose:** Generate, analyze, and modify code

- **Code Generator** (Code: C)
  - Input: Description + context
  - Output: Code snippet
  - Agent use: Generate code based on requirements

- **Debugger** (Code: D)
  - Input: Code + error
  - Output: Fixed code
  - Agent use: Validate and fix generated code

- **Optimizer** (Code: O)
  - Input: Code
  - Output: Optimized version
  - Agent use: Improve performance

- **Test Generator** (Code: T)
  - Input: Code
  - Output: Unit tests
  - Agent use: Ensure code quality

### 3. Civic/Document Chips (Purple)
**Purpose:** Write and manage civic documents

- **Civic Writer** (Code: C)
  - Input: Topic + context
  - Output: Document draft
  - Agent use: Create civic framework docs

- **Editor** (Code: E)
  - Input: Document + feedback
  - Output: Revised document
  - Agent use: Improve existing documents

- **Summarizer** (Code: S)
  - Input: Long document
  - Output: Concise summary
  - Agent use: Distill key points

### 4. Analysis Chips (Yellow)
**Purpose:** Analyze data and patterns

- **Data Analyzer** (Code: A)
  - Input: Dataset
  - Output: Insights
  - Agent use: Extract meaningful patterns

- **Sentiment Analyzer** (Code: S)
  - Input: Text
  - Output: Sentiment score
  - Agent use: Gauge tone and emotion

- **Trend Detector** (Code: T)
  - Input: Time series data
  - Output: Trends and predictions
  - Agent use: Identify patterns over time

### 5. System/Utility Chips (Red)
**Purpose:** System operations and monitoring

- **PULSE Check** (Code: P)
  - Input: None
  - Output: System health report
  - Agent use: Verify system before operations

- **Log Analyzer** (Code: L)
  - Input: Log file path
  - Output: Error summary
  - Agent use: Diagnose issues

- **Backup** (Code: B)
  - Input: Data to backup
  - Output: Backup confirmation
  - Agent use: Preserve important data

### 6. Communication Chips (Orange)
**Purpose:** External interactions

- **Web Search** (Code: W)
  - Input: Search query
  - Output: Web results
  - Agent use: Gather external information

- **Translator** (Code: T)
  - Input: Text + target language
  - Output: Translated text
  - Agent use: Multilingual support

- **API Caller** (Code: A)
  - Input: API endpoint + params
  - Output: API response
  - Agent use: Interact with external services

---

## 🔗 Agentic Workflow Examples

### Workflow 1: Smart Code Generation
```
Chips: RAG Query → Code Gen → Debugger → Test Gen

Step 1 (RAG): Search for "similar authentication code"
  → Returns 3 examples from conversation history

Step 2 (Code Gen): "Create auth function based on examples"
  → Uses RAG results as context
  → Generates authentication function

Step 3 (Debugger): Validate generated code
  → Checks for common errors
  → Fixes syntax issues

Step 4 (Test Gen): Create tests for auth function
  → Generates unit tests
  → Returns complete, tested code

Final Output: Production-ready authenticated code with tests
```

### Workflow 2: Civic Document Creation
```
Chips: Context Builder → Civic Writer → Summarizer → Editor

Step 1 (Context): Gather info on "community voting systems"
  → Pulls relevant civic framework docs
  → Collects best practices

Step 2 (Civic Writer): Draft voting system proposal
  → Uses context to write comprehensive doc
  → Follows civic framework format

Step 3 (Summarizer): Create executive summary
  → Distills key points
  → Creates one-page overview

Step 4 (Editor): Polish and refine
  → Improves clarity
  → Fixes grammar and structure

Final Output: Professional civic proposal with executive summary
```

### Workflow 3: Bug Diagnosis & Fix
```
Chips: Log Analyzer → RAG Query → Debugger → Test Gen

Step 1 (Log Analyzer): Analyze error logs
  → Identifies error patterns
  → Extracts stack traces

Step 2 (RAG Query): Search for "similar errors fixed"
  → Finds solutions from past conversations
  → Returns fix strategies

Step 3 (Debugger): Apply fixes
  → Implements solution
  → Validates fix works

Step 4 (Test Gen): Create regression tests
  → Ensures bug doesn't return
  → Adds to test suite

Final Output: Fixed code with tests to prevent recurrence
```

### Workflow 4: Research & Analysis
```
Chips: Web Search → RAG Query → Analyzer → Summarizer

Step 1 (Web Search): Find current info on topic
  → Searches web for latest data
  → Returns recent articles

Step 2 (RAG Query): Find internal knowledge
  → Searches your conversation history
  → Combines with web results

Step 3 (Analyzer): Analyze combined data
  → Identifies patterns and insights
  → Extracts key findings

Step 4 (Summarizer): Create report
  → Comprehensive summary
  → Actionable recommendations

Final Output: Research report with external and internal sources
```

---

## 🎯 Combo System

### Combo Mechanics

**3-Chip Combo (Same Code):**
- Effect: +25% execution speed
- Visual: Slots glow yellow
- Example: C+C+C (Code, Civic, Context all "C")

**4-Chip Combo:**
- Effect: +50% speed, better results
- Visual: Slots glow orange
- Example: R+R+R+R (RAG chips)

**5-Chip Combo (All Same):**
- Effect: +100% speed, premium results, bonus features
- Visual: Slots glow rainbow
- Example: T+T+T+T+T (All translation/test/trend chips)

### Special Combos

**Synergy Combos (Specific Combinations):**

1. **"Developer's Dream"** (C+D+T+O)
   - Code Gen + Debug + Test + Optimize
   - Bonus: Fully production-ready code
   - Effect: Includes documentation

2. **"Civic Catalyst"** (C+E+S+R)
   - Civic Writer + Editor + Summarizer + RAG
   - Bonus: Multi-version document package
   - Effect: Draft + polished + summary versions

3. **"Deep Researcher"** (R+W+A+S)
   - RAG + Web Search + Analyzer + Summarizer
   - Bonus: Comprehensive research report
   - Effect: Cites all sources

4. **"System Sentinel"** (P+L+B+D)
   - PULSE Check + Log Analyzer + Backup + Debug
   - Bonus: Full system health + fixes
   - Effect: Auto-fixes critical issues

---

## 💾 Backend Implementation Guide

### 1. Chip Base Class

```python
# chips/base_chip.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BattleChip(ABC):
    """Base class for all battle chips"""
    
    def __init__(self):
        self.id: str = ""
        self.name: str = ""
        self.code: str = ""
        self.color: str = ""
        self.description: str = ""
    
    @abstractmethod
    async def execute(
        self, 
        params: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the chip's function
        
        Args:
            params: Chip-specific parameters
            context: Output from previous chips in workflow
            
        Returns:
            Result dictionary with output and metadata
        """
        pass
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate input parameters"""
        return True
    
    def sanitize_input(self, text: str) -> str:
        """Sanitize user input for security"""
        # Remove dangerous characters, SQL injection attempts, etc.
        return text.strip()
```

### 2. Example Chip Implementation

```python
# chips/rag_query_chip.py
from chips.base_chip import BattleChip
import chromadb

class RAGQueryChip(BattleChip):
    def __init__(self):
        super().__init__()
        self.id = "rag_query"
        self.name = "RAG QUERY"
        self.code = "R"
        self.color = "green"
        self.description = "Search knowledge base"
        self.client = chromadb.Client()
        self.collection = self.client.get_collection("conversations")
    
    async def execute(self, params, context=None):
        query = self.sanitize_input(params.get('query', ''))
        limit = params.get('limit', 5)
        
        if not query:
            return {
                'success': False,
                'error': 'Query cannot be empty',
                'output': None
            }
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            return {
                'success': True,
                'output': results,
                'metadata': {
                    'query': query,
                    'results_count': len(results['documents'][0])
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'output': None
            }
```

### 3. Chip Registry

```python
# chips/registry.py
from chips.rag_query_chip import RAGQueryChip
from chips.code_gen_chip import CodeGenChip
# ... import all chips

class ChipRegistry:
    def __init__(self):
        self.chips = {
            'rag_query': RAGQueryChip(),
            'code_gen': CodeGenChip(),
            # ... register all chips
        }
    
    def get_chip(self, chip_id: str):
        return self.chips.get(chip_id)
    
    def list_chips(self):
        return [
            {
                'id': chip.id,
                'name': chip.name,
                'code': chip.code,
                'color': chip.color,
                'description': chip.description
            }
            for chip in self.chips.values()
        ]
```

### 4. Workflow Executor

```python
# chips/executor.py
from chips.registry import ChipRegistry
from typing import List, Dict, Any

class ChipExecutor:
    def __init__(self):
        self.registry = ChipRegistry()
    
    async def execute_workflow(
        self, 
        chips: List[Dict[str, Any]], 
        mode: str = "sequence"
    ) -> Dict[str, Any]:
        """
        Execute multiple chips in a workflow
        
        Args:
            chips: List of chip configs with id and params
            mode: "sequence" | "parallel" | "conditional"
        """
        
        if mode == "sequence":
            return await self._execute_sequence(chips)
        elif mode == "parallel":
            return await self._execute_parallel(chips)
        else:
            return await self._execute_conditional(chips)
    
    async def _execute_sequence(self, chips):
        """Execute chips one after another, passing context"""
        results = []
        context = {}
        
        for chip_config in chips:
            chip = self.registry.get_chip(chip_config['id'])
            
            if not chip:
                results.append({
                    'success': False,
                    'error': f"Chip {chip_config['id']} not found"
                })
                continue
            
            # Execute chip with accumulated context
            result = await chip.execute(
                chip_config.get('params', {}),
                context
            )
            
            results.append(result)
            
            # Add output to context for next chip
            if result['success']:
                context[chip.id] = result['output']
        
        return {
            'results': results,
            'final_context': context,
            'success': all(r['success'] for r in results)
        }
    
    async def _execute_parallel(self, chips):
        """Execute all chips simultaneously"""
        import asyncio
        
        tasks = []
        for chip_config in chips:
            chip = self.registry.get_chip(chip_config['id'])
            if chip:
                task = chip.execute(chip_config.get('params', {}))
                tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        return {
            'results': results,
            'success': all(r['success'] for r in results)
        }
    
    def detect_combo(self, chips: List[Dict]) -> Dict[str, Any]:
        """Detect chip combos for bonuses"""
        codes = [c.get('code', '') for c in chips]
        code_counts = {}
        
        for code in codes:
            code_counts[code] = code_counts.get(code, 0) + 1
        
        max_combo = max(code_counts.values()) if code_counts else 0
        
        if max_combo >= 3:
            combo_code = [k for k, v in code_counts.items() if v == max_combo][0]
            return {
                'active': True,
                'code': combo_code,
                'count': max_combo,
                'bonus': 0.25 * (max_combo - 2)  # 25% per chip above 2
            }
        
        return {'active': False, 'bonus': 0}
```

### 5. API Endpoint

```python
# faithh_api.py (add this endpoint)
from chips.executor import ChipExecutor

chip_executor = ChipExecutor()

@app.route('/api/chip/execute', methods=['POST'])
async def execute_chips():
    """Execute battle chips"""
    data = request.json
    chips = data.get('chips', [])
    mode = data.get('mode', 'sequence')
    
    if not chips:
        return jsonify({'error': 'No chips provided'}), 400
    
    try:
        # Detect combo bonuses
        combo = chip_executor.detect_combo(chips)
        
        # Execute workflow
        result = await chip_executor.execute_workflow(chips, mode)
        
        # Apply combo bonuses if applicable
        if combo['active']:
            result['combo'] = combo
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chip/list', methods=['GET'])
def list_chips():
    """List all available chips"""
    return jsonify({
        'chips': chip_executor.registry.list_chips()
    })
```

---

## 🚀 Implementation Roadmap

### Phase 1: Basic Chip Execution (Week 1)
- [ ] Create base chip class
- [ ] Implement chip registry
- [ ] Build simple executor (sequence mode only)
- [ ] Create 3-5 basic chips (RAG, Code Gen, Debug)
- [ ] Add `/api/chip/execute` endpoint
- [ ] Test individual chip execution

### Phase 2: Workflow System (Week 2)
- [ ] Implement context passing between chips
- [ ] Add parallel execution mode
- [ ] Build combo detection system
- [ ] Create visual feedback for combos
- [ ] Test multi-chip workflows

### Phase 3: Advanced Features (Week 3)
- [ ] Conditional execution logic
- [ ] Chip parameter validation
- [ ] Input sanitization
- [ ] Error recovery mechanisms
- [ ] Performance optimization

### Phase 4: Polish & Documentation (Week 4)
- [ ] Add all 12 chip types
- [ ] Create chip creation guide
- [ ] Write comprehensive tests
- [ ] Document all workflows
- [ ] User testing & feedback

---

## 🎨 UI/UX Enhancements

### Visual Feedback
- **Equipping:** Slide animation from library to slot
- **Executing:** Pulsing glow on active chips
- **Combo:** Rainbow shimmer effect
- **Completion:** Success checkmark animation
- **Error:** Red flash + shake

### Sound Effects (Optional)
- Chip equip: "Click" sound
- Chip execute: "Whoosh" sound
- Combo: Special jingle
- Success: Triumphant beep
- Error: Buzzer sound

### Accessibility
- Keyboard shortcuts (1-5 for chip slots)
- Screen reader support
- High contrast mode
- Reduced motion option

---

## 📊 Metrics & Analytics

### Track These Metrics:
- Chip usage frequency
- Popular chip combinations
- Workflow success rates
- Average execution time
- Error rates per chip
- Combo activation frequency

### Dashboard Ideas:
- "Most Used Chips" chart
- "Successful Workflows" list
- "Execution Time" graphs
- "Error Hotspots" heatmap

---

## 🔐 Security Considerations

### Input Validation
- Sanitize all user text input
- Validate chip parameters
- Limit query sizes
- Rate limit executions

### Access Control
- Per-user chip libraries
- Permission-based chip access
- Audit logging
- Execution quotas

### Data Protection
- Encrypt sensitive chip parameters
- Secure API key storage
- Safe handling of code execution
- Sandboxed chip environments

---

## 🤝 Handoff to Gemini

When ready to implement, use this prompt:

```
Hi FAITHH! Ready to implement the battle chip execution system.

CONTEXT:
- Full design doc: ~/ai-stack/BATTLE_CHIP_DESIGN.md
- Current UI: ~/ai-stack/faithh_pet_v3.html (chips ready)
- Backend: ~/ai-stack/faithh_api.py (needs chip executor)

TASK: Implement Phase 1 - Basic Chip Execution

REQUIREMENTS:
1. Create chips/ directory structure
2. Implement BattleChip base class
3. Create ChipRegistry
4. Build ChipExecutor (sequence mode)
5. Implement 3 chips: RAG Query, Code Gen, PULSE Check
6. Add /api/chip/execute endpoint
7. Include error handling and input validation
8. Add unit tests

START WITH: chips/base_chip.py

Ready to begin?
```

---

**End of Battle Chip System Design Document**

*This is a living document - update as the system evolves!*
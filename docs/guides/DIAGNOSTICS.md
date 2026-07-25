# Claude Code Final Cleanup & Diagnostic Tasks
## Run Before: January 4, 2025
## Purpose: Leave FAITHH in pristine state before reduced Claude usage

---

# TASK OVERVIEW

Run these tasks in order. Each section is independent but builds context.

**Estimated Time:** 2-3 hours total
**Priority:** Complete Tasks 1-3 minimum, 4-6 if time permits

---

# TASK 1: FAITHH Health Diagnostic
**Priority:** 🔴 CRITICAL
**Time:** 30 min

## 1.1 ChromaDB Integrity Check

```bash
# Navigate to FAITHH directory
cd ~/ai-stack

# Check ChromaDB collection stats
python3 << 'EOF'
import chromadb
from chromadb.config import Settings

# Adjust path as needed
client = chromadb.PersistentClient(path="./chroma_db")

# List all collections
collections = client.list_collections()
print(f"Total collections: {len(collections)}")

for col in collections:
    print(f"\nCollection: {col.name}")
    print(f"  Count: {col.count()}")

    # Sample a few to check embedding dimensions
    sample = col.peek(limit=3)
    if sample['embeddings']:
        print(f"  Embedding dim: {len(sample['embeddings'][0])}")
    else:
        print("  WARNING: No embeddings found!")
EOF
```

**Expected:** 91,000+ documents, consistent embedding dimensions
**If Issues:** Note dimension mismatches for manual review

## 1.2 API Connection Test

```bash
# Test Ollama connection
curl http://localhost:11434/api/tags

# Test Gemini API (if configured)
python3 << 'EOF'
import os
import google.generativeai as genai

api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
if api_key:
    genai.configure(api_key=api_key)
    models = genai.list_models()
    print(f"Gemini API connected. Models available: {len(list(models))}")
else:
    print("WARNING: No Gemini API key found")
EOF

# Test Groq (if configured)
python3 << 'EOF'
import os
groq_key = os.getenv('GROQ_API_KEY')
if groq_key:
    print(f"Groq API key found: {groq_key[:8]}...")
else:
    print("INFO: Groq not configured yet (planned feature)")
EOF
```

## 1.3 GPU Status Check

```bash
# Check NVIDIA GPUs
nvidia-smi --query-gpu=name,memory.total,memory.used,temperature.gpu --format=csv

# Verify CUDA availability
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'Devices: {torch.cuda.device_count()}')"
```

**Expected:** RTX 3090 + GTX 1080 Ti both visible

---

# TASK 2: Code Audit for Dated Passages
**Priority:** 🟡 HIGH
**Time:** 45 min

## 2.1 Search for Hardcoded Dates

```bash
cd ~/ai-stack

# Find files with hardcoded 2024 dates that might be stale
grep -rn "2024" --include="*.py" --include="*.js" --include="*.ts" --include="*.md" . | grep -v node_modules | grep -v __pycache__ | grep -v ".git"

# Find TODO/FIXME comments
grep -rn -E "(TODO|FIXME|HACK|XXX)" --include="*.py" --include="*.js" --include="*.ts" . | grep -v node_modules | head -50
```

## 2.2 Check for Deprecated Patterns

```bash
# Python: Check for deprecated imports/patterns
grep -rn "from collections import " --include="*.py" . | grep -v node_modules
# (collections.abc should be used instead of collections for Mapping, etc.)

# Check for old-style string formatting
grep -rn "% s" --include="*.py" . | grep -v node_modules | head -20

# Check for print statements without parentheses (Python 2 remnants)
grep -rn "print [^(]" --include="*.py" . | grep -v node_modules
```

## 2.3 Dependencies Audit

```bash
cd ~/ai-stack

# Check Python dependencies for outdated packages
pip list --outdated 2>/dev/null | head -20

# Check for security vulnerabilities (if pip-audit installed)
pip-audit 2>/dev/null || echo "pip-audit not installed - consider adding"

# Node dependencies (if applicable)
cd frontend 2>/dev/null && npm audit 2>/dev/null || echo "No npm project or npm not available"
```

**Action Items:** Create list of files needing updates, prioritize security issues

---

# TASK 3: Parity File Updates
**Priority:** 🟡 HIGH
**Time:** 30 min

## 3.1 Identify Documentation Files

```bash
cd ~/ai-stack

# Find all markdown documentation
find . -name "*.md" -type f | grep -v node_modules | grep -v ".git" | sort

# Find README files
find . -name "README*" -type f | grep -v node_modules

# Find config/env examples
find . -name "*.example" -o -name "*.sample" -o -name ".env*" | grep -v node_modules
```

## 3.2 Check Doc-Code Parity

For each major doc file, verify it matches current implementation:

```bash
cd ~/ai-stack

# List key documentation files to review
echo "=== DOCUMENTATION PARITY CHECKLIST ==="
echo ""
echo "Review these files and compare to actual implementation:"
echo ""

for doc in README.md ARCHITECTURE.md SETUP.md CONTRIBUTING.md API.md; do
    if [ -f "$doc" ]; then
        echo "✓ $doc exists - REVIEW NEEDED"
        echo "  Last modified: $(stat -c %y "$doc" 2>/dev/null || stat -f %Sm "$doc" 2>/dev/null)"
    fi
done

# Check for handoff docs
find . -name "*HANDOFF*" -o -name "*handoff*" | grep -v node_modules
```

## 3.3 Update Version References

```bash
cd ~/ai-stack

# Find version strings that might need updating
grep -rn "version" --include="*.json" --include="*.toml" --include="*.yaml" . | grep -v node_modules | head -20

# Check package.json version
cat package.json 2>/dev/null | grep '"version"' || echo "No package.json"

# Check pyproject.toml version
cat pyproject.toml 2>/dev/null | grep "version" | head -5 || echo "No pyproject.toml"
```

---

# TASK 4: FAITHH Chip System Validation
**Priority:** 🟢 MEDIUM
**Time:** 30 min

## 4.1 Verify Chip Definitions

```bash
cd ~/ai-stack

# Find chip definition files
find . -name "*chip*" -type f | grep -v node_modules | grep -v __pycache__

# Check chip registry/configuration
cat chips/registry.json 2>/dev/null || cat config/chips.json 2>/dev/null || echo "Locate chip config manually"
```

## 4.2 Test Chip Selection Logic

```python
# Run in FAITHH environment
# Test that chips auto-select correctly

test_queries = [
    ("What files do I have about taxes?", ["RAG Search"]),
    ("Help me decide between two options", ["Decisions"]),
    ("What's the status of my project?", ["Scaffolding"]),
    ("Search my conversation history", ["RAG Search"]),
]

for query, expected_chips in test_queries:
    # Call your chip selection function
    # selected = select_chips(query)
    # assert set(expected_chips).issubset(set(selected)), f"Failed for: {query}"
    print(f"TEST: '{query[:40]}...' -> Expected: {expected_chips}")
```

## 4.3 Verify Parallel Chip Retrieval

```bash
cd ~/ai-stack

# Check that parallel retrieval is implemented
grep -rn "asyncio\|async def\|await\|ThreadPool\|concurrent" --include="*.py" . | grep -v node_modules | grep -i chip
```

## 4.4 PULSE Pattern Tracker Status (Added Jan 2026)

```bash
cd ~/ai-stack

# Check PULSE endpoints
curl -s http://localhost:5557/api/pulse/status | python3 -m json.tool

# Verify PULSE files exist
ls -lh pulse_pattern_tracker.py pulse_patterns.json personalized_chips.json

# Check for any Program Advances unlocked
cat personalized_chips.json | python3 -m json.tool
```

---

# TASK 5: Network & Storage Validation
**Priority:** 🟢 MEDIUM
**Time:** 20 min

## 5.1 Tailscale Status

```bash
# Check Tailscale connection
tailscale status

# Verify all 6 devices visible
tailscale status | wc -l
```

## 5.2 NAS Accessibility

```bash
# Check NAS mount points
df -h | grep -i nas

# Verify key folders exist
for folder in Personal Audio Backups Archive AI; do
    if [ -d "/path/to/nas/$folder" ]; then
        echo "✓ $folder folder exists"
    else
        echo "✗ $folder folder MISSING"
    fi
done
```

## 5.3 Storage Health

```bash
# Check disk usage
df -h

# Check for large files that might be cleaned up
find ~/ai-stack -type f -size +100M | grep -v node_modules | head -10
```

---

# TASK 6: Create System State Snapshot
**Priority:** 🟢 MEDIUM
**Time:** 15 min

## 6.1 Generate State Report

```bash
cd ~/ai-stack

# Create a state snapshot for future reference
mkdir -p ./snapshots

cat << EOF > ./snapshots/system_state_$(date +%Y%m%d).md
# FAITHH System State Snapshot
## Generated: $(date)

### Environment
- Python: $(python3 --version)
- Node: $(node --version 2>/dev/null || echo "N/A")
- CUDA: $(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1 || echo "N/A")

### ChromaDB
- Collections: [RUN TASK 1.1 TO FILL]
- Document Count: [RUN TASK 1.1 TO FILL]

### APIs
- Ollama: [RUN TASK 1.2 TO FILL]
- Gemini: [RUN TASK 1.2 TO FILL]
- Groq: Not yet configured

### GPUs
[RUN TASK 1.3 TO FILL]

### PULSE Pattern Tracker
- Status: [RUN TASK 4.4 TO FILL]
- Patterns tracked: [FROM PULSE STATUS]
- Program Advances: [FROM PULSE STATUS]

### Outstanding Issues
[FILL FROM AUDIT RESULTS]

### Next Actions
[FILL BASED ON FINDINGS]
EOF

echo "State snapshot template created at ./snapshots/"
```

---

# POST-DIAGNOSTIC ACTIONS

## If Issues Found:

### Critical (Fix Immediately):
- [ ] Embedding dimension mismatches
- [ ] API connection failures
- [ ] GPU not detected
- [ ] Security vulnerabilities in dependencies

### High (Fix Before Handoff):
- [ ] Outdated documentation
- [ ] Deprecated code patterns
- [ ] Stale hardcoded dates

### Medium (Note for Future):
- [ ] Minor TODOs in code
- [ ] Optimization opportunities
- [ ] Nice-to-have cleanups

---

# COMPLETION CHECKLIST

```
[ ] Task 1: FAITHH Health Diagnostic - COMPLETE
    [ ] 1.1 ChromaDB integrity verified
    [ ] 1.2 API connections tested
    [ ] 1.3 GPU status confirmed

[ ] Task 2: Code Audit - COMPLETE
    [ ] 2.1 Dated passages identified
    [ ] 2.2 Deprecated patterns flagged
    [ ] 2.3 Dependencies audited

[ ] Task 3: Parity Files - COMPLETE
    [ ] 3.1 Documentation inventory done
    [ ] 3.2 Doc-code parity checked
    [ ] 3.3 Versions updated

[ ] Task 4: Chip System - COMPLETE (if time)
    [ ] 4.1 Chip definitions verified
    [ ] 4.2 Selection logic tested
    [ ] 4.3 Parallel retrieval confirmed
    [ ] 4.4 PULSE status checked

[ ] Task 5: Network/Storage - COMPLETE (if time)
    [ ] 5.1 Tailscale connected
    [ ] 5.2 NAS accessible
    [ ] 5.3 Storage healthy

[ ] Task 6: State Snapshot - COMPLETE (if time)
    [ ] Snapshot generated and saved
```

---

# NOTES FOR CLAUDE CODE

- Adjusted paths to ~/ai-stack for Jonathan's directory structure
- Some commands assume macOS (based on stat -f flag)
- ChromaDB is accessed via HTTP client at http://servicebox.taileb8c60.ts.net:8000
- GPU commands assume NVIDIA - should work with RTX 3090 + 1080 Ti setup
- Tailscale should show ~6 devices if network is healthy
- PULSE pattern tracker added as of Jan 2026 - check Task 4.4

---

**Created:** January 3, 2025
**Updated:** January 2, 2026 (Added PULSE checks)
**Purpose:** Final system cleanup before reduced Claude usage
**Author:** Claude (Opus 4.5)

*Leave FAITHH better than you found it.* 🛠️

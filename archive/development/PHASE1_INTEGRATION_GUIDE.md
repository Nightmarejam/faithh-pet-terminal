# Phase 1: Conversation Memory - Integration Guide

**Status**: Ready to integrate  
**Time**: 30-45 minutes  
**Difficulty**: Medium (requires careful code insertion)

---

## 🎯 What Phase 1 Adds

**Conversation Memory** - FAITHH remembers your conversation and can handle follow-up questions.

**Before Phase 1**:
```
You: "What is the Penumbra Accord?"
FAITHH: [explains restorative justice framework]

You: "How does tie-breaking work in that?"
FAITHH: [doesn't know "that" refers to Penumbra - no context]
```

**After Phase 1**:
```
You: "What is the Penumbra Accord?"
FAITHH: [explains restorative justice framework]

You: "How does tie-breaking work in that?"
FAITHH: [remembers context, explains Penumbra tie-breaking specifically]
```

---

## 📋 Step-by-Step Integration

### Step 1: Backup Current Backend

```bash
cd ~/ai-stack
cp faithh_professional_backend_fixed.py faithh_professional_backend_fixed.py.backup_pre_phase1
```

### Step 2: Open Backend and Reference File

```bash
# Open backend in your editor
code faithh_professional_backend_fixed.py

# Keep phase1_conversation_memory.py open for reference
code phase1_conversation_memory.py
```

### Step 3: Add Conversation Memory Functions

**Location**: Find the line with `CURRENT_MODEL = {"name": "unknown"...}` (around line 74)

**Action**: RIGHT AFTER that line, add ALL the code from **SECTION 1** of `phase1_conversation_memory.py`

This adds:
- `conversation_sessions` dict
- `cleanup_old_sessions()` function
- `get_or_create_session()` function
- `add_to_conversation_history()` function
- `format_conversation_history()` function

### Step 4: Replace build_integrated_context Function

**Location**: Find `def build_integrated_context(query_text, intent, use_rag=True):`

**Action**: 
1. Change the signature to include `session_id=None`:
   ```python
   def build_integrated_context(query_text, intent, use_rag=True, session_id=None):
   ```

2. RIGHT AFTER `context_parts = []` line, insert the conversation history code from **SECTION 2**:
   ```python
   # Integration 0: Conversation History (NEW - PHASE 1!)
   if session_id and session_id in conversation_sessions:
       history = conversation_sessions[session_id]["history"]
       if history:
           history_text = format_conversation_history(history, last_n=5)
           if history_text:
               context_parts.append(f"""
   === RECENT CONVERSATION ===
   {history_text}
   ============================
   """)
               print(f"   💬 Added conversation history ({len(history)} exchanges)")
   ```

**OR** just replace the entire function with the version from SECTION 2.

### Step 5: Modify /api/chat Endpoint

**Location**: Find `@app.route('/api/chat', methods=['POST'])` and the `def chat():` function

**Five changes to make**:

**Change 1** - Get session_id (after `use_rag = data.get('use_rag', True)`):
```python
session_id = data.get('session_id', None)
session_id = get_or_create_session(session_id)
```

**Change 2** - Log session (after the query print):
```python
print(f"💬 Session: {session_id}")
```

**Change 3** - Pass session_id to context building:
```python
# OLD:
context, rag_results = build_integrated_context(message, intent, use_rag)

# NEW:
context, rag_results = build_integrated_context(message, intent, use_rag, session_id)
```

**Change 4** - Store conversation (BEFORE each `return jsonify(...)`):

For Gemini response:
```python
add_to_conversation_history(session_id, message, response.text, intent)
```

For Ollama response:
```python
add_to_conversation_history(session_id, message, result.get('response', ''), intent)
```

**Change 5** - Return session info (IN each `return jsonify({...})`):
```python
return jsonify({
    'success': True,
    'response': ...,
    # ... existing fields ...
    'session_id': session_id,  # ADD THIS
    'conversation_depth': len(conversation_sessions.get(session_id, {}).get('history', []))  # ADD THIS
})
```

### Step 6: Add Session Management Endpoints (Optional)

**Location**: Add BEFORE `if __name__ == '__main__':` at the end

**Action**: Copy all 4 endpoint functions from **SECTION 4** of `phase1_conversation_memory.py`:
- `/api/session/new` - Create new session
- `/api/session/<id>` GET - Get session history  
- `/api/session/<id>` DELETE - Delete session
- `/api/sessions` - List all sessions

---

## 🧪 Testing Phase 1

### Step 1: Restart Backend

```bash
cd ~/ai-stack
./quick_restart.sh
```

Check for errors in startup. If errors, check the backup and troubleshoot.

### Step 2: Test Multi-Turn Conversation

Open FAITHH UI and test:

**Test 1 - Simple Follow-up**:
1. "What is the Penumbra Accord?"
2. "How does mediation work in that system?"
3. "What happens after mediation?"

**Expected**: Each question should reference previous context naturally.

**Test 2 - Technical Follow-up**:
1. "What is FAITHH?"
2. "What capabilities does it have?"
3. "How does the RAG system work?"

**Expected**: FAITHH explains its own features conversationally.

**Test 3 - Project Follow-up**:
1. "Where am I with Constella development?"
2. "What are the blockers?"
3. "What should I work on next?"

**Expected**: Coherent project status conversation.

### Step 3: Check Backend Logs

You should see in the terminal:
```
🆕 Created session: session_20251130_...
💬 Added conversation history (0 exchanges)
💬 Added conversation history (1 exchanges)
💬 Added conversation history (2 exchanges)
```

### Step 4: Verify Response Format

API responses should now include:
```json
{
  "success": true,
  "response": "...",
  "session_id": "session_20251130_123456",
  "conversation_depth": 3
}
```

---

## 🔧 Troubleshooting

### Backend Won't Start
- **Error**: `NameError: name 'conversation_sessions' is not defined`
- **Fix**: Check you added Section 1 code after CURRENT_MODEL line

### No Conversation History
- **Error**: Responses don't reference previous exchanges
- **Fix**: Check `build_integrated_context` has `session_id=None` parameter
- **Fix**: Check you're passing `session_id` when calling it

### Session Not Persisting
- **Error**: Each query seems independent
- **Fix**: Check `add_to_conversation_history` is called before return
- **Fix**: Check UI is sending same `session_id` with each request

### Backend Crashes on Response
- **Error**: Error when returning response
- **Fix**: Check you added `session_id` handling before using it
- **Fix**: Check conversation_sessions dict exists

---

## ✅ Success Criteria

Phase 1 is working if:
- ✅ Backend starts without errors
- ✅ You can ask a question and get a response
- ✅ Follow-up questions reference previous context
- ✅ Backend logs show session creation and history
- ✅ Responses include session_id field
- ✅ Conversation feels natural, not like isolated Q&A

---

## 🚨 Rollback If Needed

If something breaks:
```bash
cd ~/ai-stack
cp faithh_professional_backend_fixed.py.backup_pre_phase1 faithh_professional_backend_fixed.py
./quick_restart.sh
```

This restores your working backend.

---

## 📝 Next Steps After Success

Once Phase 1 works:
1. **Test with real usage** - Income brainstorming conversation
2. **Document findings** - Does it feel conversational?
3. **Compare to Claude** - Is the gap closed?
4. **Plan Phase 2** - Code generation + clarifying questions

---

## 💡 Tips

- **Test incrementally**: Add Section 1, restart, confirm it works. Then add Section 2, etc.
- **Read backend logs**: They show what integrations are being used
- **Start fresh session**: If testing gets confusing, create new session
- **Keep backup**: Don't delete the backup until you're confident

---

*Reference file: `phase1_conversation_memory.py`*  
*Complete code: All sections in reference file*  
*Support docs: `PHASE1_READY.md`*

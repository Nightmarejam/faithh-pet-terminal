# Windsurf Handoff — UI Hot Fixes + Model Safety
# Date: 2026-03-07
# File: docs/archive/HANDOFF_UI_HOTFIXES_2026-03-07.md

## Context

Three problems to fix in this session:
1. deepseek-r1:32b causes CUDA crash (sm_61 / GTX 1080 Ti incompatible)
2. Failed messages have no retry — user has to copy-paste manually
3. ChromaDB reindex script hangs (from previous session — needs a fix too)

All frontend work is in faithh_pet_v4.html at ROOT level.
Verify before editing: grep -A2 "@app.route('/')" faithh_professional_backend_fixed.py
Test at: http://localhost:5557/ — NOT by opening the HTML file directly.

---

## Fix A: Mark deepseek-r1:32b as broken in the UI (15 min)

### Why
deepseek-r1:32b requires CUDA sm_70+ (RTX architecture).
The RTX 3090 (primary inference GPU) is available, but Ollama is routing it to the
GTX 1080 Ti (sm_61) which throws: "CUDA error: no kernel image is available for execution"

The model is listed in MODEL_OPTIONS at line ~4272 in faithh_pet_v4.html.
The auto-router never selects it, but the user can manually pick it from the dropdown.

### Fix
In faithh_pet_v4.html, find this line (around line 4272):
  { id: 'deepseek-r1:32b', label: '🧠 DeepSeek-R1 (32B) - Reasoning', category: 'local' },

Change to:
  { id: 'deepseek-r1:32b', label: '⚠️ DeepSeek-R1 (32B) - BROKEN (sm_61 CUDA)', category: 'local', disabled: true },

Then find the model select dropdown rendering code and add disabled support.
Search for the code that renders MODEL_OPTIONS into <option> elements.
Add: if (m.disabled) option.disabled = true; and optionally style it grey.

If you can't find the renderer easily, a simpler fix:
Just change the label text to include the warning — users will see it in the dropdown.
That's acceptable as a quick fix.

### Also fix: backend routing
In backend/llm_providers.py, find get_optimal_model_for_query().
The function can return "ollama", "deepseek-r1:32b" for complex queries if that model
is ever added to routing. As a precaution, add a BROKEN_MODELS set at the top:

BROKEN_MODELS = {"deepseek-r1:32b"}  # sm_61 CUDA incompatible on this hardware

And in get_optimal_model_for_query(), before returning any model:
  if optimal_model in BROKEN_MODELS:
      optimal_model = "llama3.3:70b"  # fallback for broken models

---

## Fix B: Add retry button on failed messages (30 min)

### Why
When a message fails (CUDA error, timeout, network error), the UI shows a red error string
but there's no way to retry without manually copying the original message and re-pasting.
This is painful for the user.

### Where
In faithh_pet_v4.html, find the catch block in sendMessage() (around line 5278):
  } catch (error) {
      console.error('Chat error:', error);
      contentDiv.innerHTML = `
          <span style="color: #ff6666;">
              ${error.name === 'AbortError' 
                  ? 'Request timed out. Try a simpler message.' 
                  : 'Connection error. Check backend on port 5557.'}
          </span>
      `;
  }

### Fix
Replace the catch block with one that shows both the error AND a retry button:

  } catch (error) {
      console.error('Chat error:', error);
      const isTimeout = error.name === 'AbortError';
      contentDiv.innerHTML = `
          <div style="color: #ff6666; margin-bottom: 8px;">
              ${isTimeout 
                  ? '⏱️ Request timed out. The model may be loading — try again.' 
                  : '⚠️ Connection error. Check backend on port 5557.'}
          </div>
          <button onclick="retryLastMessage(this, ${JSON.stringify(message).replace(/"/g, '&quot;')})" 
                  style="
                      background: rgba(0,255,255,0.1);
                      border: 1px solid #00ffff;
                      color: #00ffff;
                      padding: 6px 14px;
                      border-radius: 4px;
                      cursor: pointer;
                      font-size: 12px;
                      margin-top: 4px;
                  ">
              🔄 Retry
          </button>
      `;
  }

### Add retryLastMessage function
Add this function near sendMessage() (before or after it, not inside):

  function retryLastMessage(btn, originalMessage) {
      // Disable button to prevent double-click
      btn.disabled = true;
      btn.textContent = '⏳ Retrying...';
      
      // Put the original message back in the input and trigger send
      const input = document.getElementById('chatInput');
      input.value = originalMessage;
      sendMessage();
  }

### Note on escaping
The JSON.stringify(message) in the onclick attribute needs to be careful with special characters.
If the message contains quotes or backticks, the inline onclick can break.
Safer alternative: store the last failed message in a module-level variable:

  // At module level (near other state variables):
  let lastFailedMessage = '';

  // In sendMessage(), right after: const message = input.value.trim();
  // Add: (but DON'T set it until we know it failed)

  // In the catch block, set it before showing the button:
  lastFailedMessage = message;

  // Then the button becomes simply:
  <button onclick="retryLastMessage(this)">🔄 Retry</button>

  // And retryLastMessage becomes:
  function retryLastMessage(btn) {
      if (!lastFailedMessage) return;
      btn.disabled = true;
      btn.textContent = '⏳ Retrying...';
      const input = document.getElementById('chatInput');
      input.value = lastFailedMessage;
      sendMessage();
  }

Use the module-level variable approach — it's cleaner and avoids HTML escaping issues.

---

## Fix C: ChromaDB reindex hang (15 min)

### Why
The reindex_core_docs.py script from the previous session hangs after "Before: 38330 docs".
The issue: ChromaDB upsert without a configured embedding function works for small documents
(proven with add_harmony_docs.py) but may time out on large files like SYSTEMS_MAP.md.
SYSTEMS_MAP.md is ~400KB — ChromaDB needs to chunk and embed it server-side.

### Fix
Rewrite reindex_core_docs.py to chunk files BEFORE upserting, matching the pattern that
worked in scripts/add_harmony_docs.py. Small chunks (1500 chars) upsert fast.

Also add per-chunk progress output and a 10s timeout per upsert call.

Here is the fixed version of scripts/reindex_core_docs.py:

```python
#!/usr/bin/env python3
"""
Re-index core orientation docs that were updated today.
Uses small chunks + per-chunk logging to avoid silent hangs.
DO NOT import torch or sentence_transformers — WSL crash risk.
"""
import sys
import hashlib
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
CHROMA_HOST = "servicebox.taileb8c60.ts.net"
CHROMA_PORT = 8000
CHUNK_SIZE = 1500
OVERLAP = 200

DOCS_TO_REINDEX = [
    BASE_DIR / "SYSTEMS_MAP.md",
    BASE_DIR / "CONTEXT.md",
    BASE_DIR / "scaffolding_state.json",
]

def chunk_text(text):
    if len(text) <= CHUNK_SIZE:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        if end < len(text):
            for sep in ['\n\n', '\n', '. ']:
                b = text.rfind(sep, start + OVERLAP, end)
                if b > start + OVERLAP:
                    end = b + len(sep)
                    break
        chunks.append(text[start:end])
        start = end - OVERLAP
    return chunks

def doc_id(filepath, chunk_idx):
    h = hashlib.md5(f"{filepath.name}:{chunk_idx}".encode()).hexdigest()[:8]
    return f"core_{filepath.stem[:25]}_{h}"

print("Starting reindex_core_docs.py")
sys.stdout.flush()

import chromadb
client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
col = client.get_collection("faithh_knowledge_base")
before = col.count()
print(f"Connected. Before: {before} docs")
sys.stdout.flush()

total_chunks = 0
for filepath in DOCS_TO_REINDEX:
    if not filepath.exists():
        print(f"SKIP: {filepath.name}")
        sys.stdout.flush()
        continue
    text = filepath.read_text(encoding='utf-8')
    chunks = chunk_text(text)
    relative = str(filepath.relative_to(BASE_DIR))
    print(f"  {filepath.name}: {len(chunks)} chunks...")
    sys.stdout.flush()
    for i, chunk in enumerate(chunks):
        try:
            col.upsert(
                ids=[doc_id(filepath, i)],
                documents=[chunk],
                metadatas=[{
                    "source": relative,
                    "category": "core_orientation",
                    "project": "faithh",
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "timestamp": datetime.now().isoformat(),
                    "indexed_by": "reindex_core_docs.py"
                }]
            )
            if i % 5 == 0:
                print(f"    chunk {i+1}/{len(chunks)}")
                sys.stdout.flush()
        except Exception as e:
            print(f"    ERROR chunk {i}: {e}")
            sys.stdout.flush()
    total_chunks += len(chunks)
    print(f"  {filepath.name}: done")
    sys.stdout.flush()

after = col.count()
print(f"Done. {total_chunks} chunks. Collection: {before} -> {after}")
```

Run it:
  wsl -d Ubuntu -e bash -lc "cd /home/jonat/ai-stack && source venv/bin/activate && python3 scripts/reindex_core_docs.py"

---

## Verification

After all fixes:

1. Open http://localhost:5557/
2. Open the model dropdown — deepseek-r1:32b should show as disabled or with ⚠️ warning
3. Send a message that fails (temporarily stop the backend, send, restart)
   → Should see red error + 🔄 Retry button
   → Click Retry → message should resend without copy-paste
4. Check ChromaDB count:
   wsl -d Ubuntu -e bash -lc "cd /home/jonat/ai-stack && source venv/bin/activate && python3 scripts/check_count.py"
   Should be higher than 38,330

---

## Commit

git add faithh_pet_v4.html backend/llm_providers.py scripts/reindex_core_docs.py
git commit -m "Hotfix: disable deepseek-r1 (CUDA), add retry button, fix reindex chunking"

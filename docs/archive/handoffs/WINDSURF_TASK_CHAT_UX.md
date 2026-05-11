# WINDSURF TASK: FAITHH Chat UX Upgrade

## Summary
Upgrade `faithh_pet.html` chat to support Markdown rendering, syntax highlighting, and message actions.

## Files to Modify
1. `faithh_pet.html` (primary)
2. `faithh_professional_backend_fixed.py` (optional - streaming endpoint)

---

## Task 1: Add Libraries (Line 7)

Add after `<title>` in `<head>`:

```html
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/python.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/javascript.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/bash.min.js"></script>
```

---

## Task 2: Add CSS (~Line 490)

Add new style section for:
- Code blocks with header and copy button
- Animated typing indicator (bouncing dots)
- Message action buttons (copy, regenerate)
- Streaming cursor animation
- Smooth scroll anchoring

See `WINDSURF_HANDOFF_CHAT_UX_UPGRADE.md` for full CSS.

---

## Task 3: Update sendMessage() (Lines 1993-2175)

Replace `sendMessage()` function with new version that:

1. **Configures marked.js** with hljs syntax highlighting
2. **Custom renderer** for code blocks with copy buttons
3. **Throttled updates** (50ms buffer for smooth rendering)
4. **Streaming support** (tries `/api/chat/stream` first, falls back to regular)
5. **Message actions** (copy, regenerate buttons)
6. **Animated typing** indicator with bouncing dots

Key changes:
- Replace `escapeHtml(data.response)` with `marked.parse(data.response)`
- Add `copyCodeBlock()`, `copyMessage()`, `regenerateMessage()` functions
- Add throttled buffer for streaming updates

See `WINDSURF_HANDOFF_CHAT_UX_UPGRADE.md` for full implementation.

---

## Task 4 (Optional): Backend Streaming

Add `/api/chat/stream` endpoint to `faithh_professional_backend_fixed.py` that:
- Uses SSE (Server-Sent Events)
- Streams from Ollama with `"stream": True`
- Returns `text/event-stream` content type

---

## Testing

After changes, verify:
- [ ] Page loads without errors
- [ ] Markdown renders (test: send "**bold** and `code`")
- [ ] Code blocks highlight (test: send "```python\nprint('hello')```")
- [ ] Copy buttons work
- [ ] Typing indicator animates
- [ ] Scroll behavior is smooth

---

## Don't Break

- PET Terminal aesthetic (cyan, orange, dark blue colors)
- Battle Chips functionality
- RAG toggle
- Stats tracking
- Active chips display

---

## Reference Files

- Full details: `docs/WINDSURF_HANDOFF_CHAT_UX_UPGRADE.md`
- Research: `docs/compass_artifact_wf-966bdfe5-..._text_markdown.md`
- Implementation plan: `docs/FAITHH_CHAT_UX_IMPLEMENTATION_PLAN.md`

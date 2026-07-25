# FAITHH PET Terminal - Chat UX Implementation Plan

**Created:** 2026-01-19
**Based on:** Research from `compass_artifact_wf-966bdfe5-bbb4-4a92-83e1-c88a2e3c94b8_text_markdown.md`
**Target:** `faithh_pet.html` / `faithh_pet_v4.html`

---

## Executive Summary

This plan translates modern AI chat interface best practices into actionable improvements for FAITHH's vanilla JavaScript PET Terminal UI. The goal is to achieve Claude.ai-level smoothness while maintaining the MegaMan Battle Network retro-futuristic aesthetic.

---

## Current State Analysis

### What FAITHH Has
- ✅ Basic SSE streaming from Flask backend
- ✅ Dark theme with retro-futuristic aesthetic
- ✅ Battle Chips (quick action buttons)
- ✅ RAG toggle for ChromaDB context
- ✅ Pulse Security integration

### What Needs Improvement
- ❌ Partial Markdown handling during streaming (broken rendering)
- ❌ Code block syntax highlighting (minimal/none)
- ❌ Layout shift during message streaming
- ❌ Message actions (copy, regenerate) - limited
- ❌ Conversation history management
- ❌ Empty state / onboarding UX

---

## Recommended Library Stack

Based on research, here's the optimal stack for vanilla JS:

| Component | Library | Size | Why |
|-----------|---------|------|-----|
| Streaming Markdown | **streaming-markdown** | ~3KB | Vanilla JS, handles partial syntax |
| Syntax Highlighting | **Highlight.js** | ~70KB | Auto-detection, easy setup |
| (Future upgrade) | **Shiki + shiki-stream** | ~280KB | VS Code quality, streaming support |

### CDN Links (for quick prototyping)
```html
<!-- Streaming Markdown -->
<script src="https://unpkg.com/streaming-markdown@latest/dist/streaming-markdown.min.js"></script>

<!-- Highlight.js (auto-detection) -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
**Goal:** Smooth streaming with proper Markdown rendering

#### 1.1 Integrate streaming-markdown
```javascript
// Replace current text appending with streaming-markdown parser
import { StreamingMarkdown } from 'streaming-markdown';

const parser = new StreamingMarkdown({
  renderer: {
    // Custom renderer to match PET Terminal aesthetic
    paragraph: (text) => `<p class="pet-text">${text}</p>`,
    code: (code, lang) => renderCodeBlock(code, lang),
    // ... other elements
  }
});

// In your SSE handler:
eventSource.onmessage = (event) => {
  const chunk = JSON.parse(event.data);
  parser.write(chunk.text);
  // Parser automatically updates DOM
};
```

#### 1.2 Add Highlight.js for code blocks
```javascript
function renderCodeBlock(code, language) {
  const detected = language || hljs.highlightAuto(code).language;
  const highlighted = hljs.highlight(code, { language: detected }).value;
  
  return `
    <div class="code-block pet-code">
      <div class="code-header">
        <span class="language-badge">${detected}</span>
        <button class="copy-btn" onclick="copyCode(this)">
          <span class="copy-icon">📋</span>
          <span class="copy-text">Copy</span>
        </button>
      </div>
      <pre><code class="hljs language-${detected}">${highlighted}</code></pre>
    </div>
  `;
}
```

#### 1.3 Fix scroll behavior during streaming
```css
/* Add to FAITHH styles */
.chat-container {
  overflow-anchor: none;
}

.scroll-anchor {
  overflow-anchor: auto;
  height: 1px;
}
```

```javascript
// Smart auto-scroll
let userScrolledAway = false;
const chatContainer = document.getElementById('chat-messages');

chatContainer.addEventListener('scroll', () => {
  const { scrollTop, scrollHeight, clientHeight } = chatContainer;
  userScrolledAway = scrollHeight - scrollTop - clientHeight > 100;
});

function scrollToBottom(behavior = 'smooth') {
  if (!userScrolledAway) {
    chatContainer.scrollTo({
      top: chatContainer.scrollHeight,
      behavior: behavior
    });
  }
}
```

#### 1.4 Throttle DOM updates (50ms)
```javascript
let updateBuffer = '';
let updateTimeout = null;

function bufferUpdate(text) {
  updateBuffer += text;
  
  if (!updateTimeout) {
    updateTimeout = setTimeout(() => {
      flushBuffer();
      updateTimeout = null;
    }, 50);
  }
}

function flushBuffer() {
  if (updateBuffer) {
    parser.write(updateBuffer);
    updateBuffer = '';
    requestAnimationFrame(scrollToBottom);
  }
}
```

---

### Phase 2: Enhanced UX (Week 3-4)
**Goal:** Message actions and visual polish

#### 2.1 Message action buttons
```html
<!-- Add to each message -->
<div class="message-actions">
  <button class="action-btn" onclick="copyMessage(this)" title="Copy">
    <span>📋</span>
  </button>
  <button class="action-btn" onclick="regenerate(this)" title="Regenerate">
    <span>🔄</span>
  </button>
  <button class="action-btn feedback-btn" onclick="feedback(this, 'up')" title="Good">
    <span>👍</span>
  </button>
  <button class="action-btn feedback-btn" onclick="feedback(this, 'down')" title="Bad">
    <span>👎</span>
  </button>
</div>
```

```css
/* PET Terminal-styled action buttons */
.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.message:hover .message-actions,
.message-actions:focus-within {
  opacity: 1;
}

.action-btn {
  background: var(--pet-panel-bg);
  border: 1px solid var(--pet-border-color);
  border-radius: 4px;
  padding: 4px 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.15s ease;
}

.action-btn:hover {
  background: var(--pet-accent-color);
  transform: scale(1.05);
}

.action-btn:active {
  transform: scale(0.98);
}
```

#### 2.2 Copy functionality with feedback
```javascript
async function copyMessage(btn) {
  const message = btn.closest('.message');
  const content = message.querySelector('.message-content').textContent;
  
  try {
    await navigator.clipboard.writeText(content);
    showCopyFeedback(btn, true);
  } catch (err) {
    showCopyFeedback(btn, false);
  }
}

function showCopyFeedback(btn, success) {
  const originalContent = btn.innerHTML;
  btn.innerHTML = success ? '✓' : '✗';
  btn.classList.add(success ? 'success' : 'error');
  
  setTimeout(() => {
    btn.innerHTML = originalContent;
    btn.classList.remove('success', 'error');
  }, 2000);
}
```

#### 2.3 Typing indicator
```html
<div id="typing-indicator" class="typing-indicator hidden">
  <div class="typing-dots">
    <span></span><span></span><span></span>
  </div>
  <span class="typing-text">FAITHH is thinking...</span>
</div>
```

```css
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  color: var(--pet-text-secondary);
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  background: var(--pet-accent-color);
  border-radius: 50%;
  animation: typing-bounce 1.4s ease-in-out infinite;
}

.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-8px); }
}
```

---

### Phase 3: Conversation Management (Week 5-6)
**Goal:** History, branching, and persistence

#### 3.1 State management with Proxy
```javascript
const chatState = new Proxy({
  messages: [],
  currentConversation: null,
  isStreaming: false,
  error: null
}, {
  set(target, key, value) {
    target[key] = value;
    notifySubscribers(key, value);
    return true;
  }
});

const subscribers = new Map();

function subscribe(key, callback) {
  if (!subscribers.has(key)) subscribers.set(key, []);
  subscribers.get(key).push(callback);
}

function notifySubscribers(key, value) {
  (subscribers.get(key) || []).forEach(cb => cb(value));
}

// Usage
subscribe('messages', (messages) => renderMessages(messages));
subscribe('isStreaming', (streaming) => toggleTypingIndicator(streaming));
```

#### 3.2 Local storage persistence
```javascript
function saveConversation() {
  const data = {
    id: chatState.currentConversation,
    messages: chatState.messages,
    timestamp: Date.now()
  };
  
  const conversations = JSON.parse(localStorage.getItem('faithh_conversations') || '[]');
  const existingIndex = conversations.findIndex(c => c.id === data.id);
  
  if (existingIndex >= 0) {
    conversations[existingIndex] = data;
  } else {
    conversations.push(data);
  }
  
  localStorage.setItem('faithh_conversations', JSON.stringify(conversations));
}

function loadConversations() {
  return JSON.parse(localStorage.getItem('faithh_conversations') || '[]')
    .sort((a, b) => b.timestamp - a.timestamp);
}
```

#### 3.3 Empty state with suggested prompts
```html
<div id="empty-state" class="empty-state">
  <div class="pet-logo"><!-- FAITHH logo --></div>
  <h2>Ready to assist, Operator!</h2>
  <p>What would you like to explore today?</p>
  
  <div class="suggested-prompts">
    <button class="prompt-chip" onclick="useSuggestion(this)">
      🔍 Search my conversation history
    </button>
    <button class="prompt-chip" onclick="useSuggestion(this)">
      📊 Show project status
    </button>
    <button class="prompt-chip" onclick="useSuggestion(this)">
      💡 Help me brainstorm ideas
    </button>
    <button class="prompt-chip" onclick="useSuggestion(this)">
      📝 Draft a document
    </button>
  </div>
</div>
```

---

## Accessibility Checklist

- [ ] Add `role="log"` to chat container
- [ ] Add `aria-live="polite"` for new messages
- [ ] Ensure all buttons have `aria-label`
- [ ] Add `tabindex="0"` to scrollable code blocks
- [ ] Support keyboard navigation (Enter to send, Shift+Enter for newline)
- [ ] Add visible focus indicators
- [ ] Use sufficient color contrast (WCAG AA minimum)

---

## Performance Targets

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Time to First Token | <200ms | Network tab |
| Scroll FPS | 60fps | DevTools Performance |
| DOM updates during streaming | <50ms batches | Custom logging |
| Memory (100 messages) | <50MB | DevTools Memory |

---

## File Changes Needed

### `faithh_pet.html` / `faithh_pet_v4.html`
1. Add CDN links for streaming-markdown and highlight.js
2. Update message rendering logic
3. Add message action buttons
4. Add typing indicator
5. Add empty state
6. Update CSS for new components

### `faithh_professional_backend_fixed.py`
1. Ensure SSE sends proper `content_block_delta` format
2. Add message ID to enable regeneration
3. Add feedback endpoint

---

## Quick Wins (Do First)

1. **Copy button for code blocks** - High impact, easy to add
2. **Typing indicator** - Makes waiting feel shorter
3. **Scroll anchor CSS** - Fixes janky scrolling, CSS-only
4. **50ms throttle** - Smoother streaming, small code change

---

## Testing Plan

1. **Stream 1000+ tokens** - Check for lag/memory leaks
2. **Nested code blocks** - Verify highlighting works
3. **Rapid messages** - Test state management
4. **Mobile view** - Responsive design check
5. **Keyboard only** - Accessibility test

---

## Next Steps

1. Review this plan with Claude/Windsurf
2. Start with Phase 1.1 (streaming-markdown integration)
3. Test in isolation before integrating
4. Document any PET Terminal-specific adaptations
5. Update session report when complete

---

**End of Implementation Plan**

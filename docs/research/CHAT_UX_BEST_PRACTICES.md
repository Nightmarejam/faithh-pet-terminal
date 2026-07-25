# Modern AI chat interface best practices: A technical blueprint

Building a polished AI chat interface requires solving three interconnected challenges: rendering streaming Markdown without visual jank, implementing developer-friendly code blocks, and creating a UX that feels conversational rather than mechanical. **Vercel's Streamdown library** and **Shiki with shiki-stream** have emerged as the leading solutions for streaming text and syntax highlighting respectively, while **Server-Sent Events (SSE)** remains the industry-standard streaming protocol used by Claude.ai and ChatGPT alike. The distinction between Claude.ai's warm, natural feel and Windsurf's tool-like precision comes down to deliberate design choices—serif typography, warm color palettes, and generous whitespace versus dense, functional IDE conventions.

## Streaming Markdown rendering demands purpose-built libraries

Traditional Markdown parsers like marked.js and markdown-it were designed for complete documents, making them problematic for token-by-token streaming. When tokens arrive mid-syntax (like `**bold` without the closing `**`), these libraries either fail to render or produce broken HTML.

**Streamdown**, Vercel's open-source library with **3,300 GitHub stars**, solves this directly. It uses a companion library called `remend` for "self-healing Markdown"—automatically closing incomplete syntax during streaming. For example, `**bold text` becomes `**bold text**` until the actual closing delimiter arrives. Streamdown handles incomplete links by substituting placeholder URLs (`streamdown:incomplete-link`) and manages partial code blocks gracefully.

For vanilla JavaScript projects, **streaming-markdown** (338 stars, ~3KB gzipped) takes an "optimistic parsing" approach—styling elements immediately when opening delimiters are detected, then only appending new DOM nodes without modifying existing ones. This design allows users to select text during streaming without their selection being disrupted. The library provides a custom renderer interface for precise DOM control.

The key technique for smooth 60fps rendering is **block-level memoization**. Parse the Markdown into distinct blocks using `marked.lexer()`, then memoize each block independently. Only the currently-streaming block re-renders as tokens arrive, while completed blocks remain static. The Vercel AI SDK recommends throttling updates to **50ms intervals** using `experimental_throttle: 50` to prevent excessive re-renders.

Layout shift prevention requires a combination of CSS scroll anchoring and JavaScript coordination. Set `overflow-anchor: none` on all chat elements except a designated anchor element at the bottom, which gets `overflow-anchor: auto`. Use Intersection Observer to detect when the user has scrolled away from the bottom, then conditionally auto-scroll only when they're already at the bottom. Apply `scroll-behavior: smooth` for streaming updates but `instant` for initial page loads to avoid jarring animations.

## Shiki dominates syntax highlighting for AI chat interfaces

The syntax highlighting landscape has consolidated around three major options, with **Shiki emerging as the clear winner** for AI chat applications due to its streaming support and VS Code-quality output.

| Library | Bundle Size | Streaming | Auto-Detection | Accuracy | Performance |
|---------|-------------|-----------|----------------|----------|-------------|
| Shiki | ~280KB (WASM) | ✅ via shiki-stream | ❌ Manual | Excellent (VS Code engine) | ~7x slower than Prism |
| Prism.js | ~2KB core | ❌ No | ❌ Manual | Good | Fastest |
| Highlight.js | ~70KB common | ❌ No | ✅ Built-in | Good | ~50% slower than Prism |

Shiki's **shiki-stream** library, created by Anthony Fu, provides `CodeToTokenTransformStream` specifically designed for LLM outputs. It supports "recall tokens" for context-aware highlighting updates and ships with React and Vue components. The tradeoff is bundle size—**280KB including WebAssembly**—but this delivers perfect VS Code theme compatibility and support for over 200 languages.

For language auto-detection when users don't specify, **Guesslang** (used by VS Code itself) achieves over 90% accuracy using a TensorFlow model trained on 1.9 million GitHub files. Common confusions occur between JavaScript/TypeScript and Java/Groovy. Alternatively, Highlight.js's built-in heuristic detection works well for most use cases without the ML overhead.

Code block implementation should include a **persistent copy button** (not hover-only), language badge in the header, and line numbers for blocks exceeding 10 lines. Position the copy button in the top-right corner with visual feedback—a checkmark icon and "Copied!" state lasting 2 seconds. For accessibility, use WCAG-compliant themes like **a11y-dark** (AAA compliant) or **a11y-light** (AA compliant), add `tabindex="0"` to scrollable code blocks, and include `role="region"` with descriptive `aria-label` attributes.

Windsurf's "Apply to File" functionality works by writing changes directly to disk before user approval, showing inline diffs with syntax highlighting. The implementation detects target files through code fence hints (```python:path/to/file.py```) or AST parsing to match function signatures against the codebase index. Accept/reject uses keyboard shortcuts (⌥+A/⌥+R) with code lens positioned above the diff.

## Claude.ai's warmth versus Windsurf's precision reflects intentional design philosophy

Claude.ai deliberately breaks from typical AI tool aesthetics by employing a **warm, terracotta-accented palette** (`#ae5630`) against cream backgrounds (`#F5F5F0` light, `#2b2a27` dark). The interface uses serif typography—unusual in software—creating what Anthropic describes as a "refined reading experience." This choice evokes academic warmth rather than cold technological precision.

The specific design tokens that create Claude's conversational feel include multi-layered box shadows (`shadow-[0_0.25rem_1.25rem_rgba(0,0,0,0.035)]`), subtle borders (`border-[#00000015]`), and smooth cubic-bezier transitions (`ease-[cubic-bezier(0.165,0.85,0.45,1)]`). Button interactions include `active:scale-[0.98]` for tactile feedback. Typography uses **16px body text with 1.6 line-height**, generous by software standards.

Windsurf, as a VS Code fork, inherits IDE conventions prioritizing information density over aesthetics. Its Cascade panel uses **14px sans-serif typography with 1.4 line-height**, compact 8-12px padding, and minimal decoration. The @-mentions system (`@files`, `@diff`, `@codebase`) provides deterministic context inclusion—function-level AST parsing, terminal contents, and git state. A "Stats for Nerds" panel reveals under-the-hood details, reinforcing its tool-first identity.

Developer feedback reveals the distinction clearly: Claude.ai users praise its "natural" conversation flow and UX simplicity, while Windsurf users appreciate the "cleaner UI compared to Cursor" and the Write/Chat mode toggle for switching between code modification and Q&A. The most common complaints across both platforms center on usage limits and context window limitations—UX concerns secondary to capability constraints.

For implementations seeking Claude's warmth, use these CSS custom properties: `--bg-primary: oklch(0.97 0.02 70)` for cream, `--accent: oklch(0.70 0.14 45)` for terracotta, with `font-family: ui-serif, Georgia, Cambria, serif`. For Windsurf's precision, inherit VS Code tokens (`var(--vscode-editor-background)`) and use system fonts with tighter spacing.

## Server-Sent Events power the streaming architecture

**SSE is the industry standard** for AI chat streaming—Claude.ai, ChatGPT, and most LLM providers use it with `"stream": true` parameters. SSE's unidirectional server-to-client flow matches the AI chat pattern perfectly: user input travels via standard HTTP POST, while responses stream back over SSE.

Claude's API sends structured SSE events: `message_start` initializes the response, `content_block_delta` delivers text chunks with `{"type": "text_delta", "text": "Hello"}`, periodic `ping` events maintain the connection, and `message_stop` signals completion. The browser's EventSource API provides **automatic reconnection** with `Last-Event-ID` headers for resumption—functionality that requires manual implementation with WebSockets.

For POST requests with complex payloads (which EventSource doesn't support), use fetch streaming with `response.body.getReader()`. Parse the stream by splitting on `\r?\n\r?\n` for event boundaries, then extracting data lines prefixed with `data: `. Buffer incomplete events across chunks.

State management for vanilla JavaScript chat applications should use a Proxy-based reactive store. Track messages as an array of objects containing `id`, `role` (user/assistant), `content`, `status` (pending/streaming/complete/error), and `timestamp`. Implement optimistic updates—immediately display user messages with "pending" status, create assistant message placeholders when streaming starts, then append chunks to the streaming message's content. A pub/sub pattern with `subscribe()` and `notify()` methods allows UI components to react to state changes.

For conversations exceeding **50-100 messages**, virtual scrolling becomes essential. The pattern renders only visible messages plus a buffer (typically 5 above and below), replacing off-screen messages with spacer elements matching their cumulative height. **HyperList** (under 300 lines, zero dependencies) supports chat-specific features including `reverse: true` for bottom-anchored scrolling. Combine with Intersection Observer for lazy-loading older messages as users scroll up.

DOM optimization during streaming requires batching updates via `requestAnimationFrame`. Accumulate incoming text in a buffer, then flush to the DOM once per animation frame. **Always use `textContent` rather than `innerHTML`** for streaming text—it's significantly faster (no HTML parsing) and eliminates XSS risks. Never use `innerText`, which triggers layout reflow. Separate DOM reads from writes to prevent layout thrashing; the FastDOM pattern queues all measurements before mutations.

## Message actions and conversation management shape the core UX

Message actions should be **always visible, not hover-only**—AWS Cloudscape guidelines explicitly recommend this for accessibility and discoverability. Place actions below message content, left-aligned for LTR languages, limiting visible buttons to approximately five with extras in a dropdown. Essential actions include copy, regenerate (refresh icon), and thumbs up/down feedback.

Thumbs up/down implementation requires four states: default (both enabled), loading (submitting), submitted (selected button fills), and disabled (after submission). On thumbs-down, optionally present a modal with categorized feedback reasons: Harmful, Incomplete, Inaccurate, or Other. Display confirmation text like "Your feedback has been submitted" and avoid lengthy follow-up questionnaires.

Conversation branching—essential for edit and regenerate functionality—preserves original messages while creating divergent paths. When users edit a previous message, warn them that subsequent messages will regenerate, then create a new branch from that point. Display branch navigation with "Response 2 of 3" indicators and Previous/Next chevrons on messages with alternatives. Store all versions rather than overwriting to enable full branch navigation.

Empty states should never leave users stranded. Display a welcoming header ("How can I help you today?"), **3-5 diverse clickable example prompts** showcasing different capabilities, and clear visual hierarchy guiding attention to the input field. Make prompts clickable to auto-fill the input—some implementations send immediately, others fill the input for user editing. Avoid overly niche examples; demonstrate the breadth of capabilities.

Error handling requires clear, human-readable messages with recovery actions. For rate limiting (HTTP 429), show "You've sent too many messages. Please wait [X] seconds" with a countdown timer if possible. For streaming interruptions, save partial responses and offer "Continue generating" options. Implement exponential backoff for reconnection attempts (1s → 2s → 4s → 8s, capped at 30s). Toast notifications should use `aria-live="polite"` for non-critical updates, reserving `aria-live="assertive"` exclusively for urgent errors.

For accessibility, the chat container should use `role="log"` which implicitly sets `aria-live="polite"` and `aria-atomic="false"`. New messages are announced automatically without stealing focus from the input field. Ensure all interactive elements are keyboard-reachable with visible focus indicators, support Enter for send, Shift+Enter for newlines, and up arrow (in empty input) to edit the last message.

## Implementation should follow a phased priority

The research converges on a clear implementation hierarchy. **Phase one** establishes the foundation: streaming Markdown with Streamdown or streaming-markdown, syntax highlighting with Shiki, SSE-based streaming architecture, core message actions (copy, regenerate, feedback), typing indicators, and ARIA live regions for accessibility. This phase delivers a functional, accessible chat experience.

**Phase two** enhances the experience: conversation history sidebar with search and rename, empty state design with suggested prompts, file attachment support with drag-drop and preview, and edit/branch functionality for message revision. These features transform basic chat into a productive tool.

**Phase three** adds advanced capabilities: full branching visualization, advanced search with filters across conversations, export/sharing in multiple formats, and power-user features like comprehensive keyboard shortcuts and customization options.

For library selection, the optimal stack combines **Streamdown** (React) or **streaming-markdown** (vanilla JS) for Markdown, **Shiki with shiki-stream** for syntax highlighting with **Highlight.js as fallback** for auto-detection, and vanilla **EventSource or fetch streaming** for SSE. State management in vanilla JS works well with Proxy-based stores; for React, the Vercel AI SDK's `useChat` hook handles streaming automatically.

The distinction between a mechanical and natural chat interface ultimately comes down to **attention to micro-interactions**: smooth transitions (300ms cubic-bezier), tactile button feedback (scale transforms), warm color temperatures, generous whitespace, and serif typography options. These details, combined with robust technical foundations for streaming and code handling, create the polished experience users increasingly expect from AI assistants.

## Conclusion

Modern AI chat interfaces have converged on SSE streaming, purpose-built Markdown parsers that handle incomplete syntax gracefully, and Shiki-based syntax highlighting with streaming support. The visual distinction between conversational interfaces like Claude.ai and tool-like interfaces like Windsurf reflects deliberate choices about typography (serif vs. sans-serif), color temperature (warm terracotta vs. neutral), and information density (generous whitespace vs. compact layouts). 

Implementation should prioritize streaming performance through block-level memoization and 50ms throttling, ensure accessibility via ARIA live regions and visible action buttons, and build toward branching/editing capabilities that preserve conversation history. The **Vercel AI SDK** provides the most complete React solution, while vanilla implementations should combine streaming-markdown, Shiki, and custom SSE handling with Proxy-based state management.
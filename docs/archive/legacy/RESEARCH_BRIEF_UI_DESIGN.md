# FAITHH UI/UX Research Brief

**Date**: 2026-01-01
**Purpose**: Gather design recommendations for FAITHH interface improvements
**Priority Feature**: Prioritizer MVP integration

---

## Context

FAITHH (Friendly AI Teaching & Helping Hub) is a personal AI assistant with:
- MegaMan Battle Network-inspired "chip" system
- RAG-powered knowledge base (27,500+ documents)
- Parallel chip retrieval for contextual responses
- Current UI: Single-page chat interface with avatar characters

**Tech Stack**: Flask backend, vanilla HTML/CSS/JS frontend, considering React migration

---

## Current State Questions

### 1. Inventory
- What pages/views currently exist?
- What's connected to backend vs. static/placeholder?
- What's the navigation structure?

### 2. Prioritizer Integration
The Prioritizer MVP will include:
- Eisenhower Matrix (4 quadrants: Important+Urgent, Important+Not Urgent, etc.)
- Kanban-style drag-drop between quadrants
- "Task of the Day" recommendation
- Task persistence (JSON/SQLite)

**Design questions:**
- Should Prioritizer be a dedicated page, sidebar panel, modal, or expandable chip?
- How should "Task of the Day" surface? (Banner, chat greeting, floating widget?)
- Should tasks be creatable from chat? ("Add task: finish report by Friday")

### 3. Design Direction
Current aesthetic: MegaMan Battle Network (chips, avatars, game-inspired UI)

**Questions:**
- Keep the game aesthetic or evolve toward professional dashboard?
- What's the right balance of playful vs. functional?
- Color scheme preferences? (Current: dark theme with accent colors)

### 4. Information Architecture
Potential FAITHH "modes":
- **Chat** (current) - Conversational interface
- **Prioritizer** (new) - Task management
- **Knowledge Explorer** (future) - Browse indexed documents
- **Project Status** (future) - View project states
- **Settings** - Configuration

**Questions:**
- How should users switch between modes? (Tabs, sidebar, command palette, chat commands?)
- Should modes be combinable? (Chat + Prioritizer side-by-side?)
- What's the primary view on launch?

### 5. Layout Options
Consider these patterns:
- **Single panel**: One view at a time, full width
- **Split panel**: Chat on left, tools on right
- **Dashboard**: Multiple widgets/cards
- **Floating panels**: Draggable, resizable windows

**Questions:**
- Which pattern fits FAITHH's use case best?
- Should layout be user-customizable?

### 6. Responsive/Mobile
**Questions:**
- Does FAITHH need mobile support?
- If yes, what's the priority view on mobile?
- Touch-friendly interactions needed?

---

## Screenshots to Capture

Please take screenshots of:
1. [ ] Current chat interface (default/empty state)
2. [ ] Chat with response showing chips used
3. [ ] Chat with long response (scroll behavior)
4. [ ] Any existing navigation elements
5. [ ] Status indicators (backend connection, etc.)
6. [ ] Avatar/character display (FAITHH + PULSE)

---

## Competitor/Inspiration Research

Look at these for inspiration:
- **Notion** - Clean task management + docs
- **Linear** - Modern project management UI
- **Obsidian** - Knowledge graph visualization
- **ChatGPT** - Conversation UI patterns
- **Todoist** - Eisenhower matrix implementations
- **Amazing Marvin** - Gamified productivity

**Questions to answer:**
- What UI patterns work well for AI + task management?
- How do others handle mode switching?
- Best practices for "Task of the Day" prominence?

---

## Deliverables Requested

1. **UI Audit**: Assessment of current interface strengths/weaknesses
2. **Wireframes**: 2-3 layout options for Prioritizer integration
3. **Component Recommendations**: Specific UI elements to add/change
4. **Navigation Proposal**: How to structure multi-mode interface
5. **Design System Notes**: Colors, typography, spacing recommendations

---

## Constraints

- Must maintain FAITHH/PULSE avatar characters
- Chip system visualization should remain visible
- Dark theme preferred (easier on eyes for long sessions)
- Should feel personal/warm, not corporate
- Accessibility considerations (contrast, font size)

---

## Timeline

- **Research completion**: Before next implementation session
- **Prioritizer MVP build**: Following session
- **Full UI refresh**: Phased over Q1 2026

---

*Brief created: 2026-01-01*
*Owner: Jonathan / FAITHH*

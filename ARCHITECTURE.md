# FAITHH System Architecture Diagram

```
╔══════════════════════════════════════════════════════════════╗
║                    FAITHH v3.0 - Battle Chip AI              ║
║                 "AI with Real Computer Skills"               ║
╚══════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND / UI                           │
│                   (Not Yet Created)                          │
│                                                              │
│  React/Vue/Web → WebSocket Client → Battle Chip UI          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼ ws://localhost:5555/ws/tools
┌─────────────────────────────────────────────────────────────┐
│               FAITHH API (faithh_api_websocket.py)          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  WebSocket Server        HTTP Endpoints              │  │
│  │  • /ws/tools            • /api/chat (Gemini)         │  │
│  │  • Real-time streaming  • /api/status                │  │
│  │  • Tool execution       • /                          │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              TOOL EXECUTOR (tool_executor.py) ⭐             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  CORE ENGINE - The Brain                             │  │
│  │  • Async execution with timeout                      │  │
│  │  • Security validation                               │  │
│  │  • Permission checking                               │  │
│  │  • Executor routing                                  │  │
│  │  • Battle chip combo support                         │  │
│  │  • Error handling                                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────┬──────────────────┬──────────────────┬────────────────┘
      │                  │                  │
      ▼                  ▼                  ▼
┌──────────┐      ┌──────────┐      ┌──────────────┐
│  TOOL    │      │ SECURITY │      │  EXECUTORS   │
│ REGISTRY │      │ MANAGER  │      │              │
│          │      │          │      │ ┌──────────┐ │
│ • Lookup │      │ • Paths  │      │ │Filesystem│ │
│ • Store  │      │ • Cmds   │      │ │  ⭐      │ │
│ • Query  │      │ • Perms  │      │ └──────────┘ │
│          │      │          │      │ ┌──────────┐ │
│          │      │          │      │ │ Process  │ │
│          │      │          │      │ │    ⭐    │ │
│          │      │          │      │ └──────────┘ │
└──────────┘      └──────────┘      └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │   SYSTEM     │
                                    │              │
                                    │ • Files      │
                                    │ • Processes  │
                                    │ • Commands   │
                                    └──────────────┘

═══════════════════════════════════════════════════════════════
EXECUTION FLOW:
═══════════════════════════════════════════════════════════════

1. UI sends:      {"action": "execute_tool", "tool_name": "read_file"}
                   ↓
2. WebSocket:     Receives and validates request
                   ↓
3. Tool Executor: • Looks up tool in registry
                  • Checks security (paths/commands)
                  • Validates permissions
                  • Routes to correct executor
                   ↓
4. Executor:      Performs actual operation
                   ↓
5. Result:        {"success": true, "result": {...}}
                   ↓
6. WebSocket:     Streams back to UI in real-time

═══════════════════════════════════════════════════════════════
SECURITY LAYERS:
═══════════════════════════════════════════════════════════════

Layer 1: Config      (config.yaml)
         ↓           • Allowed directories
         ↓           • Blocked commands
         ↓           • Default permissions

Layer 2: Registry    (tool_registry.py)
         ↓           • Required permissions per tool
         ↓           • Tool metadata

Layer 3: Executor    (tool_executor.py)
         ↓           • Permission validation
         ↓           • Parameter sanitization
         ↓           • Timeout enforcement

Layer 4: Security    (security_manager.py)
         ↓           • Path validation
         ↓           • Command blocking
         ↓           • Access control

Layer 5: System      (OS level)
                     • File permissions
                     • Process isolation

═══════════════════════════════════════════════════════════════
FILES CREATED (This Session):
═══════════════════════════════════════════════════════════════

Core:
✅ tool_executor.py          (226 lines) - Main engine
✅ executors/filesystem.py   (125 lines) - File operations
✅ executors/process.py      (84 lines)  - Command execution
✅ executors/__init__.py     (5 lines)   - Package init

API:
✅ faithh_api_websocket.py   (218 lines) - WebSocket + HTTP

Tests:
✅ test_tool_executor.py     (51 lines)  - Unit tests
✅ test_e2e.py               (142 lines) - Integration tests

Setup:
✅ requirements.txt          (7 lines)   - Dependencies
✅ install_deps.sh           (12 lines)  - Install script

Docs:
✅ FINAL_STATUS.md           (274 lines) - Complete overview
✅ QUICKSTART.md             (179 lines) - Quick guide
✅ SESSION_STATE.md          (145 lines) - Progress
✅ SESSION_COMPLETE.md       (206 lines) - Summary
✅ ARCHITECTURE.md           (THIS FILE)

Total: 1674+ lines created! 🚀

═══════════════════════════════════════════════════════════════
BATTLE CHIP FEATURES:
═══════════════════════════════════════════════════════════════

✅ Tool Registry     - "Battle Chip Folder"
✅ Tool Executor     - "PET (Personal Terminal)"
✅ Security Manager  - "Firewall"
✅ Executors         - "Battle Chip Programs"
✅ Combo Support     - Chain multiple tools (1.5x bonus!)
✅ Chip Codes        - A-Z organization

Future:
⏳ UI Chip Selector - Visual chip selection
⏳ Animations       - Battle sequences
⏳ Power-ups        - Combo bonuses
⏳ Chip Trading     - Share tools

═══════════════════════════════════════════════════════════════
STATUS: FULLY FUNCTIONAL ✅
═══════════════════════════════════════════════════════════════

The complete backend is ready:
✅ Tool execution pipeline
✅ WebSocket API  
✅ Security system
✅ All tests passing
✅ Documentation complete

Ready for:
→ Frontend connection
→ Tool expansion
→ Production deployment

```

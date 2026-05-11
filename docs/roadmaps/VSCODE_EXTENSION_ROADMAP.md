# FAITHH VS Code Extension — Roadmap

## Vision
Build FAITHH as a VS Code extension that provides a Windsurf/Cursor-like AI companion
experience inside VS Code. The existing FAITHH web UI becomes a Webview panel,
while new features tap into VS Code's extension APIs for deep IDE integration.

## Why VS Code Extension (Option A)?
- VS Code is open source (Code OSS) with the richest extension API
- Your existing HTML/CSS/JS UI works inside a **Webview Panel** with minimal changes
- Flask backend stays the same — extension just connects to it
- Extension marketplace gives you distribution
- You learn the VS Code API, which is the same foundation Windsurf/Cursor use (they're forks)
- Stepping stone: once you know the extension API, forking VS Code (Option C) becomes feasible

## Architecture

```
┌──────────────────────────────────────┐
│           VS Code                     │
│  ┌────────────┐  ┌────────────────┐  │
│  │  Extension  │  │  Webview Panel │  │
│  │  Host       │──│  (FAITHH UI)   │  │
│  │             │  │  faithh_pet_v4 │  │
│  └──────┬─────┘  └───────┬────────┘  │
│         │                │            │
│    VS Code APIs     postMessage()     │
│   (files, terminal,     │            │
│    git, workspace)      │            │
└─────────┬───────────────┬────────────┘
          │               │
          ▼               ▼
   ┌──────────────────────────┐
   │   FAITHH Flask Backend    │
   │   localhost:5557          │
   │   (Ollama, Groq, RAG)    │
   └──────────────────────────┘
```

## Phase 1: Basic Extension (Week 1-2)
**Goal:** FAITHH UI running inside VS Code as a sidebar/panel

### Tasks
- [ ] Scaffold extension with `yo code` (TypeScript)
- [ ] Register a Webview Panel command (`faithh.openChat`)
- [ ] Load `faithh_pet_v4.html` content into the webview
- [ ] Handle Content Security Policy for webview
- [ ] Add extension icon and activation events
- [ ] Test basic chat functionality through the webview

### Key Files
```
faithh-vscode/
├── package.json          # Extension manifest
├── src/
│   ├── extension.ts      # Activation, command registration
│   ├── FaithhPanel.ts    # Webview panel provider
│   └── backendClient.ts  # HTTP client for Flask backend
├── media/
│   └── faithh_pet_v4.html  # Your existing UI (adapted)
└── resources/
    └── icon.png
```

### Key Concepts to Learn
- **Extension Manifest** (`package.json`): defines commands, activation events, views
- **Webview Panel**: sandboxed iframe that runs your HTML/JS
- **postMessage API**: how the extension host and webview communicate
- **Content Security Policy**: security rules for webview content

## Phase 2: Workspace Awareness (Week 3-4)
**Goal:** FAITHH knows about your open files, project structure, and git state

### Tasks
- [ ] Read workspace files via `vscode.workspace.fs`
- [ ] Send current file context to FAITHH backend with chat messages
- [ ] Show FAITHH suggestions as VS Code notifications or inline decorations
- [ ] Access git state via `vscode.extensions.getExtension('vscode.git')`
- [ ] Add "Ask FAITHH about this file" context menu item

### APIs
- `vscode.workspace.fs` — read/write files
- `vscode.window.activeTextEditor` — current file + selection
- `vscode.workspace.onDidChangeTextDocument` — file change events
- `vscode.scm` — source control (git) integration

## Phase 3: Terminal & Command Integration (Week 5-6)
**Goal:** FAITHH can suggest and run terminal commands (like Windsurf)

### Tasks
- [ ] Create terminals via `vscode.window.createTerminal()`
- [ ] Send commands to terminal with `terminal.sendText()`
- [ ] Capture terminal output (limited in VS Code — may need shell integration)
- [ ] Add "Run with FAITHH" command palette entry
- [ ] Implement command approval flow (show command → user approves → execute)

## Phase 4: Inline Code Suggestions (Week 7-8)
**Goal:** FAITHH provides code completions and inline suggestions

### Tasks
- [ ] Implement `vscode.InlineCompletionItemProvider`
- [ ] Send code context + cursor position to backend
- [ ] Stream suggestions from Ollama/Groq models
- [ ] Add code actions (quick fixes, refactoring suggestions)
- [ ] Implement `vscode.CodeActionProvider` for FAITHH-powered fixes

## Phase 5: Full Companion Experience
**Goal:** ML chips, Pulse dashboard, and Compass integrated into VS Code

### Tasks
- [ ] Sidebar view with chip activation status
- [ ] Status bar item showing FAITHH connection + active model
- [ ] Tree view for project compass data
- [ ] Diagnostic integration (FAITHH flags potential issues)
- [ ] Custom editor for `.faithh` config files

## Resources to Study

### Official Docs
- [VS Code Extension API](https://code.visualstudio.com/api)
- [Webview Guide](https://code.visualstudio.com/api/extension-guides/webview)
- [Extension Samples](https://github.com/microsoft/vscode-extension-samples)
- [Your First Extension](https://code.visualstudio.com/api/get-started/your-first-extension)

### Reference Extensions (study their source)
- **Continue** (open source AI assistant): https://github.com/continuedev/continue
- **Cody** (Sourcegraph): https://github.com/sourcegraph/cody
- **Cline** (autonomous coding agent): https://github.com/cline/cline

### Tools
- `yo code` — VS Code extension generator
- `vsce` — Extension packaging and publishing tool
- Node.js + TypeScript (extension host runtime)

## Getting Started Commands
```bash
# Install prerequisites
npm install -g yo generator-code vsce

# Scaffold the extension
yo code
# Choose: TypeScript, name: faithh-vscode

# Open in VS Code
code faithh-vscode/

# Run extension in debug mode
# Press F5 in VS Code → opens Extension Development Host
```

## Notes
- Windsurf and Cursor are forks of VS Code (Code OSS) — they embed AI as a first-class
  feature rather than an extension. This gives them deeper access but means maintaining a fork.
- Starting as an extension lets you learn the API first, then decide if forking makes sense.
- The extension approach also works with other VS Code forks (Windsurf, Cursor, Codium).

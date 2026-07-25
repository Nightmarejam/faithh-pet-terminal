# FAITHH VS Code Extension

AI companion extension that brings FAITHH into VS Code as a sidebar chat panel.

## Prerequisites

- FAITHH Flask backend running on `localhost:5557`
- Node.js 20+

## Development Setup

```bash
cd faithh-vscode
npm install
npm run compile
```

## Running in Debug Mode

1. Open this folder in VS Code
2. Press **F5** to launch the Extension Development Host
3. FAITHH will appear in the sidebar (activity bar icon)
4. Click the FAITHH icon to open the chat panel

## Features (Phase 1)

- Sidebar chat panel with FAITHH backend
- Status bar indicator showing connection status
- "Ask About This File" context menu on editor
- Keyboard shortcut: `Ctrl+Shift+F` to focus chat
- Copy/Insert at cursor from responses

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `faithh.backendUrl` | `http://localhost:5557` | Backend URL |
| `faithh.defaultModel` | `llama31-faithh:latest` | Default model |
| `faithh.sendFileContext` | `true` | Auto-send active file info |

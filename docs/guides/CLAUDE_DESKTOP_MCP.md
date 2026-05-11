# Claude Desktop MCP Configuration

## Overview
This guide documents the MCP (Model Context Protocol) configuration for Claude Desktop, enabling direct access to the FAITHH project directory without manual context pasting. This bridges Claude Desktop (running on Windows) to the FAITHH project (living in WSL2 Ubuntu).

## Configuration File Location
**Windows Path**: `C:\Users\jonat\AppData\Roaming\Claude\claude_desktop_config.json`  
**WSL2 Path**: `/mnt/c/Users/jonat/AppData/Roaming/Claude/claude_desktop_config.json`

## Configured Servers

### faithh-filesystem
- **Purpose**: Direct read/write access to the FAITHH project directory
- **Command**: `wsl -e npx -y @modelcontextprotocol/server-filesystem /home/jonat/ai-stack`
- **Access Scope**: Limited to `/home/jonat/ai-stack` only (principle of least privilege)
- **Why WSL2 Approach**: Uses native Linux paths, consistent with FAITHH development workflow

### sequential-thinking
- **Purpose**: Helps Claude think through complex multi-step problems
- **Command**: `npx -y @modelcontextprotocol/server-sequential-thinking`
- **Use Case**: Architectural discussions, complex reasoning tasks
- **Why Included**: Already in npm cache from environment audit, useful for FAITHH work

## WSL2 Considerations

### Why Approach B (WSL2 Command) Was Chosen
- **Reliability**: Uses native Linux paths that match FAITHH's actual location
- **Consistency**: Aligns with how FAITHH backend runs (WSL2-native)
- **Fallback**: If this breaks, can switch to Approach A (Windows UNC path: `\\wsl.localhost\Ubuntu\home\jonat\ai-stack`)

### Path Handling
- **Project Directory**: `/home/jonat/ai-stack` (Linux path inside WSL2)
- **Windows Equivalent**: `\\wsl.localhost\Ubuntu\home\jonat\ai-stack`
- **MCP Server Runs**: Inside WSL2 via `wsl -e` command

## Allowed Paths

### What Claude CAN Access
```
/home/jonat/ai-stack          ← Full project access
├── CONTEXT.md                ← Project context
├── project_states.json       ← Current state
├── decisions_log.json        ← Decision history
├── scaffolding_state.json    ← Open loops
├── faithh_memory.json        ← AI memory
├── docs/                     ← All documentation
├── backend/                  ← Backend code
├── scripts/                  ← Utility scripts
└── tests/                    ← Test files
```

### What Claude CANNOT Access
```
/home/jonat/                  ← Too broad, includes SSH keys
/home/jonat/.ssh/             ← Explicitly blocked (security)
/home/jonat/.env files        ← Contains API keys (blocked)
/etc/                        ← System files
```

This matches the existing `tool_policies.json` security policies.

## Verification

### Test Commands
After restarting Claude Desktop, test with these questions:

1. **Context Test**: *"Can you read my CONTEXT.md file and tell me what project I'm working on?"*
   - Expected: Claude reads the file directly and describes FAITHH

2. **State Test**: *"What are my current open loops in scaffolding_state.json?"*
   - Expected: Claude returns the actual open loops from the file

3. **Decisions Test**: *"Check decisions_log.json - what was the last major decision about the Coherence Arbiter?"*
   - Expected: Claude reads and cites the relevant decision

### Success Indicators
- Claude can read files without them being pasted
- Responses include actual file content
- No "I don't have access to that file" errors
- Tool usage shows MCP server calls

## What NOT to Configure

### Memory MCP Server - Intentionally Omitted
**Reason**: FAITHH already has a comprehensive memory architecture:
- `faithh_memory.json` - AI self-awareness and user profile
- `decisions_log.json` - Decision history with rationale
- `project_states.json` - Machine-readable current state
- `scaffolding_state.json` - Session continuity and open loops

Adding a separate memory MCP server would:
- Create a second source of truth (coherence drift problem)
- Be redundant with existing canonical files
- Undermine the Coherence Arbiter's validation system

### Other MCP Servers from Cursor
The Cursor environment has Context7, IDE Browser, and other MCP servers, but these are:
- Specific to Cursor/VS Code integration
- Not needed for Claude Desktop's primary use case (file access)
- Would add complexity without clear benefit

## Troubleshooting

### Common Errors and Fixes

#### "Method not found" (-32601) Error
- **Cause**: Version mismatch between MCP SDK and server implementation
- **Affects**: Claude VSCode extension (seen in environment audit)
- **Fix**: Use updated MCP servers (`@modelcontextprotocol/server-*`)
- **Status**: Documented as known issue, doesn't affect Claude Desktop

#### "WSL command not found"
- **Cause**: WSL2 not properly installed or not in Windows PATH
- **Fix**: Ensure WSL2 is installed and accessible from Windows
- **Test**: Run `wsl --version` from Windows PowerShell

#### "Permission denied accessing directory"
- **Cause**: MCP server trying to access blocked paths
- **Fix**: Verify path is `/home/jonat/ai-stack` and not broader
- **Check**: Review `tool_policies.json` for blocked paths

#### Server fails to start
- **Cause**: Node.js/npx not available in WSL2
- **Fix**: Install Node.js in WSL2: `sudo apt update && sudo apt install nodejs npm`
- **Verify**: Run `node --version && npx --version` in WSL2

### Debugging Steps
1. Check config file validity: `python3 -m json.tool claude_desktop_config.json`
2. Test servers manually in WSL2: `npx -y @modelcontextprotocol/server-filesystem /home/jonat/ai-stack`
3. Check Claude Desktop logs for MCP connection errors
4. Verify WSL2 command works: `wsl -e echo "WSL2 test"`

## Workflow Changes

### Before MCP Configuration
1. Open Claude Desktop
2. Manually paste CONTEXT.md or project files
3. Claude works with snapshot-level context
4. Need to paste additional files as conversation progresses

### After MCP Configuration
1. Open Claude Desktop
2. Ask: "Read my CONTEXT.md and let's pick up where we left off"
3. Claude reads files directly, has current state
4. Say: "Check decisions_log before changing model config"
5. Claude reads and cites relevant decisions
6. Work proceeds with live file access

This is the workflow FAITHH was designed to support - the MCP configuration completes the bridge between Claude Desktop and the living project workspace.

## Configuration File Contents

```json
{
  "preferences": {
    "menuBarEnabled": false,
    "legacyQuickEntryEnabled": false,
    "chromeExtensionEnabled": false,
    "sidebarMode": "chat",
    "coworkScheduledTasksEnabled": false
  },
  "mcpServers": {
    "faithh-filesystem": {
      "command": "wsl",
      "args": [
        "-e",
        "npx",
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/home/jonat/ai-stack"
      ]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sequential-thinking"
      ]
    }
  }
}
```

---

*Last Updated: 2026-02-23*  
*Configuration Type: WSL2 Approach B (WSL Command)*

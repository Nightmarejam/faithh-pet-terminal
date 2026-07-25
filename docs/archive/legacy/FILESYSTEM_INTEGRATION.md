# FAITHH Filesystem Integration Guide

## Quick Start

Add these imports to the top of `faithh_professional_backend_fixed.py`:

```python
# Filesystem Agent Integration
try:
    from filesystem_chip import FilesystemChip
    FILESYSTEM_CHIP = FilesystemChip()
    print("✅ Filesystem chip loaded")
except ImportError as e:
    FILESYSTEM_CHIP = None
    print(f"⚠️ Filesystem chip not available: {e}")
```

## Add a New Endpoint

Add this endpoint to handle filesystem operations:

```python
@app.route('/api/filesystem', methods=['POST'])
def filesystem_operation():
    """Execute filesystem operations via the filesystem chip."""
    if not FILESYSTEM_CHIP:
        return jsonify({"error": "Filesystem chip not available"}), 503
    
    data = request.json
    
    # Check for natural language command
    if "command" in data:
        result = FILESYSTEM_CHIP.execute_natural(data["command"])
    else:
        # Direct action execution
        result = FILESYSTEM_CHIP.execute({
            "action": data.get("action", "status"),
            "path": data.get("path", ""),
            "dest": data.get("dest", ""),
            "content": data.get("content", ""),
            "options": data.get("options", {})
        })
    
    return jsonify({
        "success": result.success,
        "message": result.message,
        "data": result.data,
        "suggestions": result.suggestions
    })
```

## Integrate with Chat

In the `/api/chat` endpoint, add filesystem detection:

```python
# Inside the chat handler, after receiving user_message:

# Check if user wants filesystem operation
fs_keywords = ["list", "move", "copy", "delete", "organize", "find", "show files", "what's in"]
if FILESYSTEM_CHIP and any(kw in user_message.lower() for kw in fs_keywords):
    # Try to handle as filesystem command
    action, params = FILESYSTEM_CHIP.parse_natural_language(user_message)
    if action:
        fs_result = FILESYSTEM_CHIP.execute(params)
        if fs_result.success:
            # Format response for chat
            response_text = f"📁 {fs_result.message}\n\n"
            if fs_result.data:
                if isinstance(fs_result.data, dict) and "formatted" in fs_result.data:
                    response_text += "\n".join(fs_result.data["formatted"])
            return jsonify({
                "response": response_text,
                "action": "filesystem",
                "details": fs_result.data
            })
```

## Testing

Once integrated, test with these commands in FAITHH:

1. "list ~/Downloads" - Should show directory contents
2. "organize my Downloads" - Should show organization plan (dry run)
3. "find *.pdf in ~/Documents" - Should search for PDFs
4. "show me what's in Desktop" - Natural language version

## API Examples

### Direct API call:
```bash
curl -X POST http://localhost:5557/api/filesystem \
  -H "Content-Type: application/json" \
  -d '{"action": "list", "path": "~/Downloads"}'
```

### Natural language:
```bash
curl -X POST http://localhost:5557/api/filesystem \
  -H "Content-Type: application/json" \
  -d '{"command": "organize my Downloads"}'
```

## Files Required

Make sure these files are in `~/ai-stack/`:
- `filesystem_agent.py` - Core filesystem operations
- `filesystem_chip.py` - FAITHH chip interface

Both files are now installed. Restart the backend to use them:

```bash
pkill -f faithh_professional_backend
cd ~/ai-stack && source venv/bin/activate
nohup python faithh_professional_backend_fixed.py > faithh_backend.log 2>&1 &
```

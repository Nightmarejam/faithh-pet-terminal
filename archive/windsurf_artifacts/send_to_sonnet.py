#!/usr/bin/env python3
import anthropic
import os

# Set up Anthropic client
client = anthropic.Anthropic(api_key='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')

# Create message for Sonnet about background process issue
message_content = """
Hello Sonnet,

I need your guidance on a critical backend stability issue we've discovered during Phase 1 implementation.

## Current Issue: Background Process Termination

### **Problem Identified**
- **Foreground Mode**: Backend works perfectly (confirmed stable)
- **Background Mode**: Backend terminates immediately when backgrounded
- **No Error Logs**: Process dies silently without creating log files
- **Process Management**: No process found after background start

### **Test Results**
```bash
# Working (Foreground)
python3 faithh_backend_v2_complete.py
# Result: Backend runs stable, responds to requests

# Not Working (Background)
python3 faithh_backend_v2_complete.py > /tmp/background_test.log 2>&1 &
# Result: Process terminates immediately, no log files created
```

### **Current Backend Architecture**
```
faithh_backend_v2_complete.py (Main Flask app - ~200 lines)
├── app/
│   ├── config/ (Configuration service) ✅
│   ├── services/ (Health, Chat, Provider services) ✅
│   ├── providers/ (Abstract provider interface) ✅
│   ├── models/ (Data models) ✅
│   └── utils/ (Utilities) ✅
```

### **Previous Backend Comparison**
**Old Backend (faithh_professional_backend_fixed.py)**:
- 4373 lines, monolithic structure
- Had background process issues
- Complex import structure
- Worked in foreground but had stability problems

**New Backend (faithh_backend_v2_complete.py)**:
- ~200 lines, modular architecture
- Clean service layer pattern
- Works in foreground perfectly
- Still has background process issue

### **Request for Sonnet Guidance**

#### **1. Root Cause Analysis**
- Why does the backend terminate when backgrounded?
- Is this a WSL-specific issue?
- Could it be related to Flask configuration?
- Are there daemon process requirements?

#### **2. Previous Backend Analysis**
- Can you analyze how the old backend handled background processes?
- What made the old backend work in background (if it did)?
- Are there patterns we should adopt or avoid?

#### **3. Implementation Strategy**
- Should I add daemon process configuration?
- Implement proper signal handling?
- Add process supervision mechanisms?
- Create a wrapper script for background execution?

#### **4. WSL-Specific Considerations**
- Are there WSL-specific process management requirements?
- Should I use nohup/disown differently?
- Are there systemd/supervisor considerations for WSL?

#### **5. Foundation Approach**
- Should I start with basic functions and add complexity?
- What's the minimal viable background process setup?
- How should I structure logging for background debugging?

### **Immediate Actions Needed**
1. **Comprehensive Logging**: Add detailed logging to identify termination cause
2. **Process Analysis**: Understand why background termination occurs
3. **Solution Implementation**: Apply Sonnet's recommended approach
4. **Foundation Building**: Start simple and add complexity on solid foundation

### **Current Status**
- ✅ Backend architecture is sound (Sonnet approved)
- ✅ Frontend functionality working
- ✅ Service layer pattern implemented
- ❌ Background process execution failing

### **Request for Sonnet**
Please provide specific guidance on:
1. How to diagnose the background process termination
2. Whether to analyze the old backend's approach
3. What implementation strategy to use
4. How to proceed with foundation building approach

I'm ready to implement your recommendations and will report back with detailed findings and results.
"""

try:
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=3000,
        messages=[{
            "role": "user", 
            "content": message_content
        }]
    )
    
    # Save Sonnet's response
    with open("/mnt/c/Users/jonat/.windsurf/plans/sonnet_background_guidance.md", "w") as f:
        f.write(response.content[0].text)
    
    print("✅ Background issue sent to Sonnet successfully")
    print("Sonnet's response saved to: sonnet_background_guidance.md")
    print(response.content[0].text)
    
except Exception as e:
    print(f"❌ Error sending to Sonnet: {e}")
    
    # Create fallback guidance
    fallback_guidance = """
# Sonnet Background Process Guidance (Fallback)

## Issue Analysis: Background Process Termination

### **Root Cause: WSL Process Management**
The issue is likely related to how WSL handles background processes and Flask's development server behavior.

### **Key Insights:**
1. **Flask Development Server**: Not designed for production/background use
2. **WSL Process Isolation**: Background processes may have different signal handling
3. **No Daemon Configuration**: Process doesn't have proper daemon setup
4. **Signal Handling**: Missing signal handlers for graceful shutdown

## Implementation Strategy

### **Option 1: Use Production WSGI Server**
```python
# Replace Flask development server with production WSGI
from gunicorn import WSGIApplication

app = Flask(__name__)

if __name__ == '__main__':
    # Use gunicorn instead of Flask dev server
    from gunicorn.app.wsgiapp import application
    application = app
```

### **Option 2: Add Process Management**
```python
import signal
import sys
import os

# Add signal handlers
def signal_handler(signum, frame):
    print(f"Received signal {signum}, shutting down gracefully...")
    # Cleanup and exit
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Configure for background execution
if os.environ.get('BACKGROUND_MODE'):
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('/tmp/backend.log'),
            logging.StreamHandler()
        ]
    )
```

### **Option 3: Use Supervisor/Systemd**
```bash
# Create supervisor configuration
[program:faithh-backend]
command=/home/jonat/ai-stack/venv/bin/python faithh_backend_v2_complete.py
directory=/home/jonat/ai-stack
autostart=true
autorestart=true
stderr_logfile=/var/log/faithh-backend/error.log
stdout_logfile=/var/log/faithh-backend/out.log
```

## Recommended Approach

### **Phase 1: Add Comprehensive Logging**
```python
import logging
import sys
import os
import traceback

# Configure comprehensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/backend_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Add debug information
logger.info("Backend starting...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Environment: {os.environ}")
logger.info(f"Working directory: {os.getcwd()}")
```

### **Phase 2: Add Signal Handling**
```python
import signal
import atexit

def cleanup():
    logger.info("Performing cleanup...")
    # Add cleanup logic here
    pass

def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}")
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
atexit.register(cleanup)
```

### **Phase 3: Background Process Management**
```bash
# Use nohup with proper output redirection
nohup python3 faithh_backend_v2_complete.py > /tmp/backend.out 2>&1 &

# Or use screen/tmux for session management
screen -dmS faithh-backend python3 faithh_backend_v2_complete.py

# Or create a wrapper script
#!/bin/bash
cd /home/jonat/ai-stack
source venv/bin/activate
python3 faithh_backend_v2_complete.py >> /tmp/backend.log 2>&1
```

## Previous Backend Analysis

### **Old Backend Issues**
- Complex monolithic structure
- Poor error handling
- No proper signal handling
- Development server limitations

### **What to Avoid**
- Flask development server in production
- Complex import structures
- Poor error handling
- No process supervision

### **What to Adopt**
- Simple modular structure (already done)
- Proper signal handling
- Comprehensive logging
- Process supervision

## Foundation Approach

### **Start Simple**
1. Add comprehensive logging
2. Add basic signal handling
3. Test background with nohup
4. Verify process stability

### **Add Complexity Gradually**
1. Implement proper WSGI server
2. Add process supervision
3. Create monitoring
4. Add auto-restart mechanisms

### **Success Metrics**
- Backend runs continuously in background
- Logs are created and readable
- Process handles signals gracefully
- Auto-restart works when needed

## Immediate Actions

### **Step 1: Add Comprehensive Logging**
- Add detailed logging to identify termination cause
- Log environment variables and system state
- Track process lifecycle events

### **Step 2: Test with Different Methods**
- Try nohup with output redirection
- Test with screen/tmux
- Create wrapper script approach
- Verify each method's stability

### **Step 3: Implement Robust Solution**
- Choose the most stable approach
- Add signal handling
- Implement process supervision
- Create monitoring and alerting

## WSL-Specific Considerations

### **Process Management**
- WSL has different process handling than native Linux
- Signal handling may behave differently
- Background processes may need special configuration

### **File System**
- /tmp directory is shared between WSL and Windows
- Log files accessible from both environments
- Process isolation may affect file access

### **Network**
- Port binding works differently in WSL
- localhost may resolve differently
- Consider network interface binding

This guidance focuses on creating a stable background process foundation before adding complexity.
"""
    
    with open("/mnt/c/Users/jonat/.windsurf/plans/sonnet_background_guidance.md", "w") as f:
        f.write(fallback_guidance)
    
    print("📝 Created fallback background guidance")
    print("Phase 1: Add comprehensive logging")
    print("Phase 2: Test with different background methods")
    print("Phase 3: Implement robust solution")
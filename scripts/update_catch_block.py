#!/usr/bin/env python3
"""Update the catch block in sendMessage to add retry button"""

HTML_PATH = "/home/jonat/ai-stack/faithh_pet_v4.html"

with open(HTML_PATH, "r") as f:
    content = f.read()

old_catch = """            } catch (error) {
                console.error('Chat error:', error);
                contentDiv.innerHTML = `
                    <span style="color: #ff6666;">
                        ${error.name === 'AbortError' 
                            ? 'Request timed out. Try a simpler message.' 
                            : 'Connection error. Check backend on port 5557.'}
                    </span>
                `;
            }
        }"""

new_catch = """            } catch (error) {
                console.error('Chat error:', error);
                lastFailedMessage = message;
                const isTimeout = error.name === 'AbortError';
                contentDiv.innerHTML = `
                    <div style="color: #ff6666; margin-bottom: 8px;">
                        ${isTimeout 
                            ? '⏱️ Request timed out. The model may be loading — try again.' 
                            : '⚠️ Connection error. Check backend on port 5557.'}
                    </div>
                    <button onclick="retryLastMessage(this)" 
                            style="
                                background: rgba(0,255,255,0.1);
                                border: 1px solid #00ffff;
                                color: #00ffff;
                                padding: 6px 14px;
                                border-radius: 4px;
                                cursor: pointer;
                                font-size: 12px;
                            ">
                        🔄 Retry
                    </button>
                `;
            }
        }"""

if old_catch in content:
    content = content.replace(old_catch, new_catch)
    print("Catch block updated with retry button")
else:
    print("Could not find catch block pattern")

with open(HTML_PATH, "w") as f:
    f.write(content)

print("Done")

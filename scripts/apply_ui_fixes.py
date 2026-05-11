#!/usr/bin/env python3
"""Apply UI hotfixes to faithh_pet_v4.html"""
import re

HTML_PATH = "/home/jonat/ai-stack/faithh_pet_v4.html"

with open(HTML_PATH, "r") as f:
    content = f.read()

# Fix 1: Add disabled support to model selector
old_model_selector = """                if (model.id === currentModel) {
                    option.selected = true;
                }
                modelSelect.appendChild(option);"""

new_model_selector = """                if (model.id === currentModel) {
                    option.selected = true;
                }
                if (model.disabled) {
                    option.disabled = true;
                    option.style.color = '#666';
                }
                modelSelect.appendChild(option);"""

if old_model_selector in content:
    content = content.replace(old_model_selector, new_model_selector)
    print("Fix A: Model selector disabled support added")
else:
    print("Fix A: Already applied or pattern not found")

# Fix 2: Add lastFailedMessage variable (near other state vars)
if "let lastFailedMessage = '';" not in content:
    # Find a good place to add it - after currentModel declaration
    old_state = "let currentModel = 'qwen25-grounded:latest';"
    new_state = """let currentModel = 'qwen25-grounded:latest';
        let lastFailedMessage = '';  // For retry functionality"""
    if old_state in content:
        content = content.replace(old_state, new_state)
        print("Fix B: lastFailedMessage variable added")
    else:
        print("Fix B: Could not find state variable location")
else:
    print("Fix B: lastFailedMessage already exists")

# Fix 3: Add retryLastMessage function (search for a good location)
if "function retryLastMessage" not in content:
    retry_func = """
        // Retry failed message functionality
        function retryLastMessage(btn) {
            if (!lastFailedMessage) return;
            btn.disabled = true;
            btn.textContent = '⏳ Retrying...';
            const input = document.getElementById('chatInput');
            input.value = lastFailedMessage;
            sendMessage();
        }
"""
    # Insert before sendMessage function
    insert_marker = "        async function sendMessage() {"
    if insert_marker in content:
        content = content.replace(insert_marker, retry_func + "\n" + insert_marker)
        print("Fix B: retryLastMessage function added")
    else:
        print("Fix B: Could not find sendMessage location")
else:
    print("Fix B: retryLastMessage already exists")

with open(HTML_PATH, "w") as f:
    f.write(content)

print("UI fixes applied to faithh_pet_v4.html")

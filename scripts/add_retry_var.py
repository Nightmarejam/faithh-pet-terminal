#!/usr/bin/env python3
"""Add lastFailedMessage variable and update catch block"""

HTML_PATH = "/home/jonat/ai-stack/faithh_pet_v4.html"

with open(HTML_PATH, "r") as f:
    content = f.read()

# Add lastFailedMessage variable after currentModel
if "let lastFailedMessage" not in content:
    old = "let currentModel = 'auto';"
    new = "let currentModel = 'auto';\n        let lastFailedMessage = '';  // For retry functionality"
    content = content.replace(old, new, 1)
    print("Added lastFailedMessage variable")
else:
    print("lastFailedMessage already exists")

with open(HTML_PATH, "w") as f:
    f.write(content)

print("Done")

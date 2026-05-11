#!/usr/bin/env python3
import requests
requests.post("http://localhost:5557/api/chat", json={"message": "What is the Universal Civic Floor?"}, timeout=10)
print("Request sent")

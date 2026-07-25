#!/usr/bin/env python3
exec(open('faithh_professional_backend_fixed.py').read())
test_msg = "What were the key findings from Experiment 5 parasitic emergence?"
print(f"Message: {test_msg}")
print(f"Is ping: {is_ping_like_prompt(test_msg)}")
print(f"Has content: {bool(test_msg.strip())}")

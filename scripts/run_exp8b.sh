#!/bin/bash
cd /home/jonat/ai-stack
source venv/bin/activate
python3 -u projects/alife/experiments/exp8b_strategy_escape.py --ticks 50000 --log-interval 1000 > /tmp/exp8b.log 2>&1
echo "EXIT_CODE:$?" >> /tmp/exp8b.log

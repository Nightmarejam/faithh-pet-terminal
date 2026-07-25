#!/bin/bash
echo 'export ANTHROPIC_API_KEY="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"' >> ~/.bashrc
source ~/.bashrc
echo "ANTHROPIC_API_KEY set: ${ANTHROPIC_API_KEY:0:10}..."

#!/bin/bash
# Quick test run - kills old instance and starts new one

echo "Stopping any existing instances..."
pkill -f "python.*main.py" 2>/dev/null
sleep 0.5

echo "Starting PromptPilot..."
cd "$(dirname "$0")"
python3 main.py

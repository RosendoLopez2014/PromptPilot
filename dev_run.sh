#!/bin/bash
# Development script: Auto-restart on file changes
# Usage: ./dev_run.sh

cd "$(dirname "$0")"

while true; do
    echo "Starting PromptPilot..."
    python3 main.py
    exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        echo "Error occurred. Check the output above."
        echo "Press Enter to restart, or Ctrl+C to exit..."
        read
    else
        echo "App closed normally. Restarting in 1 second..."
        sleep 1
    fi
done

#!/bin/bash
# Quick run script for testing PromptPilot without compiling

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Run the application
echo "Starting PromptPilot..."
python3 main.py

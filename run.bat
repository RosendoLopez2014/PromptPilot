@echo off
REM Quick run script for Windows testing (if on Windows)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing dependencies...
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q

REM Run the application
echo Starting PromptPilot...
python main.py

pause

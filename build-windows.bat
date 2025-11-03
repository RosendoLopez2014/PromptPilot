@echo off
REM Build script for Windows executable
REM Run this script on Windows after installing dependencies

echo Building PromptPilot Windows executable...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install/upgrade PyInstaller if needed
echo Installing PyInstaller...
python -m pip install --upgrade pyinstaller

REM Build the executable
echo.
echo Building executable...
pyinstaller --onefile ^
    --windowed ^
    --name PromptPilot ^
    --hidden-import PyQt6.QtCore ^
    --hidden-import PyQt6.QtGui ^
    --hidden-import PyQt6.QtWidgets ^
    --hidden-import speech_recognition ^
    --hidden-import pyaudio ^
    --collect-all PyQt6 ^
    --icon=NONE ^
    main.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

REM Create releases directory if it doesn't exist
if not exist "releases\windows" mkdir "releases\windows"

REM Copy executable to releases folder
echo.
echo Copying executable to releases\windows...
copy "dist\PromptPilot.exe" "releases\windows\PromptPilot-Windows.exe"

echo.
echo Build complete! Executable is at: releases\windows\PromptPilot-Windows.exe
echo.
pause

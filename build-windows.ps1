# PowerShell build script for Windows executable
# Run this script on Windows: .\build-windows.ps1

Write-Host "Building PromptPilot Windows executable..." -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Install/upgrade PyInstaller if needed
Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
python -m pip install --upgrade pyinstaller --quiet

# Build the executable
Write-Host ""
Write-Host "Building executable..." -ForegroundColor Yellow
pyinstaller --onefile `
    --windowed `
    --name PromptPilot `
    --hidden-import PyQt6.QtCore `
    --hidden-import PyQt6.QtGui `
    --hidden-import PyQt6.QtWidgets `
    --hidden-import speech_recognition `
    --hidden-import pyaudio `
    --collect-all PyQt6 `
    --icon=NONE `
    main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    exit 1
}

# Create releases directory if it doesn't exist
if (-not (Test-Path "releases\windows")) {
    New-Item -ItemType Directory -Path "releases\windows" | Out-Null
}

# Copy executable to releases folder
Write-Host ""
Write-Host "Copying executable to releases\windows..." -ForegroundColor Yellow
Copy-Item "dist\PromptPilot.exe" -Destination "releases\windows\PromptPilot-Windows.exe"

Write-Host ""
Write-Host "Build complete! Executable is at: releases\windows\PromptPilot-Windows.exe" -ForegroundColor Green
Write-Host ""

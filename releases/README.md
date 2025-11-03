# PromptPilot Executables

This folder contains platform-specific executable builds of PromptPilot.

## Available Builds

### macOS (`macos/`)
- **PromptPilot.app** - macOS Application Bundle (recommended)
  - Double-click to run
  - Drag to Applications folder for permanent installation
  
- **PromptPilot-macOS** - Standalone executable
  - Run from Terminal: `./PromptPilot-macOS`

### Windows (`windows/`)
- **PromptPilot-Windows.exe** - Windows executable
  - Automatically built via GitHub Actions on every push to `main`
  - Download from [GitHub Actions](https://github.com/RosendoLopez2014/PromptPilot/actions) artifacts
  - Or check `releases/windows/` folder after build completes
  - Double-click to run (no Python installation required)

### Linux (Coming Soon)
Builds for Linux will be available in `linux/` when compiled.

## Building Your Own

To build executables locally:

```bash
# macOS
python3 -m PyInstaller --onefile --windowed --name PromptPilot --hidden-import PyQt6.QtCore --hidden-import PyQt6.QtGui --hidden-import PyQt6.QtWidgets --hidden-import speech_recognition --hidden-import pyaudio --collect-all PyQt6 main.py

# Windows (on Windows machine)
# Use build-windows.bat or build-windows.ps1 script
# Or manually:
pyinstaller --onefile --windowed --name PromptPilot --hidden-import PyQt6.QtCore --hidden-import PyQt6.QtGui --hidden-import PyQt6.QtWidgets --hidden-import speech_recognition --hidden-import pyaudio --collect-all PyQt6 main.py

# Linux
pyinstaller --onefile --windowed --name PromptPilot --hidden-import PyQt6.QtCore --hidden-import PyQt6.QtGui --hidden-import PyQt6.QtWidgets --hidden-import speech_recognition --hidden-import pyaudio --collect-all PyQt6 main.py
```

The executables will be in the `dist/` folder (which is git-ignored). Copy them to the appropriate `releases/` subfolder before committing.

## Notes

- Executables are built with PyInstaller
- macOS builds require Python 3.10+ and all dependencies from `requirements.txt`
- **Windows builds are automated** via GitHub Actions - no manual building needed!
- Linux builds should be compiled on a Linux machine
- All executables bundle Python and dependencies (no separate installation required)

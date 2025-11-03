# PromptPilot Executables

This folder contains platform-specific executable builds of PromptPilot.

## Available Builds

### macOS (`macos/`)
- **PromptPilot.app** - macOS Application Bundle (recommended)
  - Double-click to run
  - Drag to Applications folder for permanent installation
  
- **PromptPilot-macOS** - Standalone executable
  - Run from Terminal: `./PromptPilot-macOS`

### Windows (Coming Soon)
Builds for Windows will be available in `windows/` when compiled.

### Linux (Coming Soon)
Builds for Linux will be available in `linux/` when compiled.

## Building Your Own

To build executables locally:

```bash
# macOS
python3 -m PyInstaller --onefile --windowed --name PromptPilot main.py

# Windows (on Windows machine)
pyinstaller --onefile --windowed --name PromptPilot main.py

# Linux
pyinstaller --onefile --windowed --name PromptPilot main.py
```

The executables will be in the `dist/` folder (which is git-ignored). Copy them to the appropriate `releases/` subfolder before committing.

## Notes

- Executables are built with PyInstaller
- macOS builds require Python 3.10+ and all dependencies from `requirements.txt`
- Windows/Linux builds should be compiled on their respective platforms

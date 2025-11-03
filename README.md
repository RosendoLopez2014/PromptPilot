# PromptPilot

A beautiful, production-ready desktop automation assistant with a floating orb UI. Control your computer with natural language prompts - type or speak commands to automate mouse, keyboard, and application interactions.

![PromptPilot](https://img.shields.io/badge/Python-3.10+-blue) ![License](https://img.shields.io/badge/license-MIT-green)

## Features

### 🎨 Beautiful UI
- **Floating circular orb** (50x50px) - draggable, always-on-top
- **Dark glassmorphism design** with cyan accents (`#00D4FF`)
- Subtle pulse animation when idle
- **Expands into Spotlight-like input panel** when clicked

### 🎤 Voice & Text Input
- Type natural language prompts
- Voice recognition (speech-to-text) via microphone
- Real-time status updates ("Opening Chrome...", "Done")

### 🤖 Automation Engine
- **Mouse & Keyboard Control** - Click, type, drag, move cursor
- **Application Launcher** - Open apps by name (VS Code, Chrome, Spotify, etc.)
- **Web Automation** - Open URLs, create Google Sheets
- **Clipboard Operations** - Copy/paste text
- **Screenshots** - Capture and save to Desktop
- **Drawing Tools** - Draw shapes in Paint

### 📝 Supported Commands

| Command | Action |
|---------|--------|
| `open chrome` | Launch Chrome browser |
| `open vs code` | Launch Visual Studio Code |
| `make google sheet budget 2025` | Create new Google Sheet named "Budget 2025" |
| `type hello in notepad` | Open Notepad and type "hello" |
| `draw circle in paint` | Open Paint and draw a red circle |
| `take screenshot` | Capture screenshot, save to Desktop |
| `open spotify play jazz` | Launch Spotify and search for "jazz" |
| `copy "text here"` | Copy text to clipboard |

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Step 1: Clone or Download

```bash
cd PromptPilot
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note for macOS/Linux users**: You may need to install `portaudio` for microphone support:

```bash
# macOS
brew install portaudio

# Ubuntu/Debian
sudo apt-get install portaudio19-dev python3-pyaudio

# Fedora
sudo dnf install portaudio-devel
```

### Step 3: Run the Application

**Quick Start (Recommended for Testing):**
```bash
# On macOS/Linux
./run.sh

# On Windows
run.bat

# Or directly with Python
python main.py
```

**Or manually:**
```bash
# Activate virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR: venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

The floating orb will appear in the bottom-right corner of your screen.

## Usage

1. **Click the orb** to open the input panel
2. **Type or speak** your command:
   - Type in the text field, or
   - Click the 🎤 button and speak
3. **Press Send** or Enter to execute
4. **Press ESC** or click outside to close the panel

### Example Prompts

```
open chrome
make google sheet called Budget 2025
type "Hello World" in notepad
draw a red circle in paint
take screenshot
open spotify play jazz
open https://github.com
```

## Building Executable

### Windows

**Option 1: Automated Build (Recommended)**
- The Windows executable is automatically built via GitHub Actions on every push to `main`
- Download the latest build from the [Actions](https://github.com/RosendoLopez2014/PromptPilot/actions) tab
- Or check the `releases/windows/` folder after the build completes

**Option 2: Manual Build on Windows**
1. Install Python 3.10+ and dependencies:
   ```cmd
   pip install -r requirements.txt
   pip install pyinstaller
   ```
2. Run the build script:
   ```cmd
   build-windows.bat
   ```
   Or with PowerShell:
   ```powershell
   .\build-windows.ps1
   ```
3. The executable will be at `releases/windows/PromptPilot-Windows.exe`

**Option 3: Manual PyInstaller Command**
```cmd
pyinstaller --onefile --windowed --name PromptPilot --hidden-import PyQt6.QtCore --hidden-import PyQt6.QtGui --hidden-import PyQt6.QtWidgets --hidden-import speech_recognition --hidden-import pyaudio --collect-all PyQt6 main.py
```

### macOS

To create a standalone executable:

```bash
python3 -m PyInstaller --onefile --windowed --name PromptPilot --hidden-import PyQt6.QtCore --hidden-import PyQt6.QtGui --hidden-import PyQt6.QtWidgets --hidden-import speech_recognition --hidden-import pyaudio --collect-all PyQt6 main.py
```

The executable will be in the `dist/` directory. Copy it to `releases/macos/` if you want to commit it.

### Cross-platform Build

The app works on:
- ✅ **Windows** (Windows 10/11)
- ✅ **macOS** (10.14+)
- ✅ **Linux** (Ubuntu, Fedora, etc.)

## Project Structure

```
PromptPilot/
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── ui/
│   ├── __init__.py
│   ├── orb.py          # Floating orb component
│   └── panel.py        # Input panel component
└── core/
    ├── __init__.py
    ├── automation.py   # Automation engine
    ├── parser.py       # Command parser
    └── voice.py        # Voice recognition
```

## Troubleshooting

### Microphone Not Working

1. Check microphone permissions in system settings
2. Verify `pyaudio` is installed: `pip install pyaudio`
3. On Linux, install system audio libraries (see Installation)

### Apps Not Launching

- **Windows**: Ensure app is in PATH or provide full path
- **macOS**: App name must match exactly (e.g., "Visual Studio Code" not "VS Code")
- **Linux**: App must be installed and accessible via command line

### Automation Not Working

- Ensure apps have necessary permissions (accessibility on macOS)
- Some apps may block automation - try different approaches
- Check that `pyautogui` can control your system

## Customization

### Changing Colors

Edit `ui/orb.py` and `ui/panel.py`:
- Background: `rgba(10, 10, 10, ...)` → `#0A0A0A`
- Accent: `rgba(0, 212, 255, ...)` → `#00D4FF`

### Adding Commands

Edit `core/parser.py` to add new command patterns:

```python
if re.search(r'your pattern', prompt_lower):
    return ("Status message...", {
        'action': your_function,
        'args': (arg1, arg2)
    })
```

## License

MIT License - feel free to use, modify, and distribute.

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- Automation powered by [pyautogui](https://github.com/asweigart/pyautogui)
- Voice recognition via [SpeechRecognition](https://github.com/Uberi/speech_recognition)

---

**Made with ❤️ for productivity enthusiasts**


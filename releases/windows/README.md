# Windows Executable

## Download

The Windows executable (`PromptPilot-Windows.exe`) is automatically built via GitHub Actions.

### Latest Build
- Check the [GitHub Actions](https://github.com/RosendoLopez2014/PromptPilot/actions) tab for the latest build
- Artifacts are available for download from completed workflow runs
- Or check this folder after the build completes (if you have push access)

## Building Locally

If you want to build the Windows executable on your Windows machine:

1. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. **Run the build script:**
   ```cmd
   build-windows.bat
   ```
   Or with PowerShell:
   ```powershell
   .\build-windows.ps1
   ```

3. **Find the executable:**
   - Location: `releases/windows/PromptPilot-Windows.exe`
   - The executable will be a single .exe file (~10-50MB)

## Usage

1. Download `PromptPilot-Windows.exe`
2. Double-click to run
3. The floating orb will appear in the bottom-right corner

## Requirements

- Windows 10/11 (64-bit)
- No Python installation required (all dependencies bundled)

## Automatic Ollama Installation

**On first run**, if Ollama is not already installed on your system:

1. The app will automatically download the Ollama installer (~50MB)
2. Run the installer silently in the background
3. You may see a Windows UAC (User Account Control) prompt - click **"Yes"** to allow installation
4. Wait 1-2 minutes for installation to complete
5. The default LLM model (`llama3.2:3b`) will be downloaded automatically (~2GB)

**Note**: 
- Installation requires internet connection
- Admin privileges may be required (UAC prompt)
- If installation fails, you can install Ollama manually from [ollama.com/download](https://ollama.com/download)
- After installation, restart the app if needed

Once installed, Ollama will be available for all users and will persist across app restarts.

## Troubleshooting

### Windows Defender / Antivirus Warning
- Some antivirus software may flag PyInstaller executables as suspicious
- This is a false positive - you can safely allow it
- Or build from source if you're concerned

### Missing DLL Errors
- If you get DLL errors, install [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- This is usually not needed for most systems

## File Size

The executable is typically 40-60MB because it bundles:
- Python runtime
- PyQt6 libraries
- All Python dependencies
- Application code

This is normal for PyInstaller one-file executables.

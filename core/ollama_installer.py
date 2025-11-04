"""
Automatic Ollama installer for Windows.
Downloads and installs Ollama if not already present.
"""
import os
import sys
import platform
import subprocess
import urllib.request
import tempfile
import time
from pathlib import Path
from typing import Optional


class OllamaInstaller:
    """Handles automatic installation of Ollama on Windows."""
    
    OLLAMA_WINDOWS_URL = "https://ollama.com/download/windows"
    OLLAMA_INSTALLER_URL = "https://github.com/ollama/ollama/releases/latest/download/OllamaSetup.exe"
    
    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.temp_dir = tempfile.gettempdir()
        self.installer_path = None
    
    def is_ollama_installed(self) -> bool:
        """Check if Ollama is already installed."""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if self.is_windows else 0
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def download_installer(self) -> Optional[str]:
        """Download Ollama installer to a location with proper permissions."""
        if not self.is_windows:
            return None
        
        try:
            print("Downloading Ollama installer...")
            
            # Use user's local AppData/Temp instead of system temp for better permissions
            localappdata = os.environ.get('LOCALAPPDATA', self.temp_dir)
            download_dir = os.path.join(localappdata, 'Temp')
            os.makedirs(download_dir, exist_ok=True)
            
            installer_path = os.path.join(download_dir, "OllamaSetup.exe")
            
            # Remove old installer if it exists
            if os.path.exists(installer_path):
                try:
                    os.remove(installer_path)
                except:
                    pass  # Ignore if can't remove
            
            # Download with progress and verification
            def report_hook(blocknum, blocksize, totalsize):
                if totalsize > 0:
                    percent = min(100, (blocknum * blocksize * 100) // totalsize)
                    if blocknum % 10 == 0:  # Print every 10 blocks
                        print(f"Downloading... {percent}%")
            
            print("Downloading from GitHub releases...")
            urllib.request.urlretrieve(
                self.OLLAMA_INSTALLER_URL, 
                installer_path,
                reporthook=report_hook
            )
            
            # Verify download completed
            if not os.path.exists(installer_path):
                print("ERROR: Installer file not found after download")
                return None
            
            # Check file size (should be at least 40MB)
            file_size = os.path.getsize(installer_path)
            if file_size < 40 * 1024 * 1024:  # Less than 40MB is suspicious
                print(f"WARNING: Downloaded file seems too small ({file_size} bytes)")
                # Continue anyway, might be a newer smaller version
            
            print(f"Download complete: {file_size / (1024*1024):.1f} MB")
            print(f"Installer saved to: {installer_path}")
            
            # Unblock the file if Windows marked it as unsafe (common for downloads)
            # Windows adds a Zone.Identifier that can prevent execution
            try:
                # Use PowerShell to unblock the file
                unblock_cmd = f'powershell -Command "Unblock-File -Path \'{installer_path}\' -ErrorAction SilentlyContinue"'
                unblock_result = subprocess.run(
                    unblock_cmd,
                    shell=True,
                    capture_output=True,
                    timeout=10,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if unblock_result.returncode == 0:
                    print("Unblocked installer file (removed Windows download security flag)")
            except Exception as e:
                # If unblocking fails, continue anyway - installer might still work
                pass
            
            self.installer_path = installer_path
            return installer_path
            
        except Exception as e:
            print(f"Error downloading Ollama installer: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def install_ollama(self, installer_path: Optional[str] = None) -> bool:
        """
        Install Ollama using the downloaded installer.
        Returns True if installation was successful.
        """
        if not self.is_windows:
            print("Ollama auto-install is only supported on Windows")
            return False
        
        if installer_path is None:
            installer_path = self.installer_path
        
        if installer_path is None or not os.path.exists(installer_path):
            print("Installer not found. Downloading...")
            installer_path = self.download_installer()
            if installer_path is None:
                return False
        
        try:
            # Verify file is accessible and not locked
            if not os.path.exists(installer_path):
                print(f"ERROR: Installer file not found: {installer_path}")
                return False
            
            # Get absolute path to avoid path issues
            installer_path = os.path.abspath(installer_path)
            
            # Verify file is readable
            try:
                with open(installer_path, 'rb') as f:
                    f.read(1)  # Read first byte to verify file is accessible
            except Exception as e:
                print(f"ERROR: Cannot read installer file: {e}")
                return False
            
            print("Installing Ollama... This may require administrator privileges.")
            print("If a UAC prompt appears, please click 'Yes' to allow installation.")
            print(f"Running installer from: {installer_path}")
            
            # Change to the directory containing the installer
            installer_dir = os.path.dirname(installer_path)
            installer_name = os.path.basename(installer_path)
            
            # Try silent install first
            # Note: Ollama installer uses /S for silent install (NSIS installer)
            print("Attempting silent installation...")
            result = subprocess.run(
                [installer_path, "/S"],
                timeout=180,  # 3 minute timeout (installer can be slow)
                cwd=installer_dir,  # Run from installer directory
                capture_output=True,  # Capture output for debugging
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # If silent install failed, provide helpful error message
            if result.returncode != 0:
                print(f"Silent installation returned code: {result.returncode}")
                if result.stdout:
                    print(f"Installer output: {result.stdout}")
                if result.stderr:
                    print(f"Installer errors: {result.stderr}")
                
                # Check for common error messages
                error_output = (result.stdout or "") + (result.stderr or "")
                if "cannot read" in error_output.lower() or "source file" in error_output.lower():
                    print("\nERROR: Installer cannot read source file.")
                    print("This might be due to:")
                    print("  1. Antivirus blocking the installer")
                    print("  2. File permissions issue")
                    print("  3. Installer file is corrupted")
                    print("\nTry:")
                    print("  1. Temporarily disable antivirus")
                    print("  2. Run the app as administrator")
                    print("  3. Download and install Ollama manually from: https://ollama.com/download")
                    return False
            
            if result.returncode == 0:
                # Wait for installation to complete and service to start
                print("Waiting for Ollama service to start...")
                time.sleep(5)
                
                # Try to refresh PATH by checking common installation locations
                # Ollama typically installs to %LOCALAPPDATA%\Programs\Ollama
                import os
                localappdata = os.environ.get('LOCALAPPDATA', '')
                ollama_path = os.path.join(localappdata, 'Programs', 'Ollama')
                if os.path.exists(ollama_path):
                    ollama_exe = os.path.join(ollama_path, 'ollama.exe')
                    if os.path.exists(ollama_exe):
                        # Try running ollama directly from install path
                        try:
                            test_result = subprocess.run(
                                [ollama_exe, "--version"],
                                capture_output=True,
                                timeout=5,
                                creationflags=subprocess.CREATE_NO_WINDOW
                            )
                            if test_result.returncode == 0:
                                print("Ollama installed successfully!")
                                return True
                        except:
                            pass
                
                # Verify installation using PATH
                if self.is_ollama_installed():
                    print("Ollama installed successfully!")
                    return True
                else:
                    print("Ollama installer completed, but verification failed.")
                    print("The Ollama service may need a moment to start.")
                    print("Please restart the application or install Ollama manually.")
                    return False
            else:
                print(f"Installer returned error code: {result.returncode}")
                print("You may need to run the installer manually as administrator.")
                return False
                
        except subprocess.TimeoutExpired:
            print("Installer timed out. Please install Ollama manually.")
            return False
        except Exception as e:
            print(f"Error installing Ollama: {e}")
            print("You can download Ollama manually from: https://ollama.com/download")
            return False
    
    def ensure_ollama_installed(self, auto_install: bool = True) -> bool:
        """
        Check if Ollama is installed, and install it if not.
        
        Args:
            auto_install: If True, automatically download and install Ollama if missing.
        
        Returns:
            True if Ollama is installed (or was successfully installed), False otherwise.
        """
        # Check if already installed
        if self.is_ollama_installed():
            print("Ollama is already installed.")
            return True
        
        if not auto_install:
            print("Ollama is not installed. Please install it manually from: https://ollama.com/download")
            return False
        
        if not self.is_windows:
            print("Automatic Ollama installation is only available on Windows.")
            print("Please install Ollama manually: https://ollama.com/download")
            return False
        
        # Try to install
        print("Ollama not found. Attempting automatic installation...")
        return self.install_ollama()
    
    def cleanup(self):
        """Clean up downloaded installer file."""
        if self.installer_path and os.path.exists(self.installer_path):
            try:
                os.remove(self.installer_path)
            except:
                pass  # Ignore cleanup errors


def install_ollama_if_needed(auto_install: bool = True) -> bool:
    """
    Convenience function to ensure Ollama is installed.
    
    Args:
        auto_install: If True, automatically install Ollama if missing.
    
    Returns:
        True if Ollama is available, False otherwise.
    """
    installer = OllamaInstaller()
    try:
        return installer.ensure_ollama_installed(auto_install=auto_install)
    finally:
        installer.cleanup()

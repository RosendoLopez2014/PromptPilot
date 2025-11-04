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
        """Download Ollama installer to temp directory."""
        if not self.is_windows:
            return None
        
        try:
            print("Downloading Ollama installer...")
            installer_path = os.path.join(self.temp_dir, "OllamaSetup.exe")
            
            # Download the installer
            urllib.request.urlretrieve(self.OLLAMA_INSTALLER_URL, installer_path)
            
            if os.path.exists(installer_path):
                self.installer_path = installer_path
                print(f"Downloaded installer to: {installer_path}")
                return installer_path
        except Exception as e:
            print(f"Error downloading Ollama installer: {e}")
            return None
        
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
            print("Installing Ollama... This may require administrator privileges.")
            print("If a UAC prompt appears, please click 'Yes' to allow installation.")
            
            # Run installer silently (/S = silent install)
            # Note: This may still trigger UAC if user doesn't have admin rights
            result = subprocess.run(
                [installer_path, "/S"],
                timeout=120,  # 2 minute timeout
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
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

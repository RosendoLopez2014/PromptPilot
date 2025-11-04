"""
Beautiful installation dialog for Ollama setup.
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QProgressBar, QFileDialog,
                             QMessageBox, QTextEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QPaintEvent, QIcon
import os
import platform


class InstallWorker(QThread):
    """Background thread for Ollama installation."""
    
    progress_updated = pyqtSignal(str, int)  # message, percentage
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, installer_path, install_location, installer_module):
        super().__init__()
        self.installer_path = installer_path
        self.install_location = install_location
        self.installer_module = installer_module
    
    def run(self):
        """Run installation in background thread."""
        import subprocess
        import time
        
        try:
            self.progress_updated.emit("Starting installation...", 10)
            
            # Check if installer exists
            if not os.path.exists(self.installer_path):
                self.finished.emit(False, "Installer file not found")
                return
            
            self.progress_updated.emit("Preparing installer...", 20)
            installer_dir = os.path.dirname(self.installer_path)
            
            # Ollama installer typically installs to Program Files, but we can try to specify location
            # Note: Ollama installer may not support custom location, but we try
            install_args = ["/S"]
            if self.install_location and self.install_location != "":
                # Some installers support /D= for directory
                install_args = ["/S", f"/D={self.install_location}"]
            
            self.progress_updated.emit("Running installer...", 30)
            
            result = subprocess.run(
                [self.installer_path] + install_args,
                cwd=installer_dir,
                timeout=180,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
            
            self.progress_updated.emit("Waiting for installation to complete...", 60)
            
            if result.returncode == 0:
                # Wait a bit for service to start
                time.sleep(3)
                
                self.progress_updated.emit("Verifying installation...", 80)
                
                # Verify Ollama is installed
                try:
                    verify_result = subprocess.run(
                        ["ollama", "--version"],
                        capture_output=True,
                        timeout=5,
                        creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
                    )
                    if verify_result.returncode == 0:
                        self.progress_updated.emit("Installation successful!", 100)
                        self.finished.emit(True, "Ollama installed successfully!")
                    else:
                        self.finished.emit(False, "Installation completed but verification failed. Please restart the app.")
                except:
                    self.progress_updated.emit("Installation may have succeeded...", 95)
                    self.finished.emit(True, "Installation completed. Please restart the app to verify.")
            else:
                error_msg = result.stderr or result.stdout or "Unknown error"
                self.finished.emit(False, f"Installation failed: {error_msg}")
                
        except subprocess.TimeoutExpired:
            self.finished.emit(False, "Installation timed out. Please try again.")
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")


class InstallDialog(QDialog):
    """Beautiful installation dialog with progress tracking."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Install Ollama")
        self.setFixedSize(550, 450)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowTitleHint
        )
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 8px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #00D4FF;
            }
            QPushButton {
                background-color: #00D4FF;
                border: none;
                border-radius: 8px;
                color: #0a0a0a;
                font-size: 14px;
                font-weight: 600;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #00B8E6;
            }
            QPushButton:pressed {
                background-color: #0099CC;
            }
            QPushButton:disabled {
                background-color: #3a3a3a;
                color: #666666;
            }
            QTextEdit {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                color: #ffffff;
                font-size: 11px;
            }
        """)
        
        self.installer_path = None
        self.install_worker = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header with logo area
        header_layout = QHBoxLayout()
        
        # Logo/Icon area (we'll add a visual logo placeholder)
        logo_label = QLabel("🚀")
        logo_label.setStyleSheet("font-size: 48px;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(logo_label)
        
        header_text_layout = QVBoxLayout()
        title = QLabel("Ollama Installation")
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #00D4FF;")
        subtitle = QLabel("Required for AI-powered automation")
        subtitle.setStyleSheet("font-size: 13px; color: #888888;")
        header_text_layout.addWidget(title)
        header_text_layout.addWidget(subtitle)
        header_layout.addLayout(header_text_layout)
        
        layout.addLayout(header_layout)
        
        # Description
        desc = QLabel(
            "Ollama enables intelligent command understanding.\n"
            "The installer will be downloaded automatically."
        )
        desc.setStyleSheet("font-size: 12px; color: #aaaaaa; padding: 10px 0;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Install location (optional)
        location_layout = QVBoxLayout()
        location_label = QLabel("Install Location (optional):")
        location_label.setStyleSheet("font-size: 13px; font-weight: 600; margin-top: 10px;")
        location_layout.addWidget(location_label)
        
        location_input_layout = QHBoxLayout()
        self.location_input = QLineEdit()
        # Default to Program Files
        default_location = os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Ollama')
        self.location_input.setText(default_location)
        self.location_input.setPlaceholderText("C:\\Program Files\\Ollama")
        
        browse_btn = QPushButton("Browse...")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self._browse_location)
        
        location_input_layout.addWidget(self.location_input)
        location_input_layout.addWidget(browse_btn)
        location_layout.addLayout(location_input_layout)
        layout.addLayout(location_layout)
        
        # Progress area
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 6px;
                background-color: #2a2a2a;
                height: 30px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00D4FF;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Status log
        status_label = QLabel("Status:")
        status_label.setStyleSheet("font-size: 13px; font-weight: 600; margin-top: 10px;")
        layout.addWidget(status_label)
        
        self.status_log = QTextEdit()
        self.status_log.setReadOnly(True)
        self.status_log.setFixedHeight(100)
        self.status_log.append("Ready to install...")
        layout.addWidget(self.status_log)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.install_btn = QPushButton("Install Ollama")
        self.install_btn.clicked.connect(self._start_installation)
        button_layout.addWidget(self.install_btn)
        
        layout.addLayout(button_layout)
    
    def _browse_location(self):
        """Browse for installation location."""
        location = QFileDialog.getExistingDirectory(
            self,
            "Select Install Location",
            self.location_input.text() or "C:\\",
            QFileDialog.Option.ShowDirsOnly
        )
        if location:
            self.location_input.setText(location)
    
    def set_installer_path(self, path):
        """Set the path to the Ollama installer."""
        self.installer_path = path
    
    def _start_installation(self):
        """Start the installation process."""
        if not self.installer_path or not os.path.exists(self.installer_path):
            QMessageBox.warning(self, "Error", "Installer file not found. Please download it first.")
            return
        
        # Disable controls
        self.install_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.location_input.setEnabled(False)
        
        # Start installation worker
        install_location = self.location_input.text().strip()
        if not install_location:
            install_location = None
        
        # Import installer module
        from core.ollama_installer import OllamaInstaller
        
        self.install_worker = InstallWorker(
            self.installer_path,
            install_location,
            OllamaInstaller
        )
        self.install_worker.progress_updated.connect(self._on_progress)
        self.install_worker.finished.connect(self._on_installation_finished)
        self.install_worker.start()
    
    def _on_progress(self, message, percentage):
        """Update progress bar and status."""
        self.progress_bar.setValue(percentage)
        self.status_log.append(f"• {message}")
        # Auto-scroll to bottom
        self.status_log.verticalScrollBar().setValue(
            self.status_log.verticalScrollBar().maximum()
        )
    
    def _on_installation_finished(self, success, message):
        """Handle installation completion."""
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setValue(100 if success else 0)
        self.status_log.append(f"\n{'✓' if success else '✗'} {message}")
        
        if success:
            self.cancel_btn.setText("Close")
            self.cancel_btn.clicked.disconnect()
            self.cancel_btn.clicked.connect(self.accept)
            QMessageBox.information(self, "Success", "Ollama installed successfully!\n\nPlease restart the application.")
        else:
            self.install_btn.setEnabled(True)
            self.install_btn.setText("Retry")
            QMessageBox.warning(self, "Installation Failed", message)

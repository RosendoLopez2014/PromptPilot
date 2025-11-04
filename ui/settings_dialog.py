"""
Settings dialog for PromptPilot configuration.
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QComboBox, QCheckBox, QTabWidget,
                             QWidget, QGroupBox, QSpinBox, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QPaintEvent, QIcon
import os
import json
from pathlib import Path


class SettingsDialog(QDialog):
    """Beautiful settings dialog with tabs."""
    
    settings_changed = pyqtSignal()  # Emitted when settings are saved
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings - PromptPilot")
        self.setFixedSize(650, 550)
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
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                background-color: #2a2a2a;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                color: #aaaaaa;
                padding: 10px 20px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: #1a1a1a;
                color: #00D4FF;
                border-bottom: 2px solid #00D4FF;
            }
            QLineEdit, QComboBox, QSpinBox {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 8px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 2px solid #00D4FF;
            }
            QCheckBox {
                color: #ffffff;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #3a3a3a;
                border-radius: 4px;
                background-color: #2a2a2a;
            }
            QCheckBox::indicator:checked {
                background-color: #00D4FF;
                border-color: #00D4FF;
            }
            QGroupBox {
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
                font-size: 14px;
                font-weight: 600;
                color: #00D4FF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
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
            QPushButton#secondary {
                background-color: #3a3a3a;
                color: #ffffff;
            }
            QPushButton#secondary:hover {
                background-color: #4a4a4a;
            }
        """)
        
        self.settings_file = self._get_settings_path()
        self.settings = self._load_settings()
        self._setup_ui()
        self._load_settings_to_ui()
    
    def _get_settings_path(self):
        """Get path to settings file."""
        app_data = Path.home() / ".promptpilot"
        app_data.mkdir(exist_ok=True)
        return app_data / "settings.json"
    
    def _load_settings(self):
        """Load settings from file."""
        default = {
            "ollama_model": "llama3.2:3b",
            "ollama_auto_install": True,
            "ollama_location": "",
            "orb_opacity": 100,
            "orb_size": 50,
            "panel_opacity": 98,
            "theme": "dark",
            "auto_start": False,
            "enable_sounds": False,
            "click_highlight_duration": 600,
            "save_history": True,
            "history_size": 100
        }
        
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    default.update(loaded)
            except:
                pass
        
        return default
    
    def _save_settings(self):
        """Save settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save settings: {str(e)}")
            return False
    
    def _setup_ui(self):
        """Setup UI with tabs."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with logo
        header = self._create_header()
        layout.addWidget(header)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("margin: 15px;")
        
        # General tab
        self.general_tab = self._create_general_tab()
        self.tabs.addTab(self.general_tab, "General")
        
        # Ollama/AI tab
        self.ai_tab = self._create_ai_tab()
        self.tabs.addTab(self.ai_tab, "AI & Ollama")
        
        # Appearance tab
        self.appearance_tab = self._create_appearance_tab()
        self.tabs.addTab(self.appearance_tab, "Appearance")
        
        # Advanced tab
        self.advanced_tab = self._create_advanced_tab()
        self.tabs.addTab(self.advanced_tab, "Advanced")
        
        layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.setObjectName("secondary")
        self.reset_btn.clicked.connect(self._reset_settings)
        button_layout.addWidget(self.reset_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("secondary")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_and_close)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
    def _create_header(self):
        """Create header with logo."""
        header_widget = QWidget()
        header_widget.setFixedHeight(80)
        header_widget.setStyleSheet("background-color: #0a0a0a; border-bottom: 1px solid #3a3a3a;")
        
        layout = QHBoxLayout(header_widget)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Logo (using emoji/icon)
        logo_label = QLabel("🚀 PromptPilot")
        logo_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #00D4FF;")
        layout.addWidget(logo_label)
        
        layout.addStretch()
        
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("font-size: 12px; color: #666666;")
        layout.addWidget(version_label)
        
        return header_widget
    
    def _create_general_tab(self):
        """Create General settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Auto-start
        self.auto_start_cb = QCheckBox("Start PromptPilot automatically on system startup")
        layout.addWidget(self.auto_start_cb)
        
        # Sounds
        self.enable_sounds_cb = QCheckBox("Enable sound effects")
        layout.addWidget(self.enable_sounds_cb)
        
        # History
        history_group = QGroupBox("Command History")
        history_layout = QVBoxLayout()
        
        self.save_history_cb = QCheckBox("Save command history")
        history_layout.addWidget(self.save_history_cb)
        
        history_size_layout = QHBoxLayout()
        history_size_layout.addWidget(QLabel("History size:"))
        self.history_size_spin = QSpinBox()
        self.history_size_spin.setRange(10, 1000)
        self.history_size_spin.setSuffix(" commands")
        history_size_layout.addWidget(self.history_size_spin)
        history_size_layout.addStretch()
        history_layout.addLayout(history_size_layout)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        layout.addStretch()
        return widget
    
    def _create_ai_tab(self):
        """Create AI & Ollama settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Model selection
        model_group = QGroupBox("LLM Model")
        model_layout = QVBoxLayout()
        
        model_layout.addWidget(QLabel("Ollama Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "llama3.2:3b",
            "llama3.2:1b",
            "phi3:mini",
            "mistral:7b",
            "llama3:8b"
        ])
        model_layout.addWidget(self.model_combo)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Installation
        install_group = QGroupBox("Installation")
        install_layout = QVBoxLayout()
        
        self.auto_install_cb = QCheckBox("Automatically install Ollama if not found")
        install_layout.addWidget(self.auto_install_cb)
        
        install_location_layout = QHBoxLayout()
        install_location_layout.addWidget(QLabel("Install Location:"))
        self.install_location_input = QLineEdit()
        self.install_location_input.setPlaceholderText("Default: Program Files\\Ollama")
        install_location_layout.addWidget(self.install_location_input)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.setFixedWidth(80)
        browse_btn.setObjectName("secondary")
        browse_btn.clicked.connect(self._browse_ollama_location)
        install_location_layout.addWidget(browse_btn)
        
        install_layout.addLayout(install_location_layout)
        install_group.setLayout(install_layout)
        layout.addWidget(install_group)
        
        layout.addStretch()
        return widget
    
    def _create_appearance_tab(self):
        """Create Appearance settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Orb settings
        orb_group = QGroupBox("Floating Orb")
        orb_layout = QVBoxLayout()
        
        orb_opacity_layout = QHBoxLayout()
        orb_opacity_layout.addWidget(QLabel("Opacity:"))
        self.orb_opacity_spin = QSpinBox()
        self.orb_opacity_spin.setRange(20, 100)
        self.orb_opacity_spin.setSuffix("%")
        orb_opacity_layout.addWidget(self.orb_opacity_spin)
        orb_opacity_layout.addStretch()
        orb_layout.addLayout(orb_opacity_layout)
        
        orb_size_layout = QHBoxLayout()
        orb_size_layout.addWidget(QLabel("Size:"))
        self.orb_size_spin = QSpinBox()
        self.orb_size_spin.setRange(30, 100)
        self.orb_size_spin.setSuffix(" px")
        orb_size_layout.addWidget(self.orb_size_spin)
        orb_size_layout.addStretch()
        orb_layout.addLayout(orb_size_layout)
        
        orb_group.setLayout(orb_layout)
        layout.addWidget(orb_group)
        
        # Panel settings
        panel_group = QGroupBox("Input Panel")
        panel_layout = QVBoxLayout()
        
        panel_opacity_layout = QHBoxLayout()
        panel_opacity_layout.addWidget(QLabel("Opacity:"))
        self.panel_opacity_spin = QSpinBox()
        self.panel_opacity_spin.setRange(50, 100)
        self.panel_opacity_spin.setSuffix("%")
        panel_opacity_layout.addWidget(self.panel_opacity_spin)
        panel_opacity_layout.addStretch()
        panel_layout.addLayout(panel_opacity_layout)
        
        panel_group.setLayout(panel_layout)
        layout.addWidget(panel_group)
        
        # Click highlight
        highlight_group = QGroupBox("Click Highlight")
        highlight_layout = QVBoxLayout()
        
        highlight_duration_layout = QHBoxLayout()
        highlight_duration_layout.addWidget(QLabel("Animation Duration:"))
        self.highlight_duration_spin = QSpinBox()
        self.highlight_duration_spin.setRange(200, 2000)
        self.highlight_duration_spin.setSuffix(" ms")
        highlight_duration_layout.addWidget(self.highlight_duration_spin)
        highlight_duration_layout.addStretch()
        highlight_layout.addLayout(highlight_duration_layout)
        
        highlight_group.setLayout(highlight_layout)
        layout.addWidget(highlight_group)
        
        layout.addStretch()
        return widget
    
    def _create_advanced_tab(self):
        """Create Advanced settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        info_label = QLabel(
            "Advanced settings are coming soon.\n\n"
            "This will include:\n"
            "• Custom prompt templates\n"
            "• API key management\n"
            "• Debug logging\n"
            "• Performance tuning"
        )
        info_label.setStyleSheet("color: #888888; padding: 20px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addStretch()
        return widget
    
    def _browse_ollama_location(self):
        """Browse for Ollama installation location."""
        location = QFileDialog.getExistingDirectory(
            self,
            "Select Ollama Installation Location",
            self.install_location_input.text() or "C:\\",
            QFileDialog.Option.ShowDirsOnly
        )
        if location:
            self.install_location_input.setText(location)
    
    def _load_settings_to_ui(self):
        """Load current settings into UI."""
        self.model_combo.setCurrentText(self.settings.get("ollama_model", "llama3.2:3b"))
        self.auto_install_cb.setChecked(self.settings.get("ollama_auto_install", True))
        self.install_location_input.setText(self.settings.get("ollama_location", ""))
        self.orb_opacity_spin.setValue(self.settings.get("orb_opacity", 100))
        self.orb_size_spin.setValue(self.settings.get("orb_size", 50))
        self.panel_opacity_spin.setValue(self.settings.get("panel_opacity", 98))
        self.auto_start_cb.setChecked(self.settings.get("auto_start", False))
        self.enable_sounds_cb.setChecked(self.settings.get("enable_sounds", False))
        self.highlight_duration_spin.setValue(self.settings.get("click_highlight_duration", 600))
        self.save_history_cb.setChecked(self.settings.get("save_history", True))
        self.history_size_spin.setValue(self.settings.get("history_size", 100))
    
    def _collect_settings_from_ui(self):
        """Collect settings from UI."""
        self.settings["ollama_model"] = self.model_combo.currentText()
        self.settings["ollama_auto_install"] = self.auto_install_cb.isChecked()
        self.settings["ollama_location"] = self.install_location_input.text()
        self.settings["orb_opacity"] = self.orb_opacity_spin.value()
        self.settings["orb_size"] = self.orb_size_spin.value()
        self.settings["panel_opacity"] = self.panel_opacity_spin.value()
        self.settings["auto_start"] = self.auto_start_cb.isChecked()
        self.settings["enable_sounds"] = self.enable_sounds_cb.isChecked()
        self.settings["click_highlight_duration"] = self.highlight_duration_spin.value()
        self.settings["save_history"] = self.save_history_cb.isChecked()
        self.settings["history_size"] = self.history_size_spin.value()
    
    def _reset_settings(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Delete settings file and reload
            if self.settings_file.exists():
                self.settings_file.unlink()
            self.settings = self._load_settings()
            self._load_settings_to_ui()
    
    def _save_and_close(self):
        """Save settings and close dialog."""
        self._collect_settings_from_ui()
        if self._save_settings():
            self.settings_changed.emit()
            self.accept()
    
    def get_settings(self):
        """Get current settings."""
        return self.settings.copy()

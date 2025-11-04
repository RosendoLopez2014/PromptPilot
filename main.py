"""
PromptPilot - Desktop automation assistant with floating orb UI.
"""
import sys
import threading
from PyQt6.QtWidgets import QApplication, QWidget, QMenu
from PyQt6.QtCore import Qt, QTimer, QPoint, QMetaObject, Q_ARG, QObject
from PyQt6.QtGui import QScreen, QKeyEvent, QMouseEvent
from ui.orb import FloatingOrb
from ui.panel import InputPanel
from ui.click_highlight import ClickHighlight
from ui.install_dialog import InstallDialog
from ui.settings_dialog import SettingsDialog
from core.automation import AutomationEngine
from core.parser import CommandParser
from core.voice import VoiceRecognizer
from core.vision import VisionEngine
from core.llm_agent import LLMAgent
from core.ollama_installer import OllamaInstaller
import platform
import json
from pathlib import Path


class OverlayWidget(QWidget):
    """Transparent overlay to detect clicks outside panel."""
    
    def __init__(self, app_instance, parent=None):
        super().__init__(parent)
        self.app_instance = app_instance
        self.panel_widget = None  # Will be set after panel is created
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
    
    def mousePressEvent(self, event: QMouseEvent):
        """Close panel when clicking outside."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if click is actually on the panel
            if self.panel_widget:
                panel_rect = self.panel_widget.geometry()
                click_pos = event.globalPosition().toPoint()
                if panel_rect.contains(click_pos):
                    # Click is on panel, don't close
                    return
            
            # Click is outside panel, close it
            if self.app_instance and hasattr(self.app_instance, '_hide_panel'):
                self.app_instance._hide_panel()
        super().mousePressEvent(event)


class PromptPilotApp(QObject):
    """Main application class."""
    
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Core components
        self.vision = VisionEngine()
        
        # Click highlight overlay
        self.click_highlight = ClickHighlight()
        self.click_highlight.hide()
        
        # Automation with click callback
        self.automation = AutomationEngine(click_callback=self._on_automation_click)
        
        # Load settings before creating parser (to get Ollama model preference)
        temp_settings = self._load_settings()
        auto_install = temp_settings.get("ollama_auto_install", False)  # Disable auto-install, use UI instead
        
        # Parser with LLM agent (will check Ollama availability but not auto-install)
        self.parser = CommandParser(self.automation, self.vision)
        if self.parser.llm_agent:
            self.parser.llm_agent.auto_install = False  # Disable auto-install, use UI dialog instead
        
        self.voice = VoiceRecognizer()
        
        # UI components
        self.orb = FloatingOrb()
        self.panel = InputPanel()
        
        # Overlay for click-outside detection
        self.overlay = OverlayWidget(self)
        self.overlay.panel_widget = self.panel  # Link panel for click detection
        
        # Panel visibility
        self.panel_is_open = False
        
        # Settings
        self.settings = self._load_settings()
        self.ollama_installer = OllamaInstaller() if platform.system() == "Windows" else None
        
        # Store original orb mousePressEvent
        self.orb_original_press = self.orb.mousePressEvent
        
        # Setup UI
        self._setup_ui()
        self._setup_connections()
        self._apply_settings()
        
        # Position orb at bottom-right
        self._position_orb()
        
        # Position panel at center
        self._position_panel()
        
        # Check for Ollama and show install dialog if needed
        QTimer.singleShot(1000, self._check_ollama_on_startup)
    
    def _setup_ui(self):
        """Setup UI components."""
        # Orb visibility
        self.orb.show()
        
        # Panel initially hidden
        self.panel.hide()
        self.overlay.hide()
        
        # Click highlight initially hidden
        screen = self.app.primaryScreen()
        geometry = screen.geometry()
        self.click_highlight.setGeometry(geometry)
        self.click_highlight.hide()
        
        # Install event filter on panel for ESC key
        self.panel.installEventFilter(self)
    
    def _on_automation_click(self, x: int, y: int, bbox: tuple = None):
        """Callback when automation engine performs a click."""
        # Show click highlight
        self.click_highlight.show_click(x, y, bbox)
    
    def _setup_connections(self):
        """Setup signal/slot connections."""
        # Orb click -> show panel (override mousePressEvent)
        self.orb.mousePressEvent = self._on_orb_clicked
        
        # Track orb drag state to detect clicks vs drags
        original_release = self.orb.mouseReleaseEvent
        def orb_release_with_click_detection(event):
            original_release(event)
            # If it was a click (not a drag), toggle panel
            if event.button() == Qt.MouseButton.LeftButton and not self.orb.is_dragging:
                if self.panel_is_open:
                    self._hide_panel()
                else:
                    self._show_panel()
        self.orb.mouseReleaseEvent = orb_release_with_click_detection
        
        # Panel buttons
        self.panel.send_button.clicked.connect(self._on_send_clicked)
        self.panel.mic_button.clicked.connect(self._on_mic_clicked)
        self.panel.send_requested.connect(self._on_send_clicked)  # Enter key
        
        # Voice recognition callback
        self.voice.callback = self._on_voice_result
    
    def _load_settings(self):
        """Load settings from file."""
        settings_file = Path.home() / ".promptpilot" / "settings.json"
        default = {
            "ollama_model": "llama3.2:3b",
            "ollama_auto_install": True,
            "ollama_location": "",
            "orb_opacity": 100,
            "orb_size": 50,
            "panel_opacity": 98,
            "click_highlight_duration": 600,
        }
        
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    loaded = json.load(f)
                    default.update(loaded)
            except:
                pass
        
        return default
    
    def _apply_settings(self):
        """Apply loaded settings to UI."""
        # Orb size
        orb_size = self.settings.get("orb_size", 50)
        self.orb.setFixedSize(orb_size, orb_size)
        
        # Orb opacity
        orb_opacity = self.settings.get("orb_opacity", 100) / 100.0
        self.orb.setWindowOpacity(orb_opacity)
        
        # Panel opacity
        panel_opacity = self.settings.get("panel_opacity", 98) / 100.0
        self.panel.setWindowOpacity(panel_opacity)
        
        # Click highlight duration
        duration = self.settings.get("click_highlight_duration", 600)
        self.click_highlight.fade_anim.setDuration(duration)
        self.click_highlight.scale_anim.setDuration(duration)
        
        # Update LLM agent model if parser has one
        if hasattr(self.parser, 'llm_agent') and self.parser.llm_agent:
            self.parser.llm_agent.model = self.settings.get("ollama_model", "llama3.2:3b")
    
    def _check_ollama_on_startup(self):
        """Check if Ollama is installed on startup and show install dialog if needed."""
        if not platform.system() == "Windows":
            return
        
        # Check if Ollama is installed
        if self.ollama_installer and not self.ollama_installer.is_ollama_installed():
            # Check if auto-install is enabled
            if self.settings.get("ollama_auto_install", True):
                self._show_install_dialog()
    
    def _show_install_dialog(self):
        """Show Ollama installation dialog."""
        dialog = InstallDialog(self.orb)
        
        # Download installer first
        if self.ollama_installer:
            dialog.status_log.append("Downloading Ollama installer...")
            installer_path = self.ollama_installer.download_installer()
            if installer_path:
                dialog.set_installer_path(installer_path)
                dialog.status_log.append("Installer downloaded successfully!")
            else:
                dialog.status_log.append("Failed to download installer. Please install manually.")
                QTimer.singleShot(2000, dialog.close)
                return
        
        # Show dialog
        if dialog.exec() == dialog.DialogCode.Accepted:
            # Installation successful, refresh LLM agent
            if hasattr(self.parser, 'llm_agent'):
                self.parser.llm_agent.ollama_available = self.ollama_installer.is_ollama_installed()
                if self.parser.llm_agent.ollama_available:
                    self.parser.llm_agent.ensure_model_available()
    
    def _show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self.orb)
        dialog.settings_changed.connect(self._on_settings_changed)
        
        if dialog.exec() == dialog.DialogCode.Accepted:
            # Settings saved, reload and apply
            self.settings = dialog.get_settings()
            self._apply_settings()
    
    def _on_settings_changed(self):
        """Handle settings changed signal."""
        # Reload settings
        self.settings = self._load_settings()
        self._apply_settings()
    
    def _show_orb_context_menu(self, position):
        """Show context menu when right-clicking orb."""
        menu = QMenu(self.orb)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #00D4FF;
                color: #0a0a0a;
            }
        """)
        
        settings_action = menu.addAction("⚙️ Settings")
        menu.addSeparator()
        install_action = menu.addAction("📥 Install Ollama") if platform.system() == "Windows" else None
        menu.addSeparator()
        quit_action = menu.addAction("❌ Quit")
        
        action = menu.exec(self.orb.mapToGlobal(position))
        
        if action == settings_action:
            self._show_settings()
        elif action == install_action and install_action:
            self._show_install_dialog()
        elif action == quit_action:
            self.app.quit()
    
    def eventFilter(self, obj, event):
        """Filter events for ESC key."""
        if obj == self.panel:
            # ESC key to close
            if event.type() == event.Type.KeyPress:
                if event.key() == Qt.Key.Key_Escape:
                    self._hide_panel()
                    return True
        
        return False
    
    def _position_orb(self):
        """Position orb at bottom-right of screen."""
        screen = self.app.primaryScreen()
        geometry = screen.geometry()
        orb_x = geometry.width() - self.orb.width() - 20
        orb_y = geometry.height() - self.orb.height() - 20
        self.orb.move(orb_x, orb_y)
    
    def _position_panel(self):
        """Position panel on the right side of screen."""
        screen = self.app.primaryScreen()
        geometry = screen.geometry()
        panel_x = geometry.width() - self.panel.width() - 30  # Right side with margin
        panel_y = 50  # Top with margin
        self.panel.move(panel_x, panel_y)
        
        # Position overlay to cover entire screen
        self.overlay.setGeometry(geometry)
        self.overlay.lower()  # Put behind panel
    
    def _on_orb_clicked(self, event):
        """Handle orb click - left click opens panel, right click shows menu."""
        if event.button() == Qt.MouseButton.RightButton:
            # Right-click: show context menu
            self._show_orb_context_menu(event.position().toPoint())
            event.accept()
            return
        elif event.button() == Qt.MouseButton.LeftButton:
            # Left-click: start dragging (panel toggle handled separately on release if not dragged)
            self.orb_original_press(event)
    
    def _show_panel(self):
        """Show input panel."""
        self.panel_is_open = True
        self.panel.showPanel()
        self.panel.raise_()  # Bring panel to front
        self.overlay.show()
        self.overlay.lower()  # Behind panel
        # Ensure panel stays on top
        QTimer.singleShot(50, lambda: self.panel.raise_())
        QTimer.singleShot(150, lambda: self.panel.text_input.setFocus())
    
    def _hide_panel(self):
        """Hide input panel."""
        self.panel_is_open = False
        self.overlay.hide()
        self.panel.hidePanel()
        self.panel.text_input.clear()
        self.panel.setStatus("Ready")
    
    def _on_send_clicked(self):
        """Handle send button click."""
        prompt = self.panel.text_input.toPlainText().strip()
        if prompt:
            self._execute_prompt(prompt)
            # Don't clear text - keep it visible
            # self.panel.text_input.clear()
    
    def _on_mic_clicked(self):
        """Handle mic button click for voice input."""
        if self.voice.is_listening:
            self.voice.stop_listening()
            self.panel.mic_button.setText("🎤")
            self.panel.setStatus("Ready")
        else:
            self.panel.mic_button.setText("⏸")
            self.voice.start_listening(self._on_voice_result)
    
    def _on_voice_result(self, text: str):
        """Handle voice recognition result - called from background thread."""
        # Use QMetaObject.invokeMethod for thread-safe UI updates
        if text.startswith(("Listening", "Error", "Could not", "Recognition", "Microphone")):
            QMetaObject.invokeMethod(
                self.panel,
                "setStatus",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, text)
            )
        else:
            # Valid transcription
            QMetaObject.invokeMethod(
                self.panel.text_input,
                "setPlainText",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, text)
            )
            QTimer.singleShot(100, lambda: self._execute_prompt(text))
        
        QMetaObject.invokeMethod(
            self.panel.mic_button,
            "setText",
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(str, "🎤")
        )
    
    def _execute_prompt(self, prompt: str):
        """Execute parsed prompt."""
        if not prompt.strip():
            return
        
        # Parse prompt
        status_msg, params = self.parser.parse(prompt)
        self.panel.setStatus(status_msg, show_progress=True)
        
        # Execute action in background thread
        action = params.get('action')
        args = params.get('args', ())
        
        if action:
            thread = threading.Thread(
                target=self._run_action,
                args=(action, args),
                daemon=True
            )
            thread.start()
        else:
            # No action, just show status (keep panel open)
            self.panel.setStatus(status_msg, show_progress=False)
    
    def _run_action(self, action, args):
        """Run action in background thread."""
        try:
            if callable(action):
                result = action(*args)
                # If action returns a string, use it as status message
                if isinstance(result, str):
                    status_msg = result
                else:
                    status_msg = "✓ Done"
            else:
                status_msg = "✓ Done"
            
            # Update status after completion (keep panel open)
            QMetaObject.invokeMethod(
                self.panel,
                "setStatusWithProgress",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, status_msg),
                Q_ARG(bool, False)
            )
            # Panel stays open - no auto-close
        except Exception as e:
            error_msg = f"✗ Error: {str(e)[:40]}"
            QMetaObject.invokeMethod(
                self.panel,
                "setStatusWithProgress",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, error_msg),
                Q_ARG(bool, False)
            )
    
    def run(self):
        """Run the application."""
        sys.exit(self.app.exec())


def main():
    """Entry point."""
    app = PromptPilotApp()
    app.run()


if __name__ == "__main__":
    main()


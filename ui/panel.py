"""
Expanded input panel UI component.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QLabel, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtProperty, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPaintEvent, QFont, QKeyEvent


class CommandTextEdit(QTextEdit):
    """Custom QTextEdit that emits signal on Enter key."""
    
    enter_pressed = pyqtSignal()
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle Enter key to send command."""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                self.enter_pressed.emit()
                event.accept()
                return
        super().keyPressEvent(event)


class InputPanel(QWidget):
    """Minimal centered input panel with glassmorphism design."""
    
    send_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(500, 300)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        
        self._opacity = 0.0
        self.is_visible = False
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #00D4FF;
            font-size: 12px;
            font-weight: 500;
            background: transparent;
            padding: 5px;
        """)
        layout.addWidget(self.status_label)
        
        # Text input
        self.text_input = CommandTextEdit()
        self.text_input.setPlaceholderText("Type your prompt...")
        # Note: setMaximumBlockCount() is only available for QPlainTextEdit, not QTextEdit
        # Text length limitation removed - QTextEdit handles large text well
        self.text_input.setStyleSheet("""
            QTextEdit {
                background-color: rgba(10, 10, 10, 0.9);
                border: 2px solid rgba(0, 212, 255, 0.3);
                border-radius: 10px;
                padding: 12px;
                color: #FFFFFF;
                font-size: 14px;
                font-family: 'Inter', system-ui, -apple-system, sans-serif;
            }
            QTextEdit:focus {
                border-color: rgba(0, 212, 255, 0.6);
            }
        """)
        self.text_input.enter_pressed.connect(self.send_requested)
        layout.addWidget(self.text_input)
        
        # Button row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Mic button
        self.mic_button = QPushButton("🎤")
        self.mic_button.setFixedSize(50, 50)
        self.mic_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(10, 10, 10, 0.9);
                border: 2px solid rgba(0, 212, 255, 0.3);
                border-radius: 25px;
                color: #00D4FF;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: rgba(0, 212, 255, 0.2);
                border-color: rgba(0, 212, 255, 0.6);
            }
            QPushButton:pressed {
                background-color: rgba(0, 212, 255, 0.3);
            }
        """)
        button_layout.addWidget(self.mic_button)
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #00D4FF;
                border: none;
                border-radius: 10px;
                color: #0A0A0A;
                font-size: 14px;
                font-weight: 600;
                padding: 12px 30px;
                font-family: 'Inter', system-ui, -apple-system, sans-serif;
            }
            QPushButton:hover {
                background-color: #00B8E6;
            }
            QPushButton:pressed {
                background-color: #0099CC;
            }
        """)
        button_layout.addWidget(self.send_button, stretch=1)
        
        layout.addLayout(button_layout)
        
        # Fade animation
        self.fade_anim = QPropertyAnimation(self, b"opacity")
        self.fade_anim.setDuration(200)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    def opacity(self):
        return self._opacity
    
    def setOpacity(self, value):
        self._opacity = value
        self.setWindowOpacity(value)
    
    opacity = pyqtProperty(float, opacity, setOpacity)
    
    def showPanel(self):
        """Show panel with fade-in animation."""
        self.is_visible = True
        self.show()
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(0.98)
        self.fade_anim.start()
        self.text_input.setFocus()
    
    def hidePanel(self):
        """Hide panel with fade-out animation."""
        self.is_visible = False
        try:
            self.fade_anim.finished.disconnect()
        except TypeError:
            pass  # Nothing connected
        self.fade_anim.setStartValue(self._opacity)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.finished.connect(self.hide)
        self.fade_anim.start()
    
    def setStatus(self, text: str):
        """Update status label."""
        self.status_label.setText(text)
    
    def paintEvent(self, event: QPaintEvent):
        """Draw glassmorphism background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Blurred background
        bg_color = QColor(10, 10, 10, int(230 * self._opacity))
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor(0, 212, 255, int(100 * self._opacity)), 2))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 15, 15)
        
        # Inner glow
        inner_glow = QColor(0, 212, 255, int(30 * self._opacity))
        painter.setBrush(QBrush(inner_glow))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect().adjusted(3, 3, -3, -3), 13, 13)


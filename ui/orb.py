"""
Floating orb UI component with glassmorphism design.
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, QRect, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPaintEvent, QMouseEvent


class FloatingOrb(QWidget):
    """Draggable floating orb with pulse animation."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 50)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        
        self._opacity = 1.0
        self._scale = 1.0
        self.drag_position = QPoint()
        self.is_dragging = False
        
        # Pulse animation
        self.pulse_anim = QPropertyAnimation(self, b"scale")
        self.pulse_anim.setDuration(2000)
        self.pulse_anim.setStartValue(0.95)
        self.pulse_anim.setEndValue(1.0)
        self.pulse_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.pulse_anim.setLoopCount(-1)
        self.pulse_anim.start()
    
    def scale(self):
        return self._scale
    
    def setScale(self, value):
        self._scale = value
        self.update()
    
    scale = pyqtProperty(float, scale, setScale)
    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            event.accept()
    
    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Outer glow (cyan)
        glow_radius = 25 * self._scale
        glow_color = QColor(0, 212, 255, 60)
        painter.setBrush(QBrush(glow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(self.rect().center(), int(glow_radius), int(glow_radius))
        
        # Main orb (dark with blur effect)
        orb_radius = 20 * self._scale
        center_point = self.rect().center()
        orb_rect = QRect(
            int(center_point.x() - orb_radius),
            int(center_point.y() - orb_radius),
            int(orb_radius * 2),
            int(orb_radius * 2)
        )
        
        # Dark background with transparency
        gradient = QColor(10, 10, 10, 220)
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(0, 212, 255, 150), 2))
        painter.drawEllipse(orb_rect)
        
        # Inner highlight
        highlight_radius = 8 * self._scale
        highlight_center = self.rect().center()
        highlight_color = QColor(0, 212, 255, 80)
        painter.setBrush(QBrush(highlight_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(highlight_center, int(highlight_radius), int(highlight_radius))


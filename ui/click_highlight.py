"""
Glassmorphism click highlight overlay with ripple effect.
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QPoint, pyqtProperty, QTimer
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPaintEvent, QPainterPath


class ClickHighlight(QWidget):
    """Animated click highlight with glassmorphism ripple effect."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        
        # Highlight properties
        self._opacity = 0.0
        self._scale = 0.3
        self.bbox = None  # (x, y, width, height)
        self.center_point = None  # (x, y)
        
        # Animation
        self.fade_anim = QPropertyAnimation(self, b"opacity")
        self.fade_anim.setDuration(600)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.scale_anim = QPropertyAnimation(self, b"scale")
        self.scale_anim.setDuration(600)
        self.scale_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.hide()
    
    def opacity(self):
        return self._opacity
    
    def setOpacity(self, value):
        self._opacity = value
        self.update()
    
    opacity = pyqtProperty(float, opacity, setOpacity)
    
    def scale(self):
        return self._scale
    
    def setScale(self, value):
        self._scale = value
        self.update()
    
    scale = pyqtProperty(float, scale, setScale)
    
    def show_click(self, x: int, y: int, bbox: tuple = None, duration: int = 600):
        """
        Show click highlight at position.
        
        Args:
            x, y: Click coordinates
            bbox: Optional bounding box (x, y, width, height) of clicked element
            duration: Animation duration in ms
        """
        self.center_point = (x, y)
        self.bbox = bbox
        
        # Size highlight based on bbox or default
        if bbox:
            bx, by, bw, bh = bbox
            # Add padding
            padding = 10
            self.setGeometry(bx - padding, by - padding, bw + padding * 2, bh + padding * 2)
        else:
            # Default size for point click
            size = 60
            self.setGeometry(x - size // 2, y - size // 2, size, size)
        
        # Show and animate
        self.show()
        self.raise_()
        
        # Reset animations
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEndValue(0.0)  # Fade out
        
        self.scale_anim.setStartValue(0.3)
        self.scale_anim.setEndValue(1.2)
        
        # Start animations
        self.fade_anim.start()
        self.scale_anim.start()
        
        # Auto-hide after animation
        QTimer.singleShot(duration + 50, self.hide)
    
    def paintEvent(self, event: QPaintEvent):
        """Draw glassmorphism ripple effect."""
        if self._opacity <= 0 or not self.center_point:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate center relative to widget
        if self.bbox:
            # Highlight the bounding box
            bx, by, bw, bh = self.bbox
            rect = QRect(bx, by, bw, bh)
        else:
            # Circular highlight at point
            size = int(30 * self._scale)
            center = self.rect().center()
            rect = QRect(center.x() - size // 2, center.y() - size // 2, size, size)
        
        # Cyan glow (outer)
        glow_color = QColor(0, 212, 255, int(150 * self._opacity))
        painter.setPen(QPen(glow_color, 3))
        painter.setBrush(QBrush(QColor(0, 212, 255, int(30 * self._opacity))))
        painter.drawRoundedRect(rect, 8, 8)
        
        # Inner highlight
        inner_color = QColor(0, 212, 255, int(200 * self._opacity))
        painter.setPen(QPen(inner_color, 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Ripple effect (multiple rings)
        for i in range(3):
            ring_opacity = self._opacity * (1.0 - i * 0.3)
            if ring_opacity > 0:
                ring_color = QColor(0, 212, 255, int(100 * ring_opacity))
                painter.setPen(QPen(ring_color, 2))
                ring_size = int((30 + i * 10) * self._scale)
                ring_rect = QRect(
                    rect.center().x() - ring_size // 2,
                    rect.center().y() - ring_size // 2,
                    ring_size, ring_size
                )
                painter.drawEllipse(ring_rect)
        
        # Center dot
        dot_color = QColor(0, 212, 255, int(255 * self._opacity))
        painter.setBrush(QBrush(dot_color))
        painter.setPen(Qt.PenStyle.NoPen)
        dot_size = 6
        dot_rect = QRect(
            rect.center().x() - dot_size // 2,
            rect.center().y() - dot_size // 2,
            dot_size, dot_size
        )
        painter.drawEllipse(dot_rect)


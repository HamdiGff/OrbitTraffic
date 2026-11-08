"""
OrbitTraffic — Modern Toggle Switch & Feature Card Components
Replaces dated native checkboxes with iOS/Linear-style interactive toggle switches
and elevated feature control cards.
"""
from PyQt6.QtWidgets import (
    QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel, QAbstractButton,
)
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint, QSize
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from gui.typography import FontSystem


class ModernToggleSwitch(QAbstractButton):
    """
    Sleek modern toggle switch with glowing track and smooth circular thumb.
    """
    def __init__(self, parent=None, checked: bool = True):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(checked)
        self.setFixedSize(44, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Track colors
        if self.isChecked():
            track_brush = QBrush(QColor("#4F46E5"))
            track_border = QColor("#6366F1")
            thumb_x = self.width() - 20
        else:
            track_brush = QBrush(QColor("#1A202E"))
            track_border = QColor("#2A344A")
            thumb_x = 4

        # Draw pill track
        painter.setPen(QPen(track_border, 1.2))
        painter.setBrush(track_brush)
        painter.drawRoundedRect(1, 1, self.width() - 2, self.height() - 2, 11, 11)

        # Draw glowing thumb
        painter.setPen(Qt.PenStyle.NoPen)
        if self.isChecked():
            painter.setBrush(QBrush(QColor("#FFFFFF")))
        else:
            painter.setBrush(QBrush(QColor("#94A3B8")))

        painter.drawEllipse(thumb_x, 4, 16, 16)
        painter.end()


class FeatureToggleCard(QFrame):
    """
    Luxury feature card with vector icon badge, title, subtitle description,
    and integrated ModernToggleSwitch. Clickable anywhere on the card.
    """
    toggled = pyqtSignal(bool)

    def __init__(
        self,
        icon_symbol: str,
        title: str,
        description: str,
        checked: bool = True,
        accent_color: str = "#6366F1",
        parent=None,
    ):
        super().__init__(parent)
        self.accent_color = accent_color
        self.setObjectName("surfaceCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QFrame#surfaceCard {
                background-color: #0E121B;
                border: 1px solid rgba(255, 255, 255, 0.07);
                border-radius: 8px;
            }
            QFrame#surfaceCard:hover {
                border-color: rgba(99, 102, 241, 0.4);
                background-color: #121622;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)

        # Left Icon Badge
        self.icon_badge = QLabel(icon_symbol)
        self.icon_badge.setFixedSize(36, 36)
        self.icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_badge.setFont(FontSystem.get_display_font(14))
        self.icon_badge.setStyleSheet(f"""
            background: {accent_color}18;
            color: {accent_color};
            border: 1px solid {accent_color}35;
            border-radius: 7px;
        """)
        layout.addWidget(self.icon_badge)

        # Middle Content
        text_v = QVBoxLayout()
        text_v.setSpacing(2)

        self.title_lbl = QLabel(title)
        self.title_lbl.setFont(FontSystem.get_display_font(12))
        self.title_lbl.setStyleSheet("color: #FFFFFF; font-weight: 600;")
        text_v.addWidget(self.title_lbl)

        self.desc_lbl = QLabel(description)
        self.desc_lbl.setFont(FontSystem.get_badge_font(9))
        self.desc_lbl.setStyleSheet("color: #64748B;")
        self.desc_lbl.setWordWrap(True)
        text_v.addWidget(self.desc_lbl)
        layout.addLayout(text_v, stretch=1)

        # Right Toggle Switch
        self.switch = ModernToggleSwitch(checked=checked)
        self.switch.toggled.connect(self._on_switch_toggled)
        layout.addWidget(self.switch)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.switch.toggle()
        super().mousePressEvent(event)

    def _on_switch_toggled(self, checked: bool):
        self.toggled.emit(checked)

    def isChecked(self) -> bool:
        return self.switch.isChecked()

    def setChecked(self, checked: bool):
        self.switch.setChecked(checked)

"""
Dark/Light Theme Manager for OrbitTraffic GUI.
"""
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

DARK_STYLESHEET = """
/* ── Global ─────────────────────────────────────────── */
* {
    font-family: 'Segoe UI', 'Inter', 'SF Pro', sans-serif;
}
QMainWindow, QWidget {
    background-color: #0f0f1a;
    color: #e2e8f0;
}
/* ── Tab Widget ──────────────────────────────────────── */
QTabWidget::pane {
    border: none;
    background: #0f0f1a;
}
QTabWidget#mainTabs > QTabBar::tab {
    background: #1a1a2e;
    color: #94a3b8;
    padding: 10px 22px;
    font-size: 12px;
    border: none;
    border-bottom: 2px solid transparent;
    min-width: 120px;
}
QTabWidget#mainTabs > QTabBar::tab:selected {
    color: #6c63ff;
    border-bottom: 2px solid #6c63ff;
    background: #12122a;
}
QTabWidget#mainTabs > QTabBar::tab:hover:!selected {
    color: #c4b5fd;
    background: #16162a;
}
/* ── Buttons ─────────────────────────────────────────── */
QPushButton {
    background: #6c63ff;
    color: #fff;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 12px;
}
QPushButton:hover {
    background: #7c74ff;
}
QPushButton:pressed {
    background: #5c54e0;
}
QPushButton:disabled {
    background: #2a2a3e;
    color: #555;
}
QPushButton#dangerBtn {
    background: #ef4444;
}
QPushButton#dangerBtn:hover {
    background: #dc2626;
}
QPushButton#successBtn {
    background: #22c55e;
    color: #000;
}
QPushButton#successBtn:hover {
    background: #16a34a;
}
QPushButton#secondaryBtn {
    background: #1e1e3a;
    color: #94a3b8;
    border: 1px solid #334155;
}
QPushButton#secondaryBtn:hover {
    background: #252545;
    color: #c4b5fd;
}
/* ── Input Fields ────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background: #1a1a2e;
    border: 1px solid #334155;
    border-radius: 6px;
    color: #e2e8f0;
    padding: 6px 10px;
    font-size: 12px;
    selection-background-color: #6c63ff;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid #6c63ff;
}
QComboBox::drop-down { border: none; }
QComboBox::down-arrow { color: #6c63ff; }
QComboBox QAbstractItemView {
    background: #1a1a2e;
    border: 1px solid #334155;
    color: #e2e8f0;
    selection-background-color: #6c63ff;
}
/* ── Tables ──────────────────────────────────────────── */
QTableWidget, QTableView {
    background: #0f0f1a;
    alternate-background-color: #12122a;
    color: #e2e8f0;
    border: 1px solid #1e1e3a;
    gridline-color: #1e1e3a;
    font-size: 12px;
}
QTableWidget::item:selected, QTableView::item:selected {
    background: #2d2d5e;
    color: #fff;
}
QHeaderView::section {
    background: #1a1a2e;
    color: #94a3b8;
    padding: 8px 12px;
    border: none;
    border-right: 1px solid #252545;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
/* ── Scroll Bars ─────────────────────────────────────── */
QScrollBar:vertical {
    background: #0f0f1a;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #334155;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #6c63ff; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
/* ── Group Boxes ─────────────────────────────────────── */
QGroupBox {
    border: 1px solid #1e1e3a;
    border-radius: 8px;
    margin-top: 16px;
    padding: 12px 10px 10px 10px;
    font-weight: 600;
    color: #94a3b8;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #6c63ff;
}
/* ── Progress Bar ────────────────────────────────────── */
QProgressBar {
    background: #1a1a2e;
    border: 1px solid #334155;
    border-radius: 4px;
    text-align: center;
    color: #e2e8f0;
    font-size: 11px;
    height: 18px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6c63ff, stop:1 #a78bfa);
    border-radius: 3px;
}
/* ── Labels ──────────────────────────────────────────── */
QLabel#sectionTitle {
    color: #c4b5fd;
    font-size: 14px;
    font-weight: bold;
}
QLabel#statValue {
    color: #6c63ff;
    font-size: 28px;
    font-weight: bold;
}
QLabel#statLabel {
    color: #64748b;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
/* ── Status Bar ──────────────────────────────────────── */
QStatusBar { border-top: 1px solid #1e1e3a; }
/* ── Checkboxes ──────────────────────────────────────── */
QCheckBox {
    color: #e2e8f0;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 3px;
    border: 1px solid #334155;
    background: #1a1a2e;
}
QCheckBox::indicator:checked {
    background: #6c63ff;
    border: 1px solid #6c63ff;
}
/* ── Sliders ─────────────────────────────────────────── */
QSlider::groove:horizontal {
    height: 4px;
    background: #1e1e3a;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #6c63ff;
    width: 16px;
    height: 16px;
    border-radius: 8px;
    margin: -6px 0;
}
QSlider::sub-page:horizontal {
    background: #6c63ff;
    border-radius: 2px;
}
/* ── Tooltips ─────────────────────────────────────────── */
QToolTip {
    background: #1e1e3a;
    color: #e2e8f0;
    border: 1px solid #6c63ff;
    padding: 4px 8px;
    border-radius: 4px;
}
/* ── Frames / Cards ──────────────────────────────────── */
QFrame#statCard {
    background: #12122a;
    border: 1px solid #1e1e3a;
    border-radius: 10px;
    padding: 15px;
}
QFrame#statCard:hover {
    border: 1px solid #6c63ff;
}
"""


def apply_dark_theme(app_or_widget):
    """Apply the dark theme to the application or a widget."""
    if isinstance(app_or_widget, QApplication):
        app_or_widget.setStyleSheet(DARK_STYLESHEET)
    else:
        app_or_widget.setStyleSheet(DARK_STYLESHEET)

"""
OrbitTraffic — Next-Gen Obsidian Design System & Stylesheet
Crafted with high-contrast typography, refined glassmorphism,
subtle border glows, and crisp enterprise UI hierarchy.
"""

MODERN_DARK_THEME = """
/* ── Reset & Global Typography ─────────────────────────────────── */
* {
    font-family: 'Segoe UI Variable Text', 'Segoe UI', 'Inter', -apple-system, sans-serif;
    outline: none;
}

QMainWindow, QWidget#centralWidget, QDialog {
    background-color: #080A0F;
    color: #F8FAFC;
}

/* ── Left Navigation Sidebar ───────────────────────────────────── */
QFrame#sidebarFrame {
    background-color: #0B0E16;
    border-right: 1px solid rgba(255, 255, 255, 0.07);
}

QLabel.navCategory {
    color: #475569;
    font-family: 'Bahnschrift', 'Segoe UI Variable Small', sans-serif;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1.5px;
    padding: 10px 8px 4px 8px;
    text-transform: uppercase;
}

QPushButton.navBtn {
    background-color: transparent;
    color: #94A3B8;
    border: none;
    border-radius: 7px;
    padding: 9px 12px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
    margin: 1px 0;
}

QPushButton.navBtn:hover {
    background-color: rgba(255, 255, 255, 0.04);
    color: #F1F5F9;
}

QPushButton.navBtn:checked, QPushButton.navBtn.active {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(99, 102, 241, 0.16),
        stop:0.6 rgba(99, 102, 241, 0.04),
        stop:1 transparent);
    color: #A5B4FC;
    border-left: 3px solid #6366F1;
    font-weight: 600;
}

/* ── Top App Bar ───────────────────────────────────────────────── */
QFrame#topBarFrame {
    background-color: #0A0D14;
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
}

/* ── Buttons ───────────────────────────────────────────────────── */
QPushButton {
    background-color: #121622;
    color: #E2E8F0;
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 6px;
    padding: 7px 16px;
    font-size: 12px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #181E2E;
    border-color: rgba(255, 255, 255, 0.18);
    color: #FFFFFF;
}

QPushButton:pressed {
    background-color: #0E121B;
}

QPushButton#primaryActionBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:1 #7C3AED);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.15);
    font-weight: 600;
    padding: 8px 18px;
    border-radius: 6px;
}

QPushButton#primaryActionBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5B52F2, stop:1 #8B5CF6);
    border-color: rgba(255, 255, 255, 0.3);
}

QPushButton#successBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10B981);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.15);
    font-weight: 600;
}

QPushButton#dangerBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #B91C1C, stop:1 #EF4444);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.15);
    font-weight: 600;
}

QPushButton#secondaryBtn {
    background-color: rgba(255, 255, 255, 0.03);
    color: #94A3B8;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

QPushButton#secondaryBtn:hover {
    background-color: rgba(255, 255, 255, 0.07);
    color: #F8FAFC;
    border-color: rgba(255, 255, 255, 0.16);
}

/* ── Surface Cards & Glass Panels ──────────────────────────────── */
QFrame.kpiCard, QFrame#surfaceCard {
    background-color: #0E121B;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 9px;
}

QFrame.kpiCard:hover, QFrame#surfaceCard:hover {
    border-color: rgba(99, 102, 241, 0.35);
    background-color: #111622;
}

/* ── Form Inputs ───────────────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #0A0D14;
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 6px;
    color: #F8FAFC;
    padding: 7px 11px;
    font-size: 12px;
    selection-background-color: #4F46E5;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid #6366F1;
    background-color: #0D111A;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #0D111A;
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #F8FAFC;
    selection-background-color: #1E273D;
    padding: 4px;
}

/* ── Modern Flat Tables ────────────────────────────────────────── */
QTableWidget, QTableView {
    background-color: #0A0D14;
    alternate-background-color: #0E1119;
    color: #F1F5F9;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    gridline-color: transparent;
    font-size: 12px;
}

QTableWidget::item {
    padding: 9px 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

QTableWidget::item:selected {
    background-color: rgba(99, 102, 241, 0.15);
    color: #C7D2FE;
}

QHeaderView::section {
    background-color: #080A0E;
    color: #64748B;
    font-family: 'Bahnschrift', 'Segoe UI Variable Small', sans-serif;
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* ── Progress & Status Bars ────────────────────────────────────── */
QProgressBar {
    background-color: #090C12;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 5px;
    text-align: center;
    color: #94A3B8;
    font-family: 'Cascadia Code', monospace;
    font-size: 11px;
    height: 18px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:1 #06B6D4);
    border-radius: 4px;
}

/* ── Scrollbars ────────────────────────────────────────────────── */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.12);
    min-height: 25px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(99, 102, 241, 0.5);
}

QScrollBar:horizontal {
    background: transparent;
    height: 6px;
}

QScrollBar::handle:horizontal {
    background: rgba(255, 255, 255, 0.12);
    border-radius: 3px;
}

/* ── Checkboxes ────────────────────────────────────────────────── */
QCheckBox {
    color: #E2E8F0;
    spacing: 8px;
    font-size: 12px;
}

QCheckBox::indicator {
    width: 17px;
    height: 17px;
    border-radius: 4px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    background-color: #0A0D14;
}

QCheckBox::indicator:hover {
    border-color: #6366F1;
}

QCheckBox::indicator:checked {
    background-color: #6366F1;
    border-color: #6366F1;
}

/* ── Group Boxes ───────────────────────────────────────────────── */
QGroupBox {
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    margin-top: 14px;
    padding: 16px 14px 14px 14px;
    font-family: 'Bahnschrift', sans-serif;
    font-weight: 600;
    font-size: 11px;
    letter-spacing: 0.5px;
    color: #94A3B8;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #818CF8;
}
"""


def apply_modern_theme(app_or_widget):
    app_or_widget.setStyleSheet(MODERN_DARK_THEME)

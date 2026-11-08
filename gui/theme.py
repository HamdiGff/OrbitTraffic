"""
OrbitTraffic — Ultra-Modern Dark Theme & Design System
Crafted for enterprise-grade analytics, dark mode depth, crisp typography,
refined glassmorphism, and seamless UI hierarchy.
"""

MODERN_DARK_THEME = """
/* ── Global Styles ─────────────────────────────────────────────── */
* {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Inter', Roboto, sans-serif;
    outline: none;
}

QMainWindow, QWidget#centralWidget, QDialog {
    background-color: #090C12;
    color: #F8FAFC;
}

/* ── Sidebar Navigation ────────────────────────────────────────── */
QFrame#sidebarFrame {
    background-color: #0D111A;
    border-right: 1px solid #1A2133;
}

QPushButton.navBtn {
    background-color: transparent;
    color: #94A3B8;
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
}

QPushButton.navBtn:hover {
    background-color: #151C2C;
    color: #F8FAFC;
}

QPushButton.navBtn:checked, QPushButton.navBtn.active {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1E273D, stop:1 #171E2F);
    color: #818CF8;
    border-left: 3px solid #6366F1;
    font-weight: 600;
}

/* ── Top App Bar ───────────────────────────────────────────────── */
QFrame#topBarFrame {
    background-color: #0D111A;
    border-bottom: 1px solid #1A2133;
}

/* ── Buttons ───────────────────────────────────────────────────── */
QPushButton {
    background-color: #1A2133;
    color: #F8FAFC;
    border: 1px solid #26314D;
    border-radius: 6px;
    padding: 7px 16px;
    font-size: 12px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #232D45;
    border-color: #38486F;
}

QPushButton:pressed {
    background-color: #161C2C;
}

QPushButton#primaryActionBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:1 #8B5CF6);
    color: #FFFFFF;
    border: none;
    font-weight: 600;
    padding: 8px 18px;
}

QPushButton#primaryActionBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7175F3, stop:1 #9A6EF8);
}

QPushButton#successBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10B981);
    color: #FFFFFF;
    border: none;
    font-weight: 600;
}

QPushButton#dangerBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #DC2626, stop:1 #EF4444);
    color: #FFFFFF;
    border: none;
    font-weight: 600;
}

QPushButton#secondaryBtn {
    background-color: #131824;
    color: #94A3B8;
    border: 1px solid #1E2638;
}

QPushButton#secondaryBtn:hover {
    background-color: #1B2233;
    color: #F8FAFC;
    border-color: #2D3952;
}

/* ── KPI & Surface Cards ───────────────────────────────────────── */
QFrame.kpiCard, QFrame#surfaceCard {
    background-color: #101522;
    border: 1px solid #1B2337;
    border-radius: 10px;
}

QFrame.kpiCard:hover {
    border-color: #2A3654;
    background-color: #121827;
}

/* ── Input Fields ──────────────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #0E131E;
    border: 1px solid #1E273D;
    border-radius: 6px;
    color: #F8FAFC;
    padding: 7px 12px;
    font-size: 12px;
    selection-background-color: #6366F1;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid #6366F1;
    background-color: #111726;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #101522;
    border: 1px solid #1F2A42;
    color: #F8FAFC;
    selection-background-color: #263352;
    padding: 4px;
}

/* ── Tables & Lists ────────────────────────────────────────────── */
QTableWidget, QTableView {
    background-color: #0E131E;
    alternate-background-color: #111726;
    color: #F8FAFC;
    border: 1px solid #1A2236;
    border-radius: 8px;
    gridline-color: #161E30;
    font-size: 12px;
}

QTableWidget::item {
    padding: 8px 10px;
    border-bottom: 1px solid #161E30;
}

QTableWidget::item:selected {
    background-color: #202A42;
    color: #818CF8;
}

QHeaderView::section {
    background-color: #0D121D;
    color: #64748B;
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid #1A2236;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ── Progress Bar ──────────────────────────────────────────────── */
QProgressBar {
    background-color: #0E131E;
    border: 1px solid #1A2236;
    border-radius: 5px;
    text-align: center;
    color: #94A3B8;
    font-size: 11px;
    height: 18px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:1 #10B981);
    border-radius: 4px;
}

/* ── Scrollbars ────────────────────────────────────────────────── */
QScrollBar:vertical {
    background: #090C12;
    width: 7px;
    margin: 0;
    border-radius: 3px;
}

QScrollBar::handle:vertical {
    background: #1F283E;
    min-height: 25px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: #344368;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: #090C12;
    height: 7px;
    border-radius: 3px;
}

QScrollBar::handle:horizontal {
    background: #1F283E;
    border-radius: 3px;
}

/* ── Group Boxes ───────────────────────────────────────────────── */
QGroupBox {
    border: 1px solid #1B2338;
    border-radius: 8px;
    margin-top: 14px;
    padding: 16px 14px 14px 14px;
    font-weight: 600;
    font-size: 12px;
    color: #CBD5E1;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #818CF8;
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
    border: 1px solid #2B3754;
    background-color: #0E131E;
}

QCheckBox::indicator:hover {
    border-color: #6366F1;
}

QCheckBox::indicator:checked {
    background-color: #6366F1;
    border-color: #6366F1;
}
"""


def apply_modern_theme(app_or_widget):
    app_or_widget.setStyleSheet(MODERN_DARK_THEME)

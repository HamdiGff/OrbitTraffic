"""
OrbitTraffic — Redesigned Top Action Bar
Features typographic hierarchy, live throughput meter, and clean global buttons.
"""
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton,
)
from PyQt6.QtCore import pyqtSignal
from gui.typography import FontSystem


class TopBar(QFrame):
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("topBarFrame")
        self.setFixedHeight(56)
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(22, 0, 22, 0)
        layout.setSpacing(14)

        # Title & Breadcrumb
        self.section_title = QLabel("DASHBOARD RADAR")
        self.section_title.setFont(FontSystem.get_display_font(13))
        self.section_title.setStyleSheet("color: #FFFFFF; font-weight: 700; letter-spacing: 0.5px;")
        layout.addWidget(self.section_title)

        # Operational Badges
        pogo_badge = QLabel("POGO-STICKING ACTIVE")
        pogo_badge.setFont(FontSystem.get_badge_font(8))
        pogo_badge.setStyleSheet("""
            background: rgba(30, 58, 138, 0.4);
            color: #93C5FD;
            padding: 3px 8px;
            border-radius: 4px;
            border: 1px solid rgba(59, 130, 246, 0.35);
        """)
        layout.addWidget(pogo_badge)

        stealth_badge = QLabel("STEALTH LVL 10")
        stealth_badge.setFont(FontSystem.get_badge_font(8))
        stealth_badge.setStyleSheet("""
            background: rgba(6, 78, 59, 0.4);
            color: #6EE7B7;
            padding: 3px 8px;
            border-radius: 4px;
            border: 1px solid rgba(16, 185, 129, 0.35);
        """)
        layout.addWidget(stealth_badge)

        layout.addStretch()

        # Throughput Ticker
        self.throughput_lbl = QLabel("0.0 req/min")
        self.throughput_lbl.setFont(FontSystem.get_mono_font(11))
        self.throughput_lbl.setStyleSheet("color: #38BDF8; font-weight: 600; margin-right: 12px;")
        layout.addWidget(self.throughput_lbl)

        # Controls
        self.btn_start = QPushButton("▶  Start Traffic")
        self.btn_start.setObjectName("primaryActionBtn")
        self.btn_start.setFont(FontSystem.get_badge_font(9))
        self.btn_start.clicked.connect(self.start_requested.emit)
        layout.addWidget(self.btn_start)

        self.btn_stop = QPushButton("⏹  Emergency Kill")
        self.btn_stop.setObjectName("dangerBtn")
        self.btn_stop.setFont(FontSystem.get_badge_font(9))
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_requested.emit)
        layout.addWidget(self.btn_stop)

    def set_title(self, title: str):
        self.section_title.setText(title.upper())

    def set_running(self, running: bool):
        self.btn_start.setEnabled(not running)
        self.btn_stop.setEnabled(running)

    def update_throughput(self, req_per_min: float):
        self.throughput_lbl.setText(f"⚡ {req_per_min:.1f} req/min")

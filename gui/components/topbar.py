"""
OrbitTraffic — Top Action Bar Component
Provides breadcrumb title, live operational badges, and quick global controls.
"""
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal


class TopBar(QFrame):
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("topBarFrame")
        self.setFixedHeight(58)
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(14)

        # Title & Section Info
        self.section_title = QLabel("Dashboard Radar")
        self.section_title.setStyleSheet("color: #FFFFFF; font-size: 15px; font-weight: 700;")
        layout.addWidget(self.section_title)

        # Badges
        pogo_badge = QLabel("⚡ POGO-STICKING ACTIVE")
        pogo_badge.setStyleSheet("""
            background: #172554;
            color: #60A5FA;
            font-size: 10px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 4px;
            border: 1px solid #1E40AF;
        """)
        layout.addWidget(pogo_badge)

        stealth_badge = QLabel("🛡️ STEALTH LEVEL 10")
        stealth_badge.setStyleSheet("""
            background: #064E3B;
            color: #34D399;
            font-size: 10px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 4px;
            border: 1px solid #065F46;
        """)
        layout.addWidget(stealth_badge)

        layout.addStretch()

        # Throughput Ticker
        self.throughput_lbl = QLabel("Throughput: 0 req/min")
        self.throughput_lbl.setStyleSheet("color: #94A3B8; font-size: 11px; margin-right: 10px;")
        layout.addWidget(self.throughput_lbl)

        # Quick Controls
        self.btn_start = QPushButton("▶  Start Traffic")
        self.btn_start.setObjectName("primaryActionBtn")
        self.btn_start.clicked.connect(self.start_requested.emit)
        layout.addWidget(self.btn_start)

        self.btn_stop = QPushButton("⏹  Emergency Kill")
        self.btn_stop.setObjectName("dangerBtn")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_requested.emit)
        layout.addWidget(self.btn_stop)

    def set_title(self, title: str):
        self.section_title.setText(title)

    def set_running(self, running: bool):
        self.btn_start.setEnabled(not running)
        self.btn_stop.setEnabled(running)

    def update_throughput(self, req_per_min: float):
        self.throughput_lbl.setText(f"⚡ Throughput: {req_per_min:.1f} req/min")

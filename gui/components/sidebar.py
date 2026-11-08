"""
OrbitTraffic — Modern Sidebar Component
Includes brand badge, navigation items with custom indicators, and system telemetry stats.
"""
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QProgressBar,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
import psutil


class Sidebar(QFrame):
    tab_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarFrame")
        self.setFixedWidth(240)
        self.buttons = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 18, 14, 16)
        layout.setSpacing(6)

        # ── 1. Brand Logo & Title ─────────────────────────────────
        brand_widget = QWidget()
        brand_layout = QHBoxLayout(brand_widget)
        brand_layout.setContentsMargins(4, 2, 4, 12)
        brand_layout.setSpacing(10)

        # Sleek Orb Icon
        logo_lbl = QLabel("🪐")
        logo_lbl.setStyleSheet("font-size: 24px;")
        brand_layout.addWidget(logo_lbl)

        title_v = QVBoxLayout()
        title_v.setSpacing(1)
        name_lbl = QLabel("OrbitTraffic")
        name_lbl.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: 700; letter-spacing: 0.5px;")

        badge_row = QHBoxLayout()
        badge_row.setSpacing(6)
        tag_lbl = QLabel("ENTERPRISE")
        tag_lbl.setStyleSheet(
            "background: #1E293B; color: #818CF8; font-size: 9px; "
            "font-weight: 700; padding: 2px 6px; border-radius: 4px; border: 1px solid #312E81;"
        )
        ver_lbl = QLabel("v2.0")
        ver_lbl.setStyleSheet("color: #64748B; font-size: 10px; font-weight: 600;")
        badge_row.addWidget(tag_lbl)
        badge_row.addWidget(ver_lbl)
        badge_row.addStretch()

        title_v.addWidget(name_lbl)
        title_v.addLayout(badge_row)
        brand_layout.addLayout(title_v)

        layout.addWidget(brand_widget)

        # Divider
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #1A2133; max-height: 1px; margin: 4px 0 10px 0;")
        layout.addWidget(sep)

        # ── 2. Navigation Items ───────────────────────────────────
        nav_section_lbl = QLabel("WORKSPACE")
        nav_section_lbl.setStyleSheet("color: #475569; font-size: 10px; font-weight: 700; letter-spacing: 1px; padding-left: 8px; margin-bottom: 4px;")
        layout.addWidget(nav_section_lbl)

        nav_items = [
            ("📊", "Dashboard", 0),
            ("🚀", "Campaigns & Flow", 1),
            ("🌐", "Proxy Radar", 2),
            ("🎯", "Keyword Studio", 3),
            ("🧪", "Fingerprint Lab", 4),
            ("🛰️", "Live Workers", 5),
            ("⚙️", "Settings & Updates", 6),
        ]

        for icon, title, index in nav_items:
            btn = QPushButton(f"{icon}   {title}")
            btn.setProperty("class", "navBtn")
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.clicked.connect(lambda checked, idx=index: self._on_btn_clicked(idx))
            self.buttons.append(btn)
            layout.addWidget(btn)

        self.buttons[0].setChecked(True)

        layout.addStretch()

        # ── 3. Bottom Telemetry Widget ────────────────────────────
        telemetry_box = QFrame()
        telemetry_box.setStyleSheet("""
            background-color: #101522;
            border: 1px solid #1C2436;
            border-radius: 8px;
            padding: 8px;
        """)
        t_layout = QVBoxLayout(telemetry_box)
        t_layout.setContentsMargins(8, 8, 8, 8)
        t_layout.setSpacing(6)

        t_title = QLabel("SYSTEM RADAR")
        t_title.setStyleSheet("color: #64748B; font-size: 10px; font-weight: 700; letter-spacing: 0.8px;")
        t_layout.addWidget(t_title)

        # CPU bar
        cpu_row = QHBoxLayout()
        cpu_lbl = QLabel("CPU Load")
        cpu_lbl.setStyleSheet("color: #94A3B8; font-size: 10px;")
        self.cpu_val = QLabel("12%")
        self.cpu_val.setStyleSheet("color: #38BDF8; font-size: 10px; font-weight: 600;")
        cpu_row.addWidget(cpu_lbl)
        cpu_row.addStretch()
        cpu_row.addWidget(self.cpu_val)
        t_layout.addLayout(cpu_row)

        self.cpu_bar = QProgressBar()
        self.cpu_bar.setFixedHeight(4)
        self.cpu_bar.setTextVisible(False)
        self.cpu_bar.setValue(12)
        t_layout.addWidget(self.cpu_bar)

        # Status indicator
        status_row = QHBoxLayout()
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #10B981; font-size: 12px;")
        self.status_text = QLabel("Engine Ready")
        self.status_text.setStyleSheet("color: #E2E8F0; font-size: 11px; font-weight: 500;")
        status_row.addWidget(self.status_dot)
        status_row.addWidget(self.status_text)
        status_row.addStretch()
        t_layout.addLayout(status_row)

        layout.addWidget(telemetry_box)

    def _on_btn_clicked(self, index: int):
        self.tab_changed.emit(index)

    def select_tab(self, index: int):
        if 0 <= index < len(self.buttons):
            self.buttons[index].setChecked(True)

    def update_telemetry(self, cpu_pct: float, ram_pct: float, is_running: bool):
        self.cpu_val.setText(f"{cpu_pct:.0f}%")
        self.cpu_bar.setValue(int(cpu_pct))
        if is_running:
            self.status_dot.setStyleSheet("color: #38BDF8; font-size: 12px;")
            self.status_text.setText("Generating Traffic")
        else:
            self.status_dot.setStyleSheet("color: #10B981; font-size: 12px;")
            self.status_text.setText("Engine Ready")

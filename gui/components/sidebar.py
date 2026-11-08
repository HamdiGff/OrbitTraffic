"""
OrbitTraffic — Redesigned Modern Sidebar Component
Features geometric iconography, categorized navigation groups,
and monospace system telemetry gauges.
"""
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QProgressBar,
)
from PyQt6.QtCore import Qt, pyqtSignal
from gui.typography import FontSystem


class Sidebar(QFrame):
    tab_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarFrame")
        self.setFixedWidth(250)
        self.buttons = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 18, 14, 16)
        layout.setSpacing(4)

        # ── 1. Brand Logo & Title ─────────────────────────────────
        brand_widget = QWidget()
        brand_layout = QHBoxLayout(brand_widget)
        brand_layout.setContentsMargins(6, 2, 6, 14)
        brand_layout.setSpacing(10)

        # Geometric Hex Emblem
        logo_glyph = QLabel("⬡")
        logo_glyph.setFont(FontSystem.get_display_font(22))
        logo_glyph.setStyleSheet("color: #818CF8; font-weight: 900;")
        brand_layout.addWidget(logo_glyph)

        title_v = QVBoxLayout()
        title_v.setSpacing(2)
        name_lbl = QLabel("ORBITTRAFFIC")
        name_lbl.setFont(FontSystem.get_display_font(13))
        name_lbl.setStyleSheet("color: #FFFFFF; font-weight: 800; letter-spacing: 1.5px;")

        badge_row = QHBoxLayout()
        badge_row.setSpacing(6)
        tag_lbl = QLabel("ENTERPRISE")
        tag_lbl.setFont(FontSystem.get_badge_font(8))
        tag_lbl.setStyleSheet(
            "background: rgba(99, 102, 241, 0.15); color: #A5B4FC; "
            "padding: 1px 6px; border-radius: 4px; border: 1px solid rgba(99, 102, 241, 0.3);"
        )
        ver_lbl = QLabel("v2.4")
        ver_lbl.setFont(FontSystem.get_mono_font(9))
        ver_lbl.setStyleSheet("color: #64748B;")
        badge_row.addWidget(tag_lbl)
        badge_row.addWidget(ver_lbl)
        badge_row.addStretch()

        title_v.addWidget(name_lbl)
        title_v.addLayout(badge_row)
        brand_layout.addLayout(title_v)

        layout.addWidget(brand_widget)

        # Hairline divider
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: rgba(255, 255, 255, 0.06); max-height: 1px; margin-bottom: 8px;")
        layout.addWidget(sep)

        # ── 2. Categorized Navigation ─────────────────────────────
        nav_sections = [
            ("// OVERVIEW", [
                ("◈", "Dashboard Radar", 0),
            ]),
            ("// TRAFFIC ENGINES", [
                ("⚡", "Campaigns & Flow", 1),
                ("⌁", "Keyword Studio", 3),
            ]),
            ("// INFRASTRUCTURE", [
                ("🌐", "Proxy Fleet", 2),
                ("🛡️", "Fingerprint Lab", 4),
                ("■", "Live Workers", 5),
            ]),
            ("// PREFERENCES", [
                ("⚙", "Global Settings", 6),
            ])
        ]

        for category_title, items in nav_sections:
            cat_lbl = QLabel(category_title)
            cat_lbl.setProperty("class", "navCategory")
            cat_lbl.setFont(FontSystem.get_badge_font(8))
            layout.addWidget(cat_lbl)

            for icon, title, index in items:
                btn = QPushButton(f"  {icon}   {title}")
                btn.setProperty("class", "navBtn")
                btn.setCheckable(True)
                btn.setAutoExclusive(True)
                btn.clicked.connect(lambda checked, idx=index: self._on_btn_clicked(idx))
                self.buttons.append((index, btn))
                layout.addWidget(btn)

        # Select Dashboard by default
        self.buttons[0][1].setChecked(True)

        layout.addStretch()

        # ── 3. Bottom Telemetry Widget ────────────────────────────
        telemetry_box = QFrame()
        telemetry_box.setStyleSheet("""
            background-color: #0E121B;
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-radius: 8px;
            padding: 10px;
        """)
        t_layout = QVBoxLayout(telemetry_box)
        t_layout.setContentsMargins(8, 8, 8, 8)
        t_layout.setSpacing(6)

        t_title = QLabel("SYSTEM RADAR")
        t_title.setFont(FontSystem.get_badge_font(8))
        t_title.setStyleSheet("color: #64748B; letter-spacing: 1px;")
        t_layout.addWidget(t_title)

        # CPU bar
        cpu_row = QHBoxLayout()
        cpu_lbl = QLabel("CPU Load")
        cpu_lbl.setStyleSheet("color: #94A3B8; font-size: 10px;")
        self.cpu_val = QLabel("0%")
        self.cpu_val.setFont(FontSystem.get_mono_font(10))
        self.cpu_val.setStyleSheet("color: #38BDF8; font-weight: 600;")
        cpu_row.addWidget(cpu_lbl)
        cpu_row.addStretch()
        cpu_row.addWidget(self.cpu_val)
        t_layout.addLayout(cpu_row)

        self.cpu_bar = QProgressBar()
        self.cpu_bar.setFixedHeight(4)
        self.cpu_bar.setTextVisible(False)
        self.cpu_bar.setValue(10)
        t_layout.addWidget(self.cpu_bar)

        # Status row
        status_row = QHBoxLayout()
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #10B981; font-size: 11px;")
        self.status_text = QLabel("Engine Ready")
        self.status_text.setFont(FontSystem.get_badge_font(9))
        self.status_text.setStyleSheet("color: #E2E8F0;")
        status_row.addWidget(self.status_dot)
        status_row.addWidget(self.status_text)
        status_row.addStretch()
        t_layout.addLayout(status_row)

        layout.addWidget(telemetry_box)

    def _on_btn_clicked(self, index: int):
        self.tab_changed.emit(index)

    def select_tab(self, target_idx: int):
        for idx, btn in self.buttons:
            if idx == target_idx:
                btn.setChecked(True)

    def update_telemetry(self, cpu_pct: float, ram_pct: float, is_running: bool):
        self.cpu_val.setText(f"{cpu_pct:.0f}%")
        self.cpu_bar.setValue(int(cpu_pct))
        if is_running:
            self.status_dot.setStyleSheet("color: #38BDF8; font-size: 11px;")
            self.status_text.setText("Active Generating")
        else:
            self.status_dot.setStyleSheet("color: #10B981; font-size: 11px;")
            self.status_text.setText("Engine Ready")

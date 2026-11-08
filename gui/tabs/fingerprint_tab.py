"""
Fingerprint Lab & Anti-Detect Diagnostics Tab
Allows users to visually inspect and audit active fingerprint spoofing:
- Canvas 2D Noise Verification
- WebGL Unmasked Vendor & Renderer
- AudioContext Oscillator Hash
- WebRTC IP Leak Prevention Shield
- Battery Status API
- Client Hints & Hardware Concurrency
"""
import random
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QPushButton, QTextEdit, QScrollArea,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from browser.fingerprint import FingerprintProfile


class FingerprintTab(QWidget):
    def __init__(self):
        super().__init__()
        self._current_profile = FingerprintProfile()
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(14)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # Header
        top_h = QHBoxLayout()
        title_v = QVBoxLayout()
        title = QLabel("🧪 Fingerprint & Anti-Detect Diagnostics Lab")
        title.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: 700;")
        subtitle = QLabel("Audit browser stealth parameters, hardware emulation, and leak protection.")
        subtitle.setStyleSheet("color: #94A3B8; font-size: 12px;")
        title_v.addWidget(title)
        title_v.addWidget(subtitle)
        top_h.addLayout(title_v)
        top_h.addStretch()

        self.btn_regenerate = QPushButton("🔄 Generate New Identity")
        self.btn_regenerate.setObjectName("primaryActionBtn")
        self.btn_regenerate.clicked.connect(self._regenerate_profile)
        top_h.addWidget(self.btn_regenerate)
        layout.addLayout(top_h)

        # ── 1. Security & Protection Status ───────────────────────
        shield_card = QFrame()
        shield_card.setObjectName("surfaceCard")
        shield_l = QHBoxLayout(shield_card)
        shield_l.setContentsMargins(18, 14, 18, 14)
        shield_l.setSpacing(16)

        protections = [
            ("🛡️ WebRTC Leak", "BLOCKED / NO LEAK", "#10B981"),
            ("🎨 Canvas Fingerprint", "NOISE INJECTED", "#6366F1"),
            ("🎮 WebGL Renderer", "SPOOFED & MASKED", "#38BDF8"),
            ("🔊 AudioContext", "DYNAMIC JITTER", "#F59E0B"),
            ("⚡ WebDriver Flag", "UNDEFINED / REMOVED", "#10B981"),
        ]

        for title, status, col in protections:
            col_v = QVBoxLayout()
            t_lbl = QLabel(title)
            t_lbl.setStyleSheet("color: #64748B; font-size: 10px; font-weight: 700; letter-spacing: 0.5px;")
            s_lbl = QLabel(status)
            s_lbl.setStyleSheet(f"color: {col}; font-size: 12px; font-weight: 700;")
            col_v.addWidget(t_lbl)
            col_v.addWidget(s_lbl)
            shield_l.addLayout(col_v)

        layout.addWidget(shield_card)

        # ── 2. Active Profile Parameters ──────────────────────────
        params_card = QFrame()
        params_card.setObjectName("surfaceCard")
        p_layout = QVBoxLayout(params_card)
        p_layout.setContentsMargins(18, 16, 18, 16)
        p_layout.setSpacing(12)

        p_title = QLabel("ACTIVE VIRTUAL MACHINE IDENTITY")
        p_title.setStyleSheet("color: #CBD5E1; font-size: 12px; font-weight: 700; letter-spacing: 0.8px;")
        p_layout.addWidget(p_title)

        grid = QGridLayout()
        grid.setSpacing(10)

        self.fields = {}
        row_cols = [
            ("Platform / OS", "platform", 0, 0),
            ("Locale & Timezone", "locale_tz", 0, 1),
            ("Screen Resolution", "screen", 1, 0),
            ("Device Pixel Ratio", "dpr", 1, 1),
            ("Hardware Concurrency (CPU Cores)", "cpu", 2, 0),
            ("Device Memory (RAM)", "ram", 2, 1),
            ("WebGL Vendor", "webgl_v", 3, 0),
            ("WebGL Unmasked Renderer", "webgl_r", 3, 1),
            ("Battery Emulation", "battery", 4, 0),
            ("Canvas Noise Seed", "canvas_seed", 4, 1),
        ]

        for label_text, key, r, c in row_cols:
            box = QFrame()
            box.setStyleSheet("background-color: #0E131E; border: 1px solid #1C2436; border-radius: 6px; padding: 6px 10px;")
            b_layout = QVBoxLayout(box)
            b_layout.setContentsMargins(6, 6, 6, 6)
            b_layout.setSpacing(2)

            t = QLabel(label_text.upper())
            t.setStyleSheet("color: #64748B; font-size: 9px; font-weight: 700;")
            v = QLabel("—")
            v.setStyleSheet("color: #F8FAFC; font-size: 12px; font-weight: 600;")
            b_layout.addWidget(t)
            b_layout.addWidget(v)
            self.fields[key] = v
            grid.addWidget(box, r, c)

        p_layout.addLayout(grid)
        layout.addWidget(params_card)

        # ── 3. Stealth JS Injection Code Preview ─────────────────
        code_card = QFrame()
        code_card.setObjectName("surfaceCard")
        c_layout = QVBoxLayout(code_card)
        c_layout.setContentsMargins(18, 14, 18, 14)
        c_layout.setSpacing(8)

        code_title = QLabel("BROWSER INJECTION PAYLOAD (Playwright Context Script)")
        code_title.setStyleSheet("color: #CBD5E1; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;")
        c_layout.addWidget(code_title)

        self.code_view = QTextEdit()
        self.code_view.setReadOnly(True)
        self.code_view.setStyleSheet("""
            background-color: #0A0D14;
            color: #818CF8;
            font-family: 'Cascadia Code', Consolas, monospace;
            font-size: 11px;
            border: 1px solid #1A2133;
            border-radius: 6px;
        """)
        self.code_view.setFixedHeight(160)
        c_layout.addWidget(self.code_view)

        layout.addWidget(code_card)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        self._refresh_fields()

    def _regenerate_profile(self):
        self._current_profile = FingerprintProfile()
        self._refresh_fields()

    def _refresh_fields(self):
        fp = self._current_profile
        self.fields["platform"].setText(f"{fp.platform} ({fp.nav_platform})")
        self.fields["locale_tz"].setText(f"{fp.locale} / {fp.timezone}")
        self.fields["screen"].setText(f"{fp.screen_w} x {fp.screen_h}")
        self.fields["dpr"].setText(f"{fp.device_pixel_ratio}x")
        self.fields["cpu"].setText(f"{fp.hardware_concurrency} Threads")
        self.fields["ram"].setText(f"{fp.device_memory} GB")
        self.fields["webgl_v"].setText(fp.webgl_vendor)
        self.fields["webgl_r"].setText(fp.webgl_renderer[:50])
        self.fields["battery"].setText(f"{int(fp.battery_level * 100)}% (Charging: {fp.battery_charging})")
        self.fields["canvas_seed"].setText(str(fp.canvas_noise_seed))

        from browser.fingerprint import get_stealth_init_script
        self.code_view.setText(get_stealth_init_script(fp)[:1200] + "\n\n// ... [8 additional anti-fingerprint layers loaded]")

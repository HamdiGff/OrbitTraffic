"""
OrbitTraffic — Redesigned Modern Master GUI Application Window
Constructed with:
- Left Navigation Sidebar with live telemetry meter
- Top Action Bar with live throughput ticker & emergency controls
- Seamless QStackedWidget transitioning between 7 specialized studios:
  0. Dashboard Radar
  1. Campaigns & Flow Studio
  2. Proxy Fleet Radar
  3. Keyword & SERP Studio
  4. Fingerprint & Anti-Detect Lab
  5. Live Worker Thread Matrix
  6. Settings & Security
"""
import sys
import time
import psutil
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QStatusBar,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from gui.theme import apply_modern_theme
from gui.components.sidebar import Sidebar
from gui.components.topbar import TopBar

from gui.tabs.dashboard_tab import DashboardTab
from gui.tabs.campaigns_tab import CampaignsTab
from gui.tabs.proxy_tab import ProxyTab
from gui.tabs.keywords_tab import KeywordsTab
from gui.tabs.fingerprint_tab import FingerprintTab
from gui.tabs.workers_tab import WorkersTab
from gui.tabs.settings_tab import SettingsTab
from utils.logger import get_logger

logger = get_logger("gui.app")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OrbitTraffic Enterprise v2.0 — Organic Traffic Intelligence & RankBrain Booster")
        self.setMinimumSize(1340, 840)
        self.resize(1440, 900)

        # Apply ultra-modern dark theme
        apply_modern_theme(self)

        self._build_layout()
        self._wire_signals()
        self._start_system_monitors()

    def _build_layout(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        main_h = QHBoxLayout(central)
        main_h.setContentsMargins(0, 0, 0, 0)
        main_h.setSpacing(0)

        # ── 1. Left Navigation Sidebar ────────────────────────────
        self.sidebar = Sidebar(self)
        main_h.addWidget(self.sidebar)

        # ── 2. Right View Canvas ──────────────────────────────────
        right_v = QVBoxLayout()
        right_v.setContentsMargins(0, 0, 0, 0)
        right_v.setSpacing(0)

        # Top Action Bar
        self.topbar = TopBar(self)
        right_v.addWidget(self.topbar)

        # Content Stack
        self.stack = QStackedWidget()

        self.dashboard_tab = DashboardTab()
        self.campaigns_tab = CampaignsTab()
        self.proxy_tab = ProxyTab()
        self.keywords_tab = KeywordsTab()
        self.fingerprint_tab = FingerprintTab()
        self.workers_tab = WorkersTab()
        self.settings_tab = SettingsTab()

        self.stack.addWidget(self.dashboard_tab)      # 0
        self.stack.addWidget(self.campaigns_tab)      # 1
        self.stack.addWidget(self.proxy_tab)          # 2
        self.stack.addWidget(self.keywords_tab)       # 3
        self.stack.addWidget(self.fingerprint_tab)    # 4
        self.stack.addWidget(self.workers_tab)        # 5
        self.stack.addWidget(self.settings_tab)       # 6

        right_v.addWidget(self.stack)
        main_h.addLayout(right_v)

        # Subtle bottom status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.setStyleSheet("background-color: #0A0D14; color: #475569; font-size: 10px; border-top: 1px solid #161D2B;")
        self.status.showMessage("OrbitTraffic Core Engine Ready  |  RankBrain Pogo-Sticking Enabled  |  Fingerprint Level 10")

    def _wire_signals(self):
        self.sidebar.tab_changed.connect(self._on_nav_change)

        # TopBar quick controls
        self.topbar.start_requested.connect(self._on_global_start)
        self.topbar.stop_requested.connect(self._on_global_stop)

    def _on_nav_change(self, index: int):
        self.stack.setCurrentIndex(index)
        titles = [
            "Dashboard Radar",
            "Campaigns & Organic Flow Studio",
            "Proxy Fleet Radar",
            "Keyword Studio & SERP Architecture",
            "Fingerprint Lab & Anti-Detect Diagnostics",
            "Live Worker Matrix & Inspector",
            "Global Settings & Architecture",
        ]
        if 0 <= index < len(titles):
            self.topbar.set_title(titles[index])

    def _on_global_start(self):
        self.sidebar.select_tab(1)  # Switch to Campaigns
        self.stack.setCurrentIndex(1)
        self.campaigns_tab._start_campaign()
        self.topbar.set_running(True)

    def _on_global_stop(self):
        self.campaigns_tab._stop_campaign()
        self.topbar.set_running(False)

    def _start_system_monitors(self):
        self.telemetry_timer = QTimer()
        self.telemetry_timer.timeout.connect(self._refresh_telemetry)
        self.telemetry_timer.start(2000)

    def _refresh_telemetry(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            is_running = self.campaigns_tab._running
            self.sidebar.update_telemetry(cpu, ram, is_running)

            if is_running:
                self.topbar.set_running(True)
                elapsed = time.time() - (self.campaigns_tab._start_time or time.time())
                rate = self.campaigns_tab._total_visits / (elapsed / 60) if elapsed > 0 else 0
                self.topbar.update_throughput(rate)
            else:
                self.topbar.set_running(False)
        except Exception:
            pass

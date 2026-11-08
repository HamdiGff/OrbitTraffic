"""
OrbitTraffic — Main Application Window
Dark-themed PyQt6 GUI with tabbed interface.
"""
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QStatusBar, QFrame,
    QPushButton, QSystemTrayIcon, QMenu,
)
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette, QAction
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from gui.theme import apply_dark_theme
from gui.tabs.dashboard_tab import DashboardTab
from gui.tabs.campaigns_tab import CampaignsTab
from gui.tabs.proxy_tab import ProxyTab
from gui.tabs.keywords_tab import KeywordsTab
from gui.tabs.settings_tab import SettingsTab
from gui.tabs.logs_tab import LogsTab
from utils.logger import get_logger

logger = get_logger("gui.app")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OrbitTraffic v1.0 — Organic Traffic Platform")
        self.setMinimumSize(1280, 800)
        self.resize(1400, 900)

        apply_dark_theme(self)
        self._build_ui()
        self._setup_tray()
        self._setup_status_bar()
        self._start_stat_timer()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header bar
        header = self._make_header()
        layout.addWidget(header)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setObjectName("mainTabs")
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setDocumentMode(True)

        self.dashboard_tab = DashboardTab()
        self.campaigns_tab = CampaignsTab()
        self.proxy_tab = ProxyTab()
        self.keywords_tab = KeywordsTab()
        self.settings_tab = SettingsTab()
        self.logs_tab = LogsTab()

        self.tabs.addTab(self.dashboard_tab,  "📊  Dashboard")
        self.tabs.addTab(self.campaigns_tab,  "🚀  Campaigns")
        self.tabs.addTab(self.proxy_tab,      "🔌  Proxies")
        self.tabs.addTab(self.keywords_tab,   "🔑  Keywords")
        self.tabs.addTab(self.settings_tab,   "⚙️  Settings")
        self.tabs.addTab(self.logs_tab,       "📋  Live Logs")

        layout.addWidget(self.tabs)

    def _make_header(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("headerBar")
        frame.setFixedHeight(56)
        frame.setStyleSheet("""
            #headerBar {
                background: qlineargradient(
                    x1:0 y1:0, x2:1 y2:0,
                    stop:0 #0f0f1a, stop:0.5 #1a1a2e, stop:1 #0f0f1a
                );
                border-bottom: 2px solid #6c63ff;
            }
        """)

        h = QHBoxLayout(frame)
        h.setContentsMargins(20, 0, 20, 0)

        logo = QLabel("🚀 OrbitTraffic")
        logo.setStyleSheet("color: #6c63ff; font-size: 20px; font-weight: bold; letter-spacing: 2px;")
        h.addWidget(logo)

        tagline = QLabel("Organic Traffic Intelligence Platform")
        tagline.setStyleSheet("color: #888; font-size: 11px; margin-left: 10px;")
        h.addWidget(tagline)

        h.addStretch()

        # Live stats in header
        self.header_stats = QLabel("🟢 Ready")
        self.header_stats.setStyleSheet("color: #4ade80; font-size: 11px;")
        h.addWidget(self.header_stats)

        return frame

    def _setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("background: #0f0f1a; color: #666; font-size: 10px;")
        self.status_bar.showMessage("OrbitTraffic ready. Configure campaigns to begin.")

    def _setup_tray(self):
        self.tray = QSystemTrayIcon(self)
        tray_menu = QMenu()
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        quit_action = QAction("Quit OrbitTraffic", self)
        quit_action.triggered.connect(sys.exit)
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        self.tray.setContextMenu(tray_menu)

    def _start_stat_timer(self):
        self.stat_timer = QTimer()
        self.stat_timer.timeout.connect(self._update_stats)
        self.stat_timer.start(2000)  # Update every 2 seconds

    def _update_stats(self):
        try:
            stats = self.campaigns_tab.get_stats() if hasattr(self.campaigns_tab, "get_stats") else {}
            active = stats.get("active_sessions", 0)
            total = stats.get("total_visits", 0)
            if active > 0:
                self.header_stats.setText(f"🔵 {active} active sessions | ✅ {total} visits")
                self.header_stats.setStyleSheet("color: #60a5fa; font-size: 11px;")
            else:
                self.header_stats.setText("🟢 Ready")
                self.header_stats.setStyleSheet("color: #4ade80; font-size: 11px;")
        except Exception:
            pass

    def closeEvent(self, event):
        if self.tray.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()

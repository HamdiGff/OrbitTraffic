"""
Dashboard Tab — Real-time stats, charts, and overview.
"""
import random
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QScrollArea,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class StatCard(QFrame):
    """A single metric card for the dashboard."""
    def __init__(self, title: str, value: str, icon: str, color: str = "#6c63ff"):
        super().__init__()
        self.setObjectName("statCard")
        self.setFixedHeight(100)
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 22px;")
        top.addWidget(icon_lbl)
        top.addStretch()

        title_lbl = QLabel(title.upper())
        title_lbl.setObjectName("statLabel")
        title_lbl.setStyleSheet(f"color: #64748b; font-size: 10px; letter-spacing: 1px; font-weight: 600;")

        self.value_lbl = QLabel(value)
        self.value_lbl.setStyleSheet(f"color: {color}; font-size: 26px; font-weight: bold;")

        layout.addLayout(top)
        layout.addWidget(self.value_lbl)
        layout.addWidget(title_lbl)

    def set_value(self, value: str):
        self.value_lbl.setText(value)


class DashboardTab(QWidget):
    def __init__(self):
        super().__init__()
        self._total_visits = 0
        self._active_sessions = 0
        self._alive_proxies = 0
        self._keywords_active = 0
        self._build_ui()
        self._start_refresh()

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)

        # Title
        title = QLabel("📊 Dashboard Overview")
        title.setStyleSheet("color: #c4b5fd; font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Stat cards row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(14)

        self.card_visits = StatCard("Total Visits", "0", "✅", "#22c55e")
        self.card_sessions = StatCard("Active Sessions", "0", "🔵", "#60a5fa")
        self.card_proxies = StatCard("Live Proxies", "0", "🔌", "#a78bfa")
        self.card_keywords = StatCard("Active Keywords", "0", "🔑", "#f59e0b")
        self.card_success = StatCard("Success Rate", "—", "📈", "#6c63ff")
        self.card_avg_dwell = StatCard("Avg. Dwell Time", "—", "⏱️", "#ec4899")

        for card in [self.card_visits, self.card_sessions, self.card_proxies,
                     self.card_keywords, self.card_success, self.card_avg_dwell]:
            cards_layout.addWidget(card)

        layout.addLayout(cards_layout)

        # Recent activity section
        activity_title = QLabel("🕒 Recent Activity")
        activity_title.setStyleSheet("color: #94a3b8; font-size: 14px; font-weight: 600; margin-top: 10px;")
        layout.addWidget(activity_title)

        self.activity_log = QLabel("No activity yet. Start a campaign to see live results.")
        self.activity_log.setStyleSheet("""
            background: #12122a;
            border: 1px solid #1e1e3a;
            border-radius: 8px;
            padding: 20px;
            color: #64748b;
            font-size: 12px;
        """)
        self.activity_log.setWordWrap(True)
        self.activity_log.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.activity_log.setMinimumHeight(200)
        layout.addWidget(self.activity_log)

        # Tips section
        tips = QFrame()
        tips.setStyleSheet("""
            background: #12122a;
            border: 1px solid #1e3a1e;
            border-left: 3px solid #22c55e;
            border-radius: 6px;
            padding: 10px 16px;
        """)
        tips_layout = QVBoxLayout(tips)
        tips_layout.setContentsMargins(8, 8, 8, 8)
        tips_lbl = QLabel(
            "💡 <b>Tips:</b> Add residential proxies in the Proxies tab for best results. "
            "Use long-tail keywords for more natural traffic patterns. "
            "Start with low concurrency (3-5 sessions) and scale up gradually."
        )
        tips_lbl.setStyleSheet("color: #86efac; font-size: 11px;")
        tips_lbl.setWordWrap(True)
        tips_layout.addWidget(tips_lbl)
        layout.addWidget(tips)

        layout.addStretch()
        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _start_refresh(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self._refresh_stats)
        self.timer.start(3000)

    def _refresh_stats(self):
        self.card_visits.set_value(str(self._total_visits))
        self.card_sessions.set_value(str(self._active_sessions))
        self.card_proxies.set_value(str(self._alive_proxies))
        self.card_keywords.set_value(str(self._keywords_active))

    def update_stats(self, total_visits=None, active_sessions=None,
                     alive_proxies=None, keywords_active=None,
                     success_rate=None, avg_dwell=None):
        if total_visits is not None:
            self._total_visits = total_visits
        if active_sessions is not None:
            self._active_sessions = active_sessions
        if alive_proxies is not None:
            self._alive_proxies = alive_proxies
        if keywords_active is not None:
            self._keywords_active = keywords_active
        if success_rate is not None:
            self.card_success.set_value(f"{success_rate:.0f}%")
        if avg_dwell is not None:
            self.card_avg_dwell.set_value(f"{avg_dwell:.0f}s")

    def log_activity(self, message: str):
        current = self.activity_log.text()
        if current == "No activity yet. Start a campaign to see live results.":
            current = ""
        self.activity_log.setText(f"{message}\n{current}"[:3000])

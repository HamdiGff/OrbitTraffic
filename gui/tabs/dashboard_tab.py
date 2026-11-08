"""
OrbitTraffic — Redesigned Modern Dashboard Tab
Features:
- 4 High-Impact KPI Cards with trend badges and micro-metrics
- Real-Time Live Traffic Area Chart powered by pyqtgraph
- Channel Acquisition & Geolocation Breakdown Bars
- Live Session Activity Stream Table with country flags & anti-detect scores
"""
import random
import time
from collections import deque
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QScrollArea,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont
import pyqtgraph as pg


class ModernKpiCard(QFrame):
    def __init__(self, title: str, value: str, trend: str, subtext: str, icon: str, color: str = "#6366F1"):
        super().__init__()
        self.setProperty("class", "kpiCard")
        self.setFixedHeight(120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        # Header row
        header = QHBoxLayout()
        header.setSpacing(8)

        icon_box = QLabel(icon)
        icon_box.setStyleSheet(f"""
            background: {color}18;
            color: {color};
            border-radius: 6px;
            font-size: 16px;
            padding: 4px;
        """)
        header.addWidget(icon_box)

        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 700; letter-spacing: 0.8px;")
        header.addWidget(title_lbl)
        header.addStretch()

        self.trend_badge = QLabel(trend)
        self.trend_badge.setStyleSheet("""
            background: #064E3B;
            color: #34D399;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 4px;
        """)
        header.addWidget(self.trend_badge)
        layout.addLayout(header)

        # Value
        self.val_lbl = QLabel(value)
        self.val_lbl.setStyleSheet(f"color: #FFFFFF; font-size: 26px; font-weight: 800; letter-spacing: -0.5px;")
        layout.addWidget(self.val_lbl)

        # Subtext
        self.sub_lbl = QLabel(subtext)
        self.sub_lbl.setStyleSheet("color: #94A3B8; font-size: 11px;")
        layout.addWidget(self.sub_lbl)

    def set_value(self, val: str, trend: str = None):
        self.val_lbl.setText(val)
        if trend:
            self.trend_badge.setText(trend)


class DashboardTab(QWidget):
    def __init__(self):
        super().__init__()
        self._traffic_history = deque([random.randint(10, 45) for _ in range(30)], maxlen=30)
        self._total_visits = 0
        self._active_sessions = 0
        self._build_ui()
        self._start_timers()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(16)

        # Scroll area for clean display on any screen resolution
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # ── 1. Top KPI Row ────────────────────────────────────────
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(14)

        self.card_visits = ModernKpiCard(
            title="Total Organic Visits",
            value="14,290",
            trend="▲ +24.8%",
            subtext="Campaign: Active Google Search Boost",
            icon="🚀",
            color="#6366F1",
        )
        self.card_dwell = ModernKpiCard(
            title="Avg Session Dwell Time",
            value="3m 18s",
            trend="▲ +42% vs GA4",
            subtext="High-retention reading behavior",
            icon="⏱️",
            color="#10B981",
        )
        self.card_rankbrain = ModernKpiCard(
            title="RankBrain CTR Uplift",
            value="+16.4%",
            trend="● Pogo-Stick Active",
            subtext="Competitor dissatisfaction signal",
            icon="🧠",
            color="#F59E0B",
        )
        self.card_proxies = ModernKpiCard(
            title="Proxy Pool Health",
            value="99.4%",
            trend="142ms Avg Latency",
            subtext="Residential SOCKS5 / HTTP Fleet",
            icon="🌐",
            color="#38BDF8",
        )

        for card in [self.card_visits, self.card_dwell, self.card_rankbrain, self.card_proxies]:
            kpi_row.addWidget(card)

        layout.addLayout(kpi_row)

        # ── 2. Middle Grid: Live Chart + Acquisition Radar ───────
        grid = QHBoxLayout()
        grid.setSpacing(14)

        # Left: Live PyQtGraph Wave
        chart_card = QFrame()
        chart_card.setObjectName("surfaceCard")
        chart_card.setMinimumHeight(280)
        chart_v = QVBoxLayout(chart_card)
        chart_v.setContentsMargins(16, 14, 16, 14)
        chart_v.setSpacing(8)

        chart_header = QHBoxLayout()
        chart_title = QLabel("📈 REAL-TIME TRAFFIC THROUGHPUT")
        chart_title.setStyleSheet("color: #CBD5E1; font-size: 12px; font-weight: 700; letter-spacing: 0.5px;")
        chart_header.addWidget(chart_title)
        chart_header.addStretch()

        live_tag = QLabel("● LIVE (1s update)")
        live_tag.setStyleSheet("color: #10B981; font-size: 10px; font-weight: 700;")
        chart_header.addWidget(live_tag)
        chart_v.addLayout(chart_header)

        # PyQtGraph widget
        pg.setConfigOptions(antialias=True)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("#0E131E")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.15)
        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.hideAxis("left")
        self.plot_widget.hideAxis("bottom")

        # Neon line with gradient fill
        self.curve = self.plot_widget.plot(
            list(self._traffic_history),
            pen=pg.mkPen(color="#818CF8", width=2.5),
            fillLevel=0,
            brush=pg.mkBrush(99, 102, 241, 45),
        )
        chart_v.addWidget(self.plot_widget)
        grid.addWidget(chart_card, stretch=65)

        # Right: Acquisition Radar Card
        radar_card = QFrame()
        radar_card.setObjectName("surfaceCard")
        radar_card.setMinimumHeight(280)
        radar_v = QVBoxLayout(radar_card)
        radar_v.setContentsMargins(16, 14, 16, 14)
        radar_v.setSpacing(12)

        radar_title = QLabel("🎯 TRAFFIC SOURCE BREAKDOWN")
        radar_title.setStyleSheet("color: #CBD5E1; font-size: 12px; font-weight: 700; letter-spacing: 0.5px;")
        radar_v.addWidget(radar_title)

        sources = [
            ("Google Organic SERP", 68, "#6366F1"),
            ("Bing Organic Search", 16, "#38BDF8"),
            ("Direct / Type-In", 10, "#10B981"),
            ("Social Referrers (Reddit/X)", 6, "#F59E0B"),
        ]

        for name, pct, col in sources:
            row = QVBoxLayout()
            row.setSpacing(3)
            info_h = QHBoxLayout()
            n_lbl = QLabel(name)
            n_lbl.setStyleSheet("color: #94A3B8; font-size: 11px;")
            p_lbl = QLabel(f"{pct}%")
            p_lbl.setStyleSheet(f"color: {col}; font-size: 11px; font-weight: 700;")
            info_h.addWidget(n_lbl)
            info_h.addStretch()
            info_h.addWidget(p_lbl)

            bar = QProgressBar()
            bar.setFixedHeight(5)
            bar.setTextVisible(False)
            bar.setValue(pct)
            bar.setStyleSheet(f"""
                QProgressBar {{ background-color: #1A2234; border: none; border-radius: 2px; }}
                QProgressBar::chunk {{ background-color: {col}; border-radius: 2px; }}
            """)
            row.addLayout(info_h)
            row.addWidget(bar)
            radar_v.addLayout(row)

        radar_v.addStretch()
        grid.addWidget(radar_card, stretch=35)

        layout.addLayout(grid)

        # ── 3. Bottom Table: Live Session Activity Matrix ─────────
        matrix_card = QFrame()
        matrix_card.setObjectName("surfaceCard")
        matrix_v = QVBoxLayout(matrix_card)
        matrix_v.setContentsMargins(16, 14, 16, 14)
        matrix_v.setSpacing(10)

        matrix_header = QHBoxLayout()
        m_title = QLabel("🛰️ LIVE TELEMETRY & BEHAVIORAL STREAM")
        m_title.setStyleSheet("color: #CBD5E1; font-size: 12px; font-weight: 700; letter-spacing: 0.5px;")
        matrix_header.addWidget(m_title)
        matrix_header.addStretch()
        matrix_v.addLayout(matrix_header)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Time", "Worker", "Geo", "Proxy IP", "Keyword / URL", "Behavioral Action", "Stealth Score"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setMinimumHeight(240)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        matrix_v.addWidget(self.table)

        layout.addWidget(matrix_card)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _start_timers(self):
        self.chart_timer = QTimer()
        self.chart_timer.timeout.connect(self._update_chart)
        self.chart_timer.start(1000)

    def _update_chart(self):
        # Add new point to graph
        next_val = max(5, self._traffic_history[-1] + random.randint(-4, 5))
        self._traffic_history.append(next_val)
        self.curve.setData(list(self._traffic_history))

    def add_telemetry_event(self, worker_id: str, geo: str, ip: str, target: str, action: str, score: str = "99/100"):
        row = 0
        self.table.insertRow(row)

        ts = time.strftime("%H:%M:%S")

        def cell(text, color="#F8FAFC"):
            it = QTableWidgetItem(str(text))
            it.setForeground(QColor(color))
            it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            return it

        self.table.setItem(row, 0, cell(ts, "#64748B"))
        self.table.setItem(row, 1, cell(f"Worker #{worker_id}", "#818CF8"))
        self.table.setItem(row, 2, cell(geo))
        self.table.setItem(row, 3, cell(ip, "#94A3B8"))
        self.table.setItem(row, 4, cell(target[:40]))
        self.table.setItem(row, 5, cell(action, "#38BDF8"))
        self.table.setItem(row, 6, cell(score, "#10B981"))

        if self.table.rowCount() > 200:
            self.table.removeRow(200)

    def update_stats(self, total_visits=None, active_sessions=None, avg_dwell=None, health_score=None):
        if total_visits is not None:
            self.card_visits.set_value(f"{total_visits:,}")
        if active_sessions is not None:
            self._active_sessions = active_sessions
        if avg_dwell is not None:
            self.card_dwell.set_value(f"{avg_dwell:.0f}s")
        if health_score is not None:
            self.card_proxies.set_value(f"{health_score:.1f}%")

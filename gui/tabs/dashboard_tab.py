"""
OrbitTraffic — Redesigned Modern Dashboard Tab
Features high-contrast typography, JetBrains/Cascadia tabular figures,
and real-time PyQtGraph area visualizations.
"""
import random
import time
from collections import deque
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QScrollArea,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont
import pyqtgraph as pg
from gui.typography import FontSystem


class ModernKpiCard(QFrame):
    def __init__(self, title: str, value: str, trend: str, subtext: str, glyph: str, color: str = "#6366F1"):
        super().__init__()
        self.setProperty("class", "kpiCard")
        self.setFixedHeight(125)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(4)

        # Header row
        header = QHBoxLayout()
        header.setSpacing(8)

        glyph_box = QLabel(glyph)
        glyph_box.setFont(FontSystem.get_display_font(13))
        glyph_box.setStyleSheet(f"""
            background: {color}20;
            color: {color};
            border-radius: 5px;
            padding: 3px 6px;
        """)
        header.addWidget(glyph_box)

        title_lbl = QLabel(title.upper())
        title_lbl.setFont(FontSystem.get_badge_font(9))
        title_lbl.setStyleSheet("color: #64748B; letter-spacing: 1.2px;")
        header.addWidget(title_lbl)
        header.addStretch()

        self.trend_badge = QLabel(trend)
        self.trend_badge.setFont(FontSystem.get_badge_font(8))
        self.trend_badge.setStyleSheet("""
            background: rgba(16, 185, 129, 0.15);
            color: #34D399;
            padding: 2px 7px;
            border-radius: 4px;
            border: 1px solid rgba(16, 185, 129, 0.3);
        """)
        header.addWidget(self.trend_badge)
        layout.addLayout(header)

        # Numeric KPI Value
        self.val_lbl = QLabel(value)
        self.val_lbl.setFont(FontSystem.get_mono_font(26, QFont.Weight.Bold))
        self.val_lbl.setStyleSheet(f"color: #FFFFFF; letter-spacing: -0.5px;")
        layout.addWidget(self.val_lbl)

        # Subtext
        self.sub_lbl = QLabel(subtext)
        self.sub_lbl.setFont(FontSystem.get_badge_font(9))
        self.sub_lbl.setStyleSheet("color: #94A3B8;")
        layout.addWidget(self.sub_lbl)

    def set_value(self, val: str, trend: str = None):
        self.val_lbl.setText(val)
        if trend:
            self.trend_badge.setText(trend)


class DashboardTab(QWidget):
    def __init__(self):
        super().__init__()
        self._traffic_history = deque([random.randint(15, 50) for _ in range(35)], maxlen=35)
        self._total_visits = 0
        self._build_ui()
        self._start_timers()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(22, 18, 22, 18)
        main_layout.setSpacing(16)

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
            glyph="⬡",
            color="#6366F1",
        )
        self.card_dwell = ModernKpiCard(
            title="Avg Retention Dwell",
            value="3m 18s",
            trend="▲ +42% vs GA4",
            subtext="High-engagement reading behavior",
            glyph="⏱",
            color="#10B981",
        )
        self.card_rankbrain = ModernKpiCard(
            title="RankBrain CTR Uplift",
            value="+16.4%",
            trend="● Pogo-Stick Active",
            subtext="Competitor dissatisfaction signal",
            glyph="⚡",
            color="#F59E0B",
        )
        self.card_proxies = ModernKpiCard(
            title="Proxy Fleet Health",
            value="99.4%",
            trend="142ms Avg Latency",
            subtext="Residential SOCKS5 / HTTP Fleet",
            glyph="◈",
            color="#38BDF8",
        )

        for card in [self.card_visits, self.card_dwell, self.card_rankbrain, self.card_proxies]:
            kpi_row.addWidget(card)

        layout.addLayout(kpi_row)

        # ── 2. Middle Grid: Live Wave + Traffic Radar ─────────────
        grid = QHBoxLayout()
        grid.setSpacing(14)

        # Left: Live Wave Chart
        chart_card = QFrame()
        chart_card.setObjectName("surfaceCard")
        chart_card.setMinimumHeight(280)
        chart_v = QVBoxLayout(chart_card)
        chart_v.setContentsMargins(18, 16, 18, 16)
        chart_v.setSpacing(10)

        chart_header = QHBoxLayout()
        chart_title = QLabel("REAL-TIME THROUGHPUT MONITOR")
        chart_title.setFont(FontSystem.get_badge_font(9))
        chart_title.setStyleSheet("color: #94A3B8; letter-spacing: 1.5px;")
        chart_header.addWidget(chart_title)
        chart_header.addStretch()

        live_tag = QLabel("● 1000ms TELEMETRY")
        live_tag.setFont(FontSystem.get_mono_font(9))
        live_tag.setStyleSheet("color: #10B981; font-weight: 700;")
        chart_header.addWidget(live_tag)
        chart_v.addLayout(chart_header)

        # PyQtGraph — Polished with smooth curve and no clunky buttons
        pg.setConfigOptions(antialias=True)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("#0A0D14")
        self.plot_widget.plotItem.hideButtons()
        self.plot_widget.plotItem.setMouseEnabled(x=False, y=False)
        self.plot_widget.plotItem.showGrid(x=False, y=True, alpha=0.06)
        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.hideAxis("left")
        self.plot_widget.hideAxis("bottom")

        self.curve = self.plot_widget.plot(
            list(self._traffic_history),
            pen=pg.mkPen(color="#818CF8", width=2.8),
            fillLevel=0,
            brush=pg.mkBrush(99, 102, 241, 30),
        )
        chart_v.addWidget(self.plot_widget)
        grid.addWidget(chart_card, stretch=65)

        # Right: Acquisition Radar Card
        radar_card = QFrame()
        radar_card.setObjectName("surfaceCard")
        radar_card.setMinimumHeight(280)
        radar_v = QVBoxLayout(radar_card)
        radar_v.setContentsMargins(18, 16, 18, 16)
        radar_v.setSpacing(12)

        radar_title = QLabel("ACQUISITION CHANNELS")
        radar_title.setFont(FontSystem.get_badge_font(9))
        radar_title.setStyleSheet("color: #94A3B8; letter-spacing: 1.5px;")
        radar_v.addWidget(radar_title)

        sources = [
            ("Google Organic SERP", 68, "#6366F1"),
            ("Bing Organic Search", 16, "#38BDF8"),
            ("Direct / Type-In", 10, "#10B981"),
            ("Social Referrers (Reddit/X)", 6, "#F59E0B"),
        ]

        for name, pct, col in sources:
            row = QVBoxLayout()
            row.setSpacing(4)
            info_h = QHBoxLayout()
            n_lbl = QLabel(name)
            n_lbl.setFont(FontSystem.get_badge_font(9))
            n_lbl.setStyleSheet("color: #94A3B8;")
            p_lbl = QLabel(f"{pct}%")
            p_lbl.setFont(FontSystem.get_mono_font(10, QFont.Weight.Bold))
            p_lbl.setStyleSheet(f"color: {col};")
            info_h.addWidget(n_lbl)
            info_h.addStretch()
            info_h.addWidget(p_lbl)

            bar = QProgressBar()
            bar.setFixedHeight(5)
            bar.setTextVisible(False)
            bar.setValue(pct)
            bar.setStyleSheet(f"""
                QProgressBar {{ background-color: rgba(255, 255, 255, 0.05); border: none; border-radius: 2px; }}
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
        matrix_v.setContentsMargins(18, 16, 18, 16)
        matrix_v.setSpacing(10)

        matrix_header = QHBoxLayout()
        m_title = QLabel("LIVE BEHAVIORAL TELEMETRY STREAM")
        m_title.setFont(FontSystem.get_badge_font(9))
        m_title.setStyleSheet("color: #94A3B8; letter-spacing: 1.5px;")
        matrix_header.addWidget(m_title)
        matrix_header.addStretch()
        matrix_v.addLayout(matrix_header)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Timestamp", "Worker Slot", "Geo Region", "Proxy IP", "Target Query / URL", "Behavioral Step", "Stealth"
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
        import numpy as np
        next_val = max(12, min(85, self._traffic_history[-1] + random.randint(-4, 5)))
        self._traffic_history.append(next_val)

        # Smooth spline interpolation across data points
        y_raw = np.array(self._traffic_history, dtype=float)
        x_raw = np.arange(len(y_raw))

        # Generate smooth curve
        try:
            from scipy.interpolate import make_interp_spline
            spl = make_interp_spline(x_raw, y_raw, k=2)
            x_smooth = np.linspace(0, len(y_raw) - 1, len(y_raw) * 3)
            y_smooth = np.maximum(5, spl(x_smooth))
            self.curve.setData(x_smooth, y_smooth)
        except Exception:
            self.curve.setData(list(self._traffic_history))

    def add_telemetry_event(self, worker_id: str, geo: str, ip: str, target: str, action: str, score: str = "99/100"):
        row = 0
        self.table.insertRow(row)
        ts = time.strftime("%H:%M:%S")

        def cell(text, color="#F8FAFC", is_mono=False):
            it = QTableWidgetItem(str(text))
            it.setForeground(QColor(color))
            it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if is_mono:
                it.setFont(FontSystem.get_mono_font(10))
            else:
                it.setFont(FontSystem.get_badge_font(9))
            return it

        self.table.setItem(row, 0, cell(ts, "#64748B", is_mono=True))
        self.table.setItem(row, 1, cell(f"Worker #{worker_id}", "#818CF8"))
        self.table.setItem(row, 2, cell(geo))
        self.table.setItem(row, 3, cell(ip, "#94A3B8", is_mono=True))
        self.table.setItem(row, 4, cell(target[:40]))
        self.table.setItem(row, 5, cell(action, "#38BDF8"))
        self.table.setItem(row, 6, cell(score, "#10B981", is_mono=True))

        if self.table.rowCount() > 200:
            self.table.removeRow(200)

    def update_stats(self, total_visits=None, avg_dwell=None, health_score=None):
        if total_visits is not None:
            self.card_visits.set_value(f"{total_visits:,}")
        if avg_dwell is not None:
            self.card_dwell.set_value(f"{avg_dwell:.0f}s")
        if health_score is not None:
            self.card_proxies.set_value(f"{health_score:.1f}%")

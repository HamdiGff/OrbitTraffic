"""
OrbitTraffic — Campaigns & Organic Flow Studio
Configures and launches sophisticated multi-stage organic campaigns:
- Pogo-Sticking RankBrain Boost
- Multi-Hop Internal Site Exploration (1-4 pages)
- Persona & Cookie Pre-warming
- Search Engine Distribution & Long-Tail Variations
"""
import asyncio
import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QSpinBox,
    QComboBox, QCheckBox, QProgressBar, QHeaderView,
    QFrame, QSplitter, QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
import qasync

from browser.controller import BrowserController
from traffic_keyword.engine import KeywordEngine, Keyword
from utils.logger import get_logger

logger = get_logger("gui.campaigns")


class CampaignsTab(QWidget):
    def __init__(self):
        super().__init__()
        self._running = False
        self._total_visits = 0
        self._success_count = 0
        self._dwell_times = []
        self._pogo_count = 0
        self._start_time = None
        self._campaign_task = None
        self.browser = None
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(14)

        header_v = QVBoxLayout()
        title = QLabel("🚀 Campaigns & Organic Journey Studio")
        title.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: 700;")
        subtitle = QLabel("Configure organic search flows, multi-page deep sessions, and RankBrain boosts.")
        subtitle.setStyleSheet("color: #94A3B8; font-size: 12px;")
        header_v.addWidget(title)
        header_v.addWidget(subtitle)
        main_layout.addLayout(header_v)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── Left Panel: Campaign Architect ────────────────────────
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 10, 0)
        left_layout.setSpacing(12)

        # Presets
        preset_group = QGroupBox("Campaign Architecture Preset")
        preset_v = QVBoxLayout(preset_group)
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "⚡ E-Commerce RankBrain Booster (Pogo-Stick + 3 Hops)",
            "📖 Content & Blog High-Retention (Deep Reading + 2 Hops)",
            "🛡️ Stealth Brand Impression (Gradual Curve + Cookie Farm)",
            "⚙️ Custom Tailored Flow",
        ])
        preset_v.addWidget(self.preset_combo)
        left_layout.addWidget(preset_group)

        # Execution Parameters
        config_group = QGroupBox("Execution Parameters")
        config_v = QVBoxLayout(config_group)
        config_v.setSpacing(8)

        # Visits & Concurrency
        h1 = QHBoxLayout()
        v_box = QVBoxLayout()
        v_box.addWidget(QLabel("Target Visits:"))
        self.visits_spin = QSpinBox()
        self.visits_spin.setRange(1, 1000000)
        self.visits_spin.setValue(250)
        self.visits_spin.setSingleStep(25)
        v_box.addWidget(self.visits_spin)
        h1.addLayout(v_box)

        c_box = QVBoxLayout()
        c_box.addWidget(QLabel("Concurrent Workers:"))
        self.concurrency_spin = QSpinBox()
        self.concurrency_spin.setRange(1, 20)
        self.concurrency_spin.setValue(3)
        c_box.addWidget(self.concurrency_spin)
        h1.addLayout(c_box)
        config_v.addLayout(h1)

        # Dwell Range
        h2 = QHBoxLayout()
        d1 = QVBoxLayout()
        d1.addWidget(QLabel("Min Dwell (sec):"))
        self.min_dwell = QSpinBox()
        self.min_dwell.setRange(10, 600)
        self.min_dwell.setValue(35)
        d1.addWidget(self.min_dwell)
        h2.addLayout(d1)

        d2 = QVBoxLayout()
        d2.addWidget(QLabel("Max Dwell (sec):"))
        self.max_dwell = QSpinBox()
        self.max_dwell.setRange(10, 600)
        self.max_dwell.setValue(180)
        d2.addWidget(self.max_dwell)
        h2.addLayout(d2)
        config_v.addLayout(h2)

        left_layout.addWidget(config_group)

        # Innovative Algorithms
        algo_group = QGroupBox("Advanced Algorithms")
        algo_v = QVBoxLayout(algo_group)
        algo_v.setSpacing(6)

        self.chk_pogo = QCheckBox("🔥 RankBrain Pogo-Sticking (Bounce competitor -> Land target)")
        self.chk_pogo.setChecked(True)
        algo_v.addWidget(self.chk_pogo)

        self.chk_journey = QCheckBox("🧭 Multi-Hop Journey (Navigate 2-3 internal pages)")
        self.chk_journey.setChecked(True)
        algo_v.addWidget(self.chk_journey)

        self.chk_farm = QCheckBox("🍪 Cookie Farm Pre-warming (Acquire authentic 3rd-party history)")
        self.chk_farm.setChecked(True)
        algo_v.addWidget(self.chk_farm)

        self.chk_mouse = QCheckBox("🖱️ AI Bezier Curves (Micro-tremors & saccadic overshoot)")
        self.chk_mouse.setChecked(True)
        algo_v.addWidget(self.chk_mouse)

        left_layout.addWidget(algo_group)

        # Action Buttons
        btn_row = QHBoxLayout()
        self.btn_start = QPushButton("▶ Launch Campaign")
        self.btn_start.setObjectName("primaryActionBtn")
        self.btn_start.clicked.connect(self._start_campaign)

        self.btn_stop = QPushButton("⏹ Stop")
        self.btn_stop.setObjectName("dangerBtn")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._stop_campaign)

        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_stop)
        left_layout.addLayout(btn_row)
        left_layout.addStretch()

        # ── Right Panel: Real-Time Telemetry ──────────────────────
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setFormat("0 / 0 visits (0%)")
        right_layout.addWidget(self.progress)

        # Metric Tiles
        metric_h = QHBoxLayout()
        metric_h.setSpacing(10)

        for attr, title, color in [
            ("lbl_success", "✅ Completed", "#10B981"),
            ("lbl_dwell_avg", "⏱️ Avg Retention", "#38BDF8"),
            ("lbl_pogo_metric", "🔥 Pogo-Sticks", "#F59E0B"),
            ("lbl_rate", "⚡ Rate/Min", "#818CF8"),
        ]:
            card = QFrame()
            card.setObjectName("surfaceCard")
            card.setFixedHeight(65)
            c_l = QVBoxLayout(card)
            c_l.setContentsMargins(10, 8, 10, 8)
            c_l.setSpacing(2)

            v = QLabel("—")
            v.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: 800;")
            t = QLabel(title)
            t.setStyleSheet("color: #64748B; font-size: 10px; font-weight: 700;")
            c_l.addWidget(v)
            c_l.addWidget(t)
            setattr(self, attr, v)
            metric_h.addWidget(card)

        right_layout.addLayout(metric_h)

        # Live Execution Log
        right_layout.addWidget(QLabel("CAMPAIGN EXECUTION LOG"))
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(5)
        self.log_table.setHorizontalHeaderLabels(["Timestamp", "Target / Keyword", "Flow Used", "Dwell Time", "Status"])
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.log_table.setAlternatingRowColors(True)
        right_layout.addWidget(self.log_table)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([380, 820])
        main_layout.addWidget(splitter)

    def _start_campaign(self):
        # Fetch keywords from parent
        app = self.window()
        keywords = app.keywords_tab.get_keywords() if hasattr(app, "keywords_tab") else []

        if not keywords:
            # Create a sample keyword if none exists
            keywords = [Keyword(text="best organic traffic platform", target_url="https://example.com")]

        proxy_pool = app.proxy_tab.pool if hasattr(app, "proxy_tab") else None

        self._running = True
        self._start_time = time.time()
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        total_visits = self.visits_spin.value()
        concurrency = self.concurrency_spin.value()
        self.progress.setMaximum(total_visits)

        @qasync.asyncSlot()
        async def run():
            self.browser = BrowserController(headless=True)
            await self.browser.init()
            engine = KeywordEngine(self.browser, proxy_pool=proxy_pool)

            def on_progress(res: dict):
                self._total_visits += 1
                if res.get("success"):
                    self._success_count += 1
                if res.get("pogo_used"):
                    self._pogo_count += 1
                dwell = res.get("dwell_seconds", 0)
                if dwell:
                    self._dwell_times.append(dwell)

                self._add_row(res)
                self.progress.setValue(self._total_visits)
                pct = int(self._total_visits / total_visits * 100)
                self.progress.setFormat(f"{self._total_visits} / {total_visits} visits ({pct}%)")
                self._update_metrics()

                # Notify dashboard
                if hasattr(app, "dashboard_tab"):
                    app.dashboard_tab.add_telemetry_event(
                        worker_id="1",
                        geo="🇺🇸 US",
                        ip=res.get("proxy_ip", "Direct"),
                        target=res.get("target", "Target"),
                        action="Pogo-Stick Dwell Completed" if res.get("pogo_used") else "Organic Search Dwell",
                    )
                    app.dashboard_tab.update_stats(
                        total_visits=self._total_visits,
                        avg_dwell=sum(self._dwell_times) / max(1, len(self._dwell_times)),
                    )

            def on_action(worker_id, action_str, kw_str):
                if hasattr(app, "workers_tab"):
                    app.workers_tab.update_worker_state(worker_id, kw_str, action_str)

            try:
                await engine.run_campaign(
                    keywords=keywords,
                    total_visits=total_visits,
                    concurrency=concurrency,
                    on_progress=on_progress,
                    on_action=on_action,
                )
            finally:
                if self.browser:
                    await self.browser.close()
                self._running = False
                self.btn_start.setEnabled(True)
                self.btn_stop.setEnabled(False)

        self._campaign_task = asyncio.ensure_future(run())

    def _stop_campaign(self):
        if self._campaign_task:
            self._campaign_task.cancel()
        self._running = False
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)

    def _add_row(self, res: dict):
        row = 0
        self.log_table.insertRow(row)
        ts = time.strftime("%H:%M:%S")

        def cell(text, color="#F8FAFC"):
            it = QTableWidgetItem(str(text))
            it.setForeground(QColor(color))
            it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            return it

        self.log_table.setItem(row, 0, cell(ts, "#64748B"))
        self.log_table.setItem(row, 1, cell(res.get("keyword") or res.get("target")[:40]))
        flow = "🔥 Pogo-Stick + Hop" if res.get("pogo_used") else "🎯 SERP Search"
        self.log_table.setItem(row, 2, cell(flow, "#F59E0B" if res.get("pogo_used") else "#818CF8"))
        self.log_table.setItem(row, 3, cell(f"{res.get('dwell_seconds', 0):.0f}s", "#38BDF8"))
        ok = res.get("success", False)
        self.log_table.setItem(row, 4, cell("SUCCESS" if ok else "FAILED", "#10B981" if ok else "#EF4444"))

        if self.log_table.rowCount() > 200:
            self.log_table.removeRow(200)

    def _update_metrics(self):
        self.lbl_success.setText(str(self._success_count))
        self.lbl_pogo_metric.setText(str(self._pogo_count))
        avg_dwell = sum(self._dwell_times) / len(self._dwell_times) if self._dwell_times else 0
        self.lbl_dwell_avg.setText(f"{avg_dwell:.0f}s" if avg_dwell else "—")
        if self._start_time:
            elapsed = time.time() - self._start_time
            rate = self._total_visits / (elapsed / 60) if elapsed > 0 else 0
            self.lbl_rate.setText(f"{rate:.1f}")

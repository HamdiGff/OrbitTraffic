"""
OrbitTraffic — Redesigned Campaigns & Organic Flow Studio
Replaces primitive checkboxes with luxury FeatureToggleCards and iOS-style switches.
Includes Circadian Dayparting, Mobile Device Matrix, and Live Report Export.
"""
import asyncio
import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QSpinBox,
    QComboBox, QProgressBar, QHeaderView,
    QFrame, QSplitter, QFileDialog, QMessageBox, QScrollArea,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont
import qasync

from browser.controller import BrowserController
from traffic_keyword.engine import KeywordEngine, Keyword
from gui.components.toggle_switch import FeatureToggleCard
from gui.typography import FontSystem
from analytics.report_generator import export_client_csv_report
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
        self._completed_sessions = []
        self.browser = None
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(22, 18, 22, 18)
        main_layout.setSpacing(14)

        # Header with Export action
        top_h = QHBoxLayout()
        header_v = QVBoxLayout()
        title = QLabel("CAMPAIGN ARCHITECT & ORGANIC FLOW")
        title.setFont(FontSystem.get_display_font(14))
        title.setStyleSheet("color: #FFFFFF; font-weight: 700; letter-spacing: 0.5px;")
        subtitle = QLabel("Configure Pogo-Sticking curves, multi-hop internal page sessions, and mobile emulation.")
        subtitle.setFont(FontSystem.get_badge_font(9))
        subtitle.setStyleSheet("color: #64748B;")
        header_v.addWidget(title)
        header_v.addWidget(subtitle)
        top_h.addLayout(header_v)
        top_h.addStretch()

        self.btn_export_audit = QPushButton("💾 Export Client Report")
        self.btn_export_audit.setObjectName("secondaryBtn")
        self.btn_export_audit.setFont(FontSystem.get_badge_font(9))
        self.btn_export_audit.clicked.connect(self._export_report)
        top_h.addWidget(self.btn_export_audit)
        main_layout.addLayout(top_h)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── Left: Controls & Executive Feature Toggles ───────────
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QFrame.Shape.NoFrame)

        left_content = QWidget()
        left_layout = QVBoxLayout(left_content)
        left_layout.setContentsMargins(0, 0, 10, 0)
        left_layout.setSpacing(12)

        # Presets
        preset_group = QGroupBox("CAMPAIGN BLUEPRINTS")
        preset_v = QVBoxLayout(preset_group)
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "E-Commerce RankBrain Booster (Pogo-Stick + 3 Internal Hops)",
            "High-Retention Publishing (Circadian Dayparting + Deep Reading)",
            "Mobile Search Impression (60% Mobile Safari / Android)",
            "Stealth Persona Farm (Cookie Pre-Warming + Long Dwell)",
        ])
        preset_v.addWidget(self.preset_combo)
        left_layout.addWidget(preset_group)

        # Numerical Limits
        limits_group = QGroupBox("VOLUME & CONCURRENCY")
        limits_v = QVBoxLayout(limits_group)
        limits_v.setSpacing(8)

        h1 = QHBoxLayout()
        v_box = QVBoxLayout()
        v_box.addWidget(QLabel("Target Impressions / Visits:"))
        self.visits_spin = QSpinBox()
        self.visits_spin.setFont(FontSystem.get_mono_font(11))
        self.visits_spin.setRange(1, 1000000)
        self.visits_spin.setValue(250)
        self.visits_spin.setSingleStep(25)
        v_box.addWidget(self.visits_spin)
        h1.addLayout(v_box)

        c_box = QVBoxLayout()
        c_box.addWidget(QLabel("Concurrent Browser Slots:"))
        self.concurrency_spin = QSpinBox()
        self.concurrency_spin.setFont(FontSystem.get_mono_font(11))
        self.concurrency_spin.setRange(1, 24)
        self.concurrency_spin.setValue(3)
        c_box.addWidget(self.concurrency_spin)
        h1.addLayout(c_box)
        limits_v.addLayout(h1)

        # Dwell Range
        h2 = QHBoxLayout()
        d1 = QVBoxLayout()
        d1.addWidget(QLabel("Min Dwell (sec):"))
        self.min_dwell = QSpinBox()
        self.min_dwell.setFont(FontSystem.get_mono_font(11))
        self.min_dwell.setRange(10, 600)
        self.min_dwell.setValue(35)
        d1.addWidget(self.min_dwell)
        h2.addLayout(d1)

        d2 = QVBoxLayout()
        d2.addWidget(QLabel("Max Dwell (sec):"))
        self.max_dwell = QSpinBox()
        self.max_dwell.setFont(FontSystem.get_mono_font(11))
        self.max_dwell.setRange(10, 600)
        self.max_dwell.setValue(180)
        d2.addWidget(self.max_dwell)
        h2.addLayout(d2)
        limits_v.addLayout(h2)

        left_layout.addWidget(limits_group)

        # Executive Feature Cards (Replaces ugly checkboxes!)
        feature_header = QLabel("BEHAVIORAL & ALGORITHMIC ENGINES")
        feature_header.setFont(FontSystem.get_badge_font(8))
        feature_header.setStyleSheet("color: #64748B; letter-spacing: 1px; margin-top: 4px;")
        left_layout.addWidget(feature_header)

        self.card_pogo = FeatureToggleCard(
            icon_symbol="⚡",
            title="RankBrain Pogo-Sticking",
            description="Bounces competitor results to trigger search engine satisfaction signal",
            checked=True,
            accent_color="#F59E0B",
        )
        left_layout.addWidget(self.card_pogo)

        self.card_journey = FeatureToggleCard(
            icon_symbol="🧭",
            title="Multi-Hop Organic Journey",
            description="Explores 2-4 internal pages, eliminating high bounce rates in GA4",
            checked=True,
            accent_color="#6366F1",
        )
        left_layout.addWidget(self.card_journey)

        self.card_dayparting = FeatureToggleCard(
            icon_symbol="⏱",
            title="Circadian Dayparting Curve",
            description="Shapes 24h traffic to mirror human morning rushes and sleep lulls",
            checked=True,
            accent_color="#10B981",
        )
        left_layout.addWidget(self.card_dayparting)

        self.card_mobile = FeatureToggleCard(
            icon_symbol="📱",
            title="Mobile Device Matrix (60%)",
            description="Emulates iPhone & Android touch viewports with real TouchEvent APIs",
            checked=True,
            accent_color="#38BDF8",
        )
        left_layout.addWidget(self.card_mobile)

        self.card_farm = FeatureToggleCard(
            icon_symbol="◈",
            title="Cookie Pre-Warming Farm",
            description="Acquires genuine 3rd-party history on Wikipedia/BBC before landing",
            checked=True,
            accent_color="#A855F7",
        )
        left_layout.addWidget(self.card_farm)

        # Action Buttons
        btn_row = QHBoxLayout()
        self.btn_start = QPushButton("▶ Launch Campaign")
        self.btn_start.setObjectName("primaryActionBtn")
        self.btn_start.setFont(FontSystem.get_badge_font(9))
        self.btn_start.clicked.connect(self._start_campaign)

        self.btn_stop = QPushButton("⏹ Terminate")
        self.btn_stop.setObjectName("dangerBtn")
        self.btn_stop.setFont(FontSystem.get_badge_font(9))
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._stop_campaign)

        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_stop)
        left_layout.addLayout(btn_row)
        left_layout.addStretch()

        left_scroll.setWidget(left_content)

        # ── Right: Real-Time Execution Telemetry ─────────────────
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # Progress
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setFormat("0 / 0 visits (0%)")
        right_layout.addWidget(self.progress)

        # Metric Tiles
        metric_h = QHBoxLayout()
        metric_h.setSpacing(10)

        for attr, title, color in [
            ("lbl_success", "COMPLETED", "#10B981"),
            ("lbl_dwell_avg", "AVG RETENTION", "#38BDF8"),
            ("lbl_pogo_metric", "POGO BOUNCES", "#F59E0B"),
            ("lbl_rate", "THROUGHPUT", "#818CF8"),
        ]:
            card = QFrame()
            card.setObjectName("surfaceCard")
            card.setFixedHeight(68)
            c_l = QVBoxLayout(card)
            c_l.setContentsMargins(12, 8, 12, 8)
            c_l.setSpacing(1)

            v = QLabel("—")
            v.setFont(FontSystem.get_mono_font(18, QFont.Weight.Bold))
            v.setStyleSheet(f"color: {color};")
            t = QLabel(title)
            t.setFont(FontSystem.get_badge_font(8))
            t.setStyleSheet("color: #64748B; letter-spacing: 1px;")
            c_l.addWidget(v)
            c_l.addWidget(t)
            setattr(self, attr, v)
            metric_h.addWidget(card)

        right_layout.addLayout(metric_h)

        # Live Execution Log
        right_layout.addWidget(QLabel("REAL-TIME CAMPAIGN AUDIT LOG"))
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(5)
        self.log_table.setHorizontalHeaderLabels(["Timestamp", "Target / Keyword", "Flow Used", "Dwell Time", "Status"])
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.log_table.setAlternatingRowColors(True)
        right_layout.addWidget(self.log_table)

        splitter.addWidget(left_scroll)
        splitter.addWidget(right)
        splitter.setSizes([420, 800])
        main_layout.addWidget(splitter)

    def _start_campaign(self):
        app = self.window()
        keywords = app.keywords_tab.get_keywords() if hasattr(app, "keywords_tab") else []

        if not keywords:
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
                self._completed_sessions.append(res)
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

                if hasattr(app, "dashboard_tab"):
                    app.dashboard_tab.add_telemetry_event(
                        worker_id="1",
                        geo="US",
                        ip=res.get("proxy_ip", "Direct"),
                        target=res.get("target", "Target"),
                        action="Pogo-Stick Completed" if res.get("pogo_used") else "Organic Search Dwell",
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

        def cell(text, color="#F8FAFC", is_mono=False):
            it = QTableWidgetItem(str(text))
            it.setForeground(QColor(color))
            it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if is_mono:
                it.setFont(FontSystem.get_mono_font(10))
            else:
                it.setFont(FontSystem.get_badge_font(9))
            return it

        self.log_table.setItem(row, 0, cell(ts, "#64748B", is_mono=True))
        self.log_table.setItem(row, 1, cell(res.get("keyword") or res.get("target")[:40]))
        flow = "Pogo-Stick + Hop" if res.get("pogo_used") else "SERP Search"
        self.log_table.setItem(row, 2, cell(flow, "#F59E0B" if res.get("pogo_used") else "#818CF8"))
        self.log_table.setItem(row, 3, cell(f"{res.get('dwell_seconds', 0):.0f}s", "#38BDF8", is_mono=True))
        ok = res.get("success", False)
        self.log_table.setItem(row, 4, cell("VERIFIED" if ok else "FAILED", "#10B981" if ok else "#EF4444"))

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
            self.lbl_rate.setText(f"{rate:.1f}/m")

    def _export_report(self):
        if not self._completed_sessions:
            QMessageBox.information(self, "No Data", "Run a campaign first to generate audit records.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Audit Report", "orbittraffic_audit.csv", "CSV Files (*.csv)")
        if path:
            export_client_csv_report(self._completed_sessions, path)
            QMessageBox.information(self, "Report Exported", f"Successfully saved to {path}")

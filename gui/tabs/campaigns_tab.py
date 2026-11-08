"""
Campaigns Tab — Create, run, monitor traffic campaigns.
"""
import asyncio
import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QSpinBox,
    QComboBox, QCheckBox, QProgressBar, QHeaderView,
    QFrame, QSplitter, QTextEdit,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
import qasync

from browser.controller import BrowserController
from keyword.engine import KeywordEngine
from utils.logger import get_logger

logger = get_logger("gui.campaigns")


class CampaignsTab(QWidget):
    def __init__(self):
        super().__init__()
        self._running = False
        self._total_visits = 0
        self._active_sessions = 0
        self._success_count = 0
        self._dwell_times = []
        self._start_time = None
        self._campaign_task = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        title = QLabel("🚀 Campaign Manager")
        title.setStyleSheet("color: #c4b5fd; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── Left: Campaign Config ───────────────────────
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 10, 0)
        left_layout.setSpacing(12)

        # Campaign settings
        config_group = QGroupBox("Campaign Settings")
        config_v = QVBoxLayout(config_group)
        config_v.setSpacing(10)

        config_v.addWidget(QLabel("Total Visits:"))
        self.visits_spin = QSpinBox()
        self.visits_spin.setRange(1, 100000)
        self.visits_spin.setValue(100)
        self.visits_spin.setSingleStep(10)
        config_v.addWidget(self.visits_spin)

        config_v.addWidget(QLabel("Max Concurrent Sessions:"))
        self.concurrency_spin = QSpinBox()
        self.concurrency_spin.setRange(1, 50)
        self.concurrency_spin.setValue(3)
        config_v.addWidget(self.concurrency_spin)

        config_v.addWidget(QLabel("Browser Mode:"))
        self.headless_combo = QComboBox()
        self.headless_combo.addItems(["Headless (Recommended)", "Visible (Debug)"])
        config_v.addWidget(self.headless_combo)

        config_v.addWidget(QLabel("Browser Type:"))
        self.browser_type_combo = QComboBox()
        self.browser_type_combo.addItems(["chromium", "firefox", "webkit"])
        config_v.addWidget(self.browser_type_combo)

        # Behavior options
        behavior_group = QGroupBox("Behavior Settings")
        behavior_v = QVBoxLayout(behavior_group)
        self.chk_scroll = QCheckBox("Simulate Reading & Scroll")
        self.chk_scroll.setChecked(True)
        self.chk_mouse = QCheckBox("Human Mouse Movement")
        self.chk_mouse.setChecked(True)
        self.chk_fingerprint = QCheckBox("Fingerprint Spoofing")
        self.chk_fingerprint.setChecked(True)
        self.chk_cookies = QCheckBox("Cookie Aging & Seeding")
        self.chk_cookies.setChecked(True)
        self.chk_referrer = QCheckBox("Referrer Chain Simulation")
        self.chk_referrer.setChecked(True)
        for chk in [self.chk_scroll, self.chk_mouse, self.chk_fingerprint,
                    self.chk_cookies, self.chk_referrer]:
            behavior_v.addWidget(chk)

        # Min/max dwell
        dwell_row = QHBoxLayout()
        dwell_row.addWidget(QLabel("Dwell (sec):"))
        self.min_dwell = QSpinBox()
        self.min_dwell.setRange(5, 600)
        self.min_dwell.setValue(20)
        self.max_dwell = QSpinBox()
        self.max_dwell.setRange(5, 600)
        self.max_dwell.setValue(180)
        dwell_row.addWidget(self.min_dwell)
        dwell_row.addWidget(QLabel("–"))
        dwell_row.addWidget(self.max_dwell)
        behavior_v.addLayout(dwell_row)

        # Action buttons
        btn_row = QHBoxLayout()
        self.btn_start = QPushButton("▶ Start Campaign")
        self.btn_start.setObjectName("successBtn")
        self.btn_start.clicked.connect(self._toggle_campaign)
        self.btn_stop = QPushButton("⏹ Stop")
        self.btn_stop.setObjectName("dangerBtn")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._stop_campaign)
        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_stop)

        left_layout.addWidget(config_group)
        left_layout.addWidget(behavior_group)
        left_layout.addLayout(btn_row)
        left_layout.addStretch()

        # ── Right: Live Monitor ─────────────────────────
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        # Progress
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setFormat("0 / 0 visits  (0%)")
        right_layout.addWidget(self.progress)

        # Quick stats row
        stats_row = QHBoxLayout()
        for attr, label, color in [
            ("lbl_success", "✅ Success", "#22c55e"),
            ("lbl_failed", "❌ Failed", "#ef4444"),
            ("lbl_rate", "📈 Rate/min", "#60a5fa"),
            ("lbl_dwell", "⏱️ Avg Dwell", "#f59e0b"),
            ("lbl_elapsed", "🕒 Elapsed", "#a78bfa"),
        ]:
            frame = QFrame()
            frame.setObjectName("statCard")
            frame.setFixedHeight(70)
            fv = QVBoxLayout(frame)
            val_lbl = QLabel("—")
            val_lbl.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: bold;")
            name_lbl = QLabel(label)
            name_lbl.setStyleSheet("color: #64748b; font-size: 10px;")
            fv.addWidget(val_lbl)
            fv.addWidget(name_lbl)
            setattr(self, attr, val_lbl)
            stats_row.addWidget(frame)
        right_layout.addLayout(stats_row)

        # Session log table
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(5)
        self.log_table.setHorizontalHeaderLabels(["Keyword", "URL", "Source", "Dwell", "Status"])
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.log_table.setAlternatingRowColors(True)
        self.log_table.setMaximumHeight(300)
        right_layout.addWidget(QLabel("Session Log:"))
        right_layout.addWidget(self.log_table)

        # Notes
        note = QLabel(
            "⚠️ Ensure you have proxies loaded and keywords configured before starting. "
            "Higher concurrency = more resources needed."
        )
        note.setStyleSheet(
            "background: #1a1a0f; border: 1px solid #3a3a1e; border-radius: 6px; "
            "color: #fbbf24; padding: 8px 12px; font-size: 11px;"
        )
        note.setWordWrap(True)
        right_layout.addWidget(note)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([360, 840])
        layout.addWidget(splitter)

        # Stat refresh timer
        self._stat_timer = QTimer()
        self._stat_timer.timeout.connect(self._refresh_live_stats)
        self._stat_timer.start(1500)

    def _toggle_campaign(self):
        if not self._running:
            self._start_campaign()

    def _start_campaign(self):
        # Get keywords from parent
        parent = self.parent()
        while parent and not hasattr(parent, "keywords_tab"):
            parent = parent.parent()
        keywords = parent.keywords_tab.get_keywords() if parent and hasattr(parent, "keywords_tab") else []

        if not keywords:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Keywords", "Add keywords in the Keywords tab first.")
            return

        proxy_pool = None
        if parent and hasattr(parent, "proxy_tab"):
            proxy_pool = parent.proxy_tab.pool

        self._running = True
        self._start_time = time.time()
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.progress.setMaximum(self.visits_spin.value())

        headless = self.headless_combo.currentIndex() == 0
        browser_type = self.browser_type_combo.currentText()
        total_visits = self.visits_spin.value()
        concurrency = self.concurrency_spin.value()

        @qasync.asyncSlot()
        async def run():
            browser = BrowserController(headless=headless, browser_type=browser_type)
            await browser.init()
            engine = KeywordEngine(browser, proxy_pool=proxy_pool)

            def on_progress(result: dict):
                self._total_visits += 1
                if result.get("success"):
                    self._success_count += 1
                dwell = result.get("dwell_seconds", 0)
                if dwell:
                    self._dwell_times.append(dwell)
                self._add_log_row(result)
                self.progress.setValue(self._total_visits)
                pct = int(self._total_visits / total_visits * 100)
                self.progress.setFormat(f"{self._total_visits} / {total_visits} visits  ({pct}%)")

            try:
                await engine.run_campaign(
                    keywords=keywords,
                    total_visits=total_visits,
                    concurrency=concurrency,
                    on_progress=on_progress,
                )
            finally:
                await browser.close()
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

    def _add_log_row(self, result: dict):
        row = 0
        self.log_table.insertRow(row)
        kw = result.get("keyword", "—")[:40]
        url = result.get("target", "—")[:50]
        source = result.get("source", "—")
        dwell = f"{result.get('dwell_seconds', 0):.0f}s"
        ok = result.get("success", False)

        self.log_table.setItem(row, 0, QTableWidgetItem(kw))
        self.log_table.setItem(row, 1, QTableWidgetItem(url))
        self.log_table.setItem(row, 2, QTableWidgetItem(source))
        self.log_table.setItem(row, 3, QTableWidgetItem(dwell))

        status_item = QTableWidgetItem("✅ OK" if ok else "❌ FAIL")
        status_item.setForeground(QColor("#22c55e" if ok else "#ef4444"))
        self.log_table.setItem(row, 4, status_item)

        # Keep max 500 rows
        if self.log_table.rowCount() > 500:
            self.log_table.removeRow(500)

    def _refresh_live_stats(self):
        failed = self._total_visits - self._success_count
        self.lbl_success.setText(str(self._success_count))
        self.lbl_failed.setText(str(failed))
        if self._start_time and self._running:
            elapsed = time.time() - self._start_time
            rate = self._total_visits / (elapsed / 60) if elapsed > 0 else 0
            self.lbl_rate.setText(f"{rate:.1f}")
            m, s = divmod(int(elapsed), 60)
            h, m = divmod(m, 60)
            self.lbl_elapsed.setText(f"{h:02d}:{m:02d}:{s:02d}")
        avg_dwell = sum(self._dwell_times) / len(self._dwell_times) if self._dwell_times else 0
        self.lbl_dwell.setText(f"{avg_dwell:.0f}s" if avg_dwell else "—")

    def get_stats(self) -> dict:
        return {
            "active_sessions": self._active_sessions,
            "total_visits": self._total_visits,
            "success_count": self._success_count,
        }

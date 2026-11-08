"""
Proxy Management Tab — Import, check, manage proxy pools.
"""
import asyncio
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QTextEdit, QFileDialog,
    QProgressBar, QFrame, QComboBox, QGroupBox, QLineEdit,
    QHeaderView, QMessageBox, QSplitter,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QColor, QFont
import qasync

from proxy.checker import Proxy, ProxyPool, ProxyStatus, ProxyType, check_proxies_bulk, parse_proxy_list
from utils.logger import get_logger

logger = get_logger("gui.proxy_tab")

STATUS_COLORS = {
    ProxyStatus.ALIVE: "#22c55e",
    ProxyStatus.DEAD: "#ef4444",
    ProxyStatus.SLOW: "#f59e0b",
    ProxyStatus.UNCHECKED: "#64748b",
}


class ProxyTab(QWidget):
    def __init__(self):
        super().__init__()
        self.pool = ProxyPool(strategy="best_health")
        self._check_task = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        # Title
        title = QLabel("🔌 Proxy Manager")
        title.setStyleSheet("color: #c4b5fd; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # Stats bar
        self.stats_label = QLabel("No proxies loaded.")
        self.stats_label.setStyleSheet("color: #64748b; font-size: 11px; padding: 4px 0;")
        layout.addWidget(self.stats_label)

        # Splitter: left = import, right = table
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── Left Panel ──────────────────────────────────
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 10, 0)
        left_layout.setSpacing(10)

        import_group = QGroupBox("Import Proxies")
        import_v = QVBoxLayout(import_group)

        self.proxy_input = QTextEdit()
        self.proxy_input.setPlaceholderText(
            "Paste proxies here (one per line):\n\n"
            "host:port\n"
            "user:pass@host:port\n"
            "socks5://host:port\n"
            "http://user:pass@host:port\n"
        )
        self.proxy_input.setMinimumHeight(200)
        import_v.addWidget(self.proxy_input)

        btn_row = QHBoxLayout()
        self.btn_import = QPushButton("📥 Import from Text")
        self.btn_import.clicked.connect(self._import_from_text)
        self.btn_file = QPushButton("📂 Load from File")
        self.btn_file.setObjectName("secondaryBtn")
        self.btn_file.clicked.connect(self._load_from_file)
        btn_row.addWidget(self.btn_import)
        btn_row.addWidget(self.btn_file)
        import_v.addLayout(btn_row)

        # API Integration
        api_group = QGroupBox("Proxy API Integration")
        api_v = QVBoxLayout(api_group)
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("API Key (BrightData / Oxylabs / Smartproxy)")
        self.api_provider = QComboBox()
        self.api_provider.addItems(["BrightData", "Oxylabs", "Smartproxy", "IPRoyal", "Residential Generic"])
        self.btn_fetch_api = QPushButton("🔗 Fetch from API")
        self.btn_fetch_api.setObjectName("secondaryBtn")
        api_v.addWidget(QLabel("Provider:"))
        api_v.addWidget(self.api_provider)
        api_v.addWidget(QLabel("API Key:"))
        api_v.addWidget(self.api_key_input)
        api_v.addWidget(self.btn_fetch_api)

        left_layout.addWidget(import_group)
        left_layout.addWidget(api_group)
        left_layout.addStretch()

        # ── Right Panel ─────────────────────────────────
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        # Toolbar
        toolbar = QHBoxLayout()
        self.btn_check_all = QPushButton("⚡ Check All")
        self.btn_check_all.clicked.connect(self._check_all_proxies)
        self.btn_clear_dead = QPushButton("🗑️ Remove Dead")
        self.btn_clear_dead.setObjectName("dangerBtn")
        self.btn_clear_dead.clicked.connect(self._remove_dead)
        self.btn_export = QPushButton("💾 Export Alive")
        self.btn_export.setObjectName("secondaryBtn")
        self.btn_export.clicked.connect(self._export_alive)
        self.rotation_combo = QComboBox()
        self.rotation_combo.addItems(["best_health", "round_robin", "least_used", "random"])
        self.rotation_combo.currentTextChanged.connect(lambda s: setattr(self.pool, "strategy", s))
        toolbar.addWidget(self.btn_check_all)
        toolbar.addWidget(self.btn_clear_dead)
        toolbar.addWidget(self.btn_export)
        toolbar.addStretch()
        toolbar.addWidget(QLabel("Rotation:"))
        toolbar.addWidget(self.rotation_combo)
        right_layout.addLayout(toolbar)

        # Progress
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setTextVisible(True)
        right_layout.addWidget(self.progress)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Host", "Port", "Type", "Status", "Latency", "Country", "ISP", "Health"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        right_layout.addWidget(self.table)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([380, 820])
        layout.addWidget(splitter)

    def _import_from_text(self):
        text = self.proxy_input.toPlainText().strip()
        if not text:
            return
        proxies = parse_proxy_list(text)
        self.pool.add_many(proxies)
        self._refresh_table()
        self._update_stats()
        logger.info(f"Imported {len(proxies)} proxies from text")

    def _load_from_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Proxy File", "", "Text Files (*.txt);;All Files (*)"
        )
        if path:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            proxies = parse_proxy_list(text)
            self.pool.add_many(proxies)
            self._refresh_table()
            self._update_stats()
            logger.info(f"Loaded {len(proxies)} proxies from {path}")

    def _check_all_proxies(self):
        if not self.pool.proxies:
            QMessageBox.information(self, "No Proxies", "Import proxies first.")
            return
        self.btn_check_all.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.progress.setMaximum(len(self.pool.proxies))

        @qasync.asyncSlot()
        async def run_check():
            try:
                def on_progress(checked, total):
                    self.progress.setValue(checked)
                    self.progress.setFormat(f"Checking {checked}/{total}...")
                    if checked % 10 == 0:
                        self._refresh_table()
                        self._update_stats()

                await check_proxies_bulk(
                    self.pool.proxies,
                    timeout=10,
                    concurrency=50,
                    on_progress=on_progress,
                )
            finally:
                self._refresh_table()
                self._update_stats()
                self.progress.setVisible(False)
                self.btn_check_all.setEnabled(True)

        asyncio.ensure_future(run_check())

    def _remove_dead(self):
        before = len(self.pool.proxies)
        self.pool.proxies = [p for p in self.pool.proxies if p.status != ProxyStatus.DEAD]
        removed = before - len(self.pool.proxies)
        self._refresh_table()
        self._update_stats()
        logger.info(f"Removed {removed} dead proxies")

    def _export_alive(self):
        alive = self.pool.alive()
        if not alive:
            QMessageBox.information(self, "No Alive Proxies", "Check proxies first.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Proxies", "alive_proxies.txt", "Text Files (*.txt)")
        if path:
            with open(path, "w") as f:
                for p in alive:
                    f.write(f"{p.url}\n")
            logger.info(f"Exported {len(alive)} proxies to {path}")

    def _refresh_table(self):
        self.table.setRowCount(len(self.pool.proxies))
        for row, p in enumerate(self.pool.proxies):
            color = STATUS_COLORS.get(p.status, "#64748b")

            def cell(text, clr=None):
                item = QTableWidgetItem(str(text))
                if clr:
                    item.setForeground(QColor(clr))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                return item

            self.table.setItem(row, 0, cell(p.host))
            self.table.setItem(row, 1, cell(p.port))
            self.table.setItem(row, 2, cell(p.proxy_type.value))
            self.table.setItem(row, 3, cell(p.status.value.upper(), color))
            latency = f"{p.latency_ms:.0f}ms" if p.latency_ms > 0 else "—"
            self.table.setItem(row, 4, cell(latency))
            self.table.setItem(row, 5, cell(p.country or "—"))
            self.table.setItem(row, 6, cell(p.isp[:30] if p.isp else "—"))
            health = f"{p.health_score:.0%}" if p.status != ProxyStatus.UNCHECKED else "—"
            self.table.setItem(row, 7, cell(health))

    def _update_stats(self):
        stats = self.pool.stats()
        self.stats_label.setText(
            f"📊 Total: {stats['total']}  |  "
            f"🟢 Alive: {stats['alive']}  |  "
            f"🔴 Dead: {stats['dead']}  |  "
            f"⚪ Unchecked: {stats['unchecked']}"
        )

"""
OrbitTraffic — Professional Proxy Radar Tab
Features:
- Multi-format Proxy Importer (Text, CSV, API)
- Async Multi-threaded Proxy Latency & Anonymity Checker
- Geolocation Detection & Country Flags
- Live Health Scoring & One-Click Dead Proxy Purge
"""
import asyncio
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QTextEdit, QFileDialog,
    QProgressBar, QFrame, QComboBox, QGroupBox, QLineEdit,
    QHeaderView, QMessageBox, QSplitter,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import qasync

from proxy.checker import Proxy, ProxyPool, ProxyStatus, check_proxies_bulk, parse_proxy_list
from utils.logger import get_logger

logger = get_logger("gui.proxy_tab")

STATUS_COLORS = {
    ProxyStatus.ALIVE: "#10B981",
    ProxyStatus.DEAD: "#EF4444",
    ProxyStatus.SLOW: "#F59E0B",
    ProxyStatus.UNCHECKED: "#64748B",
}


class ProxyTab(QWidget):
    def __init__(self):
        super().__init__()
        self.pool = ProxyPool(strategy="best_health")
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(14)

        header_v = QVBoxLayout()
        title = QLabel("🌐 Proxy Radar & Fleet Manager")
        title.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: 700;")
        subtitle = QLabel("Import, validate, and rotate residential & datacenter proxies with geolocation matching.")
        subtitle.setStyleSheet("color: #94A3B8; font-size: 12px;")
        header_v.addWidget(title)
        header_v.addWidget(subtitle)
        main_layout.addLayout(header_v)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── Left: Import & API ────────────────────────────────────
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 10, 0)
        left_layout.setSpacing(12)

        import_group = QGroupBox("Import Proxy Pool")
        iv = QVBoxLayout(import_group)

        self.proxy_input = QTextEdit()
        self.proxy_input.setPlaceholderText(
            "Paste proxies here (one per line):\n\n"
            "user:pass@host:port\n"
            "socks5://host:port\n"
            "http://host:port\n"
        )
        self.proxy_input.setMinimumHeight(180)
        iv.addWidget(self.proxy_input)

        b_row = QHBoxLayout()
        self.btn_import = QPushButton("Import Text")
        self.btn_import.setObjectName("primaryActionBtn")
        self.btn_import.clicked.connect(self._import_from_text)
        self.btn_file = QPushButton("Load File")
        self.btn_file.setObjectName("secondaryBtn")
        self.btn_file.clicked.connect(self._load_from_file)
        b_row.addWidget(self.btn_import)
        b_row.addWidget(self.btn_file)
        iv.addLayout(b_row)
        left_layout.addWidget(import_group)

        # API integration
        api_group = QGroupBox("Residential Proxy API Provider")
        av = QVBoxLayout(api_group)
        av.setSpacing(6)
        av.addWidget(QLabel("Provider:"))
        self.api_provider = QComboBox()
        self.api_provider.addItems(["Bright Data (Luminati)", "Oxylabs Residential", "Smartproxy", "IPRoyal", "Generic Rotating SOCKS5"])
        av.addWidget(self.api_provider)

        av.addWidget(QLabel("API Key / Endpoint:"))
        self.api_key = QLineEdit()
        self.api_key.setPlaceholderText("Enter API token or rotating endpoint")
        av.addWidget(self.api_key)

        self.btn_api_sync = QPushButton("Sync from Provider")
        self.btn_api_sync.setObjectName("secondaryBtn")
        av.addWidget(self.btn_api_sync)
        left_layout.addWidget(api_group)
        left_layout.addStretch()

        # ── Right: Proxy Table & Actions ──────────────────────────
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # Toolbar
        bar = QHBoxLayout()
        self.btn_check_all = QPushButton("Test Latency & Geolocation")
        self.btn_check_all.setObjectName("primaryActionBtn")
        self.btn_check_all.clicked.connect(self._check_all)

        self.btn_purge_dead = QPushButton("Purge Inactive")
        self.btn_purge_dead.setObjectName("dangerBtn")
        self.btn_purge_dead.clicked.connect(self._remove_dead)

        self.btn_export = QPushButton("Export Verified")
        self.btn_export.setObjectName("secondaryBtn")
        self.btn_export.clicked.connect(self._export_alive)

        bar.addWidget(self.btn_check_all)
        bar.addWidget(self.btn_purge_dead)
        bar.addWidget(self.btn_export)
        bar.addStretch()

        bar.addWidget(QLabel("Rotation:"))
        self.rotation_combo = QComboBox()
        self.rotation_combo.addItems(["best_health", "round_robin", "least_used", "random"])
        self.rotation_combo.currentTextChanged.connect(lambda s: setattr(self.pool, "strategy", s))
        bar.addWidget(self.rotation_combo)
        right_layout.addLayout(bar)

        # Progress
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        right_layout.addWidget(self.progress)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Host", "Port", "Protocol", "Status", "Latency", "Country / City", "Health Score"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        right_layout.addWidget(self.table)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([360, 840])
        main_layout.addWidget(splitter)

    def _import_from_text(self):
        text = self.proxy_input.toPlainText().strip()
        if not text:
            return
        proxies = parse_proxy_list(text)
        self.pool.add_many(proxies)
        self._refresh_table()
        self.proxy_input.clear()

    def _load_from_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Proxy File", "", "Text Files (*.txt);;All (*)")
        if path:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                proxies = parse_proxy_list(f.read())
                self.pool.add_many(proxies)
                self._refresh_table()

    def _check_all(self):
        if not self.pool.proxies:
            QMessageBox.information(self, "No Proxies", "Please import proxies first.")
            return

        self.btn_check_all.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.progress.setMaximum(len(self.pool.proxies))

        @qasync.asyncSlot()
        async def run():
            try:
                def on_progress(done, total):
                    self.progress.setValue(done)
                    if done % 5 == 0:
                        self._refresh_table()

                await check_proxies_bulk(self.pool.proxies, timeout=8, concurrency=40, on_progress=on_progress)
            finally:
                self._refresh_table()
                self.progress.setVisible(False)
                self.btn_check_all.setEnabled(True)

        asyncio.ensure_future(run())

    def _remove_dead(self):
        self.pool.proxies = [p for p in self.pool.proxies if p.status != ProxyStatus.DEAD]
        self._refresh_table()

    def _export_alive(self):
        alive = self.pool.alive()
        if not alive:
            QMessageBox.information(self, "No Alive Proxies", "No verified proxies to export.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Proxies", "alive_proxies.txt", "Text Files (*.txt)")
        if path:
            with open(path, "w") as f:
                for p in alive:
                    f.write(f"{p.url}\n")

    def _refresh_table(self):
        self.table.setRowCount(len(self.pool.proxies))
        for row, p in enumerate(self.pool.proxies):
            color = STATUS_COLORS.get(p.status, "#64748B")

            def cell(text, clr=None):
                it = QTableWidgetItem(str(text))
                if clr:
                    it.setForeground(QColor(clr))
                it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                return it

            self.table.setItem(row, 0, cell(p.host))
            self.table.setItem(row, 1, cell(p.port))
            self.table.setItem(row, 2, cell(p.proxy_type.value.upper(), "#818CF8"))
            self.table.setItem(row, 3, cell(p.status.value.upper(), color))
            latency = f"{p.latency_ms:.0f}ms" if p.latency_ms > 0 else "—"
            self.table.setItem(row, 4, cell(latency, "#38BDF8" if p.latency_ms > 0 else "#64748B"))
            geo = f"{p.country} ({p.city})" if p.country else "—"
            self.table.setItem(row, 5, cell(geo))
            score = f"{p.health_score * 100:.0f}%" if p.status != ProxyStatus.UNCHECKED else "—"
            self.table.setItem(row, 6, cell(score, "#10B981"))

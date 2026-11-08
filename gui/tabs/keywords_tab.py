"""
OrbitTraffic — Keyword Studio & SERP Target Manager
Manage organic search queries, SERP position targets, CTR curve calculations,
and individual multi-hop journey depths.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QSpinBox, QDoubleSpinBox, QGroupBox, QHeaderView,
    QDialog, QFormLayout, QDialogButtonBox, QMessageBox,
    QFileDialog, QTextEdit, QCheckBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from traffic_keyword.engine import Keyword


class KeywordDialog(QDialog):
    def __init__(self, parent=None, keyword: Keyword = None):
        super().__init__(parent)
        self.setWindowTitle("Add Organic Keyword" if keyword is None else "Edit Keyword")
        self.setModal(True)
        self.setMinimumWidth(480)
        self._build_ui()
        if keyword:
            self._populate(keyword)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("e.g. best organic seo tools")
        form.addRow("Keyword / Query:", self.keyword_input)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://yourwebsite.com/target-page")
        form.addRow("Target Landing URL:", self.url_input)

        self.engine_combo = QComboBox()
        self.engine_combo.addItems(["google", "bing", "duckduckgo"])
        form.addRow("Search Engine:", self.engine_combo)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["en", "de", "fr", "es", "ja", "it", "nl", "pt", "ru"])
        form.addRow("Language:", self.lang_combo)

        self.position_spin = QSpinBox()
        self.position_spin.setRange(1, 10)
        self.position_spin.setValue(1)
        form.addRow("Target SERP Rank (1-10):", self.position_spin)

        self.hops_spin = QSpinBox()
        self.hops_spin.setRange(1, 5)
        self.hops_spin.setValue(2)
        form.addRow("Internal Journey Hops:", self.hops_spin)

        self.chk_pogo = QCheckBox("Enable RankBrain Pogo-Stick Simulation")
        self.chk_pogo.setChecked(True)
        form.addRow("", self.chk_pogo)

        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _populate(self, kw: Keyword):
        self.keyword_input.setText(kw.text)
        self.url_input.setText(kw.target_url)
        self.engine_combo.setCurrentText(kw.search_engine)
        self.lang_combo.setCurrentText(kw.language)
        self.position_spin.setValue(kw.target_position)
        self.hops_spin.setValue(kw.journey_hops)
        self.chk_pogo.setChecked(kw.enable_pogo)

    def get_keyword(self) -> Keyword:
        return Keyword(
            text=self.keyword_input.text().strip(),
            target_url=self.url_input.text().strip(),
            search_engine=self.engine_combo.currentText(),
            language=self.lang_combo.currentText(),
            target_position=self.position_spin.value(),
            journey_hops=self.hops_spin.value(),
            enable_pogo=self.chk_pogo.isChecked(),
        )


class KeywordsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.keywords: list[Keyword] = [
            Keyword(text="best organic traffic booster", target_url="https://example.com/platform", target_position=1),
            Keyword(text="google search impression simulation", target_url="https://example.com/features", target_position=2),
        ]
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(14)

        header_v = QVBoxLayout()
        title = QLabel("🎯 Keyword Studio & SERP Architecture")
        title.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: 700;")
        subtitle = QLabel("Design keyword campaigns, target search positions, and configure journey depths.")
        subtitle.setStyleSheet("color: #94A3B8; font-size: 12px;")
        header_v.addWidget(title)
        header_v.addWidget(subtitle)
        main_layout.addLayout(header_v)

        # Toolbar
        bar = QHBoxLayout()
        self.btn_add = QPushButton("➕ Add Keyword")
        self.btn_add.setObjectName("primaryActionBtn")
        self.btn_add.clicked.connect(self._add)

        self.btn_edit = QPushButton("✏️ Edit")
        self.btn_edit.setObjectName("secondaryBtn")
        self.btn_edit.clicked.connect(self._edit)

        self.btn_delete = QPushButton("🗑️ Delete")
        self.btn_delete.setObjectName("dangerBtn")
        self.btn_delete.clicked.connect(self._delete)

        bar.addWidget(self.btn_add)
        bar.addWidget(self.btn_edit)
        bar.addWidget(self.btn_delete)
        bar.addStretch()

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("🔍 Filter keywords...")
        self.filter_input.setFixedWidth(220)
        self.filter_input.textChanged.connect(self._filter)
        bar.addWidget(self.filter_input)
        main_layout.addLayout(bar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Search Query", "Landing Page", "Engine", "Position", "Estimated CTR", "Journey Hops", "Pogo-Stick"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        main_layout.addWidget(self.table)

        # Bulk Box
        bulk_group = QGroupBox("Fast Bulk Importer (Format: query | url)")
        bv = QVBoxLayout(bulk_group)
        self.bulk_text = QTextEdit()
        self.bulk_text.setPlaceholderText("buy running shoes online | https://mysite.com/shoes\n...")
        self.bulk_text.setMaximumHeight(80)
        btn_bulk = QPushButton("⚡ Add Queries from Text")
        btn_bulk.setObjectName("secondaryBtn")
        btn_bulk.clicked.connect(self._bulk_import)
        bv.addWidget(self.bulk_text)
        bv.addWidget(btn_bulk)
        main_layout.addWidget(bulk_group)

        self._refresh()

    def _add(self):
        dlg = KeywordDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            kw = dlg.get_keyword()
            if kw.text and kw.target_url:
                self.keywords.append(kw)
                self._refresh()

    def _edit(self):
        row = self.table.currentRow()
        if 0 <= row < len(self.keywords):
            dlg = KeywordDialog(self, self.keywords[row])
            if dlg.exec() == QDialog.DialogCode.Accepted:
                self.keywords[row] = dlg.get_keyword()
                self._refresh()

    def _delete(self):
        rows = sorted(set(it.row() for it in self.table.selectedItems()), reverse=True)
        for r in rows:
            if 0 <= r < len(self.keywords):
                self.keywords.pop(r)
        self._refresh()

    def _bulk_import(self):
        for line in self.bulk_text.toPlainText().strip().splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split("|")
            text = parts[0].strip()
            url = parts[1].strip() if len(parts) > 1 else "https://example.com"
            self.keywords.append(Keyword(text=text, target_url=url))
        self.bulk_text.clear()
        self._refresh()

    def _filter(self, q: str):
        for r in range(self.table.rowCount()):
            text = self.table.item(r, 0).text().lower() if self.table.item(r, 0) else ""
            self.table.setRowHidden(r, q.lower() not in text)

    def _refresh(self):
        self.table.setRowCount(len(self.keywords))
        for row, kw in enumerate(self.keywords):
            def cell(text, color="#F8FAFC"):
                it = QTableWidgetItem(str(text))
                it.setForeground(QColor(color))
                it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                return it

            self.table.setItem(row, 0, cell(kw.text))
            self.table.setItem(row, 1, cell(kw.target_url[:40], "#94A3B8"))
            self.table.setItem(row, 2, cell(kw.search_engine.upper(), "#38BDF8"))
            self.table.setItem(row, 3, cell(f"Rank #{kw.target_position}"))
            ctr_pct = f"{kw.get_ctr() * 100:.1f}%"
            self.table.setItem(row, 4, cell(ctr_pct, "#10B981"))
            self.table.setItem(row, 5, cell(f"{kw.journey_hops} pages", "#818CF8"))
            self.table.setItem(row, 6, cell("ACTIVE" if kw.enable_pogo else "OFF", "#F59E0B" if kw.enable_pogo else "#64748B"))

    def get_keywords(self) -> list:
        return self.keywords

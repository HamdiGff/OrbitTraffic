"""
Keywords Management Tab
"""
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QSpinBox, QDoubleSpinBox, QGroupBox, QHeaderView,
    QDialog, QFormLayout, QDialogButtonBox, QMessageBox,
    QFileDialog, QTextEdit,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from keyword.engine import Keyword
from utils.logger import get_logger

logger = get_logger("gui.keywords")

SEARCH_ENGINES = ["google", "bing", "duckduckgo"]
LANGUAGES = ["en", "de", "fr", "es", "it", "pt", "nl", "pl", "ru", "ar", "ja", "zh", "ko", "hi", "tr"]


class KeywordDialog(QDialog):
    """Add/Edit keyword dialog."""
    def __init__(self, parent=None, keyword: Keyword = None):
        super().__init__(parent)
        self.setWindowTitle("Add Keyword" if keyword is None else "Edit Keyword")
        self.setModal(True)
        self.setMinimumWidth(480)
        self._kw = keyword
        self._build_ui()
        if keyword:
            self._populate(keyword)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("e.g. best running shoes")
        form.addRow("Keyword:", self.keyword_input)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://yourwebsite.com/page")
        form.addRow("Target URL:", self.url_input)

        self.engine_combo = QComboBox()
        self.engine_combo.addItems(SEARCH_ENGINES)
        form.addRow("Search Engine:", self.engine_combo)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(LANGUAGES)
        form.addRow("Language:", self.lang_combo)

        self.position_spin = QSpinBox()
        self.position_spin.setRange(1, 10)
        self.position_spin.setValue(1)
        form.addRow("Target SERP Position:", self.position_spin)

        self.visits_spin = QSpinBox()
        self.visits_spin.setRange(1, 10000)
        self.visits_spin.setValue(10)
        form.addRow("Daily Visits:", self.visits_spin)

        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0.1, 10.0)
        self.weight_spin.setSingleStep(0.1)
        self.weight_spin.setValue(1.0)
        form.addRow("Weight:", self.weight_spin)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _populate(self, kw: Keyword):
        self.keyword_input.setText(kw.text)
        self.url_input.setText(kw.target_url)
        idx = self.engine_combo.findText(kw.search_engine)
        if idx >= 0:
            self.engine_combo.setCurrentIndex(idx)
        lang_idx = self.lang_combo.findText(kw.language)
        if lang_idx >= 0:
            self.lang_combo.setCurrentIndex(lang_idx)
        self.position_spin.setValue(kw.target_position)
        self.visits_spin.setValue(kw.daily_visits)
        self.weight_spin.setValue(kw.weight)

    def get_keyword(self) -> Keyword:
        return Keyword(
            text=self.keyword_input.text().strip(),
            target_url=self.url_input.text().strip(),
            search_engine=self.engine_combo.currentText(),
            language=self.lang_combo.currentText(),
            target_position=self.position_spin.value(),
            daily_visits=self.visits_spin.value(),
            weight=self.weight_spin.value(),
        )


class KeywordsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.keywords: list[Keyword] = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        title = QLabel("🔑 Keyword Manager")
        title.setStyleSheet("color: #c4b5fd; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # Toolbar
        toolbar = QHBoxLayout()
        self.btn_add = QPushButton("➕ Add Keyword")
        self.btn_add.clicked.connect(self._add_keyword)
        self.btn_edit = QPushButton("✏️ Edit")
        self.btn_edit.setObjectName("secondaryBtn")
        self.btn_edit.clicked.connect(self._edit_keyword)
        self.btn_delete = QPushButton("🗑️ Delete")
        self.btn_delete.setObjectName("dangerBtn")
        self.btn_delete.clicked.connect(self._delete_keyword)
        self.btn_import = QPushButton("📂 Import CSV")
        self.btn_import.setObjectName("secondaryBtn")
        self.btn_import.clicked.connect(self._import_csv)
        self.btn_export = QPushButton("💾 Export")
        self.btn_export.setObjectName("secondaryBtn")
        self.btn_export.clicked.connect(self._export)

        for btn in [self.btn_add, self.btn_edit, self.btn_delete, self.btn_import, self.btn_export]:
            toolbar.addWidget(btn)
        toolbar.addStretch()

        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Filter keywords...")
        self.search_input.setFixedWidth(220)
        self.search_input.textChanged.connect(self._filter_table)
        toolbar.addWidget(self.search_input)

        layout.addLayout(toolbar)

        # Stats
        self.stats_label = QLabel("No keywords. Add some to get started.")
        self.stats_label.setStyleSheet("color: #64748b; font-size: 11px;")
        layout.addWidget(self.stats_label)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Keyword", "Target URL", "Engine", "Language", "Position", "Daily Visits", "Weight"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

        # Bulk import area
        bulk_group = QGroupBox("Bulk Import (one keyword per line, optionally: keyword|url)")
        bulk_v = QVBoxLayout(bulk_group)
        self.bulk_input = QTextEdit()
        self.bulk_input.setPlaceholderText("best running shoes\nbest hiking boots|https://mysite.com/boots\n...")
        self.bulk_input.setMaximumHeight(120)
        self.btn_bulk_add = QPushButton("📥 Add All")
        self.btn_bulk_add.clicked.connect(self._bulk_import)
        bulk_v.addWidget(self.bulk_input)
        bulk_v.addWidget(self.btn_bulk_add)
        layout.addWidget(bulk_group)

    def _add_keyword(self):
        dlg = KeywordDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            kw = dlg.get_keyword()
            if kw.text and kw.target_url:
                self.keywords.append(kw)
                self._refresh_table()
            else:
                QMessageBox.warning(self, "Invalid", "Keyword text and URL are required.")

    def _edit_keyword(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.keywords):
            return
        dlg = KeywordDialog(self, self.keywords[row])
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.keywords[row] = dlg.get_keyword()
            self._refresh_table()

    def _delete_keyword(self):
        rows = sorted(set(item.row() for item in self.table.selectedItems()), reverse=True)
        for row in rows:
            if 0 <= row < len(self.keywords):
                self.keywords.pop(row)
        self._refresh_table()

    def _bulk_import(self):
        text = self.bulk_input.toPlainText().strip()
        default_url = "https://example.com"
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split("|")
            kw = Keyword(
                text=parts[0].strip(),
                target_url=parts[1].strip() if len(parts) > 1 else default_url,
            )
            self.keywords.append(kw)
        self._refresh_table()
        self.bulk_input.clear()

    def _import_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Keywords", "", "CSV Files (*.csv);;Text (*.txt)")
        if path:
            import csv
            try:
                with open(path, newline="", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if row:
                            kw = Keyword(
                                text=row[0].strip(),
                                target_url=row[1].strip() if len(row) > 1 else "https://example.com",
                            )
                            self.keywords.append(kw)
                self._refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not read file: {e}")

    def _export(self):
        if not self.keywords:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Keywords", "keywords.csv", "CSV (*.csv)")
        if path:
            import csv
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["keyword", "target_url", "engine", "language", "position", "visits", "weight"])
                for kw in self.keywords:
                    writer.writerow([kw.text, kw.target_url, kw.search_engine, kw.language,
                                     kw.target_position, kw.daily_visits, kw.weight])

    def _filter_table(self, text: str):
        for row in range(self.table.rowCount()):
            match = text.lower() in (self.table.item(row, 0).text().lower() if self.table.item(row, 0) else "")
            self.table.setRowHidden(row, not match)

    def _refresh_table(self):
        self.table.setRowCount(len(self.keywords))
        for row, kw in enumerate(self.keywords):
            self.table.setItem(row, 0, QTableWidgetItem(kw.text))
            self.table.setItem(row, 1, QTableWidgetItem(kw.target_url))
            self.table.setItem(row, 2, QTableWidgetItem(kw.search_engine))
            self.table.setItem(row, 3, QTableWidgetItem(kw.language))
            self.table.setItem(row, 4, QTableWidgetItem(str(kw.target_position)))
            self.table.setItem(row, 5, QTableWidgetItem(str(kw.daily_visits)))
            self.table.setItem(row, 6, QTableWidgetItem(str(kw.weight)))
        total_visits = sum(k.daily_visits for k in self.keywords)
        self.stats_label.setText(
            f"📊 {len(self.keywords)} keywords  |  ~{total_visits} visits/day projected"
        )

    def get_keywords(self) -> list:
        return self.keywords

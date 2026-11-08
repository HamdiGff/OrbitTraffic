"""Live Logs Tab — Stream real-time log output."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QPlainTextEdit, QComboBox, QCheckBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QTextCursor
import os


class LogsTab(QWidget):
    def __init__(self):
        super().__init__()
        self._log_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "logs", "orbittraffic.log"
        )
        self._last_pos = 0
        self._build_ui()
        self._start_tail()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        title = QLabel("📋 Live Log Viewer")
        title.setStyleSheet("color: #c4b5fd; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        toolbar = QHBoxLayout()
        self.chk_scroll = QCheckBox("Auto-scroll")
        self.chk_scroll.setChecked(True)
        self.level_filter = QComboBox()
        self.level_filter.addItems(["ALL", "INFO", "WARNING", "ERROR"])
        self.btn_clear = QPushButton("🗑️ Clear")
        self.btn_clear.setObjectName("secondaryBtn")
        self.btn_clear.clicked.connect(self._clear)
        toolbar.addWidget(QLabel("Level:"))
        toolbar.addWidget(self.level_filter)
        toolbar.addWidget(self.chk_scroll)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_clear)
        layout.addLayout(toolbar)

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Cascadia Code, Consolas, Courier New", 10))
        self.log_view.setStyleSheet("""
            background: #0a0a14;
            color: #94a3b8;
            border: 1px solid #1e1e3a;
            border-radius: 6px;
            padding: 8px;
        """)
        self.log_view.setMaximumBlockCount(5000)
        layout.addWidget(self.log_view)

    def _start_tail(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self._tail_log)
        self.timer.start(1000)

    def _tail_log(self):
        try:
            if not os.path.exists(self._log_path):
                return
            with open(self._log_path, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(self._last_pos)
                new_lines = f.read()
                self._last_pos = f.tell()

            if new_lines:
                level = self.level_filter.currentText()
                for line in new_lines.splitlines():
                    if level != "ALL" and level not in line:
                        continue
                    self._append_colored(line)

                if self.chk_scroll.isChecked():
                    self.log_view.moveCursor(QTextCursor.MoveOperation.End)
        except Exception:
            pass

    def _append_colored(self, line: str):
        color = "#94a3b8"
        if "ERROR" in line or "CRITICAL" in line:
            color = "#ef4444"
        elif "WARNING" in line:
            color = "#f59e0b"
        elif "INFO" in line:
            color = "#86efac"
        elif "DEBUG" in line:
            color = "#64748b"

        cursor = self.log_view.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor.setCharFormat(fmt)
        cursor.insertText(line + "\n")

    def _clear(self):
        self.log_view.clear()

    def append_message(self, msg: str, level: str = "INFO"):
        """Directly append a message (from other tabs)."""
        import time
        ts = time.strftime("%H:%M:%S")
        self._append_colored(f"{ts} [{level}]: {msg}")

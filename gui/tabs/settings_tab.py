"""
OrbitTraffic — Settings & System Configuration Tab
"""
import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QSpinBox, QCheckBox, QComboBox,
    QLineEdit, QFormLayout, QScrollArea, QFrame, QMessageBox,
)
from PyQt6.QtCore import Qt
from utils.logger import get_logger

logger = get_logger("gui.settings")
SETTINGS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "settings.json")


class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self._settings = self._load()
        self._build_ui()

    def _load(self) -> dict:
        try:
            with open(SETTINGS_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save(self):
        try:
            with open(SETTINGS_PATH, "w") as f:
                json.dump(self._settings, f, indent=2)
            QMessageBox.information(self, "Saved", "Settings successfully persisted.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        header_v = QVBoxLayout()
        title = QLabel("GLOBAL CONFIGURATION & ARCHITECTURE")
        title.setStyleSheet("color: #FFFFFF; font-size: 15px; font-weight: 700; letter-spacing: 0.5px;")
        subtitle = QLabel("Tune concurrent browser resources, stealth thresholds, and auto-update parameters.")
        subtitle.setStyleSheet("color: #94A3B8; font-size: 12px;")
        header_v.addWidget(title)
        header_v.addWidget(subtitle)
        layout.addLayout(header_v)

        # ── 1. Engine Performance ─────────────────────────────────
        perf_group = QGroupBox("Performance & Resources")
        pf = QFormLayout(perf_group)
        self.max_workers = QSpinBox()
        self.max_workers.setRange(1, 64)
        self.max_workers.setValue(self._settings.get("max_concurrent_sessions", 5))
        pf.addRow("Max Concurrent Browser Slots:", self.max_workers)

        self.chk_headless = QCheckBox("Run browsers in headless stealth mode (Recommended)")
        self.chk_headless.setChecked(self._settings.get("browser", {}).get("headless", True))
        pf.addRow("", self.chk_headless)
        layout.addWidget(perf_group)

        # ── 2. Anti-Detect & Stealth Shield ───────────────────────
        stealth_group = QGroupBox("Anti-Detect & Fingerprint Spoofing")
        sf = QFormLayout(stealth_group)

        self.chk_canvas = QCheckBox("Canvas 2D Noise Injection (Prevents canvas fingerprinting)")
        self.chk_canvas.setChecked(True)
        self.chk_webgl = QCheckBox("WebGL Unmasked Vendor & Renderer Spoofing")
        self.chk_webgl.setChecked(True)
        self.chk_audio = QCheckBox("AudioContext Oscillator Dynamic Jitter")
        self.chk_audio.setChecked(True)
        self.chk_webrtc = QCheckBox("WebRTC Leak Shield (Masks public & private IP leaks)")
        self.chk_webrtc.setChecked(True)

        for chk in [self.chk_canvas, self.chk_webgl, self.chk_audio, self.chk_webrtc]:
            sf.addRow("", chk)
        layout.addWidget(stealth_group)

        # ── 3. GitHub Releases & CI/CD ────────────────────────────
        gh_group = QGroupBox("GitHub Releases & Remote Deployment")
        gf = QFormLayout(gh_group)
        self.gh_repo = QLineEdit()
        self.gh_repo.setText(self._settings.get("github", {}).get("repo", "HamdiGff/OrbitTraffic"))
        gf.addRow("Repository Target:", self.gh_repo)

        self.chk_autoupdate = QCheckBox("Check for automated releases on launch")
        self.chk_autoupdate.setChecked(True)
        gf.addRow("", self.chk_autoupdate)
        layout.addWidget(gh_group)

        # Save Button
        self.btn_save = QPushButton("💾 Save All Settings")
        self.btn_save.setObjectName("primaryActionBtn")
        self.btn_save.clicked.connect(self._save_all)
        layout.addWidget(self.btn_save)
        layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _save_all(self):
        self._settings["max_concurrent_sessions"] = self.max_workers.value()
        self._settings["browser"]["headless"] = self.chk_headless.isChecked()
        self._settings["github"]["repo"] = self.gh_repo.text().strip()
        self._save()

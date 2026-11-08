"""Settings Tab"""
import json, os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox,
    QLineEdit, QFormLayout, QSlider, QScrollArea, QFrame, QMessageBox,
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
            with open(SETTINGS_PATH) as f:
                return json.load(f)
        except Exception:
            return {}

    def _save(self):
        try:
            with open(SETTINGS_PATH, "w") as f:
                json.dump(self._settings, f, indent=2)
            QMessageBox.information(self, "Saved", "Settings saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(18)

        title = QLabel("⚙️ Settings")
        title.setStyleSheet("color: #c4b5fd; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # ── Browser ───────────────────────────────────
        browser_group = QGroupBox("Browser")
        bf = QFormLayout(browser_group)
        self.chk_headless = QCheckBox("Run headless (no visible window)")
        self.chk_headless.setChecked(self._settings.get("browser", {}).get("headless", True))
        self.chk_viewport = QCheckBox("Randomize viewport size")
        self.chk_viewport.setChecked(self._settings.get("browser", {}).get("viewport_randomize", True))
        self.max_sessions = QSpinBox()
        self.max_sessions.setRange(1, 100)
        self.max_sessions.setValue(self._settings.get("max_concurrent_sessions", 5))
        bf.addRow("", self.chk_headless)
        bf.addRow("", self.chk_viewport)
        bf.addRow("Max Concurrent Sessions:", self.max_sessions)
        layout.addWidget(browser_group)

        # ── Behavior ──────────────────────────────────
        behavior_group = QGroupBox("Behavior AI")
        bvf = QFormLayout(behavior_group)
        self.mouse_speed = QComboBox()
        self.mouse_speed.addItems(["slow", "natural", "fast"])
        self.mouse_speed.setCurrentText(self._settings.get("behavior", {}).get("mouse_speed", "natural"))
        self.scroll_speed = QComboBox()
        self.scroll_speed.addItems(["slow", "natural", "fast"])
        self.scroll_speed.setCurrentText(self._settings.get("behavior", {}).get("scroll_speed", "natural"))
        self.chk_reading = QCheckBox("Enable reading time simulation")
        self.chk_reading.setChecked(self._settings.get("behavior", {}).get("reading_simulation", True))
        self.min_dwell = QSpinBox()
        self.min_dwell.setRange(5, 600)
        self.min_dwell.setValue(self._settings.get("behavior", {}).get("min_session_duration", 30))
        self.max_dwell = QSpinBox()
        self.max_dwell.setRange(5, 600)
        self.max_dwell.setValue(self._settings.get("behavior", {}).get("max_session_duration", 300))
        bvf.addRow("Mouse Speed:", self.mouse_speed)
        bvf.addRow("Scroll Speed:", self.scroll_speed)
        bvf.addRow("", self.chk_reading)
        bvf.addRow("Min Session Duration (s):", self.min_dwell)
        bvf.addRow("Max Session Duration (s):", self.max_dwell)
        layout.addWidget(behavior_group)

        # ── Fingerprint ───────────────────────────────
        fp_group = QGroupBox("Fingerprint Spoofing")
        fpf = QFormLayout(fp_group)
        self.chk_canvas = QCheckBox("Canvas noise injection")
        self.chk_canvas.setChecked(self._settings.get("fingerprint", {}).get("canvas_noise", True))
        self.chk_webgl = QCheckBox("WebGL renderer spoofing")
        self.chk_webgl.setChecked(self._settings.get("fingerprint", {}).get("webgl_spoof", True))
        self.chk_audio = QCheckBox("Audio context noise")
        self.chk_audio.setChecked(self._settings.get("fingerprint", {}).get("audio_noise", True))
        self.chk_tz = QCheckBox("Match timezone to proxy geolocation")
        self.chk_tz.setChecked(self._settings.get("fingerprint", {}).get("timezone_match_proxy", True))
        for chk in [self.chk_canvas, self.chk_webgl, self.chk_audio, self.chk_tz]:
            fpf.addRow("", chk)
        layout.addWidget(fp_group)

        # ── Proxy ─────────────────────────────────────
        proxy_group = QGroupBox("Proxy")
        pf = QFormLayout(proxy_group)
        self.rotation_strategy = QComboBox()
        self.rotation_strategy.addItems(["best_health", "round_robin", "least_used", "random"])
        self.rotation_strategy.setCurrentText(self._settings.get("proxy", {}).get("rotation_strategy", "best_health"))
        self.proxy_cooldown = QSpinBox()
        self.proxy_cooldown.setRange(0, 3600)
        self.proxy_cooldown.setValue(self._settings.get("proxy", {}).get("cooldown_seconds", 60))
        self.max_proxy_failures = QSpinBox()
        self.max_proxy_failures.setRange(1, 20)
        self.max_proxy_failures.setValue(self._settings.get("proxy", {}).get("max_failures", 3))
        pf.addRow("Rotation Strategy:", self.rotation_strategy)
        pf.addRow("Cooldown (seconds):", self.proxy_cooldown)
        pf.addRow("Max Failures Before Ban:", self.max_proxy_failures)
        layout.addWidget(proxy_group)

        # ── GitHub / Updates ──────────────────────────
        gh_group = QGroupBox("GitHub & Auto-Update")
        ghf = QFormLayout(gh_group)
        self.chk_autoupdate = QCheckBox("Enable auto-update on startup")
        self.chk_autoupdate.setChecked(self._settings.get("github", {}).get("auto_update", True))
        self.github_repo = QLineEdit()
        self.github_repo.setText(self._settings.get("github", {}).get("repo", ""))
        self.github_repo.setPlaceholderText("username/repo")
        ghf.addRow("", self.chk_autoupdate)
        ghf.addRow("GitHub Repo:", self.github_repo)
        layout.addWidget(gh_group)

        # Save button
        self.btn_save = QPushButton("💾 Save Settings")
        self.btn_save.clicked.connect(self._save_all)
        layout.addWidget(self.btn_save)
        layout.addStretch()

        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _save_all(self):
        self._settings["max_concurrent_sessions"] = self.max_sessions.value()
        self._settings["browser"] = {
            "headless": self.chk_headless.isChecked(),
            "viewport_randomize": self.chk_viewport.isChecked(),
        }
        self._settings["behavior"] = {
            "mouse_speed": self.mouse_speed.currentText(),
            "scroll_speed": self.scroll_speed.currentText(),
            "reading_simulation": self.chk_reading.isChecked(),
            "min_session_duration": self.min_dwell.value(),
            "max_session_duration": self.max_dwell.value(),
        }
        self._settings["fingerprint"] = {
            "canvas_noise": self.chk_canvas.isChecked(),
            "webgl_spoof": self.chk_webgl.isChecked(),
            "audio_noise": self.chk_audio.isChecked(),
            "timezone_match_proxy": self.chk_tz.isChecked(),
        }
        self._settings["proxy"] = {
            "rotation_strategy": self.rotation_strategy.currentText(),
            "cooldown_seconds": self.proxy_cooldown.value(),
            "max_failures": self.max_proxy_failures.value(),
        }
        self._settings["github"] = {
            "auto_update": self.chk_autoupdate.isChecked(),
            "repo": self.github_repo.text().strip(),
        }
        self._save()

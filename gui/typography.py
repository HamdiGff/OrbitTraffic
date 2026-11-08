"""
OrbitTraffic — Professional Typography & Font System
Configures high-DPI font antialiasing and registers modern geometric
and monospace typefaces for enterprise dashboard readability.
"""
import os
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QApplication

FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "fonts")


class FontSystem:
    _initialized = False

    @classmethod
    def initialize(cls, app: QApplication):
        if cls._initialized:
            return

        # Register local font files if present
        if os.path.exists(FONTS_DIR):
            for file in os.listdir(FONTS_DIR):
                if file.endswith((".ttf", ".otf")):
                    QFontDatabase.addApplicationFont(os.path.join(FONTS_DIR, file))

        # Base Application Font: Segoe UI Variable Text (Windows 11 modern) -> Segoe UI -> Inter
        base_font = QFont()
        available = QFontDatabase.families()

        if "Segoe UI Variable Text" in available:
            base_font.setFamily("Segoe UI Variable Text")
        elif "Segoe UI" in available:
            base_font.setFamily("Segoe UI")
        elif "Inter" in available:
            base_font.setFamily("Inter")
        else:
            base_font.setFamily("sans-serif")

        base_font.setPointSize(10)
        base_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias | QFont.StyleStrategy.PreferQuality)
        app.setFont(base_font)

        cls._initialized = True

    @staticmethod
    def get_display_font(size: int = 16, weight: QFont.Weight = QFont.Weight.Bold) -> QFont:
        """For large headings, section titles, and modal headers."""
        font = QFont()
        available = QFontDatabase.families()
        if "Segoe UI Variable Display" in available:
            font.setFamily("Segoe UI Variable Display")
        elif "Bahnschrift" in available:
            font.setFamily("Bahnschrift")
        else:
            font.setFamily("Segoe UI")
        font.setPointSize(size)
        font.setWeight(weight)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias | QFont.StyleStrategy.PreferQuality)
        return font

    @staticmethod
    def get_mono_font(size: int = 11, weight: QFont.Weight = QFont.Weight.Normal) -> QFont:
        """For numeric metrics, IP addresses, latencies, and logs."""
        font = QFont()
        available = QFontDatabase.families()
        if "JetBrains Mono" in available:
            font.setFamily("JetBrains Mono")
        elif "Cascadia Code" in available:
            font.setFamily("Cascadia Code")
        elif "Consolas" in available:
            font.setFamily("Consolas")
        else:
            font.setFamily("monospace")
        font.setPointSize(size)
        font.setWeight(weight)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias | QFont.StyleStrategy.PreferQuality)
        return font

    @staticmethod
    def get_badge_font(size: int = 9, weight: QFont.Weight = QFont.Weight.DemiBold) -> QFont:
        """For tracked uppercase micro-badges and indicators."""
        font = QFont()
        available = QFontDatabase.families()
        if "Bahnschrift" in available:
            font.setFamily("Bahnschrift")
        elif "Segoe UI Variable Small" in available:
            font.setFamily("Segoe UI Variable Small")
        else:
            font.setFamily("Segoe UI")
        font.setPointSize(size)
        font.setWeight(weight)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.2)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias | QFont.StyleStrategy.PreferQuality)
        return font

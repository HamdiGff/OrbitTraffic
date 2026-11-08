"""
OrbitTraffic — Main Entry Point
Launches the ultra-modern enterprise GUI application with FontSystem initialization.
"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt
import qasync

from gui.typography import FontSystem
from gui.app import MainWindow
from utils.logger import get_logger

logger = get_logger("main")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("OrbitTraffic")
    app.setApplicationVersion("2.4.0")
    app.setOrganizationName("OrbitTraffic")

    # Set modern clean style
    app.setStyle("Fusion")

    # Initialize typography & font system
    FontSystem.initialize(app)

    # Sleek obsidian splash screen
    splash_pix = QPixmap(420, 220)
    splash_pix.fill(QColor("#080A0F"))

    painter = QPainter(splash_pix)
    painter.setPen(QColor("#818CF8"))
    painter.setFont(FontSystem.get_display_font(28))
    painter.drawText(40, 90, "⬡ ORBITTRAFFIC")

    painter.setPen(QColor("#64748B"))
    painter.setFont(FontSystem.get_badge_font(9))
    painter.drawText(42, 120, "ORGANIC TRAFFIC INTELLIGENCE PLATFORM v2.4")

    painter.setPen(QColor("#38BDF8"))
    painter.setFont(FontSystem.get_mono_font(10))
    painter.drawText(42, 175, "Initializing stealth contexts & font engine...")
    painter.end()

    splash = QSplashScreen(splash_pix, Qt.WindowType.WindowStaysOnTopHint)
    splash.show()
    app.processEvents()

    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        window = MainWindow()
        window.show()
        splash.finish(window)
        logger.info("OrbitTraffic Enterprise v2.4 initialized with high-DPI typography.")
        loop.run_forever()


if __name__ == "__main__":
    main()

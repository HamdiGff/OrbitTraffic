"""
OrbitTraffic — Main Entry Point
Launch the GUI application with async support.
"""
import sys
import os
import asyncio

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QTimer
import qasync

from gui.app import MainWindow
from utils.logger import get_logger

logger = get_logger("main")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("OrbitTraffic")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("OrbitTraffic")

    # Apply base font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Splash screen
    splash_pix = QPixmap(400, 200)
    splash_pix.fill(Qt.GlobalColor.transparent)
    splash = QSplashScreen(splash_pix, Qt.WindowType.WindowStaysOnTopHint)
    splash.show()
    splash.showMessage(
        "🚀 Starting OrbitTraffic...",
        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
        Qt.GlobalColor.white,
    )
    app.processEvents()

    # Async event loop integration
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        window = MainWindow()
        window.show()
        splash.finish(window)
        logger.info("OrbitTraffic started successfully")
        loop.run_forever()


if __name__ == "__main__":
    main()

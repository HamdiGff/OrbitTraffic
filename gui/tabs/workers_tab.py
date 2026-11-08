"""
Live Worker Matrix & Thread Inspector Tab
Displays real-time slots for active browser automation workers:
- Current Target Website & Search Query
- Simulated Behavioral Step (Typing, Scrolling, Pogo-Sticking, Dwell)
- Live Dwell Progress Bar
- Active Proxy IP & Country Flag
- Memory & CPU footprint
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QProgressBar, QScrollArea,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor


class WorkerSlotCard(QFrame):
    def __init__(self, slot_id: int):
        super().__init__()
        self.slot_id = slot_id
        self.setObjectName("surfaceCard")
        self.setFixedHeight(150)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        # Header
        top = QHBoxLayout()
        self.id_lbl = QLabel(f"⚡ WORKER SLOT #{self.slot_id}")
        self.id_lbl.setStyleSheet("color: #FFFFFF; font-size: 12px; font-weight: 700;")
        top.addWidget(self.id_lbl)
        top.addStretch()

        self.status_pill = QLabel("IDLE")
        self.status_pill.setStyleSheet("""
            background: #1E293B;
            color: #94A3B8;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
        """)
        top.addWidget(self.status_pill)
        layout.addLayout(top)

        # Target & Query
        self.target_lbl = QLabel("Target: Ready for next campaign batch")
        self.target_lbl.setStyleSheet("color: #94A3B8; font-size: 11px;")
        layout.addWidget(self.target_lbl)

        # Action description
        self.action_lbl = QLabel("Action: Standby")
        self.action_lbl.setStyleSheet("color: #38BDF8; font-size: 11px; font-weight: 600;")
        layout.addWidget(self.action_lbl)

        # Dwell progress
        self.dwell_bar = QProgressBar()
        self.dwell_bar.setFixedHeight(5)
        self.dwell_bar.setTextVisible(False)
        self.dwell_bar.setValue(0)
        layout.addWidget(self.dwell_bar)

        # Footer meta
        meta_h = QHBoxLayout()
        self.proxy_meta = QLabel("Proxy: Direct connection")
        self.proxy_meta.setStyleSheet("color: #64748B; font-size: 10px;")
        self.runtime_meta = QLabel("Dwell: 0s")
        self.runtime_meta.setStyleSheet("color: #64748B; font-size: 10px;")
        meta_h.addWidget(self.proxy_meta)
        meta_h.addStretch()
        meta_h.addWidget(self.runtime_meta)
        layout.addLayout(meta_h)

    def set_active(self, target: str, action: str, proxy: str = "Direct", progress: int = 50, dwell_sec: int = 45):
        self.status_pill.setText("EXECUTING")
        self.status_pill.setStyleSheet("""
            background: #064E3B;
            color: #34D399;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
        """)
        self.target_lbl.setText(f"Target: {target[:50]}")
        self.action_lbl.setText(f"Action: {action}")
        self.proxy_meta.setText(f"Proxy: {proxy}")
        self.dwell_bar.setValue(progress)
        self.runtime_meta.setText(f"Dwell: {dwell_sec}s")

    def set_idle(self):
        self.status_pill.setText("IDLE")
        self.status_pill.setStyleSheet("""
            background: #1E293B;
            color: #94A3B8;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
        """)
        self.action_lbl.setText("Action: Standby")
        self.dwell_bar.setValue(0)


class WorkersTab(QWidget):
    def __init__(self):
        super().__init__()
        self.slots = []
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(14)

        header_v = QVBoxLayout()
        title = QLabel("🛰️ Live Worker Matrix & Thread Inspector")
        title.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: 700;")
        subtitle = QLabel("Real-time inspection of active concurrent browser workers and their current behavioral state.")
        subtitle.setStyleSheet("color: #94A3B8; font-size: 12px;")
        header_v.addWidget(title)
        header_v.addWidget(subtitle)
        main_layout.addLayout(header_v)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        grid = QGridLayout(content)
        grid.setSpacing(14)

        # Create 6 visual worker slots
        for i in range(6):
            slot = WorkerSlotCard(i + 1)
            self.slots.append(slot)
            grid.addWidget(slot, i // 2, i % 2)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def update_worker_state(self, worker_id: int, target: str, action: str, proxy: str = "Direct"):
        if 1 <= worker_id <= len(self.slots):
            self.slots[worker_id - 1].set_active(target, action, proxy)

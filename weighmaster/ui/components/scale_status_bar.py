"""Bottom status bar — always visible, shows scale, user, and clock."""
from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from weighmaster.database.models import User
from weighmaster.i18n.translator import t


class ScaleStatusBar(QWidget):
    def __init__(self, user: User, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("StatusBar")
        self.setFixedHeight(32)
        self._user = user
        self._build_ui()

        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._tick)
        self._clock_timer.start(1000)
        self._tick()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(0)

        self._scale_label = QLabel("✗ " + t("scale_offline"))
        self._scale_label.setObjectName("ScaleOffline")
        layout.addWidget(self._scale_label)

        layout.addStretch()

        role_str = "Admin" if self._user.role == "admin" else "Operator"
        user_label = QLabel(f"{self._user.full_name}  ·  {role_str}")
        user_label.setObjectName("StatusBarLabel")
        user_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(user_label)

        layout.addStretch()

        self._clock_label = QLabel()
        self._clock_label.setObjectName("StatusBarClock")
        self._clock_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self._clock_label)

    def _tick(self) -> None:
        now = datetime.now()
        self._clock_label.setText(now.strftime("%a %d %b %Y  %H:%M:%S"))

    def set_connected(self, port: str, baud: int = 9600) -> None:
        self._scale_label.setObjectName("ScaleOnline")
        self._scale_label.setText(f"● {t('scale_online')} · {port} · {baud} baud")
        self._scale_label.style().unpolish(self._scale_label)
        self._scale_label.style().polish(self._scale_label)

    def set_disconnected(self) -> None:
        self._scale_label.setObjectName("ScaleOffline")
        self._scale_label.setText(f"✗ {t('scale_offline')}")
        self._scale_label.style().unpolish(self._scale_label)
        self._scale_label.style().polish(self._scale_label)

    def set_message(self, text: str) -> None:
        """Temporary status message (clears scale text). Pass empty string to restore."""
        if text:
            self._scale_label.setText(text)
            self._scale_label.setStyleSheet("color: #B45309; font-weight: 600;")
        else:
            self._scale_label.setStyleSheet("")
            self._scale_label.style().unpolish(self._scale_label)
            self._scale_label.style().polish(self._scale_label)

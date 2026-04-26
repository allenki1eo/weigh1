"""KpiCard widget — used in dashboards."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout


class KpiCard(QFrame):
    def __init__(self, label: str, value: str, icon: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self.setMinimumHeight(92)
        self._build_ui(label, value, icon)

    def _build_ui(self, label: str, value: str, icon: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(3)

        top = QHBoxLayout()
        if icon:
            icon_lbl = QLabel(icon)
            icon_lbl.setObjectName("KpiIcon")
            top.addWidget(icon_lbl)
        top.addStretch()
        layout.addLayout(top)

        layout.addStretch()

        self._value_label = QLabel(value)
        self._value_label.setObjectName("KpiValue")
        layout.addWidget(self._value_label)

        self._label_label = QLabel(label)
        self._label_label.setObjectName("KpiLabel")
        layout.addWidget(self._label_label)

    def set_value(self, value: str) -> None:
        self._value_label.setText(value)

    def set_label(self, label: str) -> None:
        self._label_label.setText(label)

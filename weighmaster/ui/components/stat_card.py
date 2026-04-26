"""Modern KPI card with icon badge."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout


# Icon → color mapping for visual variety
KPI_COLORS = {
    "TK": ("#4F46E5", "#EEF2FF"),   # Indigo
    "NT": ("#10B981", "#D1FAE5"),   # Green
    "PD": ("#F59E0B", "#FEF3C7"),   # Amber
    "SC": ("#6B7280", "#F3F4F6"),   # Gray
    "VD": ("#EF4444", "#FEE2E2"),   # Red
    "WT": ("#8B5CF6", "#EDE9FE"),   # Purple
    "MT": ("#14B8A6", "#CCFBF1"),   # Teal
    "WC": ("#8B5CF6", "#EDE9FE"),   # Purple
    "MC": ("#14B8A6", "#CCFBF1"),   # Teal
}

ICON_SYMBOLS = {
    "TK": "⊕",
    "NT": "⚖",
    "PD": "◎",
    "SC": "◎",
    "VD": "✕",
    "WT": "W",
    "MT": "M",
    "WC": "W",
    "MC": "M",
}


class KpiCard(QFrame):
    """A modern KPI card with colored icon badge, large value, and label."""

    def __init__(self, label: str, value: str, icon: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("KpiCard")
        self.setMinimumHeight(100)
        self._icon_key = icon
        self._build_ui(label, value, icon)

    def _build_ui(self, label: str, value: str, icon: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(6)

        # Top row: icon badge + context menu placeholder
        top = QHBoxLayout()
        top.setSpacing(0)

        color, bg = KPI_COLORS.get(icon, ("#4F46E5", "#EEF2FF"))
        symbol = ICON_SYMBOLS.get(icon, "•")

        icon_lbl = QLabel(symbol)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setFixedSize(36, 36)
        icon_lbl.setStyleSheet(
            f"background-color: {bg}; color: {color}; "
            f"border-radius: 10px; font-size: 16px; font-weight: 700;"
        )
        top.addWidget(icon_lbl)
        top.addStretch()
        layout.addLayout(top)

        # Value
        self._value_label = QLabel(value)
        self._value_label.setObjectName("KpiValue")
        layout.addWidget(self._value_label)

        # Label
        self._label_label = QLabel(label)
        self._label_label.setObjectName("KpiLabel")
        layout.addWidget(self._label_label)

    def set_value(self, value: str) -> None:
        self._value_label.setText(value)

    def set_label(self, label: str) -> None:
        self._label_label.setText(label)

"""KPI card with colored left accent strip — cargo-dashboard style."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget,
)


KPI_COLORS = {
    "TK": ("#4F46E5", "#EEF2FF"),   # Indigo
    "NT": ("#16A34A", "#DCFCE7"),   # Green
    "PD": ("#D97706", "#FEF3C7"),   # Amber
    "SC": ("#475569", "#F1F5F9"),   # Slate
    "VD": ("#DC2626", "#FEE2E2"),   # Red
    "WT": ("#7C3AED", "#EDE9FE"),   # Purple
    "MT": ("#0D9488", "#CCFBF1"),   # Teal
    "WC": ("#7C3AED", "#EDE9FE"),   # Purple
    "MC": ("#0D9488", "#CCFBF1"),   # Teal
}

ICON_SYMBOLS = {
    "TK": "⊕",
    "NT": "⚖",
    "PD": "◎",
    "SC": "▣",
    "VD": "✕",
    "WT": "W",
    "MT": "M",
    "WC": "W",
    "MC": "M",
}


class KpiCard(QFrame):
    """KPI card with a colored left accent border and icon badge."""

    def __init__(self, label: str, value: str, icon: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("KpiCard")
        self.setMinimumHeight(88)
        self._icon_key = icon
        self._color, self._bg = KPI_COLORS.get(icon, ("#4F46E5", "#EEF2FF"))
        self._build_ui(label, value, icon)
        self._apply_accent()

    def _apply_accent(self) -> None:
        self.setStyleSheet(f"""
            QFrame#KpiCard {{
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-left: 3px solid {self._color};
                border-radius: 2px 10px 10px 2px;
            }}
        """)

    def _build_ui(self, label: str, value: str, icon: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        top = QHBoxLayout()
        top.setSpacing(0)

        symbol = ICON_SYMBOLS.get(icon, "•")
        icon_lbl = QLabel(symbol)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setFixedSize(30, 30)
        icon_lbl.setStyleSheet(
            f"background-color: {self._bg}; color: {self._color}; "
            f"border-radius: 8px; font-size: 14px; font-weight: 700;"
        )
        top.addWidget(icon_lbl)
        top.addStretch()
        layout.addLayout(top)

        layout.addSpacing(4)

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

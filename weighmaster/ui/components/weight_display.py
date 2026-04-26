"""WeightDisplayWidget — modern live weight hero panel."""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from weighmaster.i18n.translator import t
from weighmaster.utils.helpers import format_weight


class WeightDisplayWidget(QFrame):
    """Shows live weight, stability chip, and sub-weight breakdown."""

    def __init__(self, compact: bool = False, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self._compact = compact
        self._weight = 0.0
        self._is_stable = False
        self._status = "unstable"
        self._tare: float | None = None
        self._gross: float | None = None
        self._net: float | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)

        # Header row: title + status chip
        header = QHBoxLayout()
        header.setSpacing(8)

        title = QLabel(t("live_weight"))
        title.setObjectName("SectionTitle")
        header.addWidget(title)
        header.addStretch()

        self._chip = QLabel(t("status_unstable"))
        self._chip.setObjectName("ChipUnstable")
        header.addWidget(self._chip)
        layout.addLayout(header)

        # Main weight hero
        hero_row = QHBoxLayout()
        hero_row.setSpacing(10)
        hero_row.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        font_size = "36" if self._compact else "56"
        self._weight_label = QLabel("0.00")
        self._weight_label.setObjectName("WeightHero")
        if self._compact:
            self._weight_label.setStyleSheet("font-size: 36px; letter-spacing: -1px;")
        else:
            self._weight_label.setStyleSheet("font-size: 56px; letter-spacing: -2px;")
        hero_row.addWidget(self._weight_label)

        self._unit_label = QLabel("kg")
        self._unit_label.setObjectName("WeightUnit")
        self._unit_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self._unit_label.setStyleSheet("padding-bottom: 10px;")
        hero_row.addWidget(self._unit_label)
        hero_row.addStretch()
        layout.addLayout(hero_row)

        # Divider
        divider = QWidget()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: #E5E7EB;")
        layout.addWidget(divider)

        # Sub weights row (tare / gross / net)
        self._sub_frame = QWidget()
        sub_layout = QHBoxLayout(self._sub_frame)
        sub_layout.setContentsMargins(0, 4, 0, 0)
        sub_layout.setSpacing(32)

        self._tare_label = self._make_sub(t("tare_weight"), "—")
        self._gross_label = self._make_sub(t("gross_weight"), "—")
        self._net_label = self._make_sub(t("net_weight"), "—")

        sub_layout.addWidget(self._tare_label)
        sub_layout.addWidget(self._gross_label)
        sub_layout.addWidget(self._net_label)
        sub_layout.addStretch()
        layout.addWidget(self._sub_frame)

    def _make_sub(self, title: str, value: str) -> QWidget:
        w = QWidget()
        vl = QVBoxLayout(w)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(2)
        lbl_title = QLabel(title)
        lbl_title.setObjectName("KpiLabel")
        lbl_val = QLabel(value)
        lbl_val.setObjectName("SubWeight")
        vl.addWidget(lbl_title)
        vl.addWidget(lbl_val)
        w._val_label = lbl_val
        return w

    def update_weight(self, weight_kg: float, is_stable: bool, status: str) -> None:
        self._weight = weight_kg
        self._is_stable = is_stable
        self._status = status

        self._weight_label.setText(format_weight(weight_kg))

        if status == "overload":
            self._weight_label.setProperty("overload", "true")
            self._weight_label.setProperty("stable", "false")
            self._chip.setObjectName("ChipOverload")
            self._chip.setText(t("status_overload"))
        elif is_stable:
            self._weight_label.setProperty("stable", "true")
            self._weight_label.setProperty("overload", "false")
            self._chip.setObjectName("ChipStable")
            self._chip.setText(t("status_stable"))
        else:
            self._weight_label.setProperty("stable", "false")
            self._weight_label.setProperty("overload", "false")
            self._chip.setObjectName("ChipUnstable")
            self._chip.setText(t("status_unstable"))

        # Force QSS refresh
        for widget in [self._weight_label, self._chip]:
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def set_tare(self, kg: float | None) -> None:
        self._tare = kg
        self._tare_label._val_label.setText(f"{format_weight(kg)} kg" if kg is not None else "—")

    def set_gross(self, kg: float | None) -> None:
        self._gross = kg
        self._gross_label._val_label.setText(f"{format_weight(kg)} kg" if kg is not None else "—")

    def set_net(self, kg: float | None) -> None:
        self._net = kg
        self._net_label._val_label.setText(f"{format_weight(kg)} kg" if kg is not None else "—")

    @property
    def current_weight(self) -> float:
        return self._weight

    @property
    def is_stable(self) -> bool:
        return self._is_stable

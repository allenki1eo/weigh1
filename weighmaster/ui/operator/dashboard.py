"""Operator dashboard — live weight hero + today's KPIs."""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QVBoxLayout, QWidget,
)

from weighmaster.database.models import User
from weighmaster.i18n.translator import t
from weighmaster.services.weighing_service import get_todays_kpis, get_pending_tickets
from weighmaster.ui.components.stat_card import KpiCard
from weighmaster.ui.components.weight_display import WeightDisplayWidget
from weighmaster.utils.helpers import format_weight


class OperatorDashboard(QWidget):
    new_ticket_requested = pyqtSignal()
    pending_requested = pyqtSignal()

    def __init__(self, user: User, parent=None) -> None:
        super().__init__(parent)
        self._user = user
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        main = QVBoxLayout(container)
        main.setContentsMargins(24, 20, 24, 24)
        main.setSpacing(16)

        # Page header
        header_row = QHBoxLayout()
        title = QLabel(t("dashboard"))
        title.setObjectName("PageTitle")
        header_row.addWidget(title)
        header_row.addStretch()
        new_btn = QPushButton(t("new_ticket") + "  [F2]")
        new_btn.setObjectName("BtnCapture")
        new_btn.clicked.connect(self.new_ticket_requested)
        header_row.addWidget(new_btn)
        main.addLayout(header_row)

        # KPI row
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(12)
        self._kpi_tickets = KpiCard(t("today_tickets"), "0", "TK")
        self._kpi_weight = KpiCard(t("total_net_weight"), "0.00 t", "NT")
        self._kpi_pending = KpiCard(t("awaiting_step2"), "0", "PD")
        self._kpi_scale = KpiCard(t("scale_status"), "—", "SC")
        for card in [self._kpi_tickets, self._kpi_weight, self._kpi_pending, self._kpi_scale]:
            kpi_row.addWidget(card, 1)
        main.addLayout(kpi_row)

        # Content row
        content = QHBoxLayout()
        content.setSpacing(16)

        # Weight display (2/3)
        self._weight_display = WeightDisplayWidget()
        content.addWidget(self._weight_display, 2)

        # Active ticket / quick panel (1/3)
        self._ticket_panel = self._build_ticket_panel()
        content.addWidget(self._ticket_panel, 1)

        main.addLayout(content, 1)
        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _build_ticket_panel(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        header = QLabel(t("awaiting_step2"))
        header.setObjectName("SectionTitle")
        layout.addWidget(header)

        self._pending_info = QLabel(t("no_pending"))
        self._pending_info.setObjectName("KpiLabel")
        self._pending_info.setWordWrap(True)
        layout.addWidget(self._pending_info)

        self._goto_pending_btn = QPushButton(t("pending_step2") + " [F3]")
        self._goto_pending_btn.setObjectName("BtnSecondary")
        self._goto_pending_btn.clicked.connect(self.pending_requested)
        layout.addWidget(self._goto_pending_btn)

        layout.addStretch()
        return frame

    def refresh(self) -> None:
        try:
            kpis = get_todays_kpis(
                operator_id=self._user.id if self._user.role == "operator" else None
            )
            self._kpi_tickets.set_value(str(kpis["total_tickets"]))
            self._kpi_weight.set_value(f"{kpis['net_weight_kg'] / 1000:,.2f} t")
            self._kpi_pending.set_value(str(kpis["pending_count"]))

            pending = get_pending_tickets()
            if pending:
                self._pending_info.setText(
                    f"{len(pending)} vehicle(s) waiting\nOldest: {pending[0].vehicle_plate}"
                )
            else:
                self._pending_info.setText(t("no_pending"))
        except Exception as exc:
            pass

    def update_weight(self, weight_kg: float, is_stable: bool, status: str) -> None:
        self._weight_display.update_weight(weight_kg, is_stable, status)
        chip = t("status_stable") if is_stable else t("status_unstable")
        if status == "overload":
            chip = t("status_overload")
        self._kpi_scale.set_value(chip)

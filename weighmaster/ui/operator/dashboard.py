"""Operator dashboard — compact header band, live weight hero, KPI cards."""
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


class OperatorDashboard(QWidget):
    new_ticket_requested = pyqtSignal()
    pending_requested = pyqtSignal()

    def __init__(self, user: User, parent=None) -> None:
        super().__init__(parent)
        self._user = user
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Page header band ──────────────────────────────────────────────────
        header_band = QWidget()
        header_band.setObjectName("PageHeaderBand")
        hb = QHBoxLayout(header_band)
        hb.setContentsMargins(24, 0, 20, 0)
        hb.setSpacing(10)

        title = QLabel(t("dashboard"))
        title.setObjectName("PageTitle")
        hb.addWidget(title)

        hb.addSpacing(8)
        dot = QLabel("·")
        dot.setStyleSheet("color: #CBD5E1; font-size: 16px; background: transparent;")
        hb.addWidget(dot)

        self._scale_mini = QLabel("○  Scale Offline")
        self._scale_mini.setStyleSheet(
            "font-size: 12px; color: #94A3B8; background: transparent; font-weight: 500;"
        )
        hb.addWidget(self._scale_mini)
        hb.addStretch()

        new_btn = QPushButton("+  " + t("new_ticket"))
        new_btn.setObjectName("BtnPrimary")
        new_btn.clicked.connect(self.new_ticket_requested)
        hb.addWidget(new_btn)
        outer.addWidget(header_band)

        # ── Scrollable content ────────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        main = QVBoxLayout(container)
        main.setContentsMargins(20, 16, 20, 20)
        main.setSpacing(14)

        # KPI row
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(12)
        self._kpi_tickets = KpiCard(t("today_tickets"),    "0",       "TK")
        self._kpi_weight  = KpiCard(t("total_net_weight"), "0.00 t",  "NT")
        self._kpi_pending = KpiCard(t("awaiting_step2"),   "0",       "PD")
        self._kpi_scale   = KpiCard(t("scale_status"),     "—",       "SC")
        for card in [self._kpi_tickets, self._kpi_weight,
                     self._kpi_pending, self._kpi_scale]:
            kpi_row.addWidget(card, 1)
        main.addLayout(kpi_row)

        # Content row: weight display + ticket panel
        content = QHBoxLayout()
        content.setSpacing(14)

        self._weight_display = WeightDisplayWidget()
        content.addWidget(self._weight_display, 2)

        self._ticket_panel = self._build_ticket_panel()
        content.addWidget(self._ticket_panel, 1)

        main.addLayout(content, 1)
        scroll.setWidget(container)
        outer.addWidget(scroll, 1)

    def _build_ticket_panel(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        h = QHBoxLayout()
        h.setSpacing(8)
        header = QLabel(t("awaiting_step2"))
        header.setObjectName("SectionTitle")
        h.addWidget(header)
        h.addStretch()

        self._pending_badge = QLabel("0")
        self._pending_badge.setStyleSheet(
            "background-color: #D97706; color: white; border-radius: 4px; "
            "padding: 2px 8px; font-size: 10px; font-weight: 700;"
        )
        self._pending_badge.hide()
        h.addWidget(self._pending_badge)
        layout.addLayout(h)

        # Divider
        div = QWidget()
        div.setFixedHeight(1)
        div.setStyleSheet("background: #E2E8F0;")
        layout.addWidget(div)

        self._pending_info = QLabel(t("no_pending"))
        self._pending_info.setObjectName("KpiLabel")
        self._pending_info.setWordWrap(True)
        self._pending_info.setStyleSheet(
            "font-size: 12px; color: #64748B; background: transparent; padding: 4px 0;"
        )
        layout.addWidget(self._pending_info)

        self._goto_pending_btn = QPushButton(t("pending_step2") + "  →")
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
            count = len(pending)
            if count > 0:
                self._pending_info.setText(
                    f"{count} vehicle(s) waiting\nOldest: {pending[0].vehicle_plate}"
                )
                self._pending_badge.setText(str(count))
                self._pending_badge.show()
            else:
                self._pending_info.setText(t("no_pending"))
                self._pending_badge.hide()
        except Exception:
            pass

    def update_weight(self, weight_kg: float, is_stable: bool, status: str) -> None:
        self._weight_display.update_weight(weight_kg, is_stable, status)
        chip = t("status_stable") if is_stable else t("status_unstable")
        if status == "overload":
            chip = t("status_overload")
        self._kpi_scale.set_value(chip)

        if status == "overload":
            self._scale_mini.setText("●  Overload")
            self._scale_mini.setStyleSheet(
                "font-size: 12px; color: #DC2626; background: transparent; font-weight: 600;"
            )
        elif is_stable:
            self._scale_mini.setText("●  Scale Stable")
            self._scale_mini.setStyleSheet(
                "font-size: 12px; color: #16A34A; background: transparent; font-weight: 600;"
            )
        else:
            self._scale_mini.setText("●  Scale Active")
            self._scale_mini.setStyleSheet(
                "font-size: 12px; color: #D97706; background: transparent; font-weight: 600;"
            )

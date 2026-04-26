"""TicketTableWidget — reusable table for displaying weigh tickets."""
from __future__ import annotations

from typing import Callable, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout, QHeaderView, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QWidget,
)

from weighmaster.i18n.translator import t
from weighmaster.services.weighing_service import TicketSummary
from weighmaster.utils.helpers import format_datetime, format_weight


class TicketTableWidget(QTableWidget):
    reprint_requested = pyqtSignal(int)   # ticket_id
    void_requested = pyqtSignal(int)      # ticket_id
    continue_requested = pyqtSignal(int)  # ticket_id (step 2)

    _COLUMNS = [
        ("ticket_number", t("ticket_number")),
        ("vehicle_plate", t("vehicle_plate")),
        ("commodity_name", t("commodity")),
        ("tare_weight", t("tare_weight")),
        ("gross_weight", t("gross_weight")),
        ("net_weight", t("net_weight")),
        ("created_at", t("date_time")),
        ("status", t("status")),
        ("actions", ""),
    ]

    def __init__(
        self,
        show_actions: bool = True,
        can_void: bool = False,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("TableWidget")
        self._show_actions = show_actions
        self._can_void = can_void
        self._setup()

    def _setup(self) -> None:
        cols = self._COLUMNS if self._show_actions else self._COLUMNS[:-1]
        self.setColumnCount(len(cols))
        self.setHorizontalHeaderLabels([c[1] for c in cols])
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(self.SelectionBehavior.SelectRows)
        self.setEditTriggers(self.EditTrigger.NoEditTriggers)
        self.setShowGrid(False)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.setMinimumHeight(200)

    def load_tickets(self, tickets: list[TicketSummary]) -> None:
        self.setRowCount(0)
        for ticket in tickets:
            row = self.rowCount()
            self.insertRow(row)
            self._fill_row(row, ticket)

    def _fill_row(self, row: int, ticket: TicketSummary) -> None:
        cols = self._COLUMNS if self._show_actions else self._COLUMNS[:-1]
        for col_idx, (field, _) in enumerate(cols):
            if field == "actions":
                self._add_action_cell(row, col_idx, ticket)
                continue
            if field == "status":
                self._add_status_cell(row, col_idx, ticket)
                continue

            val = getattr(ticket, field, None)
            if field in ("tare_weight", "gross_weight", "net_weight"):
                text = f"{format_weight(val)} kg" if val is not None else "—"
            elif field == "created_at":
                text = format_datetime(val)
            else:
                text = str(val) if val is not None else "—"

            item = QTableWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, ticket.id)
            if ticket.is_void:
                item.setForeground(Qt.GlobalColor.gray)
            self.setItem(row, col_idx, item)

    def _add_status_cell(self, row: int, col_idx: int, ticket: TicketSummary) -> None:
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(8, 4, 8, 4)

        if ticket.is_void:
            chip = QLabel(t("void").upper())
            chip.setObjectName("ChipVoid")
        elif ticket.status == "complete":
            chip = QLabel(t("complete").upper())
            chip.setObjectName("ChipComplete")
        elif ticket.status == "gross_captured":
            chip = QLabel(t("awaiting_tare").upper())
            chip.setObjectName("ChipPending")
        else:
            chip = QLabel(t("awaiting_gross").upper())
            chip.setObjectName("ChipPending")

        layout.addWidget(chip)
        layout.addStretch()
        self.setCellWidget(row, col_idx, w)

    def _add_action_cell(self, row: int, col_idx: int, ticket: TicketSummary) -> None:
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        if ticket.status == "complete" and not ticket.is_void:
            reprint_btn = QPushButton(t("reprint"))
            reprint_btn.setObjectName("BtnSmall")
            reprint_btn.clicked.connect(lambda _, tid=ticket.id: self.reprint_requested.emit(tid))
            layout.addWidget(reprint_btn)

            if self._can_void:
                void_btn = QPushButton(t("void_ticket"))
                void_btn.setObjectName("BtnMiniDanger")
                void_btn.clicked.connect(lambda _, tid=ticket.id: self.void_requested.emit(tid))
                layout.addWidget(void_btn)

        elif ticket.status in ("tare_captured", "gross_captured") and not ticket.is_void:
            cont_btn = QPushButton(t("continue"))
            cont_btn.setObjectName("BtnMiniPrimary")
            cont_btn.clicked.connect(lambda _, tid=ticket.id: self.continue_requested.emit(tid))
            layout.addWidget(cont_btn)

        layout.addStretch()
        self.setCellWidget(row, col_idx, w)

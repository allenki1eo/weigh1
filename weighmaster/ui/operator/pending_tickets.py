"""Pending Step 2 screen — tickets awaiting gross weight."""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from weighmaster.database.models import User
from weighmaster.i18n.translator import t
from weighmaster.services.weighing_service import get_pending_tickets
from weighmaster.utils.helpers import format_datetime, format_wait_time, format_weight


class PendingTicketsScreen(QWidget):
    open_step2 = pyqtSignal(int)

    def __init__(self, user: User, parent=None) -> None:
        super().__init__(parent)
        self._user = user
        self._tickets = []
        self._build_ui()

    def _build_ui(self) -> None:
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 20, 24, 20)
        main.setSpacing(16)

        header_row = QHBoxLayout()
        title = QLabel(t("pending_step2"))
        title.setObjectName("PageTitle")
        header_row.addWidget(title)
        header_row.addStretch()

        self._search = QLineEdit()
        self._search.setPlaceholderText(t("search"))
        self._search.setFixedWidth(240)
        self._search.textChanged.connect(self._filter)
        header_row.addWidget(self._search)
        main.addLayout(header_row)

        # Table
        self._table = QTableWidget()
        self._table.setObjectName("TableWidget")
        cols = [
            t("ticket_number"),
            t("vehicle_plate"),
            t("driver_name"),
            t("commodity"),
            t("direction"),
            t("stage"),
            t("first_weight"),
            t("date_time"),
            t("wait_time"),
            "",
        ]
        self._table.setColumnCount(len(cols))
        self._table.setHorizontalHeaderLabels(cols)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setShowGrid(False)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        main.addWidget(self._table, 1)

        self._empty_lbl = QLabel(t("no_pending"))
        self._empty_lbl.setObjectName("KpiLabel")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_lbl.hide()
        main.addWidget(self._empty_lbl)

    def refresh(self) -> None:
        self._tickets = get_pending_tickets()
        self._render(self._tickets)

    def _filter(self, text: str) -> None:
        query = text.strip().upper()
        filtered = [t for t in self._tickets if query in t.vehicle_plate.upper()] if query else self._tickets
        self._render(filtered)

    def _render(self, tickets) -> None:
        self._table.setRowCount(0)
        if not tickets:
            self._empty_lbl.show()
            return
        self._empty_lbl.hide()

        for ticket in tickets:
            row = self._table.rowCount()
            self._table.insertRow(row)
            values = [
                ticket.ticket_number,
                ticket.vehicle_plate,
                ticket.driver_name,
                ticket.commodity_name,
                t("gross_first") if ticket.weighing_mode == "gross_first" else t("tare_first"),
                t("awaiting_tare") if ticket.pending_stage == "awaiting_tare" else t("awaiting_gross"),
                f"{format_weight(ticket.gross_weight if ticket.pending_stage == 'awaiting_tare' else ticket.tare_weight)} kg",
                format_datetime(ticket.first_capture_datetime),
                format_wait_time(ticket.first_capture_datetime),
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, ticket.id)
                self._table.setItem(row, col, item)

            # Action cell
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 2, 4, 2)
            cont_btn = QPushButton(t("continue"))
            cont_btn.setObjectName("BtnPrimary")
            cont_btn.setFixedHeight(30)
            cont_btn.clicked.connect(lambda _, tid=ticket.id: self.open_step2.emit(tid))
            btn_layout.addWidget(cont_btn)
            btn_layout.addStretch()
            self._table.setCellWidget(row, len(values), btn_widget)

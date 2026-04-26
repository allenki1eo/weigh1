"""Searchable/filterable ticket history screen."""
from __future__ import annotations

from datetime import datetime, date

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QComboBox, QDateEdit, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)
from PyQt6.QtCore import QDate

from weighmaster.database.models import User
from weighmaster.i18n.translator import t
from weighmaster.services.weighing_service import (
    get_ticket_history, void_ticket, reprint_ticket, WeighingError,
)
from weighmaster.ui.components.dialogs import VoidDialog, show_error, show_info
from weighmaster.utils.helpers import format_datetime, format_weight
from weighmaster.config import TABLE_PAGE_SIZE


class TicketHistoryScreen(QWidget):
    def __init__(self, user: User, parent=None) -> None:
        super().__init__(parent)
        self._user = user
        self._offset = 0
        self._total = 0
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.timeout.connect(self._load)
        self._build_ui()

    def _build_ui(self) -> None:
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 20, 24, 20)
        main.setSpacing(12)

        title = QLabel(t("ticket_history"))
        title.setObjectName("PageTitle")
        main.addWidget(title)

        # Filter bar
        filter_frame = QFrame()
        filter_frame.setObjectName("Card")
        fl = QHBoxLayout(filter_frame)
        fl.setContentsMargins(16, 10, 16, 10)
        fl.setSpacing(10)

        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText(t("search"))
        self._search_edit.setFixedWidth(200)
        self._search_edit.textChanged.connect(lambda: self._debounce.start(300))
        fl.addWidget(self._search_edit)

        self._date_from = QDateEdit()
        self._date_from.setDate(QDate.currentDate().addDays(-30))
        self._date_from.setCalendarPopup(True)
        self._date_from.dateChanged.connect(lambda: self._debounce.start(300))
        fl.addWidget(QLabel(t("date_from")))
        fl.addWidget(self._date_from)

        self._date_to = QDateEdit()
        self._date_to.setDate(QDate.currentDate())
        self._date_to.setCalendarPopup(True)
        self._date_to.dateChanged.connect(lambda: self._debounce.start(300))
        fl.addWidget(QLabel(t("date_to")))
        fl.addWidget(self._date_to)

        self._status_combo = QComboBox()
        for key, label in [("all", t("all")), ("complete", t("complete")),
                            ("tare_captured", t("pending_step2")), ("void", t("void"))]:
            self._status_combo.addItem(label, key)
        self._status_combo.currentIndexChanged.connect(lambda: self._debounce.start(100))
        fl.addWidget(self._status_combo)

        fl.addStretch()

        export_btn = QPushButton(t("export_excel"))
        export_btn.setObjectName("BtnSecondary")
        export_btn.clicked.connect(self._export_excel)
        fl.addWidget(export_btn)

        main.addWidget(filter_frame)

        # Table
        self._table = QTableWidget()
        self._table.setObjectName("TableWidget")
        cols = [t("ticket_number"), t("vehicle_plate"), t("commodity"),
                t("tare_weight"), t("gross_weight"), t("net_weight"),
                t("date_time"), t("status"), ""]
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

        # Pagination row
        page_row = QHBoxLayout()
        self._count_lbl = QLabel()
        self._count_lbl.setObjectName("KpiLabel")
        page_row.addWidget(self._count_lbl)
        page_row.addStretch()
        self._prev_btn = QPushButton("← Prev")
        self._prev_btn.setObjectName("BtnSecondary")
        self._prev_btn.clicked.connect(self._prev_page)
        self._next_btn = QPushButton("Next →")
        self._next_btn.setObjectName("BtnSecondary")
        self._next_btn.clicked.connect(self._next_page)
        page_row.addWidget(self._prev_btn)
        page_row.addWidget(self._next_btn)
        main.addLayout(page_row)

    def refresh(self) -> None:
        self._offset = 0
        self._load()

    def _load(self) -> None:
        df = self._date_from.date()
        dt = self._date_to.date()
        date_from = datetime(df.year(), df.month(), df.day())
        date_to = datetime(dt.year(), dt.month(), dt.day(), 23, 59, 59)
        status = self._status_combo.currentData()

        tickets, total = get_ticket_history(
            date_from=date_from,
            date_to=date_to,
            search=self._search_edit.text().strip(),
            status=status,
            operator_id=self._user.id if self._user.role == "operator" else None,
            limit=TABLE_PAGE_SIZE,
            offset=self._offset,
        )
        self._total = total
        self._render(tickets)
        self._count_lbl.setText(
            f"Showing {self._offset + 1}–{min(self._offset + TABLE_PAGE_SIZE, total)} of {total}"
        )
        self._prev_btn.setEnabled(self._offset > 0)
        self._next_btn.setEnabled(self._offset + TABLE_PAGE_SIZE < total)

    def _render(self, tickets) -> None:
        self._table.setRowCount(0)
        for ticket in tickets:
            row = self._table.rowCount()
            self._table.insertRow(row)
            values = [
                ticket.ticket_number,
                ticket.vehicle_plate,
                ticket.commodity_name,
                f"{format_weight(ticket.tare_weight)} kg",
                f"{format_weight(ticket.gross_weight)} kg" if ticket.gross_weight else "—",
                f"{format_weight(ticket.net_weight)} kg" if ticket.net_weight else "—",
                format_datetime(ticket.created_at),
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, ticket.id)
                if ticket.is_void:
                    item.setForeground(Qt.GlobalColor.gray)
                self._table.setItem(row, col, item)

            # Status chip cell
            status_widget = QWidget()
            sl = QHBoxLayout(status_widget)
            sl.setContentsMargins(6, 2, 6, 2)
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
            sl.addWidget(chip)
            sl.addStretch()
            self._table.setCellWidget(row, 7, status_widget)

            # Action buttons
            btn_widget = QWidget()
            bl = QHBoxLayout(btn_widget)
            bl.setContentsMargins(4, 2, 4, 2)
            bl.setSpacing(4)
            if ticket.status == "complete" and not ticket.is_void:
                reprint_btn = QPushButton(t("reprint"))
                reprint_btn.setObjectName("BtnSmall")
                reprint_btn.clicked.connect(lambda _, tid=ticket.id: self._do_reprint(tid))
                bl.addWidget(reprint_btn)
                if self._user.role == "admin":
                    void_btn = QPushButton(t("void_ticket"))
                    void_btn.setObjectName("BtnMiniDanger")
                    void_btn.clicked.connect(
                        lambda _, tid=ticket.id, tno=ticket.ticket_number: self._do_void(tid, tno)
                    )
                    bl.addWidget(void_btn)
            bl.addStretch()
            self._table.setCellWidget(row, 8, btn_widget)

    def _prev_page(self) -> None:
        self._offset = max(0, self._offset - TABLE_PAGE_SIZE)
        self._load()

    def _next_page(self) -> None:
        self._offset += TABLE_PAGE_SIZE
        self._load()

    def _do_reprint(self, ticket_id: int) -> None:
        try:
            import os, subprocess, sys

            out_path = reprint_ticket(self._user, ticket_id)
            if sys.platform == "win32":
                os.startfile(out_path)
            else:
                subprocess.Popen(["xdg-open", out_path])
        except Exception as exc:
            show_error(str(exc), parent=self)

    def _do_void(self, ticket_id: int, ticket_number: str) -> None:
        dlg = VoidDialog(ticket_number, parent=self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            try:
                void_ticket(self._user, ticket_id, dlg.reason)
                show_info("Ticket voided successfully.", parent=self)
                self._load()
            except WeighingError as exc:
                show_error(str(exc), parent=self)

    def _export_excel(self) -> None:
        try:
            from openpyxl import Workbook
            from PyQt6.QtWidgets import QFileDialog
            path, _ = QFileDialog.getSaveFileName(
                self, "Save Excel", "ticket_history.xlsx", "Excel (*.xlsx)"
            )
            if not path:
                return
            df = self._date_from.date()
            dt = self._date_to.date()
            date_from = datetime(df.year(), df.month(), df.day())
            date_to = datetime(dt.year(), dt.month(), dt.day(), 23, 59, 59)
            tickets, _ = get_ticket_history(
                date_from=date_from, date_to=date_to,
                search=self._search_edit.text().strip(),
                limit=99999, offset=0,
            )
            wb = Workbook()
            ws = wb.active
            ws.title = "Ticket History"
            headers = ["Ticket No", "Plate", "Commodity", "Tare (kg)",
                       "Gross (kg)", "Net (kg)", "Date/Time", "Status"]
            ws.append(headers)
            for ticket in tickets:
                ws.append([
                    ticket.ticket_number, ticket.vehicle_plate, ticket.commodity_name,
                    ticket.tare_weight, ticket.gross_weight, ticket.net_weight,
                    format_datetime(ticket.created_at),
                    "VOID" if ticket.is_void else ticket.status,
                ])
            wb.save(path)
            show_info(f"Exported to {path}", parent=self)
        except Exception as exc:
            show_error(str(exc), parent=self)

"""Gate queue board with checkpoint logging."""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from weighmaster.database.models import User
from weighmaster.i18n.translator import t
from weighmaster.services.gate_service import get_gate_queue, log_gate_event
from weighmaster.ui.components.dialogs import show_error, show_info
from weighmaster.utils.helpers import format_datetime, format_wait_time


class GateQueueScreen(QWidget):
    open_step2 = pyqtSignal(int)

    def __init__(self, user: User, parent=None) -> None:
        super().__init__(parent)
        self._user = user
        self._rows: list[dict] = []
        self._selected_ticket_id: int | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 20, 24, 20)
        main.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel(t("gate_queue"))
        title.setObjectName("PageTitle")
        header.addWidget(title)
        header.addStretch()
        self._search = QLineEdit()
        self._search.setPlaceholderText(t("search"))
        self._search.setFixedWidth(240)
        self._search.textChanged.connect(self._filter)
        header.addWidget(self._search)
        main.addLayout(header)

        self._table = QTableWidget()
        self._table.setObjectName("TableWidget")
        cols = [
            t("ticket_number"),
            t("vehicle_plate"),
            t("driver_name"),
            t("direction"),
            t("stage"),
            t("date_time"),
            t("wait_time"),
            t("latest_checkpoint"),
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
        self._table.itemSelectionChanged.connect(self._on_selection_changed)
        main.addWidget(self._table, 1)

        actions = QFrame()
        actions.setObjectName("Card")
        al = QVBoxLayout(actions)
        al.setContentsMargins(14, 10, 14, 10)
        al.setSpacing(8)

        self._selected_lbl = QLabel(t("no_ticket_selected"))
        self._selected_lbl.setObjectName("KpiLabel")
        al.addWidget(self._selected_lbl)

        btn_row = QHBoxLayout()
        for event_type, label_key in [
            ("arrived", "checkpoint_arrived"),
            ("on_bridge", "checkpoint_on_bridge"),
            ("off_bridge", "checkpoint_off_bridge"),
            ("dispatch", "checkpoint_dispatch"),
            ("returned", "checkpoint_returned"),
        ]:
            btn = QPushButton(t(label_key))
            btn.setObjectName("BtnSmall")
            btn.clicked.connect(lambda _, et=event_type: self._record_checkpoint(et))
            btn_row.addWidget(btn)
        btn_row.addStretch()
        al.addLayout(btn_row)

        main.addWidget(actions)

    def refresh(self) -> None:
        self._rows = get_gate_queue()
        self._render(self._rows)

    def _filter(self, text: str) -> None:
        query = text.strip().upper()
        if not query:
            self._render(self._rows)
            return
        filtered = [
            row
            for row in self._rows
            if query in row["vehicle_plate"].upper() or query in row["ticket_number"].upper()
        ]
        self._render(filtered)

    def _render(self, rows: list[dict]) -> None:
        self._table.setRowCount(0)
        for row_data in rows:
            row = self._table.rowCount()
            self._table.insertRow(row)

            stage = t("awaiting_tare") if row_data["pending_stage"] == "awaiting_tare" else t("awaiting_gross")
            values = [
                row_data["ticket_number"],
                row_data["vehicle_plate"],
                row_data["driver_name"],
                t("gross_first") if row_data["weighing_mode"] == "gross_first" else t("tare_first"),
                stage,
                format_datetime(row_data["first_capture_datetime"]),
                format_wait_time(row_data["first_capture_datetime"]),
                self._format_event(row_data["latest_event"]),
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(str(val))
                item.setData(Qt.ItemDataRole.UserRole, row_data["ticket_id"])
                self._table.setItem(row, col, item)

            btn_widget = QWidget()
            bl = QHBoxLayout(btn_widget)
            bl.setContentsMargins(4, 2, 4, 2)
            cont_btn = QPushButton(t("continue"))
            cont_btn.setObjectName("BtnMiniPrimary")
            cont_btn.clicked.connect(lambda _, tid=row_data["ticket_id"]: self.open_step2.emit(tid))
            bl.addWidget(cont_btn)
            bl.addStretch()
            self._table.setCellWidget(row, len(values), btn_widget)

    def _on_selection_changed(self) -> None:
        items = self._table.selectedItems()
        if not items:
            self._selected_ticket_id = None
            self._selected_lbl.setText(t("no_ticket_selected"))
            return
        ticket_id = items[0].data(Qt.ItemDataRole.UserRole)
        self._selected_ticket_id = int(ticket_id)
        self._selected_lbl.setText(f"{t('ticket_number')}: {items[0].text()}")

    def _record_checkpoint(self, event_type: str) -> None:
        if self._selected_ticket_id is None:
            show_error(t("select_ticket_first"), parent=self)
            return
        try:
            log_gate_event(self._user, self._selected_ticket_id, event_type)
            show_info(t("checkpoint_saved"), parent=self)
            self.refresh()
        except Exception as exc:
            show_error(str(exc), parent=self)

    def _format_event(self, event_type: str) -> str:
        mapping = {
            "arrived": t("checkpoint_arrived"),
            "on_bridge": t("checkpoint_on_bridge"),
            "off_bridge": t("checkpoint_off_bridge"),
            "dispatch": t("checkpoint_dispatch"),
            "returned": t("checkpoint_returned"),
        }
        return mapping.get(event_type, "-")


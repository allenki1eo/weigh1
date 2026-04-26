"""Vehicle lookup screen for operators."""
from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from weighmaster.database.models import User
from weighmaster.i18n.translator import t
from weighmaster.services import report_service
from weighmaster.ui.components.stat_card import KpiCard
from weighmaster.ui.components.dialogs import show_error
from weighmaster.utils.helpers import format_datetime, format_weight


class VehicleLookupScreen(QWidget):
    def __init__(self, user: User, parent=None) -> None:
        super().__init__(parent)
        self._user = user
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.timeout.connect(self._search)
        self._build_ui()

    def _build_ui(self) -> None:
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 20, 24, 20)
        main.setSpacing(16)

        title = QLabel(t("vehicle_history"))
        title.setObjectName("PageTitle")
        main.addWidget(title)

        # Search bar
        search_frame = QFrame()
        search_frame.setObjectName("Card")
        sl = QHBoxLayout(search_frame)
        sl.setContentsMargins(16, 10, 16, 10)
        sl.setSpacing(10)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(t("search_plate"))
        self._search_input.textChanged.connect(lambda: self._debounce.start(300))
        self._search_input.returnPressed.connect(self._search)
        sl.addWidget(QLabel(t("vehicle_plate")))
        sl.addWidget(self._search_input, 1)

        search_btn = QPushButton(t("search"))
        search_btn.setObjectName("BtnSecondary")
        search_btn.clicked.connect(self._search)
        sl.addWidget(search_btn)

        main.addWidget(search_frame)

        # Stats row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)
        self._kpi_visits = KpiCard(t("total_visits"), "0", "VS")
        self._kpi_avg = KpiCard(t("avg_net_weight"), "0 kg", "AV")
        self._kpi_last = KpiCard(t("last_visit"), "—", "LV")
        for card in [self._kpi_visits, self._kpi_avg, self._kpi_last]:
            stats_row.addWidget(card, 1)
        main.addLayout(stats_row)

        # Results table
        self._table = QTableWidget()
        self._table.setObjectName("TableWidget")
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setShowGrid(False)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels([
            t("ticket_number"), t("date_time"), t("commodity"),
            t("driver_name"), t("gross_weight"), t("tare_weight"), t("net_weight"),
        ])
        main.addWidget(self._table, 1)

    def refresh(self) -> None:
        if self._search_input.text().strip():
            self._search()

    def _search(self) -> None:
        plate = self._search_input.text().strip()
        if not plate:
            self._table.setRowCount(0)
            self._kpi_visits.set_value("0")
            self._kpi_avg.set_value("0 kg")
            self._kpi_last.set_value("—")
            return
        try:
            data = report_service.vehicle_history(plate)
            self._table.setRowCount(0)
            for item in data:
                row = self._table.rowCount()
                self._table.insertRow(row)
                vals = [
                    item["ticket_number"],
                    format_datetime(item["created_at"]),
                    item["commodity"] or "—",
                    item["driver_name"] or "—",
                    format_weight(item.get("gross_kg")),
                    format_weight(item.get("tare_kg")),
                    format_weight(item.get("net_kg")),
                ]
                for col, val in enumerate(vals):
                    self._table.setItem(row, col, QTableWidgetItem(str(val)))

            if data:
                total_visits = len(data)
                avg_net = sum((d.get("net_kg") or 0.0) for d in data) / max(total_visits, 1)
                last_visit = format_datetime(data[0].get("created_at"))
                self._kpi_visits.set_value(str(total_visits))
                self._kpi_avg.set_value(f"{avg_net:,.2f} kg")
                self._kpi_last.set_value(last_visit)
            else:
                self._kpi_visits.set_value("0")
                self._kpi_avg.set_value("0 kg")
                self._kpi_last.set_value("—")
        except Exception as exc:
            show_error(str(exc), parent=self)

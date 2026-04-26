"""Admin reports screen — date-range reports with export."""
from __future__ import annotations

from datetime import datetime, date

from PyQt6.QtCore import QDate, Qt, QTimer
from PyQt6.QtWidgets import (
    QComboBox, QDateEdit, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QFileDialog,
)

from weighmaster.database.models import User
from weighmaster.i18n.translator import t
from weighmaster.services import report_service
from weighmaster.pdf import report_pdf
from weighmaster.ui.components.dialogs import show_error, show_info
from weighmaster.utils.helpers import format_datetime, format_weight


class ReportsScreen(QWidget):
    def __init__(self, user: User, parent=None) -> None:
        super().__init__(parent)
        self._user = user
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.timeout.connect(self._run_report)
        self._build_ui()

    def _build_ui(self) -> None:
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 20, 24, 20)
        main.setSpacing(12)

        title = QLabel(t("reports"))
        title.setObjectName("PageTitle")
        main.addWidget(title)

        # Filter bar
        filter_frame = QFrame()
        filter_frame.setObjectName("Card")
        fl = QHBoxLayout(filter_frame)
        fl.setContentsMargins(16, 10, 16, 10)
        fl.setSpacing(10)

        self._type_combo = QComboBox()
        for key, lbl in [
            ("daily", t("daily_summary")),
            ("monthly", t("monthly_summary")),
            ("commodity", t("commodity_report")),
            ("operator", t("operator_activity")),
            ("vehicle", t("vehicle_history")),
            ("driver", t("driver_history")),
            ("full", t("full_export")),
        ]:
            self._type_combo.addItem(lbl, key)
        self._type_combo.currentIndexChanged.connect(self._on_type_changed)
        fl.addWidget(QLabel(t("report_type")))
        fl.addWidget(self._type_combo)

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

        # Month / Year picker (for monthly summary)
        self._month_picker = QComboBox()
        for m in range(1, 13):
            self._month_picker.addItem(datetime(2000, m, 1).strftime("%B"), m)
        self._month_picker.setCurrentIndex(QDate.currentDate().month() - 1)
        self._month_picker.currentIndexChanged.connect(lambda: self._debounce.start(100))
        self._year_picker = QComboBox()
        current_year = QDate.currentDate().year()
        for y in range(current_year - 2, current_year + 2):
            self._year_picker.addItem(str(y), y)
        self._year_picker.setCurrentIndex(2)
        self._year_picker.currentIndexChanged.connect(lambda: self._debounce.start(100))
        fl.addWidget(self._month_picker)
        fl.addWidget(self._year_picker)
        self._month_picker.hide()
        self._year_picker.hide()

        # Search inputs
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(t("search"))
        self._search_input.textChanged.connect(lambda: self._debounce.start(300))
        fl.addWidget(self._search_input)
        self._search_input.hide()

        fl.addStretch()

        export_excel_btn = QPushButton(t("export_excel"))
        export_excel_btn.setObjectName("BtnSecondary")
        export_excel_btn.clicked.connect(self._export_excel)
        fl.addWidget(export_excel_btn)

        export_pdf_btn = QPushButton(t("export_pdf"))
        export_pdf_btn.setObjectName("BtnSecondary")
        export_pdf_btn.clicked.connect(self._export_pdf)
        fl.addWidget(export_pdf_btn)

        main.addWidget(filter_frame)

        # Summary stats row
        self._stats_lbl = QLabel()
        self._stats_lbl.setObjectName("KpiLabel")
        main.addWidget(self._stats_lbl)

        # Report table
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
        main.addWidget(self._table, 1)

    def refresh(self) -> None:
        self._run_report()

    def _on_type_changed(self) -> None:
        report_type = self._type_combo.currentData()
        # Show/hide date range
        is_monthly = report_type == "monthly"
        self._date_from.setVisible(not is_monthly)
        self._date_to.setVisible(not is_monthly)
        for lbl in self._date_from.parent().findChildren(QLabel):
            if lbl.text() == t("date_from"):
                lbl.setVisible(not is_monthly)
            if lbl.text() == t("date_to"):
                lbl.setVisible(not is_monthly)
        self._month_picker.setVisible(is_monthly)
        self._year_picker.setVisible(is_monthly)

        # Show/hide search input
        needs_search = report_type in ("vehicle", "driver")
        self._search_input.setVisible(needs_search)
        if needs_search:
            if report_type == "vehicle":
                self._search_input.setPlaceholderText(t("search_plate"))
            else:
                self._search_input.setPlaceholderText(t("search_driver"))
            self._search_input.setText("")

        self._debounce.start(100)

    def _date_range(self):
        df = self._date_from.date()
        dt = self._date_to.date()
        return (
            date(df.year(), df.month(), df.day()),
            date(dt.year(), dt.month(), dt.day()),
        )

    def _run_report(self) -> None:
        report_type = self._type_combo.currentData()
        date_from, date_to = self._date_range()
        try:
            if report_type == "daily":
                data = report_service.daily_summary(date_from)
                self._render_commodity(data)
            elif report_type == "monthly":
                year = self._year_picker.currentData()
                month = self._month_picker.currentData()
                data = report_service.monthly_summary(year, month)
                self._render_monthly(data)
            elif report_type == "commodity":
                data = report_service.commodity_report(date_from, date_to)
                self._render_commodity(data)
            elif report_type == "operator":
                data = report_service.operator_activity(date_from, date_to)
                self._render_operator(data)
            elif report_type == "vehicle":
                plate = self._search_input.text().strip()
                if not plate:
                    self._table.setRowCount(0)
                    self._stats_lbl.setText(t("no_results"))
                    return
                data = report_service.vehicle_history(plate, date_from, date_to)
                self._render_vehicle(data)
            elif report_type == "driver":
                driver = self._search_input.text().strip()
                if not driver:
                    self._table.setRowCount(0)
                    self._stats_lbl.setText(t("no_results"))
                    return
                data = report_service.driver_history(driver, date_from, date_to)
                self._render_driver(data)
            elif report_type == "full":
                data = report_service.full_export(date_from, date_to)
                self._render_full(data)
        except Exception as exc:
            show_error(str(exc), parent=self)

    def _render_commodity(self, data: list[dict]) -> None:
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels([t("commodity"), t("count"), t("net_weight_tonnes")])
        self._table.setRowCount(0)
        total_count = 0
        total_kg = 0.0
        for item in data:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(item["commodity"]))
            self._table.setItem(row, 1, QTableWidgetItem(str(item["count"])))
            self._table.setItem(row, 2, QTableWidgetItem(f"{item['net_kg']/1000:,.3f}"))
            total_count += item["count"]
            total_kg += item["net_kg"]
        self._stats_lbl.setText(
            f"{t('total')}: {total_count} tickets · {total_kg/1000:,.2f} tonnes"
        )

    def _render_monthly(self, data: dict) -> None:
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels([
            t("date"), t("count"), t("net_weight_tonnes"), t("total")
        ])
        self._table.setRowCount(0)
        for item in data.get("days", []):
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(item["date"]))
            self._table.setItem(row, 1, QTableWidgetItem(str(item["count"])))
            self._table.setItem(row, 2, QTableWidgetItem(f"{item['net_kg']/1000:,.3f}"))
            self._table.setItem(row, 3, QTableWidgetItem(f"{item['net_kg']:,.2f} kg"))
        self._stats_lbl.setText(
            f"{t('total')}: {data.get('total_count', 0)} tickets · "
            f"{data.get('total_net_kg', 0.0)/1000:,.2f} tonnes · "
            f"{data.get('unique_vehicles', 0)} vehicles"
        )

    def _render_operator(self, data: list[dict]) -> None:
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(
            [t("operator"), t("count"), "Complete", t("net_weight_tonnes")]
        )
        self._table.setRowCount(0)
        for item in data:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(item["operator"]))
            self._table.setItem(row, 1, QTableWidgetItem(str(item["count"])))
            self._table.setItem(row, 2, QTableWidgetItem(str(item["complete"])))
            self._table.setItem(row, 3, QTableWidgetItem(f"{item['net_kg']/1000:,.3f}"))
        self._stats_lbl.setText(f"{len(data)} operators")

    def _render_vehicle(self, data: list[dict]) -> None:
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels([
            t("ticket_number"), t("date_time"), t("commodity"),
            t("driver_name"), t("gross_weight"), t("tare_weight"), t("net_weight"),
        ])
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
            avg_net = sum((d.get("net_kg") or 0.0) for d in data) / max(len(data), 1)
            self._stats_lbl.setText(
                f"{len(data)} {t('total_visits').lower()} · "
                f"{t('avg_net_weight')}: {avg_net:,.2f} kg · "
                f"{t('last_visit')}: {format_datetime(data[0].get('created_at'))}"
            )
        else:
            self._stats_lbl.setText(t("no_results"))

    def _render_driver(self, data: list[dict]) -> None:
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels([
            t("ticket_number"), t("date_time"), t("vehicle_plate"),
            t("commodity"), t("gross_weight"), t("tare_weight"), t("net_weight"),
        ])
        self._table.setRowCount(0)
        for item in data:
            row = self._table.rowCount()
            self._table.insertRow(row)
            vals = [
                item["ticket_number"],
                format_datetime(item["created_at"]),
                item["vehicle_plate"],
                item["commodity"] or "—",
                format_weight(item.get("gross_kg")),
                format_weight(item.get("tare_kg")),
                format_weight(item.get("net_kg")),
            ]
            for col, val in enumerate(vals):
                self._table.setItem(row, col, QTableWidgetItem(str(val)))
        self._stats_lbl.setText(f"{len(data)} records")

    def _render_full(self, data: list[dict]) -> None:
        self._table.setColumnCount(10)
        self._table.setHorizontalHeaderLabels([
            t("ticket_number"), t("vehicle_plate"), t("commodity"),
            t("tare_weight"), t("gross_weight"), t("net_weight"),
            t("commodity_value"), t("oil_price"), t("total_price"),
            t("date_time"),
        ])
        self._table.setRowCount(0)
        for item in data:
            row = self._table.rowCount()
            self._table.insertRow(row)
            vals = [
                item["ticket_number"], item["vehicle_plate"], item["commodity"],
                f"{item['tare_kg']:.2f}" if item['tare_kg'] else "—",
                f"{item['gross_kg']:.2f}" if item['gross_kg'] else "—",
                f"{item['net_kg']:.2f}" if item['net_kg'] else "—",
                f"{item['commodity_value']:.2f}" if item.get('commodity_value') is not None else "—",
                f"{item['oil_price']:.2f}" if item.get('oil_price') is not None else "—",
                f"{item['total_price']:.2f}" if item.get('total_price') is not None else "—",
                format_datetime(item["created_at"]),
            ]
            for col, val in enumerate(vals):
                self._table.setItem(row, col, QTableWidgetItem(str(val)))
        self._stats_lbl.setText(f"{len(data)} records")

    def _export_excel(self) -> None:
        try:
            from openpyxl import Workbook
            path, _ = QFileDialog.getSaveFileName(
                self, "Save Report", "report.xlsx", "Excel (*.xlsx)"
            )
            if not path:
                return
            date_from, date_to = self._date_range()
            data = report_service.full_export(date_from, date_to)

            wb = Workbook()
            ws = wb.active
            ws.title = "Report"
            headers = ["Ticket No", "Plate", "Commodity", "Tare (kg)",
                       "Gross (kg)", "Net (kg)", "Commodity Value",
                       "Oil Price", "Total Price", "Date/Time", "Status"]
            ws.append(headers)
            for item in data:
                ws.append([
                    item["ticket_number"], item["vehicle_plate"], item["commodity"],
                    item["tare_kg"], item["gross_kg"], item["net_kg"],
                    item.get("commodity_value"), item.get("oil_price"), item.get("total_price"),
                    format_datetime(item["created_at"]),
                    "VOID" if item["is_void"] else item["status"],
                ])
            wb.save(path)
            show_info(f"Exported to {path}", parent=self)
        except Exception as exc:
            show_error(str(exc), parent=self)

    def _export_pdf(self) -> None:
        try:
            report_type = self._type_combo.currentData()
            path, _ = QFileDialog.getSaveFileName(
                self, t("export_pdf"), "report.pdf", "PDF (*.pdf)"
            )
            if not path:
                return
            date_from, date_to = self._date_range()

            if report_type == "daily":
                data = report_service.daily_summary(date_from)
                report_pdf.generate_daily_summary_pdf(data, date_from, path)
            elif report_type == "monthly":
                year = self._year_picker.currentData()
                month = self._month_picker.currentData()
                data = report_service.monthly_summary(year, month)
                report_pdf.generate_monthly_summary_pdf(data, year, month, path)
            elif report_type == "vehicle":
                plate = self._search_input.text().strip()
                if not plate:
                    show_error(t("no_results"), parent=self)
                    return
                data = report_service.vehicle_history(plate, date_from, date_to)
                report_pdf.generate_vehicle_history_pdf(data, plate, path)
            elif report_type == "full":
                data = report_service.full_export(date_from, date_to)
                report_pdf.generate_full_export_pdf(data, date_from, date_to, path)
            else:
                # For commodity, operator, driver — export full range as generic table
                data = report_service.full_export(date_from, date_to)
                report_pdf.generate_full_export_pdf(data, date_from, date_to, path)

            show_info(f"Exported to {path}", parent=self)
        except Exception as exc:
            show_error(str(exc), parent=self)

"""Audit log viewer — read-only, compliance record."""
from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (
    QComboBox, QDateEdit, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QPushButton, QSplitter, QTableWidget, QTableWidgetItem,
    QTextEdit, QVBoxLayout, QWidget,
)

from weighmaster.database.models import User
from weighmaster.i18n.translator import t
from weighmaster.ui.components.dialogs import show_error, show_info
from weighmaster.utils.helpers import format_datetime
from weighmaster.config import TABLE_PAGE_SIZE


_AMBER_ACTIONS = {"TICKET_MANUAL_WEIGHT", "LOGIN_FAILED", "USER_DEACTIVATE"}
_RED_ACTIONS = {"TICKET_VOID"}


class AuditLogScreen(QWidget):
    def __init__(self, user: User, parent=None) -> None:
        super().__init__(parent)
        self._user = user
        self._offset = 0
        self._build_ui()

    def _build_ui(self) -> None:
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 20, 24, 20)
        main.setSpacing(12)

        header_row = QHBoxLayout()
        title = QLabel(t("audit_log"))
        title.setObjectName("PageTitle")
        header_row.addWidget(title)
        header_row.addStretch()
        export_btn = QPushButton(t("export_excel"))
        export_btn.setObjectName("BtnSecondary")
        export_btn.clicked.connect(self._export)
        header_row.addWidget(export_btn)
        main.addLayout(header_row)

        # Filter bar
        filter_frame = QFrame()
        filter_frame.setObjectName("Card")
        fl = QHBoxLayout(filter_frame)
        fl.setContentsMargins(16, 10, 16, 10)
        fl.setSpacing(10)

        self._date_from = QDateEdit()
        self._date_from.setDate(QDate.currentDate().addDays(-7))
        self._date_from.setCalendarPopup(True)
        self._date_from.dateChanged.connect(self._load)

        self._date_to = QDateEdit()
        self._date_to.setDate(QDate.currentDate())
        self._date_to.setCalendarPopup(True)
        self._date_to.dateChanged.connect(self._load)

        self._action_combo = QComboBox()
        self._action_combo.addItem("All Actions", "")
        for action in ["LOGIN", "LOGIN_FAILED", "LOGOUT", "TICKET_CREATE_TARE",
                       "TICKET_CAPTURE_GROSS", "TICKET_VOID", "TICKET_MANUAL_WEIGHT",
                       "USER_CREATE", "USER_DEACTIVATE", "COMPANY_SETTINGS_CHANGED"]:
            self._action_combo.addItem(action, action)
        self._action_combo.currentIndexChanged.connect(self._load)

        fl.addWidget(QLabel(t("date_from")))
        fl.addWidget(self._date_from)
        fl.addWidget(QLabel(t("date_to")))
        fl.addWidget(self._date_to)
        fl.addWidget(QLabel(t("audit_action")))
        fl.addWidget(self._action_combo)
        fl.addStretch()
        main.addWidget(filter_frame)

        # Splitter: table top, detail bottom
        splitter = QSplitter(Qt.Orientation.Vertical)

        self._table = QTableWidget()
        self._table.setObjectName("TableWidget")
        cols = [t("audit_timestamp"), t("audit_user"), t("audit_action"),
                t("audit_entity"), "Entity ID"]
        self._table.setColumnCount(len(cols))
        self._table.setHorizontalHeaderLabels(cols)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setShowGrid(False)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self._table.itemSelectionChanged.connect(self._on_row_selected)
        splitter.addWidget(self._table)

        self._detail_edit = QTextEdit()
        self._detail_edit.setReadOnly(True)
        self._detail_edit.setPlaceholderText("Select a row to see details...")
        self._detail_edit.setMaximumHeight(160)
        splitter.addWidget(self._detail_edit)

        main.addWidget(splitter, 1)

        # Pagination
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
        from weighmaster.database.connection import get_session
        from weighmaster.database.models import AuditLog
        df = self._date_from.date()
        dt = self._date_to.date()
        date_from = datetime(df.year(), df.month(), df.day())
        date_to = datetime(dt.year(), dt.month(), dt.day(), 23, 59, 59)
        action_filter = self._action_combo.currentData()

        with get_session() as session:
            q = session.query(AuditLog).filter(
                AuditLog.timestamp >= date_from,
                AuditLog.timestamp <= date_to,
            )
            if action_filter:
                q = q.filter(AuditLog.action == action_filter)
            total = q.count()
            logs = (q.order_by(AuditLog.timestamp.desc())
                    .offset(self._offset).limit(TABLE_PAGE_SIZE).all())
            data = [(l.id, l.timestamp, l.username, l.action, l.entity,
                     l.entity_id, l.details) for l in logs]

        self._table.setRowCount(0)
        for lid, ts, username, action, entity, entity_id, details in data:
            row = self._table.rowCount()
            self._table.insertRow(row)
            values = [
                format_datetime(ts, "%d/%b/%Y %H:%M:%S"),
                username, action, entity, str(entity_id or ""),
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, details)
                if action in _RED_ACTIONS:
                    item.setForeground(Qt.GlobalColor.red)
                elif action in _AMBER_ACTIONS:
                    item.setForeground(Qt.GlobalColor.darkYellow)
                self._table.setItem(row, col, item)

        self._count_lbl.setText(
            f"{self._offset + 1}–{min(self._offset + TABLE_PAGE_SIZE, total)} of {total}"
        )
        self._prev_btn.setEnabled(self._offset > 0)
        self._next_btn.setEnabled(self._offset + TABLE_PAGE_SIZE < total)

    def _on_row_selected(self) -> None:
        rows = self._table.selectedItems()
        if not rows:
            return
        details_json = rows[0].data(Qt.ItemDataRole.UserRole)
        if details_json:
            import json
            try:
                parsed = json.loads(details_json)
                text = "\n".join(f"{k}: {v}" for k, v in parsed.items())
                self._detail_edit.setPlainText(text or "(no details)")
            except Exception:
                self._detail_edit.setPlainText(str(details_json))

    def _prev_page(self) -> None:
        self._offset = max(0, self._offset - TABLE_PAGE_SIZE)
        self._load()

    def _next_page(self) -> None:
        self._offset += TABLE_PAGE_SIZE
        self._load()

    def _export(self) -> None:
        try:
            from openpyxl import Workbook
            from PyQt6.QtWidgets import QFileDialog
            from weighmaster.database.connection import get_session
            from weighmaster.database.models import AuditLog

            path, _ = QFileDialog.getSaveFileName(
                self, "Save Audit Log", "audit_log.xlsx", "Excel (*.xlsx)"
            )
            if not path:
                return

            df = self._date_from.date()
            dt = self._date_to.date()
            date_from = datetime(df.year(), df.month(), df.day())
            date_to = datetime(dt.year(), dt.month(), dt.day(), 23, 59, 59)

            with get_session() as session:
                logs = (session.query(AuditLog)
                        .filter(AuditLog.timestamp >= date_from,
                                AuditLog.timestamp <= date_to)
                        .order_by(AuditLog.timestamp.desc())
                        .all())
                data = [(l.timestamp, l.username, l.action, l.entity,
                         l.entity_id, l.details) for l in logs]

            wb = Workbook()
            ws = wb.active
            ws.title = "Audit Log"
            ws.append(["Timestamp", "User", "Action", "Entity", "Entity ID", "Details"])
            for ts, username, action, entity, entity_id, details in data:
                ws.append([format_datetime(ts), username, action, entity,
                            entity_id, details])
            wb.save(path)
            show_info(f"Exported to {path}", parent=self)
        except Exception as exc:
            show_error(str(exc), parent=self)

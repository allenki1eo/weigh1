"""User management screen — CRUD for users (admin only)."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFormLayout, QFrame,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from weighmaster.database.models import User
from weighmaster.i18n.translator import t
from weighmaster.services.auth_service import create_user, deactivate_user, change_password
from weighmaster.ui.components.dialogs import ConfirmDialog, show_error, show_info
from weighmaster.utils.helpers import format_datetime


class UserManagementScreen(QWidget):
    def __init__(self, user: User, parent=None) -> None:
        super().__init__(parent)
        self._user = user
        self._build_ui()

    def _build_ui(self) -> None:
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 20, 24, 20)
        main.setSpacing(16)

        header_row = QHBoxLayout()
        title = QLabel(t("user_management"))
        title.setObjectName("PageTitle")
        header_row.addWidget(title)
        header_row.addStretch()
        add_btn = QPushButton(t("add_user"))
        add_btn.setObjectName("BtnPrimary")
        add_btn.clicked.connect(self._add_user)
        header_row.addWidget(add_btn)
        main.addLayout(header_row)

        self._table = QTableWidget()
        self._table.setObjectName("TableWidget")
        cols = [t("full_name"), t("username"), t("role"), t("active"),
                t("last_login"), t("created"), ""]
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

    def refresh(self) -> None:
        self._load()

    def _load(self) -> None:
        from weighmaster.database.connection import get_session
        from weighmaster.database.models import User as UserModel
        with get_session() as session:
            users = session.query(UserModel).order_by(UserModel.full_name).all()
            data = [(u.id, u.full_name, u.username, u.role,
                     u.is_active, u.last_login, u.created_at) for u in users]

        self._table.setRowCount(0)
        for uid, full_name, username, role, is_active, last_login, created_at in data:
            row = self._table.rowCount()
            self._table.insertRow(row)
            for col, val in enumerate([
                full_name, username, role.capitalize(),
                "✓" if is_active else "✗",
                format_datetime(last_login), format_datetime(created_at),
            ]):
                item = QTableWidgetItem(str(val))
                item.setData(Qt.ItemDataRole.UserRole, uid)
                if not is_active:
                    item.setForeground(Qt.GlobalColor.gray)
                self._table.setItem(row, col, item)

            # Action buttons
            btn_w = QWidget()
            bl = QHBoxLayout(btn_w)
            bl.setContentsMargins(4, 2, 4, 2)
            bl.setSpacing(4)
            if uid != self._user.id:
                if is_active:
                    deact_btn = QPushButton(t("deactivate"))
                    deact_btn.setObjectName("BtnDanger")
                    deact_btn.setFixedHeight(26)
                    deact_btn.setStyleSheet("font-size:10px; min-height:26px; padding:0 8px;")
                    deact_btn.clicked.connect(
                        lambda _, i=uid, n=full_name: self._deactivate(i, n)
                    )
                    bl.addWidget(deact_btn)
                reset_btn = QPushButton(t("reset_password"))
                reset_btn.setObjectName("BtnSmall")
                reset_btn.clicked.connect(lambda _, i=uid, n=full_name: self._reset_pw(i, n))
                bl.addWidget(reset_btn)
            bl.addStretch()
            self._table.setCellWidget(row, 6, btn_w)

    def _add_user(self) -> None:
        dlg = AddUserDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            try:
                create_user(
                    creator=self._user,
                    username=dlg.username,
                    full_name=dlg.full_name,
                    password=dlg.password,
                    role=dlg.role,
                )
                show_info("User created successfully.", parent=self)
                self._load()
            except Exception as exc:
                show_error(str(exc), parent=self)

    def _deactivate(self, uid: int, name: str) -> None:
        dlg = ConfirmDialog(f"Deactivate user '{name}'?", t("deactivate"), self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            try:
                deactivate_user(self._user, uid)
                self._load()
            except Exception as exc:
                show_error(str(exc), parent=self)

    def _reset_pw(self, uid: int, name: str) -> None:
        from PyQt6.QtWidgets import QInputDialog
        pw, ok = QInputDialog.getText(
            self, t("reset_password"), f"New password for '{name}':",
            QLineEdit.EchoMode.Password
        )
        if ok and pw:
            try:
                from weighmaster.database.connection import get_session
                from weighmaster.database.models import User as UserModel
                with get_session() as session:
                    target = session.query(UserModel).filter_by(id=uid).first()
                if target:
                    change_password(target, pw)
                    show_info("Password reset successfully.", parent=self)
            except Exception as exc:
                show_error(str(exc), parent=self)


class AddUserDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("add_user"))
        self.setMinimumWidth(380)
        self.full_name = ""
        self.username = ""
        self.password = ""
        self.role = "operator"
        self._build_ui()

    def _build_ui(self) -> None:
        fl = QFormLayout(self)
        fl.setSpacing(12)
        fl.setContentsMargins(20, 20, 20, 20)

        self._full_name = QLineEdit()
        self._username = QLineEdit()
        self._password = QLineEdit()
        self._password.setEchoMode(QLineEdit.EchoMode.Password)
        self._role = QComboBox()
        self._role.addItem("Operator", "operator")
        self._role.addItem("Admin", "admin")

        fl.addRow(t("full_name") + " *", self._full_name)
        fl.addRow(t("username") + " *", self._username)
        fl.addRow(t("password") + " *", self._password)
        fl.addRow(t("role"), self._role)

        self._error = QLabel()
        self._error.setObjectName("ErrorLabel")
        self._error.hide()
        fl.addRow("", self._error)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        fl.addRow(buttons)

    def _validate(self) -> None:
        fn = self._full_name.text().strip()
        un = self._username.text().strip()
        pw = self._password.text()
        if not fn or not un or not pw:
            self._error.setText("All fields are required")
            self._error.show()
            return
        self.full_name = fn
        self.username = un
        self.password = pw
        self.role = self._role.currentData()
        self.accept()

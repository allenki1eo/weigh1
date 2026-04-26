"""Reusable dialogs: ConfirmDialog, VoidDialog, ErrorDialog, ChangePasswordDialog."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFrame, QLabel, QLineEdit,
    QMessageBox, QPushButton, QVBoxLayout, QWidget,
)

from weighmaster.i18n.translator import t
from weighmaster.utils.validators import validate_password


class ConfirmDialog(QDialog):
    def __init__(self, message: str, title: str = "Confirm", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(360)
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        msg = QLabel(message)
        msg.setWordWrap(True)
        layout.addWidget(msg)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class VoidDialog(QDialog):
    def __init__(self, ticket_number: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("void_confirm_title"))
        self.setMinimumWidth(420)
        self._reason = ""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        msg = QLabel(t("confirm_void", ticket_no=ticket_number))
        msg.setWordWrap(True)
        layout.addWidget(msg)

        reason_lbl = QLabel(t("void_reason") + " *")
        layout.addWidget(reason_lbl)

        self._reason_edit = QLineEdit()
        self._reason_edit.setPlaceholderText(t("void_reason_required"))
        layout.addWidget(self._reason_edit)

        self._error_lbl = QLabel()
        self._error_lbl.setObjectName("ErrorLabel")
        self._error_lbl.hide()
        layout.addWidget(self._error_lbl)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _validate(self) -> None:
        reason = self._reason_edit.text().strip()
        if not reason:
            self._error_lbl.setText(t("void_reason_required"))
            self._error_lbl.show()
            return
        self._reason = reason
        self.accept()

    @property
    def reason(self) -> str:
        return self._reason


class ChangePasswordDialog(QDialog):
    def __init__(self, forced: bool = False, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("change_password"))
        self.setMinimumWidth(380)
        if forced:
            self.setWindowFlags(
                self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint
            )
        self._new_password = ""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        if forced:
            notice = QLabel(t("must_change_password"))
            notice.setObjectName("ErrorLabel")
            layout.addWidget(notice)

        new_lbl = QLabel(t("new_password") + " *")
        layout.addWidget(new_lbl)
        self._new_edit = QLineEdit()
        self._new_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self._new_edit)

        conf_lbl = QLabel(t("confirm_password") + " *")
        layout.addWidget(conf_lbl)
        self._conf_edit = QLineEdit()
        self._conf_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self._conf_edit)

        self._strength_lbl = QLabel()
        layout.addWidget(self._strength_lbl)

        self._error_lbl = QLabel()
        self._error_lbl.setObjectName("ErrorLabel")
        self._error_lbl.hide()
        layout.addWidget(self._error_lbl)

        self._new_edit.textChanged.connect(self._on_typing)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save)
        if not forced:
            buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
            buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self._validate)
        layout.addWidget(buttons)

    def _on_typing(self, text: str) -> None:
        if not text:
            self._strength_lbl.setText("")
            return
        _, _, strength = validate_password(text)
        colours = {"weak": "#9B1C1C", "medium": "#92400E", "strong": "#057A55"}
        self._strength_lbl.setText(
            f"<span style='color:{colours[strength]};font-weight:600;'>{strength.upper()}</span>"
        )

    def _validate(self) -> None:
        pw = self._new_edit.text()
        conf = self._conf_edit.text()
        valid, err, _ = validate_password(pw)
        if not valid:
            self._show_err(err)
            return
        if pw != conf:
            self._show_err(t("password_mismatch"))
            return
        self._new_password = pw
        self.accept()

    def _show_err(self, msg: str) -> None:
        self._error_lbl.setText(msg)
        self._error_lbl.show()

    @property
    def new_password(self) -> str:
        return self._new_password


def show_error(message: str, title: str = "Error", parent=None) -> None:
    box = QMessageBox(parent)
    box.setWindowTitle(title)
    box.setText(message)
    box.setIcon(QMessageBox.Icon.Critical)
    box.exec()


def show_info(message: str, title: str = "Information", parent=None) -> None:
    box = QMessageBox(parent)
    box.setWindowTitle(title)
    box.setText(message)
    box.setIcon(QMessageBox.Icon.Information)
    box.exec()

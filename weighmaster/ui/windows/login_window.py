"""Login screen."""
from __future__ import annotations

import time

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QWidget,
)

from weighmaster.database.models import User
from weighmaster.i18n.translator import t
from weighmaster.services.auth_service import (
    InvalidCredentialsError, LockedOutError, change_password, login,
)
from weighmaster.ui.components.dialogs import ChangePasswordDialog, show_error
from weighmaster.config import LOGIN_LOCKOUT_ATTEMPTS


class LoginWindow(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("app_name"))
        self.setMinimumSize(480, 560)
        self.setModal(True)
        self.authenticated_user: User | None = None
        self._lockout_timer: QTimer | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("LoginCard")
        card.setFixedWidth(420)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 36, 40, 36)
        card_layout.setSpacing(16)

        # Title
        title = QLabel(t("app_name"))
        title.setObjectName("PageTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        sub = QLabel(t("app_subtitle"))
        sub.setObjectName("KpiLabel")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(sub)

        card_layout.addSpacing(16)

        # Username
        user_lbl = QLabel(t("username"))
        card_layout.addWidget(user_lbl)
        self._username_edit = QLineEdit()
        self._username_edit.setPlaceholderText(t("username"))
        self._username_edit.returnPressed.connect(self._attempt_login)
        card_layout.addWidget(self._username_edit)

        # Password
        pass_lbl = QLabel(t("password"))
        card_layout.addWidget(pass_lbl)
        self._password_edit = QLineEdit()
        self._password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._password_edit.setPlaceholderText(t("password"))
        self._password_edit.returnPressed.connect(self._attempt_login)
        card_layout.addWidget(self._password_edit)

        # Error label
        self._error_lbl = QLabel()
        self._error_lbl.setObjectName("ErrorLabel")
        self._error_lbl.setWordWrap(True)
        self._error_lbl.hide()
        card_layout.addWidget(self._error_lbl)

        # Sign in button
        self._signin_btn = QPushButton(t("sign_in"))
        self._signin_btn.setObjectName("BtnCapture")
        self._signin_btn.clicked.connect(self._attempt_login)
        card_layout.addWidget(self._signin_btn)

        # Language row
        lang_row = QHBoxLayout()
        lang_row.addStretch()
        en_btn = QPushButton("EN")
        en_btn.setObjectName("BtnSmall")
        en_btn.clicked.connect(lambda: self._set_lang("en"))
        sw_btn = QPushButton("SW")
        sw_btn.setObjectName("BtnSmall")
        sw_btn.clicked.connect(lambda: self._set_lang("sw"))
        lang_row.addWidget(en_btn)
        lang_row.addWidget(sw_btn)
        lang_row.addStretch()
        card_layout.addLayout(lang_row)

        outer.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    def _set_lang(self, lang: str) -> None:
        from weighmaster.i18n.translator import set_language
        set_language(lang)

    def _attempt_login(self) -> None:
        username = self._username_edit.text().strip()
        password = self._password_edit.text()

        if not username or not password:
            self._show_error(t("error_invalid_creds"))
            return

        self._signin_btn.setEnabled(False)
        try:
            user = login(username, password)
        except LockedOutError as exc:
            self._start_lockout_countdown(exc.seconds_remaining)
            return
        except InvalidCredentialsError:
            self._show_error(t("error_invalid_creds"))
            self._signin_btn.setEnabled(True)
            return
        except Exception as exc:
            self._show_error(str(exc))
            self._signin_btn.setEnabled(True)
            return

        # Force password change if default password detected
        if user.password_hash and len(user.password_hash) < 10:
            self._force_change_password(user)
            return

        self.authenticated_user = user
        self.accept()

    def _force_change_password(self, user: User) -> None:
        dlg = ChangePasswordDialog(forced=True, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            change_password(user, dlg.new_password)
            self.authenticated_user = user
            self.accept()

    def _show_error(self, message: str) -> None:
        self._error_lbl.setText(message)
        self._error_lbl.show()

    def _start_lockout_countdown(self, seconds: int) -> None:
        self._remaining = seconds
        self._signin_btn.setEnabled(False)
        self._show_error(t("error_locked", seconds=seconds))

        self._lockout_timer = QTimer(self)
        self._lockout_timer.timeout.connect(self._tick_lockout)
        self._lockout_timer.start(1000)

    def _tick_lockout(self) -> None:
        self._remaining -= 1
        if self._remaining <= 0:
            self._lockout_timer.stop()
            self._error_lbl.hide()
            self._signin_btn.setEnabled(True)
        else:
            self._show_error(t("error_locked", seconds=self._remaining))

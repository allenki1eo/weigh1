"""First-run setup wizard — runs when no Company record exists."""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QComboBox, QDateEdit, QDialog, QDialogButtonBox, QDoubleSpinBox,
    QFileDialog, QFormLayout, QLabel, QLineEdit, QPushButton,
    QStackedWidget, QVBoxLayout, QHBoxLayout, QWidget,
)
from PyQt6.QtCore import QDate, Qt

from weighmaster.i18n.translator import t
from weighmaster.utils.validators import validate_password


class SetupWizard(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("first_run_title"))
        self.setMinimumSize(560, 520)
        self.setModal(True)
        self._current_page = 0
        self._logo_path: str = ""
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header_frame = QWidget()
        header_frame.setObjectName("WizardHeader")
        header_frame.setFixedHeight(72)
        hfl = QVBoxLayout(header_frame)
        hfl.setContentsMargins(28, 16, 28, 16)
        self._header_title = QLabel(t("setup_company"))
        self._header_title.setObjectName("PageTitle")
        self._header_title.setStyleSheet("color: white; font-size: 16px; font-weight: 600;")
        self._header_sub = QLabel(t("first_run_title"))
        self._header_sub.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 11px;")
        hfl.addWidget(self._header_title)
        hfl.addWidget(self._header_sub)
        root.addWidget(header_frame)

        # Content stack
        self._stack = QStackedWidget()
        self._stack.addWidget(self._build_page1())
        self._stack.addWidget(self._build_page2())
        self._stack.addWidget(self._build_page3())
        root.addWidget(self._stack, 1)

        # Nav buttons
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(24, 12, 24, 16)
        btn_row.setSpacing(12)

        self._back_btn = QPushButton("← Back")
        self._back_btn.setObjectName("BtnSecondary")
        self._back_btn.setEnabled(False)
        self._back_btn.clicked.connect(self._go_back)
        btn_row.addWidget(self._back_btn)

        btn_row.addStretch()

        self._next_btn = QPushButton("Next →")
        self._next_btn.setObjectName("BtnPrimary")
        self._next_btn.clicked.connect(self._go_next)
        btn_row.addWidget(self._next_btn)

        root.addLayout(btn_row)

    def _build_page1(self) -> QWidget:
        w = QWidget()
        fl = QFormLayout(w)
        fl.setContentsMargins(28, 24, 28, 24)
        fl.setSpacing(12)

        self._company_name = QLineEdit()
        self._address = QLineEdit()
        self._phone = QLineEdit()
        self._email = QLineEdit()
        self._logo_btn = QPushButton(t("choose_logo"))
        self._logo_btn.setObjectName("BtnSecondary")
        self._logo_btn.clicked.connect(self._pick_logo)
        self._logo_lbl = QLabel(t("logo") + ": (optional)")
        self._logo_lbl.setObjectName("KpiLabel")

        fl.addRow(t("company_name") + " *", self._company_name)
        fl.addRow(t("address") + " *", self._address)
        fl.addRow(t("phone") + " *", self._phone)
        fl.addRow(t("email"), self._email)
        logo_row = QHBoxLayout()
        logo_row.addWidget(self._logo_btn)
        logo_row.addWidget(self._logo_lbl)
        logo_row.addStretch()
        fl.addRow(t("logo"), logo_row)

        self._p1_error = QLabel()
        self._p1_error.setObjectName("ErrorLabel")
        self._p1_error.hide()
        fl.addRow("", self._p1_error)
        return w

    def _build_page2(self) -> QWidget:
        w = QWidget()
        fl = QFormLayout(w)
        fl.setContentsMargins(28, 24, 28, 24)
        fl.setSpacing(12)

        self._com_port = QLineEdit("COM3")
        self._baud_rate = QComboBox()
        for br in [1200, 2400, 4800, 9600, 19200]:
            self._baud_rate.addItem(str(br), br)
        self._baud_rate.setCurrentText("9600")

        test_row = QHBoxLayout()
        test_btn = QPushButton(t("test_connection"))
        test_btn.setObjectName("BtnSecondary")
        test_btn.clicked.connect(self._test_connection)
        self._test_result = QLabel()
        self._test_result.setObjectName("KpiLabel")
        test_row.addWidget(test_btn)
        test_row.addWidget(self._test_result)
        test_row.addStretch()

        self._capacity = QDoubleSpinBox()
        self._capacity.setRange(1.0, 500.0)
        self._capacity.setValue(80.0)
        self._capacity.setSuffix(" tonnes")

        self._wma_cert = QLineEdit()
        self._wma_valid = QDateEdit()
        self._wma_valid.setDate(QDate.currentDate().addYears(1))
        self._wma_valid.setCalendarPopup(True)

        fl.addRow(t("com_port"), self._com_port)
        fl.addRow(t("baud_rate"), self._baud_rate)
        fl.addRow("", test_row)
        fl.addRow(t("capacity"), self._capacity)
        fl.addRow(t("wma_cert"), self._wma_cert)
        fl.addRow(t("valid_until"), self._wma_valid)
        return w

    def _build_page3(self) -> QWidget:
        w = QWidget()
        fl = QFormLayout(w)
        fl.setContentsMargins(28, 24, 28, 24)
        fl.setSpacing(12)

        self._admin_full_name = QLineEdit()
        self._admin_username = QLineEdit("admin")
        self._admin_password = QLineEdit()
        self._admin_password.setEchoMode(QLineEdit.EchoMode.Password)
        self._admin_confirm = QLineEdit()
        self._admin_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self._pw_strength = QLabel()

        self._admin_password.textChanged.connect(self._check_strength)

        fl.addRow(t("full_name") + " *", self._admin_full_name)
        fl.addRow(t("username") + " *", self._admin_username)
        fl.addRow(t("new_password") + " *", self._admin_password)
        fl.addRow(t("confirm_password") + " *", self._admin_confirm)
        fl.addRow("", self._pw_strength)

        self._p3_error = QLabel()
        self._p3_error.setObjectName("ErrorLabel")
        self._p3_error.hide()
        fl.addRow("", self._p3_error)
        return w

    def _check_strength(self, text: str) -> None:
        if not text:
            self._pw_strength.setText("")
            return
        _, _, strength = validate_password(text)
        colours = {"weak": "#9B1C1C", "medium": "#92400E", "strong": "#057A55"}
        self._pw_strength.setText(
            f"<span style='color:{colours[strength]};font-weight:600;'>{strength.upper()}</span>"
        )

    def _pick_logo(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Logo", "", "Images (*.png *.jpg *.jpeg)"
        )
        if path:
            self._logo_path = path
            self._logo_lbl.setText(path.split("/")[-1])

    def _test_connection(self) -> None:
        try:
            import serial
            with serial.Serial(
                port=self._com_port.text(),
                baudrate=int(self._baud_rate.currentText()),
                timeout=2,
            ):
                self._test_result.setText(f"✓ {t('connection_ok')}")
                self._test_result.setStyleSheet("color: #057A55;")
        except Exception as exc:
            self._test_result.setText(f"✗ {t('connection_failed')}: {exc}")
            self._test_result.setStyleSheet("color: #9B1C1C;")

    def _go_next(self) -> None:
        if self._current_page == 0:
            if not self._validate_page1():
                return
        elif self._current_page == 1:
            pass  # Hardware page is optional
        elif self._current_page == 2:
            if not self._validate_page3():
                return
            self._finish()
            return

        self._current_page += 1
        self._stack.setCurrentIndex(self._current_page)
        self._back_btn.setEnabled(True)
        titles = [t("setup_company"), t("setup_hardware"), t("setup_admin")]
        self._header_title.setText(titles[self._current_page])
        if self._current_page == 2:
            self._next_btn.setText(t("finish"))

    def _go_back(self) -> None:
        self._current_page -= 1
        self._stack.setCurrentIndex(self._current_page)
        self._next_btn.setText("Next →")
        self._back_btn.setEnabled(self._current_page > 0)
        titles = [t("setup_company"), t("setup_hardware"), t("setup_admin")]
        self._header_title.setText(titles[self._current_page])

    def _validate_page1(self) -> bool:
        if not self._company_name.text().strip():
            self._p1_error.setText(f"{t('company_name')} is required")
            self._p1_error.show()
            return False
        if not self._address.text().strip():
            self._p1_error.setText(f"{t('address')} is required")
            self._p1_error.show()
            return False
        if not self._phone.text().strip():
            self._p1_error.setText(f"{t('phone')} is required")
            self._p1_error.show()
            return False
        self._p1_error.hide()
        return True

    def _validate_page3(self) -> bool:
        if not self._admin_full_name.text().strip():
            self._p3_error.setText(f"{t('full_name')} is required")
            self._p3_error.show()
            return False
        if not self._admin_username.text().strip():
            self._p3_error.setText(f"{t('username')} is required")
            self._p3_error.show()
            return False
        pw = self._admin_password.text()
        valid, err, _ = validate_password(pw)
        if not valid:
            self._p3_error.setText(err)
            self._p3_error.show()
            return False
        if pw != self._admin_confirm.text():
            self._p3_error.setText(t("password_mismatch"))
            self._p3_error.show()
            return False
        self._p3_error.hide()
        return True

    def _finish(self) -> None:
        try:
            from datetime import date
            from weighmaster.database.connection import get_session
            from weighmaster.database.models import Company
            from weighmaster.services.auth_service import create_first_admin

            wma_qdate = self._wma_valid.date()
            wma_date = date(wma_qdate.year(), wma_qdate.month(), wma_qdate.day())

            with get_session() as session:
                existing = session.query(Company).first()
                if existing:
                    # Update existing company instead of creating new
                    existing.name = self._company_name.text().strip()
                    existing.address = self._address.text().strip()
                    existing.phone = self._phone.text().strip()
                    existing.email = self._email.text().strip() or None
                    existing.logo_path = self._logo_path or None
                    existing.weighbridge_capacity_kg = self._capacity.value() * 1000
                    existing.wma_cert_number = self._wma_cert.text().strip()
                    existing.wma_valid_until = wma_date
                    existing.com_port = self._com_port.text().strip()
                    existing.baud_rate = int(self._baud_rate.currentText())
                else:
                    company = Company(
                        name=self._company_name.text().strip(),
                        address=self._address.text().strip(),
                        phone=self._phone.text().strip(),
                        email=self._email.text().strip() or None,
                        logo_path=self._logo_path or None,
                        weighbridge_capacity_kg=self._capacity.value() * 1000,
                        wma_cert_number=self._wma_cert.text().strip(),
                        wma_valid_until=wma_date,
                        com_port=self._com_port.text().strip(),
                        baud_rate=int(self._baud_rate.currentText()),
                    )
                    session.add(company)
                session.commit()

            create_first_admin(
                username=self._admin_username.text().strip(),
                full_name=self._admin_full_name.text().strip(),
                password=self._admin_password.text(),
            )
            self.accept()
        except Exception as exc:
            self._p3_error.setText(str(exc))
            self._p3_error.show()

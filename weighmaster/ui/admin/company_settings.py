"""Company settings — tabbed: Company Info, Hardware, Preferences, Commodities."""
from __future__ import annotations

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QDateEdit, QDialog, QDialogButtonBox,
    QDoubleSpinBox, QFileDialog, QFormLayout, QFrame, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QPushButton, QSpinBox,
    QTableWidget, QTableWidgetItem, QTabWidget, QVBoxLayout, QWidget,
)

from weighmaster.database.models import User
from weighmaster.i18n.translator import t
from weighmaster.ui.components.dialogs import show_error, show_info


class CompanySettingsScreen(QWidget):
    def __init__(self, user: User, parent=None) -> None:
        super().__init__(parent)
        self._user = user
        self._build_ui()

    def _build_ui(self) -> None:
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 20, 24, 20)
        main.setSpacing(16)

        title = QLabel(t("company_settings"))
        title.setObjectName("PageTitle")
        main.addWidget(title)

        self._tabs = QTabWidget()
        self._tabs.addTab(self._build_info_tab(), t("company_name"))
        self._tabs.addTab(self._build_hardware_tab(), t("com_port"))
        self._tabs.addTab(self._build_prefs_tab(), t("language"))
        self._tabs.addTab(self._build_commodities_tab(), t("commodity_settings"))
        main.addWidget(self._tabs, 1)

        save_btn = QPushButton(t("save"))
        save_btn.setObjectName("BtnCapture")
        save_btn.setFixedWidth(160)
        save_btn.clicked.connect(self._save)
        main.addWidget(save_btn)

    def _build_info_tab(self) -> QWidget:
        w = QWidget()
        fl = QFormLayout(w)
        fl.setContentsMargins(20, 20, 20, 20)
        fl.setSpacing(12)

        self._name_edit = QLineEdit()
        self._address_edit = QLineEdit()
        self._phone_edit = QLineEdit()
        self._email_edit = QLineEdit()
        self._logo_path = ""

        logo_row = QHBoxLayout()
        self._logo_btn = QPushButton(t("choose_logo"))
        self._logo_btn.setObjectName("BtnSecondary")
        self._logo_btn.clicked.connect(self._pick_logo)
        self._logo_lbl = QLabel("No logo selected")
        self._logo_lbl.setObjectName("KpiLabel")
        logo_row.addWidget(self._logo_btn)
        logo_row.addWidget(self._logo_lbl)
        logo_row.addStretch()

        fl.addRow(t("company_name") + " *", self._name_edit)
        fl.addRow(t("address"), self._address_edit)
        fl.addRow(t("phone"), self._phone_edit)
        fl.addRow(t("email"), self._email_edit)
        fl.addRow(t("logo"), logo_row)
        return w

    def _build_hardware_tab(self) -> QWidget:
        w = QWidget()
        fl = QFormLayout(w)
        fl.setContentsMargins(20, 20, 20, 20)
        fl.setSpacing(12)

        self._com_edit = QLineEdit()
        self._baud_combo = QComboBox()
        for br in [1200, 2400, 4800, 9600, 19200]:
            self._baud_combo.addItem(str(br), br)

        self._protocol_combo = QComboBox()
        self._protocol_combo.addItem("XK3190-DS1", "xk3190")
        self._protocol_combo.addItem("Toledo / Mettler (SICS)", "toledo")
        self._protocol_combo.addItem("Avery Berkel", "avery")
        self._protocol_combo.addItem("Generic / Continuous", "generic")

        test_row = QHBoxLayout()
        test_btn = QPushButton(t("test_connection"))
        test_btn.setObjectName("BtnSecondary")
        test_btn.clicked.connect(self._test_connection)
        self._test_result = QLabel()
        self._test_result.setObjectName("KpiLabel")
        test_row.addWidget(test_btn)
        test_row.addWidget(self._test_result)
        test_row.addStretch()

        self._capacity_spin = QDoubleSpinBox()
        self._capacity_spin.setRange(1.0, 500.0)
        self._capacity_spin.setSuffix(" tonnes")

        self._wma_cert_edit = QLineEdit()
        self._wma_valid_edit = QDateEdit()
        self._wma_valid_edit.setCalendarPopup(True)

        fl.addRow(t("com_port"), self._com_edit)
        fl.addRow(t("baud_rate"), self._baud_combo)
        fl.addRow(t("protocol"), self._protocol_combo)
        fl.addRow("", test_row)
        fl.addRow(t("capacity"), self._capacity_spin)
        fl.addRow(t("wma_cert"), self._wma_cert_edit)
        fl.addRow(t("valid_until"), self._wma_valid_edit)
        return w

    def _build_prefs_tab(self) -> QWidget:
        w = QWidget()
        fl = QFormLayout(w)
        fl.setContentsMargins(20, 20, 20, 20)
        fl.setSpacing(12)

        self._lang_combo = QComboBox()
        self._lang_combo.addItem("English", "en")
        self._lang_combo.addItem("Kiswahili", "sw")

        self._prefix_edit = QLineEdit()
        self._prefix_edit.setMaxLength(8)

        self._currency_edit = QLineEdit()
        self._currency_edit.setMaxLength(8)

        self._manual_weight_check = QCheckBox(t("allow_manual_weight"))
        self._print_copies_spin = QSpinBox()
        self._print_copies_spin.setRange(1, 3)

        fl.addRow(t("language"), self._lang_combo)
        fl.addRow(t("ticket_prefix"), self._prefix_edit)
        fl.addRow(t("currency"), self._currency_edit)
        fl.addRow("", self._manual_weight_check)
        fl.addRow(t("print_copies"), self._print_copies_spin)
        return w

    def _build_commodities_tab(self) -> QWidget:
        w = QWidget()
        main = QVBoxLayout(w)
        main.setContentsMargins(16, 16, 16, 16)
        main.setSpacing(12)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        add_btn = QPushButton(t("add"))
        add_btn.setObjectName("BtnPrimary")
        add_btn.clicked.connect(self._add_commodity)
        btn_row.addWidget(add_btn)
        main.addLayout(btn_row)

        self._comm_table = QTableWidget()
        self._comm_table.setObjectName("TableWidget")
        cols = ["EN Name", "SW Name", "Deduction (kg)", t("price_per_tonne"), t("active"), "Sort", ""]
        self._comm_table.setColumnCount(len(cols))
        self._comm_table.setHorizontalHeaderLabels(cols)
        self._comm_table.setShowGrid(False)
        self._comm_table.verticalHeader().setVisible(False)
        self._comm_table.horizontalHeader().setStretchLastSection(True)
        self._comm_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        main.addWidget(self._comm_table, 1)
        return w

    def refresh(self) -> None:
        self._load_company()
        self._load_commodities()

    def _load_company(self) -> None:
        from weighmaster.database.connection import get_session
        from weighmaster.database.models import Company
        with get_session() as session:
            co = session.query(Company).first()
            if co is None:
                return
            name, addr, phone, email, logo_path = co.name, co.address, co.phone, co.email, co.logo_path
            com_port, baud, protocol = co.com_port, co.baud_rate, co.scale_protocol
            cap = co.weighbridge_capacity_kg / 1000
            wma = co.wma_cert_number
            wma_date = co.wma_valid_until
            lang, prefix, currency = co.language, co.ticket_prefix, co.currency
            allow_manual, copies = co.allow_manual_weight, co.print_copies

        self._name_edit.setText(name or "")
        self._address_edit.setText(addr or "")
        self._phone_edit.setText(phone or "")
        self._email_edit.setText(email or "")
        if logo_path:
            self._logo_path = logo_path
            self._logo_lbl.setText(logo_path.split("/")[-1])

        self._com_edit.setText(com_port or "COM3")
        idx = self._baud_combo.findText(str(baud))
        if idx >= 0:
            self._baud_combo.setCurrentIndex(idx)
        proto_idx = self._protocol_combo.findData(protocol)
        if proto_idx >= 0:
            self._protocol_combo.setCurrentIndex(proto_idx)
        self._capacity_spin.setValue(cap)
        self._wma_cert_edit.setText(wma or "")
        if wma_date:
            self._wma_valid_edit.setDate(QDate(wma_date.year, wma_date.month, wma_date.day))

        lang_idx = self._lang_combo.findData(lang)
        if lang_idx >= 0:
            self._lang_combo.setCurrentIndex(lang_idx)
        self._prefix_edit.setText(prefix or "WM")
        self._currency_edit.setText(currency or "TZS")
        self._manual_weight_check.setChecked(bool(allow_manual))
        self._print_copies_spin.setValue(copies or 1)

    def _load_commodities(self) -> None:
        from weighmaster.database.connection import get_session
        from weighmaster.database.models import Commodity
        with get_session() as session:
            comms = session.query(Commodity).order_by(Commodity.sort_order).all()
            data = [(c.id, c.name_en, c.name_sw, c.deduction_kg, c.price_per_tonne, c.is_active, c.sort_order)
                    for c in comms]

        self._comm_table.setRowCount(0)
        for cid, en, sw, ded, rate, active, sort in data:
            row = self._comm_table.rowCount()
            self._comm_table.insertRow(row)
            for col, val in enumerate([en, sw, f"{ded:.1f}", f"{rate:,.2f}", "✓" if active else "✗", str(sort)]):
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, cid)
                self._comm_table.setItem(row, col, item)
            btn_w = QWidget()
            bl = QHBoxLayout(btn_w)
            bl.setContentsMargins(4, 2, 4, 2)
            edit_btn = QPushButton(t("edit"))
            edit_btn.setObjectName("BtnSmall")
            edit_btn.clicked.connect(lambda _, i=cid: self._edit_commodity(i))
            bl.addWidget(edit_btn)
            bl.addStretch()
            self._comm_table.setCellWidget(row, 6, btn_w)

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
                port=self._com_edit.text(), baudrate=int(self._baud_combo.currentText()), timeout=2
            ):
                self._test_result.setText(f"✓ {t('connection_ok')}")
                self._test_result.setStyleSheet("color: #057A55;")
        except Exception as exc:
            self._test_result.setText(f"✗ {t('connection_failed')}")
            self._test_result.setStyleSheet("color: #9B1C1C;")

    def _save(self) -> None:
        from datetime import date as dt
        from weighmaster.database.connection import get_session
        from weighmaster.database.models import Company
        from weighmaster.services.audit_service import log_action

        try:
            wma_qd = self._wma_valid_edit.date()
            wma_date = dt(wma_qd.year(), wma_qd.month(), wma_qd.day())
            with get_session() as session:
                co = session.query(Company).first()
                if co is None:
                    co = Company(id=1)
                    session.add(co)
                co.name = self._name_edit.text().strip()
                co.address = self._address_edit.text().strip()
                co.phone = self._phone_edit.text().strip()
                co.email = self._email_edit.text().strip() or None
                if self._logo_path:
                    co.logo_path = self._logo_path
                co.com_port = self._com_edit.text().strip()
                co.baud_rate = int(self._baud_combo.currentText())
                co.scale_protocol = self._protocol_combo.currentData()
                co.weighbridge_capacity_kg = self._capacity_spin.value() * 1000
                co.wma_cert_number = self._wma_cert_edit.text().strip()
                co.wma_valid_until = wma_date
                co.language = self._lang_combo.currentData()
                co.ticket_prefix = self._prefix_edit.text().strip() or "WM"
                co.currency = self._currency_edit.text().strip() or "TZS"
                co.allow_manual_weight = self._manual_weight_check.isChecked()
                co.print_copies = self._print_copies_spin.value()

            log_action(self._user, "COMPANY_SETTINGS_CHANGED", "Company", entity_id=1)
            show_info(f"{t('settings')} saved.", parent=self)
        except Exception as exc:
            show_error(str(exc), parent=self)

    def _add_commodity(self) -> None:
        dlg = CommodityDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            try:
                from weighmaster.database.connection import get_session
                from weighmaster.database.models import Commodity
                with get_session() as session:
                    c = Commodity(
                        name_en=dlg.name_en, name_sw=dlg.name_sw,
                        deduction_kg=dlg.deduction_kg,
                        price_per_tonne=dlg.price_per_tonne,
                        sort_order=dlg.sort_order,
                    )
                    session.add(c)
                self._load_commodities()
            except Exception as exc:
                show_error(str(exc), parent=self)

    def _edit_commodity(self, cid: int) -> None:
        from weighmaster.database.connection import get_session
        from weighmaster.database.models import Commodity
        with get_session() as session:
            c = session.query(Commodity).filter_by(id=cid).first()
            if c is None:
                return
            dlg = CommodityDialog(
                name_en=c.name_en, name_sw=c.name_sw,
                deduction_kg=c.deduction_kg,
                price_per_tonne=c.price_per_tonne,
                sort_order=c.sort_order,
                is_active=c.is_active, parent=self,
            )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            try:
                with get_session() as session:
                    c = session.query(Commodity).filter_by(id=cid).first()
                    c.name_en = dlg.name_en
                    c.name_sw = dlg.name_sw
                    c.deduction_kg = dlg.deduction_kg
                    c.price_per_tonne = dlg.price_per_tonne
                    c.sort_order = dlg.sort_order
                    c.is_active = dlg.is_active
                self._load_commodities()
            except Exception as exc:
                show_error(str(exc), parent=self)


class CommodityDialog(QDialog):
    def __init__(self, name_en="", name_sw="", deduction_kg=0.0,
                 price_per_tonne=0.0, sort_order=0, is_active=True, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("commodity_settings"))
        self.setMinimumWidth(360)
        self.name_en = name_en
        self.name_sw = name_sw
        self.deduction_kg = deduction_kg
        self.price_per_tonne = price_per_tonne
        self.sort_order = sort_order
        self.is_active = is_active
        self._build_ui()

    def _build_ui(self) -> None:
        fl = QFormLayout(self)
        fl.setContentsMargins(20, 20, 20, 20)
        fl.setSpacing(12)

        self._en = QLineEdit(self.name_en)
        self._sw = QLineEdit(self.name_sw)
        self._ded = QDoubleSpinBox()
        self._ded.setRange(0, 9999)
        self._ded.setValue(self.deduction_kg)
        self._rate = QDoubleSpinBox()
        self._rate.setRange(0, 1_000_000_000)
        self._rate.setDecimals(2)
        self._rate.setValue(self.price_per_tonne)
        self._sort = QSpinBox()
        self._sort.setRange(0, 999)
        self._sort.setValue(self.sort_order)
        self._active_check = QCheckBox("Active")
        self._active_check.setChecked(self.is_active)

        fl.addRow("Name (EN) *", self._en)
        fl.addRow("Name (SW) *", self._sw)
        fl.addRow("Deduction (kg)", self._ded)
        fl.addRow(t("price_per_tonne"), self._rate)
        fl.addRow("Sort Order", self._sort)
        fl.addRow("", self._active_check)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        fl.addRow(buttons)

    def _validate(self) -> None:
        if not self._en.text().strip() or not self._sw.text().strip():
            return
        self.name_en = self._en.text().strip()
        self.name_sw = self._sw.text().strip()
        self.deduction_kg = self._ded.value()
        self.price_per_tonne = self._rate.value()
        self.sort_order = self._sort.value()
        self.is_active = self._active_check.isChecked()
        self.accept()

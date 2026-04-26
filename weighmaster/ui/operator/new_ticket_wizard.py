"""3-step new ticket wizard — tare capture → gross capture → print."""
from __future__ import annotations

import logging
import time
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox, QCompleter, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QProgressBar, QInputDialog, QDoubleSpinBox, QCheckBox,
    QStackedWidget, QVBoxLayout, QWidget,
)

from weighmaster.database.models import User
from weighmaster.i18n.translator import t
from weighmaster.services.weighing_service import (
    TicketSummary,
    WeighingError,
    capture_second_weight,
    capture_tare,
    get_ticket,
    list_known_plates,
    log_ticket_exception,
    suggest_vehicle_profile,
)
from weighmaster.services.auth_service import check_permission
from weighmaster.config import STABLE_DURATION_SEC, MAX_AXLES
from weighmaster.ui.components.dialogs import show_error, show_info
from weighmaster.ui.components.weight_display import WeightDisplayWidget
from weighmaster.utils.helpers import format_datetime, format_weight
from weighmaster.utils.validators import validate_plate, normalise_plate

log = logging.getLogger(__name__)


class NewTicketWizard(QWidget):
    ticket_complete = pyqtSignal(int)

    def __init__(self, user: User, parent=None) -> None:
        super().__init__(parent)
        self._user = user
        self._current_weight = 0.0
        self._is_stable = False
        self._active_ticket: Optional[TicketSummary] = None
        self._commodities: list = []
        self._overload_active = False
        self._bridge_capacity = 80_000.0
        self._currency = "TZS"
        self._stable_start: Optional[float] = None
        self._build_ui()
        self._load_commodities()
        self._load_plate_completer()
        self._load_company_settings()
        self._set_step(0)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Step pills header
        header = QWidget()
        header.setFixedHeight(56)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 12, 24, 12)
        header_layout.setSpacing(12)

        title = QLabel(t("new_ticket"))
        title.setObjectName("PageTitle")
        header_layout.addWidget(title)
        header_layout.addStretch()

        self._step_pills: list[QLabel] = []
        for i, key in enumerate(["step_vehicle", "step_gross", "step_print"]):
            pill = QLabel(f"{i+1}  {t(key)}")
            pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._step_pills.append(pill)
            header_layout.addWidget(pill)

        root.addWidget(header)

        # Divider
        div = QWidget()
        div.setFixedHeight(1)
        div.setStyleSheet("background: #E5E7EB;")
        root.addWidget(div)

        # Content stack
        self._stack = QStackedWidget()
        self._stack.addWidget(self._build_step1())
        self._stack.addWidget(self._build_step2())
        self._stack.addWidget(self._build_step3())
        root.addWidget(self._stack, 1)

    def _build_step1(self) -> QWidget:
        w = QWidget()
        outer = QVBoxLayout(w)
        outer.setContentsMargins(24, 20, 24, 20)
        outer.setSpacing(12)

        # Overload banner
        self._overload_banner = QLabel("⚠ OVERLOAD — Vehicle exceeds bridge capacity!")
        self._overload_banner.setObjectName("ErrorLabel")
        self._overload_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._overload_banner.hide()
        outer.addWidget(self._overload_banner)

        row = QHBoxLayout()
        row.setSpacing(20)

        # Form (left)
        form_frame = QFrame()
        form_frame.setObjectName("Card")
        form = QVBoxLayout(form_frame)
        form.setContentsMargins(20, 16, 20, 20)
        form.setSpacing(12)

        header_lbl = QLabel(t("step_vehicle"))
        header_lbl.setObjectName("SectionTitle")
        form.addWidget(header_lbl)

        plate_lbl = QLabel(t("vehicle_plate") + " *")
        form.addWidget(plate_lbl)
        self._plate_edit = QLineEdit()
        self._plate_edit.setObjectName("PlateInput")
        self._plate_edit.setPlaceholderText("e.g. T 245 DAR")
        self._plate_edit.textChanged.connect(self._on_plate_changed)
        form.addWidget(self._plate_edit)
        self._plate_hint = QLabel("")
        self._plate_hint.setObjectName("KpiLabel")
        self._plate_hint.hide()
        form.addWidget(self._plate_hint)

        driver_lbl = QLabel(t("driver_name") + " *")
        form.addWidget(driver_lbl)
        self._driver_edit = QLineEdit()
        self._driver_edit.setPlaceholderText(t("driver_name"))
        form.addWidget(self._driver_edit)

        commodity_lbl = QLabel(t("commodity") + " *")
        form.addWidget(commodity_lbl)
        self._commodity_combo = QComboBox()
        self._commodity_combo.currentIndexChanged.connect(self._on_commodity_changed)
        form.addWidget(self._commodity_combo)

        self._deduction_lbl = QLabel()
        self._deduction_lbl.setObjectName("KpiLabel")
        form.addWidget(self._deduction_lbl)

        rate_lbl = QLabel(t("price_per_tonne"))
        form.addWidget(rate_lbl)
        self._commodity_rate_spin = QDoubleSpinBox()
        self._commodity_rate_spin.setRange(0, 1_000_000_000)
        self._commodity_rate_spin.setDecimals(2)
        self._commodity_rate_spin.setValue(0.0)
        form.addWidget(self._commodity_rate_spin)

        self._oil_apply_check = QCheckBox(t("apply_cotton_oil"))
        self._oil_apply_check.toggled.connect(self._toggle_oil_pricing)
        form.addWidget(self._oil_apply_check)

        oil_row = QHBoxLayout()
        self._oil_km_spin = QDoubleSpinBox()
        self._oil_km_spin.setRange(0, 5000)
        self._oil_km_spin.setDecimals(1)
        self._oil_km_spin.setPrefix("KM ")
        oil_row.addWidget(self._oil_km_spin)
        self._oil_rate_spin = QDoubleSpinBox()
        self._oil_rate_spin.setRange(0, 1_000_000)
        self._oil_rate_spin.setDecimals(2)
        oil_row.addWidget(self._oil_rate_spin)
        form.addLayout(oil_row)

        direction_lbl = QLabel(t("direction") + " *")
        form.addWidget(direction_lbl)
        self._direction_combo = QComboBox()
        self._direction_combo.addItem(t("tare_first"), "tare_first")
        self._direction_combo.addItem(t("gross_first"), "gross_first")
        form.addWidget(self._direction_combo)

        # Axle count selector
        axle_row = QHBoxLayout()
        axle_lbl = QLabel(t("axle_count") + ":")
        axle_row.addWidget(axle_lbl)
        self._axle_count_spin = QComboBox()
        for i in range(1, MAX_AXLES + 1):
            self._axle_count_spin.addItem(str(i), i)
        self._axle_count_spin.currentIndexChanged.connect(self._on_axle_count_changed)
        axle_row.addWidget(self._axle_count_spin)
        axle_row.addStretch()
        form.addLayout(axle_row)

        # Axle weights input area
        self._axle_weights_frame = QFrame()
        self._axle_weights_frame.setObjectName("ManualWeightBox")
        axl = QVBoxLayout(self._axle_weights_frame)
        axl.setContentsMargins(8, 8, 8, 8)
        axl.setSpacing(4)
        axl.addWidget(QLabel(t("axle_weights")))
        self._axle_input_rows: list[QHBoxLayout] = []
        self._axle_edits: list[QLineEdit] = []
        self._axle_labels: list[QLabel] = []
        for i in range(MAX_AXLES):
            arow = QHBoxLayout()
            albl = QLabel(f"Axle {i+1}:")
            albl.hide()
            aedit = QLineEdit()
            aedit.setPlaceholderText("kg")
            aedit.hide()
            aedit.setFixedWidth(100)
            arow.addWidget(albl)
            arow.addWidget(aedit)
            arow.addStretch()
            axl.addLayout(arow)
            self._axle_labels.append(albl)
            self._axle_edits.append(aedit)
        axl.addStretch()
        self._axle_weights_frame.hide()
        form.addWidget(self._axle_weights_frame)

        customer_lbl = QLabel(t("customer"))
        form.addWidget(customer_lbl)
        self._customer_edit = QLineEdit()
        self._customer_edit.setPlaceholderText(t("customer"))
        form.addWidget(self._customer_edit)

        notes_lbl = QLabel(t("notes"))
        form.addWidget(notes_lbl)
        self._notes_edit = QLineEdit()
        self._notes_edit.setPlaceholderText(t("notes"))
        form.addWidget(self._notes_edit)

        self._s1_error = QLabel()
        self._s1_error.setObjectName("ErrorLabel")
        self._s1_error.hide()
        form.addWidget(self._s1_error)

        form.addStretch()
        row.addWidget(form_frame, 3)

        # Weight panel (right)
        weight_frame = QFrame()
        weight_frame.setObjectName("Card")
        wl = QVBoxLayout(weight_frame)
        wl.setContentsMargins(16, 16, 16, 16)
        wl.setSpacing(12)

        self._s1_weight = WeightDisplayWidget(compact=True)
        wl.addWidget(self._s1_weight)

        # Stability progress bar
        self._stability_bar = QProgressBar()
        self._stability_bar.setMaximum(100)
        self._stability_bar.setValue(0)
        self._stability_bar.setTextVisible(False)
        self._stability_bar.setFixedHeight(4)
        wl.addWidget(self._stability_bar)

        self._s1_capture_btn = QPushButton(t("capture_tare") + "  [F5]")
        self._s1_capture_btn.setObjectName("BtnCapture")
        self._s1_capture_btn.setEnabled(False)
        self._s1_capture_btn.clicked.connect(self._do_capture_tare)
        wl.addWidget(self._s1_capture_btn)

        # Manual weight button
        self._s1_manual_btn = QPushButton(t("enter_manual_weight"))
        self._s1_manual_btn.setObjectName("BtnSmall")
        self._s1_manual_btn.setToolTip("Use only when scale is faulty")
        self._s1_manual_btn.clicked.connect(self._do_manual_tare)
        wl.addWidget(self._s1_manual_btn)

        exception_row = QHBoxLayout()
        self._s1_unstable_btn = QPushButton(t("log_unstable"))
        self._s1_unstable_btn.setObjectName("BtnSmall")
        self._s1_unstable_btn.clicked.connect(self._log_unstable_exception)
        exception_row.addWidget(self._s1_unstable_btn)
        self._s1_reweigh_btn = QPushButton(t("request_reweigh"))
        self._s1_reweigh_btn.setObjectName("BtnSmall")
        self._s1_reweigh_btn.clicked.connect(self._request_reweigh)
        exception_row.addWidget(self._s1_reweigh_btn)
        wl.addLayout(exception_row)

        self._s1_wait_lbl = QLabel(t("wait_stable"))
        self._s1_wait_lbl.setObjectName("KpiLabel")
        self._s1_wait_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wl.addWidget(self._s1_wait_lbl)

        wl.addStretch()
        row.addWidget(weight_frame, 2)

        outer.addLayout(row, 1)
        return w

    def _build_step2(self) -> QWidget:
        w = QWidget()
        outer = QVBoxLayout(w)
        outer.setContentsMargins(24, 20, 24, 20)
        outer.setSpacing(12)

        # Overload banner (step 2)
        self._s2_overload_banner = QLabel("⚠ OVERLOAD — Vehicle exceeds bridge capacity!")
        self._s2_overload_banner.setObjectName("ErrorLabel")
        self._s2_overload_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._s2_overload_banner.hide()
        outer.addWidget(self._s2_overload_banner)

        row = QHBoxLayout()
        row.setSpacing(20)

        # Tare summary (left)
        summary_frame = QFrame()
        summary_frame.setObjectName("Card")
        sl = QVBoxLayout(summary_frame)
        sl.setContentsMargins(20, 16, 20, 20)
        sl.setSpacing(8)

        header_lbl = QLabel(t("step_gross"))
        header_lbl.setObjectName("SectionTitle")
        sl.addWidget(header_lbl)

        self._s2_tare_box = QFrame()
        self._s2_tare_box.setObjectName("TicketSummaryBox")
        tare_layout = QVBoxLayout(self._s2_tare_box)
        self._s2_plate_lbl = QLabel()
        self._s2_plate_lbl.setObjectName("TicketNumber")
        self._s2_commodity_lbl = QLabel()
        self._s2_tare_lbl = QLabel()
        tare_layout.addWidget(self._s2_plate_lbl)
        tare_layout.addWidget(self._s2_commodity_lbl)
        tare_layout.addWidget(self._s2_tare_lbl)
        sl.addWidget(self._s2_tare_box)

        sl.addStretch()
        row.addWidget(summary_frame, 3)

        # Weight panel (right)
        weight_frame = QFrame()
        weight_frame.setObjectName("Card")
        wl = QVBoxLayout(weight_frame)
        wl.setContentsMargins(16, 16, 16, 16)
        wl.setSpacing(12)

        self._s2_weight = WeightDisplayWidget(compact=True)
        wl.addWidget(self._s2_weight)

        self._stability_bar2 = QProgressBar()
        self._stability_bar2.setMaximum(100)
        self._stability_bar2.setValue(0)
        self._stability_bar2.setTextVisible(False)
        self._stability_bar2.setFixedHeight(4)
        wl.addWidget(self._stability_bar2)

        self._s2_capture_btn = QPushButton(t("capture_gross") + "  [F5]")
        self._s2_capture_btn.setObjectName("BtnCapture")
        self._s2_capture_btn.setEnabled(False)
        self._s2_capture_btn.clicked.connect(self._do_capture_gross)
        wl.addWidget(self._s2_capture_btn)

        self._s2_manual_btn = QPushButton(t("enter_manual_weight"))
        self._s2_manual_btn.setObjectName("BtnSmall")
        self._s2_manual_btn.setToolTip("Use only when scale is faulty")
        self._s2_manual_btn.clicked.connect(self._do_manual_gross)
        wl.addWidget(self._s2_manual_btn)

        s2_exception_row = QHBoxLayout()
        self._s2_unstable_btn = QPushButton(t("log_unstable"))
        self._s2_unstable_btn.setObjectName("BtnSmall")
        self._s2_unstable_btn.clicked.connect(self._log_unstable_exception)
        s2_exception_row.addWidget(self._s2_unstable_btn)
        self._s2_reweigh_btn = QPushButton(t("request_reweigh"))
        self._s2_reweigh_btn.setObjectName("BtnSmall")
        self._s2_reweigh_btn.clicked.connect(self._request_reweigh)
        s2_exception_row.addWidget(self._s2_reweigh_btn)
        wl.addLayout(s2_exception_row)

        self._s2_wait_lbl = QLabel(t("wait_stable"))
        self._s2_wait_lbl.setObjectName("KpiLabel")
        self._s2_wait_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wl.addWidget(self._s2_wait_lbl)

        wl.addStretch()
        row.addWidget(weight_frame, 2)

        outer.addLayout(row, 1)
        return w

    def _build_step3(self) -> QWidget:
        w = QWidget()
        outer = QVBoxLayout(w)
        outer.setContentsMargins(24, 20, 24, 20)
        outer.setSpacing(16)

        header = QLabel(t("step_print"))
        header.setObjectName("PageTitle")
        outer.addWidget(header)

        # Summary box
        self._s3_summary = QFrame()
        self._s3_summary.setObjectName("Card")
        sl = QVBoxLayout(self._s3_summary)
        sl.setContentsMargins(24, 20, 24, 20)
        sl.setSpacing(8)

        self._s3_ticket_no = QLabel()
        self._s3_ticket_no.setObjectName("TicketNumber")
        self._s3_plate = QLabel()
        self._s3_plate.setObjectName("SectionTitle")
        self._s3_driver = QLabel()
        self._s3_commodity = QLabel()
        self._s3_tare = QLabel()
        self._s3_gross = QLabel()
        self._s3_deduction = QLabel()
        self._s3_rate = QLabel()
        self._s3_oil = QLabel()
        self._s3_total_price = QLabel()
        self._s3_net = QLabel()
        self._s3_net.setObjectName("NetHero")

        for lbl in [self._s3_ticket_no, self._s3_plate, self._s3_driver,
                    self._s3_commodity, self._s3_tare, self._s3_gross,
                    self._s3_deduction, self._s3_rate, self._s3_oil,
                    self._s3_total_price, self._s3_net]:
            sl.addWidget(lbl)

        outer.addWidget(self._s3_summary)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self._print_btn = QPushButton(t("print_cert") + "  [Enter]")
        self._print_btn.setObjectName("BtnCapture")
        self._print_btn.clicked.connect(self._do_print)
        btn_row.addWidget(self._print_btn)

        self._save_pdf_btn = QPushButton(t("save_pdf"))
        self._save_pdf_btn.setObjectName("BtnSecondary")
        self._save_pdf_btn.clicked.connect(self._do_save_pdf)
        btn_row.addWidget(self._save_pdf_btn)

        self._new_ticket_btn = QPushButton(t("new_ticket") + "  [N]")
        self._new_ticket_btn.setObjectName("BtnSecondary")
        self._new_ticket_btn.clicked.connect(self._start_new)
        btn_row.addWidget(self._new_ticket_btn)

        outer.addLayout(btn_row)
        outer.addStretch()
        return w

    def _load_company_settings(self) -> None:
        try:
            from weighmaster.database.connection import get_session
            from weighmaster.database.models import Company
            with get_session() as session:
                company = session.query(Company).first()
                if company:
                    self._bridge_capacity = company.weighbridge_capacity_kg
                    self._currency = company.currency or "TZS"
            self._commodity_rate_spin.setSuffix(f" {self._currency}")
            self._oil_rate_spin.setPrefix(f"{self._currency} ")
            self._toggle_oil_pricing(self._oil_apply_check.isChecked())
        except Exception as exc:
            log.error("Failed to load company settings: %s", exc)

    def _toggle_oil_pricing(self, enabled: bool) -> None:
        self._oil_km_spin.setEnabled(enabled)
        self._oil_rate_spin.setEnabled(enabled)

    def _load_plate_completer(self) -> None:
        try:
            plates = list_known_plates()
            if not plates:
                return
            completer = QCompleter(plates)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            self._plate_edit.setCompleter(completer)
        except Exception as exc:
            log.warning("Plate completer load failed: %s", exc)

    def _ask_exception_reason(self, title: str, prompt: str) -> str:
        text, ok = QInputDialog.getText(self, title, prompt)
        if not ok:
            return ""
        return text.strip()

    def _log_unstable_exception(self) -> None:
        reason = self._ask_exception_reason(t("log_unstable"), t("manual_weight_reason"))
        if not reason:
            return
        ticket_id = self._active_ticket.id if self._active_ticket else None
        log_ticket_exception(
            self._user,
            "unstable_scale",
            reason,
            ticket_id=ticket_id,
            vehicle_plate=self._plate_edit.text(),
        )
        show_info(t("exception_saved"), parent=self)

    def _request_reweigh(self) -> None:
        reason = self._ask_exception_reason(t("request_reweigh"), t("manual_weight_reason"))
        if not reason:
            return
        ticket_id = self._active_ticket.id if self._active_ticket else None
        log_ticket_exception(
            self._user,
            "reweigh_request",
            reason,
            ticket_id=ticket_id,
            vehicle_plate=self._plate_edit.text(),
        )
        show_info(t("exception_saved"), parent=self)

    def _autofill_from_profile(self, plate: str) -> None:
        profile = suggest_vehicle_profile(plate)
        if profile is None:
            self._plate_hint.hide()
            return
        if not self._driver_edit.text().strip() and profile.get("driver_name"):
            self._driver_edit.setText(profile["driver_name"])
        if not self._customer_edit.text().strip() and profile.get("company_name"):
            self._customer_edit.setText(profile["company_name"])
        self._plate_hint.setText(t("vehicle_autofill_used"))
        self._plate_hint.show()

    def _on_axle_count_changed(self) -> None:
        count = self._axle_count_spin.currentData()
        for i in range(MAX_AXLES):
            if i < count:
                self._axle_labels[i].show()
                self._axle_edits[i].show()
            else:
                self._axle_labels[i].hide()
                self._axle_edits[i].hide()
        if count > 1:
            self._axle_weights_frame.show()
        else:
            self._axle_weights_frame.hide()

    def _get_axle_weights(self) -> list[float]:
        count = self._axle_count_spin.currentData()
        weights = []
        for i in range(count):
            text = self._axle_edits[i].text().strip()
            try:
                weights.append(float(text))
            except ValueError:
                weights.append(0.0)
        return weights

    def _do_manual_tare(self) -> None:
        if not check_permission(self._user, "manual_weight"):
            show_error("Manual weight entry is not permitted. Contact admin.", parent=self)
            return
        reason = self._ask_exception_reason(t("enter_manual_weight"), t("manual_weight_reason"))
        if not reason:
            return
        val, ok = QInputDialog.getDouble(
            self, "Manual Tare Weight", "Enter weight (kg):",
            value=0.0, min=0.0, max=999999.0, decimals=2
        )
        if ok and val > 0:
            self._current_weight = val
            self._is_stable = True
            self.update_weight(val, True, "manual")
            self._do_capture_tare(source="manual", exception_reason=reason)

    def _do_manual_gross(self) -> None:
        if not check_permission(self._user, "manual_weight"):
            show_error("Manual weight entry is not permitted. Contact admin.", parent=self)
            return
        reason = self._ask_exception_reason(t("enter_manual_weight"), t("manual_weight_reason"))
        if not reason:
            return
        val, ok = QInputDialog.getDouble(
            self, "Manual Gross Weight", "Enter weight (kg):",
            value=0.0, min=0.0, max=999999.0, decimals=2
        )
        if ok and val > 0:
            self._current_weight = val
            self._is_stable = True
            self.update_weight(val, True, "manual")
            self._do_capture_gross(source="manual", exception_reason=reason)

    def _load_commodities(self) -> None:
        try:
            from weighmaster.database.connection import get_session
            from weighmaster.database.models import Commodity
            from weighmaster.i18n.translator import get_language

            with get_session() as session:
                self._commodities = (
                    session.query(Commodity)
                    .filter_by(is_active=True)
                    .order_by(Commodity.sort_order)
                    .all()
                )

            lang = get_language()
            self._commodity_combo.blockSignals(True)
            self._commodity_combo.clear()
            for c in self._commodities:
                name = c.name_sw if lang == "sw" else c.name_en
                display = name
                if c.deduction_kg > 0:
                    display += f" (−{c.deduction_kg:.0f} kg deduction)"
                self._commodity_combo.addItem(display, c.id)
            self._commodity_combo.blockSignals(False)
            self._on_commodity_changed()
        except Exception as exc:
            log.error("Failed to load commodities: %s", exc)

    def _on_commodity_changed(self) -> None:
        idx = self._commodity_combo.currentIndex()
        if idx < 0 or idx >= len(self._commodities):
            self._deduction_lbl.setText("")
            return
        c = self._commodities[idx]
        self._commodity_rate_spin.setValue(float(getattr(c, "price_per_tonne", 0.0) or 0.0))
        if c.deduction_kg > 0:
            self._deduction_lbl.setText(f"Deduction: {c.deduction_kg:.0f} kg")
        else:
            self._deduction_lbl.setText("")
        name = f"{(c.name_en or '').lower()} {(c.name_sw or '').lower()}"
        is_cotton = ("cotton" in name) or ("pamba" in name)
        self._oil_apply_check.setChecked(is_cotton)

    def _on_plate_changed(self, text: str) -> None:
        upper = text.upper()
        if upper != text:
            pos = self._plate_edit.cursorPosition()
            self._plate_edit.blockSignals(True)
            self._plate_edit.setText(upper)
            self._plate_edit.setCursorPosition(pos)
            self._plate_edit.blockSignals(False)
        if len(upper.strip()) >= 3:
            self._autofill_from_profile(upper)

    def _set_step(self, step: int) -> None:
        self._stack.setCurrentIndex(step)
        names = ["StepActive", "StepPending", "StepPending"]
        if step == 0:
            names = ["StepActive", "StepPending", "StepPending"]
        elif step == 1:
            names = ["StepDone", "StepActive", "StepPending"]
        elif step == 2:
            names = ["StepDone", "StepDone", "StepActive"]

        for pill, name in zip(self._step_pills, names):
            pill.setObjectName(name)
            pill.style().unpolish(pill)
            pill.style().polish(pill)

    def update_weight(self, weight_kg: float, is_stable: bool, status: str) -> None:
        self._current_weight = weight_kg
        self._is_stable = is_stable

        self._s1_weight.update_weight(weight_kg, is_stable, status)
        self._s2_weight.update_weight(weight_kg, is_stable, status)

        # Overload detection
        is_overload = weight_kg > self._bridge_capacity or status == "overload"
        self._overload_active = is_overload
        if is_overload:
            self._overload_banner.setText(
                f"⚠ OVERLOAD — {weight_kg:,.0f} kg exceeds capacity ({self._bridge_capacity:,.0f} kg)"
            )
            self._overload_banner.show()
            self._s2_overload_banner.setText(
                f"⚠ OVERLOAD — {weight_kg:,.0f} kg exceeds capacity ({self._bridge_capacity:,.0f} kg)"
            )
            self._s2_overload_banner.show()
        else:
            self._overload_banner.hide()
            self._s2_overload_banner.hide()

        # Enable capture only when stable AND not overloaded
        can_capture = is_stable and not is_overload and status != "overload"
        self._s1_capture_btn.setEnabled(can_capture)
        self._s2_capture_btn.setEnabled(can_capture)

        # Stability progress bar
        if is_stable:
            self._stability_bar.setValue(100)
            self._stability_bar2.setValue(100)
            self._stable_start = None
        else:
            if self._stable_start is None:
                self._stable_start = time.monotonic()
            elapsed = time.monotonic() - self._stable_start
            pct = min(100, int((elapsed / STABLE_DURATION_SEC) * 100))
            self._stability_bar.setValue(pct)
            self._stability_bar2.setValue(pct)

        if is_stable:
            self._s1_wait_lbl.hide()
            self._s2_wait_lbl.hide()
        else:
            self._s1_wait_lbl.show()
            self._s2_wait_lbl.show()

    def _do_capture_tare(self, source: str = "auto", exception_reason: str = "") -> None:
        plate = self._plate_edit.text().strip()
        valid, err = validate_plate(plate)
        if not valid:
            self._s1_error.setText(err)
            self._s1_error.show()
            return

        driver = self._driver_edit.text().strip()
        if not driver:
            self._s1_error.setText(f"{t('driver_name')} is required")
            self._s1_error.show()
            return

        idx = self._commodity_combo.currentIndex()
        if idx < 0:
            self._s1_error.setText(f"{t('commodity')} is required")
            self._s1_error.show()
            return

        commodity_id = self._commodity_combo.itemData(idx)
        self._s1_error.hide()

        try:
            axle_weights = self._get_axle_weights() if self._axle_count_spin.currentData() > 1 else None
            ticket = capture_tare(
                operator=self._user,
                vehicle_plate=normalise_plate(plate),
                driver_name=driver,
                commodity_id=commodity_id,
                company_name=self._customer_edit.text().strip(),
                weight_kg=self._current_weight,
                source=source,
                notes=self._notes_edit.text().strip(),
                axle_count=self._axle_count_spin.currentData(),
                axle_weights=axle_weights,
                weighing_mode=self._direction_combo.currentData(),
                exception_reason=exception_reason,
                commodity_rate_per_tonne=self._commodity_rate_spin.value(),
                oil_distance_km=self._oil_km_spin.value(),
                oil_rate_per_km=self._oil_rate_spin.value(),
                apply_oil_pricing=self._oil_apply_check.isChecked(),
            )
            self._active_ticket = ticket
            self._populate_step2(ticket)
            self._set_step(1)
        except WeighingError as exc:
            self._s1_error.setText(str(exc))
            self._s1_error.show()
        except Exception as exc:
            show_error(str(exc), parent=self)

    def _populate_step2(self, ticket: TicketSummary) -> None:
        self._s2_plate_lbl.setText(f"{ticket.ticket_number}  ·  {ticket.vehicle_plate}")
        self._s2_commodity_lbl.setText(ticket.commodity_name)
        self._s2_tare_lbl.setText(
            f"✓ Tare: {format_weight(ticket.tare_weight)} kg @ {format_datetime(ticket.tare_datetime, '%H:%M')}"
        )

    def _legacy_do_capture_gross(self) -> None:
        if self._active_ticket is None:
            return
        try:
            axle_weights = self._get_axle_weights() if self._axle_count_spin.currentData() > 1 else None
            ticket = capture_gross(
                operator=self._user,
                ticket_id=self._active_ticket.id,
                weight_kg=self._current_weight,
                source="auto",
                axle_weights=axle_weights,
            )
            self._active_ticket = ticket
            self._populate_step3(ticket)
            self._set_step(2)
        except WeighingError as exc:
            show_error(str(exc), parent=self)
        except Exception as exc:
            show_error(str(exc), parent=self)

    def _populate_step2(self, ticket: TicketSummary) -> None:
        self._s2_plate_lbl.setText(f"{ticket.ticket_number}  -  {ticket.vehicle_plate}")
        self._s2_commodity_lbl.setText(ticket.commodity_name)
        if ticket.pending_stage == "awaiting_tare":
            self._s2_tare_lbl.setText(
                f"{t('awaiting_tare')}: {format_weight(ticket.gross_weight)} kg @ "
                f"{format_datetime(ticket.gross_datetime, '%H:%M')}"
            )
            self._s2_capture_btn.setText(t("capture_tare") + "  [F5]")
        else:
            self._s2_tare_lbl.setText(
                f"{t('awaiting_gross')}: {format_weight(ticket.tare_weight)} kg @ "
                f"{format_datetime(ticket.tare_datetime, '%H:%M')}"
            )
            self._s2_capture_btn.setText(t("capture_gross") + "  [F5]")

    def _do_capture_gross(self, source: str = "auto", exception_reason: str = "") -> None:
        if self._active_ticket is None:
            return
        try:
            axle_weights = self._get_axle_weights() if self._axle_count_spin.currentData() > 1 else None
            ticket = capture_second_weight(
                operator=self._user,
                ticket_id=self._active_ticket.id,
                weight_kg=self._current_weight,
                source=source,
                axle_weights=axle_weights,
                exception_reason=exception_reason,
            )
            self._active_ticket = ticket
            self._populate_step3(ticket)
            self._set_step(2)
        except WeighingError as exc:
            show_error(str(exc), parent=self)
        except Exception as exc:
            show_error(str(exc), parent=self)

    def _populate_step3(self, ticket: TicketSummary) -> None:
        self._s3_ticket_no.setText(ticket.ticket_number)
        self._s3_plate.setText(ticket.vehicle_plate)
        self._s3_driver.setText(f"{t('driver_name')}: {ticket.driver_name}")
        self._s3_commodity.setText(f"{t('commodity')}: {ticket.commodity_name}")
        self._s3_tare.setText(f"{t('tare_weight')}: {format_weight(ticket.tare_weight)} kg @ {format_datetime(ticket.tare_datetime, '%H:%M')}")
        self._s3_gross.setText(f"{t('gross_weight')}: {format_weight(ticket.gross_weight)} kg @ {format_datetime(ticket.gross_datetime, '%H:%M')}")
        self._s3_deduction.setText(f"{t('deduction')}: {format_weight(ticket.deduction_kg)} kg")
        self._s3_rate.setText(
            f"{t('price_per_tonne')}: {ticket.commodity_rate_per_tonne:,.2f} {self._currency} | "
            f"{t('commodity_value')}: {float(ticket.commodity_value or 0.0):,.2f} {self._currency}"
        )
        self._s3_oil.setText(
            f"{t('oil_distance_km')}: {ticket.oil_distance_km:,.1f} | "
            f"{t('oil_rate_per_km')}: {ticket.oil_rate_per_km:,.2f} {self._currency} | "
            f"{t('oil_price')}: {float(ticket.oil_price or 0.0):,.2f} {self._currency}"
        )
        self._s3_total_price.setText(
            f"{t('total_price')}: {float(ticket.total_price or 0.0):,.2f} {self._currency}"
        )
        self._s3_net.setText(f"{t('net_weight')}: {format_weight(ticket.net_weight)} kg  ({ticket.net_weight/1000:,.3f} t)")

    def _do_print(self) -> None:
        if self._active_ticket is None:
            return
        self._generate_pdf(open_after=True)

    def _do_save_pdf(self) -> None:
        if self._active_ticket is None:
            return
        self._generate_pdf(open_after=False)

    def _generate_pdf(self, open_after: bool) -> None:
        try:
            from weighmaster.pdf.certificate import CertificateGenerator
            from weighmaster.database.connection import get_session
            from weighmaster.database.models import Company, WeighTicket
            from weighmaster.config import PDF_OUTPUT_DIR
            import os

            PDF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            out_path = str(PDF_OUTPUT_DIR / f"{self._active_ticket.ticket_number}.pdf")

            with get_session() as session:
                company = session.query(Company).first()
                ticket_orm = session.query(WeighTicket).filter_by(id=self._active_ticket.id).first()
                gen = CertificateGenerator()
                gen.generate(ticket_orm, company, out_path)

            if open_after:
                import subprocess, sys
                if sys.platform == "win32":
                    os.startfile(out_path)
                else:
                    subprocess.Popen(["xdg-open", out_path])
            show_info(f"PDF saved: {out_path}", parent=self)
        except Exception as exc:
            show_error(str(exc), parent=self)

    def _start_new(self) -> None:
        self._active_ticket = None
        self._plate_edit.clear()
        self._plate_hint.hide()
        self._driver_edit.clear()
        self._customer_edit.clear()
        self._notes_edit.clear()
        self._s1_error.hide()
        self._overload_banner.hide()
        self._s2_overload_banner.hide()
        self._stable_start = None
        self._stability_bar.setValue(0)
        self._stability_bar2.setValue(0)
        self._axle_count_spin.setCurrentIndex(0)
        self._direction_combo.setCurrentIndex(0)
        self._commodity_rate_spin.setValue(0.0)
        self._oil_apply_check.setChecked(False)
        self._oil_km_spin.setValue(0.0)
        self._oil_rate_spin.setValue(0.0)
        for edit in self._axle_edits:
            edit.clear()
        self._set_step(0)

    def open_step2(self, ticket_id: int) -> None:
        ticket = get_ticket(ticket_id)
        if ticket is None:
            return
        self._active_ticket = ticket
        self._plate_edit.setText(ticket.vehicle_plate)
        self._driver_edit.setText(ticket.driver_name)
        self._customer_edit.setText(ticket.company_name)
        idx = self._direction_combo.findData(ticket.weighing_mode)
        if idx >= 0:
            self._direction_combo.setCurrentIndex(idx)
        self._populate_step2(ticket)
        self._set_step(1)

    def refresh(self) -> None:
        self._load_commodities()
        self._load_plate_completer()

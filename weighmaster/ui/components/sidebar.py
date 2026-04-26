"""CollapsibleSidebar with role-based navigation."""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget,
)

from weighmaster.database.models import User
from weighmaster.i18n.translator import t


class CollapsibleSidebar(QWidget):
    nav_requested = pyqtSignal(str)  # screen name

    def __init__(self, user: User, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(208)
        self._user = user
        self._buttons: dict[str, QPushButton] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(64)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 8)
        app_label = QLabel(t("app_name"))
        app_label.setObjectName("SectionTitle")
        sub_label = QLabel(t("app_subtitle"))
        sub_label.setObjectName("CompanyBadge")
        header_layout.addWidget(app_label)
        header_layout.addWidget(sub_label)
        layout.addWidget(header)

        # Separator
        sep = QWidget()
        sep.setObjectName("SidebarDivider")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        layout.addSpacing(8)

        # Operator section
        op_section = QLabel("OPERATOR")
        op_section.setObjectName("SidebarSection")
        layout.addWidget(op_section)

        self._add_nav(layout, "dashboard", t("dashboard"), "F1")
        self._add_nav(layout, "new_ticket", t("new_ticket"), "F2")
        self._add_nav(layout, "pending", t("pending_step2"), "F3")
        self._add_nav(layout, "history", t("ticket_history"), "F4")
        self._add_nav(layout, "vehicle_lookup", t("vehicle_history"), "F5")
        self._add_nav(layout, "gate", t("gate_queue"), "F10")

        # Admin section
        if self._user.role == "admin":
            layout.addSpacing(8)
            admin_section = QLabel("ADMIN")
            admin_section.setObjectName("SidebarSection")
            layout.addWidget(admin_section)

            self._add_nav(layout, "users", t("user_management"), "F6")
            self._add_nav(layout, "reports", t("reports"), "F7")
            self._add_nav(layout, "settings", t("settings"), "F8")
            self._add_nav(layout, "audit", t("audit_log"), "F9")

        layout.addStretch()

        # Footer — user info + logout
        footer = QWidget()
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(16, 8, 16, 12)
        footer_layout.setSpacing(4)

        sep2 = QWidget()
        sep2.setObjectName("SidebarDivider")
        sep2.setFixedHeight(1)
        layout.addWidget(sep2)

        name_label = QLabel(self._user.full_name)
        name_label.setObjectName("SectionTitle")
        role_label = QLabel(self._user.role.capitalize())
        role_label.setObjectName("CompanyBadge")
        footer_layout.addWidget(name_label)
        footer_layout.addWidget(role_label)

        logout_btn = QPushButton(t("logout"))
        logout_btn.setObjectName("BtnSecondary")
        logout_btn.clicked.connect(lambda: self.nav_requested.emit("logout"))
        footer_layout.addWidget(logout_btn)
        layout.addWidget(footer)

    def _add_nav(self, layout: QVBoxLayout, key: str, label: str, shortcut: str) -> None:
        btn = QPushButton(f"  {label}  [{shortcut}]")
        btn.setObjectName("NavItem")
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.clicked.connect(lambda checked, k=key: self.nav_requested.emit(k))
        layout.addWidget(btn)
        self._buttons[key] = btn

    def set_active(self, key: str) -> None:
        for k, btn in self._buttons.items():
            btn.setChecked(k == key)

    def set_pending_count(self, count: int) -> None:
        btn = self._buttons.get("pending")
        if btn is None:
            return
        base = t("pending_step2")
        if count > 0:
            btn.setText(f"  {base}  [{count}]")
        else:
            btn.setText(f"  {base}  [F3]")

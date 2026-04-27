"""Slim sidebar navigation — cargo-dashboard inspired."""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout,
)

from weighmaster.database.models import User
from weighmaster.i18n.translator import t

NAV_ICONS = {
    "dashboard":      "▣",
    "new_ticket":     "+",
    "pending":        "◎",
    "history":        "≡",
    "vehicle_lookup": "⊙",
    "gate":           "▷",
    "users":          "⊞",
    "reports":        "▤",
    "settings":       "⚙",
    "audit":          "☰",
}


class SidebarButton(QPushButton):
    def __init__(self, key: str, label: str, shortcut: str, parent=None) -> None:
        super().__init__(parent)
        self._key = key
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("NavItem")

        icon = NAV_ICONS.get(key, "•")
        self.setText(f"{icon}  {label}")
        self.setToolTip(f"{label}  [{shortcut}]")

        self._badge = QLabel(self)
        self._badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._badge.hide()
        self._badge.setMinimumWidth(18)
        self._badge.setFixedHeight(16)
        self._badge.setStyleSheet(
            "background-color: #EF4444; color: white; border-radius: 8px; "
            "font-size: 9px; font-weight: 700; padding: 0 5px;"
        )

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._badge.move(self.width() - 28, (self.height() - 16) // 2)

    def set_badge(self, count: int) -> None:
        if count > 0:
            self._badge.setText(str(count))
            self._badge.show()
        else:
            self._badge.hide()


class CollapsibleSidebar(QWidget):
    nav_requested = pyqtSignal(str)

    def __init__(self, user: User, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(188)
        self._user = user
        self._buttons: dict[str, SidebarButton] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(0)

        # Role badge row
        role_row = QWidget()
        rr = QHBoxLayout(role_row)
        rr.setContentsMargins(14, 2, 14, 6)
        role_pill = QLabel(self._user.role.upper())
        role_pill.setStyleSheet(
            "background-color: #EEF2FF; color: #4F46E5; border-radius: 4px; "
            "font-size: 9px; font-weight: 700; padding: 2px 7px; letter-spacing: 0.5px;"
        )
        rr.addWidget(role_pill)
        rr.addStretch()
        layout.addWidget(role_row)

        # Operator section
        op_section = QLabel(t("operator"))
        op_section.setObjectName("SidebarSection")
        layout.addWidget(op_section)

        self._add_nav(layout, "dashboard",      t("dashboard"),      "F1")
        self._add_nav(layout, "new_ticket",     t("new_ticket"),     "F2")
        self._add_nav(layout, "pending",        t("pending_step2"),  "F3")
        self._add_nav(layout, "history",        t("ticket_history"), "F4")
        self._add_nav(layout, "vehicle_lookup", t("vehicle_history"), "F5")
        self._add_nav(layout, "gate",           t("gate_queue"),     "F10")

        if self._user.role == "admin":
            layout.addSpacing(4)
            sep = QWidget()
            sep.setFixedHeight(1)
            sep.setStyleSheet("background: #E2E8F0; margin: 0 10px;")
            layout.addWidget(sep)
            layout.addSpacing(2)

            admin_section = QLabel(t("admin"))
            admin_section.setObjectName("SidebarSection")
            layout.addWidget(admin_section)

            self._add_nav(layout, "users",    t("user_management"), "F6")
            self._add_nav(layout, "reports",  t("reports"),         "F7")
            self._add_nav(layout, "settings", t("settings"),        "F8")
            self._add_nav(layout, "audit",    t("audit_log"),       "F9")

        layout.addStretch()

        sep_bot = QWidget()
        sep_bot.setFixedHeight(1)
        sep_bot.setStyleSheet("background: #E2E8F0;")
        layout.addWidget(sep_bot)

        # Logout
        footer = QWidget()
        fl = QVBoxLayout(footer)
        fl.setContentsMargins(8, 6, 8, 8)
        fl.setSpacing(0)

        logout_btn = QPushButton("⊘  " + t("logout"))
        logout_btn.setObjectName("BtnSecondary")
        logout_btn.setStyleSheet("font-size: 12px; min-height: 30px; border-radius: 6px;")
        logout_btn.clicked.connect(lambda: self.nav_requested.emit("logout"))
        fl.addWidget(logout_btn)
        layout.addWidget(footer)

    def _add_nav(self, layout: QVBoxLayout, key: str, label: str, shortcut: str) -> None:
        btn = SidebarButton(key, label, shortcut)
        btn.clicked.connect(lambda checked, k=key: self.nav_requested.emit(k))
        layout.addWidget(btn)
        self._buttons[key] = btn

    def set_active(self, key: str) -> None:
        for k, btn in self._buttons.items():
            btn.setChecked(k == key)

    def set_pending_count(self, count: int) -> None:
        btn = self._buttons.get("pending")
        if btn:
            btn.set_badge(count)

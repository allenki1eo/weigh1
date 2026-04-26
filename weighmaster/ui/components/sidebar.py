"""Modern minimal sidebar with icon badges."""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget,
    QHBoxLayout,
)

from weighmaster.database.models import User
from weighmaster.i18n.translator import t

# Unicode icons for each nav item
NAV_ICONS = {
    "dashboard": "◈",
    "new_ticket": "⊕",
    "pending": "◎",
    "history": "☰",
    "vehicle_lookup": "🔍",
    "gate": "▣",
    "users": "👤",
    "reports": "▤",
    "settings": "⚙",
    "audit": "⊕",
}


class SidebarButton(QPushButton):
    """Single nav button with icon + label."""

    def __init__(self, key: str, label: str, shortcut: str, parent=None) -> None:
        super().__init__(parent)
        self._key = key
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("NavItem")

        icon = NAV_ICONS.get(key, "•")
        self.setText(f"{icon}  {label}  [{shortcut}]")

        # Badge label overlay (pending count)
        self._badge = QLabel(self)
        self._badge.setObjectName("PillRed")
        self._badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._badge.hide()
        self._badge.setMinimumWidth(20)
        self._badge.setFixedHeight(18)
        self._badge.setStyleSheet(
            "background-color: #EF4444; color: white; border-radius: 9px; "
            "font-size: 9px; font-weight: 700; padding: 0 6px;"
        )

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        # Position badge at right side
        self._badge.move(self.width() - 36, (self.height() - 18) // 2)

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
        self.setFixedWidth(220)
        self._user = user
        self._buttons: dict[str, SidebarButton] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header with logo area
        header = QWidget()
        header.setFixedHeight(72)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 0, 16, 0)
        hl.setSpacing(8)

        logo = QLabel("◈")
        logo.setStyleSheet(
            f"font-size: 22px; color: #4F46E5; background: transparent; font-weight: bold;"
        )
        hl.addWidget(logo)

        app_label = QLabel(t("app_name"))
        app_label.setStyleSheet(
            "font-size: 15px; font-weight: 700; color: #111827; background: transparent;"
            "font-family: 'Inter', 'DM Sans', sans-serif;"
        )
        hl.addWidget(app_label)
        hl.addStretch()
        layout.addWidget(header)

        # Subtle separator
        sep_line = QWidget()
        sep_line.setFixedHeight(1)
        sep_line.setStyleSheet("background-color: #E5E7EB;")
        sep_line.setContentsMargins(16, 0, 16, 0)
        layout.addWidget(sep_line)
        layout.addSpacing(8)

        # Operator section
        op_section = QLabel(t("operator"))
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
            admin_section = QLabel(t("admin"))
            admin_section.setObjectName("SidebarSection")
            layout.addWidget(admin_section)

            self._add_nav(layout, "users", t("user_management"), "F6")
            self._add_nav(layout, "reports", t("reports"), "F7")
            self._add_nav(layout, "settings", t("settings"), "F8")
            self._add_nav(layout, "audit", t("audit_log"), "F9")

        layout.addStretch()

        # Separator before footer
        sep2 = QWidget()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet("background-color: #E5E7EB;")
        layout.addWidget(sep2)
        layout.addSpacing(4)

        # Footer — user pill + logout
        footer = QWidget()
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(16, 8, 16, 12)
        footer_layout.setSpacing(8)

        # User pill
        user_pill = QFrame()
        user_pill.setStyleSheet(
            "background-color: #F3F4F6; border-radius: 10px; border: 1px solid #E5E7EB;"
        )
        user_pill.setFixedHeight(44)
        up_layout = QHBoxLayout(user_pill)
        up_layout.setContentsMargins(12, 0, 12, 0)
        up_layout.setSpacing(8)

        avatar = QLabel("👤")
        avatar.setStyleSheet("font-size: 16px; background: transparent;")
        up_layout.addWidget(avatar)

        user_info = QVBoxLayout()
        user_info.setSpacing(0)
        user_info.setContentsMargins(0, 0, 0, 0)
        name_label = QLabel(self._user.full_name)
        name_label.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #111827; background: transparent;"
        )
        role_label = QLabel(self._user.role.capitalize())
        role_label.setStyleSheet(
            "font-size: 10px; color: #6B7280; background: transparent;"
        )
        user_info.addWidget(name_label)
        user_info.addWidget(role_label)
        up_layout.addLayout(user_info)
        up_layout.addStretch()

        footer_layout.addWidget(user_pill)

        logout_btn = QPushButton("⊘  " + t("logout"))
        logout_btn.setObjectName("BtnSecondary")
        logout_btn.setStyleSheet(
            logout_btn.styleSheet() + "font-size: 12px; min-height: 36px;"
        )
        logout_btn.clicked.connect(lambda: self.nav_requested.emit("logout"))
        footer_layout.addWidget(logout_btn)
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
        if btn is None:
            return
        btn.set_badge(count)

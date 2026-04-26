"""Root QMainWindow with sidebar + stacked content area + session timeout."""
from __future__ import annotations

import logging
import time

from PyQt6.QtCore import Qt, pyqtSlot, QTimer, QEvent
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget,
    QVBoxLayout, QWidget,
)

from weighmaster.config import WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, SESSION_TIMEOUT_MIN
from weighmaster.database.models import User
from weighmaster.i18n.translator import t
from weighmaster.ui.components.sidebar import CollapsibleSidebar
from weighmaster.ui.components.scale_status_bar import ScaleStatusBar

log = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, user: User, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("app_name"))
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self._user = user
        self._current_weight = 0.0
        self._is_stable = False
        self._scale_thread = None
        self._screens: dict[str, QWidget] = {}
        self._last_activity = time.monotonic()
        self._lock_overlay: QWidget | None = None
        self._build_ui()
        self._navigate("dashboard")
        self._setup_shortcuts()
        self._setup_session_timeout()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Main content (sidebar + stack)
        content_row = QHBoxLayout()
        content_row.setContentsMargins(0, 0, 0, 0)
        content_row.setSpacing(0)

        self._sidebar = CollapsibleSidebar(user=self._user)
        self._sidebar.nav_requested.connect(self._on_nav)
        content_row.addWidget(self._sidebar)

        self._stack = QStackedWidget()
        content_row.addWidget(self._stack, 1)
        root_layout.addLayout(content_row, 1)

        # Status bar (always visible, full width)
        self._status_bar = ScaleStatusBar(user=self._user)
        root_layout.addWidget(self._status_bar)

    def _get_screen(self, key: str) -> QWidget:
        if key not in self._screens:
            screen = self._create_screen(key)
            if screen:
                self._screens[key] = screen
                self._stack.addWidget(screen)
        return self._screens.get(key)

    def _create_screen(self, key: str) -> QWidget | None:
        if key == "dashboard":
            if self._user.role == "admin":
                from weighmaster.ui.admin.dashboard import AdminDashboard
                s = AdminDashboard(user=self._user)
                s.reports_requested.connect(lambda r: self._navigate("reports"))
                return s
            from weighmaster.ui.operator.dashboard import OperatorDashboard
            s = OperatorDashboard(user=self._user)
            s.new_ticket_requested.connect(lambda: self._navigate("new_ticket"))
            s.pending_requested.connect(lambda: self._navigate("pending"))
            return s

        if key == "new_ticket":
            from weighmaster.ui.operator.new_ticket_wizard import NewTicketWizard
            s = NewTicketWizard(user=self._user)
            s.ticket_complete.connect(self._on_ticket_complete)
            return s

        if key == "pending":
            from weighmaster.ui.operator.pending_tickets import PendingTicketsScreen
            s = PendingTicketsScreen(user=self._user)
            s.open_step2.connect(self._open_step2)
            return s

        if key == "history":
            from weighmaster.ui.operator.ticket_history import TicketHistoryScreen
            return TicketHistoryScreen(user=self._user)

        if key == "gate":
            from weighmaster.ui.operator.gate_queue import GateQueueScreen
            s = GateQueueScreen(user=self._user)
            s.open_step2.connect(self._open_step2)
            return s

        if key == "vehicle_lookup":
            from weighmaster.ui.operator.vehicle_lookup import VehicleLookupScreen
            return VehicleLookupScreen(user=self._user)

        if key == "users" and self._user.role == "admin":
            from weighmaster.ui.admin.user_management import UserManagementScreen
            return UserManagementScreen(user=self._user)

        if key == "reports" and self._user.role == "admin":
            from weighmaster.ui.admin.reports import ReportsScreen
            return ReportsScreen(user=self._user)

        if key == "settings" and self._user.role == "admin":
            from weighmaster.ui.admin.company_settings import CompanySettingsScreen
            return CompanySettingsScreen(user=self._user)

        if key == "audit" and self._user.role == "admin":
            from weighmaster.ui.admin.audit_log import AuditLogScreen
            return AuditLogScreen(user=self._user)

        return None

    def _navigate(self, key: str) -> None:
        if key == "logout":
            self._do_logout()
            return
        screen = self._get_screen(key)
        if screen is None:
            return
        self._stack.setCurrentWidget(screen)
        self._sidebar.set_active(key)
        self._refresh_screen(key)

    def _refresh_screen(self, key: str) -> None:
        screen = self._screens.get(key)
        if screen and hasattr(screen, "refresh"):
            screen.refresh()

        # Update pending badge
        try:
            from weighmaster.services.weighing_service import get_pending_tickets
            count = len(get_pending_tickets())
            self._sidebar.set_pending_count(count)
        except Exception:
            pass

    def _on_nav(self, key: str) -> None:
        self._navigate(key)

    def _on_ticket_complete(self, ticket_id: int) -> None:
        self._navigate("history")

    def _open_step2(self, ticket_id: int) -> None:
        key = "new_ticket"
        screen = self._get_screen(key)
        if screen and hasattr(screen, "open_step2"):
            screen.open_step2(ticket_id)
        self._navigate(key)

    def _do_logout(self) -> None:
        from weighmaster.ui.components.dialogs import ConfirmDialog
        dlg = ConfirmDialog("Are you sure you want to log out?", "Logout", self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            self.close()

    def _setup_shortcuts(self) -> None:
        from PyQt6.QtGui import QShortcut, QKeySequence
        shortcuts = {
            "F1": "dashboard",
            "F2": "new_ticket",
            "F3": "pending",
            "F4": "history",
            "F5": "vehicle_lookup",
            "F10": "gate",
            "F6": "users",
            "F7": "reports",
            "F8": "settings",
            "F9": "audit",
        }
        for key, screen in shortcuts.items():
            sc = QShortcut(QKeySequence(key), self)
            sc.activated.connect(lambda s=screen: self._navigate(s))

    @pyqtSlot(float, bool, str)
    def on_weight_updated(self, weight_kg: float, is_stable: bool, status: str) -> None:
        self._current_weight = weight_kg
        self._is_stable = is_stable
        for screen in self._screens.values():
            if hasattr(screen, "update_weight"):
                screen.update_weight(weight_kg, is_stable, status)

    @pyqtSlot(str)
    def on_scale_connected(self, port: str) -> None:
        self._status_bar.set_connected(port)

    @pyqtSlot(str)
    def on_scale_disconnected(self, msg: str) -> None:
        self._status_bar.set_disconnected()

    def _setup_session_timeout(self) -> None:
        """Start timers for inactivity detection and warning."""
        timeout_sec = SESSION_TIMEOUT_MIN * 60
        warn_sec = max(30, timeout_sec - 60)  # warn 1 min before lock, min 30s

        # Activity tracking via event filter
        self.installEventFilter(self)
        for widget in self.findChildren(QWidget):
            widget.installEventFilter(self)

        # Warning timer (1 min before lock)
        self._warn_timer = QTimer(self)
        self._warn_timer.timeout.connect(self._check_inactivity_warning)
        self._warn_timer.start(max(5000, (warn_sec // 5) * 1000))  # check every 1/5th of warn period

        # Lock timer
        self._lock_timer = QTimer(self)
        self._lock_timer.timeout.connect(self._check_lock)
        self._lock_timer.start(10000)  # check every 10 seconds

    def eventFilter(self, watched, event: QEvent) -> bool:
        """Reset inactivity timer on user input."""
        if event.type() in (
            QEvent.Type.MouseButtonPress,
            QEvent.Type.MouseButtonRelease,
            QEvent.Type.MouseMove,
            QEvent.Type.KeyPress,
            QEvent.Type.KeyRelease,
            QEvent.Type.Wheel,
            QEvent.Type.TouchBegin,
            QEvent.Type.TouchUpdate,
            QEvent.Type.TouchEnd,
        ):
            self._last_activity = time.monotonic()
            if self._lock_overlay is not None:
                self._unlock_session()
        return super().eventFilter(watched, event)

    def _check_inactivity_warning(self) -> None:
        if self._lock_overlay is not None:
            return
        idle = time.monotonic() - self._last_activity
        timeout_sec = SESSION_TIMEOUT_MIN * 60
        if idle >= timeout_sec - 60:
            log.warning("Session timeout warning — %ds until lock", int(timeout_sec - idle))
            self._status_bar.set_message(
                f"Session will lock in {int(timeout_sec - idle)}s — move mouse or press key to stay logged in"
            )

    def _check_lock(self) -> None:
        if self._lock_overlay is not None:
            return
        idle = time.monotonic() - self._last_activity
        if idle >= SESSION_TIMEOUT_MIN * 60:
            log.info("Session locked due to inactivity (%d min)", SESSION_TIMEOUT_MIN)
            self._show_lock_overlay()

    def _show_lock_overlay(self) -> None:
        """Show a full-screen overlay requiring re-authentication."""
        if self._lock_overlay is not None:
            return

        overlay = QWidget(self.centralWidget())
        overlay.setGeometry(self.centralWidget().rect())
        overlay.setStyleSheet("background-color: rgba(15, 23, 42, 0.85);")
        overlay.setAutoFillBackground(True)

        layout = QVBoxLayout(overlay)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel("🔒")
        icon.setStyleSheet("font-size: 48px; color: white; background: transparent;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        msg = QLabel("Session Locked Due to Inactivity")
        msg.setStyleSheet("font-size: 18px; font-weight: 600; color: white; background: transparent;")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(msg)

        sub = QLabel(f"Logged in as: {self._user.full_name}")
        sub.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.7); background: transparent;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        btn = QPushButton("Click to Unlock")
        btn.setStyleSheet(
            "background-color: #2563EB; color: white; border: none; "
            "border-radius: 8px; padding: 12px 32px; font-size: 14px; font-weight: 600;"
        )
        btn.clicked.connect(self._unlock_session)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        overlay.show()
        overlay.raise_()
        self._lock_overlay = overlay

    def _unlock_session(self) -> None:
        """Show login dialog to re-authenticate before removing overlay."""
        if self._lock_overlay is None:
            return

        from weighmaster.ui.windows.login_window import LoginWindow
        dlg = LoginWindow(parent=self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            self._last_activity = time.monotonic()
            if self._lock_overlay:
                self._lock_overlay.hide()
                self._lock_overlay.deleteLater()
                self._lock_overlay = None
            self._status_bar.set_message("")
            log.info("Session unlocked by %s", dlg.authenticated_user.username)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._lock_overlay is not None:
            self._lock_overlay.setGeometry(self.centralWidget().rect())

    def closeEvent(self, event) -> None:
        if self._scale_thread:
            self._scale_thread.stop()
        super().closeEvent(event)

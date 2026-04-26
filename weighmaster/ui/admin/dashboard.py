"""Admin dashboard — modern KPIs, recent tickets, commodity chart."""
from __future__ import annotations

from datetime import date
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QSizePolicy,
    QVBoxLayout, QWidget, QPushButton,
)

from weighmaster.database.models import User
from weighmaster.i18n.translator import t
from weighmaster.services import report_service
from weighmaster.services.weighing_service import get_pending_tickets, get_ticket_history
from weighmaster.ui.components.stat_card import KpiCard
from weighmaster.ui.components.ticket_table import TicketTableWidget
from weighmaster.ui.theme import GREEN, BRAND, AMBER, RED, BORDER, BG_PAGE, PURPLE, TEAL


class CommodityBarChart(QWidget):
    """Simple bar chart painted with QPainter — no external chart lib."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._data: list[dict] = []
        self.setMinimumHeight(220)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_data(self, data: list[dict]) -> None:
        self._data = data[:8]
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        margin = 40

        if not self._data:
            painter.setPen(QColor("#9CA3AF"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, t("no_tickets"))
            return

        max_val = max(d["net_kg"] for d in self._data) or 1
        bar_count = len(self._data)
        total_bar_width = w - 2 * margin
        bar_width = max(12, total_bar_width // bar_count - 8)
        spacing = (total_bar_width - bar_width * bar_count) // max(bar_count - 1, 1)

        colors = [BRAND, GREEN, AMBER, TEAL, PURPLE, "#DB2777", "#EA580C", "#16A34A"]

        for i, item in enumerate(self._data):
            x = margin + i * (bar_width + spacing)
            bar_h = int((item["net_kg"] / max_val) * (h - margin - 30))
            y = h - margin - bar_h

            color = QColor(colors[i % len(colors)])
            painter.fillRect(x, y, bar_width, bar_h, color)

            # Label below
            painter.setPen(QColor("#374151"))
            painter.setFont(painter.font())
            label = item["commodity"][:8]
            painter.drawText(x - 4, h - 5, bar_width + 8, 20,
                             Qt.AlignmentFlag.AlignCenter, label)

        # Y-axis label
        painter.setPen(QColor("#9CA3AF"))
        painter.drawText(0, 0, 40, 20, Qt.AlignmentFlag.AlignCenter,
                         f"{max_val/1000:.1f}t")


class AdminDashboard(QWidget):
    reports_requested = pyqtSignal(str)

    def __init__(self, user: User, parent=None) -> None:
        super().__init__(parent)
        self._user = user
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 20, 24, 20)
        main.setSpacing(20)

        # Header
        header = QHBoxLayout()
        header.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        title = QLabel(t("dashboard"))
        title.setObjectName("PageTitle")
        header.addWidget(title)
        header.addStretch()

        self._scale_mini = QLabel("●  Scale Offline")
        self._scale_mini.setStyleSheet(
            "font-size: 12px; color: #6B7280; background: transparent; font-weight: 500;"
        )
        header.addWidget(self._scale_mini)
        main.addLayout(header)

        # KPI row 1
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(14)
        self._kpi_tickets = KpiCard(t("today_tickets"), "0", "TK")
        self._kpi_weight = KpiCard(t("total_net_weight"), "0 t", "NT")
        self._kpi_void = KpiCard("Voided Today", "0", "VD")
        self._kpi_pending = KpiCard(t("awaiting_step2"), "0", "PD")
        self._kpi_scale = KpiCard(t("scale_status"), "—", "SC")
        for card in [self._kpi_tickets, self._kpi_weight, self._kpi_void,
                     self._kpi_pending, self._kpi_scale]:
            kpi_row.addWidget(card, 1)
        main.addLayout(kpi_row)

        # KPI row 2 (WTD / MTD)
        kpi_row2 = QHBoxLayout()
        kpi_row2.setSpacing(14)
        self._kpi_wtd = KpiCard(t("week_to_date"), "0 t", "WT")
        self._kpi_mtd = KpiCard(t("month_to_date"), "0 t", "MT")
        self._kpi_wtd_count = KpiCard(f"{t('week_to_date')} ({t('count')})", "0", "WC")
        self._kpi_mtd_count = KpiCard(f"{t('month_to_date')} ({t('count')})", "0", "MC")
        for card in [self._kpi_wtd, self._kpi_mtd, self._kpi_wtd_count, self._kpi_mtd_count]:
            kpi_row2.addWidget(card, 1)
        main.addLayout(kpi_row2)

        # Quick actions bar
        actions_bar = QFrame()
        actions_bar.setObjectName("Card")
        actions_bar.setStyleSheet(
            actions_bar.styleSheet() + "padding: 12px 18px;"
        )
        ab_layout = QHBoxLayout(actions_bar)
        ab_layout.setContentsMargins(16, 8, 16, 8)
        ab_layout.setSpacing(10)

        actions_lbl = QLabel("Quick Reports")
        actions_lbl.setObjectName("SectionTitle")
        ab_layout.addWidget(actions_lbl)
        ab_layout.addSpacing(8)

        for key, label in [
            ("daily", t("daily_summary")),
            ("commodity", t("commodity_report")),
            ("operator", t("operator_activity")),
            ("full", t("full_export")),
        ]:
            btn = QPushButton(label)
            btn.setObjectName("BtnSecondary")
            btn.clicked.connect(lambda checked, k=key: self.reports_requested.emit(k))
            ab_layout.addWidget(btn)
        ab_layout.addStretch()
        main.addWidget(actions_bar)

        # Content row
        content = QHBoxLayout()
        content.setSpacing(16)

        # Recent tickets (left 2/3)
        left = QFrame()
        left.setObjectName("Card")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(18, 14, 18, 14)
        ll.setSpacing(10)
        recent_lbl = QLabel("Today's Transactions")
        recent_lbl.setObjectName("SectionTitle")
        ll.addWidget(recent_lbl)
        self._recent_table = TicketTableWidget(show_actions=False)
        ll.addWidget(self._recent_table)
        content.addWidget(left, 2)

        # Chart (right 1/3)
        right = QFrame()
        right.setObjectName("Card")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(18, 14, 18, 14)
        rl.setSpacing(10)
        chart_lbl = QLabel(t("commodity_report"))
        chart_lbl.setObjectName("SectionTitle")
        rl.addWidget(chart_lbl)
        self._chart = CommodityBarChart()
        rl.addWidget(self._chart, 1)
        content.addWidget(right, 1)

        main.addLayout(content, 1)

    def refresh(self) -> None:
        try:
            stats = report_service._summary_stats(date.today())
            self._kpi_tickets.set_value(str(stats["total_today"]))
            self._kpi_weight.set_value(f"{stats['net_kg_today']/1000:,.1f} t")
            self._kpi_void.set_value(str(stats["voided_today"]))
            self._kpi_pending.set_value(str(stats["pending_today"]))

            tickets, _ = get_ticket_history(limit=10, offset=0)
            self._recent_table.load_tickets(tickets)

            daily = report_service.daily_summary(date.today())
            self._chart.set_data(daily)

            # WTD / MTD
            weekly = report_service.weekly_summary()
            self._kpi_wtd.set_value(f"{weekly.get('total_net_kg', 0.0)/1000:,.1f} t")
            self._kpi_wtd_count.set_value(str(weekly.get('total_count', 0)))

            today = date.today()
            monthly = report_service.monthly_summary(today.year, today.month)
            self._kpi_mtd.set_value(f"{monthly.get('total_net_kg', 0.0)/1000:,.1f} t")
            self._kpi_mtd_count.set_value(str(monthly.get('total_count', 0)))
        except Exception:
            pass

    def update_weight(self, weight_kg: float, is_stable: bool, status: str) -> None:
        chip = t("status_stable") if is_stable else t("status_unstable")
        if status == "overload":
            chip = t("status_overload")
        self._kpi_scale.set_value(chip)

        if status == "overload":
            self._scale_mini.setText("●  Overload")
            self._scale_mini.setStyleSheet(
                "font-size: 12px; color: #EF4444; background: transparent; font-weight: 600;"
            )
        elif is_stable:
            self._scale_mini.setText("●  Scale Stable")
            self._scale_mini.setStyleSheet(
                "font-size: 12px; color: #10B981; background: transparent; font-weight: 600;"
            )
        else:
            self._scale_mini.setText("●  Scale Unstable")
            self._scale_mini.setStyleSheet(
                "font-size: 12px; color: #F59E0B; background: transparent; font-weight: 600;"
            )

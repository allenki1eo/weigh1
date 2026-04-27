"""Admin dashboard — cargo-dashboard style: compact header, KPI rows, chart."""
from __future__ import annotations

from datetime import date

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QFont
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QSizePolicy,
    QVBoxLayout, QWidget, QPushButton, QScrollArea,
)

from weighmaster.database.models import User
from weighmaster.i18n.translator import t
from weighmaster.services import report_service
from weighmaster.services.weighing_service import get_pending_tickets, get_ticket_history
from weighmaster.ui.components.stat_card import KpiCard
from weighmaster.ui.components.ticket_table import TicketTableWidget
from weighmaster.ui.theme import GREEN, BRAND, AMBER, RED, BORDER, BG_PAGE, PURPLE, TEAL


class CommodityBarChart(QWidget):
    """Bar chart painted with QPainter."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._data: list[dict] = []
        self.setMinimumHeight(200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_data(self, data: list[dict]) -> None:
        self._data = data[:8]
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        margin_x = 12
        margin_bottom = 36
        margin_top = 16

        if not self._data:
            painter.setPen(QColor("#94A3B8"))
            f = painter.font()
            f.setPointSize(11)
            painter.setFont(f)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, t("no_tickets"))
            return

        max_val = max(d["net_kg"] for d in self._data) or 1
        bar_count = len(self._data)
        available_w = w - 2 * margin_x
        gap = 6
        bar_width = max(10, (available_w - gap * (bar_count - 1)) // bar_count)

        colors = [BRAND, GREEN, AMBER, TEAL, PURPLE, "#DB2777", "#EA580C", "#0891B2"]

        chart_h = h - margin_bottom - margin_top

        for i, item in enumerate(self._data):
            x = margin_x + i * (bar_width + gap)
            bar_h = max(4, int((item["net_kg"] / max_val) * chart_h))
            y = margin_top + chart_h - bar_h

            color = QColor(colors[i % len(colors)])
            # Bar with rounded top
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawRoundedRect(x, y, bar_width, bar_h, 3, 3)

            # Value label above bar
            if bar_h > 20:
                painter.setPen(color)
                f = painter.font()
                f.setPointSize(8)
                f.setBold(True)
                painter.setFont(f)
                val_str = f"{item['net_kg']/1000:.1f}t"
                painter.drawText(x - 4, y - 2, bar_width + 8, 14,
                                 Qt.AlignmentFlag.AlignCenter, val_str)

            # Commodity label below
            painter.setPen(QColor("#64748B"))
            f = painter.font()
            f.setPointSize(8)
            f.setBold(False)
            painter.setFont(f)
            label = item["commodity"][:9]
            painter.drawText(x - 4, h - margin_bottom + 4, bar_width + 8, 28,
                             Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop,
                             label)


class AdminDashboard(QWidget):
    reports_requested = pyqtSignal(str)

    def __init__(self, user: User, parent=None) -> None:
        super().__init__(parent)
        self._user = user
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Page header band ──────────────────────────────────────────────────
        header_band = QWidget()
        header_band.setObjectName("PageHeaderBand")
        hb = QHBoxLayout(header_band)
        hb.setContentsMargins(24, 0, 20, 0)
        hb.setSpacing(10)

        title = QLabel(t("dashboard"))
        title.setObjectName("PageTitle")
        hb.addWidget(title)

        hb.addSpacing(6)
        dot = QLabel("·")
        dot.setStyleSheet("color: #CBD5E1; font-size: 16px; background: transparent;")
        hb.addWidget(dot)

        self._scale_mini = QLabel("○  Scale Offline")
        self._scale_mini.setStyleSheet(
            "font-size: 12px; color: #94A3B8; background: transparent; font-weight: 500;"
        )
        hb.addWidget(self._scale_mini)
        hb.addStretch()

        # Quick report buttons in header
        for key, label in [
            ("daily",     t("daily_summary")),
            ("commodity", t("commodity_report")),
            ("full",      t("full_export")),
        ]:
            btn = QPushButton(label)
            btn.setObjectName("BtnSecondary")
            btn.setStyleSheet("font-size: 11px; min-height: 30px; padding: 0 12px;")
            btn.clicked.connect(lambda checked, k=key: self.reports_requested.emit(k))
            hb.addWidget(btn)

        outer.addWidget(header_band)

        # ── Scrollable content ────────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        main = QVBoxLayout(container)
        main.setContentsMargins(20, 16, 20, 20)
        main.setSpacing(12)

        # KPI row 1: daily stats
        kpi_row1 = QHBoxLayout()
        kpi_row1.setSpacing(10)
        self._kpi_tickets = KpiCard(t("today_tickets"),    "0",   "TK")
        self._kpi_weight  = KpiCard(t("total_net_weight"), "0 t", "NT")
        self._kpi_void    = KpiCard("Voided Today",        "0",   "VD")
        self._kpi_pending = KpiCard(t("awaiting_step2"),   "0",   "PD")
        self._kpi_scale   = KpiCard(t("scale_status"),     "—",   "SC")
        for card in [self._kpi_tickets, self._kpi_weight, self._kpi_void,
                     self._kpi_pending, self._kpi_scale]:
            kpi_row1.addWidget(card, 1)
        main.addLayout(kpi_row1)

        # KPI row 2: WTD / MTD
        kpi_row2 = QHBoxLayout()
        kpi_row2.setSpacing(10)
        self._kpi_wtd       = KpiCard(t("week_to_date"),                    "0 t", "WT")
        self._kpi_mtd       = KpiCard(t("month_to_date"),                   "0 t", "MT")
        self._kpi_wtd_count = KpiCard(f"{t('week_to_date')} ({t('count')})", "0",  "WC")
        self._kpi_mtd_count = KpiCard(f"{t('month_to_date')} ({t('count')})", "0", "MC")
        for card in [self._kpi_wtd, self._kpi_mtd, self._kpi_wtd_count, self._kpi_mtd_count]:
            kpi_row2.addWidget(card, 1)
        main.addLayout(kpi_row2)

        # Content row: recent table (2/3) + chart (1/3)
        content = QHBoxLayout()
        content.setSpacing(12)

        left = QFrame()
        left.setObjectName("Card")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(0)

        # Table card header
        tbl_header = QWidget()
        tbl_header.setFixedHeight(44)
        th = QHBoxLayout(tbl_header)
        th.setContentsMargins(18, 0, 18, 0)
        th.setSpacing(8)
        recent_lbl = QLabel("Today's Transactions")
        recent_lbl.setObjectName("SectionTitle")
        th.addWidget(recent_lbl)
        th.addStretch()
        tbl_header.setStyleSheet("border-bottom: 1px solid #E2E8F0;")
        ll.addWidget(tbl_header)

        self._recent_table = TicketTableWidget(show_actions=False)
        ll.addWidget(self._recent_table)
        content.addWidget(left, 2)

        right = QFrame()
        right.setObjectName("Card")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        # Chart card header
        chart_header = QWidget()
        chart_header.setFixedHeight(44)
        ch = QHBoxLayout(chart_header)
        ch.setContentsMargins(18, 0, 18, 0)
        chart_lbl = QLabel(t("commodity_report"))
        chart_lbl.setObjectName("SectionTitle")
        ch.addWidget(chart_lbl)
        ch.addStretch()
        chart_header.setStyleSheet("border-bottom: 1px solid #E2E8F0;")
        rl.addWidget(chart_header)

        chart_body = QWidget()
        chart_body.setStyleSheet("background: transparent;")
        cb = QVBoxLayout(chart_body)
        cb.setContentsMargins(12, 8, 12, 8)
        self._chart = CommodityBarChart()
        cb.addWidget(self._chart, 1)
        rl.addWidget(chart_body, 1)
        content.addWidget(right, 1)

        main.addLayout(content, 1)
        scroll.setWidget(container)
        outer.addWidget(scroll, 1)

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
                "font-size: 12px; color: #DC2626; background: transparent; font-weight: 600;"
            )
        elif is_stable:
            self._scale_mini.setText("●  Scale Stable")
            self._scale_mini.setStyleSheet(
                "font-size: 12px; color: #16A34A; background: transparent; font-weight: 600;"
            )
        else:
            self._scale_mini.setText("●  Scale Active")
            self._scale_mini.setStyleSheet(
                "font-size: 12px; color: #D97706; background: transparent; font-weight: 600;"
            )

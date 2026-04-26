"""PDF report generator using ReportLab."""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from weighmaster.i18n.translator import t
from weighmaster.utils.helpers import format_datetime, format_weight


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle",
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=colors.HexColor("#1E3A5F"),
        alignment=TA_CENTER,
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name="ReportSubtitle",
        fontName="Helvetica",
        fontSize=10,
        textColor=colors.HexColor("#6B7280"),
        alignment=TA_CENTER,
        spaceAfter=20,
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=colors.HexColor("#1E3A5F"),
        alignment=TA_LEFT,
        spaceAfter=6,
        spaceBefore=12,
    ))
    styles.add(ParagraphStyle(
        name="TableHeader",
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=colors.white,
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="TableCell",
        fontName="Helvetica",
        fontSize=8,
        textColor=colors.HexColor("#374151"),
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="TableCellRight",
        fontName="Helvetica",
        fontSize=8,
        textColor=colors.HexColor("#374151"),
        alignment=TA_RIGHT,
    ))
    return styles


def _header_data(title: str, subtitle: str = "") -> list:
    styles = _styles()
    elements = [Paragraph(title, styles["ReportTitle"])]
    if subtitle:
        elements.append(Paragraph(subtitle, styles["ReportSubtitle"]))
    elements.append(Spacer(1, 6))
    return elements


def _build_table(data: list[list], col_widths: list, header_bg: str = "#2563EB"):
    """Build a styled platypus Table."""
    if not data:
        return Paragraph(t("no_results"), _styles()["TableCell"])
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_bg)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F9FAFB")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
    ]
    # Alternate row colors
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#FFFFFF")))
    tbl.setStyle(TableStyle(style))
    return tbl


def generate_daily_summary_pdf(data: list[dict], target_date: date, output_path: str) -> str:
    """Generate a PDF daily summary report."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    elements = _header_data(
        t("daily_summary"),
        target_date.strftime("%d %b %Y"),
    )
    table_data = [[t("commodity"), t("count"), t("net_weight_tonnes"), t("total")]]
    total_count = 0
    total_kg = 0.0
    for item in data:
        table_data.append([
            item["commodity"],
            str(item["count"]),
            f"{item['net_kg']/1000:,.3f}",
            f"{item['net_kg']:,.2f} kg",
        ])
        total_count += item["count"]
        total_kg += item["net_kg"]
    table_data.append([
        Paragraph(f"<b>{t('total')}</b>", _styles()["TableCell"]),
        str(total_count),
        f"{total_kg/1000:,.3f}",
        f"{total_kg:,.2f} kg",
    ])
    elements.append(_build_table(table_data, [None, 60, 100, 100]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
        f"{t('printed_at')}: {format_datetime(datetime.now())}",
        _styles()["ReportSubtitle"],
    ))
    doc.build(elements)
    return output_path


def generate_monthly_summary_pdf(data: dict, year: int, month: int, output_path: str) -> str:
    """Generate a PDF monthly summary report."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    month_name = date(year, month, 1).strftime("%B %Y")
    elements = _header_data(t("monthly_summary"), month_name)

    # Summary stats
    stats_data = [
        [Paragraph(f"<b>{t('total')}</b>", _styles()["TableCell"]),
         str(data.get("total_count", 0)),
         f"{data.get('total_net_kg', 0.0)/1000:,.3f} t"],
        [Paragraph(f"<b>{t('vehicle_plate')}s</b>", _styles()["TableCell"]),
         str(data.get("unique_vehicles", 0)), ""],
        [Paragraph(f"<b>{t('commodity')}</b>", _styles()["TableCell"]),
         str(data.get("unique_commodities", 0)), ""],
    ]
    elements.append(_build_table(stats_data, [None, 80, 100], header_bg="#059669"))
    elements.append(Spacer(1, 12))

    # Daily breakdown
    elements.append(Paragraph(t("daily_breakdown"), _styles()["SectionHeader"]))
    days = data.get("days", [])
    table_data = [[t("date"), t("count"), t("net_weight_tonnes"), t("total")]]
    for day in days:
        table_data.append([
            day["date"],
            str(day["count"]),
            f"{day['net_kg']/1000:,.3f}",
            f"{day['net_kg']:,.2f} kg",
        ])
    elements.append(_build_table(table_data, [None, 60, 100, 100]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
        f"{t('printed_at')}: {format_datetime(datetime.now())}",
        _styles()["ReportSubtitle"],
    ))
    doc.build(elements)
    return output_path


def generate_vehicle_history_pdf(data: list[dict], plate: str, output_path: str) -> str:
    """Generate a PDF vehicle history report."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=15*mm, leftMargin=15*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    elements = _header_data(t("vehicle_history"), plate)

    if not data:
        elements.append(Paragraph(t("no_results"), _styles()["TableCell"]))
    else:
        # Stats
        total_visits = len(data)
        avg_net = sum((d.get("net_kg") or 0.0) for d in data) / max(total_visits, 1)
        last_visit = data[0].get("created_at")
        stats_data = [
            [Paragraph(f"<b>{t('total_visits')}</b>", _styles()["TableCell"]), str(total_visits)],
            [Paragraph(f"<b>{t('avg_net_weight')}</b>", _styles()["TableCell"]), f"{avg_net:,.2f} kg"],
            [Paragraph(f"<b>{t('last_visit')}</b>", _styles()["TableCell"]), format_datetime(last_visit)],
        ]
        elements.append(_build_table(stats_data, [None, 150], header_bg="#059669"))
        elements.append(Spacer(1, 12))

        table_data = [[
            t("ticket_number"), t("date_time"), t("commodity"),
            t("gross_weight"), t("tare_weight"), t("net_weight"),
        ]]
        for item in data:
            table_data.append([
                item.get("ticket_number", ""),
                format_datetime(item.get("created_at")),
                item.get("commodity", "") or "—",
                format_weight(item.get("gross_kg")),
                format_weight(item.get("tare_kg")),
                format_weight(item.get("net_kg")),
            ])
        elements.append(_build_table(table_data, [None, 80, 80, 60, 60, 60]))

    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
        f"{t('printed_at')}: {format_datetime(datetime.now())}",
        _styles()["ReportSubtitle"],
    ))
    doc.build(elements)
    return output_path


def generate_full_export_pdf(data: list[dict], date_from: date, date_to: date, output_path: str) -> str:
    """Generate a PDF full ticket export report."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=12*mm, leftMargin=12*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    subtitle = f"{date_from.strftime('%d %b %Y')} – {date_to.strftime('%d %b %Y')}"
    elements = _header_data(t("full_export"), subtitle)

    if not data:
        elements.append(Paragraph(t("no_results"), _styles()["TableCell"]))
    else:
        table_data = [[
            t("ticket_number"), t("vehicle_plate"), t("driver_name"),
            t("commodity"), t("gross_weight"), t("tare_weight"),
            t("net_weight"), t("status"), t("date_time"),
        ]]
        for item in data:
            table_data.append([
                item.get("ticket_number", ""),
                item.get("vehicle_plate", ""),
                (item.get("driver_name") or "")[:16],
                item.get("commodity", "") or "—",
                format_weight(item.get("gross_kg")),
                format_weight(item.get("tare_kg")),
                format_weight(item.get("net_kg")),
                "VOID" if item.get("is_void") else (item.get("status") or ""),
                format_datetime(item.get("created_at")),
            ])
        elements.append(_build_table(table_data, [None, 60, 70, 60, 50, 50, 50, 50, 60]))

    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
        f"{t('printed_at')}: {format_datetime(datetime.now())}",
        _styles()["ReportSubtitle"],
    ))
    doc.build(elements)
    return output_path

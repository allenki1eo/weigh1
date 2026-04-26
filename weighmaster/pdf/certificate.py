"""A4 weigh certificate generator using ReportLab."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas

from weighmaster.ui.theme import (
    BRAND, GREEN, GREEN_LIGHT, RED, TEXT_BODY, TEXT_MUTED,
    TEXT_PRIMARY, BORDER,
)

# Page layout constants (points — 72pt = 1 inch)
PAGE_W, PAGE_H = A4          # 595 × 842
MARGIN = 40
BORDER_INSET = 8


def _hex_to_rgb(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


def _set_color(c: rl_canvas.Canvas, hex_color: str) -> None:
    c.setFillColorRGB(*_hex_to_rgb(hex_color))


def _set_stroke(c: rl_canvas.Canvas, hex_color: str) -> None:
    c.setStrokeColorRGB(*_hex_to_rgb(hex_color))


class CertificateGenerator:
    """Generates an A4 weigh certificate PDF for a completed ticket."""

    def generate(
        self,
        ticket,          # WeighTicket ORM object
        company,         # Company ORM object
        output_path: str,
    ) -> str:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        c = rl_canvas.Canvas(output_path, pagesize=A4)
        c.setTitle(f"Weigh Certificate {ticket.ticket_number}")

        self._draw_border(c, company)
        y = PAGE_H - MARGIN - 10
        y = self._draw_header(c, company, y)
        y = self._draw_meta_row(c, ticket, y)
        y = self._draw_vehicle_section(c, ticket, y)
        y = self._draw_weight_table(c, ticket, y)
        y = self._draw_weighbridge_info(c, company, y)
        y = self._draw_signatures(c, company, ticket, y)
        self._draw_footer(c, ticket)
        self._draw_qr_code(c, ticket)

        c.save()
        return output_path

    # ── Border ──────────────────────────────────────────────────────────────
    def _draw_border(self, c, company) -> None:
        _set_stroke(c, BRAND)
        c.setLineWidth(0.75)
        inset = BORDER_INSET
        c.rect(inset, inset, PAGE_W - 2 * inset, PAGE_H - 2 * inset, stroke=1, fill=0)

    # ── Header ───────────────────────────────────────────────────────────────
    def _draw_header(self, c, company, y: float) -> float:
        logo_x = MARGIN
        text_x = MARGIN + 90

        # Logo placeholder / actual logo
        if company and company.logo_path and os.path.exists(company.logo_path):
            try:
                c.drawImage(company.logo_path, logo_x, y - 80, width=80, height=80,
                            preserveAspectRatio=True, mask="auto")
            except Exception:
                pass

        # Company name
        _set_color(c, TEXT_PRIMARY)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(text_x, y - 16, (company.name if company else "Company Name") or "")

        _set_color(c, TEXT_BODY)
        c.setFont("Helvetica", 9)
        c.drawString(text_x, y - 30, (company.address if company else "") or "")
        c.drawString(text_x, y - 42, (company.phone if company else "") or "")
        if company and company.email:
            c.drawString(text_x, y - 54, company.email)

        # Certificate title (right-aligned)
        _set_color(c, BRAND)
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(PAGE_W - MARGIN, y - 16, "WEIGHBRIDGE CERTIFICATE")
        _set_color(c, TEXT_MUTED)
        c.setFont("Helvetica-Oblique", 9)
        c.drawRightString(PAGE_W - MARGIN, y - 30, "CHETI CHA MIZANI")

        # Blue divider
        new_y = y - 95
        _set_stroke(c, BRAND)
        c.setLineWidth(0.75)
        c.line(MARGIN, new_y, PAGE_W - MARGIN, new_y)
        return new_y - 8

    # ── Meta row ─────────────────────────────────────────────────────────────
    def _draw_meta_row(self, c, ticket, y: float) -> float:
        col1_x = MARGIN
        col2_x = PAGE_W / 2 + 10

        def draw_field(x, cy, label, value):
            _set_color(c, TEXT_MUTED)
            c.setFont("Helvetica", 8)
            c.drawString(x, cy, label)
            _set_color(c, TEXT_PRIMARY)
            c.setFont("Helvetica-Bold", 9)
            c.drawString(x + 80, cy, str(value or "—"))

        draw_field(col1_x, y - 12, "Ticket No:", ticket.ticket_number)
        draw_field(col2_x, y - 12, "Date:", _fmt_dt(ticket.tare_datetime))
        draw_field(col1_x, y - 26, "Completed:", _fmt_dt(ticket.gross_datetime))
        draw_field(col2_x, y - 26, "Printed:", _fmt_dt(datetime.now()))

        new_y = y - 50
        # Light separator
        _set_stroke(c, BORDER)
        c.setLineWidth(0.5)
        c.line(MARGIN, new_y, PAGE_W - MARGIN, new_y)
        return new_y - 8

    # ── Vehicle section ───────────────────────────────────────────────────────
    def _draw_vehicle_section(self, c, ticket, y: float) -> float:
        box_h = 90
        # Light grey background box
        c.setFillColorRGB(0.97, 0.98, 0.99)
        c.roundRect(MARGIN, y - box_h, PAGE_W - 2 * MARGIN, box_h, 6, stroke=0, fill=1)
        _set_stroke(c, BORDER)
        c.setLineWidth(0.5)
        c.roundRect(MARGIN, y - box_h, PAGE_W - 2 * MARGIN, box_h, 6, stroke=1, fill=0)

        # Plate highlighted box
        plate_x = MARGIN + 10
        plate_y = y - 28
        c.setFillColorRGB(*_hex_to_rgb("#EBF0FE"))
        c.roundRect(plate_x, plate_y - 4, 160, 22, 4, stroke=0, fill=1)
        _set_color(c, BRAND)
        c.setFont("Courier-Bold", 18)
        c.drawString(plate_x + 6, plate_y + 2, ticket.vehicle_plate or "")

        # Other vehicle fields
        _set_color(c, TEXT_BODY)
        c.setFont("Helvetica", 9)
        c.drawString(MARGIN + 10, y - 42, f"Driver: {ticket.driver_name or '—'}")
        c.drawString(MARGIN + 10, y - 54, f"Customer: {ticket.company_name or '—'}")
        c.drawString(MARGIN + 10, y - 66, f"Commodity: {ticket.commodity_name or '—'}")
        if ticket.notes:
            c.drawString(MARGIN + 10, y - 78, f"Notes: {ticket.notes}")

        return y - box_h - 12

    # ── Weight table ─────────────────────────────────────────────────────────
    def _draw_weight_table(self, c, ticket, y: float) -> float:
        table_x = MARGIN
        table_w = PAGE_W - 2 * MARGIN
        col_split = table_x + table_w * 0.6
        row_h = 24

        rows = [
            ("TARE WEIGHT", "Uzito wa Gari", ticket.tare_weight, False),
            ("GROSS WEIGHT", "Uzito wa Mzigo", ticket.gross_weight, False),
            ("DEDUCTION", "Makato", ticket.deduction_kg, True),
        ]

        current_y = y
        # Draw header border
        _set_stroke(c, BORDER)
        c.setLineWidth(0.5)

        for i, (en, sw, kg, muted) in enumerate(rows):
            ry = current_y - row_h
            # Row background
            if i % 2 == 0:
                c.setFillColorRGB(1, 1, 1)
            else:
                c.setFillColorRGB(0.98, 0.99, 1.0)
            c.rect(table_x, ry, table_w, row_h, stroke=0, fill=1)
            c.line(table_x, ry, table_x + table_w, ry)

            color = TEXT_MUTED if muted else TEXT_BODY
            _set_color(c, color)
            c.setFont("Helvetica", 9 if muted else 10)
            c.drawString(table_x + 8, ry + 7, f"{en}  ({sw})")

            # Weight value (right-aligned in value column)
            c.setFont("Courier-Bold" if not muted else "Courier", 10 if not muted else 9)
            c.drawRightString(table_x + table_w - 8, ry + 7, f"{kg:,.2f} kg" if kg is not None else "—")

            current_y -= row_h

        # Double border before net
        _set_stroke(c, BRAND)
        c.setLineWidth(1.5)
        c.line(table_x, current_y, table_x + table_w, current_y)
        c.line(table_x, current_y - 2, table_x + table_w, current_y - 2)
        current_y -= 4

        # NET row
        net_h = 34
        c.setFillColorRGB(*_hex_to_rgb("#EBF0FE"))
        c.rect(table_x, current_y - net_h, table_w, net_h, stroke=0, fill=1)
        _set_color(c, BRAND)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(table_x + 8, current_y - net_h + 18, "NET WEIGHT  (Uzito wa Bidhaa)")

        net_kg = ticket.net_weight or 0.0
        c.setFont("Courier-Bold", 14)
        c.drawRightString(table_x + table_w - 8, current_y - net_h + 18, f"{net_kg:,.2f} kg")
        c.setFont("Helvetica", 9)
        _set_color(c, TEXT_BODY)
        c.drawRightString(table_x + table_w - 8, current_y - net_h + 6, f"{net_kg/1000:,.3f} TONNES")

        # Outer border
        _set_stroke(c, BORDER)
        c.setLineWidth(0.75)
        total_h = y - (current_y - net_h)
        c.roundRect(table_x, current_y - net_h, table_w, total_h, 4, stroke=1, fill=0)

        return current_y - net_h - 12

    # ── Weighbridge info ──────────────────────────────────────────────────────
    def _draw_weighbridge_info(self, c, company, y: float) -> float:
        col_w = (PAGE_W - 2 * MARGIN) / 3
        box_h = 44

        items = [
            ("Capacity", f"{(company.weighbridge_capacity_kg / 1000):,.0f} Tonnes" if company else "80 t"),
            ("WMA Certificate", (company.wma_cert_number or "—") if company else "—"),
            ("Valid Until", _fmt_date(company.wma_valid_until) if company else "—"),
        ]

        for i, (label, value) in enumerate(items):
            bx = MARGIN + i * col_w
            _set_stroke(c, BORDER)
            c.setLineWidth(0.5)
            c.roundRect(bx + 2, y - box_h, col_w - 4, box_h, 4, stroke=1, fill=0)
            _set_color(c, TEXT_MUTED)
            c.setFont("Helvetica", 8)
            c.drawString(bx + 8, y - 14, label)
            _set_color(c, TEXT_PRIMARY)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(bx + 8, y - 28, value)

        # VERIFIED stamp
        is_verified = (
            company and company.wma_valid_until and company.wma_valid_until >= date.today()
        )
        if is_verified:
            stamp_x = PAGE_W - MARGIN - 80
            stamp_y = y - box_h
            _set_color(c, GREEN)
            _set_stroke(c, GREEN)
            c.setLineWidth(1.5)
            c.roundRect(stamp_x, stamp_y, 74, box_h, 6, stroke=1, fill=0)
            c.setFont("Helvetica-Bold", 11)
            c.drawCentredString(stamp_x + 37, stamp_y + box_h / 2 - 6, "✓ VERIFIED")

        return y - box_h - 12

    # ── Signatures ────────────────────────────────────────────────────────────
    def _draw_signatures(self, c, company, ticket, y: float) -> float:
        col_w = (PAGE_W - 2 * MARGIN - 20) / 2

        _set_color(c, TEXT_BODY)
        c.setFont("Helvetica", 9)

        for i, (role, name) in enumerate([("Operator", ""), ("Supervisor", "")]):
            bx = MARGIN + i * (col_w + 20)
            c.drawString(bx, y - 10, f"{role}:")
            _set_stroke(c, TEXT_MUTED)
            c.setLineWidth(0.5)
            c.line(bx, y - 30, bx + col_w - 10, y - 30)
            _set_color(c, TEXT_MUTED)
            c.setFont("Helvetica", 8)
            if i == 0 and ticket:
                c.drawString(bx, y - 42, "")

        # Company stamp box
        stamp_x = PAGE_W - MARGIN - 120
        _set_stroke(c, BORDER)
        c.setLineWidth(0.75)
        c.rect(stamp_x, y - 64, 110, 54, stroke=1, fill=0)
        _set_color(c, TEXT_MUTED)
        c.setFont("Helvetica", 8)
        c.drawCentredString(stamp_x + 55, y - 38, "COMPANY STAMP")

        return y - 72

    # ── Footer ────────────────────────────────────────────────────────────────
    def _draw_footer(self, c, ticket) -> None:
        fy = MARGIN + 28
        _set_color(c, TEXT_MUTED)
        c.setFont("Helvetica-Oblique", 7)
        c.drawCentredString(PAGE_W / 2, fy + 12,
            "This certificate is computer-generated and valid without signature")
        c.drawCentredString(PAGE_W / 2, fy + 2,
            "Cheti hiki kimetolewa na kompyuta na ni halali bila saini")
        c.setFont("Helvetica", 7)
        c.drawCentredString(PAGE_W / 2, fy - 8, f"Printed: {_fmt_dt(datetime.now())}")

    # ── QR Code ───────────────────────────────────────────────────────────────
    def _draw_qr_code(self, c, ticket) -> None:
        try:
            import qrcode
            from io import BytesIO
            from reportlab.lib.utils import ImageReader

            payload = {
                "v": 1,
                "ticket": ticket.ticket_number,
                "plate": ticket.vehicle_plate,
                "net_kg": ticket.net_weight,
                "tare_kg": ticket.tare_weight,
                "gross_kg": ticket.gross_weight,
                "commodity": ticket.commodity_name,
                "datetime": ticket.tare_datetime.isoformat() if ticket.tare_datetime else "",
            }
            payload_str = json.dumps(payload)
            sha = hashlib.sha256(payload_str.encode()).hexdigest()[:16]
            payload["sha256"] = sha

            qr = qrcode.QRCode(box_size=4, border=1)
            qr.add_data(json.dumps(payload))
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            c.drawImage(ImageReader(buf), PAGE_W - MARGIN - 65, MARGIN + 10, 60, 60)
        except Exception:
            pass  # QR is optional — don't fail certificate generation


def _fmt_dt(dt: Optional[datetime]) -> str:
    if dt is None:
        return "—"
    return dt.strftime("%d/%b/%Y %H:%M")


def _fmt_date(d) -> str:
    if d is None:
        return "—"
    if isinstance(d, date):
        return d.strftime("%d/%b/%Y")
    return str(d)

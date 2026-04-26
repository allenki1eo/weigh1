"""Ticket creation and weight capture logic."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy import func

from weighmaster.config import MAX_WEIGHT_KG, OVERLOAD_KG, TICKET_PREFIX, TICKET_ZERO_PAD
from weighmaster.database.connection import get_session
from weighmaster.database.models import Commodity, TicketException, User, VehicleProfile, WeighTicket

log = logging.getLogger(__name__)

OPEN_TICKET_STATUSES = ("tare_captured", "gross_captured")


class WeighingError(Exception):
    pass


@dataclass
class TicketSummary:
    id: int
    ticket_number: str
    vehicle_plate: str
    driver_name: str
    company_name: str
    commodity_name: str
    deduction_kg: float
    commodity_rate_per_tonne: float
    commodity_value: Optional[float]
    oil_distance_km: float
    oil_rate_per_km: float
    oil_price: float
    total_price: Optional[float]
    tare_weight: Optional[float]
    gross_weight: Optional[float]
    net_weight: Optional[float]
    tare_datetime: Optional[datetime]
    gross_datetime: Optional[datetime]
    tare_source: str
    gross_source: Optional[str]
    status: str
    pending_stage: str
    weighing_mode: str
    first_capture_datetime: Optional[datetime]
    is_void: bool
    void_reason: Optional[str]
    operator_id: int
    notes: Optional[str]
    created_at: datetime
    axle_count: int
    axle_weights: list[float]


def _next_ticket_number(session, prefix: str) -> str:
    pattern = f"{prefix}-%"
    latest = (
        session.query(WeighTicket.ticket_number)
        .filter(WeighTicket.ticket_number.like(pattern))
        .order_by(WeighTicket.id.desc())
        .first()
    )
    last_seq = 0
    if latest and latest[0]:
        parts = latest[0].split("-")
        if len(parts) >= 2:
            try:
                last_seq = int(parts[-1])
            except ValueError:
                last_seq = 0
    seq = str(last_seq + 1).zfill(TICKET_ZERO_PAD)
    return f"{prefix}-{seq}"


def _find_active_ticket_by_plate(session, vehicle_plate: str) -> Optional[WeighTicket]:
    plate = vehicle_plate.strip().upper()
    return (
        session.query(WeighTicket)
        .filter(
            WeighTicket.vehicle_plate == plate,
            WeighTicket.status.in_(OPEN_TICKET_STATUSES),
            WeighTicket.is_void == False,
        )
        .order_by(WeighTicket.created_at.desc())
        .first()
    )


def _check_overload(weight_kg: float) -> None:
    from weighmaster.database.models import Company

    with get_session() as session:
        company = session.query(Company).first()
        capacity = company.weighbridge_capacity_kg if company else MAX_WEIGHT_KG
    if weight_kg > capacity:
        raise WeighingError(
            f"OVERLOAD - {weight_kg:,.0f} kg exceeds bridge capacity ({capacity:,.0f} kg). "
            "Vehicle must be offloaded before weighing."
        )
    if weight_kg > OVERLOAD_KG:
        raise WeighingError(
            f"OVERLOAD - {weight_kg:,.0f} kg exceeds safe limit ({OVERLOAD_KG:,.0f} kg)"
        )


def _safe_log_gate_event(user: User, ticket_id: int, event_type: str, note: str = "") -> None:
    try:
        from weighmaster.services.gate_service import log_gate_event

        log_gate_event(user, ticket_id, event_type, note=note)
    except Exception as exc:
        log.warning("Gate event log failed: %s", exc)


def _update_vehicle_profile(session, ticket: WeighTicket) -> None:
    plate = (ticket.vehicle_plate or "").strip().upper()
    if not plate:
        return
    profile = session.query(VehicleProfile).filter_by(vehicle_plate=plate).first()
    if profile is None:
        profile = VehicleProfile(vehicle_plate=plate)
        session.add(profile)
    profile.default_driver_name = (ticket.driver_name or "").strip()
    profile.default_company_name = (ticket.company_name or "").strip()
    profile.last_commodity_name = (ticket.commodity_name or "").strip()
    profile.last_seen_at = datetime.now()
    profile.last_ticket_id = ticket.id


def list_known_plates(limit: int = 200) -> list[str]:
    with get_session() as session:
        rows = (
            session.query(VehicleProfile.vehicle_plate)
            .order_by(func.coalesce(VehicleProfile.last_seen_at, VehicleProfile.created_at).desc())
            .limit(limit)
            .all()
        )
        return [row[0] for row in rows if row[0]]


def suggest_vehicle_profile(vehicle_plate: str) -> Optional[dict]:
    plate = vehicle_plate.strip().upper()
    if not plate:
        return None
    with get_session() as session:
        profile = session.query(VehicleProfile).filter_by(vehicle_plate=plate).first()
        if profile is None:
            return None
        return {
            "vehicle_plate": profile.vehicle_plate,
            "driver_name": profile.default_driver_name,
            "company_name": profile.default_company_name,
            "commodity_name": profile.last_commodity_name,
        }


def log_ticket_exception(
    user: User,
    reason_type: str,
    reason_detail: str,
    ticket_id: Optional[int] = None,
    vehicle_plate: str = "",
) -> None:
    from weighmaster.services import audit_service

    detail = reason_detail.strip()
    if not detail:
        return
    with get_session() as session:
        session.add(
            TicketException(
                ticket_id=ticket_id,
                vehicle_plate=(vehicle_plate.strip().upper() or None),
                reason_type=reason_type,
                reason_detail=detail,
                recorded_by=user.id,
                recorded_by_name=user.username,
            )
        )
    audit_service.log_action(
        user,
        "TICKET_EXCEPTION",
        "TicketException",
        entity_id=ticket_id,
        details={
            "reason_type": reason_type,
            "reason_detail": detail,
            "vehicle_plate": vehicle_plate.strip().upper(),
        },
    )


def capture_tare(
    operator: User,
    vehicle_plate: str,
    driver_name: str,
    commodity_id: int,
    company_name: str,
    weight_kg: float,
    source: str = "auto",
    notes: str = "",
    axle_count: int = 1,
    axle_weights: Optional[list[float]] = None,
    weighing_mode: str = "tare_first",
    exception_reason: str = "",
    commodity_rate_per_tonne: Optional[float] = None,
    oil_distance_km: float = 0.0,
    oil_rate_per_km: float = 0.0,
    apply_oil_pricing: bool = False,
) -> TicketSummary:
    from weighmaster.database.models import Company
    from weighmaster.services import audit_service

    if weighing_mode not in ("tare_first", "gross_first"):
        raise WeighingError(f"Unsupported weighing mode: {weighing_mode}")
    if weight_kg <= 0:
        raise WeighingError("First captured weight must be greater than zero")
    _check_overload(weight_kg)

    with get_session() as session:
        company = session.query(Company).first()
        prefix = company.ticket_prefix if company else TICKET_PREFIX
        existing = _find_active_ticket_by_plate(session, vehicle_plate)
        if existing:
            raise WeighingError(
                f"Duplicate ticket warning: vehicle {vehicle_plate.strip().upper()} already has open ticket "
                f"{existing.ticket_number}. Complete or void it before creating a new one."
            )
        commodity = session.query(Commodity).filter_by(id=commodity_id, is_active=True).first()
        if commodity is None:
            raise WeighingError("Commodity not found")
        pricing_rate = max(0.0, float(commodity_rate_per_tonne if commodity_rate_per_tonne is not None else commodity.price_per_tonne))
        oil_km = max(0.0, float(oil_distance_km))
        oil_rate = max(0.0, float(oil_rate_per_km))
        if not apply_oil_pricing:
            oil_km = 0.0
            oil_rate = 0.0

        ticket_number = _next_ticket_number(session, prefix)
        ticket = WeighTicket(
            ticket_number=ticket_number,
            vehicle_plate=vehicle_plate.strip().upper(),
            driver_name=driver_name.strip(),
            company_name=company_name.strip(),
            commodity_id=commodity_id,
            commodity_name=commodity.name_en,
            deduction_kg=commodity.deduction_kg,
            commodity_rate_per_tonne=pricing_rate,
            commodity_value=0.0,
            oil_distance_km=oil_km,
            oil_rate_per_km=oil_rate,
            oil_price=oil_km * oil_rate,
            total_price=0.0,
            operator_id=operator.id,
            notes=notes.strip() or None,
            axle_count=axle_count,
            axle_weights_json=json.dumps(axle_weights or []),
        )

        now = datetime.now()
        if weighing_mode == "tare_first":
            ticket.tare_weight = weight_kg
            ticket.tare_datetime = now
            ticket.tare_source = source
            ticket.status = "tare_captured"
            first_phase = "tare"
            first_action = "TICKET_CREATE_TARE"
        else:
            ticket.gross_weight = weight_kg
            ticket.gross_datetime = now
            ticket.gross_source = source
            ticket.status = "gross_captured"
            first_phase = "gross"
            first_action = "TICKET_CREATE_GROSS"

        session.add(ticket)
        session.flush()
        _update_vehicle_profile(session, ticket)
        ticket_id = ticket.id
        ticket_no = ticket.ticket_number

    audit_service.log_action(
        operator,
        first_action,
        "WeighTicket",
        entity_id=ticket_id,
        details={
            "ticket_number": ticket_no,
            "plate": vehicle_plate.strip().upper(),
            "first_phase": first_phase,
            "weight_kg": weight_kg,
            "weighing_mode": weighing_mode,
        },
    )
    if source == "manual":
        audit_service.log_action(
            operator,
            "TICKET_MANUAL_WEIGHT",
            "WeighTicket",
            entity_id=ticket_id,
            details={"stage": first_phase, "weight_kg": weight_kg},
        )
        if exception_reason.strip():
            log_ticket_exception(
                operator,
                "manual_weight",
                exception_reason,
                ticket_id=ticket_id,
                vehicle_plate=vehicle_plate,
            )

    _safe_log_gate_event(operator, ticket_id, "arrived")
    _safe_log_gate_event(operator, ticket_id, "on_bridge", note=f"{first_phase} capture")
    _safe_log_gate_event(operator, ticket_id, "off_bridge", note=f"{first_phase} capture")
    _safe_log_gate_event(operator, ticket_id, "dispatch")

    with get_session() as session:
        t = session.query(WeighTicket).filter_by(id=ticket_id).first()
        return _to_summary(t)


def capture_second_weight(
    operator: User,
    ticket_id: int,
    weight_kg: float,
    source: str = "auto",
    axle_weights: Optional[list[float]] = None,
    exception_reason: str = "",
) -> TicketSummary:
    from weighmaster.services import audit_service

    _check_overload(weight_kg)

    with get_session() as session:
        ticket = session.query(WeighTicket).filter_by(id=ticket_id).first()
        if ticket is None:
            raise WeighingError("Ticket not found")
        if ticket.is_void:
            raise WeighingError("Cannot capture second weight on a voided ticket")
        if ticket.status not in OPEN_TICKET_STATUSES:
            raise WeighingError("Ticket is not awaiting second weight")

        if ticket.status == "tare_captured":
            if ticket.tare_weight is None:
                raise WeighingError("Ticket tare weight is missing")
            if weight_kg <= ticket.tare_weight:
                raise WeighingError(
                    f"Gross weight ({weight_kg:.2f} kg) must be greater than tare ({ticket.tare_weight:.2f} kg)"
                )
            ticket.gross_weight = weight_kg
            ticket.gross_datetime = datetime.now()
            ticket.gross_source = source
            second_phase = "gross"
            action = "TICKET_CAPTURE_GROSS"
        else:
            if ticket.gross_weight is None:
                raise WeighingError("Ticket gross weight is missing")
            if weight_kg >= ticket.gross_weight:
                raise WeighingError(
                    f"Tare weight ({weight_kg:.2f} kg) must be lower than gross ({ticket.gross_weight:.2f} kg)"
                )
            ticket.tare_weight = weight_kg
            ticket.tare_datetime = datetime.now()
            ticket.tare_source = source
            second_phase = "tare"
            action = "TICKET_CAPTURE_TARE"

        ticket.net_weight = (ticket.gross_weight or 0.0) - (ticket.tare_weight or 0.0) - ticket.deduction_kg
        commodity_value = (ticket.net_weight / 1000.0) * (ticket.commodity_rate_per_tonne or 0.0)
        oil_price = (ticket.oil_distance_km or 0.0) * (ticket.oil_rate_per_km or 0.0)
        ticket.commodity_value = commodity_value
        ticket.oil_price = oil_price
        ticket.total_price = commodity_value + oil_price
        ticket.status = "complete"
        if axle_weights:
            ticket.axle_weights_json = json.dumps(axle_weights)
        _update_vehicle_profile(session, ticket)
        net = ticket.net_weight
        total_price = ticket.total_price
        oil_cost = ticket.oil_price
        commodity_amount = ticket.commodity_value

    audit_service.log_action(
        operator,
        action,
        "WeighTicket",
        entity_id=ticket_id,
        details={
            "second_phase": second_phase,
            "weight_kg": weight_kg,
            "net_kg": net,
            "commodity_value": commodity_amount,
            "oil_price": oil_cost,
            "total_price": total_price,
        },
    )
    if source == "manual":
        audit_service.log_action(
            operator,
            "TICKET_MANUAL_WEIGHT",
            "WeighTicket",
            entity_id=ticket_id,
            details={"stage": second_phase, "weight_kg": weight_kg},
        )
        if exception_reason.strip():
            log_ticket_exception(
                operator,
                "manual_weight",
                exception_reason,
                ticket_id=ticket_id,
            )

    _safe_log_gate_event(operator, ticket_id, "returned")
    _safe_log_gate_event(operator, ticket_id, "on_bridge", note=f"{second_phase} capture")
    _safe_log_gate_event(operator, ticket_id, "off_bridge", note=f"{second_phase} capture")

    with get_session() as session:
        t = session.query(WeighTicket).filter_by(id=ticket_id).first()
        return _to_summary(t)


def capture_gross(
    operator: User,
    ticket_id: int,
    weight_kg: float,
    source: str = "auto",
    axle_weights: Optional[list[float]] = None,
) -> TicketSummary:
    """Backward-compatible alias kept for existing callers."""
    return capture_second_weight(
        operator=operator,
        ticket_id=ticket_id,
        weight_kg=weight_kg,
        source=source,
        axle_weights=axle_weights,
    )


def void_ticket(admin: User, ticket_id: int, reason: str) -> None:
    from weighmaster.services import audit_service

    if not reason.strip():
        raise WeighingError("Void reason is required")

    with get_session() as session:
        ticket = session.query(WeighTicket).filter_by(id=ticket_id).first()
        if ticket is None:
            raise WeighingError("Ticket not found")
        if ticket.is_void:
            raise WeighingError("Ticket is already voided")
        ticket.is_void = True
        ticket.status = "void"
        ticket.void_reason = reason.strip()
        ticket.voided_by = admin.id
        ticket.void_datetime = datetime.now()

    audit_service.log_action(
        admin,
        "TICKET_VOID",
        "WeighTicket",
        entity_id=ticket_id,
        details={"reason": reason},
    )


def get_ticket(ticket_id: int) -> Optional[TicketSummary]:
    with get_session() as session:
        t = session.query(WeighTicket).filter_by(id=ticket_id).first()
        return _to_summary(t) if t else None


def get_pending_tickets() -> list[TicketSummary]:
    with get_session() as session:
        tickets = (
            session.query(WeighTicket)
            .filter(
                WeighTicket.status.in_(OPEN_TICKET_STATUSES),
                WeighTicket.is_void == False,
            )
            .order_by(func.coalesce(WeighTicket.tare_datetime, WeighTicket.gross_datetime).asc())
            .all()
        )
        return [_to_summary(t) for t in tickets]


def get_ticket_history(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    search: str = "",
    commodity_id: Optional[int] = None,
    status: Optional[str] = None,
    operator_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[TicketSummary], int]:
    with get_session() as session:
        q = session.query(WeighTicket)
        if date_from:
            q = q.filter(WeighTicket.created_at >= date_from)
        if date_to:
            q = q.filter(WeighTicket.created_at <= date_to)
        if search:
            like = f"%{search}%"
            q = q.filter(
                WeighTicket.vehicle_plate.ilike(like)
                | WeighTicket.ticket_number.ilike(like)
                | WeighTicket.driver_name.ilike(like)
            )
        if commodity_id:
            q = q.filter(WeighTicket.commodity_id == commodity_id)
        if status and status != "all":
            if status == "void":
                q = q.filter(WeighTicket.is_void == True)
            elif status == "tare_captured":
                q = q.filter(WeighTicket.status.in_(OPEN_TICKET_STATUSES), WeighTicket.is_void == False)
            else:
                q = q.filter(WeighTicket.status == status, WeighTicket.is_void == False)
        if operator_id:
            q = q.filter(WeighTicket.operator_id == operator_id)

        total = q.count()
        tickets = q.order_by(WeighTicket.created_at.desc()).offset(offset).limit(limit).all()
        return [_to_summary(t) for t in tickets], total


def get_todays_kpis(operator_id: Optional[int] = None) -> dict:
    from datetime import date

    with get_session() as session:
        today_start = datetime.combine(date.today(), datetime.min.time())
        q = session.query(WeighTicket).filter(
            WeighTicket.created_at >= today_start,
            WeighTicket.is_void == False,
        )
        if operator_id:
            q = q.filter(WeighTicket.operator_id == operator_id)
        tickets = q.all()
        total = len(tickets)
        complete = [t for t in tickets if t.status == "complete"]
        pending = [t for t in tickets if t.status in OPEN_TICKET_STATUSES]
        net_sum = sum(t.net_weight or 0.0 for t in complete)
        return {
            "total_tickets": total,
            "net_weight_kg": net_sum,
            "pending_count": len(pending),
            "complete_count": len(complete),
        }


def _guess_mode(t: WeighTicket) -> str:
    if t.status == "gross_captured":
        return "gross_first"
    if t.status == "tare_captured":
        return "tare_first"
    if t.gross_datetime and t.tare_datetime:
        return "gross_first" if t.gross_datetime < t.tare_datetime else "tare_first"
    if t.gross_datetime and not t.tare_datetime:
        return "gross_first"
    return "tare_first"


def _to_summary(t: WeighTicket) -> TicketSummary:
    axle_weights = []
    try:
        axle_weights = json.loads(t.axle_weights_json)
    except Exception:
        pass

    mode = _guess_mode(t)
    if t.status == "tare_captured":
        pending_stage = "awaiting_gross"
    elif t.status == "gross_captured":
        pending_stage = "awaiting_tare"
    else:
        pending_stage = ""

    first_capture = t.gross_datetime if mode == "gross_first" else t.tare_datetime

    return TicketSummary(
        id=t.id,
        ticket_number=t.ticket_number,
        vehicle_plate=t.vehicle_plate,
        driver_name=t.driver_name,
        company_name=t.company_name,
        commodity_name=t.commodity_name,
        deduction_kg=t.deduction_kg,
        commodity_rate_per_tonne=t.commodity_rate_per_tonne or 0.0,
        commodity_value=t.commodity_value,
        oil_distance_km=t.oil_distance_km or 0.0,
        oil_rate_per_km=t.oil_rate_per_km or 0.0,
        oil_price=t.oil_price or 0.0,
        total_price=t.total_price,
        tare_weight=t.tare_weight,
        gross_weight=t.gross_weight,
        net_weight=t.net_weight,
        tare_datetime=t.tare_datetime,
        gross_datetime=t.gross_datetime,
        tare_source=t.tare_source,
        gross_source=t.gross_source,
        status=t.status,
        pending_stage=pending_stage,
        weighing_mode=mode,
        first_capture_datetime=first_capture,
        is_void=t.is_void,
        void_reason=t.void_reason,
        operator_id=t.operator_id,
        notes=t.notes,
        created_at=t.created_at,
        axle_count=t.axle_count,
        axle_weights=axle_weights,
    )


def reprint_ticket(user: User, ticket_id: int) -> str:
    from weighmaster.config import PDF_OUTPUT_DIR
    from weighmaster.database.models import Company
    from weighmaster.pdf.certificate import CertificateGenerator
    from weighmaster.services import audit_service

    with get_session() as session:
        ticket = session.query(WeighTicket).filter_by(id=ticket_id).first()
        if ticket is None:
            raise WeighingError("Ticket not found")
        company = session.query(Company).first()
        PDF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        out_path = str(PDF_OUTPUT_DIR / f"{ticket.ticket_number}.pdf")
        CertificateGenerator().generate(ticket, company, out_path)
        ticket_no = ticket.ticket_number

    audit_service.log_action(
        user,
        "TICKET_REPRINT",
        "WeighTicket",
        entity_id=ticket_id,
        details={"ticket_number": ticket_no},
    )
    return out_path

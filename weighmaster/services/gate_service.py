"""Gate checkpoint logging and queue helpers."""
from __future__ import annotations

from typing import Optional

from sqlalchemy import func

from weighmaster.database.connection import get_session
from weighmaster.database.models import GateEvent, User


GATE_EVENT_TYPES = ("arrived", "on_bridge", "off_bridge", "dispatch", "returned")


class GateEventError(Exception):
    pass


def log_gate_event(
    user: User,
    ticket_id: int,
    event_type: str,
    note: str = "",
) -> None:
    if event_type not in GATE_EVENT_TYPES:
        raise GateEventError(f"Unsupported gate event: {event_type}")
    with get_session() as session:
        session.add(
            GateEvent(
                ticket_id=ticket_id,
                event_type=event_type,
                event_note=note.strip() or None,
                recorded_by=user.id,
                recorded_by_name=user.username,
            )
        )


def get_latest_events_by_ticket(ticket_ids: list[int]) -> dict[int, str]:
    if not ticket_ids:
        return {}
    with get_session() as session:
        rows = (
            session.query(GateEvent.ticket_id, func.max(GateEvent.id))
            .filter(GateEvent.ticket_id.in_(ticket_ids))
            .group_by(GateEvent.ticket_id)
            .all()
        )
        latest_ids = [row[1] for row in rows]
        if not latest_ids:
            return {}
        latest = (
            session.query(GateEvent.ticket_id, GateEvent.event_type)
            .filter(GateEvent.id.in_(latest_ids))
            .all()
        )
        return {ticket_id: event_type for ticket_id, event_type in latest}


def get_ticket_events(ticket_id: int, limit: int = 25) -> list[GateEvent]:
    with get_session() as session:
        return (
            session.query(GateEvent)
            .filter_by(ticket_id=ticket_id)
            .order_by(GateEvent.created_at.desc())
            .limit(limit)
            .all()
        )


def get_gate_queue() -> list[dict]:
    from weighmaster.services.weighing_service import get_pending_tickets

    tickets = get_pending_tickets()
    latest = get_latest_events_by_ticket([t.id for t in tickets])
    rows: list[dict] = []
    for t in tickets:
        rows.append(
            {
                "ticket_id": t.id,
                "ticket_number": t.ticket_number,
                "vehicle_plate": t.vehicle_plate,
                "driver_name": t.driver_name,
                "pending_stage": t.pending_stage,
                "weighing_mode": t.weighing_mode,
                "first_capture_datetime": t.first_capture_datetime,
                "latest_event": latest.get(t.id, ""),
            }
        )
    return rows


"""Query and aggregate data for all reports."""
from __future__ import annotations

from datetime import datetime, date, timedelta
from typing import Optional

from weighmaster.database.connection import get_session
from weighmaster.database.models import WeighTicket, Commodity, User


def daily_summary(target_date: date) -> list[dict]:
    start = datetime.combine(target_date, datetime.min.time())
    end = datetime.combine(target_date, datetime.max.time())
    with get_session() as session:
        tickets = (
            session.query(WeighTicket)
            .filter(
                WeighTicket.created_at >= start,
                WeighTicket.created_at <= end,
                WeighTicket.is_void == False,
                WeighTicket.status == "complete",
            )
            .all()
        )
        by_commodity: dict[str, dict] = {}
        for t in tickets:
            key = t.commodity_name
            if key not in by_commodity:
                by_commodity[key] = {"commodity": key, "count": 0, "net_kg": 0.0}
            by_commodity[key]["count"] += 1
            by_commodity[key]["net_kg"] += t.net_weight or 0.0
        return sorted(by_commodity.values(), key=lambda x: x["net_kg"], reverse=True)


def vehicle_history(plate: str, date_from: Optional[date] = None, date_to: Optional[date] = None) -> list[dict]:
    with get_session() as session:
        q = session.query(WeighTicket).filter(WeighTicket.vehicle_plate.ilike(plate.strip()))
        if date_from:
            q = q.filter(WeighTicket.created_at >= datetime.combine(date_from, datetime.min.time()))
        if date_to:
            q = q.filter(WeighTicket.created_at <= datetime.combine(date_to, datetime.max.time()))
        tickets = q.order_by(WeighTicket.created_at.desc()).all()
        return [_ticket_dict(t) for t in tickets]


# Backward-compatible alias
vehicle_report = vehicle_history


def commodity_report(date_from: date, date_to: date) -> list[dict]:
    start = datetime.combine(date_from, datetime.min.time())
    end = datetime.combine(date_to, datetime.max.time())
    with get_session() as session:
        tickets = (
            session.query(WeighTicket)
            .filter(
                WeighTicket.created_at >= start,
                WeighTicket.created_at <= end,
                WeighTicket.is_void == False,
                WeighTicket.status == "complete",
            )
            .all()
        )
        by_commodity: dict[str, dict] = {}
        for t in tickets:
            key = t.commodity_name
            if key not in by_commodity:
                by_commodity[key] = {"commodity": key, "count": 0, "net_kg": 0.0}
            by_commodity[key]["count"] += 1
            by_commodity[key]["net_kg"] += t.net_weight or 0.0
        return sorted(by_commodity.values(), key=lambda x: x["net_kg"], reverse=True)


def operator_activity(date_from: date, date_to: date) -> list[dict]:
    start = datetime.combine(date_from, datetime.min.time())
    end = datetime.combine(date_to, datetime.max.time())
    with get_session() as session:
        tickets = (
            session.query(WeighTicket, User.full_name)
            .join(User, WeighTicket.operator_id == User.id)
            .filter(
                WeighTicket.created_at >= start,
                WeighTicket.created_at <= end,
                WeighTicket.is_void == False,
            )
            .all()
        )
        by_op: dict[int, dict] = {}
        for t, name in tickets:
            if t.operator_id not in by_op:
                by_op[t.operator_id] = {
                    "operator": name, "count": 0, "net_kg": 0.0, "complete": 0
                }
            by_op[t.operator_id]["count"] += 1
            if t.status == "complete":
                by_op[t.operator_id]["complete"] += 1
                by_op[t.operator_id]["net_kg"] += t.net_weight or 0.0
        return sorted(by_op.values(), key=lambda x: x["count"], reverse=True)


def full_export(date_from: date, date_to: date) -> list[dict]:
    start = datetime.combine(date_from, datetime.min.time())
    end = datetime.combine(date_to, datetime.max.time())
    with get_session() as session:
        tickets = (
            session.query(WeighTicket)
            .filter(WeighTicket.created_at >= start, WeighTicket.created_at <= end)
            .order_by(WeighTicket.created_at.asc())
            .all()
        )
        return [_ticket_dict(t) for t in tickets]


def weekly_summary() -> dict:
    from datetime import date as dt
    today = dt.today()
    monday = today - timedelta(days=today.weekday())
    start = datetime.combine(monday, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())
    with get_session() as session:
        tickets = (
            session.query(WeighTicket)
            .filter(
                WeighTicket.created_at >= start,
                WeighTicket.created_at <= end,
                WeighTicket.is_void == False,
            )
            .all()
        )
        complete = [t for t in tickets if t.status == "complete"]
        by_day: dict[str, dict] = {}
        for t in complete:
            key = t.created_at.strftime("%Y-%m-%d")
            if key not in by_day:
                by_day[key] = {"date": key, "count": 0, "net_kg": 0.0}
            by_day[key]["count"] += 1
            by_day[key]["net_kg"] += t.net_weight or 0.0
        return {
            "days": sorted(by_day.values(), key=lambda x: x["date"]),
            "total_count": len(complete),
            "total_net_kg": sum(d["net_kg"] for d in by_day.values()),
            "unique_vehicles": len({t.vehicle_plate for t in complete}),
            "unique_commodities": len({t.commodity_name for t in complete}),
        }


def monthly_summary(year: int, month: int) -> dict:
    from datetime import date as dt
    first_day = dt(year, month, 1)
    if month == 12:
        last_day = dt(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = dt(year, month + 1, 1) - timedelta(days=1)
    start = datetime.combine(first_day, datetime.min.time())
    end = datetime.combine(last_day, datetime.max.time())
    with get_session() as session:
        tickets = (
            session.query(WeighTicket)
            .filter(
                WeighTicket.created_at >= start,
                WeighTicket.created_at <= end,
                WeighTicket.is_void == False,
            )
            .all()
        )
        complete = [t for t in tickets if t.status == "complete"]
        by_day: dict[str, dict] = {}
        for t in complete:
            key = t.created_at.strftime("%Y-%m-%d")
            if key not in by_day:
                by_day[key] = {"date": key, "count": 0, "net_kg": 0.0}
            by_day[key]["count"] += 1
            by_day[key]["net_kg"] += t.net_weight or 0.0
        # Ensure all days in month are present
        all_days = []
        current = first_day
        while current <= last_day:
            key = current.strftime("%Y-%m-%d")
            day_data = by_day.get(key, {"date": key, "count": 0, "net_kg": 0.0})
            all_days.append(day_data)
            current += timedelta(days=1)
        return {
            "days": all_days,
            "total_count": len(complete),
            "total_net_kg": sum(d["net_kg"] for d in by_day.values()),
            "unique_vehicles": len({t.vehicle_plate for t in complete}),
            "unique_commodities": len({t.commodity_name for t in complete}),
        }


def driver_history(driver_name: str, date_from: Optional[date] = None, date_to: Optional[date] = None) -> list[dict]:
    with get_session() as session:
        q = session.query(WeighTicket).filter(WeighTicket.driver_name.ilike(f"%{driver_name.strip()}%"))
        if date_from:
            q = q.filter(WeighTicket.created_at >= datetime.combine(date_from, datetime.min.time()))
        if date_to:
            q = q.filter(WeighTicket.created_at <= datetime.combine(date_to, datetime.max.time()))
        tickets = q.order_by(WeighTicket.created_at.desc()).all()
        return [_ticket_dict(t) for t in tickets]


def admin_kpis() -> dict:
    from datetime import date as dt
    today = dt.today()
    return {
        "daily": daily_summary(today),
        **_summary_stats(today),
        "weekly": weekly_summary(),
    }


def _summary_stats(target_date: date) -> dict:
    start = datetime.combine(target_date, datetime.min.time())
    end = datetime.combine(target_date, datetime.max.time())
    with get_session() as session:
        all_today = (
            session.query(WeighTicket)
            .filter(WeighTicket.created_at >= start, WeighTicket.created_at <= end)
            .all()
        )
        complete = [t for t in all_today if t.status == "complete" and not t.is_void]
        voided = [t for t in all_today if t.is_void]
        pending = [t for t in all_today if t.status == "tare_captured" and not t.is_void]
        pending += [t for t in all_today if t.status == "gross_captured" and not t.is_void]
        net_sum = sum(t.net_weight or 0.0 for t in complete)
        return {
            "total_today": len(all_today),
            "complete_today": len(complete),
            "voided_today": len(voided),
            "pending_today": len(pending),
            "net_kg_today": net_sum,
        }


def _ticket_dict(t: WeighTicket) -> dict:
    return {
        "ticket_number": t.ticket_number,
        "vehicle_plate": t.vehicle_plate,
        "driver_name": t.driver_name,
        "company_name": t.company_name,
        "commodity": t.commodity_name,
        "tare_kg": t.tare_weight,
        "gross_kg": t.gross_weight,
        "deduction_kg": t.deduction_kg,
        "net_kg": t.net_weight,
        "rate_per_tonne": t.commodity_rate_per_tonne,
        "commodity_value": t.commodity_value,
        "oil_distance_km": t.oil_distance_km,
        "oil_rate_per_km": t.oil_rate_per_km,
        "oil_price": t.oil_price,
        "total_price": t.total_price,
        "tare_datetime": t.tare_datetime,
        "gross_datetime": t.gross_datetime,
        "status": t.status,
        "is_void": t.is_void,
        "void_reason": t.void_reason,
        "created_at": t.created_at,
    }

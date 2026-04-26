"""Formatting helpers for weights, dates, and ticket numbers."""
from __future__ import annotations

from datetime import datetime
from typing import Optional


def format_weight(kg: Optional[float], decimals: int = 2) -> str:
    if kg is None:
        return "—"
    return f"{kg:,.{decimals}f}"


def format_weight_tonnes(kg: Optional[float]) -> str:
    if kg is None:
        return "—"
    return f"{kg / 1000:,.3f}"


def format_datetime(dt: Optional[datetime], fmt: str = "%d/%b/%Y %H:%M") -> str:
    if dt is None:
        return "—"
    return dt.strftime(fmt)


def format_wait_time(dt: Optional[datetime]) -> str:
    if dt is None:
        return "—"
    delta = datetime.now() - dt
    total_seconds = int(delta.total_seconds())
    if total_seconds < 60:
        return f"{total_seconds}s"
    minutes = total_seconds // 60
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins}m"


def format_date(dt: Optional[datetime]) -> str:
    if dt is None:
        return "—"
    return dt.strftime("%d %b %Y")
